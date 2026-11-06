from pathlib import Path
import pytest
from src.cli import main as cli_main
from src.onboarder import onboard_repository
from src.scanner import scan_repository


def test_scan_go_repository(tmp_path: Path):
    (tmp_path / "go.mod").write_text("module example.com/api\n\ngo 1.22\n")
    (tmp_path / "api_test.go").write_text("package main\nimport \"testing\"\nfunc TestAPI(t *testing.T) {}\n")

    rep = scan_repository(tmp_path)
    assert "go" in rep.detected_stack
    assert rep.pillars[0].passed is True  # Build
    assert rep.pillars[1].passed is True  # Tests
    assert rep.pillars[2].passed is False  # Missing .agent-policy.yaml
    assert rep.pillars[3].passed is False  # Missing AGENTS.md
    assert rep.score_before == 50
    assert "go test ./..." in rep.generated_policy_yaml


def test_scan_rust_repository(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text("[package]\nname = \"core\"\nversion = \"0.1.0\"\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "integration_test.rs").write_text("// test")

    rep = scan_repository(tmp_path)
    assert "rust" in rep.detected_stack
    assert rep.pillars[0].passed is True
    assert rep.pillars[1].passed is True
    assert rep.score_before == 50
    assert "cargo test" in rep.generated_policy_yaml


def test_cli_markdown_output(tmp_path: Path, capsys):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'")
    (tmp_path / "tests").mkdir()

    assert cli_main(["scan", str(tmp_path), "--markdown"]) == 0
    out = capsys.readouterr().out
    assert "# 📊 Agent Readiness Report" in out
    assert "| Build & Dependency Specs | ✅ PASS | 25/25 |" in out
    assert "| Blast-Radius Boundary Policy | ❌ FAIL | 0/25 |" in out
    assert "## 💡 Remediation Recommendations" in out


def test_cli_min_score_threshold(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'")

    # Score will be 25 (only build specs)
    # Passes if min-score <= 25
    assert cli_main(["scan", str(tmp_path), "--min-score", "25"]) == 0
    # Fails with exit code 1 if min-score is 75
    assert cli_main(["scan", str(tmp_path), "--min-score", "75"]) == 1


def test_cli_fix_dry_run_preview(tmp_path: Path, capsys):
    (tmp_path / "package.json").write_text("{\"name\": \"web-app\"}")
    (tmp_path / "tests").mkdir()

    assert cli_main(["fix", str(tmp_path), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "[DRY-RUN] Auto-Onboarding Preview" in out
    assert "Projected Score: 50/100 -> 100/100" in out
    assert "--- .agent-policy.yaml ---" in out
    assert "--- AGENTS.md ---" in out

    # Files must NOT have been written
    assert not (tmp_path / ".agent-policy.yaml").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_cli_init_command(tmp_path: Path, capsys):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'init-test'")
    (tmp_path / "tests").mkdir()

    assert cli_main(["init", str(tmp_path)]) == 0
    assert (tmp_path / ".agent-policy.yaml").exists()
    assert (tmp_path / "AGENTS.md").exists()
