#!/usr/bin/env python3
"""Gate full site statistics on independent complete first/resident validation."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from native_site_runtime_benchmark import sha256
ROOT=Path(__file__).resolve().parents[1]
PREFIX=ROOT/'results/native_site_runtime_pipeline_20261023_v1'
VALIDATION=ROOT/'data/derived/native_site_runtime_validation_20261023_v1'
STATISTICS=ROOT/'data/derived/native_site_runtime_statistics_20261023_v1'


def identity(pid):
    try:
        words=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        return None if words[0]=='Z' else words[19]
    except FileNotFoundError:return None


def main():
    lock=PREFIX.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state_path=PREFIX.with_suffix('.json')
    if state_path.exists() or STATISTICS.exists():raise ValueError('Existing statistics owner/output')
    plan_path=VALIDATION/'plan.json';plan=json.loads(plan_path.read_text());owner=plan['owner_pid'];start=identity(owner)
    if start and b'native_site_runtime_benchmark.py' not in Path(f'/proc/{owner}/cmdline').read_bytes():
        raise ValueError('Unexpected validation process')
    checker=ROOT/'scripts/check_native_site_runtime.py';driver=ROOT/'scripts/native_site_runtime_benchmark.py'
    frozen={str(p):sha256(p) for p in (Path(__file__),checker,driver,plan_path,
        ROOT/'results/native_site_runtime_protocol_20261023_v1.json')}
    state={'owner_pid':os.getpid(),'validation_owner_pid':owner,'validation_start_ticks':start,
           'status':'running','stage':'wait_validation','files':frozen,'statistics_output':str(STATISTICS),
           'matrix':{'capacities':[0,64,4096],'repeats':7,'seed':20261023,'workers':63,'cpu':plan['cpu']}}
    def save(**changes):
        state.update(changes);tmp=state_path.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(state_path)
    def check_frozen():
        for path,value in frozen.items():
            if sha256(path)!=value:raise ValueError('Frozen pipeline dependency changed: '+path)
    def run(stage,command,log):
        check_frozen()
        with log.open('x') as stream:
            child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT)
            save(stage=stage,child_pid=child.pid,command=command)
            code=child.wait()
        state.pop('child_pid',None)
        if code:raise RuntimeError(stage+' failed with exit '+str(code))
    save()
    try:
        while start is not None and identity(owner)==start:time.sleep(15)
        # Full independent raw re-read is mandatory before the statistics launch.
        validation_audit=ROOT/'results/native_site_runtime_validation_audit_20261023_v1.json'
        run('independent_validation_audit',[sys.executable,'-u',str(checker),str(VALIDATION),
            '--capacities','4096','--repeats','1','--output',str(validation_audit)],
            PREFIX.with_suffix('.validation_audit.log'))
        verified=json.loads(validation_audit.read_text())
        if verified['status']!='complete_site_runtime_matrix_independently_audited' or verified['completed_workers']!=3:
            raise ValueError('Validation scope incomplete')
        save(validation_audit_sha256=sha256(validation_audit))
        run('statistics',[sys.executable,'-u',str(driver),'--output',str(STATISTICS),
            '--capacities','0','64','4096','--repeats','7','--seed','20261023','--cpu',str(plan['cpu'])],
            PREFIX.with_suffix('.statistics.log'))
        final_audit=ROOT/'results/native_site_runtime_statistics_audit_20261023_v1.json'
        run('independent_statistics_audit',[sys.executable,'-u',str(checker),str(STATISTICS),'--output',str(final_audit)],
            PREFIX.with_suffix('.statistics_audit.log'))
        verified=json.loads(final_audit.read_text())
        if verified['status']!='complete_site_runtime_matrix_independently_audited' or verified['completed_workers']!=63:
            raise ValueError('Formal statistics scope incomplete')
        save(status='complete',stage='complete',statistics_audit_sha256=sha256(final_audit))
    except BaseException as error:
        save(status='failed',error=str(error));raise


if __name__=='__main__':main()
