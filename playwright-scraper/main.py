import asyncio
import math
import random
import shutil
import tempfile
from pathlib import Path

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, async_playwright

PLATFORM_CONFIGS = {
    "chatgpt": {
        "url": "https://chatgpt.com",
        "input_selector": "#prompt-textarea",
        "stop_button_selector": "button[data-testid='stop-button']",
        "response_selector": "div[data-message-author-role='assistant']",
        "code_block_selector": "div[data-message-author-role='assistant'] pre code",
    },
    "claude": {
        "url": "https://claude.ai",
        "input_selector": "div[contenteditable='true']",
        "stop_button_selector": "button[aria-label='Stop response']",
        "response_selector": "div[data-test-render-count]",
        "code_block_selector": "pre code",
    },
    "gemini": {
        "url": "https://gemini.google.com/app",
        "input_selector": "div.ql-editor[contenteditable='true']",
        "stop_button_selector": "button[aria-label='Stop response']",
        "response_selector": "message-content",
        "code_block_selector": "message-content pre code",
    },
}


class AccountExhaustedError(Exception):
    """Raised when the active account hits a usage/context cap or rate limit."""


class BrowserRelay:
    LIMIT_PHRASES = (
        "something went wrong",
        "try again later",
        "too many requests",
        "sign in to continue",
        "reached your limit",
        "message limit reached",
    )

    def __init__(self, platform: str = "gemini", max_retries: int = 3):
        if platform not in PLATFORM_CONFIGS:
            raise ValueError(
                f"Unsupported platform '{platform}'. Choose from: {list(PLATFORM_CONFIGS)}"
            )

        self.platform = platform
        self.config = PLATFORM_CONFIGS[platform]
        self.max_retries = max_retries
        self.mouse_pos: tuple[float, float] = (200.0, 200.0)
        self.playwright = None
        self.context = None
        self.page = None
        self.temp_profile_dir: Path | None = None

    async def _cleanup_profile(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.temp_profile_dir and self.temp_profile_dir.exists():
            shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
            self.temp_profile_dir = None

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()

        await self._cleanup_profile()
        self.temp_profile_dir = Path(tempfile.mkdtemp(prefix=f"zepas_{self.platform}_"))

        url = self.config["url"]
        print(
            f"[Relay] Starting ephemeral {self.platform} session ({self.temp_profile_dir.name})..."
        )

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.temp_profile_dir),
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ],
            ignore_default_args=["--enable-automation"],
        )
        await self.context.grant_permissions(
            ["clipboard-read", "clipboard-write"], origin=url
        )

        self.page = (
            self.context.pages[0]
            if self.context.pages
            else await self.context.new_page()
        )
        await self.page.goto(url, wait_until="domcontentloaded")

    async def _dismiss_guest_popups(self):
        for label in ("Accept all", "Got it", "No thanks", "Stay signed out"):
            btn = self.page.get_by_role("button", name=label).first
            if await btn.is_visible():
                await btn.click()
                await asyncio.sleep(0.3)

    async def _send_and_scrape_once(
        self, prompt: str, timeout_ms: int = 120000
    ) -> dict:
        await self._dismiss_guest_popups()

        body_text = (await self.page.inner_text("body")).lower()
        for phrase in self.LIMIT_PHRASES:
            if phrase in body_text:
                raise RuntimeError(f"Session blocked/limited: '{phrase}'")

        input_sel = self.config["input_selector"]
        stop_sel = self.config["stop_button_selector"]
        resp_sel = self.config["response_selector"]

        prev_count = await self.page.locator(resp_sel).count()

        self.mouse_pos = await Humanizer.human_click_locator(
            self.page, input_sel, self.mouse_pos
        )
        await Humanizer.human_input_text(self.page, prompt)
        await asyncio.sleep(random.uniform(0.15, 0.35))
        await self.page.keyboard.press("Enter")

        try:
            await self.page.locator(stop_sel).first.wait_for(
                state="visible", timeout=10000
            )
            await self.page.locator(stop_sel).first.wait_for(
                state="hidden", timeout=timeout_ms
            )
        except PlaywrightError:
            await self.page.wait_for_function(
                "(args) => document.querySelectorAll(args.sel).length > args.prev",
                arg={"sel": resp_sel, "prev": prev_count},
                timeout=timeout_ms,
            )

        latest_reply = self.page.locator(resp_sel).last
        full_text = (await latest_reply.inner_text()).strip()
        code_blocks = await latest_reply.locator("pre code").all_inner_texts()

        return {
            "platform": self.platform,
            "full_text": full_text,
            "code_blocks": [c.strip() for c in code_blocks if c.strip()],
        }

    async def execute_with_failover(
        self, prompt: str, timeout_ms: int = 120000
    ) -> dict:
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                if not self.page or self.page.is_closed():
                    await self.start()
                return await self._send_and_scrape_once(prompt, timeout_ms=timeout_ms)
            except Exception as e:
                last_error = e
                print(f"[Relay] Error on attempt {attempt}/{self.max_retries}: {e}")
                if attempt < self.max_retries:
                    await self.start()

        raise RuntimeError(
            f"Failed after {self.max_retries} ephemeral sessions. Last error: {last_error}"
        )

    async def close(self):
        await self._cleanup_profile()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None


class Humanizer:
    """Provides human-like mouse trajectories, clicks, and hybrid typing/pasting."""

    @staticmethod
    def _cubic_bezier(
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
        t: float,
    ) -> tuple[float, float]:
        """Evaluates a point along a cubic Bézier curve for parameter t in [0, 1]."""
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return x, y

    @classmethod
    async def move_mouse_bezier(
        cls,
        page: Page,
        start: tuple[float, float],
        end: tuple[float, float],
        steps: int | None = None,
    ):
        """Moves the mouse along a randomized cubic Bézier curve with subtle micro-jitters."""
        steps = steps or random.randint(18, 32)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        ctrl1 = (
            start[0] + dx * random.uniform(0.2, 0.45) + random.uniform(-60, 60),
            start[1] + dy * random.uniform(0.1, 0.4) + random.uniform(-60, 60),
        )
        ctrl2 = (
            start[0] + dx * random.uniform(0.55, 0.85) + random.uniform(-50, 50),
            start[1] + dy * random.uniform(0.6, 0.9) + random.uniform(-50, 50),
        )

        for i in range(1, steps + 1):
            linear_t = i / steps
            eased_t = linear_t * linear_t * (3.0 - 2.0 * linear_t)
            x, y = cls._cubic_bezier(start, ctrl1, ctrl2, end, eased_t)

            # Add subtle hand tremor jitter (dampened to 0 on the final landing step)
            if i < steps:
                x += random.gauss(0, 1.4)
                y += random.gauss(0, 1.4)

            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.006, 0.018))

    @classmethod
    async def human_click_locator(
        cls,
        page: Page,
        selector: str,
        last_pos: tuple[float, float] = (200.0, 200.0),
    ) -> tuple[float, float]:
        """Moves via Bézier curve to a randomized point inside the target element and clicks."""
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=15000)
        box = await locator.bounding_box()
        if not box:
            await locator.click()
            return last_pos

        target_x = box["x"] + box["width"] * random.uniform(0.25, 0.75)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        await cls.move_mouse_bezier(page, last_pos, (target_x, target_y))
        await asyncio.sleep(random.uniform(0.04, 0.12))
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.02, 0.07))
        await page.mouse.up()
        return (target_x, target_y)

    @staticmethod
    async def _type_cadence(page: Page, chunk: str):
        """Types text with 3-7ms per character and 8-12ms per space."""
        for char in chunk:
            if char == " ":
                delay_ms = random.uniform(8, 12)
            else:
                delay_ms = random.uniform(3, 7)

            await page.keyboard.type(char, delay=delay_ms)

            if char == "\n":
                await asyncio.sleep(random.uniform(0.015, 0.035))

    @classmethod
    async def human_input_text(cls, page: Page, text: str):
        """Types prompts <= 200 chars completely; for > 200 chars, types ~30% up to the next space and pastes the rest."""
        if len(text) <= 200:
            await cls._type_cadence(page, text)
            return

        raw_cut = math.ceil(len(text) * 0.30)
        next_space = text.find(" ", raw_cut)

        if next_space != -1:
            split_idx = next_space + 1
        else:
            split_idx = raw_cut

        prefix = text[:split_idx]
        remainder = text[split_idx:]

        await cls._type_cadence(page, prefix)

        if remainder:
            await asyncio.sleep(random.uniform(0.06, 0.14))
            await page.evaluate(
                "async (clipText) => { await navigator.clipboard.writeText(clipText); }",
                remainder,
            )
            await page.keyboard.press("Control+v")
            await asyncio.sleep(random.uniform(0.08, 0.16))


async def main():
    relay = BrowserRelay(platform="gemini", max_retries=3)
    try:
        await relay.start()
        test_prompt = (
            "Write a short 3-line Python function that adds two numbers "
            "and returns the result. Include only a Python code block."
        )
        result = await relay.execute_with_failover(test_prompt)
        print("\n--- Scraped Response ---")
        print("Full Text:\n", result["full_text"])
        print("Code Blocks:", result["code_blocks"])
    finally:
        await relay.close()


if __name__ == "__main__":
    asyncio.run(main())
