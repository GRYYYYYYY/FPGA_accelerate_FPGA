#!/usr/bin/env python3
"""Run isolated full workload for each representation/execution, then audit."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import subprocess
import time
from prepare_controller_router import ROOT,OUT,digest,PRIOR,PRIOR_STATUS

def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    prior=PRIOR
    if not prior.exists() or json.loads(prior.read_text()).get('status')!=PRIOR_STATUS:raise RuntimeError('Prior label-record full-workload audit must pass before launch')
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():
        if digest(p)!=h:raise ValueError('Changed input '+p)
    state={'owner_pid':os.getpid(),'status':'running','stage':'four_full_workloads','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    if (OUT/'state.json').exists():raise ValueError('Existing owner state; do not relaunch')
    save(OUT/'prior_audit_binding.json',{'path':str(PRIOR),'sha256':digest(PRIOR),'status':PRIOR_STATUS})
    update()
    def run(i,job):
        inp=plan['inputs'][job['mode']];prefix=OUT/f'worker_{i:03d}'
        command=['taskset','-c',str(job['cpu']),plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution']]
        submission={'command':command,'condition':job,'owner_pid':os.getpid(),'plan_sha256':digest(pp)}
        with prefix.with_suffix('.raw.json').open('x') as raw,prefix.with_suffix('.log').open('x') as log:
            start=time.monotonic();child=subprocess.Popen(command,stdout=raw,stderr=log)
            submission['child_pid']=child.pid;save(prefix.with_suffix('.submission.json'),submission)
            code=child.wait();wall=1000*(time.monotonic()-start)
        receipt={'exit_code':code,'condition':job,'command':command,'process_wall_ms':wall,
                 'raw_sha256':digest(prefix.with_suffix('.raw.json')),'log_sha256':digest(prefix.with_suffix('.log'))}
        save(prefix.with_suffix('.receipt.json'),receipt)
        if code:raise RuntimeError('Worker failed '+str(i))
        return i
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for f in as_completed([pool.submit(run,i,j) for i,j in enumerate(plan['jobs'])]):
                state['completed'].append(f.result());update()
        state['stage']='independent_full_audit';update()
        command=['taskset','-c','122','python3',str(ROOT/'scripts/check_controller_router.py')]
        with (OUT/'audit.log').open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        save(OUT/'audit_receipt.json',{'exit_code':r.returncode,'command':command,'log_sha256':digest(OUT/'audit.log')})
        if r.returncode:raise RuntimeError('Independent audit failed')
        state.update(status='complete',stage='independently_audited');update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
