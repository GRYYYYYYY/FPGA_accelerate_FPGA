#!/usr/bin/env python3
"""Validate all44 actual allocations and retain full-payload CPU snapshots."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    require(int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())>=32*1024**3,'Insufficient CPU-test headroom')
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/read_control_staging_full44_cpu_v1');out.mkdir(exist_ok=False)
    source=out/'source';prior=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_rtl_tb_cpu_v2/source');shutil.copytree(prior,source)
    candidate=ROOT/'hardware/vitis/search_control_staging_v1/search_label_records.hpp'
    require(digest(source/'search_label_records.hpp')==digest(ROOT/'hardware/vitis/search_label_records.hpp'),'Different original records')
    shutil.copyfile(candidate,source/'search_label_records.hpp')
    tb=ROOT/'hardware/vitis/test_compressed_batch_rtl_full_depth.cpp';shutil.copyfile(tb,source/tb.name)
    inventory=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json';inv=json.loads(inventory.read_text())
    for p,h in inv['files'].items():require(digest(p)==h,'Changed generated depth inventory')
    inputs={str(p):digest(p) for p in source.iterdir() if p.is_file()}
    for p in [tb,inventory,candidate,ROOT/'results/search_read_control_staging_hls_audit_20261025_v1.json',ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json',Path(__file__).resolve()]:inputs[str(p)]=digest(p)
    atomic(out/'plan.json',dict(files=inputs,ports=inv['ports'],transactions_per_mode=4,modes=[0,1]))
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        atomic(out/'state.json',state)
    save()
    try:
        for mode in [0,1]:
            commands=[('compile',['g++','-std=c++14','-O1','-g','-Wall','-Wextra','-Werror','-Wno-error=unused-parameter','-Wno-unknown-pragmas','-fsanitize=address,undefined','-fno-omit-frame-pointer',f'-DSEARCH_GRAPH_MODE={mode}',str(source/tb.name),str(source/'search_batch_trace_top_v2.cpp'),'-o',str(out/f'mode_{mode}')]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(out/f'mode_{mode}')])]
            for phase,cmd in commands:
                state['stage']=f'{phase}_{mode}';save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1',A_BATCH_RTL_SNAPSHOT_PREFIX=str(out/'cpu'))
                with (out/f'{phase}_{mode}.log').open('x') as log:
                    child=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                atomic(out/f'{phase}_{mode}.receipt.json',dict(command=cmd,exit_code=code,log_sha256=digest(out/f'{phase}_{mode}.log')))
                require(code==0,'Full-depth CPU phase failed')
            state['completed'].append(mode);save()
        for p,h in inputs.items():require(digest(p)==h,'Changed full-depth CPU input')
        state.update(status='complete',stage='full44port_payload_snapshots_captured_independent_audit_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
