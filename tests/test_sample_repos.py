from pathlib import Path
import pytest
from src.scanner import scan_repository


def test_unprepared_service_scores_zero():
    rep = scan_repository("examples/unprepared_service")
    assert rep.score_before == 0
    assert rep.grade == "F - Unprepared"
    assert "infra/prod/" in rep.discovered_sensitive_paths
    assert ".env" in rep.discovered_sensitive_paths
    assert len(rep.missing_safeguards) == 2


def test_agent_ready_service_scores_one_hundred():
    rep = scan_repository("examples/agent_ready_service")
    assert rep.score_before == 100
    assert rep.grade == "A - Enterprise Agent Ready"
    assert rep.missing_safeguards == []
    assert all(p.passed for p in rep.pillars)

    # Verify architecture, design, and agent guidelines contracts
    p = Path("examples/agent_ready_service")
    assert (p / "ARCHITECTURE.md").exists()
    assert (p / "DESIGN.md").exists()
    agents_md = (p / "AGENTS.md").read_text()
    assert "ARCHITECTURE.md" in agents_md
    assert "DESIGN.md" in agents_md
    assert "Multi-Tier Verification Ladder" in agents_md


def test_unconfigured_service_scores_fifty():
    rep = scan_repository("examples/unconfigured_service")
    assert rep.score_before == 50
    assert "bazel" in rep.detected_stack
    assert "python" in rep.detected_stack

