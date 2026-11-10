#!/usr/bin/env python3
"""Run six complete order permutations with the unchanged full worker and block oracle."""
import copy
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from training_order_control_contract_v1 import *
from real_experiment import write_new
from supervise_search_axi_dpi_v3 import atomic,identity


def capture_worker(pid,command):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        actual=identity(pid)
        argv=[os.fsdecode(a) for a in (Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0') if a] if actual else []
        if actual and argv==command:
            require(resource.prlimit(pid,resource.RLIMIT_AS)==(AS_BYTES,AS_BYTES) and resource.prlimit(pid,resource.RLIMIT_CORE)==(0,0) and os.sched_getaffinity(pid)=={CPU},'Different actual worker limits')
            return dict(owner=actual,argv=argv,address_space=[AS_BYTES]*2,core=[0,0],cpu=[CPU])
        time.sleep(.02)
    raise ValueError('Full worker exec/limits not observed')


def main():
    preparation=prepared();require(not OUT.exists() and not FINAL.exists(),'Refuse duplicate supplemental trial')
    control=json.loads((CONTROL/'state.json').read_text())
    require(control['owner_pid']==os.getppid() and control['status']=='running' and control['stage']=='six_complete_permutations','Must run under the unique prepared resource supervisor')
    require(resource.getrlimit(resource.RLIMIT_AS)==(AS_BYTES,)*2 and resource.getrlimit(resource.RLIMIT_CORE)==(0,0) and os.sched_getaffinity(0)=={CPU},'Wrong inherited execution limits')
    base=json.loads((VALIDATION/'plan.json').read_text());files=dict(preparation['execution_files']);files[str(PREPARATION)]=digest(PREPARATION)
    orders=schedule();plan=dict(owner_pid=os.getpid(),cpu=CPU,repeats=6,seed=SEED,conditions=base['jobs'],block_orders=orders,files=files,
        validation_plan=str(VALIDATION/'plan.json'),validation_audit=str(VALIDATION_AUDIT),resource_policy=POLICY,worker_as_bytes=AS_BYTES,
        original_seven_block_report=str(ORIGINAL),original_seven_block_sha256=digest(ORIGINAL),
        limitations=[s for s in base['limitations'] if not s.startswith('One full integration trial')]+[
          'Supplemental order control selected after inspecting the original seven blocks; does not replace or pool their results.',
          'All six permutations once: each condition occurs twice at each position; each pair precedes the other three times.',
          'Six fresh processes per condition; each application includes fresh input preparation and TWO complete1062-net batches.',
          'No cache flush or exclusive host; balanced order is not cold-cache control and does not remove unrelated/shared RTL workload effects.',
          'Original native algorithm, cache4096, budgets and14-instance physical site model remain unchanged.',
          'No real-device or full end-to-end FPGA claim; inherited RUSAGE_CHILDREN peaks are not native-only post-exec memory.'])
    OUT.mkdir();write_new(OUT/'plan.json',plan)
    state=dict(owner_pid=os.getpid(),status='running',stage='start',completed_workers=0,completed_blocks=0)
    atomic(OUT/'state.json',state);records=[]
    try:
        for repeat,order in enumerate(orders):
            verify(files);block=OUT/f'block_{repeat:03d}';block.mkdir()
            inner=copy.deepcopy(base);inner.update(owner_pid=os.getpid(),cpu=CPU,files=files,limitations=plan['limitations'],statistics_repeat=repeat,execution_order=order)
            write_new(block/'plan.json',inner)
            for position,index in enumerate(order):
                command=[sys.executable,'-u',str(DRIVER),'--output',str(block),'--worker',str(index)]
                log=block/f'worker_{index:03d}.log';start=time.monotonic_ns()
                with log.open('x') as stream:
                    child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
                    write_new(block/f'worker_{index:03d}.submission.json',dict(owner_pid=os.getpid(),child_pid=child.pid,command=command,cpu=CPU,execution_position=position,started_monotonic_ns=start))
                    state.update(stage='full_worker',block=repeat,position=position,condition=base['jobs'][index],child_pid=child.pid);atomic(OUT/'state.json',state)
                    write_new(block/f'worker_{index:03d}.actual_limits.json',capture_worker(child.pid,command))
                    native_observed=False
                    while child.poll() is None:
                        native_submission=block/f'worker_{index:03d}/native.submission.json'
                        if not native_observed and native_submission.exists():
                            n=json.loads(native_submission.read_text())
                            require(n['owner_pid']==child.pid,'Different native child owner')
                            write_new(block/f'worker_{index:03d}.native_limits.json',capture_worker(n['child_pid'],n['command']))
                            native_observed=True
                        time.sleep(1)
                    code=child.wait()
                finished=time.monotonic_ns()
                write_new(block/f'worker_{index:03d}.receipt.json',dict(exit_code=code,worker_process_wall_ms=(finished-start)/1e6,log_sha256=digest(log),finished_monotonic_ns=finished))
                require(code==0,'Full worker failed; no retry')
                require(native_observed,'Actual full native CPU/limits were not observed')
                state['completed_workers']+=1;state.pop('child_pid',None);atomic(OUT/'state.json',state)
                print('ORDER_CONTROL_FULL_WORKER_DONE',repeat,index,flush=True)
            workers=[dict(condition=job,report=str(block/f'worker_{i:03d}/report.json'),sha256=digest(block/f'worker_{i:03d}/report.json')) for i,job in enumerate(base['jobs'])]
            write_new(block/'report.json',dict(status='all_three_full_integration_trials_verified',plan_sha256=digest(block/'plan.json'),workers=workers))
            command=[sys.executable,'-u',str(BLOCK_CHECKER),str(block),'--output',str(block/'audit.json')]
            with (block/'audit.log').open('x') as stream:
                child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
                state.update(stage='original_full_block_audit',child_pid=child.pid);atomic(OUT/'state.json',state)
                code=child.wait()
            require(code==0,'Original complete block audit failed; no retry')
            report=json.loads((block/'audit.json').read_text());require(report['status']=='all_source_to_route_integration_trials_audited' and report['completed_workers']==3,'Partial original block audit')
            records.append(dict(repeat=repeat,audit=str(block/'audit.json'),sha256=digest(block/'audit.json')))
            state.pop('child_pid',None);state['completed_blocks']+=1;atomic(OUT/'state.json',state)
            print('ORDER_CONTROL_FULL_BLOCK_AUDITED',repeat,flush=True)
        write_new(OUT/'report.json',dict(status='all_six_order_control_blocks_audited',plan_sha256=digest(OUT/'plan.json'),blocks=records))
        state.update(status='complete',stage='all18_full_workers_and_six_original_block_audits_complete');atomic(OUT/'state.json',state)
    except BaseException as error:
        state.update(status='failed',error=str(error));atomic(OUT/'state.json',state);raise

if __name__=='__main__':main()
