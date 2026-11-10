#!/usr/bin/env python3
"""Derive an isolated exact-trace diagnostic top from the frozen batch entry."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def once(s,a,b):
    assert s.count(a)==1, (a,s.count(a))
    return s.replace(a,b)
def derive():
    s=(ROOT/'hardware/vitis/search_batch_top.cpp').read_text()
    s=s.replace('#define SEARCH_TOP_NAME search_batch_top','#define SEARCH_TOP_NAME search_batch_trace_top')
    s='#include "search_trace_records.hpp"\n#include "search_round_trace.hpp"\n#include "search_batch_trace_frames.hpp"\n'+s
    s=once(s,'const uint32_t* sinks,unsigned sink_count) {','const uint32_t* sinks,unsigned sink_count,uint64_t trace_iteration,unsigned trace_query,uint64_t* trace_meta,uint64_t* trace_data) {')
    s=once(s,'uint64_t* net_result) {','uint64_t* net_result,uint64_t trace_iteration,unsigned trace_query,uint64_t* trace_meta,uint64_t* trace_data) {')
    # Capture search before its roots/path/demand buffers can be overwritten.
    needle='        if(result[0]>=5)'
    pos=s.index(needle)
    s=s[:pos]+'''        fpga_search::SearchTraceV2<>::search(trace_iteration,(uint64_t(trace_query)<<32)|sink,sinks[sink],unsigned(tree_meta[1]),root_nodes,root_count,result,path,unknown_nodes,unknown_pips,trace_meta,trace_data);
'''+s[pos:]
    s=once(s,'control_result,sinks,sink_count);','control_result,sinks,sink_count,trace_iteration,trace_query,trace_meta,trace_data);')
    start=s.index('extern "C" void SEARCH_TOP_NAME');opening=s.index(' {',start)
    declaration=s[start:opening]
    declaration=declaration[:-1]+',\n        const uint64_t* trace_control,uint64_t* trace_meta,uint64_t* trace_data)'
    body=s[opening+2:];lines=body.splitlines()
    pragmas='\n'.join(l for l in lines if l.startswith('#pragma HLS INTERFACE'))+'\n'
    body='\n'.join(l for l in lines if not l.startswith('#pragma HLS INTERFACE'))+'\n'
    body=once(body,'old_nodes,net_result);','old_nodes,net_result,iteration,q,trace_meta,trace_data);')
    needle='            complete_flags[q]=uint32_t(net_result[5]);'
    body=once(body,needle,'''            fpga_search::SearchTraceRecords<>::net(iteration,q,uint32_t(control[0]),root_nodes,unsigned(net_result[6]),net_result,tree_demands,tree_meta,node_meta,node_counts,node_history,node_keys,node_flags,retained_meta,retained_rows,edge_meta,edge_rows,site_meta,site_owners,trace_meta,trace_data);
'''+needle)
    needle='        if(round_result[6]){'
    body=once(body,needle,'''        fpga_search::RoundTrace<>::write(0,rc,round_result,complete_flags,node_meta,node_counts,node_history,site_meta,site_owners,site_history,site_groups,site_summaries,trace_meta,trace_data);
'''+needle)
    body=once(body,'            ++batch_result[11];','''            ++batch_result[11];
            fpga_search::RoundTrace<>::write(1,rc,round_result,complete_flags,node_meta,node_counts,node_history,site_meta,site_owners,site_history,site_groups,site_summaries,trace_meta,trace_data);''')
    worker=declaration.replace('extern "C" void SEARCH_TOP_NAME','static void batch_worker')+' {'+body
    args=[]
    for part in declaration[declaration.index('(')+1:-1].split(','):
        args.append(re.search(r'(\w+)\s*$',part).group(1))
    for name,depth in [('trace_control',8),('trace_meta',8),('trace_data',16777216)]:
        pragmas+=f'#pragma HLS INTERFACE m_axi port={name} offset=slave bundle=trace_mem depth={depth}\n#pragma HLS INTERFACE s_axilite port={name} bundle=control\n'
    wrapper=declaration+' {\n'+pragmas+'''    using Trace=fpga_search::SearchTraceV2<>;
    for(unsigned i=0;i<12;++i)batch_result[i]=0;
    if(trace_control[0]>16777216 || !trace_control[0]){batch_result[0]=9;return;}
    Trace::reset(unsigned(trace_control[0]),trace_meta);
    for(unsigned i=1;i<8;++i)if(trace_control[i]){Trace::reject(trace_meta,1);batch_result[0]=9;return;}
    fpga_search::BatchTraceFrames<>::begin(batch_control,query_table,all_sinks,trace_meta,trace_data);
    if(trace_meta[4]){batch_result[0]=9;return;}
    batch_worker('''+','.join(args)+''');
    fpga_search::BatchTraceFrames<>::terminal(batch_result,trace_meta,trace_data);
}
'''
    return s[:start]+worker+'\n'+wrapper
if __name__=='__main__':
    p=ROOT/'hardware/vitis/search_batch_trace_top.cpp'
    text=derive()
    assert not p.exists() or p.stat().st_size==0
    p.write_text(text)
