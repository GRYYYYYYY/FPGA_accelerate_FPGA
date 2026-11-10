#!/usr/bin/env python3
"""Bind boundary-case receipts and check the complete literal-result matrix."""
import json
import re
from pathlib import Path
from run_search_kernel_state_boundaries import ROOT,OUT,digest

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text());state=OUT/'state.json';s=json.loads(state.read_text())
    require(s['status']=='complete' and s['completed']==['csr','compact'],'Incomplete boundary execution')
    artifacts={**plan['files'],**plan['copied']}
    for p,h in artifacts.items():require(digest(p)==h,'Changed input '+p)
    statuses=[0,5,5,5,0,1,1,0];results=[]
    require([(j['mode'],j['mode_id']) for j in plan['jobs']]==[('csr',0),('compact',1)],'Wrong mode pair')
    for job in plan['jobs']:
        mode=job['mode'];mid=job['mode_id']
        for phase in ['compile','run']:
            prefix=OUT/(mode+'.'+phase)
            log=Path(str(prefix)+'.log');rp=Path(str(prefix)+'.receipt.json');sp=Path(str(prefix)+'.submission.json')
            receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text())
            require(receipt['exit_code']==0 and receipt['command']==submission['command']==job[phase],'Failed/different command')
            require(receipt['log_sha256']==digest(log) and receipt['binary_sha256']==digest(OUT/mode),'Changed output or binary')
            require(submission['plan_sha256']==digest(pp),'Changed plan')
            for p in [log,rp,sp,OUT/mode]:artifacts[str(p)]=digest(p)
        text=(OUT/(mode+'.run.log')).read_text()
        require('Sanitizer' not in text and 'runtime error:' not in text,'Sanitizer failure')
        rows=[tuple(map(int,r)) for r in re.findall(r'^STATE_BOUNDARY_PASS mode=(\d+) transaction=(\d+) status=(\d+) full_capacity=32,16,8 literal_output=1 guards=1$',text,re.M)]
        require(rows==[(mid,i,status) for i,status in enumerate(statuses)],'Missing/reordered boundary cases')
        observed=[tuple(map(int,r)) for r in re.findall(r'^STATE_BOUNDARY_OBSERVED mode=(\d+) transaction=(\d+) status=(\d+) cost=(\d+) expanded=(\d+) path=(\d+)$',text,re.M)]
        require(observed==[(mid,i,status,2 if status==0 else 0,2,2 if status==0 else 0) for i,status in enumerate(statuses)],'Wrong literal result')
        require(text.count('STATE_BOUNDARY_ALL_PASS transactions=8 production_top=1 full_workspace_limits=1')==1,'Missing terminal marker')
        results.append({'mode':mode,'transactions':8,'statuses':statuses,'full_state_capacity':[32,16,8],'full_workspace':True})
    for p in [pp,state,Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    report={'status':'production_search_top_state_capacity_boundaries_cpu_verified','results':results,'cases':plan['cases'],'artifacts':artifacts,'limitations':plan['limitations']}
    output=ROOT/'results/search_kernel_state_boundaries_20261024_v1.json'
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'])

if __name__=='__main__':main()
