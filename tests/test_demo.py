import re
from pathlib import Path
import pytest


def test_demo_index_html_exists_and_contains_core_elements():
    doc = Path("docs/index.html")
    assert doc.exists()
    content = doc.read_text()
    assert "agent-readiness" in content
    assert 'What Makes a Repository "Agent-Ready"?' in content
    assert "The 4 Foundations of Harness Engineering" in content
    assert "unconfigured_service" in content
    assert "agent_ready_service" in content
    assert "Auto-Onboard" in content


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


