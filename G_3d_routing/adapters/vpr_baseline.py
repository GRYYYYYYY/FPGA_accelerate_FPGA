"""Reproduce the pinned original VPR on frozen model inputs, sequentially.

No placement regeneration, source mutation, or modified sibling router. Failed
runs and timeouts remain in the new batch directory. Native FULL legality and
an independent scoped XML audit are both required. Timing is descriptive on a
shared CPU host; no acceleration comparison is inferred.
"""
import argparse
from dataclasses import astuple
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import statistics
import subprocess
import time

from adapters.common import ROOT, read_json, sha256, verified_file, write_new
from adapters.route_audit import audit, batch_graph_evidence, read_trace
from adapters.vpr_rrg import check_route_projection


def parse_metrics(log):
    patterns = {
        "critical_path_delay_ns": r"Final critical path delay \(least slack\):\s+([\d.eE+-]+)\s+ns",
        "routed_wirelength": r"Total wirelength:\s+(\d+)",
        "routing_seconds": r"Routing took\s+([\d.eE+-]+)\s+seconds",
        "routing_iterations": r"Successfully routed after\s+(\d+)\s+routing iterations",
    }
    result = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, log)
        result[key] = float(matches[-1]) if matches else None
    result["native_full_check_passed"] = "Completed routing consistency check successfully." in log
    result["routing_success"] = "Circuit successfully routed" in log
    return result


def route_fingerprint(path):
    # Route headers contain output paths. Compare every parsed routing record,
    # including branch restarts, switch identity and sink pin index instead.
    nets = read_trace(path)
    payload = [(nid, net["name"], [astuple(n) for n in net["trace"]]) for nid, net in sorted(nets.items())]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def build_command(binary, files, case, directory):
    return [str(binary), str(files["architecture"]), str(files["circuit"]),
            "--route_chan_width", str(case["route_chan_width"]),
            "--device_width", str(case["device_width"]),
            "--target_utilization", str(case["target_utilization"]),
            "--seed", str(case["seed"]), "--num_workers", "1",
            "--router_algorithm", "timing_driven", "--flat_routing", "off",
            "--check_route", "full", "--net_file", str(files["packed_netlist"]),
            "--place_file", str(files["placement"]), "--route_file", str(directory / "routed.route"),
            "--timing_report_npaths", "10", "--route", "--analysis",
            "--read_rr_graph", str(files["rr_graph"])]


def runtime_environment(lock):
    for record in lock["runtime"]["libraries"]:
        verified_file(record)
    env = os.environ.copy()
    for name in list(env):
        if name.startswith("VPR_H3D_"):
            del env[name]
    env.update(OMP_NUM_THREADS="1", LC_ALL="C",
               LD_LIBRARY_PATH=str((ROOT / lock["runtime"]["library_directory"]).resolve()))
    return env


def run_once(binary, files, case, directory, timeout, env):
    directory.mkdir()
    command = build_command(binary, files, case, directory)
    record = {"execution_kind": "real_benchmark", "model_scope": "stacked_3d_fpga_architecture_model",
              "backend": "native_vpr_cpu", "variant": "original_vpr", "case_id": case["id"],
              "placement_kind": case["placement_kind"], "seed": case["seed"],
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "command": command, "cwd": str(directory), "timeout_seconds": timeout,
              "input_hashes": {k: sha256(v) for k, v in files.items()},
              "binary_sha256": sha256(binary),
              "environment": {k: env.get(k) for k in ("OMP_NUM_THREADS", "LC_ALL", "LD_LIBRARY_PATH")},
              "experimental_environment": {}, "status": "running"}
    write_new(directory / "invocation.json", record)
    start = time.monotonic()
    timed_command = ["/usr/bin/time", "-v", "-o", str(directory / "resource_usage.txt"), *command]
    with (directory / "vpr.log").open("x") as stream:
        process = subprocess.Popen(timed_command, cwd=directory, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
            record.update(status="completed" if code == 0 else "failed", returncode=code)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            record.update(status="timeout" if isinstance(exc, subprocess.TimeoutExpired) else "interrupted",
                          returncode=process.returncode)
    record["process_wall_seconds"] = time.monotonic() - start
    record["metrics"] = parse_metrics((directory / "vpr.log").read_text(errors="replace"))
    record["output_files"] = {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size}
                              for p in directory.iterdir() if p.is_file()}
    write_new(directory / "process.json", record)
    return record


def run_batch(args):
    lock_path = ROOT / "configs/vpr.lock.json"
    lock = read_json(lock_path)
    binary = verified_file(lock["binary"])
    verified_file(lock["archived_build_manifest"])
    verified_file(lock["route_audit_snapshot"]["local"])
    env = runtime_environment(lock)
    linked = subprocess.run(["ldd", str(binary)], env=env, capture_output=True, text=True, check=True).stdout
    if "not found" in linked:
        raise ValueError(f"Missing baseline runtime dependency:\n{linked}")
    case_paths = [ROOT / "data/raw" / f"{name}.json" for name in args.cases]
    cases = [read_json(path) for path in case_paths]
    prepared = [{k: verified_file(v) for k, v in case["inputs"].items()} for case in cases]
    for case in cases:
        verified_file(case["prepared_manifest"])
        verified_file(case["reference"]["manifest"])
        verified_file(case["reference"]["route"])
    projection = read_json(args.graph_export / "summary.json")
    if projection["status"] != "complete":
        raise ValueError("Graph export incomplete")
    database = verified_file(projection["database"])
    if any(case["inputs"]["rr_graph"]["sha256"] != projection["source"]["sha256"] for case in cases):
        raise ValueError("Cases do not match the exported graph")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = (args.output or ROOT / "results" / f"baseline_{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=False)
    cpu = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")), None)
    batch = {"schema_version": 1, "execution_kind": "real_benchmark",
             "variant": "original_vpr", "backend": "native_vpr_cpu",
             "model_scope": "Hecate native 3D architecture model; balanced case is a constructed placement fixture",
             "status": "running", "upstream_commit": lock["upstream_commit"],
             "binary_sha256": lock["binary"]["sha256"], "toolchain_lock_sha256": sha256(lock_path),
             "case_manifests": {str(p): sha256(p) for p in case_paths},
             "code_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in (ROOT / "adapters").glob("*.py")},
             "graph_export": {"path": str(args.graph_export.resolve()), "database_sha256": projection["database"]["sha256"]},
             "environment": {"platform": platform.platform(), "python": platform.python_version(),
                             "cpu": cpu, "cpu_affinity": sorted(os.sched_getaffinity(0)),
                             "load_average_start": os.getloadavg(), "ldd": linked},
             "repetitions": args.repetitions, "execution_order": "case-major, sequential",
             "timing_scope": {"native_routing": "VPR 'Routing took' log value, 0.01 s printed resolution",
                              "process_wall": "route-only process: graph/netlist read + routing + analysis + time wrapper; excludes hashing/export/audit",
                              "comparison": "descriptive baseline repeats only; shared-host load uncontrolled; no speedup claim"},
             "runs": []}
    write_new(output / "batch_invocation.json", batch)
    try:
        for case, files in zip(cases, prepared):
            reference_fp = route_fingerprint(Path(case["reference"]["route"]["path"]))
            for repeat in range(1, args.repetitions + 1):
                name = f"{case['id']}_r{repeat}"
                record = run_once(binary, files, case, output / name, args.timeout, env)
                record["directory"] = name
                record["repetition"] = repeat
                record["reference_route_fingerprint"] = reference_fp
                batch["runs"].append(record)
                print(json.dumps({"run": name, "status": record["status"], "metrics": record["metrics"]}), flush=True)
                if record["status"] == "interrupted":
                    raise KeyboardInterrupt
        routes = [output / r["directory"] / "routed.route" for r in batch["runs"]
                  if (output / r["directory"] / "routed.route").exists()]
        # Both cases use exactly the same graph; parse XML once for the batch.
        evidence = batch_graph_evidence(prepared[0]["rr_graph"], routes) if routes else None
        for record in batch["runs"]:
            directory = output / record["directory"]
            route = directory / "routed.route"
            checks = {"process_completed": record["status"] == "completed",
                      "native_full_check": record["metrics"]["native_full_check_passed"],
                      "routing_success": record["metrics"]["routing_success"]}
            if route.exists():
                result = audit(prepared[0]["rr_graph"], route, graph_evidence=evidence)
                write_new(directory / "route_audit.json", result)
                record["route_audit"] = {k: v for k, v in result.items() if k != "nets"}
                checks["scoped_xml_audit"] = result["passed"]
                checks["derived_graph_route_match"] = check_route_projection(database, route)["passed"]
                checks["reference_route_equal"] = route_fingerprint(route) == record["reference_route_fingerprint"]
                case = next(c for c in cases if c["id"] == record["case_id"])
                remote = result["route"]["cross_layer_sink_connections"]
                checks["endpoint_layer_coverage"] = remote == 0 if case["expected_cross_layer_connections"] == 0 else remote > 0
                checks["reference_cpd_equal"] = record["metrics"]["critical_path_delay_ns"] == case["reference"]["metrics"]["critical_path_ns"]
                checks["reference_wirelength_equal"] = record["metrics"]["routed_wirelength"] == case["reference"]["metrics"]["wirelength"]
            else:
                checks["route_exists"] = False
            record["checks"] = checks
            record["status"] = "passed" if all(checks.values()) else "failed"
            write_new(directory / "result.json", record)
        # Do not accept evidence if any referenced bytes changed mid-experiment.
        for case in cases:
            for rec in case["inputs"].values():
                verified_file(rec)
        verified_file(lock["binary"])
        runtime_environment(lock)
        verified_file(projection["database"])
        batch["status"] = "passed" if all(r["status"] == "passed" for r in batch["runs"]) else "failed"
        batch["summary"] = {}
        for case in cases:
            rows = [r for r in batch["runs"] if r["case_id"] == case["id"] and r["status"] == "passed"]
            values = [r["metrics"]["routing_seconds"] for r in rows]
            batch["summary"][case["id"]] = {"passed_repetitions": len(rows),
                "routing_seconds_median": statistics.median(values) if values else None,
                "routing_seconds_min": min(values) if values else None,
                "routing_seconds_max": max(values) if values else None}
    except BaseException as exc:
        batch.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        batch["environment"]["load_average_end"] = os.getloadavg()
        write_new(output / "summary.json", batch)
        print(json.dumps({"status": batch["status"], "output": str(output)}), flush=True)
    return 0 if batch["status"] == "passed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=["ex5p_natural", "ex5p_balanced"], default=["ex5p_natural", "ex5p_balanced"])
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--graph-export", type=Path, default=ROOT / "data/derived/ex5p_w100")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.repetitions < 1 or args.timeout < 1 or len(args.cases) != len(set(args.cases)):
        parser.error("Positive repetition/timeout values and unique cases required")
    try:
        return run_batch(args)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
