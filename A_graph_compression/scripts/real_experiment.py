#!/usr/bin/env python3
"""Real device semantics experiment. Does not run routing or measure acceleration."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters")]
from import_vivado import read_export, sha256
from canonical_graph import compare, signature, validate
from template_codec import DirectDecoder, encode
from real_validation import ablate_exceptions, coverage, fault_injections, occupancy_checks


def write_new(path, value):
    """Publish complete JSON atomically and exclusively for downstream readers."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.'+path.name+'.', suffix='.tmp')
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            os.fchmod(stream.fileno(),0o644)
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
            stream.write("\n")
        os.link(temporary,path)  # Atomic no-replace publication on this filesystem.
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Complete TSV from export_vivado.tcl")
    parser.add_argument("--output", type=Path, help="New report path (never overwritten)")
    args = parser.parse_args(argv)
    try:
        settings = json.loads((ROOT / "configs/real_sample.json").read_text())
        source = args.input or ROOT / settings["raw_path"]
        if args.input is None and sha256(source) != settings["raw_sha256"]:
            raise ValueError("Default raw sample SHA256 differs from configuration")
        now = datetime.now(timezone.utc)
        stamp = now.strftime("%Y%m%dT%H%M%S.%fZ")
        report_path = args.output or ROOT / "results" / f"real_check_{stamp}.json"
        if report_path.exists():
            raise FileExistsError(report_path)
        graph = read_export(source)
        known_capture = graph["provenance"]["raw_sha256"] == settings["raw_sha256"]
        if graph["metadata"]["part"] != settings["part"]:
            raise ValueError("Input part differs from sample configuration")
        validate(graph)
        compact = encode(graph)
        decoder = DirectDecoder(compact)
        comparison = compare(graph, decoder.materialize())
        fault_results = fault_injections(graph, compact)
        state_checks = occupancy_checks(graph, compact)
        # Check lazy reads independently of materialization, retaining all pip properties.
        by_root = {r: [] for r in graph["roots"]}
        for edge in graph["edges"]:
            by_root[edge["src"]].append(signature([edge, graph["pips"][edge["pip"]]]))
        direct_equal = all(sorted(signature([e, p]) for e, p in decoder.neighbors(r)) == sorted(by_root[r])
                           for r in graph["roots"])
        unexpanded = next(n for n in graph["nodes"] if n not in graph["roots"])
        try:
            list(decoder.neighbors(unexpanded))
            partial_guard = False
        except KeyError:
            partial_guard = True
        counts = coverage(graph, compact)
        ablation = ablate_exceptions(graph, compact)
        checks = {"export_integrity_and_independent_downhill_oracle": True,
                  "all_nodes_aliases_pips_attributes_and_edges_equal": comparison["equal"],
                  "lazy_neighbor_reads_equal": direct_equal,
                  "unexpanded_targets_rejected_as_unknown_adjacency": partial_guard,
                  "all_fault_injections_detected": all(f["detected"] for f in fault_results),
                  "exceptions_ablation_has_real_mismatches": ablation["mismatched_sources"] > 0,
                  **state_checks}
        graph_path = ROOT / "data/derived" / f"canonical_{stamp}.json"
        compact_path = ROOT / "data/derived" / f"templates_{stamp}.json"
        write_new(graph_path, graph)
        write_new(compact_path, compact)
        files = ["adapters/export_vivado.tcl", "adapters/import_vivado.py", "src/canonical_graph.py",
                 "src/template_codec.py", "src/real_validation.py", "scripts/run.py", "scripts/real_experiment.py",
                 "scripts/verify_compact.py", "tests/test_real_graph.py", "configs/real_sample.json",
                 "configs/experiment.json", "data/datasets.json"]
        references = [ROOT.parent / "_shared/assets/gpu_router_original/rewrite/cpp_router/include/DeviceModel.hpp",
                      ROOT.parent / "_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp"]
        record = {
            "schema_version": 1, "project_id": "A", "execution_kind": "real_device_validation",
            "backend": "python_cpu", "status": "passed" if all(checks.values()) else "failed",
            "timestamp_utc": now.isoformat(), "source": graph["metadata"],
            "provenance": {**graph["provenance"], "command": [sys.executable, *sys.argv],
                           "python_version": platform.python_version(), "platform": platform.platform(),
                           "cwd": str(Path.cwd()), "sampling": "deterministic; no random seed",
                           "code_sha256": {p: sha256(ROOT / p) for p in files},
                           "reference_code_sha256": {str(p): sha256(p) for p in references},
                           "environment": {k: os.environ.get(k) for k in ["OMP_NUM_THREADS", "PYTHONHASHSEED"]},
                           "reproduction_export_command": settings["reproduction_export_command"],
                           "capture_method": settings["capture_method"] if known_capture else "external TSV; capture provenance not supplied",
                           "capture_commands": settings["capture_commands"] if known_capture else None,
                           "exporter_sha256_at_capture": settings["exporter_sha256_at_capture"] if known_capture else None},
            "checks": checks, "observations": counts, "exception_ablation": ablation,
            "fault_injections": fault_results, "comparison": comparison,
            "artifacts": {"canonical": {"path": str(graph_path), "sha256": sha256(graph_path)},
                          "templates": {"path": str(compact_path), "sha256": sha256(compact_path)}},
            "measurements": {"graph_bytes": None, "bytes_per_relaxation": None, "decode_cycles": None,
                             "routing_ms": None, "speedup": None},
            "limitations": ["Selected source adjacency only; not a closed or full-device routing graph.",
                            "All properties exposed at export are preserved as strings; timing delays and routing costs are not modeled.",
                            "Canonical/alias/node-property tables remain explicit; JSON sizes are not a hardware compression ratio.",
                            "Templates fitted and validated on this sample; no held-out generalization claim.",
                            "Empty linked design: no real-net protected resources or occupancy trace.",
                            "No excluded PIP observed in this sample; this category is not validated on real data.",
                            "No CPU router, GPU, FPGA, board, timing-quality or acceleration benchmark."]}
        write_new(report_path, record)
        print(json.dumps({"status": record["status"], "output": str(report_path.resolve()),
                          "observations": counts, "checks": checks}, ensure_ascii=False, indent=2))
        return 0 if record["status"] == "passed" else 1
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
