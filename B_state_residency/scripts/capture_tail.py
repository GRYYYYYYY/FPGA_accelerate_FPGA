#!/usr/bin/env python3
"""Supplement systematic sampling with every attempt above a fixed pop threshold."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))
from prepare_real import sha, UPSTREAM
from profile_real import validate, parse_log
from analyze_real import summarize_traces


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--min-pops", type=int, default=16384)
    args = parser.parse_args(argv)
    directory = args.directory.resolve()
    record = json.loads((directory / "manifest.json").read_text())
    if record["status"] != "passed": raise ValueError("Primary experiment must pass first")
    config = record["config"]; validate(config, record["build"])
    tail = directory / "tail"; tail.mkdir(exist_ok=False)
    selected = []
    with (directory / "trace_0.jsonl").open() as file:
        for line in file:
            row = json.loads(line)
            if row["pops"] >= args.min_pops:
                selected.append({k: row[k] for k in ("attempt", "iteration", "connection_id", "pops", "label_accesses")})
    if not selected: raise ValueError("No tail attempts")
    selected_ids = {r["attempt"] for r in selected}
    cap = max(r["label_accesses"] for r in selected)
    manifest = {"status": "running", "min_pops": args.min_pops, "selected": selected, "cap": cap,
                "base_build": record["build"], "base_result_sha256": record["runs"][0]["result_sha256"]}
    def save(): (tail / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    save()
    try:
        # Freeze the primary build and derive a separate header; no measured binary is replaced.
        source = ROOT / "build/real_trace/trace.cpp"
        if sha(source) != record["build"]["trace"]["source_sha256"]: raise ValueError("Trace source changed")
        (tail / "trace.cpp").write_text(source.read_text())
        header = (ROOT / "adapters/real_trace.hpp").read_text()
        header = header.replace("inline unsigned stride = 512, cap = 200000;", f"inline unsigned stride = 512, cap = {cap};\ninline std::unordered_set<uint64_t> selectedIds = {{" + ",".join(map(str, sorted(selected_ids))) + "};")
        header = header.replace("id % stride == 0", "selectedIds.count(id) != 0")
        if "id % stride == 0" in header or "cap = 200000" in header: raise ValueError("Tail derivation failed")
        (tail / "real_trace.hpp").write_text(header)
        binary = tail / "router_trace_tail"
        command = ["g++", "-std=c++17", "-O3", "-g", "-fno-fast-math", "-fno-omit-frame-pointer", "-no-pie", "-pthread",
                   "-I", str(UPSTREAM / "cpp_router/include"), "-I", str(ROOT / "adapters"),
                   str(tail / "trace.cpp"), "-o", str(binary)]
        manifest["build_command"] = command
        with (tail / "build.log").open("w") as file:
            subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, check=True, timeout=180)
        manifest["hashes"] = {str(p): sha(p) for p in (source, tail/"trace.cpp", tail/"real_trace.hpp", binary)}
        prefix = tail / "trace"
        env = {k: v for k, v in os.environ.items() if not k.startswith(("RW_", "B_TRACE", "B_SAMPLE", "B_PROFILE"))}
        extra = dict(config["environment"], B_TRACE_PREFIX=str(prefix), B_PROFILE_PREFIX=str(prefix))
        env.update(extra); manifest["environment"] = extra
        command = ["/usr/bin/time", "-v", "-o", str(tail/"trace.time"), "taskset", "-c", str(config["cpu"]),
                   str(binary), str(ROOT/config["input"]), str(prefix.with_suffix(".result"))]
        manifest["command"] = command; save()
        with prefix.with_suffix(".log").open("w") as file:
            subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, env=env, check=True, timeout=600)
        manifest["metrics"] = parse_log(prefix.with_suffix(".log").read_text())
        manifest["result_sha256"] = sha(prefix.with_suffix(".result"))
        if manifest["result_sha256"] != manifest["base_result_sha256"]: raise ValueError("Tail instrumentation changed result")
        if manifest["metrics"]["convergence"] != record["runs"][0]["metrics"]["convergence"]:
            raise ValueError("Tail instrumentation changed convergence")
        traces = summarize_traces(prefix.with_suffix(".jsonl"), prefix.with_suffix(".accesses"),
                                  config["nodes"], config["connections"], config["trace_stride"], selected_ids)
        primary = json.loads((directory / "trace_analysis.json").read_text())
        if traces["all_attempt_label_accesses"] != primary["all_attempt_label_accesses"]:
            raise ValueError("Tail instrumentation changed access count")
        if traces["counts"]["truncated_attempts"] or traces["counts"]["selected_attempts"] != len(selected_ids):
            raise ValueError("Tail coverage incomplete")
        (tail / "trace_analysis.json").write_text(json.dumps(traces, indent=2)+"\n")
        manifest["status"] = "passed"
        print(json.dumps({"status": "passed", "tail_attempts": len(selected), "events": traces["counts"]["captured_events"],
                          "page_summary": traces["page_summary"]}, indent=2), flush=True)
    except Exception as error:
        manifest["status"] = "failed"; manifest["error"] = str(error); raise
    finally: save()
    return 0


if __name__ == "__main__": raise SystemExit(main())
