#!/usr/bin/env python3
"""Check a saved (possibly externally modified) compact artifact against a reference."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters")]
from canonical_graph import compare
from import_vivado import sha256
from template_codec import DirectDecoder


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--compact", type=Path, required=True)
    args = parser.parse_args(argv)
    record = {"execution_kind": "real_device_validation"}
    try:
        reference = json.loads(args.reference.read_text())
        compact = json.loads(args.compact.read_text())
        record.update(reference_sha256=sha256(args.reference), compact_sha256=sha256(args.compact))
        record.update(compare(reference, DirectDecoder(compact).materialize()))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        record.update(equal=False, error=str(exc))
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
