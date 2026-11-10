#!/usr/bin/env python3
"""Continue the single existing search-parity chain into full44 batch RTL and audit."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic,identity

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    upstream=ROOT/'data/derived/search_axi_dpi_capped_supervision_20261025_v4'
    previous=json.loads((upstream/'state.json').read_text());owner=identity(previous['owner_pid'])
    require(owner and 'supervise_search_axi_dpi_capped_replay_v4.py' in owner['command'],'Original independent parity audit owner missing; reconcile')
    out=ROOT/'data/derived/compressed_bus64_dpi_supervision_20261025_v2';out.mkdir(exist_ok=False)
    driver=ROOT/'scripts/run_compressed_bus64_dpi_rtl_v1.py';checker=ROOT/'scripts/check_compressed_bus64_dpi_rtl_v1.py'
    inputs=[driver,checker,Path(__file__).resolve(),upstream/'plan.json',ROOT/'scripts/supervise_search_axi_dpi_v3.py',
            ROOT/'results/compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json',
            ROOT/'data/derived/compressed_bus64_dpi_models_preflight_20261025_v1/plan.json',
            ROOT/'results/compressed_batch_bus64_full_depth_cosim_setup_20261025_v1.json',
            ROOT/'results/compressed_batch_bus64_cosim_allocations_20261025_v1.json']
    hashes={str(p):digest(p) for p in inputs}
    atomic(out/'plan.json',dict(upstream_owner=owner,files=hashes,required_raw_free_bytes=184*1024**3,
        policy='One run then independent audit; no restart, no reduced scope, no interference with original owned jobs'))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_existing_full_search_parity_audit')
    atomic(out/'state.json',state)
    try:
        while identity(owner['pid'])==owner:time.sleep(30)
        previous=json.loads((upstream/'state.json').read_text())
        require(previous['status']=='complete' and previous['stage']=='search_core_full_depth_dpi_replay_independently_audited','Original full search parity audit did not succeed')
        gate=ROOT/'results/search_axi_dpi_replay_audit_20261025_v3.json'
        require(previous['report_sha256']==digest(gate),'Changed independent search parity proof')
        state['stage']='waiting_cgroup_admission_for_full44_batch';atomic(out/'state.json',state)
        cg=Path('/sys/fs/cgroup')
        while True:
            maximum=int((cg/'memory.max').read_text());current=int((cg/'memory.current').read_text())
            state['memory']=dict(maximum_bytes=maximum,current_bytes=current,raw_free_bytes=maximum-current)
            atomic(out/'state.json',state)
            if maximum-current>=184*1024**3:break
            time.sleep(30)
        bundle=BASE/'compressed_batch_bus64_dpi_rtl_v1'
        result=ROOT/'results/compressed_bus64_dpi_rtl_audit_20261025_v1.json'
        require(not bundle.exists() and not result.exists(),'Existing batch attempt/report; never duplicate')
        jobs=[('full44_batch_rtl',[sys.executable,str(driver)]),
              ('independent_final_audit',[sys.executable,str(checker),'--bundle',str(bundle),'--output',str(result)])]
        for phase,command in jobs:
            for p,h in hashes.items():require(digest(p)==h,'Changed scheduled input '+p)
            state['stage']=phase;atomic(out/'state.json',state)
            with (out/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;atomic(out/'state.json',state);start=time.monotonic();code=child.wait()
            atomic(out/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/(phase+'.log'))))
            require(code==0,'Batch pipeline phase failed '+phase+'; retain original trial')
        accepted=json.loads(result.read_text())
        require(accepted['status']=='compressed_bus64_full44_four_transaction_dpi_rtl_c_postcheck_and_complete_snapshots_independently_verified','Independent full44 acceptance missing')
        state.update(status='complete',stage='full44_bus64_batch_dpi_rtl_independently_verified',report=str(result),report_sha256=digest(result))
        atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
