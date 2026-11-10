#!/usr/bin/env python3
"""Run the whole existing compact router with observation only, then audit."""
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/derived/router_access_profile_build_20261023_v1'
OUT=ROOT/'data/derived/router_access_profile_run_20261023_v1'


def save(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def main():
    require(123 in os.sched_getaffinity(0),'CPU123 unavailable')
    pp=SOURCE/'plan.json';prep=json.loads(pp.read_text())
    require(prep['status']=='compiled_diagnostic_observer_not_yet_full_router_validated','Preparation failed')
    files={**prep['files'],**prep['generated']}
    for p in [pp,Path(__file__).resolve(),ROOT/'scripts/check_router_access_profile.py',
              ROOT/'scripts/check_native_site_runtime.py',ROOT/'scripts/check_vitis_kernel.py',
              ROOT/'tests/test_router_access_profile.py',ROOT/'results/regression_router_access_profile_20261023_v1.log']:
        files[str(p)]=digest(p)
    for path,sha in files.items():require(digest(path)==sha,'Frozen profile dependency changed: '+path)
    OUT.mkdir(parents=True,exist_ok=False)
    plan={'owner_pid':os.getpid(),'files':files,'inputs':prep['inputs'],'reference':prep['reference'],
          'binary':prep['binary'],'cpu':123,'capacity':4096,'batches':2,'limitations':prep['limitations']}
    save(OUT/'plan.json',plan)
    state={'owner_pid':os.getpid(),'status':'running','stage':'full_router'};save(OUT/'state.json',state)
    try:
        inp=plan['inputs'];command=[plan['binary'],inp['image'],inp['fixture'],inp['sites'],
                                   '4096','80','200000','8','direct',str(OUT/'access')]
        start=perf_counter()
        with (OUT/'router.raw.json').open('x') as stream,(OUT/'router.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=log,
                                   preexec_fn=lambda:os.sched_setaffinity(0,{123}))
            save(OUT/'submission.json',{'command':command,'cpu':123,'owner_pid':os.getpid(),'child_pid':child.pid})
            state['child_pid']=child.pid;save(OUT/'state.json',state);code=child.wait()
        receipt={'exit_code':code,'process_wall_ms':1000*(perf_counter()-start),
                 'raw_sha256':digest(OUT/'router.raw.json'),'log_sha256':digest(OUT/'router.log'),
                 'profiles':{str(i):digest(OUT/f'access.batch_{i}.tsv') for i in range(2) if (OUT/f'access.batch_{i}.tsv').exists()}}
        save(OUT/'receipt.json',receipt);require(code==0 and len(receipt['profiles'])==2,'Access router failed/incomplete')
        state.pop('child_pid');state['stage']='independent_full_audit';save(OUT/'state.json',state)
        report=ROOT/'results/router_access_profile_audit_20261023_v1.json'
        with (OUT/'audit.log').open('x') as log:
            child=subprocess.Popen(['taskset','-c','123',sys.executable,str(ROOT/'scripts/check_router_access_profile.py'),
                                     '--bundle',str(OUT),'--output',str(report)],stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save(OUT/'state.json',state);code=child.wait()
        save(OUT/'audit_receipt.json',{'exit_code':code,'log_sha256':digest(OUT/'audit.log'),
             'report':str(report),'report_sha256':digest(report) if report.exists() else None})
        require(code==0,'Access independent audit failed')
        state.pop('child_pid');state.update(status='complete',stage='full_router_and_access_audited',report=str(report));save(OUT/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(OUT/'state.json',state);raise


if __name__=='__main__':main()
