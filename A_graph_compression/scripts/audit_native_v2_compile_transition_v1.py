#!/usr/bin/env python3
"""Freeze completed native compilation and an observed RTL transition, not acceptance."""
import json
from pathlib import Path
import re
import resource
import time
from compact_nonzero_native_contract_v2 import ROOT,OUT,PREPORT,COMPILER_AS,RUNTIME_AS,STACK,commands,ERRORS
from check_vitis_kernel import digest,require
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
from supervise_search_axi_dpi_v3 import atomic,identity

DEST=ROOT/'data/derived/native_v2_compile_transition_20261029_v1'
RESULT=ROOT/'results/native_v2_compile_transition_audit_20261029_v1.json'

def main():
    require(not DEST.exists() and not RESULT.exists(),'Refuse overwrite')
    plan=json.loads((OUT/'plan.json').read_text());receipt=json.loads((OUT/'elaborate.receipt.json').read_text())
    log=(OUT/'elaborate.log').read_text();limits=json.loads((OUT/'elaborate.actual_limits.json').read_text())
    expected=commands()[0]
    require(all(receipt[k]==v for k,v in expected.items()) and plan['commands']==commands(),'Different actual compiler command')
    require(plan['preparation_sha256']==digest(PREPORT),'Changed prepared contract')
    require(receipt['exit_code']==0 and receipt['resource_abort'] is False and receipt['resource_abort_observation'] is None and receipt['log_sha256']==digest(OUT/'elaborate.log'),'Unsuccessful or changed compiler receipt')
    require(receipt['resource_policy']==POLICY and abort_reason(receipt['start_memory'],receipt['end_memory']) is None,'Wrong compiler resource policy/OOM')
    require('Built simulation snapshot search_batch_trace_top_v2' in log and not any(e in log for e in ERRORS),'No successful compiler snapshot')
    require(limits['address_space']==[COMPILER_AS]*2 and limits['stack']==[STACK]*2 and limits['core']==[0,0] and limits['cwd']==expected['cwd'] and Path(limits['command'].split()[0]).name=='xelab','Wrong observed compiler limits')
    require(identity(limits['pid']) is None,'Completed compiler PID is live/reused; reconcile before freezing')
    rss=int(re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',log)[1])
    tool_peak=int(re.search(r'XELAB Memory Usage: \d+ KB \(Peak: (\d+) KB\)',log)[1])
    state=json.loads((OUT/'state.json').read_text());kernel=json.loads((OUT/'rtl.actual_limits.json').read_text())
    actual=identity(kernel['pid'])
    require(state['status']=='running' and state['stage']=='rtl' and actual and all(actual[k]==kernel[k] for k in ['pid','start_ticks','command','cwd']),'RTL transition owner mismatch')
    require(resource.prlimit(kernel['pid'],resource.RLIMIT_AS)==(RUNTIME_AS,)*2 and resource.prlimit(kernel['pid'],resource.RLIMIT_STACK)==(STACK,)*2 and resource.prlimit(kernel['pid'],resource.RLIMIT_CORE)==(0,0),'Actual kernel limits differ')
    memory=observe();require(abort_reason(receipt['start_memory'],memory) is None,'New OOM since compilation')
    DEST.mkdir();files={}
    for name in ['plan.json','elaborate.receipt.json','elaborate.log','elaborate.actual_limits.json','rtl.actual_limits.json']:
        original=OUT/name;copy=DEST/name;copy.write_bytes(original.read_bytes())
        require(digest(copy)==digest(original),'Changed phase evidence copy');files[str(copy)]=digest(copy);files[str(original)]=digest(original)
    # Active state/log get snapshots; they are never frozen in place or treated as terminal.
    for name in ['state.json','rtl.log']:
        copy=DEST/('observed_'+name);copy.write_bytes((OUT/name).read_bytes());files[str(copy)]=digest(copy)
    observation=DEST/'observation.json';atomic(observation,dict(observed_unix=time.time(),owner=actual,driver_state=state,memory=memory,actual_limits=kernel))
    files[str(observation)]=digest(observation)
    for path in [Path(__file__).resolve(),PREPORT,ROOT/'scripts/compact_nonzero_native_contract_v2.py',ROOT/'scripts/owned_sim_resource_policy_v1.py']:files[str(path)]=digest(path)
    progress=re.findall(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"',(DEST/'observed_rtl.log').read_text())
    atomic(RESULT,dict(status='native_full44_compilation_complete_and_original_rtl_started_not_accepted',files=files,compiler_exit_code=0,compiler_elapsed_seconds=receipt['elapsed_seconds'],compiler_as_bytes=COMPILER_AS,maximum_resident_set_kib=rss,xelab_reported_peak_kb=tool_peak,minimum_observed_raw_free_bytes=receipt['minimum_observed_raw_free_bytes'],resource_policy=POLICY,oom_events_before=receipt['start_memory']['events'],oom_events_after=receipt['end_memory']['events'],kernel_pid=kernel['pid'],runtime_as_bytes=RUNTIME_AS,last_logged_progress=list(map(int,progress[-1])) if progress else None,rtl_verified=False,full_experiment_complete=False,limitations=['Compilation success and instantaneous kernel identity/limits only; full4 transactions, original C postcheck and four complete snapshots still await independent acceptance.','GNU time maximum RSS and tool peak are distinct measurements; per-process AS is not aggregate cgroup memory.','No complete source/output re-audit here; the final native checker remains mandatory.']))
    for path,h in files.items():require(digest(path)==h,'Changed frozen transition evidence')
    print(RESULT)

if __name__=='__main__':main()
