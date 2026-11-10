#!/usr/bin/env python3
"""Synthesize the actual combined connection entry after both-mode rejection tests."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=ROOT/'data/derived/search_sink_loop_cpu_20261025_v2';state=json.loads((prior/'state.json').read_text());require(state['status']=='complete' and state['completed']==[0,1],'Missing connection CPU gate')
    p=json.loads((prior/'plan.json').read_text())
    for path,h in {**p['files'],**p['generated']}.items():require(digest(path)==h,'Changed CPU integration '+path)
    out=ROOT/'data/derived/search_sink_loop_hls_20261025_v2';project=ROOT/'build/search_sink_loop_hls_20261025_v2';require(not project.exists(),'Existing HLS project');out.mkdir(exist_ok=False)
    source=out/'source';shutil.copytree(prior/'source',source)
    flow=out/'flow.tcl';flow.write_text('''set source_dir [file normalize $::env(A_CONNECTION_SOURCE)]
set project [file normalize $::env(A_CONNECTION_PROJECT)]
if {[file exists $project]} {error "Existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_sink_loop_top
add_files $source_dir/search_sink_loop_top_v2.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
add_files -tb $source_dir/test_search_sink_loop.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_compile -pipeline_loops 0
csim_design
puts SINK_LOOP_CSIM_COMPLETE
csynth_design
puts SINK_LOOP_SYNTHESIS_COMPLETE
exit
''')
    files={**p['files'],**p['generated']}
    for path in [prior/'state.json',prior/'plan.json',Path(__file__).resolve(),flow]:files[str(path)]=digest(path)
    for mode in [0,1]:
        for phase in ['compile','run']:
            log=prior/(phase+'_'+str(mode)+'.log');rp=prior/(phase+'_'+str(mode)+'.receipt.json');r=json.loads(rp.read_text());require(r['exit_code']==0 and r['log_sha256']==digest(log),'Failed CPU receipt')
            for path in [log,rp]:files[str(path)]=digest(path)
    generated={str(path):digest(path) for path in source.iterdir()}
    command=['prlimit','--stack=67108864:67108864','--','taskset','-c','124','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    plan=dict(files=files,generated=generated,command=command,project=str(project),part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35)
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');state=dict(owner_pid=os.getpid(),status='running',stage='csim_and_synthesis')
    def save():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    save()
    try:
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_CONNECTION_SOURCE':str(source),'A_CONNECTION_PROJECT':str(project)}
        with (out/'flow.log').open('x') as log:
            child=subprocess.Popen(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/'receipt.json').write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/'flow.log')),indent=2)+'\n')
        t=(out/'flow.log').read_text();require(code==0 and 'ERROR:' not in t and 'SINK_LOOP_SYNTHESIS_COMPLETE' in t and 'SEARCH_SINK_LOOP_PASS mode=0 sorted_duplicate_sinks=3 empty=1 rejected=2 unknown_incomplete=1 internal_roots_patch_search_tree_edges=1' in t,'Connection HLS failed')
        for path,h in {**files,**generated}.items():require(digest(path)==h,'Changed HLS input '+path)
        state.update(status='complete',stage='synthesized_pending_independent_review_and_rtl');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
