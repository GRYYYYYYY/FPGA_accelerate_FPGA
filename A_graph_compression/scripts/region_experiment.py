#!/usr/bin/env python3
"""Frozen SLR holdout validation and a bounded real-resource CPU search microbenchmark."""
import argparse
from collections import Counter, defaultdict
import cProfile
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import pstats
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters")]
from canonical_graph import NodeState, compare, split_name, validate
from heldout import encode_frozen, fit_bank, heldout_stats, object_digest, select_sources, source_slr
from import_vivado import read_export, sha256
from real_experiment import write_new
from search_experiment import LazyTemplates, compare_search, make_queries, search
from template_codec import DirectDecoder


def summary(graph):
    by_node = defaultdict(set)
    for wire, node in graph["aliases"].items():
        by_node[node].add(int(graph["tiles"][split_name(wire)[0]]["SLR_REGION_ID"]))
    crossing = [n for n, slrs in by_node.items() if len(slrs) > 1]
    scan = [v.split("/") for k, v in graph["metadata"].items() if k.startswith("excluded_scan:")]
    return {**{k: len(graph[k]) for k in ["roots", "nodes", "aliases", "pips", "edges", "seed_tiles"]},
            "source_slrs": dict(sorted(Counter(source_slr(graph, r) for r in graph["roots"]).items())),
            "cross_slr_canonical_nodes": len(crossing), "cross_slr_examples": crossing[:5],
            "excluded_scan_tiles": len(scan), "excluded_scan_pips": sum(int(v[1]) for v in scan),
            "excluded_scan_matches": sum(int(v[0]) for v in scan)}


def closure_check(graph, settings):
    """Verify the BFS sampling contract against the independent saved child oracle."""
    seeds = settings["seeds"]
    max_depth = settings["max_depth"]
    metadata = graph["metadata"]
    if metadata["bfs_seeds"].split(",") != seeds or int(metadata["bfs_max_depth"]) != max_depth:
        raise ValueError("Closure settings differ from capture")
    if int(metadata["bfs_max_sources"]) != settings["max_exported_sources"]:
        raise ValueError("Closure source budget differs")
    if metadata["bfs_budget_hit"] != "0":
        raise ValueError("Captured domain exhausted its source budget; full depth coverage not certified")
    levels = {s: 0 for s in seeds}
    frontier = list(seeds)
    for depth in range(max_depth):
        next_frontier = []
        for node in frontier:
            if node not in graph["roots"]:
                raise ValueError(f"Missing adjacency before depth boundary: {node}")
            for child in graph["oracle_children"][node]:
                if child not in levels:
                    levels[child] = depth+1
                    next_frontier.append(child)
        frontier = next_frontier
    expected = {n for n, d in levels.items() if d < max_depth}
    if expected != set(graph["roots"]) or set(levels) != set(graph["nodes"]):
        raise ValueError("BFS source/discovery sets differ from oracle")
    actual_depths = {s["node"]: int(s["reason"].split(":")[1]) for s in graph["selections"]}
    if actual_depths != {n: levels[n] for n in expected}:
        raise ValueError("Exported BFS depth differs from oracle")
    if int(metadata["bfs_discovered"]) != len(levels):
        raise ValueError("BFS discovery count differs")
    return {"passed": True, "depth_counts": dict(sorted(Counter(levels.values()).items())),
            "expanded_before_boundary": len(expected), "unexpanded_boundary_nodes": len(frontier),
            "source_budget_hit": False}


def profile_queries(compact, queries):
    provider = LazyTemplates(compact)
    profiler = cProfile.Profile()
    profiler.enable()
    for q in queries:
        if q["kind"] == "reachable_by_exported_edges":
            search(provider, q["source"], q["target"], q["max_expansions"])
    profiler.disable()
    stats = pstats.Stats(profiler)
    rows = []
    for (filename, line, function), (primitive, calls, own, cumulative, _) in stats.stats.items():
        rows.append({"file": filename, "line": line, "function": function, "primitive_calls": primitive,
                     "calls": calls, "self_ms": own*1000, "cumulative_ms": cumulative*1000})
    return {"scope": "Separate instrumented query batch; excluded from benchmark timing; cumulative rows overlap.",
            "top_self_time": sorted(rows, key=lambda r: r["self_ms"], reverse=True)[:20],
            "top_cumulative_time": sorted(rows, key=lambda r: r["cumulative_ms"], reverse=True)[:20]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/region_query.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        cfg = json.loads(args.config.read_text())
        if cfg["repetitions"] < 1:
            raise ValueError("repetitions must be positive")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        output = args.output or ROOT / "results" / f"region_check_{stamp}.json"
        if output.exists():
            raise FileExistsError(output)
        timings = {}
        def timed(name, fn):
            t0 = perf_counter_ns()
            value = fn()
            timings[name] = (perf_counter_ns()-t0)/1e6
            return value
        def load(which):
            entry = cfg[which]
            path = ROOT / entry["path"]
            if sha256(path) != entry["sha256"]:
                raise ValueError(f"Input SHA256 differs: {which}")
            graph = read_export(path)
            if graph["metadata"]["part"] != cfg["part"]:
                raise ValueError(f"Wrong device: {which}")
            validate(graph)
            return graph
        train_raw = timed("training_load_and_validation", lambda: load("training"))
        train = timed("training_selection", lambda: select_sources(train_raw, [r for r in train_raw["roots"]
                      if source_slr(train_raw, r) in cfg["training"]["source_slrs"]]))
        # Fit and freeze BEFORE loading either evaluation file.
        bank = timed("training_bank_fit", lambda: fit_bank(train))
        bank_hash = object_digest(bank)
        held = timed("heldout_load_and_validation", lambda: load("heldout"))
        domain = timed("search_domain_load_and_validation", lambda: load("search_domain"))
        if set(bank["training_source_slrs"]) != {0} or set(cfg["heldout"]["source_slrs"]) != {1, 2, 3}:
            raise ValueError("This experiment requires the declared SLR0 -> SLR1/2/3 split")
        if {source_slr(held, r) for r in held["roots"]} != set(cfg["heldout"]["source_slrs"]):
            raise ValueError("Held-out source SLR coverage differs")
        if any(source_slr(domain, r) == 0 for r in domain["roots"]):
            raise ValueError("Search domain source leaked into training SLR")
        held_compact = timed("heldout_exception_generation", lambda: encode_frozen(held, bank))
        domain_compact = timed("search_domain_exception_generation", lambda: encode_frozen(domain, bank))
        held_equal = timed("heldout_roundtrip_validation", lambda: compare(held, DirectDecoder(held_compact).materialize()))
        domain_equal = timed("search_domain_roundtrip_validation", lambda: compare(domain, DirectDecoder(domain_compact).materialize()))
        closure = closure_check(domain, cfg["search_domain"])
        held_stats = heldout_stats(held, held_compact)
        domain_stats = heldout_stats(domain, domain_compact)
        queries = make_queries(domain, cfg["search_domain"]["seeds"], cfg["search_domain"]["max_depth"], cfg["query_max_expansions"])
        searches = compare_search(domain, domain_compact, queries, cfg["repetitions"])
        statuses = Counter(o["result"]["status"] for o in searches["outcomes"])
        # Actual cross-SLR aliases, not just cross-tile geometry.
        crossing = summary(domain)["cross_slr_examples"]
        state = NodeState(domain)
        state_ok = bool(crossing)
        for node in crossing:
            state.add(node, 1)
            state_ok &= all(state.get(w) == 1 for w, n in domain["aliases"].items() if n == node)
            state.add(node, -1)
        checks = {
            "training_and_evaluation_sources_disjoint": not (set(train["roots"]) & (set(held["roots"]) | set(domain["roots"]))),
            "bank_unchanged_after_evaluation": bank_hash == object_digest(bank),
            "evaluation_template_tables_equal_frozen_bank": held_compact["templates"] == domain_compact["templates"] == bank["templates"],
            "heldout_exact_with_exceptions": held_equal["equal"],
            "search_domain_exact_with_exceptions_and_fallback": domain_equal["equal"],
            "bfs_domain_complete_to_declared_depth": closure["passed"],
            "same_search_paths_status_and_trace": searches["all_equal_and_valid"],
            "all_reachable_queries_found_at_discovery_distance": all(o["result"]["status"] == "found" and o["result"]["distance"] == o["query"]["discovery_distance"] for o in searches["outcomes"] if o["query"]["kind"] == "reachable_by_exported_edges"),
            "budget_incomplete_and_no_path_distinguished": all(statuses[s] > 0 for s in ["found", "budget_exhausted", "incomplete_domain", "no_path"]),
            "actual_cross_slr_aliases_share_occupancy": bool(state_ok)}
        artifact_dir = ROOT / "data/derived" / f"regions_{stamp}"
        artifact_values = {"bank": bank, "heldout_canonical": held, "heldout_templates": held_compact,
                           "search_canonical": domain, "search_templates": domain_compact, "queries": queries,
                           "search_traces": searches.pop("outcomes")}
        artifacts = {}
        for name, value in artifact_values.items():
            path = artifact_dir / f"{name}.json"
            write_new(path, value)
            artifacts[name] = {"path": str(path), "sha256": sha256(path)}
        files = ["adapters/export_vivado.tcl", "adapters/export_regions.tcl", "adapters/import_vivado.py",
                 "src/canonical_graph.py", "src/template_codec.py", "src/heldout.py", "src/search_experiment.py",
                 "scripts/run.py", "scripts/region_experiment.py", "scripts/real_experiment.py",
                 "tests/test_regions.py"]
        report = {"schema_version": 1, "execution_kind": "real_device_search_microbenchmark", "project_id": "A",
                  "status": "passed" if all(checks.values()) else "failed", "checks": checks,
                  "provenance": {"command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
                                 "python": platform.python_version(), "platform": platform.platform(),
                                 "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "config_path": str(args.config), "config_sha256": sha256(args.config),
                                 "code_sha256": {p: sha256(ROOT / p) for p in files},
                                 "input_config": cfg, "bank_content_sha256": bank_hash,
                                 "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None},
                  "training": {"coverage": summary(train), "templates": len(bank["templates"])},
                  "heldout": {"coverage": summary(held), **held_stats},
                  "search_domain": {"coverage": summary(domain), "closure_validation": closure, **domain_stats},
                  "search": {"query_count": len(queries), "status_counts": dict(statuses), **searches},
                  "preprocessing_ms": timings, "profile": profile_queries(domain_compact, queries), "artifacts": artifacts,
                  "limitations": ["Constructed static-device resource queries, not real netlist/source-sink workload.",
                                  "Frozen template prediction and exact recovery are separate: exceptions/fallback use evaluation ground truth.",
                                  "Source SLRs are disjoint; physical target/alias resources can cross SLRs. This is not independent-device validation.",
                                  "Four-hop domain only; unknown adjacency is an explicit termination status.",
                                  "Unit-hop BFS has no timing/congestion/protected-net constraints.",
                                  "Python JSON/copy-based decoder is a semantic prototype, not a packed or optimized codec.",
                                  "Warm resident microbenchmark, same process, no CPU pinning, no hardware measurements.",
                                  "Canonical nodes, aliases, properties and fallback remain explicit; no compression-byte claim."]}
        write_new(output, report)
        print(json.dumps({"status": report["status"], "output": str(output.resolve()), "checks": checks,
                          "heldout": held_stats["counts"], "search_domain": domain_stats["counts"],
                          "search_statuses": dict(statuses), "median_query_batch_ms": searches["measurements"]["median_query_batch_ms"]}, ensure_ascii=False, indent=2))
        return 0 if all(checks.values()) else 1
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
