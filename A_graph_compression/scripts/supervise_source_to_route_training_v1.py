#!/usr/bin/env python3
"""Run three full validation conditions, then seven audited paired blocks with fresh training."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic
from supervise_integrated_rtl_recovery_v1 import source_closure

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/derived/source_to_route_training_supervision_20261027_v1'


def main():
    validation = ROOT/'data/derived/source_to_route_training_validation_20261027_v1'
    validation_audit = ROOT/'results/source_to_route_training_validation_audit_20261027_v1.json'
    statistics = ROOT/'data/derived/source_to_route_training_statistics_20261027_v1'
    final = ROOT/'results/source_to_route_training_statistics_audit_20261027_v1.json'
    require(not any(p.exists() for p in [OUT, validation, validation_audit, statistics, final]), 'Existing training-inclusive run; refuse duplicate')
    commands = [
        ('full_validation', [sys.executable, '-u', str(ROOT/'scripts/source_to_route_with_training_v1.py'), '--output', str(validation), '--cpu', '121']),
        ('validation_audit', [sys.executable, '-u', str(ROOT/'scripts/check_source_to_route_with_training_v1.py'), str(validation), '--output', str(validation_audit)]),
        ('seven_paired_blocks', [sys.executable, '-u', str(ROOT/'scripts/source_to_route_training_statistics_v1.py'), '--output', str(statistics), '--cpu', '121']),
        ('statistics_audit', [sys.executable, '-u', str(ROOT/'scripts/check_source_to_route_training_statistics_v1.py'), str(statistics), '--output', str(final)]),
    ]
    files = source_closure([Path(__file__).resolve(), *[Path(c[2]) for _, c in commands]], ROOT/'scripts')
    preflight = ROOT/'data/derived/fresh_training_equivalence_20261027_v1/report.json'
    proof = json.loads(preflight.read_text())
    require(proof['status'] == 'fresh_training_from_original_complete3761_sources_reproduces_exact440_template_bank', 'Fresh training equivalence missing')
    for p, h in proof['files'].items():
        require(digest(p) == h, 'Training equivalence input changed')
        files[p] = h
    files[str(preflight)] = digest(preflight)
    OUT.mkdir(exist_ok=False)
    atomic(OUT/'plan.json', dict(files=files, commands=commands, cpu=121,
           validation_conditions=3, repetitions=7, statistics_workers=21, batches_per_worker=2, nets_per_batch=1062,
           worker_address_space_bytes=16*1024**3, resource_abort_free_bytes=16*1024**3,
           policy='One full validation/audit then21 fresh full workload workers and audits; no retries or reduced scope; original native algorithm and14-instance site model preserved'))
    state = dict(owner_pid=os.getpid(), status='running', stage='preflight')
    atomic(OUT/'state.json', state)
    try:
        for stage, command in commands:
            for p, h in files.items():
                require(digest(p) == h, 'Scheduled source changed: '+p)
            cg = Path('/sys/fs/cgroup')
            require(int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text()) >= 16*1024**3,
                    'Runtime memory protection already active')
            state.update(stage=stage)
            atomic(OUT/'state.json', state)
            start = time.monotonic()
            aborted = False
            with (OUT/(stage+'.log')).open('x') as log:
                child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                state['child_pid'] = child.pid
                atomic(OUT/'state.json', state)
                while child.poll() is None:
                    free = int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())
                    if free < 16*1024**3:
                        aborted = True
                        state['triggering_raw_free_bytes'] = free
                        atomic(OUT/'state.json', state)
                        try: os.killpg(child.pid, signal.SIGTERM)
                        except ProcessLookupError: pass
                        break
                    time.sleep(2)
                try: code = child.wait(timeout=15 if aborted else None)
                except subprocess.TimeoutExpired:
                    try: os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    code = child.wait()
            atomic(OUT/(stage+'.receipt.json'), dict(command=command, exit_code=code, resource_abort=aborted,
                   elapsed_seconds=time.monotonic()-start, log_sha256=digest(OUT/(stage+'.log'))))
            require(code == 0 and not aborted, 'Training-inclusive phase failed: '+stage)
            if stage == 'validation_audit':
                accepted = json.loads(validation_audit.read_text())
                require(accepted['status'] == 'all_source_to_route_integration_trials_audited' and accepted['completed_workers'] == 3,
                        'Full three-condition validation incomplete')
        report = json.loads(final.read_text())
        require(report['status'] == 'complete_source_to_route_statistics_audited' and report['completed_workers'] == 21,
                'Complete seven-repeat matrix missing')
        state.pop('child_pid', None)
        state.update(status='complete', stage='training_inclusive_full_workload_statistics_audited', report=str(final), report_sha256=digest(final))
        atomic(OUT/'state.json', state)
    except BaseException as error:
        state.update(status='failed', error=str(error))
        atomic(OUT/'state.json', state)
        raise


if __name__ == '__main__':
    main()
