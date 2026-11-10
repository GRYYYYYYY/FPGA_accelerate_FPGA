#!/usr/bin/env python3
"""Single-variable packet AXI widening experiment; original sources remain frozen."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3'
    out=ROOT/'data/derived/search_packet_width64_20261024_v1'
    project=ROOT/'build/search_packet_width64_20261024_v1'
    if project.exists():raise ValueError('Existing project')
    out.mkdir(exist_ok=False);source=out/'source';shutil.copytree(base/'source',source)
    oldplan=json.loads((base/'plan.json').read_text())
    bound={**oldplan.get('files',{}),**oldplan.get('copied',{})}
    for p in (base/'source').iterdir():
        if str(p) not in bound or sha(p)!=bound[str(p)]:raise ValueError('Unverified baseline source '+str(p))
    top=source/'search_kernel_top.cpp';text=top.read_text()
    old='#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304'
    if text.count(old)!=1:raise ValueError('Wrong packet pragma anchor')
    top.write_text(text.replace(old,old+' max_widen_bitwidth=64'))
    flow=source/'run_width_experiment.tcl'
    flow.write_text('''set source_dir [file normalize $::env(A_SEARCH_KERNEL_SOURCE)]
set project [file normalize $::env(A_SEARCH_KERNEL_PROJECT)]
if {[file exists $project]} {error "Refusing existing experiment"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_kernel_top
add_files $source_dir/search_kernel_top.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
add_files -tb $source_dir/test_search_kernel_top.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=0"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_compile -pipeline_loops 0
csim_design
puts PACKET_WIDTH_CSIM_COMPLETE
csynth_design
puts PACKET_WIDTH_SYNTHESIS_COMPLETE
exit
''')
    files={str(p):sha(p) for p in (base/'source').iterdir()}
    for p in [base/'plan.json',ROOT/'results/search_kernel_physical_csr_audit_20261024_v1.json',ROOT/'results/search_kernel_physical_csr_path_analysis_20261024_v1.json',Path(__file__).resolve()]:files[str(p)]=sha(p)
    generated={str(p):sha(p) for p in source.iterdir()}
    plan=dict(files=files,generated=generated,project=str(project),change='Only packet m_axi max_widen_bitwidth=64; algorithm/interface parameter order/depths unchanged.',target=dict(part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35),hypothesis='Narrowing the widened input bundle may reduce dynamic byte-lane/address selection logic; actual port width and generated RTL must be measured. It may reduce bandwidth or worsen latency.',documentation='https://docs.amd.com/r/2022.2-English/ug1399-vitis-hls/pragma-HLS-interface')
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='prepare')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    def run(name,cmd,amd=False):
        state['stage']=name;save()
        env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'}
        if amd:env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
        else:env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        env.update(A_SEARCH_KERNEL_SOURCE=str(source),A_SEARCH_KERNEL_PROJECT=str(project))
        with (out/(name+'.log')).open('x') as log:
            child=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/(name+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=sha(out/(name+'.log')),plan_sha256=sha(out/'plan.json')),indent=2)+'\n')
        if code:raise ValueError(name+' failed')
        print(name,'PASS',flush=True)
    save()
    try:
        for mode in [0,1]:
            binary=out/('preflight_'+str(mode))
            run('compile_'+str(mode),['taskset','-c','122','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(source/'test_search_kernel_top.cpp'),str(top),'-o',str(binary)])
            run('preflight_'+str(mode),['prlimit','--stack=67108864:67108864','--','taskset','-c','122',str(binary)])
            if 'SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1' not in (out/('preflight_'+str(mode)+'.log')).read_text():raise ValueError('Missing complete preflight')
        run('hls',['prlimit','--stack=67108864:67108864','--','taskset','-c','122','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)],True)
        for p,h in {**files,**generated}.items():
            if sha(p)!=h:raise ValueError('Changed experiment input '+p)
        if 'PACKET_WIDTH_SYNTHESIS_COMPLETE' not in (out/'hls.log').read_text():raise ValueError('Incomplete synthesis')
        state.update(status='complete',stage='synthesized_pending_structural_comparison');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
