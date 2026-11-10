#!/usr/bin/env python3
"""Run from this project directory or invoke this file by absolute path."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT.parent / "_shared/python"))
from framework import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"budget-bench", "budget-evaluate"}:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.budget import main as budget_main
        raise SystemExit(budget_main(sys.argv[1:]))
    if len(sys.argv) > 1 and sys.argv[1] in {"trace-smoke", "profile", "build-router"}:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.profile import main as profile_main
        argv = sys.argv[1:]
        if argv[0] == "build-router":
            argv[0] = "build"
        raise SystemExit(profile_main(argv))
    if "--help" in sys.argv:
        print("Scheme C also supports: build-router, trace-smoke, profile, budget-bench, budget-evaluate. Use <action> --help for options.")
    raise SystemExit(main(PROJECT_ROOT))
