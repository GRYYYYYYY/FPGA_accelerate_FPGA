#!/usr/bin/env python3
"""Freeze validated width64 CSR RTL for same-constraint OOC comparison."""
import json,shutil
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
def main():
    gate=ROOT/'results/search_packet_width64_rtl_audit_20261025_v1.json';r=json.loads(gate.read_text())
    assert r['rtl_verified'] and r['cycles']==[2132461,12404]
    for p,h in r['files'].items():assert digest(p)==h,p
    out=ROOT/'data/derived/search_packet_width64_physical_20261025_v1/csr';out.mkdir(parents=True,exist_ok=False)
    source=out/'source';source.mkdir()
    original=ROOT/'build/search_packet_width64_20261024_v1/solution/syn/verilog'
    files=sorted(p for p in original.iterdir() if p.suffix in ['.v','.dat']);assert files
    generated={}
    for p in files:
        assert r['files'].get(str(p))==digest(p),p
        q=source/p.name;shutil.copyfile(p,q);assert digest(q)==digest(p);generated[str(q)]=digest(q)
    baseline=ROOT/'data/derived/search_kernel_physical_20261024_v1/csr'
    for name in ['run_flow.tcl','clock.xdc']:
        p=baseline/name;q=out/name;shutil.copyfile(p,q);assert digest(q)==digest(p);generated[str(q)]=digest(q)
    report=dict(status='validated_width64_csr_rtl_frozen_for_same_constraints_physical_run',inputs={str(gate):digest(gate),str(Path(__file__).resolve()):digest(__file__)},generated=generated,source_rtl_files=len(files),part='xcu280-fsvh2892-2L-e',clock_ns=5,setup_uncertainty_ns=1.35,max_threads=2,baseline_flow_sha256=digest(baseline/'run_flow.tcl'),baseline_xdc_sha256=digest(baseline/'clock.xdc'),limits=['OOC full device only, no platform shell; external IO paths remain unconstrained and reported','No actual mapping or timing result yet','Unchanged original baseline flow/XDC, no waivers'])
    (out.parent/'plan.json').write_text(json.dumps(report,indent=2)+'\n');print(str(out))
if __name__=='__main__':main()
