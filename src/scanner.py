from pathlib import Path
import time
from src.models import ReadinessPillar, ReadinessReport

CORE_SENSITIVE_TARGETS = ["infra/prod/", "security/", "db/migrations/", "proto/", ".env"]
ADDITIONAL_SENSITIVE_TARGETS = ["secrets/", "credentials/", "certs/", ".env.production", ".env.local"]

CORE_BUILD_TARGETS = [
    ("bazel", "BUILD.bazel"),
    ("python", "pyproject.toml"),
    ("node", "package.json"),
    ("rust", "Cargo.toml"),
    ("go", "go.mod"),
]

ADDITIONAL_BUILD_TARGETS = [
    ("python", "setup.py"),
    ("python", "requirements.txt"),
    ("python", "Pipfile"),
    ("node", "tsconfig.json"),
    ("c/cpp", "Makefile"),
    ("c/cpp", "CMakeLists.txt"),
    ("java", "pom.xml"),
    ("java", "build.gradle"),
    ("container", "Dockerfile"),
    ("container", "docker-compose.yml"),
]


def scan_repository(repo_path: Path | str) -> ReadinessReport:
    t0 = time.perf_counter()
    p = Path(repo_path).resolve()

    # Detect stack: prioritize CORE_BUILD_TARGETS first, then additional targets without duplicating languages
    matched_stack: list[str] = []
    for name, marker in CORE_BUILD_TARGETS:
        if (p / marker).exists() and name not in matched_stack:
            matched_stack.append(name)
    for name, marker in ADDITIONAL_BUILD_TARGETS:
        if (p / marker).exists() and name not in matched_stack:
            matched_stack.append(name)

    # Detect sensitive & high blast-radius paths
    sens: list[str] = []
    for s in CORE_SENSITIVE_TARGETS:
        if (p / s.rstrip("/")).exists() and s not in sens:
            sens.append(s)
    for s in ADDITIONAL_SENSITIVE_TARGETS:
        if (p / s.rstrip("/")).exists() and s not in sens:
            sens.append(s)

    has_build = len(matched_stack) > 0

    # Test detection: check directories and test file conventions
    has_test_dir = (p / "tests").is_dir() or (p / "test").is_dir() or (p / "__tests__").is_dir() or (p / "spec").is_dir()
    has_test_files = False
    if not has_test_dir:
        # Check top-level or src test files
        for pattern in ("test_*.py", "*_test.py", "*.test.ts", "*.spec.ts", "*_test.go"):
            if list(p.glob(pattern)) or list((p / "src").glob(pattern) if (p / "src").is_dir() else []):
                has_test_files = True
                break

    has_tests = has_test_dir or has_test_files
    has_policy = (p / ".agent-policy.yaml").exists()
    has_agents = (p / "AGENTS.md").exists() or (p / "CLAUDE.md").exists()

    # Recommendations per pillar
    build_recs = [] if has_build else ["Add reproducible package specification (pyproject.toml, package.json, Cargo.toml, go.mod)."]
    test_recs = [] if has_tests else ["Create automated test suite under tests/ runnable via standard test runner (pytest, npm test)."]
    policy_recs = [] if has_policy else ["Run 'readiness fix' to scaffold zero-trust path boundaries in .agent-policy.yaml."]
    agents_recs = [] if has_agents else ["Run 'readiness fix' to create AGENTS.md with verification ladders and architectural anchor points."]

    pillars = [
        ReadinessPillar(
            name="Build & Dependency Specs",
            score=25 if has_build else 0,
            passed=has_build,
            details=f"Detected: {', '.join(matched_stack)}" if has_build else "Missing reproducible build config",
            recommendations=build_recs,
        ),
        ReadinessPillar(
            name="Verification Test Harness",
            score=25 if has_tests else 0,
            passed=has_tests,
            details="Automated test suite present" if has_tests else "Missing test harness directory",
            recommendations=test_recs,
        ),
        ReadinessPillar(
            name="Blast-Radius Boundary Policy",
            score=25 if has_policy else 0,
            passed=has_policy,
            details="Zero-trust path boundary active" if has_policy else "Missing .agent-policy.yaml",
            recommendations=policy_recs,
        ),
        ReadinessPillar(
            name="Agent Operating Guidelines",
            score=25 if has_agents else 0,
            passed=has_agents,
            details="Guidelines active in repository" if has_agents else "Missing AGENTS.md contract",
            recommendations=agents_recs,
        ),
    ]

    score = sum(pi.score for pi in pillars)
    grade = (
        "A - Enterprise Agent Ready"
        if score == 100
        else "B - Moderately Ready"
        if score >= 75
        else "C - High Blast Risk"
        if score >= 50
        else "F - Unprepared"
    )
    missing = [m for m, ok in [(".agent-policy.yaml", has_policy), ("AGENTS.md", has_agents)] if not ok]

    # Quarantined paths list
    prot = sorted(set(sens + [".agent-policy.yaml"]))
    paths_str = "".join(f"  - {x}\n" for x in prot)

    # Determine default test runner command based on detected stack
    if "python" in matched_stack:
        test_gate = "pytest -v --tb=short tests/"
    elif "node" in matched_stack:
        test_gate = "npm test"
    elif "go" in matched_stack:
        test_gate = "go test ./..."
    elif "rust" in matched_stack:
        test_gate = "cargo test"
    elif "bazel" in matched_stack:
        test_gate = "bazel test //..."
    else:
        test_gate = "pytest -v --tb=short tests/"

    yaml_txt = (
        f"# Zero-Trust AI Agent Policy Contract\n"
        f"version: '1.0'\n"
        f"permission_tier: sandbox_write\n"
        f"enforcement: strict\n"
        f"protected_paths:\n{paths_str}"
        f"allowed_tools:\n  - file_read\n  - file_edit\n  - run_command\n"
        f"command_rules:\n"
        f"  banned:\n"
        f"    - 'rm -rf*'\n"
        f"    - '*curl*|*sh*'\n"
        f"    - 'git push --force*'\n"
        f"    - 'git push -f*'\n"
        f"    - 'DROP TABLE*'\n"
        f"    - 'DROP DATABASE*'\n"
        f"verification_hooks:\n"
        f"  pre_commit_gate: '{test_gate}'\n"
    )

    doc_links = [
        f"- [{d}]({d}): Core architectural topology and invariants"
        for d in ["ARCHITECTURE.md", "DESIGN.md", "SPEC.md"]
        if (p / d).exists()
    ]
    docs_block = "\n".join(doc_links) or "- [ARCHITECTURE.md](ARCHITECTURE.md): System boundaries and topology"

    md_txt = (
        f"# Agent Operating Guidelines & Harness Engineering Contract\n\n"
        f"> **First Principles:** Models are stochastic token predictors. Without an execution harness, "
        f"agents suffer from context drift and undetected regressions. All actions here are bounded and test-gated.\n\n"
        f"## 1. Architectural & Design Anchor Points\n{docs_block}\n\n"
        f"## 2. Multi-Tier Verification Ladder\n"
        f"1. Tier 1 (Unit Loop): Fast sub-second test execution (`{test_gate}`, budget < 0.2s)\n"
        f"2. Tier 2 (Static Checks): Linting and strict type verification before submitting edits\n"
        f"3. Tier 3 (Full Regression Gate): Automated test suite execution (100% green required)\n"
        f"4. Tier 4 (CI Telemetry): Structured telemetry and test results\n\n"
        f"## 3. Environment & Boundaries\n"
        f"- Detected Stack: {', '.join(matched_stack) or 'general'}\n"
        f"- Permission Tier: `sandbox_write` (scoped strictly to `src/` and `tests/`)\n"
        f"- Quarantined Paths (Read-Only): {', '.join(prot)}\n"
        f"- Invariant: Never mark task complete or push commits if any test fails.\n"
    )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    return ReadinessReport(
        repo_name=p.name,
        score_before=score,
        score_after=score,
        grade=grade,
        detected_stack=matched_stack,
        discovered_sensitive_paths=sens,
        pillars=pillars,
        missing_safeguards=missing,
        generated_policy_yaml=yaml_txt,
        generated_agents_md=md_txt,
        scan_duration_ms=elapsed_ms,
    )
