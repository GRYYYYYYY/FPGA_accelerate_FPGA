#!/usr/bin/env python3
"""Run from this project directory or invoke this file by absolute path."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT.parent / "_shared/python"))
from framework import main

if __name__ == "__main__":
    raise SystemExit(main(PROJECT_ROOT))
