#!/usr/bin/env python3
"""Run 2022.2 C simulation and synthesis for the isolated exact-trace entry."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    failed=ROOT/'data/derived/search_batch_trace_hls_20261025_v1'
    old=json.loads((failed/'state.json').read_text())
    assert old['status']=='failed' and not Path('/proc',str(old['owner_pid'])).exists(),'Original owner not terminal'
    proof=ROOT/'results/search_batch_trace_cpu_20261025_v1.json';d=json.loads(proof.read_text())
    assert d['status']=='diagnostic_batch_top_both_modes_cpu_trace_and_independent_mixed_protocol_verified_hls_rtl_pending'
    for p,h in d['files'].items():assert sha(p)==h,p
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_hls_recovery');project=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_hls_project')
    assert not project.exists();out.mkdir(exist_ok=False)
    source=out/'source';shutil.copytree(ROOT/'data/derived/search_batch_trace_cpu_20261025_v1/source',source)
    flow=out/'flow.tcl';flow.write_text('''set source_dir [file normalize $::env(A_BATCH_TRACE_SOURCE)]
set project [file normalize $::env(A_BATCH_TRACE_PROJECT)]
if {[file exists $project]} {error "Existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_batch_trace_top
add_files $source_dir/search_batch_trace_top.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
add_files -tb $source_dir/test_search_batch_trace.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_compile -pipeline_loops 0
csim_design
puts BATCH_TRACE_CSIM_COMPLETE
csynth_design
puts BATCH_TRACE_SYNTHESIS_COMPLETE
exit
''')
    files={**d['files'],str(proof):sha(proof),str(Path(__file__).resolve()):sha(__file__),str(flow):sha(flow)}
    files.update({str(p):sha(p) for p in source.iterdir() if p.is_file()})
    for p in [failed/'state.json',failed/'receipt.json',failed/'flow.log',Path('/tmp/A_graph_compression_recovery_20261025_v1/relocation.json')]:files[str(p)]=sha(p)
    pointer=ROOT/'data/derived/search_batch_trace_hls_local_recovery_20261025_v1'
    pointer.mkdir(exist_ok=False)
    (pointer/'location.json').write_text(json.dumps(dict(bundle=str(out),project=str(project),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    cmd=['prlimit','--stack=67108864:67108864','--','taskset','-c','127','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    (out/'plan.json').write_text(json.dumps(dict(files=files,command=cmd,project=str(project),part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='csim_and_synthesis')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_TRACE_SOURCE':str(source),'A_BATCH_TRACE_PROJECT':str(project)}
        with (out/'flow.log').open('x') as log:
            child=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/'receipt.json').write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=sha(out/'flow.log')),indent=2)+'\n')
        t=(out/'flow.log').read_text()
        assert code==0 and 'ERROR:' not in t and 'BATCH_TRACE_SYNTHESIS_COMPLETE' in t,'HLS failure; preserve logs'
        for p,h in files.items():assert sha(p)==h,p
        state.update(status='complete',stage='csim_synthesized_pending_independent_review_rtl')
    except BaseException as e:
        state.update(status='failed',error=str(e));raise
    finally:save()
if __name__=='__main__':main()
