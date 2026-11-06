import argparse
import sys
import webbrowser
from pathlib import Path
from src.llm import get_api_key, is_demo_mode
from src.onboarder import onboard_repository
from src.scanner import scan_repository


def format_markdown_report(rep) -> str:
    md = [
        f"# 📊 Agent Readiness Report: `{rep.repo_name}`\n",
        f"**Readiness Score:** {rep.score_before}/100 (`{rep.grade}`)\n",
        f"- **Detected Stack:** {', '.join(rep.detected_stack) or 'general'}",
        f"- **Quarantined Paths:** {', '.join(rep.discovered_sensitive_paths) or 'None'}",
        f"- **Missing Contracts:** {', '.join(rep.missing_safeguards) or 'None (Fully Configured)'}\n",
        "## 🏛️ Pillar Score Breakdown\n",
        "| Pillar | Status | Score | Details |",
        "|---|:---:|:---:|---|",
    ]
    for pi in rep.pillars:
        status = "✅ PASS" if pi.passed else "❌ FAIL"
        md.append(f"| {pi.name} | {status} | {pi.score}/{pi.max_score} | {pi.details} |")

    recs = []
    for pi in rep.pillars:
        if not pi.passed and getattr(pi, "recommendations", None):
            for r in pi.recommendations:
                recs.append(f"- **{pi.name}:** {r}")

    if recs:
        md.append("\n## 💡 Remediation Recommendations\n")
        md.extend(recs)
        md.append("\n> **Auto-Onboard:** Run `readiness fix .` to synthesize contracts and escalate to 100/100.\n")

    return "\n".join(md)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="readiness",
        description="AI Agent Repository Readiness Engine & Auto-Onboarder CLI",
    )
    sub = parser.add_subparsers(dest="cmd")

    # scan
    p_scan = sub.add_parser("scan", help="Scan repository and output readiness score breakdown")
    p_scan.add_argument("path", default=".", nargs="?")
    p_scan.add_argument("--json", action="store_true", help="Output report as JSON")
    p_scan.add_argument("--markdown", action="store_true", help="Output GitHub Markdown readiness report")
    p_scan.add_argument("--min-score", type=int, default=0, help="Fail with exit code 1 if score < min-score")

    # fix
    p_fix = sub.add_parser("fix", help="Auto-onboard repository and generate missing contracts")
    p_fix.add_argument("path", default=".", nargs="?")
    p_fix.add_argument("--llm", action="store_true", help="Call real LLM for contract synthesis")
    p_fix.add_argument("--dry-run", action="store_true", help="Preview synthesized contracts without writing to disk")

    # init
    p_init = sub.add_parser("init", help="Initialize agent readiness contracts (.agent-policy.yaml, AGENTS.md)")
    p_init.add_argument("path", default=".", nargs="?")
    p_init.add_argument("--dry-run", action="store_true", help="Preview files without writing")

    # ui
    sub.add_parser("ui", help="Open Control Plane Web UI")

    args = parser.parse_args(argv)
    target = Path(getattr(args, "path", ".")).resolve()

    if args.cmd == "scan":
        rep = scan_repository(target)
        if args.json:
            print(rep.model_dump_json(indent=2))
        elif args.markdown:
            print(format_markdown_report(rep))
        else:
            print(f"\n📦 Repository: {rep.repo_name} ({target})")
            print(f"📊 Readiness Score: {rep.score_before}/100 [{rep.grade}]")
            print(f"⚙️  Detected Stack: {', '.join(rep.detected_stack) or 'None'}")
            print(f"🛡️  Quarantined Paths: {', '.join(rep.discovered_sensitive_paths) or 'None'}")
            print("\nPillars:")
            for pi in rep.pillars:
                status = "PASS" if pi.passed else "FAIL"
                print(f"  [{status}] {pi.name:30} {pi.score}/{pi.max_score} pts ({pi.details})")
            if rep.missing_safeguards:
                print(f"\nMissing Safeguards: {', '.join(rep.missing_safeguards)}")
                print(f"Run 'readiness fix {target}' to auto-onboard to 100/100.\n")

        if args.min_score > 0 and rep.score_before < args.min_score:
            return 1

    elif args.cmd in ("fix", "init"):
        is_dry_run = getattr(args, "dry_run", False)
        force_llm = getattr(args, "llm", False)
        rep = onboard_repository(target, write_files=not is_dry_run, force_llm=force_llm, dry_run=is_dry_run)
        has_key, provider = get_api_key()
        engine = f"LLM ({provider})" if (force_llm or (not is_demo_mode() and has_key)) else "Pre-Calculated Fixtures"

        if is_dry_run:
            print(f"\n⚡ [DRY-RUN] Auto-Onboarding Preview for {rep.repo_name}:")
            print(f"   Projected Score: {rep.score_before}/100 -> {rep.score_after}/100 [{rep.grade}]")
            print("\n--- .agent-policy.yaml ---")
            print(rep.generated_policy_yaml)
            print("--- AGENTS.md ---")
            print(rep.generated_agents_md)
        else:
            print(f"\n⚡ Auto-Onboarded {rep.repo_name} [Engine: {engine}]")
            print(f"   Score: {rep.score_before}/100 -> {rep.score_after}/100 [{rep.grade}]")
            print("   Synthesized contracts: .agent-policy.yaml, AGENTS.md\n")

    elif args.cmd == "ui":
        ui_path = Path(__file__).resolve().parent.parent / "docs" / "index.html"
        webbrowser.open(f"file://{ui_path}")
        print(f"Control Plane UI: file://{ui_path}")
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
