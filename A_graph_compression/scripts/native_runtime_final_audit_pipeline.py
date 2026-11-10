#!/usr/bin/env python3
"""One audit successor for the already-running canonical-only63-trial owner."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'results/native_runtime_pipeline_20261023_v1.json'
BUNDLE=ROOT/'data/derived/native_runtime_statistics_20261023_v1'
OUT=ROOT/'data/derived/native_runtime_final_audit_20261023_v1'
REPORT=ROOT/'results/native_runtime_statistics_audit_20261023_v1.json'


def save(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def identity(pid):
    proc=Path('/proc')/str(pid)
    try:
        stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
        return {'start_ticks':stat[19],'state':stat[0],'command':(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()}
    except FileNotFoundError:return None


def main():
    lock=(ROOT/'results/native_runtime_final_audit_20261023_v1.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    upstream=json.loads(UPSTREAM.read_text());pid=upstream['owner_pid'];origin=identity(pid)
    require(upstream['status'] in ['running','complete'],'Original statistics failed')
    if upstream['status']=='running':
        require(origin is not None and origin['state']!='Z' and 'scripts/native_runtime_pipeline.py' in origin['command'],
                'Original statistics owner is not live')
    require(not REPORT.exists(),'Refusing existing independent audit')
    pp=BUNDLE/'plan.json';plan=json.loads(pp.read_text());require(len(plan['jobs'])==63 and plan['cpu']==0,'Wrong trial matrix/CPU')
    files={str(p):digest(p) for p in [pp,Path(__file__).resolve(),ROOT/'scripts/native_runtime_pipeline.py',
        ROOT/'scripts/check_native_runtime_bound.py',ROOT/'scripts/check_native_runtime.py',
        ROOT/'scripts/check_vitis_kernel.py',ROOT/'tests/test_native_runtime_bound.py',
        ROOT/'results/regression_native_runtime_bound_20261023_v1.log']}
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/'plan.json',{'files':files,'upstream_owner_pid':pid,'upstream_identity':origin,'bundle':str(BUNDLE),
        'scope':'Audit existing canonical-only statistics after original owner completes. No rerun, no site-model claims.'})
    state={'owner_pid':os.getpid(),'upstream_owner_pid':pid,'status':'running','stage':'wait_original_statistics'}
    save(OUT/'state.json',state)
    try:
        while True:
            current=json.loads(UPSTREAM.read_text())
            require(current['owner_pid']==pid,'Original owner changed')
            if current['status']=='complete':break
            require(current['status']=='running','Original statistics failed')
            now=identity(pid)
            if now is None or now['state']=='Z':
                # Completion may have been atomically published between the reads.
                current=json.loads(UPSTREAM.read_text())
                require(current['owner_pid']==pid and current['status']=='complete','Owner ended without successful completion')
                break
            require(now['start_ticks']==origin['start_ticks'] and now['command']==origin['command'],'Owner PID reused/changed')
            time.sleep(30)
        require(current['stage']=='await_independent_statistics_audit','Unexpected original terminal stage')
        require(digest(BUNDLE/'report.json')==current['statistics_report_sha256'],'Original final report changed')
        for path,sha in files.items():require(digest(path)==sha,'Frozen audit input changed: '+path)
        command=['taskset','-c','0',sys.executable,str(ROOT/'scripts/check_native_runtime_bound.py'),str(BUNDLE),
                 '--capacities','0','64','4096','--repeats','7','--output',str(REPORT)]
        with (OUT/'audit.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage='independent_full_audit',child_pid=child.pid,command=command);save(OUT/'state.json',state)
            code=child.wait()
        save(OUT/'receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(OUT/'audit.log'),
             'report_sha256':digest(REPORT) if REPORT.exists() else None})
        require(code==0,'Independent audit failed')
        report=json.loads(REPORT.read_text())
        require(report['status']=='complete_runtime_matrix_independently_audited' and report['completed_workers']==63
                and report['submission_commands_verified']==63,'Independent audit incomplete')
        state.pop('child_pid');state.update(status='complete',stage='all63_independently_audited',report=str(REPORT));save(OUT/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(OUT/'state.json',state);raise


if __name__=='__main__':main()
