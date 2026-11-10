#!/usr/bin/env python3
"""Integrate exact compressed trace top into the full existing CPU differential."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def one(s,a,b):
    require(s.count(a)==1,'Ambiguous transformation '+a);return s.replace(a,b)
def main():
    proof=ROOT/'results/batch_component_20261025_v1.json';d=json.loads(proof.read_text())
    for p,h in d['files'].items():require(digest(p)==h,'Changed baseline '+p)
    base=ROOT/'data/derived/batch_router_20261025_v1';out=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router');out.mkdir(exist_ok=False)
    source=out/'source';shutil.copytree(base/'source',source)
    for name in ['search_batch_trace_top_v2.cpp','search_trace_v3.hpp','search_trace_v2.hpp','search_trace_set_codec.hpp','search_trace_records.hpp','search_round_trace.hpp','search_batch_trace_frames.hpp']:
        shutil.copyfile(ROOT/'hardware/vitis'/name,source/name)
    text=(source/'search_batch_trace_top_v2.cpp').read_text();guard='#if defined(SEARCH_SINK_LOOP_OBSERVE) && !defined(__SYNTHESIS__)\n'
    text=one(text,'static void sink_loop_worker',guard+'extern "C" void search_sink_loop_observe(uint32_t,unsigned,const uint64_t*,const uint64_t*,const uint64_t*,const uint32_t*,unsigned);\nextern "C" void search_batch_boundary(unsigned,unsigned,unsigned);\n#endif\nstatic void sink_loop_worker')
    text=one(text,'        fpga_search::SearchTraceV3<>::search',guard+'        search_sink_loop_observe(sinks[sink],root_count,result,unknown_nodes,unknown_pips,path,unsigned(packet[2]));\n#endif\n        fpga_search::SearchTraceV3<>::search')
    text=one(text,'            net_worker(image',guard+'            search_batch_boundary(0,iteration,q);\n#endif\n            net_worker(image')
    line='            complete_flags[q]=uint32_t(net_result[5]);++batch_result[4];batch_result[5]+=net_result[3];batch_result[6]+=net_result[4];'
    text=one(text,line,line+'\n'+guard+'            search_batch_boundary(1,iteration,q);\n#endif')
    line='        fpga_search::RoundTrace<>::write(0,'
    text=one(text,line,guard+'        search_batch_boundary(2,iteration,nets);\n#endif\n'+line)
    observed=source/'search_batch_trace_observed_top_v2.cpp';observed.write_text(text)
    raw=(source/'search_batch_trace_top_v2.cpp').read_text();a=raw.index('extern "C" void SEARCH_TOP_NAME');decl=raw[a:raw.index(' {',a)]+';'
    p=source/'sink_loop_observer.hpp';s=p.read_text();start=s.index('extern "C" void search_batch_csr');s=s[:start]+decl.replace('SEARCH_TOP_NAME','search_batch_csr')+'\n'+decl.replace('SEARCH_TOP_NAME','search_batch_compact')+'\n';p.write_text(s)
    p=source/'search_kernel_route_adapter.hpp';s=p.read_text();s='#include <fstream>\n#include <cstdlib>\n'+s
    s=one(s,'    std::array<uint64_t,8> last_net_{},last_round_{};', '    std::array<uint64_t,8> last_net_{},last_round_{};\n    std::array<uint64_t,8> trace_meta_{};\n    std::vector<uint64_t> trace_words_=std::vector<uint64_t>(16777216);')
    s=one(s,'budget,0,0,0,0,0,0,0,0,0,0};','budget,1,0,0,0,0,0,0,0,0,0};')
    s=one(s,'        {sink_loop_observation::Scope search_observer', '        const uint64_t trace_control[8]={16777216,0,0,0,0,0,0,0};\n        {sink_loop_observation::Scope search_observer')
    s=one(s,'last_round_.data(),batch_result.data());','last_round_.data(),batch_result.data(),trace_control,trace_meta_.data(),trace_words_.data());')
    s=one(s,'        if(batch_result[0] || meta[0]', '''        if(const char* prefix=std::getenv("A_BATCH_TRACE_OUTPUT_PREFIX")){
            static thread_local unsigned invocation=0;
            const std::string name=std::string(prefix)+"_"+std::to_string(image_.config[0])+"_"+std::to_string(invocation++)+".bin";
            std::ofstream trace(name,std::ios::binary);auto put=[&](uint64_t word){for(unsigned b=0;b<8;++b)trace.put(char(word>>(8*b)));};
            for(auto word:trace_meta_)put(word);
            for(unsigned i=0;i<trace_meta_[2];++i)put(trace_words_[i]);
            trace.close();if(!trace)fail(false,"write diagnostic trace");
        }
        if(trace_meta_[4])fail(false,"diagnostic compressed trace overflow/invalid");
        if(batch_result[0] || meta[0]''')
    p.write_text(s)
    command=json.loads((base/'plan.json').read_text())['command']
    command=[x.replace(str(base/'source'),str(source)).replace(str(base/'differential'),str(out/'differential')).replace(str(base/'batch_csr.o'),str(out/'batch_csr.o')).replace(str(base/'batch_compact.o'),str(out/'batch_compact.o')) for x in command]
    # Preserve whole original 400-case driver and compiler flags.
    command[2]='125'
    files={**d['files'],str(proof):digest(proof),str(Path(__file__).resolve()):digest(__file__)}
    generated={str(p):digest(p) for p in source.iterdir() if p.is_file()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated,command=command,trace_capacity_words=16777216,reset_state=1),indent=2)+'\n')
    pointer=ROOT/'data/derived/compressed_batch_router_20261025_v1';pointer.mkdir(exist_ok=False);(pointer/'location.json').write_text(json.dumps(dict(bundle=str(out),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='prepare')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    def run(phase,cmd):
        state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        with (out/(phase+'.log')).open('x') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n')
        require(code==0,'Compressed batch phase failed '+phase)
    save()
    try:
        for name in ['search_batch_trace_top_v2.cpp','search_batch_trace_observed_top_v2.cpp']:
            path=out/(name+'.preprocessed')
            with path.open('x') as f:
                subprocess.run(['g++','-std=c++14','-E','-P','-D__SYNTHESIS__','-DSEARCH_SINK_LOOP_OBSERVE=1',str(source/name)],stdout=f,check=True)
        paths=[out/(name+'.preprocessed') for name in ['search_batch_trace_top_v2.cpp','search_batch_trace_observed_top_v2.cpp']]
        require(re.findall(r'\w+|\S',paths[0].read_text())==re.findall(r'\w+|\S',paths[1].read_text()),'Observer synthesis tokens differ')
        for mode,name in [(0,'csr'),(1,'compact')]:
            run('compile_'+name,['taskset','-c','125','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_SINK_LOOP_OBSERVE=1',f'-DSEARCH_GRAPH_MODE={mode}',f'-DSEARCH_TOP_NAME=search_batch_{name}','-c',str(observed),'-o',str(out/f'batch_{name}.o')])
        run('compile_differential',command);run('differential',['taskset','-c','125',str(out/'differential'),str(source/'sites.txt')])
        expected='ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n'
        require((out/'differential.log').read_text()==expected,'Different full differential scope')
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed integration input '+p)
        state.update(status='complete',stage='all_400_cases_with_exact_compressed_trace_verified_independent_audit_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
