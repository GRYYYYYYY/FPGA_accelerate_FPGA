"""Export another genuine placed Interchange design through the pinned RRT1 exporter."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from prepare_real import ROOT, JAVA_BIN, UPSTREAM, RUNTIME, sha


def export(dataset, logical, physical):
    output = ROOT/f"data/derived/{dataset}.rrt"
    manifest = output.with_name(dataset+"_provenance.json")
    if output.exists():
        record=json.loads(manifest.read_text())
        if record["status"]!="exported" or sha(output)!=record["output_sha256"]:raise ValueError("Existing export mismatch")
        for p,info in record["files"].items():
            if sha(p)!=info["sha256"]:raise ValueError("Export input changed")
        print("Reused verified",output,flush=True);return
    directory=ROOT/f"build/export_{dataset}";directory.mkdir(parents=True,exist_ok=False)
    classes=directory/"java";classes.mkdir()
    original=UPSTREAM/"RapidWright/src/com/xilinx/rapidwright/rwroute/RWRouteCppProblemExport.java"
    if sha(original)!="e182643773bb4affda26368224f8d8da42183bc1a1942068804d37fdc9ccb73a":raise ValueError("Exporter snapshot changed")
    text=original.read_text()
    if text.count("RWRoute.rwMaxThreads()")!=2:raise ValueError("Compatibility anchors changed")
    generated=directory/original.name;generated.write_text(text.replace("RWRoute.rwMaxThreads()","48"))
    jar=RUNTIME/"rapidwright.jar"
    if sha(jar)!="0c68053094351987a16920b05f155e3b7180f9080ff0a3316b979cbeaa6b7534":raise ValueError("Runtime snapshot changed")
    cmd=[str(JAVA_BIN/"javac"),"-cp",str(jar),"-d",str(classes),str(generated),str(ROOT/"adapters/RealInterchangeExport.java")]
    subprocess.run(cmd,check=True)
    cmd=["taskset","-c","24-31",str(JAVA_BIN/"java"),"-Xmx48g","-XX:ActiveProcessorCount=8","-cp",f"{classes}:{jar}",
         "com.xilinx.rapidwright.rwroute.RealInterchangeExport",str(logical),str(physical),str(output),"--nonTimingDriven","--fixBoundingBox"]
    files=[original,generated,jar,ROOT/"adapters/RealInterchangeExport.java",logical,physical,*logical.parent.glob("LICENSE*")]
    record={"dataset_kind":"real_placed_netlist","dataset_id":dataset,"status":"export_pending","command":cmd,
            "files":{str(p):{"sha256":sha(p),"bytes":p.stat().st_size} for p in files},
            "compatibility_change":"Same RRT2-only rwMaxThreads compatibility replacement as first design; serial RRT1 used"}
    manifest.write_text(json.dumps(record,indent=2)+"\n")
    with (directory/"export.log").open("w") as log:
        process=subprocess.run(cmd,env=dict(os.environ,RAPIDWRIGHT_PATH=str(RUNTIME)),stdout=log,stderr=subprocess.STDOUT)
    record["exit_code"]=process.returncode
    record["status"]="exported" if process.returncode==0 else "failed"
    if output.exists():record.update(output=str(output),output_sha256=sha(output),output_bytes=output.stat().st_size)
    manifest.write_text(json.dumps(record,indent=2)+"\n")
    if process.returncode:raise RuntimeError("Real export failed; inspect export.log")
    print(json.dumps({"status":"exported","dataset":dataset,"bytes":record["output_bytes"],"sha256":record["output_sha256"]}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("dataset");parser.add_argument("logical",type=Path);parser.add_argument("physical",type=Path)
    args=parser.parse_args();export(args.dataset,args.logical.resolve(),args.physical.resolve())
