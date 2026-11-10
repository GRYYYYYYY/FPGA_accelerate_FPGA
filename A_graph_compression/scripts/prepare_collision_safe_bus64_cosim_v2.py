#!/usr/bin/env python3
"""Fresh per-mode full44 setup from the independently reviewed collision-safe bus64 pair.

Clone the completed project; do not change or re-synthesize the reviewed RTL.
This step prepares vectors/models only and never launches xelab or xsim.
"""
import json
import argparse
import signal
import os
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from run_collision_safe_bus64_pair_v1 import actual_hls

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
REVIEW=ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v3.json'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def main():
    def interrupted(signum, frame): raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',type=int,choices=[0,1],required=True)
    mode=parser.parse_args().mode
    OLD=BASE/'collision_safe_bus64_pair_v1'/f'mode_{mode}'
    OUT=BASE/'collision_safe_bus64_cosim_setup_v2'/f'mode_{mode}'
    require(REVIEW.is_file(),'Independent recovered bus64 pair audit missing')
    require(not OUT.exists(),'Refuse overwrite or duplicate setup')
    review=json.loads(REVIEW.read_text())
    require(review['status']=='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending',
            'Missing new independent synthesis gate')
    require(review['full44_transactions_per_mode']==4 and [r['mode'] for r in review['modes']]==[0,1], 'Different paired scope')
    for n,h in review['files'].items():require(digest(n)==h,'Changed reviewed evidence '+n)
    initial=observe();OUT.mkdir(parents=True)
    state=dict(owner_pid=os.getpid(),status='running',stage='clone_reviewed_project',rtl_executed=False)
    atomic(OUT/'state.json',state);child=None
    try:
        source=OUT/'source';shutil.copytree(OLD/'source',source)
        require({p.name for p in source.iterdir()}=={p.name for p in (OLD/'source').iterdir()},'Source clone set differs')
        for p in source.iterdir():
            require(p.is_file() and digest(p)==review['files'][str(OLD/'source'/p.name)],'Source clone differs from reviewed pair')
        project=OUT/'project'
        shutil.copytree(OLD/'project',project,ignore=lambda d,n:[x for x in n if x in ('csim','sim')])
        synthesis={}
        for original in (OLD/'project/solution/syn').rglob('*'):
            if not original.is_file():continue
            target=project/original.relative_to(OLD/'project')
            sha=digest(original);require(digest(target)==sha,'Synthesis clone differs')
            synthesis[str(original)]=sha;synthesis[str(target)]=sha
        app=project/'hls.app';xml=ET.parse(app);entries=xml.getroot().findall('files/file')
        require(len(entries)==2,'Unexpected HLS source list')
        for entry in entries:
            name=Path(entry.attrib['name']).name
            require(name in ('search_batch_trace_top_v2.cpp','test_compressed_batch_rtl_full_depth.cpp'), 'Unexpected source '+name)
            require(f'-DSEARCH_GRAPH_MODE={mode}' in entry.attrib.get('cflags',''),'Wrong mode')
            if entry.attrib.get('tb') in ('1','true'):
                require(name=='test_compressed_batch_rtl_full_depth.cpp','Wrong full-depth testbench')
                entry.set('name',str(source/name))
            else:
                require(name=='search_batch_trace_top_v2.cpp','Wrong DUT')
                entry.set('name',str(OLD/'source'/name))
        xml.write(app,encoding='utf-8',xml_declaration=True)
        initial_app=OUT/'initial.hls.app';shutil.copy2(app,initial_app)
        flow=OUT/'prepare.tcl';flow.write_text('cd {'+str(OUT)+'}\nopen_project project\nopen_solution solution\n'
                'csim_design -clean\nputs COLLISION_SAFE_FULL44_CSIM_COMPLETE\n'
                'cosim_design -rtl verilog -trace_level none -setup\nputs COLLISION_SAFE_FULL44_SETUP_COMPLETE\nexit\n')
        files={str(p):digest(p) for p in source.iterdir() if p.is_file()}
        for p in [REVIEW,Path(__file__).resolve(),ROOT/'scripts/owned_sim_resource_policy_v1.py',
                  ROOT/'scripts/run_collision_safe_batch_hls_v1.py',ROOT/'scripts/run_collision_safe_bus64_pair_v1.py',initial_app,flow]:files[str(p)]=digest(p)
        command=['prlimit','--as=68719476736:68719476736','--stack=67108864:67108864','--core=0:0','--',str(HLS),'-f',str(flow)]
        atomic(OUT/'plan.json',dict(files=files,synthesis=synthesis,command=command,project=str(project),
               original_project=str(OLD/'project'),transactions=4,ports=44,graph_mode=mode,resource_policy=POLICY,
               initial_memory=initial,rtl_executed=False))
        state['stage']='full_depth_csim_and_cosim_setup';atomic(OUT/'state.json',state)
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'hls')}
        begin=time.monotonic();reason=None;last=0;actual=None
        with (OUT/'prepare.log').open('x') as log:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            state['child_pid']=child.pid;atomic(OUT/'state.json',state)
            while child.poll() is None:
                if actual is None:
                    actual=actual_hls(child)
                    if actual:atomic(OUT/'actual_limits.json',actual)
                current=observe();reason=abort_reason(initial,current)
                if time.monotonic()-last>=30:
                    atomic(OUT/'resource_observation.json',dict(observation=current));last=time.monotonic()
                if reason:stop(child);break
                time.sleep(1)
            code=child.wait();child=None
        reason=reason or abort_reason(initial,observe())
        log=OUT/'prepare.log'
        atomic(OUT/'prepare.receipt.json',dict(command=command,exit_code=code,abort_reason=reason,
               elapsed_seconds=time.monotonic()-begin,log_sha256=digest(log),final_memory=observe(),actual_limits=actual))
        text=log.read_text(errors='replace')
        require(reason is None and code==0 and actual is not None and not any(e in text for e in ['ERROR:','Fatal:','LLVM ERROR','runtime error:']),'Setup execution failed')
        for marker in ['COLLISION_SAFE_FULL44_CSIM_COMPLETE','COLLISION_SAFE_FULL44_SETUP_COMPLETE',
                       f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4',f'SEARCH_BATCH_PASS mode={mode}']:
            require(marker in text,'Missing full setup marker '+marker)
        for n,h in {**files,**synthesis}.items():require(digest(n)==h,'Changed reviewed/copied input '+n)
        comparisons=[]
        for transaction in range(4):
            target=OUT/f'hls_{mode}_{transaction}.bin';reference=BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_{mode}_{transaction}.bin'
            require(target.stat().st_size==reference.stat().st_size==946498280,'Full snapshot size changed')
            sha=digest(target);require(sha==digest(reference),'Full HLS C snapshot differs')
            comparisons.append(dict(transaction=transaction,target=str(target),reference=str(reference),sha256=sha))
            files[str(target)]=sha;files[str(reference)]=sha
        sim=project/'solution/sim';rtl=sim/'verilog';models=list(rtl.glob('AESL_axi_master_*.v'))
        require(len(models)==30,'Incomplete full44 AXI model set')
        require('parameter AUTOTB_TRANSACTION_NUM = 4;' in (rtl/'search_batch_trace_top_v2.autotb.v').read_text(),
                'Wrong transaction count')
        for p in (project/'solution/syn/verilog').glob('*'):
            if p.is_file() and p.suffix in ('.v','.dat'):
                q=rtl/p.name;require(q.exists() and digest(q)==digest(p),'Simulation DUT/ROM differs '+p.name)
        for p in sim.rglob('*'):
            if p.is_file() and (p.suffix in ('.v','.sv','.dat','.tcl','.sh','.prj','.ini') or
                                p.name in ('cosim.pc.exe','apatb_search_batch_trace_top_v2.cpp')):
                files[str(p)]=digest(p)
        for p in [app,OUT/'plan.json',OUT/'prepare.receipt.json',OUT/'actual_limits.json',log]:files[str(p)]=digest(p)
        report=dict(status='collision_safe_bus64_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending',
                    files={**files,**synthesis},project=str(project),comparisons=comparisons,
                    transactions=4,ports=44,models=30,graph_mode=mode,rtl_executed=False,
                    limits=['Fresh generated zero-based models/vectors still need allocation audit, read-only guards and nonzero pointer mapping.',
                            'No RTL execution or physical acceptance; no downstream prerequisite release.'])
        atomic(OUT/'setup.json',report)
        state.update(status='complete',stage='fresh_setup_verified_rtl_preparation_pending');atomic(OUT/'state.json',state)
        print(report['status'])
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
