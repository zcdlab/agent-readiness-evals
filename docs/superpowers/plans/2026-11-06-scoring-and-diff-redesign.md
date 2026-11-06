# Plan: 4-Archetype Interactive Repository Evaluator & Git Diff Viewer

## Tasks

### Task 1: Update Test Suite for Single-Page Layout and 4 Archetypes
- File: `tests/test_demo.py`
- Replace assertions for removed Tab 2 text with assertions for the 4-pillar scorecard and 4 archetypes.
- Ensure delimiter and depth balance checks continue to pass.

### Task 2: Implement 4 Archetypes Data Model and Git Diff Logic
- File: `docs/index.html`
- Define 4 repository fixture datasets:
  - `unprepared` (0/100)
  - `fastmcp` (25/100)
  - `unconfigured` (50/100)
  - `guarded` (75/100)
- Update `computeReadinessDiff()` to correctly resolve initial vs current files for all 4 archetypes.
- Update `autoOnboardCurrentRepo()`:
  - Onboard to 100/100 with simulated synthesis HUD.
  - Disable action button and set label to `✓ Applied (100/100) — Git Diff Active`.
  - Remove all revert-to-initial branches.

### Task 3: Streamline DOM into Single-Page Layout
- File: `docs/index.html`
- Remove `<nav>` and Tab 2 `<section id="tab-anatomy">`.
- Update archetype selector to 4 responsive cards (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).
- Update file tree, 4-pillar scorecard, and safety diagnostic card.

### Task 4: Verify Full Suite, Sync Artifacts, and Deploy
- Run `.venv/bin/pytest -v`.
- Sync `docs/index.html` to root `index.html` and brain artifact `interactive_demo.html`.
- Commit changes and push to `main` and `gh-pages` on `git@github.com:zcdlab/agent-readiness-evals.git`.

