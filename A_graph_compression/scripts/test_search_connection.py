#!/usr/bin/env python3
"""Run actual integrated search/tree/edge hardware entry under sanitizers."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'data/derived/search_connection_cpu_20261025_v1';out.mkdir(exist_ok=False);source=out/'source'
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3/source';shutil.copytree(base,source)
    proof=json.loads((base.parent/'plan.json').read_text());bound={**proof['files'],**proof['copied']}
    for p in base.iterdir():require(digest(p)==bound[str(p)],'Changed search core '+str(p))
    paths=[ROOT/'hardware/vitis'/name for name in ['search_connection_top.cpp','search_route_tree.hpp','search_retained_edges.hpp']]
    for p in paths:shutil.copyfile(p,source/p.name)
    s=(source/'test_search_kernel_top.cpp').read_text().replace('search_kernel_top','search_connection_top')
    s=s.replace('uint64_t*,uint64_t*);','uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*);',1)
    anchor='    for(unsigned transaction=0;transaction<2;++transaction){'
    s=s.replace(anchor,'''    uint64_t tree_meta[5]={UINT64_C(0x4154524545535431),4,0,1,1},tree_demands[65]{};
    std::vector<uint64_t> tree_bits(16384);tree_bits[0]=1;
    uint64_t edge_meta[6]={UINT64_C(0x4152455445444731),4,0,0,0,1},control_result[8]{};
    std::vector<uint32_t> edge_rows(37748736,0xdeadbeef);
'''+anchor,1)
    s=s.replace('path.data(),meta,result);','path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result);',1)
    s=s.replace('        assert(unknown[0]==0);','''        assert(control_result[0]==0 && control_result[1]==4 && control_result[2]==result[0] && !control_result[3] && !control_result[4]);
        assert(control_result[5]==unsigned(!transaction) && control_result[6]==2 && control_result[7]==2);
        assert(tree_meta[3]==3 && tree_meta[4]==2 && tree_bits[0]==7);
        assert(edge_meta[2]==2 && edge_meta[3]==1 && edge_meta[4]==1 && edge_meta[5]==2);
        const uint32_t expected_rows[18]={7,0,1,0,3,10,11,1,0,7,1,2,0,7,11,12,0,0};
        assert(std::equal(expected_rows,expected_rows+18,edge_rows.begin()+2097152*9));
        assert(std::all_of(edge_rows.begin(),edge_rows.begin()+2097152*9,[](uint32_t v){return v==0xdeadbeef;}));
        assert(std::all_of(edge_rows.begin()+2097152*9+18,edge_rows.end(),[](uint32_t v){return v==0xdeadbeef;}));
        assert(unknown[0]==0);''',1)
    s=s.replace('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1','SEARCH_CONNECTION_PASS transactions=2 internal_search_tree_edge_sequence=1 nonfound_preserves_tree_edges=1')
    tb=source/'test_search_connection.cpp';tb.write_text(s)
    files={str(p):digest(p) for p in [*base.iterdir(),*paths,Path(__file__).resolve()]};generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode));commands=[('compile',['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_connection_top.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]
            for name,cmd in commands:
                phase=name+'_'+str(mode);state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(phase+'.log')).open('x') as f:
                    child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Connection test failed '+phase)
            require('SEARCH_CONNECTION_PASS transactions=2 internal_search_tree_edge_sequence=1 nonfound_preserves_tree_edges=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing connection checks')
            state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed connection input '+p)
        state.update(status='complete',stage='sanitizer_verified_hls_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
