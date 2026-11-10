#!/usr/bin/env python3
"""Execute diagnostic batch top on the unchanged production-capacity CPU cases."""
from pathlib import Path
import shutil
import subprocess
import os
import json
import hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu');out.mkdir(exist_ok=False)
    source=out/'source';shutil.copytree(ROOT/'data/derived/search_batch_cpu_20261025_v1/source',source)
    for name in ['search_batch_trace_top_v2.cpp','search_trace_v3.hpp','search_trace_set_codec.hpp','search_batch_trace_frames.hpp','search_trace_v2.hpp','search_trace_records.hpp','search_round_trace.hpp']:
        shutil.copyfile(ROOT/'hardware/vitis'/name,source/name)
    text=(source/'test_search_batch.cpp').read_text();a=text.index('extern "C" void search_batch_top');b=text.index(';',a)+1
    raw=(source/'search_batch_trace_top_v2.cpp').read_text();a0=raw.index('extern "C" void SEARCH_TOP_NAME');decl=raw[a0:raw.index(' {',a0)].replace('SEARCH_TOP_NAME','search_batch_trace_top_v2')+';'
    text=text[:a]+decl+text[b:];text='#include <fstream>\n'+text
    text=text.replace('    auto invoke=[&](){search_batch_top(','''    uint64_t trace_meta[8]{},trace_control[8]={262144,0,0,0,0,0,0,0};
    std::vector<uint64_t> trace_data(262145,UINT64_C(0xdeadbeef));unsigned invocation=0;
    auto invoke=[&](){search_batch_trace_top_v2(''')
    needle='site_summaries.data(),round_result,batch_result);};'
    assert text.count(needle)==1
    text=text.replace(needle,'''site_summaries.data(),round_result,batch_result,trace_control,trace_meta,trace_data.data());
        assert(!trace_meta[4] && trace_meta[2] && trace_data.back()==UINT64_C(0xdeadbeef));
        const std::string name="trace_mode_"+std::to_string(SEARCH_GRAPH_MODE)+"_case_"+std::to_string(invocation++)+".bin";
        std::ofstream out(name,std::ios::binary);auto put=[&](uint64_t w){for(unsigned b=0;b<8;++b)out.put(char(w>>(8*b)));};
        for(auto w:trace_meta)put(w);
        for(unsigned i=0;i<trace_meta[2];++i)put(trace_data[i]);
        out.close();assert(out);
    };''')
    (source/'test_search_batch_trace.cpp').write_text(text)
    state={'status':'running','owner_pid':os.getpid(),'completed':[]}
    def save(): (out/'state.json').write_text(json.dumps(state,indent=2)+'\n')
    save()
    env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'}
    env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    for mode in [0,1]:
        binary=out/f'mode_{mode}'
        for phase,cmd in [('compile',['g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas',f'-DSEARCH_GRAPH_MODE={mode}',str(source/'test_search_batch_trace.cpp'),str(source/'search_batch_trace_top_v2.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--',str(binary)])]:
            state.update(stage=f'{phase}_{mode}');save()
            with (out/f'{phase}_{mode}.log').open('w') as log:
                proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=proc.pid;save();code=proc.wait()
            if code:state.update(status='failed',exit_code=code);save();raise RuntimeError(state)
        state['completed'].append(mode);save()
    state.update(status='complete',stage='cpu_trace_exported_independent_mixed_reader_pending');save()
    paths=[p for p in source.iterdir() if p.is_file()]+[p for p in out.iterdir() if p.is_file() and p.name!='state.json']+[Path(__file__).resolve()]
    (out/'files.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
if __name__=='__main__':main()
