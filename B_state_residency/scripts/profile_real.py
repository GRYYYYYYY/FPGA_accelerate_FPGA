#!/usr/bin/env python3
"""Run the frozen real input sequentially, preserving all commands and checksums."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))
from prepare_real import sha, UPSTREAM


def parse_log(text):
    timing = re.search(r"timing: load=(\d+) ms, route=(\d+) ms, write .result=(\d+) ms, total=(\d+) ms", text)
    summary = re.search(r"ROUTE_SUMMARY iters=(\d+) overused=(\d+).*totalPushes=(\d+)", text)
    wire = re.search(r"WIRELENGTH usedNodes=(\d+) totalLen=(\d+)", text)
    iterations = re.findall(r"^\s*(\d+)\s+overused=(\d+)\s+totalOveruse=(\d+)\s+unroutable=(\d+)\s+rerouted=(\d+)", text, re.M)
    bbox = re.search(r"\[bbox\].*prep=([\d.]+)s solve=([\d.]+)s", text)
    if not timing or not summary or not wire or not iterations:
        raise ValueError("Missing completed route metrics")
    result = dict(zip(("load_ms", "route_ms", "write_ms", "total_ms"), map(int, timing.groups())))
    result.update(dict(zip(("iterations", "overused", "pushes"), map(int, summary.groups()))))
    result.update(dict(zip(("used_nodes", "wire_length"), map(int, wire.groups()))))
    result["convergence"] = [list(map(int, row)) for row in iterations]
    result["bbox_ms"] = sum(map(float, bbox.groups())) * 1000 if bbox else None
    if result["overused"] or result["convergence"][-1][3]:
        raise ValueError("Routing did not converge")
    return result


def validate(config, build):
    if config.get("dataset_kind") != "real_placed_netlist":
        raise ValueError("Only verified real placed netlists are accepted")
    if not 1 <= config["repetitions"] <= 10 or len(config["sample_intervals_us"]) != config["repetitions"]:
        raise ValueError("Provide one sampling interval per repetition (1 to 10 runs)")
    if config["trace_stride"] < 1 or config["trace_cap"] != 200000:
        raise ValueError("Trace build requires positive stride and its fixed 200000 event cap")
    if any(interval < 1000 for interval in config["sample_intervals_us"]):
        raise ValueError("Sample intervals must be at least 1000 us")
    if sha(ROOT / config["input"]) != config["input_sha256"]:
        raise ValueError("Input hash mismatch")
    if config["cpu"] not in os.sched_getaffinity(0):
        raise ValueError("Requested CPU unavailable")
    for path, digest in build["inputs"].items():
        if sha(path) != digest:
            raise ValueError(f"Build input changed: {path}")
    for mode in ("original", "profile", "trace"):
        if sha(ROOT / f"build/real_trace/router_{mode}") != build[mode]["binary_sha256"]:
            raise ValueError(f"Binary changed: {mode}")


def run(config, directory):
    build = json.loads((ROOT / "build/real_trace/build.json").read_text())
    validate(config, build)
    directory.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "dataset_kind": config["dataset_kind"], "config": config,
              "build": build, "host": platform.platform(), "python": sys.version,
              "cpuinfo": Path("/proc/cpuinfo").read_text().split("\n\n")[0],
              "source_provenance": json.loads((ROOT / "data/derived/logicnets_jscl_provenance.json").read_text()),
              "started_utc": datetime.now(timezone.utc).isoformat(), "runs": []}
    manifest = directory / "manifest.json"
    def save(): manifest.write_text(json.dumps(record, indent=2) + "\n")
    save()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RW_", "B_SAMPLE", "B_TRACE", "B_PROFILE"))}
    env.update(config["environment"])
    schedule = [(mode, rep) for rep in range(config["repetitions"]) for mode in ("original", "profile")]
    random.Random(config["order_seed"]).shuffle(schedule)
    schedule.append(("trace", 0))
    digest = None
    convergence = None
    try:
        for mode, rep in schedule:
            name = f"{mode}_{rep}"
            prefix = directory / name
            result = prefix.with_suffix(".result")
            extra = {}
            if mode != "original": extra["B_PROFILE_PREFIX"] = str(prefix)
            if mode == "profile": extra["B_SAMPLE_US"] = str(config["sample_intervals_us"][rep])
            if mode == "trace":
                extra.update(B_TRACE_PREFIX=str(prefix), B_TRACE_STRIDE=str(config["trace_stride"]))
            command = ["/usr/bin/time", "-v", "-o", str(prefix.with_suffix(".time")),
                       "taskset", "-c", str(config["cpu"]), str(ROOT / f"build/real_trace/router_{mode}"),
                       str(ROOT / config["input"]), str(result)]
            entry = {"name": name, "mode": mode, "repetition": rep, "command": command,
                     "environment": dict(config["environment"], **extra)}
            record["runs"].append(entry); save()
            started = time.monotonic()
            with prefix.with_suffix(".log").open("w") as log:
                process = subprocess.run(command, cwd=ROOT, env=dict(env, **extra),
                                         stdout=log, stderr=subprocess.STDOUT, timeout=600)
            entry.update(exit_code=process.returncode, process_wall_seconds=time.monotonic()-started)
            if process.returncode: raise RuntimeError(f"{name} exited {process.returncode}")
            entry["metrics"] = parse_log(prefix.with_suffix(".log").read_text())
            if mode != "original": entry["profile"] = json.loads(prefix.with_suffix(".json").read_text())
            entry["result_sha256"] = sha(result)
            if digest is None: digest = entry["result_sha256"]; convergence = entry["metrics"]["convergence"]
            if digest != entry["result_sha256"] or convergence != entry["metrics"]["convergence"]:
                raise ValueError(f"Instrumentation changed routing in {name}")
            entry["matches_other_runs"] = True
            save()
            print(f"{name}: route={entry['metrics']['route_ms']}ms, identical output and convergence", flush=True)
        # Check graph legality independently, outside every timing interval.
        verifier = ROOT / "build/real_trace/verify_real"
        command = ["g++", "-std=c++17", "-O2", "-fno-fast-math", "-pthread",
                   "-I", str(ROOT / "build/real_trace"), "-I", str(UPSTREAM / "cpp_router/include"),
                   str(ROOT / "adapters/verify_real.cpp"), "-o", str(verifier)]
        subprocess.run(command, check=True, timeout=180)
        record["verification_command"] = [str(verifier), str(ROOT / config["input"]), str(directory / "original_0.result")]
        record["verification"] = json.loads(subprocess.check_output(record["verification_command"], env=env, text=True, timeout=120))
        record["verifier_build"] = {"command": command, "source_sha256": sha(ROOT / "adapters/verify_real.cpp"),
                                    "binary_sha256": sha(verifier)}
        validate(config, build)
        record["status"] = "passed"
    except Exception as error:
        record["status"] = "failed"; record["error"] = str(error)
        raise
    finally:
        record["finished_utc"] = datetime.now(timezone.utc).isoformat(); save()
    print(f"Saved {manifest}", flush=True)
    return directory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/real_trace.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    directory = args.output or ROOT / "results" / ("real_trace_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    run(json.loads(args.config.read_text()), directory.resolve())
    return 0


if __name__ == "__main__": raise SystemExit(main())
