#!/usr/bin/env python3
"""Wait for the current paired full44 owner, then perform one complete full50 run."""
import json
import os
from pathlib import Path
import subprocess
import time
from run_route_tree_full50_recovery_v2 import ROOT, OUT, PROJECT, AUDIT, CONTROL
from route_tree_serial_prerequisites_v1 import validate_predecessors
from check_vitis_kernel import digest,require
from supervise_compressed_batch_hls import identity
from run_compact_native_stack_recovery_v3 import atomic

FOLDER=ROOT/'data/derived/route_tree_recovery_supervision_20261029_v2'
PREDECESSOR=ROOT/'data/derived/paired_binary_nonzero_supervision_20261029_v3'
PREPARATION=ROOT/'results/route_tree_serial_recovery_preparation_20261029_v2.json'


def main():
    prep=json.loads(PREPARATION.read_text())
    require(prep['status']=='full50_serial_recovery_inputs_and_resource_only_pipeline_delta_verified','Unprepared full50 entry')
    for p,h in prep['files'].items():require(digest(p)==h,'Changed prepared full50 source/evidence')
    require(not any(p.exists() for p in [FOLDER,OUT,PROJECT,AUDIT,CONTROL]),'Refuse duplicate/retry')
    previous=json.loads((PREDECESSOR/'state.json').read_text());pid=previous['owner_pid']
    owner=identity(pid) if previous['status']=='running' else None
    if owner:require('supervise_paired_binary_nonzero_full44_v3.py' in owner['command'],'Different paired owner')
    FOLDER.mkdir()
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_paired_nonzero_full44_independent_acceptance',predecessor_pid=pid,transactions_required=50)
    atomic(FOLDER/'state.json',state)
    files={**prep['files'],str(PREPARATION):digest(PREPARATION),str(PREDECESSOR/'plan.json'):digest(PREDECESSOR/'plan.json')}
    atomic(FOLDER/'plan.json',dict(files=files,predecessor_identity=owner,output=str(AUDIT),transactions_required=50))
    try:
        while True:
            previous=json.loads((PREDECESSOR/'state.json').read_text())
            require(previous['owner_pid']==pid,'Paired owner changed')
            if previous['status']!='running':break
            require(owner is not None and identity(pid)==owner,'Paired owner missing/replaced')
            time.sleep(30)
        require(previous['status']=='complete' and previous['stage']=='both_modes_full44_independently_audited','Paired prerequisite failed; no retry')
        validate_predecessors()
        for p,h in files.items():require(digest(p)==h,'Changed serial plan/input')
        state.update(stage='full50_recovery');atomic(FOLDER/'state.json',state)
        command=['python3',str(ROOT/'scripts/run_route_tree_full50_recovery_v2.py')];started=time.monotonic()
        with (FOLDER/'execution.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;atomic(FOLDER/'state.json',state);code=child.wait()
        atomic(FOLDER/'execution.receipt.json',dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-started,log_sha256=digest(FOLDER/'execution.log')))
        require(code==0 and AUDIT.is_file(),'Full50 recovery failed; no retry')
        state.update(status='complete',stage='full50_independently_audited');atomic(FOLDER/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error));atomic(FOLDER/'state.json',state);raise


if __name__=='__main__':main()
