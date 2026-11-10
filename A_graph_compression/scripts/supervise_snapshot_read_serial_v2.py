#!/usr/bin/env python3
"""After corrected full50 acceptance, serialize the complete full30 and full2 RTL contracts."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from supervise_route_tree_recovery_v3 import stop, matches
from snapshot_read_serial_prerequisites_v2 import (
    ROOT, TREE, SNAPSHOT, READ, validate_snapshot, validate_read, snapshot_scope)

BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
CONTROL = ROOT / 'data/derived/snapshot_read_serial_supervision_20261031_v2'
PREDECESSOR = ROOT / 'data/derived/route_tree_recovery_supervision_20261031_v3'
PREPARATION = ROOT / 'results/snapshot_read_serial_preparation_20261031_v2.json'


def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    prepared = json.loads(PREPARATION.read_text())
    require(prepared['status'] == 'corrected_chain_full30_and_full2_original_scope_entries_prepared',
            'Unprepared full30/read entries')
    for p, h in prepared['files'].items():
        require(digest(p) == h, 'Changed full30/read preparation: ' + p)
    require(not CONTROL.exists(), 'Refuse competing supervisor or retry')
    definitions = [
        ('snapshot', 'run_snapshot_dpi_rtl_v6.py', 'check_snapshot_dpi_rtl_v6.py',
         BASE / 'snapshot_dpi_rtl_v6', ROOT / 'results' / SNAPSHOT),
        ('read', 'run_search_read_control_staging_dpi_rtl_v5.py',
         'check_search_read_control_staging_dpi_rtl_v5.py',
         BASE / 'search_read_control_staging_dpi_rtl_v5', ROOT / 'results' / READ)]
    jobs = []
    for label, driver, checker, trial, report in definitions:
        require(not trial.exists() and not report.exists(), 'Existing full30/read trial/report')
        jobs.extend([
            dict(stage=label+'_execute', command=[sys.executable, str(ROOT/'scripts'/driver)], audit=False),
            dict(stage=label+'_independent_audit', command=[
                'prlimit', '--as=17179869184:17179869184', '--stack=67108864:67108864', '--core=0:0', '--',
                sys.executable, str(ROOT/'scripts'/checker), '--bundle', str(trial), '--output', str(report)],
                 audit=True, report=str(report), label=label)])
    previous = json.loads((PREDECESSOR / 'state.json').read_text())
    owner = process(previous['owner_pid'])
    require(owner and owner['state'] != 'Z' and
            'supervise_route_tree_recovery_v3.py' in owner['command'], 'Full50 owner not verified')
    files = {**prepared['files'], str(PREPARATION): digest(PREPARATION),
             str(PREDECESSOR/'plan.json'): digest(PREDECESSOR/'plan.json')}
    CONTROL.mkdir()
    atomic(CONTROL/'plan.json', dict(files=files, predecessor_identity=owner, jobs=jobs,
           transactions=[30, 2], pointers=[13, 13], models=[10, 7], no_physical_or_board_launch=True))
    state = dict(owner_pid=os.getpid(), status='running',
                 stage='waiting_corrected_full50_tree_independent_acceptance', completed=[])
    atomic(CONTROL/'state.json', state)
    child = None
    try:
        while True:
            previous = json.loads((PREDECESSOR/'state.json').read_text())
            require(previous['owner_pid'] == owner['pid'] and previous['status'] != 'failed',
                    'Full50 predecessor changed/failed')
            live = matches(owner)
            require(live or previous['status'] == 'complete', 'Full50 owner lost without success')
            if not live:
                require(previous['stage'] == 'full50_independently_audited' and
                        previous['report_sha256'] == digest(ROOT/'results'/TREE), 'Wrong full50 completion')
                gates = validate_snapshot()
                receipt_path = PREDECESSOR/'execution.receipt.json'
                receipt = json.loads(receipt_path.read_text())
                log = PREDECESSOR/'execution.log'
                require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and
                        receipt['log_sha256'] == digest(log), 'Failed full50 execution receipt')
                for p in (receipt_path, log, PREDECESSOR/'state.json'):
                    gates[str(p)] = digest(p)
                atomic(CONTROL/'gates.json', dict(files=gates))
                break
            atomic(CONTROL/'observation.json', dict(predecessor_verified=True,
                   predecessor_stage=previous['stage'], monotonic_seconds=time.monotonic()))
            time.sleep(10)
        initial = observe()
        for job in jobs:
            if job['stage'] == 'snapshot_execute':
                validate_snapshot()
            if job['stage'] == 'read_execute':
                validate_read()
            for p, h in files.items():
                require(digest(p) == h, 'Changed serial source/input: ' + p)
            require(abort_reason(initial, observe()) is None, 'New OOM/reset before stage')
            state['stage'] = job['stage']
            atomic(CONTROL/'state.json', state)
            started = time.monotonic()
            log = CONTROL/(job['stage']+'.log')
            reason = None
            with log.open('x') as output:
                child = subprocess.Popen(job['command'], cwd=ROOT, stdin=subprocess.DEVNULL,
                                         stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
                state['child_pid'] = child.pid
                atomic(CONTROL/'state.json', state)
                while child.poll() is None:
                    reason = abort_reason(initial, observe())
                    if reason:
                        stop(child)
                        break
                    time.sleep(1)
                code = child.wait()
                child = None
            reason = reason or abort_reason(initial, observe())
            atomic(CONTROL/(job['stage']+'.receipt.json'), dict(**job, exit_code=code,
                   abort_reason=reason, elapsed_seconds=time.monotonic()-started, log_sha256=digest(log)))
            require(code == 0 and reason is None, 'Failed '+job['stage']+'; no retry')
            if job['audit']:
                report_path = Path(job['report'])
                report = json.loads(report_path.read_text())
                if job['label'] == 'snapshot':
                    snapshot_scope(report)
                else:
                    require(report['status'] == 'read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified'
                            and report['rtl_verified'] is True and
                            (report['transactions'], report['models'], report['output_files']) == (2, 7, 5),
                            'Incomplete read-control acceptance')
                for p, h in report['files'].items():
                    require(digest(p) == h, 'Changed independent audit evidence')
                atomic(CONTROL/(job['stage']+'.result.json'),
                       dict(report=str(report_path), sha256=digest(report_path), status=report['status']))
            state['completed'].append(job['stage'])
            atomic(CONTROL/'state.json', state)
        state.update(status='complete', stage='full30_snapshot_and_read_control_independently_audited')
        atomic(CONTROL/'state.json', state)
    except BaseException as exc:
        if child is not None and child.poll() is None:
            stop(child)
        state.update(status='failed', error=str(exc))
        atomic(CONTROL/'state.json', state)
        raise


if __name__ == '__main__':
    main()
