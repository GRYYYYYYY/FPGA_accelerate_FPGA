#!/usr/bin/env python3
"""Wait for the existing integration audit, then run and audit 21 fresh full-chain trials."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_source_to_route import digest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / 'results/source_to_route_statistics_pipeline_20261023_v1'
UPSTREAM = ROOT / 'results/source_to_route_audit_pipeline_20261023_v1.json'
VALIDATION = ROOT / 'results/source_to_route_validation_audit_20261023_v1.json'
OUTPUT = ROOT / 'data/derived/source_to_route_statistics_20261023_v1'
FINAL = ROOT / 'results/source_to_route_statistics_audit_20261023_v1.json'


def identity(pid):
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        return None if fields[0] == 'Z' else fields[19]
    except FileNotFoundError:
        return None


def main():
    lock = PREFIX.with_suffix('.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state_path = PREFIX.with_suffix('.json')
    if state_path.exists() or OUTPUT.exists() or FINAL.exists():
        raise ValueError('Existing statistics ownership or output; do not resubmit')
    upstream = json.loads(UPSTREAM.read_text())
    owner = upstream['owner_pid']
    start = identity(owner)
    if start and b'source_to_route_audit_pipeline.py' not in Path(f'/proc/{owner}/cmdline').read_bytes():
        raise ValueError('Unexpected upstream audit owner')
    driver = ROOT / 'scripts/source_to_route_statistics.py'
    checker = ROOT / 'scripts/check_source_to_route_statistics.py'
    files = {str(path): digest(path) for path in (Path(__file__), driver, checker,
             ROOT / 'scripts/check_source_to_route.py', ROOT / 'scripts/source_to_route_experiment.py',
             ROOT / 'results/regression_source_to_route_statistics_20261023_v1.log')}
    state = {'owner_pid': os.getpid(), 'upstream_audit_owner_pid': owner, 'upstream_start_ticks': start,
             'status': 'running', 'stage': 'wait_existing_integration_audit', 'files': files,
             'matrix': {'repeats': 7, 'conditions': 3, 'workers': 21, 'batches_per_worker': 2,
                        'cpu': 125, 'seed': 20261023}, 'output': str(OUTPUT)}
    def save(**changes):
        state.update(changes)
        tmp = state_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2)+'\n')
        tmp.replace(state_path)
    def run(stage, command):
        for path, value in files.items():
            if digest(path) != value:
                raise ValueError('Frozen pipeline dependency changed: ' + path)
        with PREFIX.with_suffix('.'+stage+'.log').open('x') as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT)
            save(stage=stage, child_pid=child.pid, command=command)
            code = child.wait()
        state.pop('child_pid', None)
        if code:
            raise RuntimeError(stage+' failed: '+str(code))
    save()
    try:
        while start is not None and identity(owner) == start:
            time.sleep(15)
        upstream = json.loads(UPSTREAM.read_text())
        if upstream['owner_pid'] != owner or upstream['status'] != 'complete' or upstream['report_sha256'] != digest(VALIDATION):
            raise ValueError('Original independent integration audit did not complete successfully')
        audited = json.loads(VALIDATION.read_text())
        if audited['status'] != 'all_source_to_route_integration_trials_audited' or audited['completed_workers'] != 3:
            raise ValueError('Full integration audit scope incomplete')
        save(validation_audit_sha256=digest(VALIDATION))
        run('statistics', [sys.executable, '-u', str(driver), '--output', str(OUTPUT), '--cpu', '125'])
        run('final_audit', [sys.executable, '-u', str(checker), str(OUTPUT), '--output', str(FINAL)])
        final = json.loads(FINAL.read_text())
        if final['status'] != 'complete_source_to_route_statistics_audited' or final['completed_workers'] != 21:
            raise ValueError('Full statistics audit scope incomplete')
        save(status='complete', stage='complete', report_sha256=digest(FINAL))
    except BaseException as error:
        save(status='failed', error=str(error))
        raise


if __name__ == '__main__':
    main()
