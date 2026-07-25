# Agent Operating Guidelines & Harness Engineering Contract

> **System Mental Model (First Principles)**  
> Autonomous coding agents are stochastic token predictors sampled conditioned on prompt text. Without a deterministic execution harness, models suffer from context drift, hallucinated dependencies, and undetected regressions. This repository operates under strict **Harness Engineering**: every model action is bounded, observable, and gated by automated verification.

---

## 1. Architectural & Design Anchor Points

Before writing code or proposing changes, the agent **must inspect and align with**:
- [**`ARCHITECTURE.md`**](file:///Users/zcd/.gemini/antigravity/scratch/agent-readiness-evals/examples/agent_ready_service/ARCHITECTURE.md): Layer isolation boundaries, domain ingress flow, and quarantined infrastructure topology.
- [**`DESIGN.md`**](file:///Users/zcd/.gemini/antigravity/scratch/agent-readiness-evals/examples/agent_ready_service/DESIGN.md): Idempotency deduplication pattern, finite state machine transitions, and financial invariant rules.

---

## 2. Multi-Tier Verification Ladder & Differentiated Testing

Testing is not a single binary check. The harness provides five differentiated verification tiers:

```
[Tier 1: Fast Sub-Second Unit Loop]  ──> pytest tests/ -k <test_name> (< 0.2s)
                 │
                 ▼
[Tier 2: Static Contract & Types]   ──> ruff check src/ tests/ && mypy --strict src/ (< 1s)
                 │
                 ▼
[Tier 3: Property & Invariant Tests] ──> pytest tests/ -k "idempotent or rejection" (< 0.5s)
                 │
                 ▼
[Tier 4: Full Regression Gate]       ──> pytest -v --tb=short tests/ (100% green, budget < 5s)
                 │
                 ▼
[Tier 5: Machine-Readable Telemetry] ──> pytest --junitxml=.agent/results.xml
```

### Verification Tier Details

| Tier | Focus Area | Canonical Command | SLA / Budget | Required Gate Invariant |
| :--- | :--- | :--- | :--- | :--- |
| **1. Fast Unit Loop** | Single function isolation | `pytest tests/test_app.py -k <func>` | `< 0.2s` | Immediate feedback while typing |
| **2. Static Analysis** | Typings & linting | `ruff check src/ tests/` | `< 0.5s` | Zero lint errors or unvetted imports |
| **3. Invariant Tests** | Idempotency & state | `pytest tests/test_app.py -k deduplication` | `< 0.3s` | Mathematical guarantee against double billing |
| **4. Full Regression** | Entire test suite | `pytest -v --tb=short tests/` | `< 5.0s` | All tests green (0 failures) |
| **5. CI Telemetry** | Automated reporting | `pytest --junitxml=.agent/results.xml` | `< 5.0s` | Valid XML artifact emitted for CI gating |

**Core Invariant:** Never mark a task complete or push a commit if any verification tier fails.

---

## 3. Deterministic Execution Loop (Red -> Green -> Refactor)

All code modifications must follow the strict four-stage loop:
1. **RED (Reproduce):** Add minimal failing test in `tests/` asserting the new feature or capturing the bug.
2. **GREEN (Patch):** Apply minimal surgical patch in `src/` (< 60 LOC). Execute Tier 1 test.
3. **REFACTOR & LINT:** Run Tier 2 static analysis (`ruff`, `mypy`).
4. **VERIFICATION GATE:** Run Tier 4 full regression suite.

---

## 4. Blast Radius & Zero-Trust Sandbox Isolation

Access boundaries are governed cryptographically by [`.agent-policy.yaml`](.agent-policy.yaml):

- **Permission Tier:** `sandbox_write` (scoped exclusively to `src/` and `tests/`).
- **Quarantined Paths (READ ONLY / WRITE PROHIBITED):**
  - `infra/prod/` — Production Terraform, CloudFormation, Helm manifests.
  - `.env*` — Live production API keys, database credentials, secrets.
  - `db/migrations/` — Production schema migrations.
  - `.agent-policy.yaml` — Security policy governance.
- **Banned Terminal Operations:**
  - `rm -rf` or sweeping filesystem deletions.
  - `curl | bash` or downloading untrusted binaries.
  - Altering git remotes, branch histories, or global git configurations.
  - Spawning unmonitored background daemons without explicit timeouts.

---

## 5. Systematic Error Recovery Protocol

When a test or build fails, follow the systematic 4-step diagnostic protocol:
1. **Extract Root Failure:** Read the exact exception line, error code, and stack trace.
2. **Formulate Single Falsifiable Hypothesis:** State clearly: *"Function X failed because input Y caused condition Z."*
3. **Isolate with Test:** If not already covered, write a 5-line unit test isolating the exact edge case.
4. **Surgical Patch:** Edit only the lines necessary to satisfy the assertion. Do not refactor unrelated subsystems.
