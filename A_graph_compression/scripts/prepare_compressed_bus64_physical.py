#!/usr/bin/env python3
"""Freeze full integrated bus64 RTL for OOC characterization, not functional signoff."""
import json,shutil
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    cg=Path('/sys/fs/cgroup');limit=int((cg/'memory.max').read_text());current=int((cg/'memory.current').read_text());require(limit-current>=64*1024**3,'Insufficient cgroup margin for modest two-thread physical characterization')
    gate=ROOT/'results/compressed_batch_bus64_synthesis_review_20261025_v1.json';r=json.loads(gate.read_text());require(r['status']=='compressed_batch_trace_bus64_integrated_control_csim_synthesis_verified_rtl_pending','Missing synthesis gate')
    for p,h in r['files'].items():require(digest(p)==h,'Changed synthesis input '+p)
    out=ROOT/'data/derived/compressed_batch_bus64_physical_20261025_v1/csr';out.mkdir(parents=True,exist_ok=False);source=out/'source';source.mkdir()
    original=BASE/'compressed_batch_bus64_hls_project/solution/syn/verilog';files=sorted(p for p in original.iterdir() if p.suffix in ['.v','.dat']);require(files,'No generated RTL')
    generated={}
    for p in files:
        h=digest(p);require(r['files'].get(str(p))==h,'RTL not bound by independent synthesis review')
        q=source/p.name;shutil.copyfile(p,q);require(digest(q)==h,'Copy differs');generated[str(q)]=h
    baseline=ROOT/'data/derived/search_kernel_physical_20261024_v1/csr'
    clock=out/'clock.xdc';shutil.copyfile(baseline/'clock.xdc',clock)
    flow=out/'run_flow.tcl';old=(baseline/'run_flow.tcl').read_text();flow.write_text(old.replace('search_kernel_top','search_batch_trace_top_v2'))
    require(flow.read_text().replace('search_batch_trace_top_v2','search_kernel_top')==old,'Physical algorithm or constraints changed')
    for p in [clock,flow]:generated[str(p)]=digest(p)
    plan=dict(status='integrated_bus64_csr_frozen_for_ooc_physical_characterization_functional_rtl_pending',inputs={str(gate):digest(gate),str(baseline/'clock.xdc'):digest(baseline/'clock.xdc'),str(baseline/'run_flow.tcl'):digest(baseline/'run_flow.tcl'),str(Path(__file__).resolve()):digest(__file__)},generated=generated,source_rtl_files=len(files),top='search_batch_trace_top_v2',part='xcu280-fsvh2892-2L-e',clock_ns=5,setup_uncertainty_ns=1.35,max_threads=2,admission_cgroup=dict(limit_bytes=limit,current_bytes=current,required_headroom_bytes=64*1024**3),limits=['Independent OOC characterization only, full integrated functional RTL pending','No platform shell or complete external AXI timing, no board or bandwidth claim','Source and constraints frozen; only top identifier differs from reused physical flow; no waivers'])
    (out.parent/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(str(out))
if __name__=='__main__':main()
