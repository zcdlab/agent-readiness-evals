from pathlib import Path
from src.models import ReadinessPillar, ReadinessReport

SENSITIVE_TARGETS = ["infra/prod/", "security/", "db/migrations/", "proto/", ".env"]
BUILD_TARGETS = [("bazel", "BUILD.bazel"), ("python", "pyproject.toml"), ("node", "package.json"), ("rust", "Cargo.toml"), ("go", "go.mod")]


def scan_repository(repo_path: Path | str) -> ReadinessReport:
    p = Path(repo_path).resolve()
    stack = [name for name, marker in BUILD_TARGETS if (p / marker).exists()]
    sens = [s for s in SENSITIVE_TARGETS if (p / s.rstrip("/")).exists()]

    has_build = len(stack) > 0
    has_tests = (p / "tests").is_dir() or (p / "test").is_dir()
    has_policy = (p / ".agent-policy.yaml").exists()
    has_agents = (p / "AGENTS.md").exists() or (p / "CLAUDE.md").exists()

    pillars = [
        ReadinessPillar(name="Build & Dependency Specs", score=25 if has_build else 0, passed=has_build,
                        details=f"Detected: {', '.join(stack)}" if has_build else "Missing reproducible build config"),
        ReadinessPillar(name="Verification Test Harness", score=25 if has_tests else 0, passed=has_tests,
                        details="Automated test suite present" if has_tests else "Missing test harness directory"),
        ReadinessPillar(name="Blast-Radius Boundary Policy", score=25 if has_policy else 0, passed=has_policy,
                        details="Zero-trust path boundary active" if has_policy else "Missing .agent-policy.yaml"),
        ReadinessPillar(name="Agent Operating Guidelines", score=25 if has_agents else 0, passed=has_agents,
                        details="Guidelines active in repository" if has_agents else "Missing AGENTS.md contract"),
    ]

    score = sum(pi.score for pi in pillars)
    grade = "A - Enterprise Agent Ready" if score == 100 else "B - Moderately Ready" if score >= 75 else "C - High Blast Risk" if score >= 50 else "F - Unprepared"
    missing = [m for m, ok in [(".agent-policy.yaml", has_policy), ("AGENTS.md", has_agents)] if not ok]

    prot = sorted(set(sens + [".agent-policy.yaml"]))
    paths_str = "".join(f"  - {x}\n" for x in prot)
    yaml_txt = (
        f"# Zero-Trust AI Agent Policy Contract\nversion: '1.0'\npermission_tier: sandbox_write\nenforcement: strict\n"
        f"protected_paths:\n{paths_str}allowed_tools:\n  - file_read\n  - file_edit\n  - run_command\n"
        f"command_rules:\n  banned:\n    - 'rm -rf*'\n    - '*curl*|*sh*'\n    - 'git push --force*'\n"
        f"verification_hooks:\n  pre_commit_gate: 'pytest -v --tb=short tests/'\n"
    )

    doc_links = [f"- [{d}]({d}): Core architectural topology and invariants" for d in ["ARCHITECTURE.md", "DESIGN.md"] if (p / d).exists()]
    docs_block = "\n".join(doc_links) or "- [ARCHITECTURE.md](ARCHITECTURE.md): System boundaries and topology"

    md_txt = (
        f"# Agent Operating Guidelines & Harness Engineering Contract\n\n"
        f"> **First Principles:** Models are stochastic token predictors. Without an execution harness, "
        f"agents suffer from context drift and undetected regressions. All actions here are bounded and test-gated.\n\n"
        f"## 1. Architectural & Design Anchor Points\n{docs_block}\n\n"
        f"## 2. Multi-Tier Verification Ladder\n"
        f"1. Tier 1 (Unit Loop): Fast sub-second test execution (`pytest -k <func>`, budget < 0.2s)\n"
        f"2. Tier 2 (Static Checks): `ruff check` linting and `mypy --strict` type verification\n"
        f"3. Tier 3 (Full Regression Gate): `pytest -v --tb=short tests/` (100% green required)\n"
        f"4. Tier 4 (CI Telemetry): `pytest --junitxml=.agent/results.xml`\n\n"
        f"## 3. Environment & Boundaries\n"
        f"- Detected Stack: {', '.join(stack) or 'general'}\n"
        f"- Permission Tier: `sandbox_write` (scoped strictly to `src/` and `tests/`)\n"
        f"- Quarantined Paths (Read-Only): {', '.join(prot)}\n"
        f"- Invariant: Never mark task complete or push commits if any test fails.\n"
    )

    return ReadinessReport(repo_name=p.name, score_before=score, score_after=score, grade=grade,
                           detected_stack=stack, discovered_sensitive_paths=sens, pillars=pillars,
                           missing_safeguards=missing, generated_policy_yaml=yaml_txt, generated_agents_md=md_txt)
