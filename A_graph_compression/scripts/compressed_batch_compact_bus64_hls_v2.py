#!/usr/bin/env python3
"""Run 2022.2 C simulation and synthesis for the isolated exact-trace entry."""
import hashlib
import json
import os
import resource
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def atomic_text(path, value):
    temporary=path.with_name(path.name+'.tmp')
    with temporary.open('x') as handle:
        handle.write(value);handle.flush();os.fsync(handle.fileno())
    os.replace(temporary,path)
from check_vitis_kernel import digest as sha
def child_limits():
    resource.setrlimit(resource.RLIMIT_FSIZE,(8589934592,8589934592))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))

def main():
    # Revalidate accepted evidence, rather than treating a filename as success.
    from compact_bus64_prerequisites_v1 import validate_prerequisites
    prerequisite_files=validate_prerequisites(ROOT/'results')
    maximum=int(Path('/sys/fs/cgroup/memory.max').read_text()); current=int(Path('/sys/fs/cgroup/memory.current').read_text())
    assert maximum-current>=184*1024**3, 'Insufficient cgroup memory headroom'
    proof=ROOT/'results/compressed_batch_trace_cases_20261025_v2.json';d=json.loads(proof.read_text())
    assert d['status']=='compressed_batch_all400_native_differential_and_exact_trace_v4_independently_verified_real_workload_pending'
    for p,h in d['files'].items():assert sha(p)==h,p
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_bus64_hls');project=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_bus64_hls_project')
    assert not project.exists();out.mkdir(exist_ok=False)
    source=out/'source';shutil.copytree(Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu/source'),source)
    for name in ['search_batch_trace_top_v2.cpp','search_trace_v3.hpp','search_trace_set_codec.hpp']:
        assert sha(ROOT/'hardware/vitis'/name)==sha(source/name),'Source differs from CPU '+name
    cpu_proof=ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json'
    full=json.loads(cpu_proof.read_text());assert full['ports']==44 and full['transactions_per_mode']==4
    tb=ROOT/'hardware/vitis/test_compressed_batch_rtl_full_depth.cpp'
    assert full['files'].get(str(tb))==sha(tb),'Full TB changed'
    shutil.copyfile(tb,source/tb.name)
    flow=out/'flow.tcl';atomic_text(flow,'''set source_dir [file normalize $::env(A_BATCH_TRACE_SOURCE)]
set project [file normalize $::env(A_BATCH_TRACE_PROJECT)]
if {[file exists $project]} {error "Existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_batch_trace_top_v2
add_files $source_dir/search_batch_trace_top_v2.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=1"
add_files -tb $source_dir/test_compressed_batch_rtl_full_depth.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=1"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_interface -m_axi_max_widen_bitwidth 64
config_compile -pipeline_loops 0
csim_design
puts COMPRESSED_BATCH_TRACE_CSIM_COMPLETE
csynth_design
puts COMPRESSED_BATCH_TRACE_SYNTHESIS_COMPLETE
exit
''')
    local_help=Path('/tmp/A_graph_compression_recovery_20261025_v1/hls_interface_options_20261025_v1/help.log')
    assert '-m_axi_max_widen_bitwidth' in local_help.read_text(),'Unsupported local interface configuration'
    previous_flow=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_bus64_hls/flow.tcl')
    assert flow.read_text().replace('SEARCH_GRAPH_MODE=1','SEARCH_GRAPH_MODE=0')==previous_flow.read_text(),'Configuration difference beyond graph mode'
    atomic_text(out/'single_variable_configuration.json',json.dumps(dict(configuration='config_interface -m_axi_max_widen_bitwidth 64',source_unchanged=True,graph_mode=1,baseline_flow_sha256=sha(previous_flow),local_help_sha256=sha(local_help),scope='Mode1 counterpart of CSR global64; same canonical top, capacity, full44 testbench and constraints'),indent=2)+'\n')
    files={**prerequisite_files,**d['files'],str(proof):sha(proof),str(Path(__file__).resolve()):sha(__file__),str(ROOT/'scripts/compact_bus64_prerequisites_v1.py'):sha(ROOT/'scripts/compact_bus64_prerequisites_v1.py'),str(flow):sha(flow),str(cpu_proof):sha(cpu_proof),str(out/'single_variable_configuration.json'):sha(out/'single_variable_configuration.json'),str(local_help):sha(local_help),str(previous_flow):sha(previous_flow)}
    files.update({str(p):sha(p) for p in source.iterdir() if p.is_file()})
    cmd=['prlimit','--stack=67108864:67108864','--','taskset','-c','122','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    atomic_text(out/'plan.json',json.dumps(dict(files=files,command=cmd,project=str(project),part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35,graph_mode=1,transactions=4,full44_depth_tb=True,max_single_output_file_bytes=8589934592),indent=2)+'\n')
    pointer=ROOT/'data/derived/compressed_batch_compact_bus64_hls_20261025_v1'
    pointer.mkdir(exist_ok=False)
    atomic_text(pointer/'location.json',json.dumps(dict(bundle=str(out),project=str(project),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='csim_and_synthesis')
    def save():
        atomic_text(out/'state.json',json.dumps(state,indent=2)+'\n')
    save()
    try:
        env={**os.environ,'A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'csim'),'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_TRACE_SOURCE':str(source),'A_BATCH_TRACE_PROJECT':str(project)}
        with (out/'flow.log').open('x') as log:
            child=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=child_limits);state['child_pid']=child.pid;save();code=child.wait()
        atomic_text(out/'receipt.json',json.dumps(dict(command=cmd,exit_code=code,log_sha256=sha(out/'flow.log')),indent=2)+'\n')
        t=(out/'flow.log').read_text()
        assert code==0 and 'ERROR:' not in t and 'COMPRESSED_BATCH_TRACE_SYNTHESIS_COMPLETE' in t,'HLS failure; preserve logs'
        for p,h in files.items():assert sha(p)==h,p
        state.update(status='complete',stage='csim_synthesized_pending_independent_review_rtl')
    except BaseException as e:
        state.update(status='failed',error=str(e));raise
    finally:save()
if __name__=='__main__':main()
