#!/usr/bin/env python3
"""Check actual all-net/round entry at complete capacities under sanitizers."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=ROOT/'data/derived/search_net_cpu_20261025_v1';p=json.loads((prior/'plan.json').read_text())
    for path,h in {**p['files'],**p['generated']}.items():require(digest(path)==h,'Changed net baseline')
    out=ROOT/'data/derived/search_batch_cpu_20261025_v1';out.mkdir(exist_ok=False);source=out/'source';shutil.copytree(prior/'source',source)
    top=ROOT/'hardware/vitis/search_batch_top.cpp';round_header=ROOT/'hardware/vitis/search_round_control.hpp'
    for path in [top,round_header]:shutil.copyfile(path,source/path.name)
    tb=source/'test_search_batch.cpp';text=(source/'test_search_net.cpp').read_text();a=text.index('extern "C" void search_net_top');b=text.index(';',a)+1
    raw=top.read_text();start=raw.index('extern "C" void SEARCH_TOP_NAME');decl=raw[start:raw.index(' {',start)].replace('SEARCH_TOP_NAME','search_batch_top')+';'
    text=text[:a]+decl+text[b:];text=text[:text.index('    uint64_t net_control[8]')]
    text=text.replace('sinks(1048576,0xdeadbeef)','sinks(4194304,0xdeadbeef)')
    text+='''    std::vector<uint64_t> query_table(262144),site_summaries(131072);
    std::vector<uint32_t> complete_flags(65536,0xdeadbeef),site_conflict_flags(65536);
    uint64_t round_result[8]{},batch_result[12]{},batch_control[16]={8,80,2,3,93,8,1,0,0,0,0,0,0,0,0,0};
    const uint64_t schedule[8]={7,0,0,3,8,3,3,0};std::copy(schedule,schedule+8,query_table.begin());sinks[0]=1;sinks[1]=sinks[2]=2;
    std::fill(static_image.begin(),static_image.end(),0);static_image[0]=UINT64_C(0x41534e4150535431);static_image[1]=93;static_image[2]=4;static_image[3]=2;static_image[5]=1;static_image[6]=1;static_image[7]=4;
    for(unsigned i=0;i<4;++i)static_image[17+i]=(uint64_t(i)<<32)|(i==3?8:7);
    static_image[21]=0x100;static_image[23]=3;assert(W::store(static_image.data()+24,0,requirement_key));std::copy(fixed,fixed+4,static_image.begin()+89);
    auto invoke=[&](){search_batch_top(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result,sinks.data(),static_image.data(),node_meta,node_counts.data(),node_history.data(),node_keys.data(),node_flags.data(),site_meta,site_owners.data(),site_history.data(),site_request.data(),retained_meta,retained_rows.data(),old_nodes.data(),net_result,batch_control,query_table.data(),complete_flags.data(),site_conflict_flags.data(),site_summaries.data(),round_result,batch_result);};
    invoke();
    assert(!batch_result[0] && batch_result[1]==7 && batch_result[3]==1 && batch_result[4]==2 && batch_result[5]==3 && batch_result[6]==3 && batch_result[7]==1 && !batch_result[8] && !batch_result[9] && !batch_result[10] && !batch_result[11]);
    assert(complete_flags[0]==1 && complete_flags[1]==1 && round_result[3]==0 && round_result[6]==0);
    for(unsigned i=0;i<4;++i)assert(node_counts[i]==1 && node_history[i]==0);
    assert(retained_meta[2]==4 && retained_meta[4]==2 && edge_meta[2]==2 && site_meta[2]==3);
    // Explicit trusted component-state seed for an unsatisfiable persistent conflict.
    assert(Node::reset(4,node_meta,node_counts.data(),node_history.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
    assert(Site::reset(site_meta)==fpga_search::SiteOccupancyStatus::ok);
    assert(fpga_search::RetainedNodes<>::reset(4,retained_meta)==fpga_search::RetainedStatus::ok);
    assert(fpga_search::RetainedEdges<>::reset(4,edge_meta)==fpga_search::RetainedEdgeStatus::ok);
    uint32_t occupied_node=1;
    assert(Node::update(77,nullptr,0,&occupied_node,1,node_meta,node_counts.data(),node_keys.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
    assert(fpga_search::RetainedNodes<>::replace(77,&occupied_node,1,retained_meta,retained_rows.data())==fpga_search::RetainedStatus::ok);
    batch_control[1]=2;batch_control[6]=0;invoke();
    assert(!batch_result[0] && batch_result[3]==2 && batch_result[4]==4 && batch_result[5]==6 && batch_result[6]==6 && !batch_result[7] && !batch_result[8] && batch_result[9]==1 && !batch_result[10] && batch_result[11]==2);
    assert(round_result[3]==1 && round_result[6]==1 && round_result[7]==2 && node_counts[1]==2 && node_history[1]==2 && retained_meta[2]==5 && retained_meta[4]==3);
    // No conflict + incomplete => terminate immediately with no history update.
    static_image[1]=27;static_image[5]=0;std::copy(fixed,fixed+4,static_image.begin()+23);
    batch_control[1]=80;batch_control[4]=27;batch_control[6]=1;invoke();
    assert(!batch_result[0] && batch_result[3]==1 && batch_result[4]==2 && batch_result[5]==3 && !batch_result[6] && !batch_result[7] && batch_result[8]==1 && !batch_result[9] && !batch_result[10] && !batch_result[11]);
    assert(complete_flags[0]==0 && complete_flags[1]==1 && round_result[3]==1 && round_result[6]==0 && retained_meta[2]==2 && edge_meta[2]==0);
    for(unsigned i=0;i<4;++i)assert(node_history[i]==0);
    const uint64_t version=node_meta[3],epoch=meta[0];batch_control[2]=0;invoke();assert(batch_result[0]==1 && !batch_result[1] && node_meta[3]==version && meta[0]==epoch);
    assert(std::all_of(complete_flags.begin()+2,complete_flags.end(),[](uint32_t v){return v==0xdeadbeef;}));
    std::printf("SEARCH_BATCH_PASS mode=%u routed=1 persistent_conflict_rounds=2 final_history_advance=1 incomplete_early_stop=1 invalid=1\\n",SEARCH_GRAPH_MODE);
}
'''
    tb.write_text(text);files={str(path):digest(path) for path in [top,round_header,ROOT/'scripts/derive_search_batch_top.py',Path(__file__).resolve(),prior/'plan.json']};files.update(p['files']);files.update(p['generated']);generated={str(path):digest(path) for path in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n');state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode));jobs=[('compile',['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_batch_top.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]
            for name,cmd in jobs:
                phase=name+'_'+str(mode);state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(phase+'.log')).open('x') as f:
                    child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Batch test failed '+phase)
            require('SEARCH_BATCH_PASS mode='+str(mode)+' routed=1 persistent_conflict_rounds=2 final_history_advance=1 incomplete_early_stop=1 invalid=1' in (out/('run_'+str(mode)+'.log')).read_text(),'Missing batch control scope');state['completed'].append(mode);save()
        for path,h in {**files,**generated}.items():require(digest(path)==h,'Changed batch input')
        state.update(status='complete',stage='both_modes_sanitizer_verified_hls_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
