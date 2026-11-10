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
    out=ROOT/'data/derived/search_connection_cpu_20261025_v2';out.mkdir(exist_ok=False);source=out/'source'
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
    marker='    std::puts("SEARCH_CONNECTION_PASS transactions=2 internal_search_tree_edge_sequence=1 nonfound_preserves_tree_edges=1");'
    rejection=r"""    view.semantics_count=1;
    auto rejection_packet=search_kernel_host::packet<L>(view,2,1,8,{});
    unsigned rejection_words=unsigned(rejection_packet.size());rejection_packet.resize(fpga_search::SearchPacketMaxWords);
    unsigned checked_rejections=0;
    for(unsigned scenario=0;scenario<8;++scenario){
        tree_meta[4]=2;edge_meta[5]=2;
        unsigned supplied_words=rejection_words;
        unsigned wanted_overall=1,wanted_stage=0,wanted_tree=0,wanted_edge=0;
        if(scenario==0)edge_meta[0]=0;
        if(scenario==1)supplied_words=31;
        if(scenario==2)rejection_packet[4]=UINT64_C(1)<<32;
        if(scenario==3){rejection_packet[0]=0;wanted_overall=2;wanted_stage=1;}
        if(scenario==4){rejection_packet[8]=200001;wanted_overall=2;wanted_stage=1;}
        if(scenario==5){tree_meta[4]=UINT64_MAX;wanted_overall=3;wanted_stage=2;wanted_tree=3;}
        if(scenario==6){edge_meta[5]=UINT64_MAX;wanted_overall=4;wanted_stage=3;wanted_edge=3;}
        if(scenario==7){
            const uint32_t edge_words[8]={0,1,0,3,10,11,1,0};
            for(unsigned i=0;i<2097152;++i){edge_rows[9*i]=7;for(unsigned j=0;j<8;++j)edge_rows[9*i+1+j]=edge_words[j];}
            edge_meta[2]=2097152;edge_meta[3]=0;edge_meta[4]=1;
            wanted_overall=4;wanted_stage=3;wanted_edge=2;
        }
        const auto previous_rows=edge_rows,previous_bits=tree_bits;
        std::array<uint64_t,5> previous_tree{};std::copy(tree_meta,tree_meta+5,previous_tree.begin());
        std::array<uint64_t,6> previous_edge{};std::copy(edge_meta,edge_meta+6,previous_edge.begin());
        std::array<uint64_t,65> previous_demands{};std::copy(tree_demands,tree_demands+65,previous_demands.begin());
        std::array<uint64_t,81> previous_search{};std::copy(result,result+81,previous_search.begin());
        const uint64_t old_epoch=meta[0],old_records=meta[1];const auto previous_path=path;
        search_connection_top(fixture.data.data(),fixture.config.data(),image_words,roots.data(),rejection_packet.data(),supplied_words,heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result);
        assert(control_result[0]==wanted_overall && control_result[1]==wanted_stage && control_result[3]==wanted_tree && control_result[4]==wanted_edge);
        assert(edge_rows==previous_rows && std::equal(edge_meta,edge_meta+6,previous_edge.begin()));
        if(scenario<6){assert(std::equal(tree_meta,tree_meta+5,previous_tree.begin()) && tree_bits==previous_bits && std::equal(tree_demands,tree_demands+65,previous_demands.begin()) && !control_result[5]);}
        else {assert(tree_meta[4]==previous_tree[4]+1 && control_result[5]==1);}
        if(scenario<3){assert(std::equal(result,result+81,previous_search.begin()) && meta[0]==old_epoch && meta[1]==old_records && path==previous_path);}
        if(scenario==3)assert(control_result[2]==6);
        if(scenario==4)assert(control_result[2]==5);
        edge_meta[0]=UINT64_C(0x4152455445444731);rejection_packet[0]=UINT64_C(0x4153454152434831);rejection_packet[4]=7;rejection_packet[8]=8;
        ++checked_rejections;
    }
    assert(checked_rejections==8);
    std::puts("SEARCH_CONNECTION_REJECTION_PASS cases=8 preflight_no_search=3 search=2 tree=1 edge=2 edge_failure_keeps_accepted_tree=1");
"""
    require(s.count(marker)==1,'Missing final oracle marker');s=s.replace(marker,rejection+marker)

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
            require('SEARCH_CONNECTION_REJECTION_PASS cases=8 preflight_no_search=3 search=2 tree=1 edge=2 edge_failure_keeps_accepted_tree=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing rejection checks')
            require('SEARCH_CONNECTION_PASS transactions=2 internal_search_tree_edge_sequence=1 nonfound_preserves_tree_edges=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing connection checks')
            state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed connection input '+p)
        state.update(status='complete',stage='sanitizer_verified_hls_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
