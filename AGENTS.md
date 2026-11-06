# Agent Operating Guidelines & Platform Contract

> **System Mental Model:**  
> Autonomous coding agents operating in `agent-readiness` must follow strict harness engineering discipline. Treat this document as your primary operating contract.

---

## 1. Architectural & Design Anchor Points

Before mutating any code or proposing refactors, agents must inspect:
- [**`ARCHITECTURE.md`**](file:///Users/zcd/.gemini/antigravity/scratch/agent-readiness-evals/ARCHITECTURE.md): System topology, non-destructive filesystem traversal pipeline, and component responsibilities.
- [**`DESIGN.md`**](file:///Users/zcd/.gemini/antigravity/scratch/agent-readiness-evals/DESIGN.md): Pydantic schema contracts, deterministic scoring function ($0 \le \text{Score} \le 100$), and idempotent contract synthesis invariants.

---

## 2. Differentiated Testing & Multi-Tier Verification Ladder

Testing in this repository is structured into 4 distinct verification tiers:

```
[Tier 1: Sub-Second Targeted Unit Loop] ──> pytest tests/test_scanner.py -k <name> (< 0.2s)
                     │
                     ▼
[Tier 2: Static Contract & Type Safety]  ──> ruff check src/ tests/ && mypy --strict src/
                     │
                     ▼
[Tier 3: Full Regression Suite]          ──> pytest -v tests/ (< 0.5s, 100% green required)
                     │
                     ▼
[Tier 4: Idempotence & Boundary Fuzzing] ──> Test multi-pass execution & sensitive path lockout
```

### Verification Command Reference

| Verification Tier | Command | Latency SLA | Invariant Required |
| :--- | :--- | :--- | :--- |
| **Fast Targeted** | `pytest tests/test_scanner.py -k <name>` | `< 0.2s` | Immediate feedback on edited function |
| **Linting** | `ruff check src/ tests/` | `< 0.5s` | Zero style or unused import violations |
| **Type Check** | `mypy --strict src/` | `< 1.0s` | Zero type errors on Pydantic schemas |
| **Full Regression** | `pytest -v tests/` | `< 1.0s` | 100% green across all 12+ tests |
| **CLI Verification**| `readiness scan examples/unconfigured_service` | `< 0.1s` | Deterministic score output |

**Core Invariant:** Never commit code or open PRs if any tier in the ladder fails.

---

## 3. Blast Radius Boundaries & Permissions

- **Permission Tier:** `sandbox_write` (scoped strictly to `src/` and `tests/`).
- **Protected Paths (Read-Only):**
  - `.github/workflows/` — Production CI/CD pipelines.
  - `.agent-policy.yaml` — Security governance policy.
  - `LICENSE` — Legal distribution contract.
- **Size Bounds:** Every Python module in `src/` must remain under 85 lines of code with zero filler comments.
