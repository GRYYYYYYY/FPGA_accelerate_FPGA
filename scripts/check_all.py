#!/usr/bin/env python3
"""Validate all seven independent scaffolds and run their CPU toy references."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT / "_shared/project_catalog.json").read_text())
    provenance = json.loads((ROOT / "_shared/assets/gpu_router_provenance.json").read_text())
    failures = []
    for item in provenance["files"]:
        path = ROOT / item["path"]
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            failures.append(f"Original reference changed or missing: {path}")
    runs = []
    for project in catalog:
        directory = ROOT / project["folder"]
        for action in ["check", "plan", "smoke"]:
            process = subprocess.run([sys.executable, "scripts/run.py", action], cwd=directory,
                                     capture_output=True, text=True, timeout=60)
            row = {"project": project["id"], "action": action, "returncode": process.returncode}
            if process.returncode:
                row["error"] = process.stderr.strip() or process.stdout.strip()
                failures.append(f"{project['id']} {action}: {row['error']}")
            else:
                row["result"] = json.loads(process.stdout)
            runs.append(row)
        print(f"{project['id']}: " + ", ".join(
            f"{r['action']}={'PASS' if r['returncode'] == 0 else 'FAIL'}" for r in runs[-3:]))
    now = datetime.now(timezone.utc)
    destination = ROOT / "results" / f"workspace_validation_{now.strftime('%Y%m%dT%H%M%S.%fZ')}.json"
    destination.parent.mkdir(exist_ok=True)
    record = {"timestamp_utc": now.isoformat(), "execution_kind": "scaffold_validation",
              "original_source_files_checked": len(provenance["files"]), "runs": runs,
              "status": "passed" if not failures else "failed", "failures": failures}
    with destination.open("x") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"Original reference integrity: {'PASS' if not any('reference changed' in x for x in failures) else 'FAIL'}")
    print(f"Validation report: {destination}")
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
