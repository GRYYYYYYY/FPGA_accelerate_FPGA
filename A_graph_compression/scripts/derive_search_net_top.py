"""Compose existing bounded cores into one net transaction; preserve the source loop."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def derive():
    source=(ROOT/'hardware/vitis/search_sink_loop_top_v2.cpp').read_text()
    start=source.index('extern "C" void SEARCH_TOP_NAME');opening=source.index(' {',start)
    declaration=source[start:opening]
    helper=declaration.replace('extern "C" void SEARCH_TOP_NAME','static void sink_loop_worker')+source[opening:]
    helper='\n'.join(l for l in helper.splitlines() if not l.startswith('#pragma HLS INTERFACE'))+'\n'
    includes='\n'.join(l for l in source[:start].splitlines() if l.startswith('#include'))+'\n#include "search_retained_nodes.hpp"\n#include "search_site_request.hpp"\n#ifndef SEARCH_GRAPH_MODE\n#define SEARCH_GRAPH_MODE 0\n#endif\n#ifndef SEARCH_TOP_NAME\n#define SEARCH_TOP_NAME search_net_top\n#endif\n'
    extra=[('const uint64_t*','net_control','net_input_mem',8),('const uint64_t*','static_image','static_mem',4194304),('uint64_t*','node_meta','node_meta_mem',4),('uint32_t*','node_counts','node_count_mem',1048576),('uint64_t*','node_history','node_history_mem',1048576),('uint64_t*','node_keys','node_table_mem',2097152),('uint32_t*','node_flags','node_table_mem',2097152),('uint64_t*','site_meta','site_meta_mem',6),('uint64_t*','site_owners','site_owner_mem',524288),('uint64_t*','site_history','site_history_mem',262144),('uint64_t*','site_request','site_request_mem',196608),('uint64_t*','retained_meta','retained_meta_mem',6),('uint64_t*','retained_rows','retained_store_mem',4194304),('uint32_t*','old_nodes','old_node_mem',1048576),('uint64_t*','net_result','output_mem',8)]
    top=declaration.replace('unsigned packet_words,','').replace(',unsigned sink_count)',',\n        '+',\n        '.join(t+' '+n for t,n,_,_ in extra)+')')
    pragmas='\n'.join(l for l in source[opening:].splitlines() if l.startswith('#pragma HLS INTERFACE') and 'port=packet_words ' not in l and 'port=sink_count ' not in l)+'\n'
    for _,name,bundle,depth in extra:pragmas+=f'#pragma HLS INTERFACE m_axi port={name} offset=slave bundle={bundle} depth={depth}\n#pragma HLS INTERFACE s_axilite port={name} bundle=control\n'
    body='''    // net_control=[net,source,present,budget,static_words,sink_count,0,0].
    // net_result=[error,stage,core_status,processed,found,complete,nroots,edges].
    for(unsigned i=0;i<8;++i)net_result[i]=0;
    using Node=fpga_search::ProductionNodeOccupancy;using Site=fpga_search::ProductionSiteOccupancy;
    using Retained=fpga_search::RetainedNodes<>;using Tree=fpga_search::ProductionRouteTree;
    using Edges=fpga_search::RetainedEdges<>;using Snapshot=fpga_search::ProductionResidentSnapshot;
    if(net_control[0]>UINT32_MAX || net_control[1]>UINT32_MAX || !net_control[2] || !net_control[3] || net_control[3]>200000 ||
       net_control[4]<16 || net_control[4]>4194304 || net_control[5]>1048576 || net_control[6] || net_control[7] ||
       !Node::valid_meta(node_meta) || !Site::valid(site_meta) || !Retained::valid(retained_meta) || !Edges::valid(edge_meta) ||
       node_meta[1]!=static_image[2] || retained_meta[1]!=node_meta[1] || edge_meta[1]!=node_meta[1] || net_control[1]>=node_meta[1]){net_result[0]=1;return;}
    const uint32_t net=uint32_t(net_control[0]);const unsigned sink_count=unsigned(net_control[5]);
    for(unsigned i=0;i<sink_count;++i)if(sinks[i]>=node_meta[1] || (i && sinks[i]<sinks[i-1])){net_result[0]=1;return;}
    net_result[1]=1;unsigned old_count=0;
    auto retained_status=Retained::get(net,retained_meta,retained_rows,old_nodes,old_count);
    if(retained_status!=fpga_search::RetainedStatus::ok){net_result[0]=2;net_result[2]=uint64_t(retained_status);return;}
    net_result[1]=2;
    if(old_count){auto status=Node::update(net,old_nodes,old_count,root_nodes,0,node_meta,node_counts,node_keys,node_flags);
        if(status!=fpga_search::OccupancyStatus::ok){net_result[0]=2;net_result[2]=uint64_t(status);return;}}
    net_result[1]=3;
    auto site_status=Site::replace(net,site_request,0,site_meta,site_owners);
    if(site_status!=fpga_search::SiteOccupancyStatus::ok){net_result[0]=2;net_result[2]=uint64_t(site_status);return;}
    net_result[1]=4;
    auto tree_status=Tree::reset(unsigned(node_meta[1]),uint32_t(net_control[1]),tree_meta,tree_bits,tree_demands);
    if(tree_status!=fpga_search::RouteTreeStatus::ok){net_result[0]=2;net_result[2]=uint64_t(tree_status);return;}
    auto edge_status=Edges::update(net,old_nodes,0,false,edge_meta,edge_rows);
    if(edge_status!=fpga_search::RetainedEdgeStatus::ok){net_result[0]=2;net_result[2]=uint64_t(edge_status);return;}
    net_result[1]=5;
    const uint64_t build[16]={0,net,net_control[2],0,1,net_control[3],net_control[4],4194304,0,0,0,0,0,0,0,0};uint64_t snapshot_result[8]{};
    Snapshot::run(build,static_image,tree_demands,node_meta,node_counts,node_history,node_keys,node_flags,site_meta,site_owners,site_history,packet,snapshot_result);
    if(snapshot_result[0]){net_result[0]=2;net_result[2]=snapshot_result[0];return;}
    unsigned packet_words=unsigned(snapshot_result[1]);net_result[1]=6;
    sink_loop_worker(image,config,image_words,root_nodes,packet,packet_words,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result,tree_meta,tree_bits,tree_demands,edge_meta,edge_rows,control_result,sinks,sink_count);
    if(control_result[0]){net_result[0]=2;net_result[2]=control_result[0];return;}
    const unsigned nroots=unsigned(control_result[5]);net_result[1]=7;
    auto node_status=Node::update(net,old_nodes,0,root_nodes,nroots,node_meta,node_counts,node_keys,node_flags);
    if(node_status!=fpga_search::OccupancyStatus::ok){net_result[0]=2;net_result[2]=uint64_t(node_status);return;}
    net_result[1]=8;retained_status=Retained::replace(net,root_nodes,nroots,retained_meta,retained_rows);
    if(retained_status!=fpga_search::RetainedStatus::ok){net_result[0]=2;net_result[2]=uint64_t(retained_status);return;}
    net_result[1]=9;unsigned request_count=0;unsigned encode_status=fpga_search::SiteRequest<>::run(tree_demands,site_request,request_count);
    if(encode_status){net_result[0]=2;net_result[2]=encode_status;return;}
    site_status=Site::replace(net,site_request,request_count,site_meta,site_owners);
    if(site_status!=fpga_search::SiteOccupancyStatus::ok){net_result[0]=2;net_result[2]=uint64_t(site_status);return;}
    net_result[1]=10;net_result[3]=control_result[2];net_result[4]=control_result[3];net_result[5]=control_result[4];net_result[6]=nroots;net_result[7]=edge_meta[2];
}
'''
    return includes+helper+'\n'+top+' {\n'+pragmas+body
if __name__=='__main__':
    p=ROOT/'hardware/vitis/search_net_top.cpp'
    with p.open('x') as f:f.write(derive())
