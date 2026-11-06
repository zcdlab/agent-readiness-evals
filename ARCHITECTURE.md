# Architecture & System Design

`agent-readiness` provides automated repository readiness auditing and zero-trust contract generation for autonomous AI coding agents.

## Architectural Data Flow

```text
+-------------------------------------------------------------------------+
|                  1. Zero-Config Filesystem Scanner                      |
|                                                                         |
|  [Target Codebase]                                                      |
|         │                                                               |
|         ▼                                                               |
|  [Filesystem Scanner] ────► Inspect: BUILD.bazel, pyproject.toml, tests |
|         │                  Quarantine: infra/prod/, security/, db/      |
|         ▼                                                               |
|  [4-Pillar Evaluation]───► 1. Reproducible Build & Dependencies (25%)   |
|         │                  2. Deterministic Verification Harness (25%)  |
|         │                  3. Blast-Radius Boundary Policy (25%)        |
|         │                  4. Agent Operating Guidelines (25%)          |
|         ▼                                                               |
|  [Readiness Report]   ────► Initial Score (e.g. 50/100, High Blast Risk)|
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                  2. Automated Contract Synthesizer                      |
|                                                                         |
|  [Missing Safeguard Identification]                                     |
|         │                                                               |
|         ├──► Synthesize: .agent-policy.yaml (Zero-Trust Path Lockout)   |
|         └──► Synthesize: AGENTS.md (Operating Conventions & Guidelines) |
|         │                                                               |
|         ▼                                                               |
|  [Atomic Write & Re-Verification]                                       |
|         │                                                               |
|         ▼                                                               |
|  [Certified Agent-Ready Score] ──► 100 / 100 [Enterprise Agent Ready]   |
+-------------------------------------------------------------------------+
```

## Core Modules
- `src/models.py`: Pydantic v2 schemas (`ReadinessReport`, `ReadinessPillar`, `PermissionTier`).
- `src/scanner.py`: Non-destructive multi-stack filesystem analyzer and sensitive path discoverer.
- `src/onboarder.py`: Automated contract synthesizer and score elevator.
- `src/cli.py`: Standalone CLI binary (`readiness scan`, `readiness fix`, `readiness ui`).

---

## The Harness Engineering Verification Loop

```text
       [Stochastic LLM Agent]
                 │
                 ▼  (Proposes code mutation)
    ┌───────────────────────────┐
    │  Harness Execution Gate   │
    │  - Sandbox Permissions    │
    │  - Path Quarantines       │
    └─────────────┬─────────────┘
                  │  (Allowed write in src/ or tests/)
                  ▼
    ┌───────────────────────────┐
    │ Deterministic Verification│
    │ - Fast Test Runner (< 5s) │
    │ - Type Checker & Linter   │
    └─────────────┬─────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
     [PASS: 100%]      [FAIL: > 0]
         │                 │
         │                 ▼ (Extract exact trace & failing line)
         │           [Systematic Debugging Protocol]
         │                 │
         │                 ▼ (Minimal surgical patch < 60 LOC)
         │           [Loop back to Verification]
         ▼
    [Commit Accepted]
```
