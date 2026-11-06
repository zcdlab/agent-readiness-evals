from pathlib import Path
from src.llm import synthesize_contracts
from src.models import ReadinessReport
from src.scanner import scan_repository


def onboard_repository(repo_path: Path | str, write_files: bool = True, force_llm: bool = False) -> ReadinessReport:
    p = Path(repo_path).resolve()
    rep = scan_repository(p)
    if write_files:
        yaml_txt, md_txt, _ = synthesize_contracts(rep, force_llm=force_llm)
        (p / ".agent-policy.yaml").write_text(yaml_txt)
        (p / "AGENTS.md").write_text(md_txt)
        after = scan_repository(p)
        rep.score_after = after.score_before
        rep.grade = after.grade
        rep.missing_safeguards = []
    return rep
