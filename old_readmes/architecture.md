# 🏛️ Zero-Trust Ephemeral Pipeline Architecture (ZEPA)
## Technical Architecture Design Document

This document outlines the system architecture for a localized, zero-trust, multi-agent file automation engine designed for high-stability execution on a dual-boot (Windows/Linux) workstation. The architecture leverages a four-language polyglot layout, isolating process management, network ingestion, cryptographic memory staging, filesystem mutations, and frontend observability.

---

## 1. Executive Summary & Design Paradigm

The **Zero-Trust Ephemeral Pipeline Architecture (ZEPA)** resolves the fragility, security, and contextual runtime limits of standard web-based AI automation tools. By decoupling the execution phases into isolated, single-responsibility memory boundaries, ZEPA ensures that external web runtime errors, LLM hallucinations, network dropped sockets, or path-traversal attacks cannot destabilize the local operating system.

### Core Architectural Pillars
*   **Process Isolation:** A compiled supervisor core wraps dynamic script runtimes, neutralizing unhandled sub-process crashes.
*   **Staged Pipeline Defense:** Multi-tier validation gates verify syntax structure and execution permissions before the hard drive is engaged.
*   **Data-Agnostic Routing:** Memory streams are passed across system layers as dynamic byte arrays/strings, minimizing type-marshaling friction.
*   **Ephemeral Compute:** High-overhead local inference workers are dynamically allocated and pruned, optimizing system RAM constraints.

---

## 2. System Core Blueprint & Naming Directory

The core infrastructure splits operational duties among four distinct, isolated system layers managed by an implicit process boundary.

| Component Name | Runtime / Language | Operational Responsibility | Memory Strategy |
| :--- | :--- | :--- | :--- |
| **Thread X** | Rust (Compiled Binary) | Master Process Supervisor & Pre-flight String Inspector | Core Orchestration Memory |
| **Thread A** | Web JS / Postman CLI | Web Ingestion & Async Network Command Collector | Volatile Network Memory |
| **Thread C** | Rust (Dynamic Spawns) | Ephemeral Local 2B Model Inference & JSON Engine Parser | Ephemeral Allocated Worker Memory |
| **Thread B** | Python Engine | Local File System Operations & CWD Sandbox Shield | Persistent Disk I/O Memory |
| **NodeJS UI** | JavaScript Runtime | Frontend Observability Dashboard & Async Process Status Logger | UI Heap Stream Memory |

---

## 3. Structural Data Flow & Pipeline Diagram

The system operates as a **First-In, First-Out (FIFO) Sequential Relay Queue**, transferring ownership parameters through continuous memory drops.

```
 [ Thread A: Web Ingest ]
         │
         ▼ (Pushes Payload via Postman CLI)
 ┌────────────────────────────────────────────────────────┐
 │ Thread X: Master Rust Supervisor                       │
 │   - Risk Score Assessment                              │
 │   - Pre-Flight Text Firewall                           │
 └──────────────────────────┬─────────────────────────────┘
                            │
                    (Passed Verification?)
                   /                      \
                 YES                       NO
                 /                          \
                ▼                            ▼
 ┌───────────────────────────────┐   ┌──────────────────────────────┐
 │ Thread C: Ephemeral Worker    │   │  NodeJS UI Observability     │
 │   - Spawned Dynamically       │   │  - Instantly Render Alert    │
 │   - Runs 2B Model Logic Clean │   │  - Drops Malformed Packet    │
 └──────────────┬────────────────┘   └──────────────────────────────┘
                │
         (2B Clean Output?)
        /                  \
      YES                   NO
      /                      \
     ▼                        ▼
 ┌────────────────────────┐  ┌──────────────────────────────┐
 │ Thread B: Python Disk  │  │ Thread X Supervisor          │
 │   - CWD Sandbox Validation│  │  - Catch Logic Defect        │
 │   - Absolute File Mutation│  │  - Kill & Prune Thread C     │
 └────────────────────────┘  └──────────────────────────────┘
```

---

## 4. Comprehensive Tiered Risk Execution Model

ZEPA classifies incoming execution blocks into dynamic tiers based on a metadata payload computed dynamically by the remote orchestration script.

### Tiered Risk Operational Logic

```
   [ Incoming Packet ]
           │
           ├── Risk Score 1-3 (Low Risk)  ──> Bypass Thread C ──> Thread X Direct Handoff ──> Thread B Disk
           │
           └── Risk Score 4+  (High Risk) ──> Intercepted by Thread X ──> Spawn Thread C ──> 2B Inspection ──> Thread B Disk
```

### Risk Tier Categorization Matrix

| Risk Tier | Score Range | Triggers / Characteristics | Pipeline Pathway | Exception Handling Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Low Risk** | `1 - 3` | Empty folder construction (`mkdir`), minor source patches, non-destructive file touches. | **Thread A** ➔ **Thread X** ➔ **Thread B** | Immediate payload pass; failures drop directly to standard exception arrays. |
| **High Risk** | `4+` | Wildcard cleans (`rm*`), directory removals (`rmdir`), key configuration mutations, deep logic overwrites. | **Thread A** ➔ **Thread X** ➔ **Thread C (2B Model)** ➔ **Thread B** | Deep packet analysis; forced schema matching; simulation mapping. |

---

## 5. Security Protocols & Cross-Platform Execution Shield

### 5.1 The Thread X Pre-Flight String Firewall
When a payload is intercepted by the **Thread X Supervisor**, it switches from an agnostic character router into a firewall. It reads text segments looking for unbalanced brackets, missing JSON strings, or specific structural indicators that hint at an truncated token generation or a corrupted context array. If irregularities are detected, Thread X short-circuits the pipeline, drops the command, and broadcasts a `[SOFT_ERROR]` token string to the NodeJS UI.

### 5.2 Ephemeral Sandboxing (Thread C Lifecycle)
Thread C protects the main supervisor stack from memory exhaustion. Spawning a local LLM inference loop on a CPU uses specific resource footprints. By allocating this execution frame completely inside a transient thread closure (`std::thread` or `tokio::task`), the application blocks memory footprint decay:
1. **Instantiation:** Thread C pulls the thread-safe HTTP reference pointer (`Arc<reqwest::Client>`).
2. **Inference Execution:** Ingests the messy data vector, posts to the local Ollama backend (`qwen2.5-coder:1.5b`), and decodes the structured response.
3. **Cooperative Cancellation:** If processing limits are broken, Thread X toggles a cross-thread cancellation token, triggering an implicit return inside Thread C.
4. **Deallocation:** Upon function completion, the operating system kernel reclaims Thread C's thread stack allocations back into the system heap pool.

### 5.3 Thread B File System Chroot Sandbox
Thread B enforces platform-agnostic file security. Even if the web AI hallucinates paths like `../../etc/passwd` or `..\..\Windows\System32`, Thread B leverages Python's built-in path normalization to intercept and trap the operation.

```python
# System Validation Logic Profile
from pathlib import Path

ALLOWED_ROOT = Path.cwd().resolve()
requested_target = Path(incoming_ai_path)
resolved_target = requested_target.resolve()

# Strict parent-relationship enforcement
if not resolved_target.is_relative_to(ALLOWED_ROOT):
    raise PermissionError("Access Denied: AI attempted to escape the sandbox directory!")
```

### 5.4 Dual-Boot Slash Abstraction Matrix
Because the tool functions uniformly on a dual-boot workstation, path parsing strings are completely eliminated. The architecture relies on structural object models that adjust based on runtime system bindings:

*   **Linux Environment Deployment:** Path models compile as standard `PosixPath` configurations, routing through forward-slash conventions (`/home/user/project/src`).
*   **Windows Environment Deployment:** Path models compile as standard `WindowsPath` configurations, handling volume designators and backslash conventions (`C:\Users\user\project\src`).

---

## 6. Fault Isolation & Crash Recovery Matrix

The core responsibility of the Thread X supervisor framework is absolute system resilience. The table below outlines how ZEPA intercepts failures without allowing system-wide degradation.

| Failure Event | Component Origin | Fault Capture Mechanism | Recovery Action Protocol | User Experience Event |
| :--- | :--- | :--- | :--- | :--- |
| **Token Exhaustion / Truncation** | Claude Web App / Thread A | Postman Test RegEx Assertions (`pm.test`) | Appends `[STATUS: ERROR_LIMIT]` header; aborts transmission down the local pipe. | UI Dashboard updates with flashing account cooldown warning. |
| **Path Traversal / Sandbox Break** | Hallucinated Input String | Thread B Python Sandbox Assertions (`is_relative_to`) | Halts hard drive operation; drops transaction block; prints error code string. | UI Dashboard records a critical security violation block; locks the loop. |
| **LLM Inference Timeout / Glitch** | Ollama Engine / Thread C | Thread X Asynchronous Sleep Monitoring Window | Fires a cancellation token; kills the execution window; deallocates task context. | UI logs a soft timeout error; triggers a second retry loop. |
| **Unhandled Runtime Logic Exception** | Script A or Script B Engine | Thread X Supervisor Execution Monitoring (`child.wait()`) | Captures non-zero process exit status; wraps system variables; respawns fresh worker process. | System stays active; dashboard shows worker process bouncing. |

---

## 7. Context Management & Async Memory Compression

To maintain ongoing architectural awareness while using web-based free-tier accounts, ZEPA utilizes a background worker array to compress project footprints asynchronously.

```
 [ Thread B (Disk Operations) ] ──> Trigger Background Snapshot ──> [ Async Worker Thread ]
                                                                             │
 [ High-Context Cloud Input ] <─── Attach 15-Line Code Index ◄───────────────┘
```

1. **The Parallel Snapshot:** While the primary loop is executing text changes to disk, a background worker isolates the current working directory tree.
2. **Recursive Summary Processing:** The changed states are piped into an asynchronous compression loop that targets high-context public endpoints to map out structural components into dense summary indices.
3. **Context Hydration Injector:** The compressed project layout is outputted into an automated **15-line overview snapshot matrix**. This snapshot profile is prepended to the memory buffer array whenever the system rotates onto a fresh free-tier account, keeping subsequent model operations clear of layout hallucinations.