import argparse, json, sys, webbrowser
from pathlib import Path
from src.onboarder import onboard_repository
from src.scanner import scan_repository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="readiness", description="AI Agent Repository Readiness Engine")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="Scan repository and output readiness score breakdown")
    p_scan.add_argument("path", default=".", nargs="?")
    p_scan.add_argument("--json", action="store_true")

    p_fix = sub.add_parser("fix", help="Auto-onboard repository and generate missing contracts")
    p_fix.add_argument("path", default=".", nargs="?")

    sub.add_parser("ui", help="Open Control Plane Web UI")

    args = parser.parse_args(argv)
    target = Path(getattr(args, "path", ".")).resolve()

    if args.cmd == "scan":
        rep = scan_repository(target)
        if args.json:
            print(rep.model_dump_json(indent=2))
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
    elif args.cmd == "fix":
        rep = onboard_repository(target, write_files=True)
        print(f"\n⚡ Auto-Onboarded {rep.repo_name} successfully!")
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
