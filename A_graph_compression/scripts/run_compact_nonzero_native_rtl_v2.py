#!/usr/bin/env python3
"""One full4tx native trial with verified nonzero pointers and address wrappers."""
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import time
from compact_nonzero_native_contract_v2 import *
from run_compact_native_stack_recovery_v3 import atomic


def stop(child):
    try: os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError: pass
    try: child.wait(timeout=15)
    except subprocess.TimeoutExpired:
        try: os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        child.wait()


def observe_limits(child,phase):
    pending=[child.pid]; seen=set()
    while pending:
        pid=pending.pop()
        if pid in seen: continue
        seen.add(pid); proc=Path('/proc')/str(pid)
        try:
            for t in (proc/'task').iterdir():
                try: pending.extend(map(int,(t/'children').read_text().split()))
                except (FileNotFoundError,ProcessLookupError): pass
            args=(proc/'cmdline').read_bytes().split(b'\0'); name=Path(os.fsdecode(args[0])).name
            expected={'elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase]
            if name != expected: continue
            as_expected=(COMPILER_AS,COMPILER_AS) if phase=='elaborate' else (RUNTIME_AS,RUNTIME_AS)
            require(resource.prlimit(pid,resource.RLIMIT_AS)==as_expected,'Actual AS differs')
            require(resource.prlimit(pid,resource.RLIMIT_STACK)==(STACK,STACK),'Actual stack differs')
            require(resource.prlimit(pid,resource.RLIMIT_CORE)==(0,0),'Actual core differs')
            return dict(pid=pid,cwd=os.readlink(proc/'cwd'),command=b' '.join(args).decode(),
                        start_ticks=(proc/'stat').read_text().rsplit(')',1)[1].split()[19],
                        address_space=list(as_expected),stack=[STACK,STACK],core=[0,0],limits=(proc/'limits').read_text())
        except (FileNotFoundError,ProcessLookupError): pass
    return None


def main():
    preparation=verify_preparation()
    require(not OUT.exists() and not ACCEPTED.exists(),'Refuse restart/overwrite')
    start_memory=observe()
    OUT.mkdir(); state=dict(owner_pid=os.getpid(),status='running',stage='copy_full_inputs')
    atomic(OUT/'state.json',state)
    child=None
    try:
        for relative,row in preparation['manifest'].items():
            require(abort_reason(start_memory,observe()) is None,'New OOM event during input copy')
            target=OUT/'sim'/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(row['source'],target)
            require(digest(target)==row['sha256'],'Copied full input differs')
        (OUT/'sim/tv/rtldatafile').mkdir()
        (OUT/'bounded.tcl').write_text('run 10 sec\nputs COMPACT_NONZERO_NATIVE_BOUNDED_RETURNED\nquit\n')
        plan=dict(preparation=str(PREPORT),preparation_sha256=digest(PREPORT),commands=commands(),
                  startup_memory=start_memory,startup_gate_removed_by_user=True,free_memory_gate_removed_by_user=True,resource_policy=POLICY,transactions=4,pointers=44,models=30,
                  driver_sha256=digest(__file__),bounded_tcl_sha256=digest(OUT/'bounded.tcl'),
                  environment=dict(LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1',A_BATCH_RTL_SNAPSHOT_PREFIX=str(OUT/'rtl')))
        atomic(OUT/'plan.json',plan)
        env={**os.environ,**plan['environment']}
        for job in plan['commands']:
            phase=job['phase'];state.update(stage=phase);atomic(OUT/'state.json',state)
            begin=observe();require(abort_reason(start_memory,begin) is None,'New OOM event before phase')
            started=time.monotonic();aborted=False;trigger=None;minimum=begin['raw_free_bytes'];observed=None;last_sample=0
            with (OUT/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                while child.poll() is None:
                    if observed is None:
                        observed=observe_limits(child,phase)
                        if observed: atomic(OUT/(phase+'.actual_limits.json'),observed)
                    now=observe();minimum=min(minimum,now['raw_free_bytes'])
                    if time.monotonic()-last_sample>=30:
                        atomic(OUT/'resource_observation.json',dict(phase=phase,observation=now,actual_limits=observed));last_sample=time.monotonic()
                    reason=abort_reason(start_memory,now)
                    if reason is not None:
                        aborted=True;trigger=dict(reason=reason,observation=now);stop(child);break
                    time.sleep(1)
                code=child.wait();child=None
            final_memory=observe()
            if abort_reason(start_memory,final_memory) is not None and not aborted:
                aborted=True;trigger=dict(reason=abort_reason(start_memory,final_memory),observation=final_memory)
            log=OUT/(phase+'.log');text=log.read_text(errors='replace')
            receipt=dict(**job,exit_code=code,resource_abort=aborted,resource_abort_observation=trigger,
                         minimum_observed_raw_free_bytes=minimum,start_memory=begin,end_memory=final_memory,resource_policy=POLICY,
                         elapsed_seconds=time.monotonic()-started,log_sha256=digest(log))
            atomic(OUT/(phase+'.receipt.json'),receipt)
            require(code==0 and not aborted and not any(e in text for e in ERRORS),'Failed '+phase)
            require(observed is not None,'Actual phase process limits not captured')
            if phase=='rtl': require(re.search(r'RTL Simulation :\s*4 / 4',text) is not None,'Incomplete4tx')
            if phase=='postcheck': require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and 'SEARCH_BATCH_PASS mode=1' in text,'Original C oracle missing')
        for i in range(4):
            actual=OUT/f'rtl_1_{i}.bin';golden=BASE/f'compressed_batch_compact_cosim_setup/hls_1_{i}.bin'
            require(actual.stat().st_size==golden.stat().st_size==946498280 and digest(actual)==digest(golden),'Full44 snapshot differs')
        state.update(status='complete',stage='full4tx_original_postcheck_complete_independent_audit_pending')
        atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None: stop(child)
        state.update(status='failed',error=str(exc),failure_memory=observe());atomic(OUT/'state.json',state);raise


if __name__=='__main__': main()
