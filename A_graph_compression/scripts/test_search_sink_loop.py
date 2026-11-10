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
    out=ROOT/'data/derived/search_sink_loop_cpu_20261025_v1';out.mkdir(exist_ok=False);source=out/'source'
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3/source';shutil.copytree(base,source)
    proof=json.loads((base.parent/'plan.json').read_text());bound={**proof['files'],**proof['copied']}
    for p in base.iterdir():require(digest(p)==bound[str(p)],'Changed search core '+str(p))
    paths=[ROOT/'hardware/vitis'/name for name in ['search_sink_loop_top.cpp','search_route_tree.hpp','search_retained_edges.hpp','search_resident_snapshot.hpp','search_node_occupancy.hpp','search_site_occupancy.hpp']]
    for p in paths:shutil.copyfile(p,source/p.name)
    s=(source/'test_search_kernel_top.cpp').read_text()
    old_declaration=next(l for l in s.splitlines() if l.startswith('extern "C" void search_kernel_top'))
    top=(source/'search_sink_loop_top.cpp').read_text();declaration=top[top.index('extern "C" void SEARCH_TOP_NAME'):top.index(' {',top.index('extern "C" void SEARCH_TOP_NAME'))]+';'
    s=s.replace(old_declaration,declaration.replace('SEARCH_TOP_NAME','search_sink_loop_top'))
    s=s[:s.index('    for(unsigned transaction=0;transaction<2;++transaction){')]+r"""    uint64_t tree_meta[5]={UINT64_C(0x4154524545535431),4,0,1,1},tree_demands[65]{};
    std::vector<uint64_t> tree_bits(16384);tree_bits[0]=1;
    uint64_t edge_meta[6]={UINT64_C(0x4152455445444731),4,0,0,0,1},control_result[8]{};
    std::vector<uint32_t> edge_rows(37748736,0xdeadbeef),sinks(1048576,0xdeadbeef);
    sinks[0]=1;sinks[1]=sinks[2]=2;
    auto packet=search_kernel_host::packet<L>(view,2,1,8,{});unsigned packet_words=unsigned(packet.size());packet.resize(fpga_search::SearchPacketMaxWords);
    auto invoke=[&](unsigned count){search_sink_loop_top(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),packet_words,heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result,sinks.data(),count);};
    invoke(3);
    assert(control_result[0]==0 && control_result[1]==6 && control_result[2]==3 && control_result[3]==3 && control_result[4]==1 && control_result[5]==3 && control_result[6]==2 && control_result[7]==4);
    assert(meta[0]==3 && tree_meta[3]==3 && tree_meta[4]==4 && tree_bits[0]==7 && edge_meta[2]==2 && edge_meta[5]==4);
    assert(roots[0]==0 && roots[1]==1 && roots[2]==2 && packet[6]==2 && packet[7]==3 && result[0]==0 && result[7]==0);
    const uint32_t expected[18]={7,0,1,0,3,10,11,1,0,7,1,2,0,7,11,12,0,0};
    assert(edge_meta[3]==1 && std::equal(expected,expected+18,edge_rows.begin()+2097152*9));
    const auto saved_rows=edge_rows,saved_roots=roots,saved_path=path;const auto saved_packet=packet,saved_bits=tree_bits;
    const uint64_t tree_version=tree_meta[4],edge_version=edge_meta[5],epoch=meta[0];
    invoke(0);
    assert(!control_result[0] && control_result[2]==0 && control_result[3]==0 && control_result[4]==1 && control_result[5]==3 && control_result[6]==2);
    assert(tree_meta[4]==tree_version && edge_meta[5]==edge_version && meta[0]==epoch && edge_rows==saved_rows && roots==saved_roots && path==saved_path && packet==saved_packet && tree_bits==saved_bits);
    sinks[0]=2;sinks[1]=1;invoke(2);assert(control_result[0]==1 && control_result[1]==0);
    assert(tree_meta[4]==tree_version && edge_meta[5]==edge_version && meta[0]==epoch && edge_rows==saved_rows && roots==saved_roots && path==saved_path && packet==saved_packet && tree_bits==saved_bits);
    sinks[0]=4;invoke(1);assert(control_result[0]==1 && meta[0]==epoch && edge_rows==saved_rows && packet==saved_packet);
    // New independently initialized trusted net state; unknown semantics must stay incomplete.
    tree_meta[3]=1;tree_meta[4]=1;tree_bits[0]=1;std::fill(tree_demands,tree_demands+65,0);
    edge_meta[2]=0;edge_meta[3]=0;edge_meta[4]=0;edge_meta[5]=1;
    view.semantics_count=0;auto missing=search_kernel_host::packet<L>(view,2,1,8,{});packet_words=unsigned(missing.size());missing.resize(fpga_search::SearchPacketMaxWords);packet=missing;sinks[0]=2;
    invoke(1);
    assert(!control_result[0] && control_result[2]==1 && control_result[3]==0 && control_result[4]==0 && control_result[5]==1 && control_result[6]==0 && result[0]==3);
    assert(tree_meta[4]==1 && tree_bits[0]==1 && edge_meta[5]==1 && edge_rows==saved_rows);
    std::printf("SEARCH_SINK_LOOP_PASS mode=%u sorted_duplicate_sinks=3 empty=1 rejected=2 unknown_incomplete=1 internal_roots_patch_search_tree_edges=1\n",SEARCH_GRAPH_MODE);
}
"""
    tb=source/'test_search_sink_loop.cpp';tb.write_text(s)
    files={str(p):digest(p) for p in [*base.iterdir(),*paths,Path(__file__).resolve()]};generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode));commands=[('compile',['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_sink_loop_top.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]
            for name,cmd in commands:
                phase=name+'_'+str(mode);state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(phase+'.log')).open('x') as f:
                    child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Connection test failed '+phase)
            require('SEARCH_SINK_LOOP_PASS mode='+str(mode)+' sorted_duplicate_sinks=3 empty=1 rejected=2 unknown_incomplete=1 internal_roots_patch_search_tree_edges=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing sink loop checks')
            state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed connection input '+p)
        state.update(status='complete',stage='sanitizer_verified_hls_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
