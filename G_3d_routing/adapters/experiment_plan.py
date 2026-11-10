"""G-local plan: distinguish executable model baselines from planned variants."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from adapters.common import ROOT, write_new
from framework import check_project


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config, datasets = check_project(ROOT)
    rows = []
    for dataset in datasets["datasets"]:
        if dataset["kind"] != "real":
            continue
        for variant in config["variants"]:
            if variant["id"] == "reference":
                continue
            available = (variant["id"] == "original_vpr" and
                         dataset["id"] in {"ex5p_natural", "ex5p_balanced"} and
                         dataset["status"] == "ready" and
                         (ROOT / "data/derived/ex5p_w100/summary.json").is_file())
            rows.append({"dataset_id": dataset["id"], "variant": variant["id"],
                         "status": "implemented_model_baseline" if available else "planned",
                         "executable": available,
                         "command": f"python3 scripts/run.py baseline --cases {dataset['id']}" if available else None,
                         "requires": ["Runtime verifies all pinned file hashes"] if available else
                                     ["dataset adapter if pending", "variant implementation", "correctness validation"]})
    now = datetime.now(timezone.utc)
    output = args.output or ROOT / "results" / f"plan_{now.strftime('%Y%m%dT%H%M%S.%fZ')}.json"
    write_new(output, {"schema_version": 1, "project_id": "G", "execution_kind": "plan_only",
                       "timestamp_utc": now.isoformat(), "experiments": rows, "metrics": config["metrics"]})
    print(json.dumps({"status": "plan_written", "output": str(output),
                      "executable_rows": sum(row["executable"] for row in rows)}, indent=2))
    return 0
