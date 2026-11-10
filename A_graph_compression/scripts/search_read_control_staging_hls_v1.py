#!/usr/bin/env python3
"""Measure a one-header control-staging candidate in the full search kernel."""
import json,os,shutil,subprocess,time,signal
from pathlib import Path
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
from compressed_batch_compact_bus64_hls_v3 import child_limits
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    maximum=int(Path('/sys/fs/cgroup/memory.max').read_text());require(maximum-int(Path('/sys/fs/cgroup/memory.current').read_text())>=128*1024**3,'Insufficient cgroup headroom')
    proof=ROOT/'results/search_read_control_staging_cpu_20261025_v1.json';cpu=json.loads(proof.read_text());require(cpu['read_cases']==100000 and cpu['parent_chain_cases']==100000,'Missing differential gate')
    for p,h in cpu['files'].items():require(digest(p)==h,'Changed candidate CPU proof')
    predecessor=ROOT/'data/derived/search_packet_width64_20261024_v1';oldplan=json.loads((predecessor/'plan.json').read_text())
    for p,h in oldplan['generated'].items():require(digest(p)==h,'Changed full-kernel predecessor')
    out=BASE/'search_read_control_staging_hls_v1';project=BASE/'search_read_control_staging_hls_project_v1';out.mkdir(exist_ok=False);require(not project.exists(),'Refuse repeat')
    source=out/'source';shutil.copytree(predecessor/'source',source)
    candidate=ROOT/'hardware/vitis/search_control_staging_v1/search_label_records.hpp';canonical=ROOT/'hardware/vitis/search_label_records.hpp'
    require(digest(source/'search_label_records.hpp')==digest(canonical),'Different original records header')
    shutil.copyfile(candidate,source/'search_label_records.hpp')
    differences=[]
    for p in source.iterdir():
        if p.is_file() and digest(p)!=digest(predecessor/'source'/p.name):differences.append(p.name)
    require(differences==['search_label_records.hpp'],'Uncontrolled source changes')
    flow=source/'run_width_experiment.tcl';require(flow.read_text().count('-DSEARCH_GRAPH_MODE=0')==2,'Different graph mode')
    files={str(p):digest(p) for p in source.iterdir() if p.is_file()}
    for p in [proof,predecessor/'plan.json',candidate,canonical,Path(__file__).resolve(),ROOT/'scripts/compressed_batch_compact_bus64_hls_v3.py']:files[str(p)]=digest(p)
    command=['prlimit','--stack=67108864:67108864','--','taskset','-c','125','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    atomic(out/'plan.json',dict(files=files,command=command,project=str(project),predecessor_source=str(predecessor/'source'),changed_files=differences,graph_mode=0,transactions=2,full_workspace_testbench_unchanged=True,address_space_bytes=68719476736,core_bytes=0,max_single_file_bytes=8589934592,clock_ns=5,uncertainty_ns=1.35,rtl_verified=False))
    state=dict(owner_pid=os.getpid(),status='running',stage='full_kernel_csim_and_synthesis');atomic(out/'state.json',state)
    try:
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_SEARCH_KERNEL_SOURCE':str(source),'A_SEARCH_KERNEL_PROJECT':str(project)}
        log=out/'flow.log';aborted=False
        with log.open('x') as f:
            child=subprocess.Popen(command,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,preexec_fn=child_limits,start_new_session=True);state['child_pid']=child.pid;atomic(out/'state.json',state)
            while child.poll() is None:
                if maximum-int(Path('/sys/fs/cgroup/memory.current').read_text())<16*1024**3:os.killpg(child.pid,signal.SIGTERM);aborted=True
                time.sleep(1)
            code=child.wait()
        atomic(out/'receipt.json',dict(command=command,exit_code=code,resource_abort=aborted,log_sha256=digest(log)))
        text=log.read_text();require(code==0 and not aborted and 'ERROR:' not in text and text.splitlines().count('PACKET_WIDTH_SYNTHESIS_COMPLETE')==1,'Full-kernel HLS failed')
        require(text.splitlines().count('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1')==1,'Full kernel C oracle missing')
        for p,h in files.items():require(digest(p)==h,'Changed full-kernel HLS input')
        state.update(status='complete',stage='full_kernel_csim_synthesis_pending_independent_audit');atomic(out/'state.json',state)
    except BaseException as e:
        state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
