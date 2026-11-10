#!/usr/bin/env python3
"""Wait for original native full44 acceptance, then run one complete candidate trial."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from binary_fsm_full44_prerequisites_v1 import validate
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    upstream = BASE/'compact_native_stack_final_audit_v2'
    prior = json.loads((upstream/'state.json').read_text())
    owner = identity(prior['owner_pid'])
    require(owner and 'supervise_compact_native_stack_recovery_audit_v2.py' in owner['command'], 'Original independent audit owner missing')
    output = ROOT/'data/derived/binary_fsm_full44_supervision_20261025_v1'
    bundle = BASE/'compressed_batch_bus64_binary_fsm_rtl_v1'
    result = ROOT/'results/compressed_bus64_binary_fsm_rtl_audit_20261025_v1.json'
    require(not bundle.exists() and not result.exists(), 'Existing candidate trial; refuse duplicate')
    output.mkdir(exist_ok=False)
    driver = ROOT/'scripts/run_compressed_bus64_binary_fsm_rtl_v1.py'
    checker = ROOT/'scripts/check_compressed_bus64_binary_fsm_rtl_v1.py'
    paths = [driver, checker, Path(__file__).resolve(), ROOT/'scripts/binary_fsm_full44_prerequisites_v1.py',
             ROOT/'scripts/check_hls_fsm_binary_v1.py', ROOT/'scripts/audit_hls_fsm_shape_v3.py', upstream/'plan.json',
             ROOT/'results/hls_binary_fsm_candidate_edit_audit_20261025_v1.json', ROOT/'results/fsm_binary_four_state_regression_20261025_v1.json',
             ROOT/'data/derived/hls_binary_fsm_candidate_20261025_v1/plan.json']
    files = {str(path):digest(path) for path in paths}
    atomic(output/'plan.json', dict(upstream_owner=owner, files=files, transactions=4, pointers=44, models=30,
        per_process_address_space_limit_bytes=64*1024**3, minimum_raw_free_bytes=128*1024**3,
        policy='One candidate execution and independent audit after original native recovery acceptance; no automatic retry or cap increase'))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_original_native_full44_independent_acceptance')
    atomic(output/'state.json', state)
    try:
        while identity(owner['pid'])==owner:
            time.sleep(30)
        prior = json.loads((upstream/'state.json').read_text())
        require(prior['status']=='complete' and prior['stage']=='independently_audited', 'Original full44 recovery independent acceptance failed')
        validate()
        cg = Path('/sys/fs/cgroup')
        state['stage'] = 'waiting_candidate_memory_admission'
        atomic(output/'state.json', state)
        while int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())<128*1024**3:
            time.sleep(30)
        require(not bundle.exists() and not result.exists(), 'Candidate trial appeared while waiting')
        jobs = [('candidate_full44_rtl',[sys.executable,str(driver)]),
                ('independent_audit',[sys.executable,str(checker),'--bundle',str(bundle),'--output',str(result)])]
        for phase, command in jobs:
            for path, checksum in files.items():
                require(digest(path)==checksum, 'Changed scheduled candidate input '+path)
            state['stage'] = phase
            atomic(output/'state.json', state)
            start = time.monotonic()
            with (output/(phase+'.log')).open('x') as log:
                child = subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid'] = child.pid
                atomic(output/'state.json',state)
                code = child.wait()
            atomic(output/(phase+'.receipt.json'),dict(command=command,exit_code=code,
                elapsed_seconds=time.monotonic()-start,log_sha256=digest(output/(phase+'.log'))))
            require(code==0, 'Candidate phase failed '+phase+'; retain evidence without retry')
        accepted = json.loads(result.read_text())
        require(accepted['status']=='binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified', 'Full candidate acceptance missing')
        state.update(status='complete',stage='binary_fsm_full44_candidate_independently_verified',report=str(result),report_sha256=digest(result))
        atomic(output/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error))
        atomic(output/'state.json',state)
        raise


if __name__=='__main__':
    main()
