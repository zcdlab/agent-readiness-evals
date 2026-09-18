from pathlib import Path
import pytest
from src.cli import main as cli_main
from src.models import PermissionTier, ReadinessReport
from src.onboarder import onboard_repository
from src.scanner import scan_repository


def test_permission_tier_enum():
    assert PermissionTier.READ_ONLY == "read_only"
    assert PermissionTier.SANDBOX_WRITE == "sandbox_write"
    assert PermissionTier.PROD_MUTATE == "prod_mutate"


def test_scan_unconfigured_repo(tmp_path: Path):
    (tmp_path / "BUILD.bazel").write_text("# bazel")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'")
    (tmp_path / "tests").mkdir()
    (tmp_path / "infra" / "prod").mkdir(parents=True)
    (tmp_path / "infra" / "prod" / "main.tf").write_text("resource 'aws_s3' {}")

    report = scan_repository(tmp_path)
    assert isinstance(report, ReadinessReport)
    assert report.score_before == 50
    assert "bazel" in report.detected_stack
    assert "python" in report.detected_stack
    assert "infra/prod/" in report.discovered_sensitive_paths
    assert ".agent-policy.yaml" in report.missing_safeguards
    assert "AGENTS.md" in report.missing_safeguards
    assert report.grade == "C - High Blast Risk"


def test_scan_legacy_bare_repo(tmp_path: Path):
    (tmp_path / "script.py").write_text("print('hello')")
    (tmp_path / ".env").write_text("SECRET=123")

    report = scan_repository(tmp_path)
    assert report.score_before == 0
    assert report.grade == "F - Unprepared"
    assert ".env" in report.discovered_sensitive_paths


def test_onboard_repository_escalates_to_100(tmp_path: Path):
    (tmp_path / "package.json").write_text("{\"name\": \"app\"}")
    (tmp_path / "tests").mkdir()
    (tmp_path / "security").mkdir()
    (tmp_path / "security" / "vault.py").write_text("# vault")

    report = onboard_repository(tmp_path, write_files=True)
    assert report.score_before == 50
    assert report.score_after == 100
    assert report.grade == "A - Enterprise Agent Ready"
    assert report.missing_safeguards == []

    policy = (tmp_path / ".agent-policy.yaml").read_text()
    assert "security/" in policy
    assert ".agent-policy.yaml" in policy

    agents = (tmp_path / "AGENTS.md").read_text()
    assert "Agent Operating Guidelines" in agents


def test_onboard_repository_idempotent(tmp_path: Path):
    (tmp_path / "BUILD.bazel").write_text("# bazel")
    (tmp_path / "tests").mkdir()

    r1 = onboard_repository(tmp_path, write_files=True)
    assert r1.score_after == 100

    r2 = onboard_repository(tmp_path, write_files=True)
    assert r2.score_before == 100
    assert r2.score_after == 100


def test_cli_scan_and_fix(tmp_path: Path, capsys):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'svc'")
    (tmp_path / "tests").mkdir()

    assert cli_main(["scan", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Readiness Score: 50/100" in out

    assert cli_main(["fix", str(tmp_path)]) == 0
    out2 = capsys.readouterr().out
    assert "Score: 50/100 -> 100/100" in out2

    assert cli_main(["scan", str(tmp_path), "--json"]) == 0
    out3 = capsys.readouterr().out
    assert '"score_before": 100' in out3
