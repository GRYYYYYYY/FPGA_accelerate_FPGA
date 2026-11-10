#!/usr/bin/env python3
"""Require all eight actual RTL transactions and independent literal C checks."""
import json
from pathlib import Path
import re
from search_kernel_boundary_rtl_pipeline import ROOT,OUT,PROJECT,SETUP,PRIOR,digest
from search_boundary_rtl_contract import require,golden,transactions

def main():
    pp=OUT/'execution_plan.json';plan=json.loads(pp.read_text());state_path=OUT/'state.json';state=json.loads(state_path.read_text())
    require(state['status']=='complete' and sorted(state['completed'])==['compact','csr'],'Incomplete boundary RTL mode pair')
    setup=json.loads(SETUP.read_text());prior=json.loads(PRIOR.read_text())
    require(digest(SETUP)==plan['prepared_report_sha256'] and digest(PRIOR)==plan['prior_replay_sha256'],'Different predecessor reports')
    require(setup['status']=='state_capacity_boundary_hls_setup_verified_rtl_pending' and prior['status']=='unchanged_search_kernel_rtl_replay_and_original_postcheck_verified','Predecessor not verified')
    artifacts={**plan['files'],**setup['artifacts'],**setup['generated']}
    for p,h in artifacts.items():require(digest(p)==h,'Changed boundary input '+p)
    require([(j['mode'],j['cpu']) for j in plan['jobs']]==[('csr',120),('compact',123)],'Wrong mode pair')
    results=[]
    for job in plan['jobs']:
        mode=job['mode'];mid=0 if mode=='csr' else 1
        for phase in ['elaborate','rtl','postcheck']:
            log=OUT/(mode+'.'+phase+'.log');rp=OUT/(mode+'.'+phase+'.receipt.json');sp=OUT/(mode+'.'+phase+'.submission.json')
            r=json.loads(rp.read_text());s=json.loads(sp.read_text());text=log.read_text(errors='replace')
            require(r['exit_code']==0 and r['command']==s['command']==job[phase],'Failed/different phase')
            require(r['log_sha256']==digest(log) and s['plan_sha256']==digest(pp),'Changed phase evidence')
            require(job[phase][:6]==['prlimit','--stack=67108864:67108864','--','taskset','-c',str(job['cpu'])],'Wrong execution environment')
            require(s['cwd']==(job['postcheck_directory'] if phase=='postcheck' else job['directory']),'Different phase working directory')
            require('ERROR:' not in text and 'FATAL_ERROR' not in text and 'runtime error:' not in text,'Phase log contains errors')
            if phase=='rtl':require('BOUNDARY_BOUNDED_RUN_RETURNED' in text and re.search(r'RTL Simulation :\s*8 / 8',text),'Incomplete RTL progress')
            if phase=='postcheck':golden(text,mid)
            for p in [log,rp,sp]:artifacts[str(p)]=digest(p)
        perf=Path(job['directory'])/'search_kernel_top.performance.result.transaction.xml';cycles=transactions(perf.read_text())
        outputs=sorted((PROJECT/mode/'solution/sim/tv/rtldatafile').glob('rtl.*.autotvout_*.dat'));require(outputs,'Missing RTL output vectors')
        for p in [perf,*outputs]:artifacts[str(p)]=digest(p)
        results.append({'mode':mode,'cycles':cycles,'transactions':8,'state_capacity':[32,16,8],'literal_postcheck':'passed','production_synthesis':'unchanged'})
    for p in [pp,state_path,Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    report={'status':'production_search_top_full_state_capacity_boundaries_rtl_verified','results':results,'artifacts':artifacts,
        'limitations':['Synthetic state-capacity and conflict boundary coverage; not full real-graph traffic or peak heap/label occupancy in RTL.','No board memory, power, post-route timing or full hardware negotiation claim.']}
    output=ROOT/'results/search_kernel_boundary_rtl_audit_20261024_v1.json'
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'results':results}))

if __name__=='__main__':main()
