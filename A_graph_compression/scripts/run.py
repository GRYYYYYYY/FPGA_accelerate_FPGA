#!/usr/bin/env python3
"""Run from this project directory or invoke this file by absolute path."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT.parent / "_shared/python"))
from framework import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "netlist-report":
        from netlist_stage_report import main as netlist_report_main
        raise SystemExit(netlist_report_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "hls-report":
        from hls_report import main as hls_main
        raise SystemExit(hls_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "netlist-check":
        from netlist_experiment import main as netlist_main
        raise SystemExit(netlist_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "packed-check":
        from packed_experiment import main as packed_main
        raise SystemExit(packed_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "region-check":
        from region_experiment import main as region_main
        raise SystemExit(region_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "real-check":
        from real_experiment import main as real_main
        raise SystemExit(real_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "verify-compact":
        from verify_compact import main as verify_main
        raise SystemExit(verify_main(sys.argv[2:]))
    raise SystemExit(main(PROJECT_ROOT))
