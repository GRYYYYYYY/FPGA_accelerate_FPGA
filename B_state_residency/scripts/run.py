#!/usr/bin/env python3
"""Run from this project directory or invoke this file by absolute path."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT.parent / "_shared/python"))
from framework import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        from benchmark import main as benchmark_main
        raise SystemExit(benchmark_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "profile-real":
        from profile_real import main as profile_main
        raise SystemExit(profile_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark-paged-real":
        from benchmark_paged_real import main as paged_main
        raise SystemExit(paged_main(sys.argv[2:]))
    raise SystemExit(main(PROJECT_ROOT))
