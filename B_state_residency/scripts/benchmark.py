#!/usr/bin/env python3
"""Build and measure extracted CPU state primitives on explicit synthetic traces."""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.extract_state import SOURCE, extract

VARIANTS = {"cpu_dense_init", "cpu_serial_stamp", "cpu_existing_paged",
            "cpu_paged_node_epoch", "cpu_lifetime_residency"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(config):
    if config["dataset_kind"] != "synthetic_state_microbenchmark":
        raise ValueError("This runner only accepts synthetic state workloads")
    for key, low, high in [("nodes", 256, 1 << 20), ("repetitions", 1, 100),
                           ("timeout_seconds", 1, 600)]:
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError(f"Invalid {key}")
    if not config["variants"] or set(config["variants"]) - VARIANTS:
        raise ValueError("Unknown or empty variant list")
    if len(set(config["variants"])) != len(config["variants"]):
        raise ValueError("Duplicate variants")
    if not config["seeds"] or any(type(s) is not int or not 0 <= s < 2**31 for s in config["seeds"]):
        raise ValueError("Invalid seeds")
    if not config["page_bits"] or any(type(b) is not int or not 2 <= b <= 12 for b in config["page_bits"]):
        raise ValueError("Invalid page_bits")
    if not config["workloads"] or len({w["id"] for w in config["workloads"]}) != len(config["workloads"]):
        raise ValueError("Workload IDs must be nonempty and unique")
    for w in config["workloads"]:
        for k, lo, hi in [("queries", 1, 999999), ("touches", 1, config["nodes"]), ("fanout", 1, 4096)]:
            if type(w[k]) is not int or not lo <= w[k] <= hi:
                raise ValueError(f"Invalid workload {k}")
        if type(w["scattered"]) is not bool:
            raise ValueError("scattered must be boolean")


def run(command, timeout=120):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {command}\n{result.stderr[-5000:]}")
    return result


def verify_samples(samples):
    """Compare all variants, page sizes and repetitions for each identical trace."""
    oracle = {}
    for row in samples:
        key = (row["workload"], row["seed"])
        result = row["result"]
        signature = [result["trace_fingerprint"]]
        for phase in ("first", "reuse"):
            p = result[phase]
            signature.extend(p[k] for k in ("label_checksum", "share_checksum", "packet_checksum", "packed_nodes"))
            if any(not math.isfinite(v) or v < 0 for k, v in p.items() if k.endswith("_ms")):
                raise ValueError("Invalid measured time")
        if key in oracle and signature != oracle[key]:
            raise ValueError(f"Differential check failed: {row['variant']} {key}")
        oracle[key] = signature


def summarize(samples):
    groups = {}
    for row in samples:
        key = (row["workload"], row["variant"], row["page_bits"])
        groups.setdefault(key, []).append(row["result"])
    rows = []
    for (workload, variant, page_bits), values in sorted(groups.items(), key=lambda item: str(item[0])):
        record = {"workload": workload, "variant": variant, "page_bits": page_bits, "sample_count": len(values)}
        for phase in ("first", "reuse"):
            record[phase] = {}
            for metric in values[0][phase]:
                if not metric.endswith("_ms"):
                    continue
                data = [v[phase][metric] for v in values]
                record[phase][metric] = {"median": statistics.median(data), "min": min(data), "max": max(data)}
        record["label_capacity_bytes"] = max(v["label_capacity_bytes"] for v in values)
        record["label_allocation_ms_median"] = statistics.median(v["label_allocation_ms"] for v in values)
        rows.append(record)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/state_microbench.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--sanitize", action="store_true", help="ASan/UBSan semantic checks; never use sanitized timings")
    args = parser.parse_args(argv)
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = args.output or ROOT / "results" / f"state_microbench_{stamp}.json"
    if output.exists():
        parser.error(f"Refusing to overwrite {output}")
    config = json.loads(args.config.read_text())
    validate(config)
    build = ROOT / "build" / stamp
    build.mkdir(parents=True, exist_ok=False)
    provenance = extract(build / "original_state.inc")
    compiler = shutil.which("g++")
    if not compiler:
        parser.error("g++ is required for the C++ microbenchmark")
    flags = ["-std=c++17", "-O3", "-fno-fast-math", "-Wall", "-Wextra", "-Werror", "-pthread", "-I", str(build)]
    source = ROOT / "src/state_bench.cpp"
    binary = build / "state_bench"
    compile_command = [compiler, *flags, str(source), "-o", str(binary)]
    run(compile_command)
    check = json.loads(run([str(binary), "--self-test"]).stdout)
    sanitizer_check = None
    if args.sanitize:
        sanitized = build / "state_check_sanitized"
        run([compiler, *flags, "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
             str(source), "-o", str(sanitized)])
        sanitizer_check = json.loads(run([str(sanitized), "--self-test"]).stdout)
    allowed = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    taskset = shutil.which("taskset")
    prefix = [taskset, "-c", str(allowed[0])] if allowed and taskset else []
    cpuinfo = Path("/proc/cpuinfo").read_text() if Path("/proc/cpuinfo").exists() else ""
    cpu_model = next((line.split(":", 1)[1].strip() for line in cpuinfo.splitlines()
                      if line.startswith("model name")), platform.processor())
    record = {"schema_version": 1, "project_id": "B", "execution_kind": "synthetic_state_microbenchmark",
              "backend": "cpp_cpu", "status": "running", "timestamp_utc": stamp,
              "config": config, "config_sha256": digest(args.config), "source_provenance": provenance,
              "local_source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in
                                      (source, Path(__file__), ROOT / "adapters/extract_state.py")},
              "compiler": run([compiler, "--version"]).stdout.splitlines()[0],
              "compile_command": compile_command, "binary_sha256": digest(binary),
              "environment": {"platform": platform.platform(), "cpu_model": cpu_model,
                              "affinity_cpu": allowed[0] if prefix else None,
                              "allowed_cpus": allowed, "python": platform.python_version(),
                              "clock": "std::chrono::steady_clock", "loadavg_at_start": os.getloadavg()},
              "checks": {"self_test": check, "sanitizers": sanitizer_check},
              "measurement_scope": {
                  "input": "generated accesses and branch paths, no physical graph or search",
                  "first": "first trace pass after allocation and preseeded occupancy",
                  "reuse": "second pass on the same allocated state, labels always invalidated",
                  "reset_ms": "explicit search reset; does not include lazy page/node initialization",
                  "label_access_including_lazy_init_ms": "four access passes, target set/cleanup, checksum arithmetic and lazy initialization",
                  "commit_ms": "original serial owner slots, reduced occupancy mirror and optional net index; excludes path materialization",
                  "sync_host_pack_ms": "host dirty-list packing using a synthetic price formula; no device transfer",
                  "phase_sum_ms": "sum of measured state phases; excludes construction, graph/search, path materialization, validation and I/O",
                  "label_capacity_bytes": "vector payload capacities only; excludes allocator overhead and shared design/net state",
                  "diagnostics": "separate instrumented runs; page miss timers perturb performance, do not use for speedup"},
              "hardware_measurements": {"device_transfer_ms": None, "fpga_ms": None, "gpu_ms": None,
                                        "routing_ms": None, "routing_speedup": None},
              "samples": [], "diagnostics": []}
    try:
        if not args.self_test_only:
            jobs = []
            for workload, seed, repetition, variant in itertools.product(
                    config["workloads"], config["seeds"], range(config["repetitions"]), config["variants"]):
                pages = config["page_bits"] if variant not in {"cpu_dense_init", "cpu_serial_stamp"} else [None]
                jobs.extend((workload, seed, repetition, variant, pb) for pb in pages)
            random.Random(config["order_seed"]).shuffle(jobs)
            last_notice = time.monotonic()
            for index, (w, seed, repetition, variant, pb) in enumerate(jobs):
                command = [*prefix, str(binary), variant, str(config["nodes"]), str(w["queries"]),
                           str(w["touches"]), str(w["fanout"]), str(pb or 9), str(seed), str(int(w["scattered"]))]
                result = json.loads(run(command, config["timeout_seconds"]).stdout)
                record["samples"].append({"workload": w["id"], "seed": seed, "repetition": repetition,
                                          "variant": variant, "page_bits": pb, "command": command, "result": result})
                if time.monotonic() - last_notice > 15:
                    print(f"Measured {index + 1}/{len(jobs)} samples", file=sys.stderr, flush=True)
                    last_notice = time.monotonic()
            verify_samples(record["samples"])
            diagnostic = build / "state_diagnostic"
            diagnostic_command = [compiler, *flags, "-DB_STATE_DIAGNOSTIC", str(source), "-o", str(diagnostic)]
            run(diagnostic_command)
            record["diagnostic_compile_command"] = diagnostic_command
            for w, pb in itertools.product(config["workloads"], config["page_bits"]):
                command = [*prefix, str(diagnostic), "cpu_existing_paged", str(config["nodes"]), str(w["queries"]),
                           str(w["touches"]), str(w["fanout"]), str(pb), str(config["seeds"][0]), str(int(w["scattered"]))]
                result = run(command, config["timeout_seconds"])
                record["diagnostics"].append({"workload": w["id"], "page_bits": pb, "command": command,
                                              "result": json.loads(result.stdout), "probes": json.loads(result.stderr)})
            record["summary"] = summarize(record["samples"])
            record["checks"]["all_variant_fingerprints_equal"] = True
        if digest(SOURCE) != provenance["source_sha256"]:
            raise ValueError("Original source changed during measurement")
        record["checks"]["original_source_unchanged"] = True
        record["status"] = "passed"
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        record["status"] = "failed"
        record["error"] = str(exc)
    record["elapsed_seconds"] = time.monotonic() - started
    record["environment"]["loadavg_at_end"] = os.getloadavg()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(record, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": record["status"], "samples": len(record["samples"]),
                      "output": str(output.resolve())}, ensure_ascii=False))
    if record["status"] != "passed":
        print(record["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
