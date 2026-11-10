#!/usr/bin/env python3
"""Wait for the actual new native owner, then execute and audit each mode once."""
import json
import os
from pathlib import Path
import subprocess
import time
from paired_binary_nonzero_contract_v3 import *
from binary_nonzero_full44_prerequisites_v2 import validate,encoded_scope
from run_compact_native_stack_recovery_v3 import atomic
from supervise_compressed_batch_hls import identity

CONTROL=ROOT/'data/derived/paired_binary_nonzero_supervision_20261029_v3'
NATIVE_CONTROL=ROOT/'data/derived/compact_nonzero_native_supervision_20261029_v2'


def main():
    prepared(0);require(not CONTROL.exists(),'Refuse duplicate owner/retry')
    for mode in [0,1]:require(not config(mode)['trial'].exists() and not config(mode)['output'].exists(),'Existing candidate trial/result')
    predecessor=json.loads((NATIVE_CONTROL/'state.json').read_text());pid=predecessor['owner_pid']
    owner=identity(pid) if predecessor['status']=='running' else None
    if owner:require('supervise_compact_nonzero_native_rtl_v2.py' in owner['command'],'Different native owner')
    CONTROL.mkdir();state=dict(owner_pid=os.getpid(),status='running',stage='waiting_nonzero_native_independent_acceptance',predecessor_pid=pid)
    atomic(CONTROL/'state.json',state)
    files={str(PREPORT):digest(PREPORT),str(NATIVE_CONTROL/'plan.json'):digest(NATIVE_CONTROL/'plan.json'),str(Path(__file__).resolve()):digest(__file__)}
    for name in ['run_binary_nonzero_full44_v3.py','check_binary_nonzero_full44_v3.py','paired_binary_nonzero_contract_v3.py','binary_nonzero_full44_prerequisites_v2.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    atomic(CONTROL/'plan.json',dict(files=files,predecessor_identity=owner,predecessor_pid=pid,graph_modes=[0,1],per_mode_transactions=4,ports=44,models=30))
    try:
        while True:
            previous=json.loads((NATIVE_CONTROL/'state.json').read_text());require(previous['owner_pid']==pid,'Native owner changed')
            if previous['status']!='running':break
            require(owner is not None and identity(pid)==owner,'Native owner missing/replaced; no restart')
            time.sleep(30)
        require(previous['status']=='complete' and previous['stage']=='independently_audited','New native prerequisite failed; preserve without retry')
        for mode in [0,1]:
            validate(mode)
            for phase,script in [('execute','run_binary_nonzero_full44_v3.py'),('independent_audit','check_binary_nonzero_full44_v3.py')]:
                for p,h in files.items():require(digest(p)==h,'Frozen supervised source changed')
                stage=config(mode)['label']+'_'+phase;state.update(stage=stage);atomic(CONTROL/'state.json',state)
                command=['python3',str(ROOT/'scripts'/script),'--mode',str(mode)];start=time.monotonic()
                with (CONTROL/(stage+'.log')).open('x') as log:
                    child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                    state['child_pid']=child.pid;atomic(CONTROL/'state.json',state);code=child.wait()
                atomic(CONTROL/(stage+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(CONTROL/(stage+'.log'))))
                require(code==0,'Failed '+stage+'; no retry')
            encoded_scope(json.loads(config(mode)['output'].read_text()),mode)
        state.update(status='complete',stage='both_modes_full44_independently_audited');atomic(CONTROL/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));atomic(CONTROL/'state.json',state);raise


if __name__=='__main__':main()
