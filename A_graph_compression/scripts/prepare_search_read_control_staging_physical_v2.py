#!/usr/bin/env python3
"""Freeze candidate RTL and identical OOC flow; execution awaits candidate RTL audit."""
import json,shutil
from pathlib import Path
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    proof=ROOT/'results/search_read_control_staging_hls_audit_20261025_v1.json';r=json.loads(proof.read_text());require(r['helper_min2_ii1_achieved'],'Actual staging not verified')
    for p,h in r['files'].items():require(digest(p)==h,'Changed HLS evidence')
    out=ROOT/'data/derived/search_read_control_staging_physical_20261025_v2';out.mkdir(exist_ok=False);mode=out/'csr';source=mode/'source';source.mkdir(parents=True)
    original=BASE/'search_read_control_staging_hls_project_v1/solution/syn/verilog';generated={};names=[]
    for p in sorted(original.iterdir()):
        if p.suffix not in ['.v','.dat']:continue
        require(r['files'].get(str(p))==digest(p),'RTL/ROM not bound by independent HLS audit');q=source/p.name;shutil.copyfile(p,q);require(digest(q)==digest(p),'Copy differs');generated[str(q)]=digest(q);names.append(p.name)
    require('search_kernel_top.v' in names and 'search_kernel_top_valid_decoded_record.v' in names,'Missing real candidate module')
    baseline=ROOT/'data/derived/search_packet_width64_physical_20261025_v1/csr'
    for name in ['run_flow.tcl','clock.xdc']:
        p=baseline/name;q=mode/name;shutil.copyfile(p,q);require(digest(q)==digest(p),'Changed physical flow or constraints');generated[str(q)]=digest(q)
    atomic(out/'plan.json',dict(status='prepared_not_started_candidate_rtl_acceptance_required',inputs={str(proof):digest(proof),str(Path(__file__).resolve()):digest(__file__),str(baseline/'run_flow.tcl'):digest(baseline/'run_flow.tcl'),str(baseline/'clock.xdc'):digest(baseline/'clock.xdc')},generated=generated,source_rtl_and_rom_files=len(names),part='xcu280-fsvh2892-2L-e',clock_ns=5,setup_uncertainty_ns=1.35,max_threads=2,execution_gate=str(ROOT/'results/search_read_control_staging_rtl_audit_20261025_v1.json'),rtl_verified=False,physical_executed=False,limits=['Same complete OOC flow and active XDC; no waiver or relaxed clock','HLS-only candidate currently lacks full RTL acceptance; do not launch physical implementation before that audit','Original canonical DUTs and physical results retained']))
    print('Candidate RTL/ROM frozen:',len(names),'same flow/XDC; not executed, RTL acceptance still required')
if __name__=='__main__':main()
