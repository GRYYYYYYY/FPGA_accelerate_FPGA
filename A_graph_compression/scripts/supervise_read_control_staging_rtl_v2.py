#!/usr/bin/env python3
"""Wait for original native full44 acceptance, then run one complete candidate trial."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from read_control_pipeline_prerequisites_v1 import validate_prerequisites as validate
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    upstream = ROOT/'data/derived/snapshot_dpi_supervision_20261025_v3'
    prior = json.loads((upstream/'state.json').read_text())
    owner = identity(prior['owner_pid'])
    require(owner and 'supervise_snapshot_dpi_rtl_v3.py' in owner['command'], 'Original independent audit owner missing')
    output = ROOT/'data/derived/read_control_staging_rtl_supervision_20261025_v2'
    bundle = BASE/'search_read_control_staging_dpi_rtl_v2'
    result = ROOT/'results/search_read_control_staging_rtl_audit_20261025_v1.json'
    require(not bundle.exists() and not result.exists(), 'Existing candidate trial; refuse duplicate')
    output.mkdir(exist_ok=False)
    driver = ROOT/'scripts/run_search_read_control_staging_dpi_rtl_v2.py'
    checker = ROOT/'scripts/check_search_read_control_staging_dpi_rtl_v2.py'
    paths = [driver, checker, Path(__file__).resolve(), ROOT/'scripts/read_control_pipeline_prerequisites_v1.py', ROOT/'scripts/paired_binary_rtl_prerequisites_v1.py', upstream/'plan.json', ROOT/'results/search_read_control_staging_full_depth_setup_audit_20261025_v1.json', ROOT/'results/search_read_control_staging_hls_audit_20261025_v1.json', ROOT/'scripts/transform_axi_memory_dpi_v2.py', ROOT/'scripts/check_axi_dpi_storage_edits_v1.py']
    files = {str(path):digest(path) for path in paths}
    atomic(output/'plan.json', dict(upstream_owner=owner, files=files, transactions=2, models=7,
        per_process_address_space_limit_bytes=64*1024**3, minimum_raw_free_bytes=152*1024**3,
        policy='One full2 read-control candidate execution and independent audit after accepted full30 snapshot; no automatic retry or cap increase'))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_full30_snapshot_independent_acceptance')
    atomic(output/'state.json', state)
    try:
        while identity(owner['pid'])==owner:
            time.sleep(30)
        prior = json.loads((upstream/'state.json').read_text())
        require(prior['status']=='complete' and prior['stage']=='full30_snapshot_dpi_independently_verified', 'Original full30 snapshot independent acceptance failed')
        validate(ROOT/'results')
        cg = Path('/sys/fs/cgroup')
        state['stage'] = 'waiting_candidate_memory_admission'
        atomic(output/'state.json', state)
        while int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())<152*1024**3:
            time.sleep(30)
        require(not bundle.exists() and not result.exists(), 'Candidate trial appeared while waiting')
        jobs = [('candidate_full2_rtl',[sys.executable,str(driver)]),
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
        require(accepted['status']=='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified', 'Full candidate acceptance missing')
        state.update(status='complete',stage='read_control_staging_full2_independently_verified',report=str(result),report_sha256=digest(result))
        atomic(output/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error))
        atomic(output/'state.json',state)
        raise


if __name__=='__main__':
    main()
