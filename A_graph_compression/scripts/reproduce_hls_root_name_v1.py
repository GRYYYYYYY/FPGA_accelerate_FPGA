#!/usr/bin/env python3
"""Controlled small HLS naming experiment, not production-kernel validation."""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/hls_root_name_reproducer_20261030_v1'
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def execute(directory,phase,args,timeout=600):
    initial=observe();start=time.monotonic();reason=None
    command=['prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--',*args]
    log=directory/(phase+'.log')
    with log.open('x') as stream:
        child=subprocess.Popen(command,cwd=directory,stdout=stream,stderr=subprocess.STDOUT,
                               start_new_session=True,env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'})
        while child.poll() is None:
            reason=abort_reason(initial,observe())
            if time.monotonic()-start>timeout:reason='bounded_diagnostic_timeout'
            if reason:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                break
            time.sleep(.5)
    receipt=dict(command=command,exit_code=child.returncode,resource_policy=POLICY,abort_reason=reason,
                 elapsed_seconds=time.monotonic()-start,initial_memory=initial,final_memory=observe(),log_sha256=digest(log))
    (directory/(phase+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    require(reason is None and child.returncode==0,'Execution failed '+phase)
    return log.read_text(errors='replace')


def main():
    require(not OUT.exists(),'Refuse overwrite');OUT.mkdir()
    body='''#include <stdint.h>
static void ROOT_FUNCTION(uint32_t* values,unsigned n){
#pragma HLS INLINE off
 for(unsigned i=0;i<n;++i)values[i]=3*i+7;
}
static uint64_t trace_read(const uint32_t* ROOT_ARGUMENT,unsigned n){
#pragma HLS INLINE off
 uint64_t sum=0;for(unsigned i=0;i<n;++i)sum+=ROOT_ARGUMENT[i];return sum;
}
extern "C" void root_name_top(uint32_t* root_nodes,unsigned n,uint64_t* result){
#pragma HLS INTERFACE m_axi port=root_nodes offset=slave bundle=input_mem depth=16
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=1
#pragma HLS INTERFACE s_axilite port=root_nodes bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=n bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
 if(n>16)return;
 ROOT_FUNCTION(root_nodes,n);result[0]=trace_read(root_nodes,n);
}
'''
    tb='''#include <stdint.h>
#include <cassert>
#include <cstdio>
extern "C" void root_name_top(uint32_t*,unsigned,uint64_t*);
int main(){uint32_t storage[64];uint64_t result=0;unsigned cases=0;
for(unsigned offset=0;offset<4;++offset)for(unsigned n=0;n<=16;++n){
 for(unsigned i=0;i<64;++i)storage[i]=0xa5a5a5a5;
 root_name_top(storage+offset,n,&result);assert(result==7*n+3*n*(n-1)/2);
 for(unsigned i=0;i<64;++i)assert(storage[i]==((i>=offset && i<offset+n)?3*(i-offset)+7:0xa5a5a5a5));
 ++cases;
}printf("NAMING_C_REFERENCE_PASS cases=%u\\n",cases);}
'''
    variants=[('collision','roots','roots'),('argument_renamed','roots','trace_roots'),
              ('function_renamed','build_roots','roots')]
    files={str(Path(__file__).resolve()):digest(__file__)};rows=[]
    for name,function,arg in variants:
        directory=OUT/name;directory.mkdir()
        source=directory/'top.cpp';source.write_text(body.replace('ROOT_FUNCTION',function).replace('ROOT_ARGUMENT',arg))
        test=directory/'tb.cpp';test.write_text(tb)
        flow=directory/'flow.tcl';flow.write_text('''open_project project
set_top root_name_top
add_files top.cpp -cflags "-std=c++14"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_compile -pipeline_loops 0
csynth_design
puts NAMING_CSYNTH_COMPLETE
exit
''')
        plan=dict(variant=name,function_name=function,argument_name=arg,
                  files={str(p):digest(p) for p in [source,test,flow]},diagnostic_only=True)
        (directory/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        execute(directory,'gpp',['g++','-std=c++14','-O2','-Wno-unknown-pragmas',str(source),str(test),'-o',str(directory/'reference')])
        require('NAMING_C_REFERENCE_PASS cases=68' in execute(directory,'reference',[str(directory/'reference')]),'C reference failed')
        log=execute(directory,'hls',[str(BIN),'-f',str(flow)])
        require('NAMING_CSYNTH_COMPLETE' in log and 'ERROR:' not in log,'HLS incomplete')
        rtl=directory/'project/solution/syn/verilog'
        parent=rtl/'root_name_top.v'
        text=parent.read_text()
        child=rtl/'root_name_top_trace_read.v'
        require(child.exists(),'Missing uninlined trace module')
        connections=re.findall(r'\.('+arg+r'(?:_x)?)\(([^)]+)\)',text)
        require(len(connections)==1,'Unexpected root argument connection '+name)
        port,value=connections[0]
        row=dict(variant=name,function_name=function,argument_name=arg,rtl_port=port,actual_connection=value,
                 literal_zero=bool(re.fullmatch(r"(?:\d+)?'[bdh]0+",value)),c_reference_cases=68,
                 renamed_warning_lines=[x for x in log.splitlines() if 'RTL name' in x and 'roots' in x])
        rows.append(row)
        for p in [*directory.glob('*.cpp'),*directory.glob('*.tcl'),*directory.glob('*.json'),
                  *directory.glob('*.log'),*rtl.glob('*.v')]:files[str(p)]=digest(p)
        print(json.dumps(row),flush=True)
    report=dict(status='small_hls_root_name_controlled_synthesis_experiment_complete',files=files,variants=rows,
                full_kernel_accepted=False,production_source_modified=False,
                naming_hypothesis_reproduced=rows[0]['literal_zero'] and not any(r['literal_zero'] for r in rows[1:]),
                limits=['Small scalar-loop diagnostic; no production capacity or RTL acceptance claim.',
                        'A reproduced difference would support a naming-related RTL generation defect in this tool release; full production regeneration and independent original oracles remain required.'])
    target=ROOT/'results/hls_root_name_reproducer_20261030_v1.json'
    require(not target.exists(),'Report exists');target.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report['naming_hypothesis_reproduced'])


if __name__=='__main__':main()
