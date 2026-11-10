#!/usr/bin/env python3
"""Single owner for complete supplemental CPU order control; stop on new actual OOM."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from training_order_control_contract_v1 import *
from owned_sim_resource_policy_v1 import observe,abort_reason
from supervise_search_axi_dpi_v3 import atomic,identity


def stop_group(child):
    # Popen created this session; every original worker/native/checker inherits it.
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    deadline=time.monotonic()+8
    while time.monotonic()<deadline:
        child.poll()
        try:os.killpg(child.pid,0)
        except ProcessLookupError:break
        time.sleep(.1)
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait(timeout=5)


def actual_limits(child,expected):
    actual=identity(child.pid)
    if not actual:return None
    try:argv=[os.fsdecode(a) for a in (Path('/proc')/str(child.pid)/'cmdline').read_bytes().split(b'\0') if a]
    except (FileNotFoundError,ProcessLookupError):return None
    if argv!=expected:return None
    require(resource.prlimit(child.pid,resource.RLIMIT_AS)==(AS_BYTES,AS_BYTES) and resource.prlimit(child.pid,resource.RLIMIT_CORE)==(0,0) and os.sched_getaffinity(child.pid)=={CPU},'Wrong actual guarded process limits')
    return dict(owner=actual,argv=argv,address_space=[AS_BYTES]*2,core=[0,0],cpu=[CPU])


def run_phase(stage,command,initial,control,state,observer=observe):
    start_memory=observer();require(abort_reason(initial,start_memory) is None,'New OOM before phase')
    state.update(stage=stage);atomic(control/'state.json',state)
    child=None;trigger=None;limits=None;start=time.monotonic();last=0
    try:
        with (control/(stage+'.log')).open('x') as stream:
            child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:os.sched_setaffinity(0,{CPU}))
            state['child_pid']=child.pid;atomic(control/'state.json',state)
            while child.poll() is None:
                if limits is None:limits=actual_limits(child,command[4:])
                memory=observer();reason=abort_reason(initial,memory)
                if time.monotonic()-last>=30:
                    atomic(control/'resource_observation.json',dict(stage=stage,memory=memory,actual_owner_limits=limits));last=time.monotonic()
                if reason is not None:trigger=dict(reason=reason,memory=memory);stop_group(child);break
                time.sleep(1)
            code=child.wait()
            if code!=0:stop_group(child)
            child=None
        end=observer();reason=abort_reason(initial,end)
        if reason is not None and trigger is None:trigger=dict(reason=reason,memory=end)
        atomic(control/(stage+'.receipt.json'),dict(command=command,exit_code=code,resource_abort=trigger is not None,resource_abort_observation=trigger,resource_policy=POLICY,
             start_memory=start_memory,end_memory=end,actual_owner_limits=limits,elapsed_seconds=time.monotonic()-start,plan_sha256=digest(control/'plan.json'),log_sha256=digest(control/(stage+'.log'))))
        require(code==0 and trigger is None and limits is not None,'Supplemental full phase failed; no retry: '+stage)
        state.pop('child_pid',None)
    finally:
        if child is not None:stop_group(child)


def main():
    proof=prepared()
    require(not any(p.exists() for p in [CONTROL,OUT,FINAL]),'Existing supplemental run; refuse duplicate')
    require(CPU in os.sched_getaffinity(0),'Original CPU unavailable')
    # Detect exact executing programs, not matches inside shell source text.
    names={'source_to_route_training_statistics_v2.py','source_to_route_with_training_v2.py','run_training_order_control_v1.py','native_site_runtime_20261023_v1'}
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            args=(proc/'cmdline').read_bytes().split(b'\0');program=Path(os.fsdecode(args[0])).name
            actual_script=Path(os.fsdecode(args[1])).name if len(args)>1 else ''
            if program.startswith('python') and actual_script=='-u' and len(args)>2:actual_script=Path(os.fsdecode(args[2])).name
            require(program not in names and actual_script not in names,'Another full CPU experiment is live; reconcile before new owner')
        except (FileNotFoundError,ProcessLookupError):pass
    prefix=['prlimit',f'--as={AS_BYTES}:{AS_BYTES}','--core=0:0','--']
    commands=[('six_complete_permutations',prefix+[sys.executable,'-u',str(ROOT/'scripts/run_training_order_control_v1.py')]),
              ('final_audit',prefix+[sys.executable,'-u',str(ROOT/'scripts/check_training_order_control_v1.py'),str(OUT),'--output',str(FINAL)])]
    initial=observe();CONTROL.mkdir();files={**proof['files'],str(PREPARATION):digest(PREPARATION)}
    atomic(CONTROL/'plan.json',dict(commands=commands,files=files,orders=schedule(),workers=18,cpu=CPU,address_space_bytes=AS_BYTES,resource_policy=POLICY,start_memory=initial,no_retry=True,original_seven_block_report=str(ORIGINAL)))
    state=dict(owner_pid=os.getpid(),status='running',stage='preflight',resource_policy=POLICY);atomic(CONTROL/'state.json',state)
    try:
        for stage,command in commands:
            verify(files);run_phase(stage,command,initial,CONTROL,state)
        report=json.loads(FINAL.read_text())
        require(report['status']==ACCEPTED and (report['completed_workers'],report['completed_blocks'])==(18,6),'Incomplete supplemental acceptance')
        state.update(status='complete',stage='six_permutation_full_workload_independently_audited',report=str(FINAL),report_sha256=digest(FINAL));atomic(CONTROL/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error));atomic(CONTROL/'state.json',state);raise

if __name__=='__main__':main()
