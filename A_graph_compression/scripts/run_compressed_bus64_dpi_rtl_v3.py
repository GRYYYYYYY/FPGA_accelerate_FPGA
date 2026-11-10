#!/usr/bin/env python3
"""Run all four full44 transactions only after independently accepted search DPI parity."""
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
    gate=ROOT/'results/search_axi_dpi_replay_audit_20261025_v3.json'
    require(gate.exists(),'Full-depth search-core DPI independent parity audit required before batch execution')
    proof=json.loads(gate.read_text())
    require(proof['status']=='full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified','Wrong full search parity gate')
    cg=Path('/sys/fs/cgroup')
    require(int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=168*1024**3,'Insufficient cgroup headroom')
    preflight=ROOT/'data/derived/compressed_bus64_dpi_models_preflight_20261025_v1'
    audit_path=ROOT/'results/compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json'
    reviewed=json.loads(audit_path.read_text());conversion=json.loads((preflight/'plan.json').read_text())
    guard_path=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json';guards=json.loads(guard_path.read_text())
    require(guards['cases']==9 and len(reviewed['models'])==30 and conversion['transactions']==4,'Incomplete conversion/guard matrix')
    files={str(p):digest(p) for p in [gate,audit_path,preflight/'plan.json',guard_path,Path(__file__).resolve(),ROOT/'scripts/supervise_search_axi_dpi_v3.py']}
    for r in [proof,reviewed,guards]:
        for p,h in r['files'].items():require(digest(p)==h,'Changed accepted prerequisite '+p);files[p]=h
    parent=BASE/'compressed_batch_bus64_rtl_guarded_v1';preparation=json.loads((parent/'plan.json').read_text())
    require(preparation['transactions']==4 and preparation['graph_mode']==0,'Wrong batch scope')
    files[str(parent/'plan.json')]=digest(parent/'plan.json')
    out=BASE/'compressed_batch_bus64_dpi_rtl_v3';out.mkdir(exist_ok=False)
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_full_guarded_setup')
    atomic(out/'state.json',state)
    try:
        dst=out/'sim'
        shutil.copytree(parent/'sim',dst,ignore=lambda d,n:[x for x in n if x in ['xsim.dir','.Xil','rtldatafile'] or x.endswith(('.log','.pb','.jou')) or 'performance.result' in x])
        (dst/'tv/rtldatafile').mkdir(exist_ok=True)
        for p,h in preparation['copied_files'].items():
            a=Path(p);b=dst/a.relative_to(parent/'sim')
            if 'rtldatafile' in a.parts or 'performance.result' in a.name or a.suffix in ['.log','.pb','.jou']:continue
            require(b.is_file() and digest(b)==h,'Copied full setup differs '+str(b));files[str(b)]=h
        directory=dst/'verilog';models=[]
        for m in conversion['models']:
            source=preflight/'input/verilog'/Path(m['path']).name;target=directory/source.name
            require(digest(target)==digest(source)==m['before_sha256'],'Guarded model differs before conversion')
            shutil.copyfile(m['path'],target);require(digest(target)==m['after_sha256'],'Converted model differs')
            files[str(target)]=digest(target);models.append({**m,'path':str(target)})
        for pattern in ['*.v','*.dat']:
            require({p.name for p in directory.glob(pattern)}=={p.name for p in (parent/'sim/verilog').glob(pattern)},'Different complete RTL/ROM set')
            for a in (parent/'sim/verilog').glob(pattern):
                if a.name.startswith('AESL_axi_master_'):continue
                b=directory/a.name;require(digest(a)==digest(b),'DUT/ROM modified');files[str(b)]=digest(b)
        cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp';files[str(cpp)]=digest(cpp)
        commands=[shlex.split(line) for line in (directory/'run_xsim.sh').read_text().splitlines() if line.strip() and not line.startswith('#')]
        require(len(commands)==2,'Different generated simulator commands')
        bounded=out/'bounded.tcl';bounded.write_text('run 10 sec\nputs FULL44_DPI_BOUNDED_RETURNED\nquit\n');files[str(bounded)]=digest(bounded)
        prefix=['prlimit','--stack=67108864:67108864','--core=0:0','--as=154618822656:154618822656','--','taskset','-c','122'];pc=dst/'wrapc_pc'
        jobs=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14',str(cpp)],directory),
              ('elaborate',prefix+['/usr/bin/time','-v']+commands[0]+['-mt','off','--O0','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),
              ('rtl',prefix+commands[1][:-1]+[str(bounded)],directory),('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
        plan=dict(files=files,models=models,transactions=4,ports=44,graph_mode=0,depths_unchanged=True,pages_unchanged=True,
                  simulation_bound_ns=10000000000,commands=[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],resource_abort_free_bytes=16*1024**3,per_process_address_space_limit_bytes=144*1024**3,core_dump_limit_bytes=0)
        atomic(out/'plan.json',plan)
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'rtl')}
        for phase,command,cwd in jobs:
            state['stage']=phase;atomic(out/'state.json',state);start=time.monotonic();aborted=False
            with (out/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(out/'state.json',state)
                while child.poll() is None:
                    if int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())<plan['resource_abort_free_bytes']:
                        os.killpg(child.pid,signal.SIGTERM);aborted=True;break
                    time.sleep(2)
                code=child.wait()
            text=(out/(phase+'.log')).read_text(errors='replace')
            atomic(out/(phase+'.receipt.json'),dict(command=command,cwd=str(cwd),exit_code=code,elapsed_seconds=time.monotonic()-start,
                resource_admission_abort=aborted,log_sha256=digest(out/(phase+'.log')),plan_sha256=digest(out/'plan.json')))
            require(not aborted and code==0 and not any(s in text for s in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST']),'Batch phase failed '+phase)
            if phase=='rtl':require('FULL44_DPI_BOUNDED_RETURNED' in text and re.search(r'RTL Simulation :\s*4 / 4',text),'Incomplete four RTL transactions')
            if phase=='postcheck':require('SEARCH_BATCH_PASS mode=0' in text and 'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=0 ports=44 transactions=4' in text,'Original full44 C oracle failed')
        performance=directory/'search_batch_trace_top_v2.performance.result.transaction.xml'
        rows=[tuple(map(int,m)) for m in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',performance.read_text(),re.M)]
        require([i for i,c in rows]==list(range(4)) and all(c>0 for i,c in rows),'Missing complete four transaction cycles')
        for i in range(4):
            actual=out/f'rtl_0_{i}.bin';reference=BASE/f'compressed_batch_bus64_cosim_setup/hls_0_{i}.bin'
            require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==digest(reference),'Complete full44 snapshot mismatch')
        for p,h in files.items():require(digest(p)==h,'Frozen execution input changed '+p)
        state.update(status='complete',stage='full44_four_transaction_dpi_rtl_and_c_oracle_pending_independent_audit',cycles=[c for i,c in rows]);atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
