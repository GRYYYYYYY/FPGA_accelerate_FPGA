#!/usr/bin/env python3
"""CPU sanitizer integration of actual search and edge tops on one max-depth path."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'data/derived/shared_search_edge_path_20261024_v1';out.mkdir(exist_ok=False)
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3/source';source=out/'source';shutil.copytree(base,source)
    original=json.loads((base.parent/'plan.json').read_text());bindings={**original['files'],**original['copied']}
    for p in base.iterdir():require(digest(p)==bindings[str(p)],'Changed baseline '+str(p))
    edge=ROOT/'hardware/vitis/search_retained_edges_top.cpp';header=edge.with_name('search_retained_edges.hpp')
    for p in [edge,header]:shutil.copyfile(p,source/p.name)
    text=(source/'test_search_kernel_top.cpp').read_text()
    declaration='extern "C" void search_retained_edges_top(const uint64_t*,uint64_t*,uint32_t*,const uint32_t*,uint32_t*,uint64_t*);\n'
    text=text.replace('struct Image {',declaration+'struct Image {',1)
    text=text.replace('path(8*L::path,0xabcdef01u)','path(16777216,0xabcdef01u)',1)
    anchor='    for(unsigned transaction=0;transaction<2;++transaction){'
    initialization='''    std::vector<uint32_t> edge_rows(37748736,0xdeadbeef),edge_out(16777216,0xdeadbeef);
    uint64_t edge_meta[6]{},edge_result[5]{},edge_config[8]={0,0,4,0,0,0,0,0};
    search_retained_edges_top(edge_config,edge_meta,edge_rows.data(),path.data(),edge_out.data(),edge_result);
    assert(edge_result[0]==0);
'''
    require(text.count(anchor)==1,'Loop anchor');text=text.replace(anchor,initialization+anchor,1)
    anchor='        assert(unknown[0]==0);'
    code='''        const auto original_path=path;
        if(result[0]==0){
            for(unsigned repeat=0;repeat<2;++repeat){
                edge_config[0]=3;edge_config[1]=7;edge_config[2]=0;edge_config[3]=result[7];
                search_retained_edges_top(edge_config,edge_meta,edge_rows.data(),path.data(),edge_out.data(),edge_result);
                assert(edge_result[0]==0 && edge_result[1]==2*(repeat+1));
            }
        }
        edge_config[0]=2;edge_config[3]=0;
        search_retained_edges_top(edge_config,edge_meta,edge_rows.data(),path.data(),edge_out.data(),edge_result);
        assert(edge_result[0]==0 && edge_result[4]==4 && edge_result[1]==4 && edge_result[3]==3);
        const uint32_t expected[16]={0,1,0,3,10,11,1,0,1,2,0,7,11,12,0,0};
        for(unsigned i=0;i<32;++i)assert(edge_out[i]==expected[i%16]);
        assert(std::all_of(edge_out.begin()+32,edge_out.end(),[](uint32_t v){return v==0xdeadbeef;}));
        assert(path==original_path);
        assert(std::all_of(path.begin()+8*L::path,path.end(),[](uint32_t v){return v==0xabcdef01u;}));
        assert(unknown[0]==0);'''
    require(text.count(anchor)==1,'Check anchor');text=text.replace(anchor,code,1)
    text=text.replace('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1','SHARED_SEARCH_EDGE_PATH_PASS transactions=2 search_path_words=4194304 shared_words=16777216 duplicate_append=1')
    tb=source/'test_shared_path.cpp';tb.write_text(text)
    files={str(p):digest(p) for p in base.iterdir()}
    for p in [edge,header,Path(__file__).resolve()]:files[str(p)]=digest(p)
    generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode));compile_cmd=['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_kernel_top.cpp'),str(source/'search_retained_edges_top.cpp'),'-o',str(binary)]
            for phase,cmd in [('compile',compile_cmd),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]:
                name=phase+'_'+str(mode);state['stage']=name;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(name+'.log')).open('x') as f:
                    child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env);state['child_pid']=child.pid;save();code=child.wait()
                (out/(name+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(name+'.log'))),indent=2)+'\n');require(code==0,'Shared path phase failed '+name)
            require('SHARED_SEARCH_EDGE_PATH_PASS transactions=2 search_path_words=4194304 shared_words=16777216 duplicate_append=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing shared path checks')
            state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed shared path input')
        state.update(status='complete',stage='both_modes_sanitizer_verified_device_ordering_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
