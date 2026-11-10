#!/usr/bin/env python3
"""Audit the single existing full-depth compact global64 setup, never rerun it."""
import json,os,subprocess,time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_compressed_batch_hls import identity
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    bundle=BASE/'compressed_batch_compact_bus64_cosim_setup';out=bundle/'audit_supervisor';out.mkdir(exist_ok=False)
    original=json.loads((bundle/'state.json').read_text());pid=original['owner_pid'];fingerprint=identity(pid) if original['status']=='running' else None
    if fingerprint:require('prepare_compressed_batch_compact_bus64_cosim.py' in fingerprint['command'],'Different setup owner')
    names=['audit_compressed_compact_bus64_cosim_model_capacity.py','audit_compressed_compact_bus64_cosim_allocations.py','audit_compressed_compact_bus64_cosim_binary_transactions.py']
    files={str(ROOT/'scripts'/n):digest(ROOT/'scripts'/n) for n in names};files[str(Path(__file__).resolve())]=digest(__file__)
    atomic(out/'plan.json',dict(files=files,observed_owner=pid,identity=fingerprint))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_existing_setup');atomic(out/'state.json',state)
    try:
        while True:
            current=json.loads((bundle/'state.json').read_text());require(current['owner_pid']==pid,'Setup owner changed')
            if current['status']!='running':break
            require(identity(pid)==fingerprint,'Setup owner disappeared without terminal state');time.sleep(10)
        require(current['status']=='complete','Original setup failed')
        for p,h in files.items():require(digest(p)==h,'Checker changed')
        state['stage']='independent_capacity_allocation_transaction_audits';atomic(out/'state.json',state)
        for name in names:
            cmd=['python3',str(ROOT/'scripts'/name)];log=out/(name+'.log')
            with log.open('x') as f:code=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
            atomic(out/(name+'.receipt.json'),dict(command=cmd,exit_code=code,log_sha256=digest(log)));require(code==0,'Setup audit failed '+name)
        setup=json.loads((bundle/'setup.json').read_text());require(setup['mode']=='compact' and setup['transactions']==4 and setup['rtl_simulated'] is False,'Wrong scope')
        files.update(setup['files']);files[str(bundle/'setup.json')]=digest(bundle/'setup.json')
        for suffix in ['model_capacity','allocations','binary_transactions']:
            p=ROOT/'results'/('compressed_batch_compact_bus64_cosim_'+suffix+'_20261025_v1.json');r=json.loads(p.read_text());files.update(r['files']);files[str(p)]=digest(p)
        for p,h in files.items():require(digest(p)==h,'Changed final setup evidence')
        target=ROOT/'results/compressed_batch_compact_bus64_full_depth_cosim_setup_20261025_v1.json';require(not target.exists(),'Refuse overwrite')
        atomic(target,dict(status='compact_global64_full44_full4tx_setup_capacity_allocations_and_vectors_independently_verified_rtl_pending',files=files,transactions=4,pointers=44,models=30,rtl_simulated=False,limits=['Generated setup only; no new xelab, RTL, physical or board success inferred']))
        state.update(status='complete',stage='independently_audited');atomic(out/'state.json',state)
    except BaseException as e:
        state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
