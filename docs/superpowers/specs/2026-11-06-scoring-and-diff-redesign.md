# Spec: 4-Archetype Interactive Repository Evaluator & Git Diff Viewer

## Goal
Transform `agent-readiness-evals` into a high-impact, single-page interactive experience with 4 distinct repository archetypes spanning the entire readiness spectrum (0%, 25%, 50%, 75%). Each archetype follows a deterministic two-step loop:
1. **Scoring & Why**: Shows initial score, grade, 4-pillar breakdown, risk diagnostic, and files with sensitive secrets highlighted in red font only.
2. **Apply Change (Git Diff)**: User clicks `⚡ Apply Readiness Fix (readiness fix)`. Engine applies the fix, escalates score to 100/100, and displays a clean unified git diff (`-` red deletions, `+` green additions). No revert button is shown after applying changes.

## Archetypes
1. **0/100 [F - Unprepared]**: `unprepared_service` — Bare script, exposed `.env` Stripe/AWS keys, unquarantined Terraform, no tests, no policy, no operating contract.
2. **25/100 [D - Unverified]**: `fastmcp_service` — FastMCP tool service with `pyproject.toml`, but zero tests, unconstrained tool execution, and no policy/guidelines.
3. **50/100 [C - High Blast Risk]**: `unconfigured_service` — Bazel + Python microservice with tests, but zero agent boundaries. Agents have unrestricted write access to root Terraform.
4. **75/100 [B - Moderately Ready]**: `guarded_service` — FastAPI backend with tests, build spec, and zero-trust policy, but missing `AGENTS.md` (no operating contract or verification ladder).

## UI & Architecture Changes
- **Remove Tab 2 ("Anatomy of an Agent-Ready Repository") and `<nav>`**: Make the application single-page, eliminating theoretical text tables.
- **Top Selector**: 4 responsive archetype cards (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).
- **Scorecard HUD**: 4 pillars with exact points (0 or 25) and failure/pass reasons.
- **Action Button**:
  - Initial state: `⚡ Apply Readiness Fix (readiness fix)` (blue, clickable).
  - After fix: `✓ Applied (100/100) — Git Diff Active` (emerald, disabled). NO revert button.
- **Git Diff Viewer**:
  - Pre-fix: Clean neutral lines, line numbers, red font on secrets.
  - Post-fix: Git-style unified diff with `-` for deletions, `+` for additions.

## Verification
- Delimiter balance depth check depth == 0.
- All 20 unit tests in pytest pass.
- Deploy to `main` and `gh-pages` on GitHub.

