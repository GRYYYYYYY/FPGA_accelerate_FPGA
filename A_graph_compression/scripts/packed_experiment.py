#!/usr/bin/env python3
"""Independent traversal training, lossless binary graphs and native BFS experiments."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
from statistics import median
import struct
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters")]
from canonical_graph import compare, validate
from heldout import encode_frozen, fit_bank, heldout_stats, object_digest, select_sources, source_slr
from import_vivado import read_export, sha256
from packed_graph import PackedGraph, write_packed
from real_experiment import write_new
from region_experiment import closure_check, summary
from search_experiment import ExplicitCSR, make_queries, search


def expected_dump(reader):
    return b"".join(struct.pack("<8I", node, *edge)
                    for node in range(len(reader.nodes)) if reader.nodes[node][3] >= 0
                    for edge in reader.numeric_neighbors(node))


def verify_native(reader, native, references):
    if len(native["first_results"]) != len(references):
        raise ValueError("Native result count differs")
    # Numeric table IDs can differ between CSR and template attribute/string pools.
    for actual, reference in zip(native["first_results"], references):
        for nk, pk in [("status", "status"), ("expanded", "expanded_sources"),
                       ("examined", "examined_edges"), ("fetched", "fetched_edge_records")]:
            if actual[nk] != reference[pk]:
                raise ValueError(f"Native {nk} differs: {actual[nk]} vs {reference[pk]}")
        if actual["distance"] != (reference["distance"] if reference["distance"] is not None else -1):
            raise ValueError("Native distance differs")
        path = []
        for row in actual["path"]:
            source, *edge = row
            matches = [pair[0] for numeric, pair in zip(reader.numeric_neighbors(source), reader.decoded_neighbors(source))
                       if tuple(edge) == numeric]
            if len(matches) != 1:
                raise ValueError("Native path contains invalid or ambiguous edge")
            path.append(matches[0])
        if path != reference["path"]:
            raise ValueError("Native canonical path/PIP/direction differs")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/traversal_v1.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    timings = {}
    def timed(name, fn):
        start = perf_counter()
        value = fn()
        timings[name] = (perf_counter() - start) * 1000
        return value
    try:
        cfg = json.loads(args.config.read_text())
        capture_path = ROOT / cfg["output_dir"] / "capture.json"
        capture = json.loads(capture_path.read_text())
        if sha256(args.config) != capture["capture"]["config_sha256"]:
            raise ValueError("Preregistered capture configuration changed")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        output = args.output or ROOT / "results" / f"packed_check_{stamp}.json"
        if output.exists():
            raise FileExistsError(output)
        artifact_dir = ROOT / "data/derived" / f"packed_{stamp}"
        artifact_dir.mkdir(parents=True, exist_ok=False)
        def load(entry):
            path = ROOT / entry["path"]
            if sha256(path) != entry["sha256"]:
                raise ValueError(f"Input SHA256 differs: {path}")
            graph = read_export(path)
            validate(graph)
            if graph["metadata"]["part"] != cfg["part"]:
                raise ValueError("Device differs")
            return graph
        training = timed("traversal_training_load_validate", lambda: load(capture["training"]))
        oldcfg = json.loads((ROOT / "configs/region_query.json").read_text())
        intent_raw = timed("intent_training_load_validate", lambda: load(oldcfg["training"]))
        intent = select_sources(intent_raw, [n for n in intent_raw["roots"] if source_slr(intent_raw, n) == 0])
        # Exploratory equal-row-budget control, fixed hash order, no evaluation selection.
        sample = sorted(training["roots"], key=lambda n: hashlib.sha256(("A-budget-control-v1/"+n).encode()).digest())[:len(intent["roots"])]
        training_sets = {"intent": intent, "traversal_equal_budget": select_sources(training, sample), "traversal": training}
        banks = {name: timed(name+"_fit", lambda graph=graph: fit_bank(graph)) for name, graph in training_sets.items()}
        bank_hashes = {name: object_digest(bank) for name, bank in banks.items()}
        for name, bank in banks.items():
            if bank["training_source_slrs"] != cfg["training_source_slrs"]:
                raise ValueError("Training source SLRs differ")
            write_new(artifact_dir / (name+"_bank.json"), bank)
        # Freeze all banks before opening the evaluation graph in this run.
        graph = timed("evaluation_load_validate", lambda: load(capture["evaluation"]))
        if sorted({source_slr(graph, n) for n in graph["roots"]}) != cfg["evaluation_source_slrs"]:
            raise ValueError("Evaluation SLRs differ")
        closures = {name: closure_check(g, {"seeds": cfg[name+"_seeds"], "max_depth": cfg["max_depth"],
                    "max_exported_sources": cfg["max_exported_sources"]}) for name, g in [("training", training), ("evaluation", graph)]}
        queries = make_queries(graph, cfg["evaluation_seeds"], cfg["max_depth"], cfg["query_max_expansions"])
        provider = ExplicitCSR(graph)
        references = [search(provider, q["source"], q["target"], q["max_expansions"], trace=True) for q in queries]
        visits = Counter(v["source"] for q, r in zip(queries, references) if q["kind"] == "reachable_by_exported_edges" for v in r["trace"])
        coverage = {}
        for name, bank in banks.items():
            compact = timed(name+"_exceptions", lambda bank=bank: encode_frozen(graph, bank))
            stats = heldout_stats(graph, compact)
            categories = {r["source"]: r["category"] for r in stats.pop("sources")}
            weighted = Counter()
            for source, count in visits.items():
                weighted[categories[source]] += count
            coverage[name] = {"training_sources": len(bank["training_sources"]), "templates": len(bank["templates"]),
                              **stats, "query_expansion_weighted_counts": dict(weighted), "query_expansions": sum(visits.values()),
                              "weighted_fallback_fraction": weighted["unseen_family_fallback"] / max(1, sum(visits.values()))}
        write_new(artifact_dir / "queries.json", queries)
        write_new(artifact_dir / "reference_traces.json", references)
        layouts, readers = {}, {}
        specs = [("csr", "csr", None, True), ("intent", "compact", banks["intent"], True),
                 ("traversal_equal_budget", "compact", banks["traversal_equal_budget"], True),
                 ("traversal_full_rules", "compact", banks["traversal"], False),
                 ("traversal", "compact", banks["traversal"], True)]
        for name, mode, bank, patch in specs:
            path = artifact_dir / (name+".agr")
            layouts[name] = timed(name+"_pack", lambda: write_packed(path, graph, mode, bank, patch))
            reader = timed(name+"_load_validate", lambda: PackedGraph(path))
            equality = timed(name+"_roundtrip", lambda: compare(graph, reader.materialize()))
            if not equality["equal"]:
                raise ValueError(f"Binary roundtrip differs: {name}")
            readers[name] = reader
        node_ids = {n: i for i, n in enumerate(sorted(graph["nodes"]))}
        query_path = artifact_dir / "queries.bin"
        with query_path.open("xb") as f:
            f.write(b"".join(struct.pack("<4I", node_ids[q["source"]], node_ids[q["target"]], q["max_expansions"],
                                       int(q["kind"] == "reachable_by_exported_edges")) for q in queries))
        binary = artifact_dir / "packed_bench"
        compile_cmd = ["g++", "-std=c++17", "-O3", "-Wall", "-Wextra", "-Wpedantic",
                       str(ROOT / "src/native/packed_bench.cpp"), "-o", str(binary)]
        compiled = subprocess.run(compile_cmd, text=True, capture_output=True, check=True)
        (artifact_dir / "compiler.log").write_text(compiled.stdout+compiled.stderr)
        cpu = min(os.sched_getaffinity(0))
        variants = [("csr", 0, "direct"), ("intent", 0, "direct"), ("traversal_equal_budget", 0, "direct"),
                    ("traversal_full_rules", 0, "direct"), ("traversal", 0, "expanded")]
        variants += [("traversal", cache, "direct") for cache in cfg["cache_capacities"]]
        measurements = {}
        for name, cache, execution in variants:
            label = f"{name}_{execution}_cache{cache}"
            dump_path = artifact_dir / (label+".edges.bin")
            command = [str(binary), str(artifact_dir / (name+".agr")), str(query_path), str(cache),
                       str(cfg["repetitions"]), str(dump_path), execution]
            start = perf_counter()
            proc = subprocess.run(command, capture_output=True, text=True, check=True,
                                  preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
            process_ms = (perf_counter()-start)*1000
            native = json.loads(proc.stdout)
            if dump_path.read_bytes() != expected_dump(readers[name]):
                raise ValueError(f"Native exhaustive edge/property-ID dump differs: {label}")
            verify_native(readers[name], native, references)
            native.update(command=command, subprocess_wall_ms_including_dump=process_ms,
                          median_resident_batch_ms=median(r[3] for r in native["resident_phase_ms"]),
                          median_resident_kernel_ms=median(r[1] for r in native["resident_phase_ms"]))
            write_new(artifact_dir / (label+".json"), native)
            measurements[label] = {k: v for k, v in native.items() if k != "first_results"}
        checks = {"train_evaluation_source_disjoint": all(not(set(b["training_sources"]) & set(graph["roots"])) for b in banks.values()),
                  "evaluation_sources_unseen_in_prior_samples": not capture["evaluation_source_overlap_with_previous_samples"],
                  "banks_unchanged": all(object_digest(b) == bank_hashes[n] for n, b in banks.items()),
                  "closures_complete_to_declared_depth": all(c["passed"] for c in closures.values()),
                  "all_binary_roundtrips_and_native_edges_exact": True,
                  "same_native_paths_status_and_search_counters": True,
                  "reachable_queries_found_at_expected_distance": all(r["status"] == "found" and r["distance"] == q["discovery_distance"] for q,r in zip(queries,references) if q["kind"] == "reachable_by_exported_edges"),
                  "termination_modes_distinguished": {r["status"] for r in references} == {"found", "no_path", "budget_exhausted", "incomplete_domain"}}
        files = ["src/packed_graph.py", "src/native/packed_bench.cpp", "src/native/packed_graph.hpp", "scripts/packed_experiment.py",
                 "src/canonical_graph.py", "src/template_codec.py", "src/heldout.py", "src/search_experiment.py",
                 "adapters/import_vivado.py", "scripts/region_experiment.py", "scripts/run.py"]
        report = {"schema_version": 1, "status": "passed" if all(checks.values()) else "failed", "checks": checks,
                  "scope": "Lossless packed static-device graphs and bounded unit-hop BFS; not netlist routing or hardware acceleration",
                  "training": summary(training), "evaluation": summary(graph), "closures": closures, "coverage": coverage,
                  "storage": layouts, "measurements": measurements, "preprocessing_ms": timings,
                  "queries": {"total": len(queries), "timed": sum(q["kind"] == "reachable_by_exported_edges" for q in queries)},
                  "provenance": {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
                                 "config": str(args.config), "config_sha256": sha256(args.config), "capture_sha256": sha256(capture_path),
                                 "code_sha256": {p: sha256(ROOT / p) for p in files}, "bank_hashes": bank_hashes,
                                 "compile_command": compile_cmd, "compiler": subprocess.check_output(["g++", "--version"], text=True),
                                 "native_binary_sha256": sha256(binary), "platform": platform.platform(), "python": platform.python_version(),
                                 "native_cpu_affinity": [cpu], "cpuinfo": Path("/proc/cpuinfo").read_text().split("\n\n")[0]},
                  "artifacts": {p.name: {"path": str(p), "sha256": sha256(p)} for p in artifact_dir.iterdir() if p.is_file()},
                  "limitations": ["Evaluation exceptions and fallback use true device adjacency; not database-free prediction.",
                                  "Traversal full training has more rows than intent; equal-budget hash subset is exploratory, not preregistered.",
                                  "No cross-SLR conductor occurs in this new domain; prior real samples cover that semantic case.",
                                  "Each native variant runs sequentially in a separate pinned process; no randomized process order or statistical CI.",
                                  "First query timings follow exhaustive validation dump, so OS/CPU caches are not cold. Resident repeats retain the LRU.",
                                  "Linux /proc/self/status VmHWM after exec includes executable, allocator/container overhead, input, dump validation, queries and result storage; not isolated accelerator memory.",
                                  "Static file bytes include all alias/property/index/audit tables and 64-byte padding; graph vector stays resident even in expanded mode.",
                                  "State and cache payload counts exclude container metadata; VmHWM is the observed process memory high-water mark.",
                                  "Logical record bytes are software accounting, not measured DRAM traffic. No FPGA board or whole-router speedup claimed."]}
        write_new(output, report)
        print(json.dumps({"status": report["status"], "output": str(output), "checks": checks,
                          "coverage": {n: {"fallback": v["counts"]["unseen_family_fallback"], "weighted_fallback": v["weighted_fallback_fraction"]} for n,v in coverage.items()},
                          "file_bytes": {n: s["file_bytes"] for n,s in layouts.items()},
                          "median_resident_batch_ms": {n:m["median_resident_batch_ms"] for n,m in measurements.items()}}, indent=2))
        return 0 if all(checks.values()) else 1
    except (OSError, ValueError, KeyError, TypeError, StopIteration, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
