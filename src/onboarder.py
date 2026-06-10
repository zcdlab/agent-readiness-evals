from pathlib import Path
from src.models import ReadinessReport
from src.scanner import scan_repository


def onboard_repository(repo_path: Path | str, write_files: bool = True) -> ReadinessReport:
    p = Path(repo_path).resolve()
    rep = scan_repository(p)
    if write_files:
        (p / ".agent-policy.yaml").write_text(rep.generated_policy_yaml)
        (p / "AGENTS.md").write_text(rep.generated_agents_md)
        after = scan_repository(p)
        rep.score_after = after.score_before
        rep.grade = after.grade
        rep.missing_safeguards = []
    return rep
