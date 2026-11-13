# 🛰️ Zero-Trust Ephemeral Pipeline Architecture (ZEPA)
## 🛠️ Systems Engineering & Multi-Agent Architecture Manifest

This document outlines the complete architectural design for a secure, localized code-automation pipeline designed to run on a dual-boot machine (**Windows & Linux**). The system utilizes a multi-tier pipeline to safely pass data from high-capability Web AIs down to a localized filesystem workspace without risk of system corruption, typos, or platform-specific failures.

---

## 🏛️ The System Naming Directory

| Component Name | Runtime Environment | Thread Scope | Structural Responsibility | Memory Management Style |
| :--- | :--- | :--- | :--- | :--- |
| **NodeJS UI** | Node.js Runtime | Persistent / Main GUI Thread | Renders the live system dashboard; streams `stdout`/`stderr` logging from the core. | Dynamic JavaScript Garbage Collection |
| **Thread X** | Compiled Native Rust | Core / Process Supervisor | Acts as the main process manager and **Structural Error** firewall. Spawns and kills worker environments. | Zero-overhead static ownership tracking |
| **Thread A** | Postman CLI Engine | Persistent Network Consumer | Executes automated cookie/session injection to interact with free-tier web AIs. | Managed by the Postman CLI process |
| **Thread C** | Ephemeral Native Rust | Short-Lived Worker Thread | **Spawned conditionally by Thread X only if no structural errors are detected.** Acts as a throwaway compute cage. | Allocation on demand; instant deallocation |
| **Thread B** | Isolated Python Engine | Long-Running File Executor | Manages the local 2B model processing loops, evaluates **Code Risks**, and executes sandboxed local disk writes. | Isolated Python Virtual Env Runtime |

---

## 🔄 End-to-End Operational Workflow Diagram

```
[ Web AI Complexity Evaluator ] ──> Choose Model Tier ──> [ Free-Tier Claude/ChatGPT ]
                                                                      │
                                                           (Generates Text Payload)
                                                                      │
                                                                      ▼
                                                              [ Postman CLI ]
                                                                      │
                                                          (Pipes Raw String String)
                                                                      │
                                                                      ▼
                                                          [ Thread X: Rust Gate ]
                                                                      │
                                                          (Has Structural Errors?)
                                                          /                                                                              YES                       NO
                                                        /                                                                   [ Drop Packet & Soft Error ]        [ Spawn Thread C ]
                                                                                     │
                                                                                     ▼
                                                                           [ Thread C Sandbox ]
                                                                                     │
                                                                           (Invokes Local 2B AI)
                                                                                     │
                                                                           [ Thread B: Python Engine ]
                                                                                     │
                                                                           (Runs Code Risk Check)
                                                                           (Runs CWD Sandbox Lock)
                                                                                     │
                                                                                     ▼
                                                                           [ Hard Drive / Disk ]
```

---

## ⚡ The Multi-Tiered Safety Firewall

The core architecture treats incoming web data with a **Zero-Trust paradigm**, dividing safety into three independent boundaries:

### 1. 🛡️ Structural Error Risk (Managed by Thread X Gatekeeper)
* **The Rule:** Before allocating any local processing memory, Thread X runs a raw-string validation check on the incoming data packet from Postman CLI. It scans for syntax layout breaks, unmatched JSON brackets, or truncated code streams (a common symptom of free-tier token cap cutoff bounds).
* **The Isolation:** **Thread X will only spin up the ephemeral Thread C when IT DOES NOT detect any structural errors.** If structural defects are present, the packet is instantly dropped at the gate, throwing a soft error to the NodeJS UI and protecting the machine from processing garbage input.

### 2. 🧠 Code Risk (Managed by Thread B inside Thread C Isolation)
* **The Rule:** If the string passes the structural check, Thread X assigns Thread C as an execution container. Inside this container, Thread B (the Python Engine) invokes a local 2B model (`qwen2.5-coder:1.5b`) running directly on your **32GB DDR5 6000 CPU RAM**.
* **The Isolation:** The 2B model performs deep content inspection to verify harder whether the operation is logically safe. Because this resource-heavy processing runs inside the short-lived wrapper of Thread C, if the local model freezes, leaks memory, or crashes, **the failure is completely contained**. Thread X will catch the crash, alert the UI, release Thread C, and keep your core terminal wide awake.

### 3. 🔒 The Hard Lock (Managed by Thread B Backend)
* **The Rule:** No matter what the Web AI outputs or what the 2B model validates, Thread B's file-writing backend has **hardcoded system restrictions**. 
* **The Isolation:** It utilizes Python's native object-oriented `pathlib` engine to enforce a absolute `is_relative_to(Path.cwd())` boundary shield. If any command tries to request root-level access (`/` or `C:\`), system directories, or execute directory traversal hacks (`../`), **Thread B kills the instruction instantly**.

---

## 🔀 Free-Tier Multi-Account & Memory Compression Pipeline

To maximize the output capability of free-tier web model channels without hitting performance limits or losing progress state variables, the system executes an automated background compression loop:

1. **Token Ceiling Interception:** Postman Test scripts continuously parse incoming text structures. If phrases like *"Limit reached"* or *"Context length exceeded"* are detected, Postman tags the header payload with a custom `[STATUS: LIMIT_HIT]` parameter.
2. **Asynchronous Handshake Loop:** Thread X processes this token alert and instantly switches its active Postman CLI configuration settings via environment profile flags (`-e Claude_Account_Work.json`), routing the pipeline to an alternative free account credentials token.
3. **Recursive Memory Compression:** While the main workflow handles the file write execution loops, a background asynchronous thread takes the current multi-turn history chat log and pumps it through a high-context window engine. It runs 2 to 3 iterations of a self-review prompt to compress the system context down into a dense text snippet.
4. **Semantic Codebase Snapshot:** Simultaneously, an async worker outputs a strict **10–20 line overview README snippet** outlining the directory architecture modified so far.
5. **Hydration Engine:** This README layout map is stitched directly to the top of the compressed memory string. When the newly switched free Claude account fires up, it reads this ultra-dense context packet first, instantly absorbing the complete codebase history in a single, token-efficient transaction step.

---

## 💻 Dual-Boot Portability & Path Mechanics

Because the tool must execute identically whether booting into **Windows** or **Linux**, the file engine completely bans manual string parsing operations or hardcoded slash symbols (`\` vs `/`).

### 📦 Object-Oriented Normalization
Both Rust (`std::path::PathBuf`) and Python (`pathlib.Path`) treat directories as logical abstract components rather than raw text string characters.

```python
# This exact syntax resolves flawlessly on BOTH operating systems
target_directory = Path.cwd() / "src" / "components" / "auth"
target_directory.mkdir(parents=True, exist_ok=True)
```
* **Under Linux POSIX:** Resolves automatically with forward slashes: `/home/user/project/src/components/auth`
* **Under Windows NT:** Resolves automatically with native backward slashes: `C:\Users\user\project\src\components\auth`

By utilizing explicit reference operators, the codebase remains 100% agnostic to the underlying operating system environment, preventing platform-specific system script failures.
