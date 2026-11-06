# Short Design Doc: Clean Diff UI for Agent Readiness Evals

## Intent & The Why
Apply the clean unified diff display and visual noise reduction established in `agent-guardrail` to `agent-readiness-evals`, replacing the plain textarea with a line-numbered diff viewer and eliminating marketing banners and redundant alert clutter.

## Goals
- **Unified Diff Viewer**: Replace `<textarea id="editor-textarea">` with a GitHub/VS Code-style diff table displaying line numbers, diff signs (`+`/`-`/` `), and syntax formatting.
  - **Pre-Fix State** (0% or 50% initial state):
    - Neutral line numbers (`1`, `2`, `3`...).
    - White row background, no `-` deletion markers.
    - Plaintext secrets (`sk_live_...`, `AKIA...`, `DATABASE_URL=...`) and unquarantined paths highlighted with **red font color only** (`<span class="text-red-600 font-semibold">`).
  - **Post-Fix State** (after clicking "Auto-Onboard"):
    - Quarantined files (`.env`, `infra/prod/main.tf`): Displays unified diff comparing unprotected lines (`-` in red) with zero-trust quarantined lines (`+` in green).
    - Newly synthesized contracts (`.agent-policy.yaml`, `AGENTS.md`, `pyproject.toml`, `tests/test_app.py`): Displays code with green `+` indicators and an `✨ AUTO-GENERATED` tag.
- **De-clutter & Noise Reduction**:
  - Remove top "Execution Architecture" callout banner from `<main>`.
  - Remove verbose "Focused When to Use Callout" card ("The Core Premise of Harness Engineering...").
  - Streamline the inspector container: Target Codebase selector, 4-pillar scorecard, File tree on left, clean File/Diff Viewer on right.
- **Maintain Test Suite & Delimiter Balance**:
  - Keep 100% test pass rate in `tests/test_demo.py` and `tests/`.
  - Maintain balanced JavaScript delimiters (`{`, `[`, `(`).

