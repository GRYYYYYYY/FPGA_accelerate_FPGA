"""Build the supplied exporter against the public matching RapidWright runtime."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
USER_ROOT = ROOT.parents[2]
JAVA_BIN = USER_ROOT / "Xilinx/Vivado/2022.2/tps/lnx64/jre11.0.11_9/bin"
UPSTREAM = ROOT.parent / "_shared/assets/gpu_router_original/rewrite"
RUNTIME = ROOT / "data/raw/rapidwright_2025.2.1"
BENCHMARK = USER_ROOT / "FPGA_Acc/projects/persistroute/third_party/fpga24/logicnets_jscl"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def prepare():
    output = ROOT / "data/derived/logicnets_jscl.rrt"
    manifest = ROOT / "data/derived/logicnets_jscl_provenance.json"
    if output.exists():
        if not manifest.exists(): raise ValueError("Existing export has no provenance; refusing overwrite")
        record = json.loads(manifest.read_text())
        if record.get("status") != "exported" or sha(output) != record.get("output_sha256"):
            raise ValueError("Existing export differs from provenance; refusing overwrite")
        for path, info in record["files"].items():
            if sha(path) != info["sha256"]: raise ValueError(f"Export input changed: {path}")
        print(json.dumps({"status": "reused_verified_export", "manifest": str(manifest)}))
        return 0
    jar = RUNTIME / "rapidwright.jar"
    if hashlib.md5(jar.read_bytes()).hexdigest() != "77fbcc7a6de286d785611e77b5a6efe8":
        raise ValueError("Public runtime release checksum mismatch")
    directory = ROOT / "build/real_trace"
    classes = directory / "java"
    classes.mkdir(parents=True, exist_ok=True)
    source = UPSTREAM / "RapidWright/src/com/xilinx/rapidwright/rwroute/RWRouteCppProblemExport.java"
    text = source.read_text()
    # Only used by RRT2's parallel serializer. This experiment exports serial RRT1.
    if text.count("RWRoute.rwMaxThreads()") != 2:
        raise ValueError("Exporter compatibility anchors changed")
    text = text.replace("RWRoute.rwMaxThreads()", "48")
    generated = directory / "RWRouteCppProblemExport.java"
    generated.write_text(text)
    command = [str(JAVA_BIN / "javac"), "-cp", str(jar), "-d", str(classes),
               str(generated), str(ROOT / "adapters/RealInterchangeExport.java")]
    subprocess.run(command, check=True)
    logical = BENCHMARK / "logicnets_jscl.netlist"
    physical = BENCHMARK / "logicnets_jscl_unrouted.phys"
    output = ROOT / "data/derived/logicnets_jscl.rrt"
    command = [str(JAVA_BIN / "java"), "-Xmx48g", "-XX:ActiveProcessorCount=8",
               "-cp", f"{classes}:{jar}", "com.xilinx.rapidwright.rwroute.RealInterchangeExport",
               str(logical), str(physical), str(output), "--nonTimingDriven", "--fixBoundingBox"]
    files = [source, generated, ROOT / "adapters/RealInterchangeExport.java", jar, logical, physical,
             BENCHMARK / "LICENSE-BENCHMARKS.txt"]
    record = {"dataset_kind": "real_placed_netlist", "dataset_id": "logicnets_jscl_fpga24",
              "runtime_release": "https://github.com/Xilinx/RapidWright/releases/tag/v2025.2.1-beta",
              "runtime_source_commit": "2fc8b6aec859c20c04218573f9dda09db0a72e3f",
              "files": {str(p): {"sha256": sha(p), "bytes": p.stat().st_size} for p in files},
              "export_command": command, "compatibility_change": "two RRT2-only rwMaxThreads calls replaced by 48; RRT1 unchanged",
              "status": "export_pending", "output": str(output)}
    manifest = ROOT / "data/derived/logicnets_jscl_provenance.json"
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    env = dict(os.environ, RAPIDWRIGHT_PATH=str(RUNTIME))
    with (directory / "export.log").open("w") as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    record["exit_code"] = result.returncode
    record["status"] = "exported" if result.returncode == 0 and output.exists() else "export_failed"
    if output.exists():
        record["output_sha256"] = sha(output)
        record["output_bytes"] = output.stat().st_size
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "manifest": str(manifest)}))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(prepare())
