import re
from pathlib import Path
import pytest


def test_demo_index_html_exists_and_contains_core_elements():
    doc = Path("docs/index.html")
    assert doc.exists()
    content = doc.read_text()
    assert "agent-readiness" in content
    assert "unprepared" in content
    assert "unconfigured" in content
    assert "fastmcp" in content
    assert "guarded" in content
    assert "Auto-Onboard" in content


def test_demo_no_revert_button_rendered():
    content = Path("docs/index.html").read_text()
    assert "Revert to Initial" not in content, "Revert button should not be present in final git diff step"


def test_demo_javascript_syntax_and_integrity():
    doc = Path("docs/index.html")
    content = doc.read_text()

    # Extract javascript
    m = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    assert m is not None, "Missing inline script in docs/index.html"
    code = m.group(1)

    # Validate delimiter balance
    assert code.count("{") == code.count("}"), "Unbalanced braces in docs/index.html script"
    assert code.count("[") == code.count("]"), "Unbalanced brackets in docs/index.html script"
    assert code.count("(") == code.count(")"), "Unbalanced parens in docs/index.html script"

    # Validate depth never drops below zero
    depth = 0
    in_backtick = False
    for line in code.splitlines():
        for ch in line:
            if ch == "`":
                in_backtick = not in_backtick
            elif not in_backtick:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    assert depth >= 0, f"Negative brace depth encountered: {line}"
    assert depth == 0

    # Ensure all interactive functions are declared
    required_fns = [
        "switchTab", "selectSampleRepo", "renderSampleRepo",
        "selectFile", "renderSelectedFile", "autoOnboardCurrentRepo"
    ]
    for fn in required_fns:
        assert f"function {fn}" in code, f"Missing function {fn} in docs/index.html"


def test_readme_and_architecture_exist():
    readme = Path("README.md")
    arch = Path("ARCHITECTURE.md")
    design = Path("DESIGN.md")
    agents = Path("AGENTS.md")
    assert readme.exists() and readme.stat().st_size > 100
    assert arch.exists() and arch.stat().st_size > 100
    assert design.exists() and design.stat().st_size > 100
    assert agents.exists() and agents.stat().st_size > 100
    assert "ARCHITECTURE.md" in agents.read_text()
    assert "DESIGN.md" in agents.read_text()
    assert "https://zcdlab.github.io/agent-readiness-evals/" in readme.read_text()


def test_demo_diff_renderer_functions_declared():
    doc = Path("docs/index.html")
    content = doc.read_text()
    assert "function computeReadinessDiff" in content, "Missing function computeReadinessDiff"
    assert "function renderDiffTable" in content, "Missing function renderDiffTable"


def test_demo_tab1_diff_container_present():
    content = Path("docs/index.html").read_text()
    assert 'id="readiness-diff-container"' in content, "Missing #readiness-diff-container in docs/index.html"


def test_demo_all_archetype_file_arrays_defined():
    content = Path("docs/index.html").read_text()
    m = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    assert m is not None
    code = m.group(1)

    expected_arrays = [
        "initialUnpreparedFiles", "onboardedUnpreparedFiles",
        "initialFastMcpFiles", "onboardedFastMcpFiles",
        "initialUnconfiguredFiles", "onboardedUnconfiguredFiles",
        "initialGuardedFiles", "onboardedGuardedFiles",
        "initialReadyFiles"
    ]
    for arr in expected_arrays:
        assert f"const {arr}" in code, f"Missing declaration of {arr} in docs/index.html script"


def test_demo_sample_repos_keys_and_buttons():
    content = Path("docs/index.html").read_text()
    archetypes = ["unprepared", "fastmcp", "unconfigured", "guarded"]
    for arch in archetypes:
        assert f'id="btn-repo-{arch}"' in content, f"Missing button for archetype {arch}"
        assert f'id="card-badge-{arch}"' in content, f"Missing score badge for archetype {arch}"


def test_demo_get_element_by_id_integrity():
    content = Path("docs/index.html").read_text()
    m = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    assert m is not None
    code = m.group(1)

    static_ids = re.findall(r"document\.getElementById\([\"\x27]([a-zA-Z0-9_\-]+)[\"\x27]\)", code)
    all_html_ids = set(re.findall(r"id=[\"\x27]([a-zA-Z0-9_\-]+)[\"\x27]", content))

    missing = [i for i in set(static_ids) if i not in all_html_ids]
    assert not missing, f"Script references non-existent HTML IDs: {missing}"


def test_demo_concrete_diff_examples():
    content = Path("docs/index.html").read_text()
    # Ensure artificial placeholder comments and dummy assertions are removed
    assert "assert True" not in content, "Dummy test assertion 'assert True' should not exist in demo"
    assert "# Missing architectural guidelines" not in content, "Trivial placeholder comment should be replaced with concrete code"
    assert "# Verified against AGENTS.md contract" not in content, "Trivial placeholder comment should be replaced with concrete code"

    # Ensure realistic domain invariants and concrete code are present
    assert "idempotency_key" in content, "Scenario 4 should demonstrate concrete idempotency key contract"
    assert "amount_cents" in content, "Scenario 4 should demonstrate concrete integer cent monetary invariants"
    assert "PaymentGatewayConfig" in content, "Scenario 1 should demonstrate concrete configuration abstraction"




