"""Fetch the official frozen training archive and extract named benchmark inputs."""
import json
from pathlib import Path
import tarfile
import urllib.request
from prepare_real import ROOT, sha

URL = "https://github.com/Xilinx/fpga24_routing_contest/releases/download/v1.8/benchmarks.tar.gz"
SIZE = 663430592


def fetch(dataset="vtr_mcml"):
    directory = ROOT/"data/raw/fpga24_v1.8"
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory/"benchmarks.tar.gz"
    if not archive.exists():
        partial = directory/"benchmarks.tar.gz.partial"
        if partial.exists(): raise ValueError("Partial download exists; inspect before retrying")
        with urllib.request.urlopen(URL, timeout=60) as response, partial.open("xb") as output:
            headers = dict(response.headers)
            while True:
                block = response.read(4 << 20)
                if not block: break
                output.write(block)
        if partial.stat().st_size != SIZE: raise ValueError("Release asset size mismatch")
        partial.rename(archive)
        (directory/"download_headers.json").write_text(json.dumps(headers,indent=2)+"\n")
    if archive.stat().st_size != SIZE: raise ValueError("Release asset size mismatch")
    target = directory/dataset
    target.mkdir(exist_ok=True)
    records = []
    wanted = {dataset+".netlist", dataset+"_unrouted.phys"}
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            name = Path(member.name).name
            if not member.isfile() or (name not in wanted and not name.startswith("LICENSE")): continue
            output = target/name
            if not output.exists():
                with source.extractfile(member) as stream, output.open("xb") as file:
                    while True:
                        block = stream.read(4 << 20)
                        if not block: break
                        file.write(block)
            if output.stat().st_size != member.size: raise ValueError("Extracted file size mismatch")
            records.append({"member":member.name,"path":str(output),"bytes":member.size,"sha256":sha(output)})
    if not all((target/name).is_file() for name in wanted): raise ValueError("Missing benchmark inputs")
    manifest = {"dataset_id":dataset,"source_url":URL,"source_release":"v1.8","archive_bytes":SIZE,
                "archive_sha256":sha(archive),"checksum_scope":"Locally computed SHA256; upstream release has no published digest",
                "files":records,"status":"ready"}
    (target/"download_provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"status":"ready","dataset":dataset,"directory":str(target)}),flush=True)


if __name__=="__main__":fetch()
