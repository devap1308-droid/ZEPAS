# Zero-Trust Ephemeral Pipeline Architecture (ZEPA)
## Technical Architecture & Core System Blueprint

This document details the complete end-to-end technical architecture for the **Zero-Trust Ephemeral Pipeline Architecture (ZEPA)**. This system is designed as a crash-proof, multi-tiered file automation tool that acts as a secure local bridge between erratic external Web AIs and a local dual-boot (Windows/Linux) file system. It leverages a local **2B LLM model (via Ollama)** running entirely on **CPU (32GB DDR5 6000MHz RAM)** as a deterministic formatting and sanity layer, managed by a compiled high-level **Rust process supervisor**.

---

## 🏛️ Comprehensive Component Directory

The entire project stack spans across four execution runtimes/environments, distinctly separated by their memory management models and operational duties:

| Component Name | Runtime Environment | Memory / Execution Model | Operational Core Duty |
| :--- | :--- | :--- | :--- |
| **The Web Brains** | Cloud / Browser Interface (`claude.ai` / `chatgpt`) | Remote Web Context (Free Tier) | Ingests initial human prompts, evaluates task complexity, manages long-term memory compression, and generates raw file content payloads. |
| **Postman CLI** | Local Terminal Shell Environment | Local Network Client Framework | Acts as the local automated "browser user" relay, injecting authentication headers/session cookies to interact with the Free Tier web interface and hitting the local application endpoints. |
| **Thread X** | Compiled **Rust** Binary | Persistent Master Process Supervisor (Async) | The main execution core. Hosts the API endpoint, manages child runtime lifecycles (Python/NodeJS), intercepts terminal crashes, and acts as the deep-packet string firewall. |
| **Thread A** | **Rust** Network Routine | Non-blocking Async Receiver (within Thread X) | Ingests raw JSON/text requests pushed down from the Postman CLI automation loop. |
| **Thread C** | **Rust** Ephemeral Thread | Short-lived, Conditional Memory Worker | **Spawned dynamically by Thread X ONLY IF the initial firewall detects no string errors.** Invokes the local 2B model for structural verification, then cleanly terminates. |
| **Thread B** | **Python** Engine Runtime | Persistent Isolated Worker Queue | The filesystem execution layer. Reads verified payloads from the Rust channel, enforces path constraints, and physically writes/deletes target files. |
| **NodeJS UI** | **Node.js** Runtime | Asynchronous Dashboard Stream | Renders the terminal interface visual dashboard, capturing standard logs from the Rust supervisor to present errors, progress, and account statuses. |

---

## 🔄 End-to-End System Workflow Map

```
   [ User Prompt Input ]
             │
             ▼
   [ Web AI Evaluator ] ──(Complexity Check / Memory Compressing)──> [ Chosen Web Claude Account ]
                                                                                │
                                                                       (Outputs Raw Text)
                                                                                │
                                                                                ▼
   [ NodeJS Dashboard ] <──(Soft Errors)── [ Postman CLI ] <──(Swaps Browser Cookies on Free Tier Limit)
                                                │
                                    (Sends String + Risk Score)
                                                │
                                                ▼
                                    [ Thread A (Rust Ingest) ]
                                                │
                                                ▼
                                    [ Thread X (Rust Firewall) ]
                                                │
                                       (Detects Any Error?)
                                       /                  \
                                     YES                   NO
                                     /                      \
                        [ Drops Envelope Payload ]     [ Spawns Thread C (Ephemeral) ]
                        [ Sends Soft Error to UI ]                  │
                                                                    ▼
                                                       [ Local 2B CPU Model Engine ]
                                                       (Qwen2.5-Coder / Ollama Server)
                                                       (Syntax Verification & Clean JSON)
                                                                    │
                                                           (Is Output Faulty?)
                                                           /                 \
                                                         YES                  NO
                                                         /                     \
                                            [ Kills Thread C ]          [ Moves String Path ]
                                            [ Sends Soft Error to UI ]  [ Kills Thread C ]
                                                                               │
                                                                               ▼
                                                                  [ Thread B (Python Exec) ]
                                                                  (Pathlib CWD Sandbox Check)
                                                                               │
                                                                               ▼
                                                                  [ Physical Hard Drive Disk ]
                                                                  (Windows \ or Linux / Partition)
```

---

## ⚡ The Staged Defensive Routing Pipeline

Data moves through the system as a **Data-Agnostic String Envelope**. It is passed along thread vectors as a raw memory pointer, removing type-checking overhead until the final stages.

### Stage 1: The Pre-Flight Risk Assessment (Postman)
Before any token leaves the web loop, the Postman script attaches a **Risk Score** metadata parameter to the string payload based on the operation scale:
*   **Low Risk (Score 1-3):** Simple incremental line injections or creating new directory paths.
*   **High Risk (Score 4+):** Wildcard structural commands, directory deletes (`rmdir`), or file overwrites on core architecture scripts.

### Stage 2: Thread X String Gate (The Initial Firewall)
Thread X reads the incoming data packet from Thread A as a raw string. 
*   **The Zero-Check Protocol:** If the Risk Score is Low, Thread X bypasses high-overhead checks and pushes the data envelope forward down the processing conveyor belt.
*   **The Inspection Block:** If the Risk Score is High, Thread X stops the conveyor belt and runs non-deserialized validation rule checks. It verifies matching brackets at the end of the payload to detect mid-sentence free-tier token cap cut-offs and screens for immediate malicious strings.
*   **The Conditional Fork:** **If Thread X detects ANY string structure error, it immediately kills the envelope and logs a soft error. Thread X ONLY spins up the ephemeral Thread C when IT DOES NOT detect any string errors.**

### Stage 3: Thread C Deep Structural Verification (The Ephemeral Sandbox)
*   **Spawning:** Thread X transfers memory ownership of the data string to a fresh, temporary Thread C instance.
*   **AI Validation:** Thread C triggers an HTTP callback to the local **Ollama background service** hosting `qwen2.5-coder:1.5b`. Running exclusively on the high-speed **32GB DDR5 6000MHz RAM**, the model processes the text into a perfectly structured JSON string schema.
*   **Deferred Termination:** If the local 2B model catches a syntax execution error, Thread C alerts Thread X, passes a soft error message, and safely shuts down. If the text is perfectly valid, it passes the pristine text string to Thread B’s queue channel, deallocates its RAM space, and self-terminates.

### Stage 4: Thread B Sandboxed Execution (Python)
Thread B picks up the validated string. Because it is the only component with file write permissions, data corruption or operating system races are physically impossible. It enforces final execution rules before touching the disk.

---

## 🌐 The Free-Tier Account Rotation & Memory Strategy

To maintain an un-interrupted development environment using the free tier of `claude.ai` without hitting subscription message caps, the system implements an asynchronous background orchestration layer managed between Postman and Node.js.

### 1. Token Limit Detection via Postman Tests
When a conversation thread hits a context window cap or hourly limit, the web page returns a text warning layout. A Javascript snippet running in the **Postman Tests Tab** automatically scans every incoming payload string for target indicators (e.g., `"limit reached"`, `"too long"`, `"exceeded maximum length"`). 

If a phrase is flagged, Postman applies a special error header tag `[STATUS: ERROR_LIMIT]` to the text envelope. Thread X passes it to Thread C, which returns an explicit, safe termination payload to Thread B:
```json
{
  "status": "error",
  "error_type": "token_limit_reached",
  "action": "none"
}
```

### 2. Multi-Account Profile Swapping
Once the `TOKEN_LIMIT_HIT` environment state is confirmed, the orchestrator script instructs the **Postman CLI** execution loop to dynamically swap out active configuration profiles. By loading a distinct environment file flag via the CLI (`-e Claude_Account_Work.postman_environment.json`), Postman instantly injects a completely different set of session cookies and authorization tokens, shifting the workflow onto an entirely fresh free-tier account.

### 3. Asynchronous Memory Compression & Indexing
To prevent the new account from suffering from project amnesia, a background routine runs concurrently to maintain memory state:
*   **Probing & Compression:** The previous chat history logs are passed through a high-context window AI (like ChatGPT free tier) with a strict recursive summarization prompt. It condenses the entire interaction history down to a dense, detail-rich "State Summary text block," running 2-3 iterations to ensure no code parameters are dropped.
*   **Background Index Readme Snapshots:** Simultaneously, Python fires a background asynchronous task (`fastapi.BackgroundTasks`) that compiles a precise **10-20 line markdown README snippet** outlining the absolute layout of files written so far. 
*   **Hydration:** When the new Claude profile initiates, the system prefixes the 15-line README snapshot to the compressed memory block, immediately hydrating the new account context window with the complete blueprint using near-zero token overhead.

---

## 🖥️ Cross-Platform Pathing & Dual-Boot Sandboxing

The application is engineered to operate seamlessly across both sides of a dual-boot setup (**Windows NTFS partitions and Linux Posix filesystems**) without hardcoding environment branches or backward/forward slash conditions.

### 1. Path Abstraction with Pathlib and PathBuf
Instead of executing raw string concatenation (like `base_path + "/src"`), the filesystem core leverages object-oriented path abstractions:
*   In the **Rust Layer (Thread X/C)**: Uses `std::path::PathBuf`.
*   In the **Python Layer (Thread B)**: Uses `pathlib.Path`.

When paths are processed as abstract objects using the path-join operators (`/`), the runtime automatically interrogates the host operating system kernel at boot. It dynamically applies forward slashes (`/`) under Linux and normalizes them into backward slashes (`\`) under Windows in real time.

### 2. The Chroot Jail Sandbox Validation
To prevent the Web AI from attempting a Path Traversal Attack (e.g., trying to write or remove system files via relative dot hacks like `../../Windows/System32` or `/etc/passwd`), Thread B executes an absolute structural shield right before running any `.write_text()` or `.unlink()` commands:

```python
# The absolute physical boundary constraint
ALLOWED_ROOT = Path.cwd().resolve()
resolved_target = Path(ai_input_path).resolve()

# Enforce the system jail restriction
if not resolved_target.is_relative_to(ALLOWED_ROOT):
    raise PermissionError("Access Denied: Target path escapes the working directory!")
```
*   `.resolve()` flattens all internal shortcuts, symbolic links, and relative dot navigations into an explicit, absolute string path.
*   `.is_relative_to()` performs a mathematical parent-child hierarchy evaluation. If the resolved path does not strictly sit *inside* the Current Working Directory tree root, the execution is terminated immediately.

---

## 🛡️ Exception Containment & Process Recovery Matrix

The Rust process supervisor core (**Thread X**) isolates faults by wrapping all child scripts inside decoupled process workers using `tokio::process::Command`. 

| Failure Scenario | Immediate Local Impact | Thread X Supervisor Containment Action | Resulting System State |
| :--- | :--- | :--- | :--- |
| **Web AI JSON Text Corruption** | Postman CLI pushes unparseable code blocks or trailing markdown symbols. | Intercepted inside the ephemeral **Thread C** sandbox wrapper. The 2B model flags the formatting error and triggers a `[SOFT_ERROR]` stream line. | **Active & Intact.** The corrupted task packet is dropped, a red notification flashes on the NodeJS Dashboard UI, and Thread B is never interrupted. |
| **Python Engine Crash (Thread B Engine)** | Unhandled runtime exception (e.g., file locked by OS partition, out of memory). | Rust catches the specific non-zero OS exit status code via `.wait().await` monitoring loops. | **Self-Healed.** Thread X fires a crash alert to the NodeJS UI, clears temporary cache files, and respawns a fresh Python process queue in 3 seconds. |
| **Network Interruption / Account Lockout** | Postman CLI fails an HTTP web endpoint handshake. | Postman execution loop logs a test failure flag, pausing the external request chain. | **Safe Idle.** The pipeline halts execution safely, protecting local data from partial updates while waiting for account switching or user manual resume. |
| **Path Traversal Attack Attempt** | Hallucinating AI attempts to create/delete directories outside the allowed project sandbox. | Python’s Thread B throws a strict `PermissionError`. The script catches the block, stops disk execution, and passes a `SANDBOX_VIOLATION` log string up. | **Secure Block.** The file system remains completely untouched. Rust captures the violation log and prints a critical security alert to the NodeJS UI display. |
