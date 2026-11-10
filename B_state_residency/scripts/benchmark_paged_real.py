#!/usr/bin/env python3
"""Compare identical real-router schedules with page clearing or node epochs."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import random
import re
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"adapters"))
from prepare_real import sha, UPSTREAM
from profile_real import parse_log


def validate(config, build):
    if config.get("dataset_kind")!="real_placed_netlist": raise ValueError("Real dataset required")
    if sha(ROOT/config["input"])!=config["input_sha256"]: raise ValueError("Input hash mismatch")
    if not 2<=config["page_bits"]<=12: raise ValueError("Invalid page bits")
    if not 1<=config["repetitions"]<=10: raise ValueError("Invalid repetition count")
    for path,digest in build["inputs"].items():
        if sha(path)!=digest: raise ValueError(f"Build input changed: {path}")
    for variant,row in build["variants"].items():
        if sha(row["binary"])!=row["binary_sha256"] or sha(row["source"])!=row["source_sha256"]:
            raise ValueError(f"Build changed: {variant}")


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/paged_real.json")
    parser.add_argument("--output",type=Path)
    parser.add_argument("--pilot",action="store_true",help="one repetition, same validity gates")
    parser.add_argument("--mode",choices=("serial","batch","all"),default="all")
    parser.add_argument("--skip-self-test",action="store_true",help="reuse a recorded successful semantic test for this exact build")
    args=parser.parse_args(argv)
    config=json.loads(args.config.read_text())
    if args.pilot: config["repetitions"]=1
    build=json.loads((ROOT/config["build"]).read_text());validate(config,build)
    directory=(args.output or ROOT/"results"/("paged_real_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    reference=json.loads((ROOT/"results/real_trace_20261022T165136Z/manifest.json").read_text())
    original=ROOT/"build/real_trace/router_original"
    if sha(original)!=reference["build"]["original"]["binary_sha256"]: raise ValueError("Serial reference binary changed")
    expected_serial=reference["runs"][0]["result_sha256"]
    record={"status":"running","config":config,"build":build,"mode":args.mode,"pilot":args.pilot,
            "host":platform.platform(),"reference_result_sha256":expected_serial,"runs":[],
            "started_utc":datetime.now(timezone.utc).isoformat(),"tool_sha256":sha(__file__),
            "cpu_model":next(line for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))}
    manifest=directory/"manifest.json"
    def save(): manifest.write_text(json.dumps(record,indent=2)+"\n")
    save()
    clean={k:v for k,v in os.environ.items() if not k.startswith(("RW_","B_"))}
    test_record=Path(config["build"]).parent/"semantic_tests.json"
    try:
        if args.skip_self_test:
            tests=json.loads((ROOT/test_record).read_text())
            if tests["status"]!="passed" or tests["source_sha256"]!=sha(ROOT/"tests/paged_semantics.cpp") or tests["build"]!=build:
                raise ValueError("No matching passed semantic test")
        else:
            tests={"status":"running","build":build,"source_sha256":sha(ROOT/"tests/paged_semantics.cpp"),"checks":{}}
            for variant,row in build["variants"].items():
                test=Path(row["source"]).parent/"test_labels"
                cmd=["g++","-std=c++17","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-pthread",
                     "-I",str(Path(row["source"]).parent),"-I",str(UPSTREAM/"cpp_router/include"),str(ROOT/"tests/paged_semantics.cpp"),"-o",str(test)]
                subprocess.run(cmd,check=True,timeout=240)
                result=subprocess.check_output([str(test)],text=True,env=dict(clean,ASAN_OPTIONS="detect_leaks=1"),timeout=60)
                tests["checks"][variant]={"build_command":cmd,"binary_sha256":sha(test),"result":json.loads(result)}
                print(f"{variant}: ASan/UBSan semantic checks passed",flush=True)
            tests["status"]="passed";(ROOT/test_record).write_text(json.dumps(tests,indent=2)+"\n")
        record["semantic_tests"]=tests;save()
        modes=["serial","batch"] if args.mode=="all" else [args.mode]
        schedule=[]
        rng=random.Random(config["seed"])
        for rep in range(config["repetitions"]):
            block=[(mode,v,rep) for mode in modes for v in (("original","paged","node_epoch") if mode=="serial" else ("paged","node_epoch"))]
            rng.shuffle(block);schedule.extend(block)
        expected={};convergence={};verified={}
        for mode,variant,rep in schedule:
            name=f"{mode}_{variant}_{rep}"
            prefix=directory/name
            binary=original if variant=="original" else Path(build["variants"][variant]["binary"])
            env={"RW_MAX_THREADS":"1","RW_PAR_PART":"0","RW_PAR_ITER1":"0","RW_OVERLAP":"0","RW_BATCH_T":"0","RW_GPU_FLOOD":"0"} if mode=="serial" else dict(config["batch_environment"])
            env["RW_BATCH_PBITS"]=str(config["page_bits"])
            if mode=="serial" and variant!="original": env["B_SERIAL_PAGED"]="1"
            if variant!="original": env["B_LABEL_REPORT"]=str(prefix.with_suffix(".labels.json"))
            cpus=config["serial_cpu"] if mode=="serial" else config["batch_cpus"]
            command=["/usr/bin/time","-v","-o",str(prefix.with_suffix(".time")),"taskset","-c",cpus,str(binary),str(ROOT/config["input"]),str(prefix.with_suffix(".result"))]
            row={"name":name,"mode":mode,"variant":variant,"repetition":rep,"command":command,"environment":env}
            record["runs"].append(row);save();start=time.monotonic()
            with prefix.with_suffix(".log").open("w") as log:
                proc=subprocess.run(command,env=dict(clean,**env),stdout=log,stderr=subprocess.STDOUT,timeout=config["timeout_seconds"])
            row.update(exit_code=proc.returncode,process_wall_seconds=time.monotonic()-start)
            if proc.returncode: raise RuntimeError(f"Run failed: {name}")
            text=prefix.with_suffix(".log").read_text();row["metrics"]=parse_log(text)
            row["result_sha256"]=sha(prefix.with_suffix(".result"))
            memory=re.search(r"Maximum resident set size \(kbytes\): (\d+)",prefix.with_suffix(".time").read_text())
            row["max_rss_kib"]=int(memory[1])
            if variant!="original":
                row["labels"]=json.loads(prefix.with_suffix(".labels.json").read_text())
                if mode=="batch" and (not row["labels"]["contexts"] or "[batch-leaf]" not in text): raise ValueError("Batch path was not exercised")
            if mode=="serial" and row["result_sha256"]!=expected_serial: raise ValueError("Serial paging changed reference routing")
            if mode in expected and (row["result_sha256"]!=expected[mode] or row["metrics"]["convergence"]!=convergence[mode]):
                raise ValueError(f"Same-schedule label ablation changed output/convergence: {mode}")
            expected[mode]=row["result_sha256"];convergence[mode]=row["metrics"]["convergence"]
            if row["result_sha256"] not in verified:
                cmd=[str(ROOT/"build/real_trace/verify_real"),str(ROOT/config["input"]),str(prefix.with_suffix(".result"))]
                result=json.loads(subprocess.check_output(cmd,env=dict(clean,RW_MAX_THREADS="1"),text=True,timeout=120))
                verified[row["result_sha256"]]={"command":cmd,"result":result}
            row["verified"]=True;save()
            print(f"{name}: route={row['metrics']['route_ms']}ms rss={row['max_rss_kib']/1024:.1f}MiB, verified",flush=True)
        validate(config,build)
        record["verification"]=verified
        summary={}
        for mode in modes:
            for variant in ("original","paged","node_epoch"):
                rows=[r for r in record["runs"] if r["mode"]==mode and r["variant"]==variant]
                if rows: summary[f"{mode}_{variant}"]={"repetitions":len(rows),"route_ms":statistics.median(r["metrics"]["route_ms"] for r in rows),"total_ms":statistics.median(r["metrics"]["total_ms"] for r in rows),"max_rss_kib":statistics.median(r["max_rss_kib"] for r in rows)}
        record["summary"]=summary;record["status"]="passed"
    except Exception as error:
        record["status"]="failed";record["error"]=str(error);raise
    finally:
        record["finished_utc"]=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({"manifest":str(manifest),"summary":record["summary"]},indent=2),flush=True)
    return 0


if __name__=="__main__":raise SystemExit(main())
