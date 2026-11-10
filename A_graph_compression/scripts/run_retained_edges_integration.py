#!/usr/bin/env python3
"""Run the frozen complete randomized router comparison once after compilation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=Path('data/derived/retained_edges_integration_20261024_v1').resolve()
    state=out/'run_state.json'
    if state.exists():raise ValueError('Existing run; reconcile instead of restarting')
    plan=json.loads((out/'plan.json').read_text())
    for p,h in plan['files'].items():
        if sha(p)!=h:raise ValueError('Changed input '+p)
    binary=out/'differential'
    if not binary.is_file():raise ValueError('Compile not completed')
    cmd=['taskset','-c','119',str(binary),str(out/'source/sites.txt')]
    record=dict(owner_pid=os.getpid(),status='running',command=cmd,binary_sha256=sha(binary),plan_sha256=sha(out/'plan.json'),supervisor_sha256=sha(__file__))
    def save():state.write_text(json.dumps(record,indent=2)+'\n')
    save();started=time.monotonic()
    env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'}
    env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    with (out/'differential.log').open('x') as log:
        child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
        record['child_pid']=child.pid;save();code=child.wait()
    text=(out/'differential.log').read_text()
    expected=('ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 '
              'node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\n'
              'ROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n')
    good=code==0 and text==expected
    for p,h in plan['files'].items():good=good and sha(p)==h
    record.update(status='complete' if good else 'failed',exit_code=code,elapsed_seconds=time.monotonic()-started,log_sha256=sha(out/'differential.log'),full_router_differential_verified=good)
    save();print(record['status'],flush=True)
    if not good:raise SystemExit(1)
if __name__=='__main__':main()
