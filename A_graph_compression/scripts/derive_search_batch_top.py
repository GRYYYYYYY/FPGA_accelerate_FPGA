"""Compose actual net transactions and native-equivalent round/history control."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def derive():
    s=(ROOT/'hardware/vitis/search_net_top.cpp').read_text();start=s.index('extern "C" void SEARCH_TOP_NAME');opening=s.index(' {',start);decl=s[start:opening]
    prefix=s[:start].replace('#define SEARCH_TOP_NAME search_net_top','#define SEARCH_TOP_NAME search_batch_top')+'#include "search_round_control.hpp"\n'
    worker=decl.replace('extern "C" void SEARCH_TOP_NAME','static void net_worker')+s[opening:]
    worker='\n'.join(l for l in worker.splitlines() if not l.startswith('#pragma HLS INTERFACE'))+'\n'
    additions=[('const uint64_t*','batch_control','batch_input_mem',16),('const uint64_t*','query_table','query_mem',262144),('uint32_t*','complete_flags','completion_mem',65536),('uint32_t*','site_conflict_flags','site_scratch_mem',65536),('uint64_t*','site_summaries','site_scratch_mem',131072),('uint64_t*','round_result','output_mem',8),('uint64_t*','batch_result','output_mem',12)]
    top=decl.replace('const uint64_t* net_control,','').replace('const uint32_t* sinks,','const uint32_t* all_sinks,').replace('uint64_t* net_result)','uint64_t* net_result,\n        '+',\n        '.join(t+' '+n for t,n,_,_ in additions)+')')
    pragmas='\n'.join(l for l in s[opening:].splitlines() if l.startswith('#pragma HLS INTERFACE') and 'port=net_control ' not in l)+'\n'
    pragmas=pragmas.replace('port=sinks offset=slave bundle=sink_mem depth=1048576','port=all_sinks offset=slave bundle=sink_mem depth=4194304').replace('port=sinks bundle=control','port=all_sinks bundle=control')
    for _,n,b,d in additions:pragmas+=f'#pragma HLS INTERFACE m_axi port={n} offset=slave bundle={b} depth={d}\n#pragma HLS INTERFACE s_axilite port={n} bundle=control\n'
    body='''    // control16=[present_cap,max_iterations,nets,sink_pool_words,static_words,budget,reset_state,9 zeros].
    // query records4=[net,source,sink_first,sink_count]; unique net IDs and terminal reservations are prevalidated immutable inputs.
    // result12=[error,stage,core_status,rounds,nets_done,searches,found,routed,incomplete,node_groups,site_groups,history_advances].
    for(unsigned i=0;i<12;++i)batch_result[i]=0;
    using Node=fpga_search::ProductionNodeOccupancy;using Site=fpga_search::ProductionSiteOccupancy;
    using Retained=fpga_search::RetainedNodes<>;using Edges=fpga_search::RetainedEdges<>;using Round=fpga_search::RoundControl<>;
    if(!batch_control[0] || !batch_control[1] || batch_control[1]>UINT32_MAX || !batch_control[2] || batch_control[2]>65536 || batch_control[3]>4194304 ||
       batch_control[4]<16 || batch_control[4]>4194304 || !batch_control[5] || batch_control[5]>200000 || batch_control[6]>1){batch_result[0]=1;return;}
    for(unsigned i=7;i<16;++i)if(batch_control[i]){batch_result[0]=1;return;}
    if(static_image[0]!=fpga_search::ProductionResidentSnapshot::StaticMagic || static_image[1]!=batch_control[4] || !static_image[2] || static_image[2]>1048576){batch_result[0]=1;return;}
    const unsigned nodes=unsigned(static_image[2]),nets=unsigned(batch_control[2]);
    for(unsigned q=0;q<nets;++q){
        const unsigned at=4*q;const uint64_t first=query_table[at+2],count=query_table[at+3];
        if(query_table[at]>UINT32_MAX || query_table[at+1]>=nodes || first>batch_control[3] || count>1048576 || count>batch_control[3]-first){batch_result[0]=1;return;}
        for(unsigned i=0;i<unsigned(count);++i)if(all_sinks[first+i]>=nodes || (i && all_sinks[first+i]<all_sinks[first+i-1])){batch_result[0]=1;return;}
    }
    batch_result[1]=1;
    if(batch_control[6]){
        auto ns=Node::reset(nodes,node_meta,node_counts,node_history,node_flags);auto ss=Site::reset(site_meta);
        auto rs=Retained::reset(nodes,retained_meta);auto es=Edges::reset(nodes,edge_meta);
        if(ns!=fpga_search::OccupancyStatus::ok || ss!=fpga_search::SiteOccupancyStatus::ok || rs!=fpga_search::RetainedStatus::ok || es!=fpga_search::RetainedEdgeStatus::ok){batch_result[0]=2;return;}
    }
    if(!Node::valid_meta(node_meta) || !Site::valid(site_meta) || !Retained::valid(retained_meta) || !Edges::valid(edge_meta) || node_meta[1]!=nodes || retained_meta[1]!=nodes || edge_meta[1]!=nodes){batch_result[0]=2;return;}
    uint64_t present=1;
    for(unsigned iteration=0;iteration<unsigned(batch_control[1]);++iteration){
        batch_result[1]=2;
        for(unsigned q=0;q<nets;++q){
            const unsigned at=4*q;const uint64_t control[8]={query_table[at],query_table[at+1],present,batch_control[5],batch_control[4],query_table[at+3],0,0};
            net_worker(image,config,image_words,root_nodes,packet,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result,tree_meta,tree_bits,tree_demands,edge_meta,edge_rows,control_result,all_sinks+query_table[at+2],control,static_image,node_meta,node_counts,node_history,node_keys,node_flags,site_meta,site_owners,site_history,site_request,retained_meta,retained_rows,old_nodes,net_result);
            if(net_result[0]){batch_result[0]=3;batch_result[2]=net_result[0];return;}
            complete_flags[q]=uint32_t(net_result[5]);++batch_result[4];batch_result[5]+=net_result[3];batch_result[6]+=net_result[4];
        }
        batch_result[1]=3;unsigned site_groups=0;
        auto site_status=Site::analyze(site_meta,site_owners,site_conflict_flags,site_summaries,site_groups);
        if(site_status!=fpga_search::SiteOccupancyStatus::ok){batch_result[0]=4;batch_result[2]=uint64_t(site_status);return;}
        batch_result[1]=4;const uint64_t rc[8]={nodes,nets,iteration,batch_control[1],batch_control[0],site_groups,0,0};
        Round::run(rc,node_counts,complete_flags,round_result);
        if(round_result[0]){batch_result[0]=5;batch_result[2]=round_result[0];return;}
        ++batch_result[3];batch_result[8]=round_result[2];batch_result[9]=round_result[1];batch_result[10]=site_groups;
        if(round_result[6]){
            batch_result[1]=5;uint64_t node_groups=0;auto status=Node::advance(node_meta,node_counts,node_history,node_groups);
            if(status!=fpga_search::OccupancyStatus::ok || node_groups!=round_result[1]){batch_result[0]=6;batch_result[2]=uint64_t(status);return;}
            batch_result[1]=6;unsigned advanced_site_groups=0;site_status=Site::advance(site_meta,site_owners,site_history,site_conflict_flags,site_summaries,advanced_site_groups);
            if(site_status!=fpga_search::SiteOccupancyStatus::ok || advanced_site_groups!=site_groups){batch_result[0]=7;batch_result[2]=uint64_t(site_status);return;}
            ++batch_result[11];
        }
        if(round_result[3]!=2){batch_result[7]=round_result[3]==0;batch_result[1]=7;return;}
        present=round_result[5];
    }
    batch_result[0]=8; // Unreachable when the original round contract is respected.
}
'''
    return prefix+worker+'\n'+top+' {\n'+pragmas+body
if __name__=='__main__':
    with (ROOT/'hardware/vitis/search_batch_top.cpp').open('x') as f:f.write(derive())
