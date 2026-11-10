#!/usr/bin/env python3
"""Run five-scope semantic validation, independent audit, then gated35-trial statistics."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
from check_source_to_route import digest
ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT/'results/template_scope_runtime_pipeline_20261023_v1'


def main():
    lock = PREFIX.with_suffix('.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state_path = PREFIX.with_suffix('.json')
    validation = ROOT/'data/derived/template_scope_runtime_validation_20261023_v1'
    statistics = ROOT/'data/derived/template_scope_runtime_statistics_20261023_v1'
    if state_path.exists() or validation.exists() or statistics.exists(): raise ValueError('Existing owner/output; do not resubmit')
    scope_report = ROOT/'data/derived/template_scope_region_20261023_v1/report.json'
    if json.loads(scope_report.read_text())['status'] != 'all_four_full_region_template_scopes_verified': raise ValueError('Full scope equivalence missing')
    driver = ROOT/'scripts/template_scope_runtime.py'; checker = ROOT/'scripts/check_template_scope_runtime.py'
    test = ROOT/'results/regression_template_scope_runtime_20261023_v1.log'
    if not test.read_text().rstrip().endswith('OK'): raise ValueError('Audit regression not passed')
    files = {str(path): digest(path) for path in (Path(__file__), driver, checker, scope_report, test,
             ROOT/'scripts/check_source_to_route.py', ROOT/'scripts/real_experiment.py')}
    state = {'owner_pid': os.getpid(), 'status': 'running', 'stage': 'preflight', 'files': files,
             'matrix': {'validation_workers': 5, 'statistics_workers': 35, 'repeats': 7, 'cpu': 126,
                        'batches_per_worker': 2, 'cache_rows': 4096, 'execution': 'direct'}}
    def save(**changes):
        state.update(changes); tmp = state_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2)+'\n'); tmp.replace(state_path)
    def run(stage, command):
        for path, value in files.items():
            if digest(path) != value: raise ValueError('Frozen scope pipeline dependency changed: '+path)
        with PREFIX.with_suffix('.'+stage+'.log').open('x') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            save(stage=stage, child_pid=child.pid, command=command)
            code = child.wait()
        state.pop('child_pid', None)
        if code: raise RuntimeError(stage+' failed: '+str(code))
    save()
    try:
        for name, repeats, output in [('validation', 1, validation), ('statistics', 7, statistics)]:
            run(name, [sys.executable, '-u', str(driver), '--output', str(output), '--repeats', str(repeats), '--cpu', '126'])
            audit = ROOT/f'results/template_scope_runtime_{name}_audit_20261023_v1.json'
            run(name+'_audit', [sys.executable, '-u', str(checker), str(output), '--repeats', str(repeats), '--output', str(audit)])
            result = json.loads(audit.read_text())
            if result['status'] != 'complete_scope_runtime_matrix_independently_audited' or result['completed_workers'] != repeats*5:
                raise ValueError('Independent scope runtime audit incomplete')
            save(**{name+'_audit_sha256': digest(audit)})
        save(status='complete', stage='complete')
    except BaseException as error:
        save(status='failed', error=str(error)); raise


if __name__ == '__main__': main()
