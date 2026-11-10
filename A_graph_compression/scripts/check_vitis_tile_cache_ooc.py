#!/usr/bin/env python3
"""Audit actual routed timing/resources from copied Vitis HLS projects."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from check_netlist_quality import timing_status,route_status,drc_status
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_tile_cache_ooc_20261023_v1'

from check_vitis_ooc import quality_gates

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    plan_path=OUT/'plan.json';state_path=OUT/'pipeline.json';plan=json.loads(plan_path.read_text());state=json.loads(state_path.read_text())
    require(state['status']=='complete' and state['completed_modes']==['compact'],'OOC owner not successfully complete')
    for name,h in plan['files'].items():require(digest(name)==h,'Original frozen dependency changed: '+name)
    prior=ROOT/'results/vitis_tile_cache_cosim_audit_20261023_v1.json';baseline=json.loads(prior.read_text())
    files={str(p):digest(p) for p in [plan_path,state_path,prior,Path(__file__).resolve(),ROOT/'scripts/check_netlist_quality.py']};modes={}
    for mode in ['compact']:
        mode_state=OUT/(mode+'.state.json');ms=json.loads(mode_state.read_text());require(ms['status']=='complete','Incomplete mode')
        work=OUT/mode;receipt_path=work/'receipt.json';receipt=json.loads(receipt_path.read_text());log=work/'impl.log'
        require(receipt['exit_code']==0 and receipt['completion_marker'] and digest(log)==receipt['log_sha256'],'Implementation receipt mismatch')
        require('VITIS_GRAPH_OOC_IMPL_COMPLETE' in log.read_text() and 'ERROR:' not in log.read_text(),'Implementation log failed')
        project=ROOT/'build'/f'vitis_graph_{mode}_tile_cache_ooc_20261023_v1';solution=project/'solution';original=ROOT/'build'/f'vitis_graph_{mode}_tile_cache_cosim_20261023_v1/solution'
        original_rtl={p.name:p for p in (original/'syn/verilog').glob('*.v')};copied_rtl={p.name:p for p in (solution/'syn/verilog').glob('*.v')}
        require(original_rtl and set(original_rtl)==set(copied_rtl),'Copied synthesized RTL set differs')
        for name,path in original_rtl.items():require(digest(path)==digest(copied_rtl[name]),'Copied RTL differs from audited tile-cache candidate')
        runs=solution/'impl/verilog/project.runs/impl_1'
        timing=runs/'bd_0_wrapper_timing_summary_routed.rpt';drc=runs/'bd_0_wrapper_drc_routed.rpt';dcp=runs/'bd_0_wrapper_routed.dcp'
        route=solution/'impl/verilog/report/graph_accel_status_routed.rpt';export=solution/'impl/report/verilog/graph_accel_export.rpt'
        exported=export.read_text();require('Post-Implementation' in exported,'Missing post-route resource summary')
        resources={k:int(v) for k,v in re.findall(r'^(LUT|FF|DSP|BRAM|URAM|SRL|CLB):\s+(\d+)',exported,re.M)}
        require({'LUT','FF','DSP','BRAM'}<=resources.keys() and resources['LUT']>0 and resources['FF']>0,'Incomplete resource report')
        clock=re.search(r'^ap_clk\s+\{[^}]+\}\s+([0-9.]+)\s+([0-9.]+)',timing.read_text(),re.M)
        require(clock and float(clock[1])==5.0 and float(clock[2])==200.0,'Actual routed clock is not5ns/200MHz')
        t,r,d=timing_status(timing),route_status(route),drc_status(drc)
        t['routed_clock_period_ns']=float(clock[1])
        modes[mode]={'timing':t,'route_status':r,'drc':d,'post_route_resources':resources,'quality_gates':quality_gates(t,r,d),
                     'matching_rtl_batches':baseline['cases'],'scope':'Constrained internal paths only; inspect no_input_delay/no_output_delay for external coverage.'}
        for p in [mode_state,receipt_path,log,work/'copied_project.json',timing,drc,dcp,route,export]+list(copied_rtl.values()):files[str(p)]=digest(p)
    passed=all(all(m['quality_gates'].values()) for m in modes.values())
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'copied_ooc_all_internal_gates_pass' if passed else 'copied_ooc_has_failed_quality_gates',
            'modes':modes,'files':files,'all_quality_gates_pass':passed,
            'limitations':['Internal OOC timing/resources, not a platform-linked xclbin or real DDR/HBM/power measurement.',
                'Unconstrained external AXI/IO paths remain outside internal closure.',
                'Original RTL co-simulation covers sampled batches; complete graph output equivalence is C simulation.']}
    write_new(a.output,report);print(json.dumps({'status':report['status'],'output':str(a.output),'modes':modes},indent=2))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
