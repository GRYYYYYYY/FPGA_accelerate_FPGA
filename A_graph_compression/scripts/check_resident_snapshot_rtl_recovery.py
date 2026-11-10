#!/usr/bin/env python3
"""Audit exact original snapshot setup plus independent 30-transaction postcheck."""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from resident_snapshot_rtl_contract import golden,transactions

def audit(out,output):
    require(not output.exists(),'Existing audit')
    plan=json.loads((out/'plan.json').read_text());state=json.loads((out/'state.json').read_text())
    require(state['status']=='running' and state['stage']=='independent_audit' or state['status']=='complete' and state['stage']=='independently_audited','Incomplete recovery')
    require(plan['transactions']==30,'Different contract')
    files={**plan['files'],**plan['copied']}
    for p,h in files.items():require(digest(p)==h,'Changed original/recovery input '+p)
    for phase,job in plan['commands'].items():
        log=out/(phase+'.log');receipt=out/(phase+'.receipt.json');submission=out/(phase+'.submission.json')
        r=json.loads(receipt.read_text());s=json.loads(submission.read_text());text=log.read_text(errors='replace')
        require(r['exit_code']==0 and r['command']==s['command']==job['command'] and s['cwd']==job['cwd'] and s['plan_sha256']==digest(out/'plan.json') and r['log_sha256']==digest(log),'Failed/different '+phase)
        require(not any(t in text for t in ['ERROR:','FATAL_ERROR','runtime error:']),'Error in '+phase)
        if phase=='elaborate':
            old=plan['original_elaborate_command'];i=old.index(next(x for x in old if x.endswith('/bin/xelab')))
            require(job['command']==old[:i]+['/usr/bin/time','-v']+old[i:]+['-mt','off','--O0','--stats'],'Unreviewed elaborate change')
            require('Maximum resident set size (kbytes)' in text,'Missing memory measurement')
        if phase=='rtl':require('RESIDENT_SNAPSHOT_BOUNDED_RUN_RETURNED' in text and re.search(r'RTL Simulation :\s*30 / 30',text),'Incomplete simulation')
        if phase=='postcheck':golden(text)
        for p in [log,receipt,submission]:files[str(p)]=digest(p)
    directory=Path(plan['project'])/'solution/sim';perf=directory/'verilog/search_resident_snapshot_top.performance.result.transaction.xml';cycles=transactions(perf.read_text())
    outputs=list((directory/'tv/rtldatafile').glob('rtl.*.autotvout_*.dat'));require(outputs,'Missing RTL outputs')
    for p in [out/'plan.json',out/'environment_before.json',perf,*outputs,Path(__file__).resolve()]:files[str(p)]=digest(p)
    r=dict(status='production_resident_snapshot_recovery_full_depth_30_transactions_rtl_verified',files=files,cycles=cycles,transactions=30,root_cause=plan['root_cause'],changes=plan['changes'],limits=['Same original full-depth RTL and input vectors; no smaller substitute','Optimization/thread changes are simulator-only; no speedup claim','Synthetic HLS AXI model only; no full real workload or board timing, bandwidth or power proof'])
    with output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(r['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
