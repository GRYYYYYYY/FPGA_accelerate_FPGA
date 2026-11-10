#!/usr/bin/env python3
"""Execute the new full44 native compact candidate under the original finite caps."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from check_vitis_kernel import digest,require
from check_collision_safe_batch_hls_v1 import instances
from owned_sim_resource_policy_v1 import observe,abort_reason,POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import observe_limits,stop

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
PREP=BASE/'collision_safe_native_rtl_preparation_v1'
OUT=BASE/'collision_safe_native_rtl_v1'
AUDIT=ROOT/'results/collision_safe_native_preparation_audit_20261030_v1.json'
HLS_AUDIT=ROOT/'results/collision_safe_compact_hls_audit_20261030_v1.json'
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
ERRORS=['ERROR:','Fatal:','FATAL_ERROR','runtime error:','LLVM ERROR','A_RO_WRITE_VIOLATION',
        'A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST','Simulator command interrupted',
        'engine not responding','unexpected manner']


def diagnostic_tcl(rtl,report):
    top='search_batch_trace_top_v2';root='/apatb_search_batch_trace_top_v2_top/AESL_inst_'+top
    paths={top:root}
    for parent,child in [(top,top+'_batch_worker'),(top+'_batch_worker',top+'_net_worker'),
                         (top+'_net_worker',top+'_sink_loop_worker')]:
        found=[r for r in instances((rtl/(parent+'.v')).read_text()) if r[0]==child]
        require(len(found)==1,'Unresolved diagnostic parent path '+child)
        paths[child]=paths[parent]+'/'+found[0][1]
    probes={}
    for signal in ['m_axi_input_mem_ARADDR','m_axi_input_mem_ARVALID','m_axi_input_mem_ARREADY',
                   'm_axi_input_mem_ARLEN','m_axi_input_mem_ARSIZE','root_nodes']:
        probes['top_'+signal]=root+'/'+signal
    for i,row in enumerate(report['restored_connections']):
        parent=Path(row['parent']).stem;scope=paths[parent]+'/'+row['instance']
        probes[f'connection_{i}_{row["port"]}']=scope+'/'+row['port']
        for signal in ['ap_start','ap_done']:
            probes[f'connection_{i}_{signal}']=scope+'/'+signal
    lines=['run 10 sec','puts COLLISION_SAFE_NATIVE_BOUNDED_RETURNED']
    for label,path in probes.items():
        # get_value is supported on the actual O0/no-debug snapshot; unlike
        # VCD export it does not require re-elaboration with debug enabled.
        lines += [f'if {{[llength [get_objects {{{path}}}]] == 1}} {{',
                  f' puts "A_NATIVE_VALUE {label} [get_value -radix hex {{{path}}}]"',
                  '} else {',f' puts "A_NATIVE_VALUE_MISSING {label}"','}']
    lines+=['quit']
    return '\n'.join(lines)+'\n',probes


def main():
    require(not OUT.exists(),'Refuse overwrite/duplicate native trial')
    audit=json.loads(AUDIT.read_text())
    require(audit['status']=='collision_safe_native_full44_inputs_all30_guards_all44_relocations_independently_verified',
            'New independent input gate missing')
    for n,h in audit['files'].items():require(digest(n)==h,'Changed new input gate '+n)
    preparation=json.loads((PREP/'preparation.json').read_text())
    hls=json.loads(HLS_AUDIT.read_text())
    require(hls['status']=='collision_safe_native_compact_hls_all9_dynamic_connections_and_full44_C_verified_rtl_pending',
            'New HLS gate missing')
    require((preparation['transactions'],preparation['pointers'],len(preparation['models']))==(4,44,30),'Scope changed')
    initial=observe();OUT.mkdir()
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_complete_reviewed_inputs',
               transactions=4,pointers=44,models=30,full_kernel_accepted=False)
    atomic(OUT/'state.json',state);child=None
    try:
        copied={}
        for original in (PREP/'sim').rglob('*'):
            if not original.is_file():continue
            require(abort_reason(initial,observe()) is None,'New OOM during copy')
            target=OUT/'sim'/original.relative_to(PREP/'sim');target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,target)
            checksum=digest(target);require(checksum==audit['files'][str(original)],'Runtime copy differs')
            copied[str(target)]=dict(source=str(original),sha256=checksum)
        (OUT/'sim/tv/rtldatafile').mkdir(parents=True)
        rtl=OUT/'sim/verilog';pc=OUT/'sim/wrapc_pc'
        tcl,probes=diagnostic_tcl(rtl,hls);bounded=OUT/'bounded.tcl';bounded.write_text(tcl)
        runtime=['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0','--']
        jobs=[dict(phase='elaborate',command=preparation['compile_command'],cwd=str(rtl)),
              dict(phase='rtl',command=runtime+[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2',
                   '-tclbatch',str(bounded)],cwd=str(rtl)),
              dict(phase='postcheck',command=runtime+[str(pc/'cosim.pc.exe')],cwd=str(pc))]
        inputs={str(p):digest(p) for p in [AUDIT,HLS_AUDIT,PREP/'preparation.json',Path(__file__).resolve(),bounded,
                ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py',ROOT/'scripts/owned_sim_resource_policy_v1.py',
                ROOT/'scripts/check_collision_safe_batch_hls_v1.py']}
        plan=dict(files=inputs,copied=copied,commands=jobs,diagnostic_probes=probes,transactions=4,pointers=44,models=30,
                  resource_policy=POLICY,initial_memory=initial,startup_free_memory_gate=False,
                  runtime_as_bytes=96*1024**3,compiler_as_bytes=192*1024**3,stack_bytes=256*1024**2,core_bytes=0,
                  original_postcheck_preserved=True,full_kernel_accepted=False)
        atomic(OUT/'plan.json',plan)
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'rtl')}
        for job in jobs:
            phase=job['phase'];state.update(stage=phase);atomic(OUT/'state.json',state)
            require(abort_reason(initial,observe()) is None,'New OOM before '+phase)
            started=time.monotonic();observed=None;reason=None;last=0
            with (OUT/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                while child.poll() is None:
                    if observed is None:
                        observed=observe_limits(child,phase)
                        if observed:atomic(OUT/(phase+'.actual_limits.json'),observed)
                    current=observe();reason=abort_reason(initial,current)
                    if time.monotonic()-last>=30:
                        atomic(OUT/'resource_observation.json',dict(phase=phase,observation=current,actual_limits=observed));last=time.monotonic()
                    if reason:stop(child);break
                    time.sleep(1)
                code=child.wait();child=None
            log=OUT/(phase+'.log')
            receipt=dict(command=job['command'],cwd=job['cwd'],exit_code=code,elapsed_seconds=time.monotonic()-started,
                         abort_reason=reason,actual_limits=observed,final_memory=observe(),log_sha256=digest(log))
            atomic(OUT/(phase+'.receipt.json'),receipt)
            text=log.read_text(errors='replace')
            require(code==0 and reason is None and not any(e in text for e in ERRORS),'Failed '+phase)
            require(observed is not None,'Actual process limits were not observed '+phase)
            if phase=='rtl':
                require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4',text) is not None and
                        'COLLISION_SAFE_NATIVE_BOUNDED_RETURNED' in text,'Incomplete four RTL transactions')
            elif phase=='postcheck':
                require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and
                        'SEARCH_BATCH_PASS mode=1' in text,'Original full C postcheck not passed')
        snapshots=[]
        for tx in range(4):
            actual=OUT/f'rtl_1_{tx}.bin';reference=BASE/'collision_safe_compact_cosim_setup_v1'/f'hls_1_{tx}.bin'
            require(actual.stat().st_size==reference.stat().st_size==946498280,'Incomplete full44 output')
            checksum=digest(actual);require(checksum==digest(reference),'Full RTL/C snapshot differs')
            snapshots.append(dict(transaction=tx,actual=str(actual),reference=str(reference),bytes=946498280,sha256=checksum))
        for n,h in inputs.items():require(digest(n)==h,'Execution input changed '+n)
        for n,row in copied.items():require(digest(n)==row['sha256'],'Copied runtime input changed '+n)
        atomic(OUT/'comparison.json',dict(status='four_complete_RTL_snapshots_equal_original_C_reference',snapshots=snapshots))
        state.update(status='complete',stage='independent_final_rtl_audit_pending');atomic(OUT/'state.json',state)
        print(state['stage'])
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
