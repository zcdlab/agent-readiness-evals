import json
from pathlib import Path
from src.scanner import scan_repository


def test_golden_cases_file_integrity():
    eval_file = Path("evals/golden_cases.json")
    assert eval_file.exists()
    data = json.loads(eval_file.read_text())
    assert data["version"] == "1.0"
    assert len(data["cases"]) == 3

    case_map = {c["id"]: c for c in data["cases"]}
    assert "unprepared_service" in case_map
    assert "unconfigured_service" in case_map
    assert "agent_ready_service" in case_map


def test_golden_cases_match_scanned_repositories():
    eval_file = Path("evals/golden_cases.json")
    data = json.loads(eval_file.read_text())

    for case in data["cases"]:
        repo_path = Path(case["path"])
        if repo_path.exists():
            rep = scan_repository(repo_path)
            assert rep.score_before == case["score_before"]
            assert rep.grade == case["grade_before"]

