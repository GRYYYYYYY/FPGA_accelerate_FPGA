#!/usr/bin/env python3
"""Attribute sampled PCs and summarize actual per-connection access traces."""
from collections import Counter, defaultdict
import argparse
import json
from pathlib import Path
import re
import statistics
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))
from prepare_real import sha


def symbolize(binary, addresses):
    addresses = sorted(set(addresses))
    text = subprocess.check_output(["addr2line", "-a", "-f", "-C", "-i", "-e", str(binary)],
                                   input="".join(f"0x{pc:x}\n" for pc in addresses), text=True)
    result = {}; current = None; pairs = []
    for line in text.splitlines():
        if re.fullmatch(r"0x[0-9a-fA-F]+", line):
            current = int(line, 16); result[current] = []; pairs = []
        else:
            if current is None: raise ValueError("Unexpected addr2line output")
            pairs.append(line)
            if len(pairs) == 2:
                match = re.match(r"^(.*):(\d+)(?:\s|$)", pairs[1])
                result[current].append({"function": pairs[0], "location": pairs[1],
                                        "file": match[1] if match else "??",
                                        "line": int(match[2]) if match else 0})
                pairs = []
    if set(result) != set(addresses): raise ValueError("Missing symbolization")
    return result


def classify(frames, source):
    """Exclusive attribution; phase contexts win over their internal label accesses."""
    functions = " ".join(f["function"] for f in frames)
    for needle, category in [
        ("tightenBoundingBoxesCoarse", "bbox_preparation"),
        ("::ripUp(", "rip_up"),
        ("::updateUsersAndPresentCongestionCost(", "commit"),
        ("::saveRouting(", "backtrace"),
        ("::setAllTargets(", "target_set"),
        ("::updateCost(", "update_cost")]:
        if needle in functions: return category
    if any("real_profile.hpp" in f["file"] for f in frames): return "profiling_code"
    if any(n in functions for n in ("::countUserHot(", "::countUserSlot(", "::searchCountUser(", "::countConnectionsOfUser(")):
        return "same_net_lookup"
    # Use the innermost application line, not an arbitrary outer TLD call site.
    app = next((f for f in frames if f["file"].endswith("/profile.cpp")), None)
    if not app: return "unresolved_or_library"
    line = source[app["line"]-1] if 0 < app["line"] <= len(source) else ""
    code = line.split("//", 1)[0]
    if "__builtin_prefetch(&tl_dyn" in code: return "label_prefetch"
    if "TLD(" in code: return "label_related_source"
    if re.search(r"dyn\[.*\]\.hist", code): return "history_price_source"
    if any(n in functions for n in ("::getChildren(", "::computeChildren(", "::deadChild(")):
        return "adjacency"
    if any(n in functions for n in ("PriorityQueue", "::offer(", "::poll(", "MinHeap")):
        return "priority_queue"
    if any(n in functions for n in ("::exploreAndExpand(", "::evaluateCostAndPush(", "::getNodeCostSearch(", "::isAccessible(", "::graphIsAccessible(")):
        return "other_expansion_and_cost"
    return "other_route_control"


def analyze_samples(directory, record):
    binary = ROOT / "build/real_trace/router_profile"
    if sha(binary) != record["build"]["profile"]["binary_sha256"]:
        raise ValueError("Profile binary differs from recorded build")
    source_path = ROOT / "build/real_trace/profile.cpp"
    if sha(source_path) != record["build"]["profile"]["source_sha256"]:
        raise ValueError("Profile source differs from recorded build")
    source = source_path.read_text().splitlines()
    stacks = {}
    for run in record["runs"]:
        if run["mode"] != "profile": continue
        rows = [[int(pc, 16) - (i > 0) for i, pc in enumerate(line.split())]
                for line in (directory / (run["name"] + ".pcs")).read_text().splitlines()]
        if len(rows) != run["profile"]["samples"]: raise ValueError("Sample count mismatch")
        stacks[run["name"]] = rows
    symbols = symbolize(binary, (pc for rows in stacks.values() for row in rows for pc in row))
    (directory / "symbols.json").write_text(json.dumps({hex(k): v for k, v in symbols.items()}, indent=2) + "\n")
    output = {}
    for name, rows in stacks.items():
        categories = Counter(); sites = Counter()
        for row in rows:
            frames = [f for pc in row for f in symbols[pc]]
            categories[classify(frames, source)] += 1
            first = next((f for f in frames if f["line"]), frames[0])
            sites[(first["function"], first["location"])] += 1
        output[name] = {"samples": len(rows), "counts": dict(categories),
                        "percent": {k: 100*v/len(rows) for k, v in categories.items()},
                        "top_sites": [{"function": k[0], "location": k[1], "samples": v}
                                      for k, v in sites.most_common(60)]}
    keys = sorted({key for row in output.values() for key in row["counts"]})
    ranges = {}
    for key in keys:
        vals = [row["percent"].get(key, 0) for row in output.values()]
        ranges[key] = {"median_percent": statistics.median(vals), "min_percent": min(vals), "max_percent": max(vals)}
    return {"runs": output, "category_ranges": ranges,
            "scope": "Route CPU PC samples, including bbox preparation; source-line attribution is not isolated memory latency",
            "caveat": "Periodic sampling, compiler line mapping and stack unwind bias; observed repetition range is not a confidence interval"}


def quantiles(values):
    values = sorted(values)
    if not values: return None
    return {"count": len(values), "min": values[0], "p50": statistics.median(values),
            "p90": values[int((len(values)-1)*0.90)], "p99": values[int((len(values)-1)*0.99)], "max": values[-1]}


def summarize_traces(metadata, accesses, nodes, connections, stride, selected_ids=None):
    counts = Counter(); iterations = Counter(); pops = []; fanouts = {}; net_fanouts = {}; paths = {}; ids = {}
    all_groups = defaultdict(Counter)
    page_data = {size: [] for size in (64, 512, 4096)}
    selected_rows = []; line_counts = Counter(); offset = 0; total_accesses = 0
    with Path(accesses).open("rb") as binary, Path(metadata).open() as records:
        for text in records:
            row = json.loads(text)
            counts["attempts"] += 1
            if row["attempt"] != counts["attempts"]: raise ValueError("Missing/reordered attempt")
            idx = row["connection_index"]
            if not 0 <= idx < connections: raise ValueError("Invalid connection index")
            if idx in ids and ids[idx] != row["connection_id"]: raise ValueError("Connection identity changed")
            ids[idx] = row["connection_id"]
            if idx in paths and paths[idx] != row["previous_path"]: raise ValueError("Rip-up does not match previous commit")
            if idx not in paths and row["previous_path"]: counts["initial_nonempty_paths"] += 1
            for node in row["path"] + row["previous_path"]:
                if not 0 <= node < nodes: raise ValueError("Path node outside graph")
            paths[idx] = row["path"]
            counts["rip_up_path_nodes"] += len(row["previous_path"])
            counts["commit_path_nodes"] += len(row["path"])
            counts["unrouted_attempts"] += not row["routed"]
            counts["aborted_attempts"] += row["aborted"]
            iterations[row["iteration"]] += 1
            fanouts[idx] = row["fanout"]; pops.append(row["pops"])
            if row["net_index"] in net_fanouts and net_fanouts[row["net_index"]] != row["fanout"]:
                raise ValueError("Net fanout changed")
            net_fanouts[row["net_index"]] = row["fanout"]
            groups = ["iteration_1" if row["iteration"] == 1 else "iteration_2_plus",
                      "fanout_lt_128" if row["fanout"] < 128 else "fanout_ge_128"]
            if row["pops"] >= 16384: groups.append("pops_ge_16384")
            for group in groups:
                all_groups[group]["attempts"] += 1
                all_groups[group]["label_accesses"] += row["label_accesses"]
                all_groups[group]["pops"] += row["pops"]
                all_groups[group]["selected"] += row["accesses_selected"]
                all_groups[group]["truncated"] += row["truncated"]
            total_accesses += row["label_accesses"]
            if row["access_byte_offset"] != offset: raise ValueError("Invalid access byte offset")
            selected = row["attempt"] % stride == 0 if selected_ids is None else row["attempt"] in selected_ids
            if row["accesses_selected"] != selected: raise ValueError("Unexpected sampling selection")
            if not row["accesses_selected"]:
                if row["access_count"] or row["truncated"]: raise ValueError("Events on unselected attempt")
                continue
            counts["selected_attempts"] += 1
            counts["truncated_attempts"] += row["truncated"]
            counts["selected_label_accesses"] += row["label_accesses"]
            if row["access_count"] > row["label_accesses"]: raise ValueError("More captured than actual accesses")
            if row["truncated"] != (row["access_count"] < row["label_accesses"]): raise ValueError("Invalid truncation marker")
            data = binary.read(row["access_count"] * 8)
            if len(data) != row["access_count"] * 8: raise ValueError("Truncated binary access trace")
            offset += len(data)
            visited = set()
            for node, line in struct.iter_unpack("<ii", data):
                if not 0 <= node < nodes or line <= 0: raise ValueError("Invalid trace event")
                visited.add(node); line_counts[line] += 1
            counts["captured_events"] += row["access_count"]
            if row["truncated"]: continue  # incomplete high-cost searches are never called low density
            summary = {k: row[k] for k in ("attempt", "iteration", "connection_id", "net_index", "fanout", "pops", "label_accesses")}
            summary["unique_nodes"] = len(visited); summary["pages"] = {}
            for size in page_data:
                pages = len({node // size for node in visited})
                density = len(visited) / (pages*size) if pages else 0
                page_data[size].append((len(visited), pages, density))
                summary["pages"][size] = {"touched_pages": pages, "density": density,
                                          "page_initialization_amplification": 1/density if density else None}
            selected_rows.append(summary)
        if binary.read(1): raise ValueError("Trailing binary access events")
    if len(paths) != connections: raise ValueError("Not all connections were traced")
    page_summary = {}
    for size, entries in page_data.items():
        total_nodes = sum(v[0] for v in entries); slots = sum(v[1]*size for v in entries)
        page_summary[size] = {"touched_pages": quantiles([v[1] for v in entries]),
                              "per_attempt_density": quantiles([v[2] for v in entries]),
                              "weighted_density": total_nodes/slots if slots else 0,
                              "page_clear_slots_per_unique_node": slots/total_nodes if total_nodes else None}
    groups = {}
    for label, predicate in [
        ("iteration_1", lambda r: r["iteration"] == 1),
        ("iteration_2_plus", lambda r: r["iteration"] > 1),
        ("fanout_lt_128", lambda r: r["fanout"] < 128),
        ("fanout_ge_128", lambda r: r["fanout"] >= 128),
        ("pops_ge_16384", lambda r: r["pops"] >= 16384)]:
        group = [r for r in selected_rows if predicate(r)]
        groups[label] = {"count": len(group), "unique_nodes": quantiles([r["unique_nodes"] for r in group]),
                         "page512_density": quantiles([r["pages"][512]["density"] for r in group])}
    return {"counts": dict(counts), "iterations": dict(iterations), "all_attempt_label_accesses": total_accesses,
            "connection_fanout": quantiles(list(fanouts.values())), "attempt_pops": quantiles(pops),
            "net_fanout": quantiles(list(net_fanouts.values())), "all_attempt_strata": dict(all_groups),
            "selected_unique_nodes": quantiles([r["unique_nodes"] for r in selected_rows]),
            "page_summary": page_summary, "strata": groups,
            "access_source_line_counts": dict(line_counts), "selected_attempts": selected_rows,
            "trace_integrity": "passed", "selection_policy": "systematic_stride" if selected_ids is None else "explicit_attempt_ids",
            "scope": "Real serial TLD calls; page results are hypothetical layout counts, not measured parallel paging time"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    directory = args.directory.resolve()
    record = json.loads((directory / "manifest.json").read_text())
    if record["status"] != "passed": raise ValueError("Require successful runs and independent verification")
    samples = analyze_samples(directory, record)
    (directory / "sampling_analysis.json").write_text(json.dumps(samples, indent=2)+"\n")
    trace = next(row for row in record["runs"] if row["mode"] == "trace")
    prefix = directory / trace["name"]
    config = record["config"]
    traces = summarize_traces(prefix.with_suffix(".jsonl"), prefix.with_suffix(".accesses"),
                              config["nodes"], config["connections"], config["trace_stride"])
    expected = {str(row[0]): row[4] for row in trace["metrics"]["convergence"]}
    if expected != {str(k): v for k, v in traces["iterations"].items()}: raise ValueError("Trace/route iteration counts differ")
    (directory / "trace_analysis.json").write_text(json.dumps(traces, indent=2)+"\n")
    print(json.dumps({"sampling": samples["category_ranges"], "trace": {k: v for k, v in traces.items() if k in ("counts", "page_summary", "strata")}}, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
