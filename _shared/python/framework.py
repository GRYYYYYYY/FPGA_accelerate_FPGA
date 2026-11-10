"""Project-local CLI for configuration checks, experiment plans and toy references."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def check_project(root):
    config = load_json(root / "configs/experiment.json")
    datasets = load_json(root / "data/datasets.json")
    variants = config["variants"]
    ids = [v["id"] for v in variants]
    if len(ids) != len(set(ids)) or "reference" not in ids:
        raise ValueError("Variant IDs must be unique and include reference")
    if any(v["status"] not in {"implemented_smoke", "planned"} for v in variants):
        raise ValueError("Unexpected variant status")
    if any(v["id"] != "reference" and v["status"] == "implemented_smoke" for v in variants):
        raise ValueError("Only reference is wired into this initial scaffold")
    if len({d["id"] for d in datasets["datasets"]}) != len(datasets["datasets"]):
        raise ValueError("Duplicate dataset ID")
    for name in ["README.md", "AGENTS.md", "EXPERIMENTS.md", "INTERFACES.md",
                 "NEXT_STEPS.md", "src/reference.py", "data/toy.json",
                 "configs/platform.json", "scripts/run.py"]:
        if not (root / name).is_file():
            raise ValueError(f"Missing project file: {name}")
    for dataset in datasets["datasets"]:
        if dataset["status"] == "ready":
            if not dataset.get("path") or not (root / "data" / dataset["path"]).is_file():
                raise ValueError(f"Ready dataset missing: {dataset['id']}")
    workspace = root.parent
    sources = load_json(workspace / "_shared/sources.json")
    missing = [s["path"] for s in sources["local"] if not (workspace / s["path"]).exists()]
    if missing:
        raise ValueError(f"Missing local research sources: {missing}")
    return config, datasets


def validate_smoke_result(record):
    if record["execution_kind"] != "synthetic_smoke" or record["backend"] != "python_cpu":
        raise ValueError("Scaffold results must be explicitly labelled as CPU toy checks")
    if not record["checks"] or any(type(v) is not bool for v in record["checks"].values()):
        raise ValueError("Reference must return nonempty boolean checks")
    if not all(record["checks"].values()):
        raise ValueError(f"Reference checks failed: {record['checks']}")
    if any(v is not None for v in record["measurements"].values()):
        raise ValueError("Toy checks must not populate experimental performance fields")


def main(root, argv=None):
    root = Path(root).resolve()
    parser = argparse.ArgumentParser(description="CPU toy checks and planned experiments; no hardware run")
    parser.add_argument("action", choices=["check", "plan", "smoke"])
    parser.add_argument("--input", type=Path, help="Synthetic fixture JSON; smoke only")
    parser.add_argument("--output", type=Path, help="New JSON output path; existing files are never overwritten")
    parser.add_argument("--variant", default="reference")
    args = parser.parse_args(argv)
    try:
        config, datasets = check_project(root)
        if args.action != "smoke" and (args.input is not None or args.variant != "reference"):
            raise ValueError("--input/--variant are only accepted with smoke")
        if args.action == "check":
            record = {"project_id": config["project_id"], "status": "passed",
                      "scope": "files, configuration and local source availability",
                      "real_data_ready": sum(d["kind"] == "real" and d["status"] == "ready"
                                             for d in datasets["datasets"])}
            if args.output:
                write_new(args.output, record)
            print(json.dumps(record, ensure_ascii=False, indent=2))
            return 0
        now = datetime.now(timezone.utc)
        stamp = now.strftime("%Y%m%dT%H%M%S.%fZ")
        if args.action == "plan":
            rows = []
            for dataset in datasets["datasets"]:
                if dataset["kind"] != "real":
                    continue
                for variant in config["variants"]:
                    if variant["status"] == "planned":
                        rows.append({"dataset_id": dataset["id"], "variant": variant["id"],
                                     "status": "planned", "executable": False,
                                     "requires": ["real dataset adapter", "variant implementation",
                                                  "correctness validation", "measurement harness"]})
            record = {"schema_version": 1, "project_id": config["project_id"],
                      "execution_kind": "plan_only", "timestamp_utc": now.isoformat(),
                      "experiments": rows, "metrics": config["metrics"]}
            output = args.output or root / "results" / f"plan_{stamp}.json"
        else:
            if args.variant != "reference":
                raise ValueError("Only --variant reference is implemented. Real CPU/GPU/FPGA variants are planned.")
            source = args.input or root / "data/toy.json"
            case = load_json(source)
            if case.get("dataset_kind") != "synthetic_smoke":
                raise ValueError("smoke accepts only explicitly labelled synthetic_smoke fixtures")
            reference = root / "src/reference.py"
            spec = importlib.util.spec_from_file_location(f"reference_{config['project_id']}", reference)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            outcome = module.run(case)
            record = {"schema_version": 1, "project_id": config["project_id"],
                      "execution_kind": "synthetic_smoke", "backend": "python_cpu",
                      "variant": "reference", "timestamp_utc": now.isoformat(), "status": "passed",
                      "input_sha256": digest(source), "config_sha256": digest(root / "configs/experiment.json"),
                      "reference_sha256": digest(reference), "framework_sha256": digest(__file__),
                      "common_sha256": digest(Path(__file__).with_name("research_common.py")),
                      "python_version": platform.python_version(),
                      "measurements": {"kernel_ms": None, "end_to_end_ms": None, "power_w": None,
                                       "energy_j": None, "achieved_clock_mhz": None, "speedup": None},
                      **outcome}
            validate_smoke_result(record)
            output = args.output or root / "results" / f"smoke_{stamp}.json"
        write_new(output, record)
        print(json.dumps({"project_id": config["project_id"], "action": args.action,
                          "status": record.get("status", "plan_written"), "output": str(output.resolve())},
                         ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
