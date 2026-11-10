#!/usr/bin/env python3
"""Wait for the corrected paired RTL owner, then run the unchanged full50 contract."""
import json
import os
import signal
import subprocess
import sys
import time

from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_route_tree_full50_recovery_v3 import ROOT, OUT, PROJECT, AUDIT, CONTROL
from route_tree_serial_prerequisites_v2 import validate_predecessors

FOLDER = ROOT / 'data/derived/route_tree_recovery_supervision_20261031_v3'
PREDECESSOR = ROOT / 'data/derived/bus64_full_rtl_supervision_20261030_v3'
PREPARATION = ROOT / 'results/route_tree_serial_recovery_preparation_20261031_v3.json'


def stop(child):
    # Give the wrapper time to stop its separately owned pipeline session.
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=30)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()


def matches(owner):
    current = process(owner['pid'])
    return bool(current and current['state'] != 'Z' and
                current['start_ticks'] == owner['start_ticks'] and
                current['command'] == owner['command'])


def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    prep = json.loads(PREPARATION.read_text())
    require(prep['status'] == 'full50_corrected_graph_predecessor_entries_prepared_not_executed',
            'Missing new full50 preparation')
    for p, h in prep['files'].items():
        require(digest(p) == h, 'Changed full50 preparation: ' + p)
    require(not any(p.exists() for p in (FOLDER, OUT, PROJECT, AUDIT, CONTROL)),
            'Existing full50 output/controller; no retry')
    previous = json.loads((PREDECESSOR / 'state.json').read_text())
    owner = process(previous['owner_pid'])
    require(owner and owner['state'] != 'Z' and
            'supervise_bus64_full_rtl_v3.py' in owner['command'], 'Paired owner not verified')
    FOLDER.mkdir()
    files = {**prep['files'], str(PREPARATION): digest(PREPARATION),
             str(PREDECESSOR / 'plan.json'): digest(PREDECESSOR / 'plan.json')}
    atomic(FOLDER / 'plan.json', dict(files=files, predecessor_identity=owner,
           transactions_required=50, output=str(AUDIT), no_physical_or_board_launch=True))
    state = dict(owner_pid=os.getpid(), status='running',
                 stage='waiting_corrected_paired_full4_independent_acceptance', completed=[])
    atomic(FOLDER / 'state.json', state)
    child = None
    try:
        while True:
            previous = json.loads((PREDECESSOR / 'state.json').read_text())
            require(previous['owner_pid'] == owner['pid'] and previous['status'] != 'failed',
                    'Paired predecessor changed/failed')
            live = matches(owner)
            require(live or previous['status'] == 'complete', 'Paired owner lost without acceptance')
            if not live:
                require(previous['stage'] ==
                        'both_bus64_modes_full4_RTL_original_C_independently_audited_physical_pending',
                        'Wrong paired completion')
                gates = validate_predecessors()
                for mode in (0, 1):
                    phase = f'mode_{mode}_independent_RTL_audit'
                    receipt_path = PREDECESSOR / (phase + '.receipt.json')
                    record_path = PREDECESSOR / (phase + '.result.json')
                    receipt = json.loads(receipt_path.read_text())
                    record = json.loads(record_path.read_text())
                    log = PREDECESSOR / (phase + '.log')
                    expected = ROOT / f'results/collision_safe_bus64_full_rtl_mode_{mode}_audit_20261030_v1.json'
                    require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and
                            receipt['log_sha256'] == digest(log), 'Failed paired final audit')
                    require(record['report'] == str(expected) and record['sha256'] == gates[str(expected)],
                            'Different paired audit result')
                    for p in (receipt_path, record_path, log):
                        gates[str(p)] = digest(p)
                gates[str(PREDECESSOR / 'state.json')] = digest(PREDECESSOR / 'state.json')
                atomic(FOLDER / 'gates.json', dict(files=gates))
                break
            atomic(FOLDER / 'observation.json', dict(predecessor_verified=True,
                   predecessor_stage=previous['stage'], monotonic_seconds=time.monotonic()))
            time.sleep(10)
        for p, h in files.items():
            require(digest(p) == h, 'Changed full50 frozen source: ' + p)
        initial = observe()
        command = [sys.executable, str(ROOT / 'scripts/run_route_tree_full50_recovery_v3.py')]
        state['stage'] = 'full50_recovery'
        atomic(FOLDER / 'state.json', state)
        started = time.monotonic()
        log = FOLDER / 'execution.log'
        reason = None
        with log.open('x') as output:
            child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                     stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            state['child_pid'] = child.pid
            atomic(FOLDER / 'state.json', state)
            while child.poll() is None:
                reason = abort_reason(initial, observe())
                if reason:
                    stop(child)
                    break
                time.sleep(1)
            code = child.wait()
            child = None
        reason = reason or abort_reason(initial, observe())
        atomic(FOLDER / 'execution.receipt.json', dict(command=command, exit_code=code,
               abort_reason=reason, elapsed_seconds=time.monotonic()-started, log_sha256=digest(log)))
        require(code == 0 and reason is None, 'Full50 failed; no retry')
        report = json.loads(AUDIT.read_text())
        require(report['status'] == 'production_route_tree_full_depth_50_transactions_rtl_verified'
                and report['transactions'] == 50 and len(report['cycles']) == 50
                and all(type(c) is int and c > 0 for c in report['cycles']), 'Incomplete full50 acceptance')
        for p, h in report['files'].items():
            require(digest(p) == h, 'Changed full50 audit evidence')
        state.update(status='complete', stage='full50_independently_audited',
                     completed=['full50_recovery'], report_sha256=digest(AUDIT))
        atomic(FOLDER / 'state.json', state)
    except BaseException as exc:
        if child is not None and child.poll() is None:
            stop(child)
        state.update(status='failed', error=str(exc))
        atomic(FOLDER / 'state.json', state)
        raise


if __name__ == '__main__':
    main()
