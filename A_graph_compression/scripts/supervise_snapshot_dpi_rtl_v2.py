#!/usr/bin/env python3
"""Run original30 snapshot transactions after the existing full44 batch chain passes."""
import json,os,subprocess,sys,time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic,identity
ROOT=Path(__file__).resolve().parents[1]
def main():
    upstream=ROOT/'data/derived/compressed_bus64_dpi_supervision_20261025_v6'
    previous=json.loads((upstream/'state.json').read_text());owner=identity(previous['owner_pid'])
    require(owner and 'supervise_compressed_bus64_dpi_rtl_v6.py' in owner['command'],'Original full44 batch owner missing; reconcile')
    out=ROOT/'data/derived/snapshot_dpi_supervision_20261025_v2';out.mkdir(exist_ok=False)
    driver=ROOT/'scripts/run_snapshot_dpi_rtl_v2.py';checker=ROOT/'scripts/check_snapshot_dpi_rtl_v2.py'
    paths=[driver,checker,Path(__file__).resolve(),upstream/'plan.json',ROOT/'scripts/resident_snapshot_rtl_contract.py',ROOT/'scripts/snapshot_dpi_output_oracle_v1.py',ROOT/'results/snapshot_dpi_storage_preflight_audit_20261025_v1.json',ROOT/'data/derived/snapshot_dpi_models_preflight_20261025_v1/plan.json']
    files={str(p):digest(p) for p in paths}
    atomic(out/'plan.json',dict(upstream_owner=owner,files=files,transactions=30,pointers=13,minimum_raw_free_bytes=168*1024**3,per_process_address_space_limit_bytes=144*1024**3,core_dump_limit_bytes=0,policy='Single original full30 snapshot execution then independent audit; no scope reduction or automatic retry'))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_existing_full44_batch_independent_acceptance');atomic(out/'state.json',state)
    try:
        while identity(owner['pid'])==owner:time.sleep(30)
        previous=json.loads((upstream/'state.json').read_text())
        require(previous['status']=='complete' and previous['stage']=='full44_bus64_batch_dpi_rtl_independently_verified','Full44 prerequisite did not pass')
        gate=ROOT/'results/compressed_bus64_dpi_rtl_audit_20261025_v1.json'
        require(digest(gate)==previous['report_sha256'],'Changed accepted full44 prerequisite')
        state['stage']='waiting_cgroup_admission_for_full30_snapshot';atomic(out/'state.json',state);cg=Path('/sys/fs/cgroup')
        while int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())<168*1024**3:time.sleep(30)
        bundle=Path('/tmp/A_graph_compression_recovery_20261025_v1/snapshot_dpi_rtl_v2');result=ROOT/'results/snapshot_dpi_rtl_audit_20261025_v1.json'
        require(not bundle.exists() and not result.exists(),'Existing snapshot attempt/report; do not duplicate')
        for phase,command in [('full30_snapshot_rtl',[sys.executable,str(driver)]),('independent_final_audit',[sys.executable,str(checker),'--bundle',str(bundle),'--output',str(result)])]:
            for p,h in files.items():require(digest(p)==h,'Changed scheduled snapshot input')
            state['stage']=phase;atomic(out/'state.json',state);start=time.monotonic()
            with (out/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;atomic(out/'state.json',state);code=child.wait()
            atomic(out/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/(phase+'.log'))))
            require(code==0,'Full30 snapshot phase failed '+phase+'; preserve evidence')
        accepted=json.loads(result.read_text());require(accepted['transactions']==30 and accepted['rtl_verified'],'Full30 independent result missing')
        state.update(status='complete',stage='full30_snapshot_dpi_independently_verified',report=str(result),report_sha256=digest(result));atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
