#!/usr/bin/env python3
"""Verify narrowed CSR RTL and original C postcheck; compare actual replay cycles."""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from search_packet_width_rtl import golden
ROOT=Path(__file__).resolve().parents[1]
def cycles(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==[0,1] and all(c>0 for _,c in rows) and len(re.findall(r'^transaction\b',text,re.M))==2,'Incomplete two-transaction timing')
    return [c for _,c in rows]
def audit(bundle,output):
    require(not output.exists(),'Existing RTL comparison')
    state=json.loads((bundle/'state.json').read_text());plan=json.loads((bundle/'plan.json').read_text());execution=json.loads((bundle/'execution_plan.json').read_text())
    require(state['status']=='complete' and state['stage']=='rtl_and_original_postcheck_complete_pending_independent_audit' and plan['transactions']==2 and plan['stack_bytes']==67108864 and plan['simulation_bound_ns']==10000000000,'Incomplete/different RTL scope')
    files={**plan['files'],**execution['files']}
    for p,h in files.items():require(digest(p)==h,'Changed execution input '+p)
    solution=Path(plan['project'])/'solution';directory=solution/'sim/verilog';pc=solution/'sim/wrapc_pc'
    first=['prlimit','--stack=67108864:67108864','--','taskset','-c','122']
    commands=execution['commands']
    expected={'setup':(first+['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(bundle/'setup.tcl')],bundle),
              'elaborate':(first+commands[0],directory),'rtl':(first+commands[1][:-1]+[str(bundle/'bounded.tcl')],directory),'postcheck':(first+[str(pc/'cosim.pc.exe')],pc)}
    for phase,(cmd,cwd) in expected.items():
        log=bundle/(phase+'.log');receipt=bundle/(phase+'.receipt.json');r=json.loads(receipt.read_text());text=log.read_text(errors='replace')
        require(r['exit_code']==0 and r['command']==cmd and r['cwd']==str(cwd) and r['plan_sha256']==digest(bundle/'plan.json') and r['log_sha256']==digest(log),'Failed/different phase '+phase)
        require(not any(t in text for t in ['ERROR:','FATAL_ERROR','runtime error:']),'RTL error '+phase)
        if phase=='setup':
            before,after=text.split('Running: cosim_design',1);golden(before);golden(after);require('WIDTH64_RTL_SETUP_COMPLETE' in text,'Missing setup marker')
        if phase=='postcheck':golden(text)
        if phase=='rtl':require('WIDTH64_RTL_BOUNDED_RETURNED' in text and re.search(r'RTL Simulation :\s*2 / 2',text),'RTL not finished')
        for p in [log,receipt]:files[str(p)]=digest(p)
    require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 2;', (directory/'search_kernel_top.autotb.v').read_text()),'Wrong RTL transaction number')
    for p in (solution/'syn/verilog').glob('*.v'):require(digest(p)==digest(directory/p.name),'Wrong simulated RTL')
    perf=directory/'search_kernel_top.performance.result.transaction.xml';actual=cycles(perf.read_text())
    require(state['cycles']==[[i,c] for i,c in enumerate(actual)],'Different owner timing observation')
    reference=ROOT/'results/search_kernel_xsim_replay_audit_20261024_v1.json';old=json.loads(reference.read_text());require(old['status']=='unchanged_search_kernel_rtl_replay_and_original_postcheck_verified','Missing baseline RTL proof')
    baseline=[r['cycles'] for r in old['results'] if r['mode']=='csr'];require(len(baseline)==1,'Ambiguous original mode')
    performance=[Path(p) for p in old['artifacts'] if '/csr/' in p and p.endswith('performance.result.transaction.xml')];require(len(performance)==1,'Missing baseline actual timing')
    original=performance[0];require(digest(original)==old['artifacts'][str(original)] and cycles(original.read_text())==baseline[0],'Changed baseline timing')
    outputs=list((solution/'sim/tv/rtldatafile').glob('rtl.*.autotvout_*.dat'));require(outputs,'Missing actual RTL output data')
    for p in [bundle/'plan.json',bundle/'execution_plan.json',bundle/'state.json',perf,reference,original,Path(__file__).resolve(),*outputs]:files[str(p)]=digest(p)
    report=dict(status='packet_width64_csr_two_transaction_rtl_and_original_postcheck_verified',files=files,cycles=actual,baseline_cycles=baseline[0],cycle_ratio=[a/b for a,b in zip(actual,baseline[0])],rtl_verified=True,physical_timing_verified=False,board_verified=False,limitations=['Two synthetic transactions at full declared capacities; no full real workload or state-capacity-boundary RTL proof for this version.','Cycle ratio uses HLS AXI simulation models; it is not actual HBM bandwidth, wall-clock speedup or board throughput.','Physical timing, congestion, full integration and platform/device proof remain required.'])
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],actual,baseline[0])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
