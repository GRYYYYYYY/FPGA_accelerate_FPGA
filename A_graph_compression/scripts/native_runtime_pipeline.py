#!/usr/bin/env python3
"""Single post-validation owner for the preregistered full native trial matrix."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
from import_vivado import sha256

PREFIX=ROOT/'results/native_runtime_pipeline_20261023_v1'
VALIDATION=ROOT/'data/derived/native_runtime_validation_20261023_v1'
VALIDATION_PID=3563530
OUTPUT=ROOT/'data/derived/native_runtime_statistics_20261023_v1'


def save(path,data):
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)


def main():
    lock=PREFIX.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    path=PREFIX.with_suffix('.json')
    if path.exists() or OUTPUT.exists():raise ValueError('Refusing existing queue or statistics output')
    state={'owner_pid':os.getpid(),'validation_owner_pid':VALIDATION_PID,'status':'running',
           'stage':'wait_validation','statistics_output':str(OUTPUT),
           'matrix':{'conditions':['csr/direct','compact/direct','compact/expanded'],
                     'cache_rows':[0,64,4096],'repeats':7,'seed':20261023,'workers':63}}
    save(path,state)
    try:
        while True:
            process=Path('/proc')/str(VALIDATION_PID)
            try:
                command=(process/'cmdline').read_bytes()
                status=(process/'stat').read_text().split(') ',1)[1].split()[0]
            except FileNotFoundError:break
            if status=='Z':break
            if b'native_runtime_benchmark.py' not in command or b'native_runtime_validation_20261023_v1' not in command:
                raise ValueError('Validation process identity changed')
            time.sleep(10)
        report=json.loads((VALIDATION/'report.json').read_text())
        plan=json.loads((VALIDATION/'plan.json').read_text())
        if report['status']!='all_complete_batches_equivalent' or report['workers']!=3:
            raise ValueError('Complete three-condition validation did not pass')
        if sha256(VALIDATION/'plan.json')!=report['plan_sha256']:raise ValueError('Validation plan changed')
        for name,digest in plan['code_inputs_and_references'].items():
            if sha256(Path(name))!=digest:raise ValueError('Frozen validation evidence changed')
        for name,digest in report['worker_sha256'].items():
            if sha256(VALIDATION/name)!=digest:raise ValueError('Validation worker changed')
            worker=json.loads((VALIDATION/name).read_text())
            if not worker['both_complete_batches_verified']:raise ValueError('Validation batches not verified')
            raw=VALIDATION/name.replace('.json','.raw.json')
            if sha256(raw)!=worker['raw_sha256']:raise ValueError('Validation native output changed')
        conditions={(j['mode'],j['execution'],j['capacity']) for j in plan['jobs']}
        if conditions!={('csr','direct',4096),('compact','direct',4096),('compact','expanded',4096)}:
            raise ValueError('Validation condition domain differs')
        state.update(stage='statistics',validation_report_sha256=sha256(VALIDATION/'report.json'));save(path,state)
        command=[sys.executable,str(ROOT/'scripts/native_runtime_benchmark.py'),'--output',str(OUTPUT),
                 '--capacities','0','64','4096','--repeats','7','--seed','20261023','--cpu',str(plan['cpu'])]
        with PREFIX.with_suffix('.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save(path,state);code=child.wait()
        state.pop('child_pid',None)
        if code:raise RuntimeError('Statistics process failed with exit '+str(code))
        final=json.loads((OUTPUT/'report.json').read_text())
        if final['status']!='all_complete_batches_equivalent' or final['workers']!=63:
            raise ValueError('Incomplete formal statistics report')
        state.update(status='complete',stage='await_independent_statistics_audit',
                     statistics_report_sha256=sha256(OUTPUT/'report.json'));save(path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(path,state);raise


if __name__=='__main__':main()
