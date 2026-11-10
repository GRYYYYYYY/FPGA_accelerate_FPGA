#!/usr/bin/env python3
"""Observe the existing snapshot/word chain; launch full search exactly once."""
import json
import os
import subprocess
import time
from pathlib import Path
from supervise_search_router_chain import ROOT, digest, save, live_owner, verified_gate

OUT = ROOT / 'data/derived/complete_search_router_chain_20261024_v1'
CHAIN = ROOT / 'data/derived/search_router_chain_20261024_v1'
WORD = ROOT / 'data/derived/word_snapshot_router_20261024_v1'
TARGET = ROOT / 'data/derived/complete_search_router_20261024_v1'
CHAIN_SCRIPT = 'supervise_search_router_chain.py'
PIPELINE = ROOT / 'scripts/complete_search_router_pipeline.py'
WORD_REPORT = ROOT / 'results/word_snapshot_router_audit_20261024_v1.json'
WORD_STATUS = 'four_full_router_word_snapshot_conditions_independently_verified'
RESULT = ROOT / 'results/complete_search_router_audit_20261024_v1.json'
RESULT_STATUS = 'two_full_router_kernel_conditions_independently_verified'


def observe_chain():
    state = json.loads((CHAIN / 'state.json').read_text())
    if state['status'] == 'complete':
        if state['stage'] != 'all_three_independently_audited' or state['completed'] != ['controller', 'snapshot', 'word_snapshot']:
            raise RuntimeError('Incomplete predecessor chain terminal state')
        return state
    if state['status'] != 'running':
        raise RuntimeError('Predecessor chain failed; no automatic relaunch')
    if not live_owner(state['owner_pid'], CHAIN_SCRIPT):
        state = json.loads((CHAIN / 'state.json').read_text())
        if state['status'] == 'complete':
            return observe_chain()
        raise RuntimeError('Predecessor owner missing; reconciliation required')
    return state


def main():
    observed = observe_chain()
    if (TARGET / 'state.json').exists():
        raise RuntimeError('Full search already has an owner; no duplicate launch')
    paths = [Path(__file__).resolve(), PIPELINE, CHAIN / 'plan.json', TARGET / 'plan.json',
             ROOT / 'scripts' / CHAIN_SCRIPT, ROOT / 'scripts/prepare_search_heap_router.py']
    bindings = {str(p): digest(p) for p in paths}
    OUT.mkdir(exist_ok=False)
    save(OUT / 'plan.json', {'files': bindings, 'predecessor': str(CHAIN), 'target': str(TARGET),
        'policy': 'Observe existing chain. Require its terminal success and independently verified word audit before single launch. Stop on failure or changed inputs; never recover/restart automatically.'})
    state = {'owner_pid': os.getpid(), 'status': 'running', 'stage': 'await_existing_chain',
             'observed_owner': observed['owner_pid'], 'observed_stage': observed['stage']}

    def update():
        temporary = OUT / 'state.tmp'
        temporary.write_text(json.dumps(state, indent=2) + '\n')
        temporary.replace(OUT / 'state.json')

    update()
    try:
        while observed['status'] != 'complete':
            time.sleep(15)
            observed = observe_chain()
            if state['observed_stage'] != observed['stage']:
                state['observed_stage'] = observed['stage']
                update()
        for p, h in bindings.items():
            if digest(p) != h:
                raise RuntimeError('Changed queue input ' + p)
        prior_plan = json.loads((CHAIN / 'plan.json').read_text())
        for p, h in prior_plan['files'].items():
            if digest(p) != h:
                raise RuntimeError('Changed predecessor plan binding ' + p)
        gate = verified_gate(WORD, WORD_REPORT, WORD_STATUS)
        original_gate = json.loads((CHAIN / 'word_snapshot_gate.json').read_text())
        if original_gate != gate:
            raise RuntimeError('Predecessor gate does not match current audit')
        save(OUT / 'word_gate.json', gate)
        if (TARGET / 'state.json').exists():
            raise RuntimeError('Full search acquired another owner; no duplicate launch')
        command = ['python3', str(PIPELINE)]
        log = OUT / 'complete_search.log'
        with log.open('x') as stream:
            child = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
            save(OUT / 'submission.json', {'command': command, 'child_pid': child.pid,
                'plan_sha256': digest(OUT / 'plan.json')})
            state.update(stage='full_search_workloads_and_audit', child_pid=child.pid)
            update()
            code = child.wait()
        save(OUT / 'receipt.json', {'command': command, 'exit_code': code, 'log_sha256': digest(log)})
        if code:
            raise RuntimeError('Full search pipeline failed')
        save(OUT / 'complete_search_gate.json', verified_gate(TARGET, RESULT, RESULT_STATUS))
        state.update(status='complete', stage='full_search_independently_audited')
        update()
    except BaseException as error:
        state.update(status='failed', error=str(error))
        update()
        raise


if __name__ == '__main__':
    main()
