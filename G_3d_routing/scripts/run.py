#!/usr/bin/env python3
"""Run from this project directory or invoke this file by absolute path."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT.parent / "_shared/python"))
sys.path.insert(0, str(PROJECT_ROOT))
from framework import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"baseline", "export-rrg", "plan"}:
        if sys.argv[1] == "baseline":
            from adapters.vpr_baseline import main as local_main
        elif sys.argv[1] == "plan":
            from adapters.experiment_plan import main as local_main
        else:
            from adapters.vpr_rrg import main as local_main
        raise SystemExit(local_main(sys.argv[2:]))
    raise SystemExit(main(PROJECT_ROOT))
