#!/usr/bin/env python3
"""Single native execution followed by independent audit; failure never retries."""
import json
import os
import subprocess
import time
from compact_nonzero_native_contract_v1 import *
from run_compact_native_stack_recovery_v3 import atomic

CONTROL=ROOT/'data/derived/compact_nonzero_native_supervision_20261029_v1'


def main():
    prep=verify_preparation();require(not CONTROL.exists() and not OUT.exists() and not ACCEPTED.exists(),'Refuse duplicate owner or retry')
    CONTROL.mkdir();state=dict(owner_pid=os.getpid(),status='running',stage='full4tx_native_execution')
    atomic(CONTROL/'state.json',state)
    files={str(PREPORT):digest(PREPORT),str(Path(__file__).resolve()):digest(__file__)}
    jobs=[('full4tx_native_execution','run_compact_nonzero_native_rtl_v1.py'),('independent_audit','check_compact_nonzero_native_rtl_v1.py')]
    for phase,name in jobs:files[str(ROOT/'scripts'/name)]=digest(ROOT/'scripts'/name)
    atomic(CONTROL/'plan.json',dict(files=files,output=str(ACCEPTED),trial=str(OUT),jobs=jobs))
    try:
        for phase,name in jobs:
            for p,h in files.items():require(digest(p)==h,'Supervised source changed')
            state.update(stage=phase);atomic(CONTROL/'state.json',state);command=['python3',str(ROOT/'scripts'/name)];start=time.monotonic()
            with (CONTROL/(phase+'.log')).open('x') as f:
                child=subprocess.Popen(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;atomic(CONTROL/'state.json',state);code=child.wait()
            atomic(CONTROL/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(CONTROL/(phase+'.log'))))
            require(code==0,'Failed '+phase+'; no retry')
        result=json.loads(ACCEPTED.read_text());require(result['rtl_verified'] and result['status']=='compact_nonzero_native_full4tx_full44_original_DUT_and_C_oracle_verified','Unexpected final audit')
        state.update(status='complete',stage='independently_audited');atomic(CONTROL/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));atomic(CONTROL/'state.json',state);raise


if __name__=='__main__':main()
