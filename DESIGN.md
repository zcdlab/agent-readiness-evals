# Design Specification: agent-readiness

> **Platform Philosophy:**  
> Autonomous coding agents require deterministic boundaries. This document specifies the domain abstractions, state transitions, scoring rubric, and design patterns governing `agent-readiness`.

---

## 1. Domain Modeling & Core Abstractions

The system is built on immutable Pydantic v2 schemas:

- **`PermissionTier(StrEnum)`**:
  - `READ_ONLY`: Code exploration, AST analysis, dependency inspection.
  - `SANDBOX_WRITE`: Scoped mutation in `src/` and `tests/`.
  - `PROD_MUTATE`: Cloud infrastructure or release modification (strictly human-gated).
- **`ReadinessPillar`**: Encapsulates one of the 4 independent evaluation pillars (name, score: 0 or 25, passed: bool, details: str).
- **`ReadinessReport`**: Comprehensive evaluation snapshot containing before/after scores, detected technology stacks, sensitive directories discovered, pillar statuses, and synthesized contract strings.

---

## 2. Deterministic Scoring Rubric

The readiness score is computed as a pure function:

$$\text{Score} = \sum_{i=1}^{4} \text{Pillar}_i.\text{score} \in \{0, 25, 50, 75, 100\}$$

| Pillar | Condition | Points |
| :--- | :--- | :--- |
| **Build & Dependencies** | Manifest exists (`pyproject.toml`, `BUILD.bazel`, `package.json`, `Cargo.toml`, `go.mod`) | 25 pts |
| **Verification Test Harness** | Test directory exists (`tests/`, `test/`) | 25 pts |
| **Blast-Radius Policy** | `.agent-policy.yaml` active and quarantining sensitive paths | 25 pts |
| **Operating Guidelines** | `AGENTS.md` (or `CLAUDE.md`) active with runtime contracts | 25 pts |

### Grade Mapping
- **`100`**: `A - Enterprise Agent Ready`
- **`75`**: `B - Moderately Ready`
- **`50`**: `C - High Blast Risk`
- **`< 50`**: `F - Unprepared`

---

## 3. Idempotent Auto-Onboarding Pattern

When `readiness fix` is executed:
1. Performs non-destructive scan of the target filesystem.
2. Identifies all sensitive directories (`infra/prod/`, `security/`, `db/migrations/`, `proto/`, `.env`).
3. Synthesizes tailored `.agent-policy.yaml` locking those paths.
4. Synthesizes tailored `AGENTS.md` linking to architecture specifications and defining verification loops.
5. Re-scans the repository to prove score elevation to $100/100$.
6. **Idempotence Invariant:** Subsequent executions produce no diff and leave `score_before == 100` and `score_after == 100`.

