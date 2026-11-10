#!/usr/bin/env python3
"""Record actual first full native worker and concurrent RTL, without claiming acceptance."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import resource
from training_order_control_contract_v1 import *
from owned_sim_resource_policy_v1 import observe
from supervise_search_axi_dpi_v3 import atomic,identity

DEST=ROOT/'data/derived/training_order_control_launch_20261029_v1'
RESULT=ROOT/'results/training_order_control_launch_20261029_v1.json'


def check_actual(path):
    recorded=json.loads(path.read_text());owner=recorded['owner'];actual=identity(owner['pid'])
    require(actual==owner,'Recorded launch owner changed: '+str(path))
    argv=[os.fsdecode(a) for a in (Path('/proc')/str(owner['pid'])/'cmdline').read_bytes().split(b'\0') if a]
    require(argv==recorded['argv'] and resource.prlimit(owner['pid'],resource.RLIMIT_AS)==(AS_BYTES,)*2 and resource.prlimit(owner['pid'],resource.RLIMIT_CORE)==(0,0) and os.sched_getaffinity(owner['pid'])=={CPU},'Wrong actual launched worker/native limits')
    return recorded


def main():
    require(not DEST.exists() and not RESULT.exists(),'Refuse overwrite')
    control=json.loads((CONTROL/'state.json').read_text());state=json.loads((OUT/'state.json').read_text())
    require(control['status']=='running' and control['stage']=='six_complete_permutations' and state['status']=='running' and state['stage']=='full_worker','Supplemental native not running')
    require((state['block'],state['position'],state['completed_workers'],state['completed_blocks'])==(0,0,0,0),'Different launch phase; inspect before recording')
    owner=identity(control['owner_pid']);driver=identity(state['owner_pid'])
    require(owner and driver and control['child_pid']==state['owner_pid'],'Missing owner/driver')
    require(resource.prlimit(driver['pid'],resource.RLIMIT_AS)==(AS_BYTES,)*2 and os.sched_getaffinity(driver['pid'])=={CPU},'Wrong actual driver resources')
    block=OUT/'block_000';worker=check_actual(block/'worker_000.actual_limits.json');native=check_actual(block/'worker_000.native_limits.json')
    require(state['child_pid']==worker['owner']['pid'],'Different full worker')
    native_submission=json.loads((block/'worker_000/native.submission.json').read_text())
    require(native_submission['owner_pid']==worker['owner']['pid'] and native_submission['child_pid']==native['owner']['pid'],'Different native process tree')
    plan=json.loads((OUT/'plan.json').read_text());require(plan['block_orders']==schedule() and state['condition']==plan['conditions'][schedule()[0][0]],'Different frozen execution order')
    files={}
    preparation=json.loads(PREPARATION.read_text())
    require(preparation['original_worker_sha256']==digest(DRIVER) and preparation['original_block_checker_sha256']==digest(BLOCK_CHECKER),'Original full worker/checker changed')
    inner=json.loads((block/'plan.json').read_text())
    for name,h in inner['expected_inputs']['csr'].items():
        p=block/'worker_000'/name;require(digest(p)==h,'First worker generated incomplete/different original input');files[str(p)]=h
    native_rtl=Path('/tmp/A_graph_compression_recovery_20261025_v1/compact_nonzero_native_rtl_v2')
    rtl_record=json.loads((native_rtl/'rtl.actual_limits.json').read_text());rtl=identity(rtl_record['pid'])
    require(rtl and all(rtl[k]==rtl_record[k] for k in ['pid','start_ticks','command','cwd']),'Original native RTL identity changed')
    DEST.mkdir();observation=DEST/'observation.json'
    atomic(observation,dict(observed_utc=datetime.now(timezone.utc).isoformat(),supervisor=owner,driver=driver,worker=worker,native=native,concurrent_original_rtl=rtl,memory=observe(),control_state=control,driver_state=state))
    for p in [observation,PREPARATION,CONTROL/'plan.json',OUT/'plan.json',block/'plan.json',block/'worker_000.actual_limits.json',block/'worker_000.native_limits.json',block/'worker_000.submission.json',block/'worker_000/native.submission.json',Path(__file__).resolve(),ROOT/'scripts/experiment_status_v19.py']:
        files[str(p)]=digest(p)
    for p,h in files.items():require(digest(p)==h,'Changed launch evidence')
    atomic(RESULT,dict(status='supplemental_six_permutation_first_full_cpu_worker_native_exec_observed_live',files=files,supervisor_pid=owner['pid'],driver_pid=driver['pid'],worker_pid=worker['owner']['pid'],native_pid=native['owner']['pid'],cpu=CPU,process_as_bytes=AS_BYTES,orders=schedule(),planned_workers=18,completed_workers=0,completed_blocks=0,
         original_worker_unchanged=True,original_block_checker_unchanged=True,final_acceptance=False,full_experiment_complete=False,
         limits=['Launch-time process identity/limits and first generated input equivalence only; no completed routing output or performance result.',
                 'All six orders remain required, followed by original full block oracles and independent18-worker audit.',
                 'Original native RTL is concurrently live; shared CPU/memory/cache effects are not isolated.',
                 'Original7-block results and original9 requirements/8 variants remain unchanged.']))
    print(RESULT)

if __name__=='__main__':main()
