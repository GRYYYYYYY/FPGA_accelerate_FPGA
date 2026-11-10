#!/usr/bin/env python3
"""Wait for full50 tree acceptance, then execute/audit full30 snapshot and full2tx read once."""
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest,require
from snapshot_read_serial_prerequisites_v1 import ROOT,SNAPSHOT,READ,validate_snapshot,validate_read,snapshot_scope
from supervise_compressed_batch_hls import identity
from run_compact_native_stack_recovery_v3 import atomic

BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
CONTROL=ROOT/'data/derived/snapshot_read_serial_supervision_20261029_v1'
PREDECESSOR=ROOT/'data/derived/route_tree_recovery_supervision_20261029_v2'
PREPARATION=ROOT/'results/snapshot_read_serial_preparation_20261029_v1.json'


def main():
    prepared=json.loads(PREPARATION.read_text())
    require(prepared['status']=='full30_snapshot_and_full2tx_read_original_scope_serial_entries_prepared','Unprepared entries')
    for p,h in prepared['files'].items():require(digest(p)==h,'Changed full30/read preparation')
    require(not CONTROL.exists(),'Refuse competing supervisor/retry')
    definitions=[('snapshot','run_snapshot_dpi_rtl_v5.py','check_snapshot_dpi_rtl_v5.py',BASE/'snapshot_dpi_rtl_v5',ROOT/'results'/SNAPSHOT),
                 ('read','run_search_read_control_staging_dpi_rtl_v4.py','check_search_read_control_staging_dpi_rtl_v4.py',BASE/'search_read_control_staging_dpi_rtl_v4',ROOT/'results'/READ)]
    for _,_,_,trial,result in definitions:require(not trial.exists() and not result.exists(),'Existing full30/read trial/result')
    previous=json.loads((PREDECESSOR/'state.json').read_text());pid=previous['owner_pid']
    owner=identity(pid) if previous['status']=='running' else None
    if owner:require('supervise_route_tree_recovery_v2.py' in owner['command'],'Different full50 owner')
    CONTROL.mkdir();state=dict(owner_pid=os.getpid(),status='running',stage='waiting_full50_tree_independent_acceptance',predecessor_pid=pid)
    atomic(CONTROL/'state.json',state)
    files={**prepared['files'],str(PREPARATION):digest(PREPARATION),str(PREDECESSOR/'plan.json'):digest(PREDECESSOR/'plan.json')}
    jobs=[]
    for label,driver,checker,trial,result in definitions:
        jobs.extend([dict(stage=label+'_execute',command=['python3',str(ROOT/'scripts'/driver)]),
                     dict(stage=label+'_independent_audit',command=['python3',str(ROOT/'scripts'/checker),'--bundle',str(trial),'--output',str(result)])])
    atomic(CONTROL/'plan.json',dict(files=files,predecessor_identity=owner,jobs=jobs,transactions=[30,2],pointers=[13,13],models=[10,7]))
    try:
        while True:
            previous=json.loads((PREDECESSOR/'state.json').read_text());require(previous['owner_pid']==pid,'Full50 owner changed')
            if previous['status']!='running':break
            require(owner is not None and identity(pid)==owner,'Full50 owner missing/replaced')
            time.sleep(30)
        require(previous['status']=='complete' and previous['stage']=='full50_independently_audited','Full50 prerequisite failed; no retry')
        for job in jobs:
            if job['stage']=='snapshot_execute':validate_snapshot()
            if job['stage']=='read_execute':validate_read()
            for p,h in files.items():require(digest(p)==h,'Changed serial source/input')
            state.update(stage=job['stage']);atomic(CONTROL/'state.json',state);started=time.monotonic()
            lp=CONTROL/(job['stage']+'.log')
            with lp.open('x') as log:
                child=subprocess.Popen(job['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;atomic(CONTROL/'state.json',state);code=child.wait()
            atomic(CONTROL/(job['stage']+'.receipt.json'),dict(**job,exit_code=code,elapsed_seconds=time.monotonic()-started,log_sha256=digest(lp)))
            require(code==0,'Failed '+job['stage']+'; no retry')
        snapshot_scope(json.loads((ROOT/'results'/SNAPSHOT).read_text()))
        read=json.loads((ROOT/'results'/READ).read_text())
        require(read['status']=='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified' and read['rtl_verified'] and read['transactions']==2 and read['models']==7 and read['output_files']==5,'Incomplete final read-control audit')
        state.update(status='complete',stage='full30_snapshot_and_read_control_independently_audited');atomic(CONTROL/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error));atomic(CONTROL/'state.json',state);raise


if __name__=='__main__':main()
