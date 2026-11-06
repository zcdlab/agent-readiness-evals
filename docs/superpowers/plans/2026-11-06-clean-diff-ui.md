# Clean Unified Diff UI Implementation Plan for Agent Readiness Evals

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the file viewer in `agent-readiness-evals` into a line-numbered code and unified diff viewer while eliminating top callout banners and visual noise.

**Architecture:** Introduce `computeReadinessDiff` and `renderDiffTable` in `docs/index.html` that contrast pre-onboard and post-onboard file states. In pre-onboard state, files are displayed as clean neutral rows with red font on sensitive tokens (`sk_live_`, `AKIA`, `postgres://`) without `-` diff markers. In post-onboard state, quarantined files display unified diffs (`-` removed unprotected lines, `+` added policy lines) and synthesized contracts display `+` additions.

**Tech Stack:** Vanilla JavaScript (ES6+), HTML5, Tailwind CSS, Python / pytest.

**Spec:** [`docs/superpowers/specs/2026-11-06-clean-diff-ui-design.md`](file:///Users/zcd/.gemini/antigravity/scratch/agent-readiness-evals/docs/superpowers/specs/2026-11-06-clean-diff-ui-design.md)

## Global Constraints

- Preserve all existing required functions in `docs/index.html`: `switchTab`, `selectSampleRepo`, `renderSampleRepo`, `selectFile`, `renderSelectedFile`, `autoOnboardCurrentRepo`, `runCliSim`.
- Preserve delimiter balance: `{` matching `}`, `[` matching `]`, `(` matching `)`.
- Zero external npm dependencies or heavy third-party CSS/JS packages.
- All core scanner and CLI tests in `tests/` must remain passing.

## Review Focus

1. **Auto-generated contracts**: Ensure `.agent-policy.yaml`, `AGENTS.md`, and `pyproject.toml` render with green `+` indicators when onboarded.
2. **Quarantined files**: Ensure `.env` and `infra/prod/main.tf` render neutral rows with red font before onboarding, and render a unified diff after onboarding.
3. **Unchanged files**: Ensure files like `src/app.py` or `BUILD.bazel` render clean neutral rows without false-positive diff signs.
4. **Reverting to initial state**: Ensure clicking `↺ Revert to Initial` cleanly restores the pre-onboard view.
5. **Anti-caching**: Ensure `<head>` includes no-cache meta tags to prevent stale edge caching.

---

### Task 1: Diff Computation and Formatting Utility in `docs/index.html`

**Files:**
- Modify: `docs/index.html`
- Test: `tests/test_demo.py`

**Interfaces:**
- Produces: `highlightReadinessSecrets(line) -> string`
- Produces: `computeReadinessDiff(currentFile, isRepoOnboarded, initialFile) -> Array<Row>`
- Produces: `renderDiffTable(rows) -> string`

- [ ] **Step 1: Write failing test in `tests/test_demo.py`**

Add assertion in `tests/test_demo.py` checking for `computeReadinessDiff` and `renderDiffTable`.

```python
def test_demo_diff_renderer_functions_declared():
    doc = Path("docs/index.html")
    content = doc.read_text()
    assert "function computeReadinessDiff" in content
    assert "function renderDiffTable" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_demo.py::test_demo_diff_renderer_functions_declared -v`
Expected: FAIL

- [ ] **Step 3: Implement `highlightReadinessSecrets`, `computeReadinessDiff`, and `renderDiffTable` in `docs/index.html`**

- `highlightReadinessSecrets`: wraps `sk_live_`, `AKIA`, `DATABASE_URL=`, `STRIPE_SECRET_KEY=`, `open('/etc/passwd')` in `<span class="text-red-600 font-semibold">`.
- `computeReadinessDiff`:
  - If `!isRepoOnboarded`: neutral rows with `oldNum`, `newNum`, `sign: ' '`, `htmlText: highlightReadinessSecrets(line)`.
  - If `isRepoOnboarded`:
    - If `currentFile.isGenerated`: all rows `type: 'add'`, `sign: '+'`.
    - If `initialFile` exists and differed: computes unified diff with common prefix/suffix, `-` for initial lines, `+` for quarantined lines.
    - If unchanged: neutral rows.
- `renderDiffTable`: renders clean line-numbered table with Tailwind styles.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_demo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_demo.py docs/index.html
git commit -m "feat(ui): add diff computation and rendering utility to readiness evals" --author="zcdlab <zcdlab@users.noreply.github.com>"
```

---

### Task 2: Streamline Tab 1 DOM and Replace Textarea with Diff Viewer

**Files:**
- Modify: `docs/index.html`
- Test: `tests/test_demo.py`

**Interfaces:**
- Consumes: `computeReadinessDiff`, `renderDiffTable`
- Modifies: `renderSelectedFile()`

- [ ] **Step 1: Write failing test in `tests/test_demo.py`**

```python
def test_demo_tab1_diff_container_present():
    content = Path("docs/index.html").read_text()
    assert 'id="readiness-diff-container"' in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_demo.py::test_demo_tab1_diff_container_present -v`
Expected: FAIL

- [ ] **Step 3: Streamline Tab 1 DOM and integrate diff viewer**

- Remove top "Execution Architecture" banner.
- Remove "Focused When to Use Callout" card.
- Add `<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">` to `<head>`.
- Replace `<textarea id="editor-textarea">` with `<div id="readiness-diff-container">`.
- Update `renderSelectedFile()` to compute and render diff.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_demo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/index.html tests/test_demo.py
git commit -m "feat(ui): streamline Tab 1 DOM and replace textarea with clean diff viewer" --author="zcdlab <zcdlab@users.noreply.github.com>"
```

---

### Task 3: Sync Artifacts, Verify Full Suite, and Deploy to Remote

**Files:**
- Sync: `docs/index.html` -> `index.html`
- Sync: `docs/index.html` -> `/Users/zcd/.gemini/antigravity/brain/a9b74abc-c0f8-41ed-8eae-fb80a7a5a177/interactive_demo.html`
- Branch: `gh-pages`

- [ ] **Step 1: Copy `docs/index.html` to root `index.html` and brain artifact**

```bash
cp docs/index.html index.html
cp docs/index.html /Users/zcd/.gemini/antigravity/brain/a9b74abc-c0f8-41ed-8eae-fb80a7a5a177/interactive_demo.html
```

- [ ] **Step 2: Run complete pytest suite**

Run: `.venv/bin/pytest -v`
Expected: All tests pass.

- [ ] **Step 3: Commit and update `gh-pages`**

```bash
git add index.html
git commit -m "deploy: update root demo with clean diff UI" --author="zcdlab <zcdlab@users.noreply.github.com>"
git checkout gh-pages
git checkout main -- docs/index.html index.html
git add docs/index.html index.html
git commit -m "deploy: update gh-pages with clean diff UI" --author="zcdlab <zcdlab@users.noreply.github.com>"
git checkout main
```

- [ ] **Step 4: Push to origin**

Run: `git push origin main gh-pages` (with BypassSandbox: true and toolSummary "Push branches to remote")

- [ ] **Step 5: Verify live endpoint**

Run: `curl -sI "https://zcdlab.github.io/agent-readiness-evals/"`
Expected: HTTP 200.

