#!/usr/bin/env python3
"""Isolated replay of the unchanged compiled snapshot for failure observability.

No recompile, force, modified DUT, reduced depth, changed vectors, or acceptance
artifact. A short visibility preflight must pass before the expensive replay.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import observe_limits, stop

ROOT=Path(__file__).resolve().parents[1]
OLD=Path('/tmp/A_graph_compression_recovery_20261025_v1/compact_nonzero_native_rtl_v2')
OUT=OLD.parent/'native_nonzero_failure_capture_v2'
SNAPSHOT='search_batch_trace_top_v2'
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
PREP=ROOT/'results/compact_nonzero_native_entry_preparation_20261029_v2.json'


def main():
    require(not OUT.exists(),'Refuse overwrite or competing replay')
    oldstate=json.loads((OLD/'state.json').read_text())
    require(oldstate['status']=='failed' and oldstate['stage']=='rtl','Different original failure')
    require('A_REBASE_BELOW_BASE input_mem write=0' in (OLD/'rtl.log').read_text(),'Wrong failure')
    diag=ROOT/'results/trace_root_address_diagnostic_20261030_v1.json'
    d=json.loads(diag.read_text())
    require(d['status']=='trace_root_constant_zero_address_cones_reproduce_guard_failure_diagnostic_only','Missing diagnosis')
    for n,h in d['files'].items(): require(digest(n)==h,'Changed diagnostic evidence '+n)
    initial=observe();OUT.mkdir()
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_compiled_snapshot_and_bind_full_inputs',
               diagnostic_only=True,full_kernel_accepted=False)
    atomic(OUT/'state.json',state)
    child=None
    try:
        sim=OUT/'sim';cwd=sim/'verilog';cwd.mkdir(parents=True)
        (sim/'tv/rtldatafile').mkdir(parents=True)
        p=json.loads(PREP.read_text());files={}
        for relative,row in p['manifest'].items():
            require(abort_reason(initial,observe()) is None,'New OOM during binding')
            source=OLD/'sim'/relative
            require(digest(source)==row['sha256'],'Original actual input changed '+str(source))
            target=sim/relative;target.parent.mkdir(parents=True,exist_ok=True)
            target.symlink_to(source)
            files[str(source)]=row['sha256']
        # Copy only the executable snapshot, never its mutable outputs by link.
        # XSim creates new journals/kernel logs/scripts in this new directory.
        oldsnap=OLD/'sim/verilog/xsim.dir'/SNAPSHOT
        newsnap=cwd/'xsim.dir'/SNAPSHOT
        newsnap.mkdir(parents=True)
        for source in oldsnap.iterdir():
            if source.is_file() and source.name in ('xsim.reloc','xsim.mem','xsim.type','xsim.xdbg',
                    'xsim.rtti','xsim.dbg','xsimk','xsim.svtype','Compile_Options.txt'):
                target=newsnap/source.name;shutil.copy2(source,target)
                sha=digest(source);require(digest(target)==sha,'Snapshot copy differs')
                files[str(source)]=sha;files[str(target)]=sha
        require((newsnap/'xsimk').is_file(),'No executable snapshot')
        # v1 queried every object successfully. Its parser mistakenly matched
        # MISSING_PROBE in Tcl source echoes; no long replay was started.
        prior=OLD.parent/'native_nonzero_failure_capture_v1'
        for source in [prior/'state.json',prior/'preflight.log',prior/'preflight.receipt.json',ROOT/'scripts/capture_native_nonzero_failure_v1.py']:
            files[str(source)]=digest(source)
        base='/apatb_search_batch_trace_top_v2_top'
        dut=base+'/AESL_inst_search_batch_trace_top_v2'
        batch=dut+'/grp_batch_worker_fu_1174'
        net=batch+'/grp_net_worker_fu_2443'
        sink=net+'/grp_sink_loop_worker_fu_1969'
        scopes=dict(dut=dut,batch=batch,net=net,sink=sink,
                    search_trace=sink+'/grp_search_fu_31062',net_trace=batch+'/grp_net_fu_2547')
        probes={}
        for label,scope in scopes.items():
            for signal in ['m_axi_input_mem_ARADDR','m_axi_input_mem_ARVALID','m_axi_input_mem_ARREADY',
                           'ap_start','ap_done']:
                # Top has an ap_CS_fsm too, but direct AXI internal READY on
                # leaf modules is only meaningful with the matching VALID.
                probes[label+'_'+signal]=scope+'/'+signal
        probes.update(top_root_nodes=dut+'/root_nodes',
                      batch_root_nodes=batch+'/root_nodes',sink_root_nodes=sink+'/root_nodes',
                      search_trace_roots=sink+'/grp_search_fu_31062/roots_x',
                      net_trace_roots=batch+'/grp_net_fu_2547/roots_x',
                      top_arsize=dut+'/m_axi_input_mem_ARSIZE',top_arlen=dut+'/m_axi_input_mem_ARLEN')
        for label,states in [('search_trace',[1291,1363,2803,2875]),('net_trace',[2806,2878,4899,4971,5545])]:
            for number in states:
                probes[label+'_state'+str(number)]=scopes[label]+'/ap_CS_fsm_state'+str(number)
        procedure='''proc capture_values {tag} {
  puts "A_CAPTURE_TIME $tag [current_time]"
'''
        for label,path in probes.items():
            procedure+=f'  if {{[llength [get_objects {{{path}}}]] != 1}} {{error "MISSING_PROBE {label}"}}\n'
            procedure+=f'  puts "A_CAPTURE_VALUE $tag {label} [get_value -radix hex {{{path}}}]"\n'
        procedure+='}\n'
        preflight=OUT/'preflight.tcl'
        preflight.write_text(procedure+'run 0 ns\ncapture_values PREFLIGHT\nputs A_CAPTURE_PREFLIGHT_PASS\nquit\n')
        capture=OUT/'capture.tcl'
        wave=cwd/'failure_window.vcd'
        capture.write_text(procedure+'run 31000000 ns\nopen_vcd {'+str(wave)+'}\nlog_vcd [get_objects {'+' '.join(probes.values())+'}]\nrun 10 sec\nflush_vcd\nclose_vcd\ncapture_values AFTER_RUN\nputs A_CAPTURE_VALUES_COMPLETE\nquit\n')
        for source in [PREP,diag,Path(__file__).resolve(),ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py',
                       ROOT/'scripts/owned_sim_resource_policy_v1.py',OLD/'rtl.log',OLD/'rtl.receipt.json',
                       OLD/'plan.json',OLD/'elaborate.receipt.json',preflight,capture]:
            files[str(source)]=digest(source)
        plan=dict(status='isolated_unchanged_snapshot_diagnostic_replay',files=files,probes=probes,
                  original_trial=str(OLD),transactions=4,pointers=44,models=30,
                  actual_input_manifest=p['manifest'],resource_policy=POLICY,runtime_as_bytes=96*1024**3,
                  stack_bytes=256*1024**2,initial_memory=initial,
                  input_links_read_only_by_use=True,private_compiled_snapshot=True,
                  full_kernel_accepted=False,downstream_release=False)
        atomic(OUT/'plan.json',plan)
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1',
             'A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'rtl')}
        for phase,tcl,wall_limit in [('preflight',preflight,180),('capture',capture,24*3600)]:
            require(abort_reason(initial,observe()) is None,'New OOM before phase')
            state.update(stage=phase);atomic(OUT/'state.json',state)
            command=['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0',
                     '--',str(BIN/'xsim'),'--noieeewarnings',SNAPSHOT,'-tclbatch',str(tcl)]
            started=time.monotonic();observed=None;reason=None;last=0
            with (OUT/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                while child.poll() is None:
                    if observed is None:
                        observed=observe_limits(child,'rtl')
                        if observed:atomic(OUT/(phase+'.actual_limits.json'),observed)
                    now=observe();reason=abort_reason(initial,now)
                    if time.monotonic()-started>wall_limit:reason='diagnostic_wall_timeout'
                    if time.monotonic()-last>=30:
                        atomic(OUT/'resource_observation.json',dict(phase=phase,observation=now,actual_limits=observed));last=time.monotonic()
                    if reason:stop(child);break
                    time.sleep(1)
                rc=child.wait();child=None
            receipt=dict(command=command,exit_code=rc,elapsed_seconds=time.monotonic()-started,
                         abort_reason=reason,actual_limits=observed,final_memory=observe(),
                         log_sha256=digest(OUT/(phase+'.log')))
            atomic(OUT/(phase+'.receipt.json'),receipt)
            require(reason is None and rc in (0,1),'Replay execution failed '+phase)
            text=(OUT/(phase+'.log')).read_text(errors='replace')
            if phase=='preflight':
                require('A_CAPTURE_PREFLIGHT_PASS' in text and not any(line.startswith(('ERROR:','Fatal:','MISSING_PROBE')) for line in text.splitlines()),
                        'Snapshot visibility preflight failed; expensive replay not started')
            else:
                require('A_REBASE_BELOW_BASE input_mem write=0' in text and 'A_CAPTURE_VALUES_COMPLETE' in text,
                        'Different replay result or incomplete capture')
                require(len([line for line in text.splitlines() if line.startswith('A_CAPTURE_VALUE AFTER_RUN ')])==len(probes),
                        'Incomplete terminal values')
        state.update(status='diagnostic_capture_complete',stage='captured_failure_not_accepted')
        atomic(OUT/'state.json',state)
        print(state['status'])
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state)
        raise


if __name__=='__main__':main()
