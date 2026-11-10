#!/usr/bin/env python3
"""One downstream audit owner; wait for the existing execution, never resubmit it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def identity(pid):
    try:
        stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        if stat[0]=='Z':return None
        return stat[19]
    except FileNotFoundError:return None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('experiment',type=Path);p.add_argument('--state',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    directory=a.experiment.resolve();plan_path=directory/'plan.json'
    plan=json.loads(plan_path.read_text());owner=plan['owner_pid'];start_id=identity(owner)
    if start_id is not None:
        command=Path(f'/proc/{owner}/cmdline').read_bytes().split(b'\0')
        if not any(v.endswith(b'native_site_experiment.py') for v in command):raise ValueError('Unexpected execution process')
    checker=ROOT/'scripts/check_native_site_routing.py'
    bound={str(path):digest(path) for path in (Path(__file__),checker,plan_path,
        ROOT/'scripts/real_experiment.py',ROOT/'src/packed_graph.py',ROOT/'src/site_search.py',ROOT/'src/site_resources.py')}
    state={'owner_pid':os.getpid(),'execution_owner_pid':owner,'execution_start_ticks':start_id,
           'status':'waiting_existing_execution','experiment':str(directory),'report':str(a.report.resolve()),'files':bound}
    write_new(a.state,state)
    def update(**changes):
        state.update(changes);tmp=a.state.with_suffix('.json.tmp')
        with tmp.open('w') as f:json.dump(state,f,indent=2);f.write('\n')
        tmp.replace(a.state)
    while start_id is not None and identity(owner)==start_id:time.sleep(15)
    try:
        complete=json.loads((directory/'execution_complete.json').read_text())
        if complete['status']!='awaiting_independent_semantic_audit' or complete['owner_pid']!=owner:
            raise ValueError('Execution did not finish successfully')
        for path,value in bound.items():
            if digest(path)!=value:raise ValueError('Frozen audit input changed: '+path)
        command=[sys.executable,'-u',str(checker),str(directory),'--output',str(a.report.resolve())]
        process=subprocess.Popen(command)
        update(status='auditing',audit_pid=process.pid,command=command)
        code=process.wait()
        if code:raise RuntimeError(f'Independent audit failed with exit {code}')
        report=json.loads(a.report.read_text())
        if report['status']!='verified_native_site_routing':raise ValueError('Audit was not complete')
        update(status='complete',report_sha256=digest(a.report))
    except Exception as error:
        update(status='failed',error=str(error));raise


if __name__=='__main__':main()
