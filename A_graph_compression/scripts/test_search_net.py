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
    out=ROOT/'data/derived/search_net_cpu_20261025_v1';out.mkdir(exist_ok=False);source=out/'source'
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3/source';shutil.copytree(base,source)
    proof=json.loads((base.parent/'plan.json').read_text());bound={**proof['files'],**proof['copied']}
    for p in base.iterdir():require(digest(p)==bound[str(p)],'Changed search core '+str(p))
    paths=[ROOT/'hardware/vitis'/name for name in ['search_net_top.cpp','search_route_tree.hpp','search_retained_edges.hpp','search_retained_nodes.hpp','search_site_request.hpp','search_resident_snapshot.hpp','search_node_occupancy.hpp','search_site_occupancy.hpp']]
    for p in paths:shutil.copyfile(p,source/p.name)
    s=(source/'test_search_kernel_top.cpp').read_text()
    declaration=next(l for l in s.splitlines() if l.startswith('extern "C" void search_kernel_top'))
    top=(source/'search_net_top.cpp').read_text();start=top.index('extern "C" void SEARCH_TOP_NAME');prototype=top[start:top.index(' {',start)]+';'
    s=s.replace(declaration,prototype.replace('SEARCH_TOP_NAME','search_net_top'))
    s=s.replace('#include "search_kernel_packet.hpp"','#include "search_kernel_packet.hpp"\n#include "search_resident_snapshot.hpp"\n#include "search_retained_nodes.hpp"\n#include "search_retained_edges.hpp"')
    s=s[:s.index('    for(unsigned transaction=0;transaction<2;++transaction){')]+'    using Node=fpga_search::ProductionNodeOccupancy;using Site=fpga_search::ProductionSiteOccupancy;\n    std::vector<uint64_t> static_image(4194304),node_history(1048576),node_keys(2097152),site_owners(524288),site_history(262144),site_request(196608),retained_rows(4194304);\n    std::vector<uint32_t> node_counts(1048576),node_flags(2097152),old_nodes(1048576,0xdeadbeef),sinks(1048576,0xdeadbeef),edge_rows(37748736,0xdeadbeef);\n    uint64_t node_meta[4]{},site_meta[6]{},retained_meta[6]{},edge_meta[6]{},tree_meta[5]{},tree_demands[65]{},control_result[8]{},net_result[8]{};\n    std::vector<uint64_t> tree_bits(16384),packet(fpga_search::SearchPacketMaxWords);\n    assert(Node::reset(4,node_meta,node_counts.data(),node_history.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);\n    assert(Site::reset(site_meta)==fpga_search::SiteOccupancyStatus::ok);\n    assert(fpga_search::RetainedNodes<>::reset(4,retained_meta)==fpga_search::RetainedStatus::ok);\n    assert(fpga_search::RetainedEdges<>::reset(4,edge_meta)==fpga_search::RetainedEdgeStatus::ok);\n    static_image[0]=UINT64_C(0x41534e4150535431);static_image[1]=89;static_image[2]=4;static_image[3]=2;static_image[5]=1;static_image[6]=1;\n    static_image[17]=0x100;static_image[19]=3;typename W::Key requirement_key{};requirement_key.state=requirement[0];assert(W::store(static_image.data()+20,0,requirement_key));\n    std::copy(fixed,fixed+4,static_image.begin()+85);\n    uint64_t net_control[8]={7,0,4,8,89,3,0,0};sinks[0]=1;sinks[1]=sinks[2]=2;\n    auto invoke=[&](){search_net_top(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result,sinks.data(),net_control,static_image.data(),node_meta,node_counts.data(),node_history.data(),node_keys.data(),node_flags.data(),site_meta,site_owners.data(),site_history.data(),site_request.data(),retained_meta,retained_rows.data(),old_nodes.data(),net_result);};\n    for(unsigned reroute=0;reroute<2;++reroute){\n        invoke();assert(net_result[0]==0 && net_result[1]==10 && net_result[3]==3 && net_result[4]==3 && net_result[5]==1 && net_result[6]==3 && net_result[7]==2);\n        assert(node_meta[2]==3 && retained_meta[2]==3 && retained_meta[4]==1 && edge_meta[2]==2 && edge_meta[4]==1 && site_meta[2]==3 && site_meta[4]==0);\n        assert(node_counts[0]==1 && node_counts[1]==1 && node_counts[2]==1 && node_counts[3]==0);\n        assert(roots[0]==0 && roots[1]==1 && roots[2]==2 && tree_bits[0]==7 && tree_meta[4]==4);\n        assert(node_history[0]==0 && node_history[1]==0 && node_history[2]==0 && node_history[3]==0);\n        if(reroute)assert(old_nodes[0]==0 && old_nodes[1]==1 && old_nodes[2]==2);\n        const uint32_t literal[18]={7,0,1,0,3,10,11,1,0,7,1,2,0,7,11,12,0,0};\n        assert(std::equal(literal,literal+18,edge_rows.begin()+edge_meta[3]*2097152*9));\n        typename W::Key demand{};assert(W::load(tree_demands,0,demand) && !demand.node && demand.state.signals.count==1 && demand.state.bits.count==1 && demand.state.values.count==1);\n    }\n    // Unknown semantic resource: commit source only and keep the other net\'s edges.\n    static_image[1]=23;static_image[5]=0;std::copy(fixed,fixed+4,static_image.begin()+19);\n    net_control[0]=8;net_control[4]=23;net_control[5]=1;sinks[0]=2;invoke();\n    assert(!net_result[0] && net_result[3]==1 && !net_result[4] && !net_result[5] && net_result[6]==1 && net_result[7]==2 && result[0]==3);\n    assert(node_counts[0]==2 && node_counts[1]==1 && node_counts[2]==1 && node_meta[2]==4 && retained_meta[2]==4 && retained_meta[4]==2 && site_meta[2]==3);\n    // Empty sink list still commits its independent source, without a search.\n    const uint64_t previous_epoch=meta[0];net_control[0]=9;net_control[1]=3;net_control[5]=0;invoke();\n    assert(!net_result[0] && net_result[3]==0 && net_result[4]==0 && net_result[5]==1 && net_result[6]==1 && net_result[7]==2 && meta[0]==previous_epoch && node_counts[3]==1 && node_meta[2]==5 && retained_meta[2]==5);\n    const uint64_t node_version=node_meta[3],site_version=site_meta[5],retained_version=retained_meta[5],edge_version=edge_meta[5];\n    net_control[7]=1;invoke();assert(net_result[0]==1 && net_result[1]==0 && node_meta[3]==node_version && site_meta[5]==site_version && retained_meta[5]==retained_version && edge_meta[5]==edge_version && meta[0]==previous_epoch);\n    std::printf("SEARCH_NET_PASS mode=%u reroutes=2 unknown_incomplete=1 empty_complete=1 rejected=1 internal_release_snapshot_sinks_acquire_retention_site_commit=1\\n",SEARCH_GRAPH_MODE);\n}\n'
    tb=source/'test_search_net.cpp';tb.write_text(s)
    files={str(p):digest(p) for p in [*base.iterdir(),*paths,Path(__file__).resolve()]};generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode));commands=[('compile',['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_net_top.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]
            for name,cmd in commands:
                phase=name+'_'+str(mode);state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(phase+'.log')).open('x') as f:
                    child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Connection test failed '+phase)
            require('SEARCH_NET_PASS mode='+str(mode)+' reroutes=2 unknown_incomplete=1 empty_complete=1 rejected=1 internal_release_snapshot_sinks_acquire_retention_site_commit=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing net transaction checks')
            state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed connection input '+p)
        state.update(status='complete',stage='sanitizer_verified_hls_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
