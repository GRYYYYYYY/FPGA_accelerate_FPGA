#!/usr/bin/env python3
"""Run one full4tx encoded graph mode with typed serial prerequisites."""
import argparse
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import time
from paired_binary_nonzero_contract_v3 import *
from binary_nonzero_full44_prerequisites_v2 import validate
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import stop


def observe(child,phase):
    pending=[child.pid];seen=set()
    while pending:
        pid=pending.pop()
        if pid in seen:continue
        seen.add(pid);proc=Path('/proc')/str(pid)
        try:
            for t in (proc/'task').iterdir():
                try:pending.extend(map(int,(t/'children').read_text().split()))
                except (FileNotFoundError,ProcessLookupError):pass
            args=(proc/'cmdline').read_bytes().split(b'\0')
            if Path(os.fsdecode(args[0])).name!={'xsc':'xsc','elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase]:continue
            require(resource.prlimit(pid,resource.RLIMIT_AS)==(AS_BYTES,AS_BYTES) and resource.prlimit(pid,resource.RLIMIT_STACK)==(STACK,STACK) and resource.prlimit(pid,resource.RLIMIT_CORE)==(0,0),'Actual process limits differ')
            require(os.sched_getaffinity(pid)=={122},'Actual CPU placement differs')
            return dict(pid=pid,start_ticks=(proc/'stat').read_text().rsplit(')',1)[1].split()[19],command=b' '.join(args).decode(),
                        cwd=os.readlink(proc/'cwd'),limits=(proc/'limits').read_text(),address_space=[AS_BYTES,AS_BYTES],stack=[STACK,STACK],core=[0,0],cpu=[122])
        except (FileNotFoundError,ProcessLookupError):pass
    return None


def run(mode):
    bindings=validate(mode);entry,prepared_files=prepared(mode);c=config(mode);out=c['trial']
    require(not out.exists() and not c['output'].exists(),'Refuse restart/overwrite')
    start_memory=memory()
    out.mkdir();state=dict(owner_pid=os.getpid(),status='running',stage='copy_full_inputs',graph_mode=mode);atomic(out/'state.json',state);child=None
    try:
        files={**prepared_files,**bindings,str(PREPORT):digest(PREPORT)}
        for relative,row in entry['manifest'].items():
            require(abort_reason(start_memory,memory()) is None,'New OOM event during input copy')
            p=out/'sim'/relative;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['source'],p)
            require(digest(p)==row['sha256'],'Copied complete input differs');files[str(p)]=digest(p)
        (out/'sim/tv/rtldatafile').mkdir()
        bounded=out/'bounded.tcl';bounded.write_text('run 10 sec\nputs FULL44_NONZERO_DPI_BOUNDED_RETURNED\nquit\n');files[str(bounded)]=digest(bounded)
        plan=dict(files=files,commands=commands(mode),preparation_sha256=digest(PREPORT),graph_mode=mode,transactions=4,ports=44,models=30,pages=4,
                  encoded_modules=c['encoded_modules'],candidate_encoding_changed=True,native_cycle_parity_claimed=False,pointer_address_offset=4096,
                  address_space_bytes=AS_BYTES,stack_bytes=STACK,core_bytes=0,resource_policy=POLICY,free_memory_gate_removed_by_user=True,startup_gate_removed_by_user=True,startup_memory=start_memory)
        atomic(out/'plan.json',plan);env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'rtl')}
        for job in plan['commands']:
            phase=job['phase'];state.update(stage=phase);atomic(out/'state.json',state);begin=memory()
            require(abort_reason(start_memory,begin) is None,'New OOM event before phase')
            start=time.monotonic();aborted=False;trigger=None;minimum=begin['raw_free_bytes'];limits=None;last_sample=0
            with (out/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(out/'state.json',state)
                while child.poll() is None:
                    if limits is None:
                        limits=observe(child,phase)
                        if limits:atomic(out/(phase+'.actual_limits.json'),limits)
                    now=memory();minimum=min(minimum,now['raw_free_bytes'])
                    if time.monotonic()-last_sample>=30:
                        atomic(out/'resource_observation.json',dict(phase=phase,observation=now,actual_limits=limits));last_sample=time.monotonic()
                    reason=abort_reason(start_memory,now)
                    if reason is not None:aborted=True;trigger=dict(reason=reason,observation=now);stop(child);break
                    time.sleep(1)
                code=child.wait();child=None
            final_memory=memory()
            if abort_reason(start_memory,final_memory) is not None and not aborted:
                aborted=True;trigger=dict(reason=abort_reason(start_memory,final_memory),observation=final_memory)
            lp=out/(phase+'.log');text=lp.read_text(errors='replace')
            receipt=dict(**job,exit_code=code,resource_abort=aborted,resource_abort_observation=trigger,minimum_observed_raw_free_bytes=minimum,
                         start_memory=begin,end_memory=final_memory,resource_policy=POLICY,elapsed_seconds=time.monotonic()-start,log_sha256=digest(lp),plan_sha256=digest(out/'plan.json'))
            atomic(out/(phase+'.receipt.json'),receipt)
            require(code==0 and not aborted and not any(e in text for e in ERRORS),'Failed '+phase)
            if phase in ['elaborate','rtl']:require(limits is not None,'Actual compiler/kernel limits missing')
            if phase=='rtl':require(re.search(r'RTL Simulation :\s*4 / 4',text) and text.splitlines().count('FULL44_NONZERO_DPI_BOUNDED_RETURNED')==1,'Incomplete4tx')
            if phase=='postcheck':require('SEARCH_BATCH_PASS mode='+str(mode) in text and text.splitlines().count(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4')==1,'Original C oracle missing')
        for i in range(4):
            actual=out/f'rtl_{mode}_{i}.bin';golden=c['golden']/f'hls_{mode}_{i}.bin'
            require(actual.stat().st_size==golden.stat().st_size==946498280 and digest(actual)==digest(golden),'Complete full44 snapshot differs')
        perf=out/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml'
        cycles=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
        require([i for i,v in cycles]==list(range(4)) and all(v>0 for i,v in cycles),'Missing positive cycles')
        state.update(status='complete',stage='binary_nonzero_full44_original_C_and_snapshots_complete_independent_audit_pending',cycles=[v for i,v in cycles]);atomic(out/'state.json',state)
    except BaseException as exc:
        if child is not None:stop(child)
        state.update(status='failed',error=str(exc),failure_memory=memory());atomic(out/'state.json',state);raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',type=int,choices=[0,1],required=True);run(p.parse_args().mode)
