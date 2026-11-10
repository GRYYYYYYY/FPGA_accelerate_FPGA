"""Run one existing full-scope XSim phase with finite AS and no free-memory gate."""
import os
from pathlib import Path
import resource
import subprocess
import time
from check_vitis_kernel import digest,require
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
from run_compact_nonzero_native_rtl_v2 import stop
from run_compact_native_stack_recovery_v3 import atomic


def actual_limits(child,phase,cpu):
    pending=[child.pid];seen=set()
    while pending:
        pid=pending.pop()
        if pid in seen:continue
        seen.add(pid);proc=Path('/proc')/str(pid)
        try:
            for task in (proc/'task').iterdir():
                try:pending.extend(map(int,(task/'children').read_text().split()))
                except (FileNotFoundError,ProcessLookupError):pass
            args=(proc/'cmdline').read_bytes().split(b'\0')
            if Path(os.fsdecode(args[0])).name!={'xsc':'xsc','elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase]:continue
            for limit,expected in [(resource.RLIMIT_AS,64*1024**3),(resource.RLIMIT_STACK,64*1024**2),(resource.RLIMIT_CORE,0)]:
                require(resource.prlimit(pid,limit)==(expected,expected),'Actual process resource limit differs')
            require(os.sched_getaffinity(pid)=={cpu},'Different actual phase CPU')
            return dict(pid=pid,start_ticks=(proc/'stat').read_text().rsplit(')',1)[1].split()[19],command=b' '.join(args).decode(),
                        cwd=os.readlink(proc/'cwd'),address_space=[64*1024**3]*2,stack=[64*1024**2]*2,core=[0,0],cpu=[cpu])
        except (FileNotFoundError,ProcessLookupError):pass
    return None


def run_phase(out,phase,command,cwd,state,initial,env,cpu):
    state['stage']=phase;atomic(out/'state.json',state)
    begin=observe();require(abort_reason(initial,begin) is None,'New OOM event before phase')
    child=None;started=time.monotonic();trigger=None;limits=None;last_sample=0
    minimum=begin['raw_free_bytes']
    try:
        with (out/(phase+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            state['child_pid']=child.pid;atomic(out/'state.json',state)
            while child.poll() is None:
                if limits is None:
                    limits=actual_limits(child,phase,cpu)
                    if limits:atomic(out/(phase+'.actual_limits.json'),limits)
                now=observe();minimum=min(minimum,now['raw_free_bytes']);reason=abort_reason(initial,now)
                if time.monotonic()-last_sample>=30:
                    atomic(out/'resource_observation.json',dict(phase=phase,observation=now,actual_limits=limits));last_sample=time.monotonic()
                if reason is not None:trigger=dict(reason=reason,observation=now);stop(child);break
                time.sleep(1)
            code=child.wait()
            if code!=0:stop(child)
            child=None
        end=observe();reason=abort_reason(initial,end)
        if reason is not None and trigger is None:trigger=dict(reason=reason,observation=end)
        lp=out/(phase+'.log')
        atomic(out/(phase+'.receipt.json'),dict(command=command,cwd=str(cwd),exit_code=code,
            resource_admission_abort=trigger is not None,resource_abort_observation=trigger,resource_policy=POLICY,
            start_memory=begin,end_memory=end,minimum_observed_raw_free_bytes=minimum,
            elapsed_seconds=time.monotonic()-started,log_sha256=digest(lp),plan_sha256=digest(out/'plan.json')))
        require(code==0 and trigger is None,'Full-scope phase failed: '+phase)
        if phase in ['elaborate','rtl']:require(limits is not None,'Actual compiler/kernel limits missing')
        return lp.read_text(errors='replace')
    finally:
        if child is not None:stop(child)
