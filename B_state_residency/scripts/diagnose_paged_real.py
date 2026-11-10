#!/usr/bin/env python3
"""Count real page/node initializations separately from performance measurements."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"adapters"))
from prepare_real import sha
from benchmark_paged_real import validate
from profile_real import parse_log


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/paged_real.json")
    parser.add_argument("--build",type=Path,default=ROOT/"build/paged_real_diag/build.json")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    config=json.loads(args.config.read_text());build=json.loads(args.build.read_text());validate(config,build)
    if not build["diagnostic"]: raise ValueError("Counter-enabled build required")
    directory=(args.output or ROOT/"results"/("paged_diagnostic_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    reference=json.loads((ROOT/"results/real_trace_20261022T165136Z/manifest.json").read_text())["runs"][0]["result_sha256"]
    record={"status":"running","performance_use":False,"config":config,"build":build,"runs":[],"tool_sha256":sha(__file__)}
    def save(): (directory/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
    save();env={k:v for k,v in os.environ.items() if not k.startswith(("RW_","B_"))}
    try:
        for variant,entry in build["variants"].items():
            prefix=directory/variant
            extra={"RW_MAX_THREADS":"1","RW_PAR_PART":"0","RW_PAR_ITER1":"0","RW_OVERLAP":"0","RW_BATCH_T":"0","RW_GPU_FLOOD":"0",
                   "RW_BATCH_PBITS":str(config["page_bits"]),"B_SERIAL_PAGED":"1","B_LABEL_REPORT":str(prefix.with_suffix(".labels.json"))}
            cmd=["taskset","-c",config["serial_cpu"],entry["binary"],str(ROOT/config["input"]),str(prefix.with_suffix(".result"))]
            row={"variant":variant,"command":cmd,"environment":extra};record["runs"].append(row);save()
            with prefix.with_suffix(".log").open("w") as log:
                subprocess.run(cmd,env=dict(env,**extra),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=config["timeout_seconds"])
            row["metrics_diagnostic_only"]=parse_log(prefix.with_suffix(".log").read_text())
            row["result_sha256"]=sha(prefix.with_suffix(".result"))
            if row["result_sha256"]!=reference: raise ValueError("Counters changed real routing")
            row["labels"]=json.loads(prefix.with_suffix(".labels.json").read_text())
            if not row["labels"]["diagnostic"]: raise ValueError("No counters in diagnostic")
            context=row["labels"]["contexts"][0]
            if context["resets"]!=570286 or not context["cleared_nodes"]: raise ValueError("Missing reset/clear events")
            save();print(variant,context,flush=True)
        a,b=[r["labels"]["contexts"][0] for r in record["runs"]]
        if a["page_claims"]!=b["page_claims"] or a["resets"]!=b["resets"]: raise ValueError("Different real access page sequence")
        record["clear_slot_reduction_factor"]=a["cleared_nodes"]/b["cleared_nodes"]
        record["status"]="passed"
    except Exception as error:
        record["status"]="failed";record["error"]=str(error);raise
    finally:save()
    print(directory,flush=True)


if __name__=="__main__":main()
