#include "search_kernel.hpp"
#include "search_route_tree.hpp"
#include "search_retained_edges.hpp"
#include "search_resident_snapshot.hpp"
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
#ifndef SEARCH_TOP_NAME
#define SEARCH_TOP_NAME search_sink_loop_top
#endif
// Build separately for Mode 0 (CSR) and Mode 1 (compact), at identical limits.
extern "C" void SEARCH_TOP_NAME(const uint32_t* image,const uint32_t* config,unsigned image_words,
        uint32_t* root_nodes,uint64_t* packet,unsigned packet_words,
        uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,
        uint64_t* unknown_nodes,uint64_t* unknown_pips,uint32_t* path,
        uint64_t* meta,uint64_t* result,
        uint64_t* tree_meta,uint64_t* tree_bits,uint64_t* tree_demands,
        uint64_t* edge_meta,uint32_t* edge_rows,uint64_t* control_result,const uint32_t* sinks,unsigned sink_count) {
#pragma HLS INTERFACE m_axi port=image offset=slave bundle=graph_mem depth=33554432
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=32
#pragma HLS INTERFACE m_axi port=root_nodes offset=slave bundle=input_mem depth=1048576
#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304
#pragma HLS INTERFACE m_axi port=heap offset=slave bundle=heap_mem depth=393216
#pragma HLS INTERFACE m_axi port=slots offset=slave bundle=index_mem depth=1048576
#pragma HLS INTERFACE m_axi port=records offset=slave bundle=record_mem depth=5242880
#pragma HLS INTERFACE m_axi port=keys offset=slave bundle=key_mem depth=34078720
#pragma HLS INTERFACE m_axi port=unknown_nodes offset=slave bundle=output_mem depth=16384
#pragma HLS INTERFACE m_axi port=unknown_pips offset=slave bundle=output_mem depth=1100754
#pragma HLS INTERFACE m_axi port=path offset=slave bundle=output_mem depth=4194304
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=output_mem depth=2
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=81
#pragma HLS INTERFACE s_axilite port=image bundle=control
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=image_words bundle=control
#pragma HLS INTERFACE s_axilite port=root_nodes bundle=control
#pragma HLS INTERFACE s_axilite port=packet bundle=control
#pragma HLS INTERFACE s_axilite port=packet_words bundle=control
#pragma HLS INTERFACE s_axilite port=heap bundle=control
#pragma HLS INTERFACE s_axilite port=slots bundle=control
#pragma HLS INTERFACE s_axilite port=records bundle=control
#pragma HLS INTERFACE s_axilite port=keys bundle=control
#pragma HLS INTERFACE s_axilite port=unknown_nodes bundle=control
#pragma HLS INTERFACE s_axilite port=unknown_pips bundle=control
#pragma HLS INTERFACE s_axilite port=path bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
#pragma HLS INTERFACE m_axi port=tree_meta offset=slave bundle=tree_meta_mem depth=5
#pragma HLS INTERFACE s_axilite port=tree_meta bundle=control
#pragma HLS INTERFACE m_axi port=tree_bits offset=slave bundle=tree_mem depth=16384
#pragma HLS INTERFACE s_axilite port=tree_bits bundle=control
#pragma HLS INTERFACE m_axi port=tree_demands offset=slave bundle=state_mem depth=65
#pragma HLS INTERFACE s_axilite port=tree_demands bundle=control
#pragma HLS INTERFACE m_axi port=edge_meta offset=slave bundle=edge_meta_mem depth=6
#pragma HLS INTERFACE s_axilite port=edge_meta bundle=control
#pragma HLS INTERFACE m_axi port=edge_rows offset=slave bundle=edge_store_mem depth=37748736
#pragma HLS INTERFACE s_axilite port=edge_rows bundle=control
#pragma HLS INTERFACE m_axi port=control_result offset=slave bundle=output_mem depth=8
#pragma HLS INTERFACE s_axilite port=control_result bundle=control
#pragma HLS INTERFACE m_axi port=sinks offset=slave bundle=sink_mem depth=1048576
#pragma HLS INTERFACE s_axilite port=sinks bundle=control
#pragma HLS INTERFACE s_axilite port=sink_count bundle=control
    // result=[error,stage,processed,found,complete,final_roots,edges,edge_version].
    // Search result remains the last actually executed search; no cross-stage rollback.
    for(unsigned i=0;i<8;++i)control_result[i]=0;
    using Tree=fpga_search::ProductionRouteTree;using Edges=fpga_search::RetainedEdges<>;
    using Snapshot=fpga_search::ProductionResidentSnapshot;
    if(packet_words<97 || packet_words>fpga_search::SearchPacketMaxWords || sink_count>1048576 ||
       packet[0]!=fpga_search::SearchPacketMagic || packet[1]!=packet_words || packet[4]>UINT32_MAX ||
       !packet[5] || !packet[8] || packet[8]>200000 || !Tree::valid(tree_meta) || !Edges::valid(edge_meta) ||
       tree_meta[1]!=packet[2] || edge_meta[1]!=packet[2]){control_result[0]=1;return;}
    for(unsigned i=0;i<sink_count;++i)if(sinks[i]>=tree_meta[1] || (i && sinks[i]<sinks[i-1])){control_result[0]=1;return;}
    for(unsigned i=14;i<32;++i)if(packet[i]){control_result[0]=1;return;}
    const uint64_t budget=packet[8];
    for(unsigned sink=0;sink<sink_count;++sink){
        control_result[1]=1;unsigned root_count=0;
        if(Tree::roots(tree_meta,tree_bits,root_nodes,root_count)!=fpga_search::RouteTreeStatus::ok){control_result[0]=2;return;}
        control_result[1]=2;
        const uint64_t patch[16]={1,0,0,sinks[sink],root_count,budget,0,packet_words,0,0,0,0,0,0,0,0};
        const uint64_t unused[1]{};const uint32_t unused32[1]{};uint64_t snapshot_result[8]{};
        Snapshot::run(patch,unused,tree_demands,unused,unused32,unused,unused,unused32,unused,unused,unused,packet,snapshot_result);
        if(snapshot_result[0]){control_result[0]=3;return;}
        control_result[1]=3;
        fpga_search::SearchKernel<SEARCH_GRAPH_MODE>::run(image,config,image_words,root_nodes,packet,packet_words,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result);
        if(result[0]>=5){control_result[0]=4;return;}
        control_result[1]=4;bool applied=false;
        if(Tree::accept(sinks[sink],result,path,tree_meta,tree_bits,tree_demands,applied)!=fpga_search::RouteTreeStatus::ok){control_result[0]=5;return;}
        if(result[0]==0){
            control_result[1]=5;
            if(Edges::update(uint32_t(packet[4]),path,unsigned(result[7]),true,edge_meta,edge_rows)!=fpga_search::RetainedEdgeStatus::ok){control_result[0]=6;return;}
            ++control_result[3];
        }
        ++control_result[2];
    }
    control_result[1]=6;bool complete=false;unsigned root_count=0;
    if(Tree::complete(tree_meta,tree_bits,sinks,sink_count,complete)!=fpga_search::RouteTreeStatus::ok ||
       Tree::roots(tree_meta,tree_bits,root_nodes,root_count)!=fpga_search::RouteTreeStatus::ok){control_result[0]=7;return;}
    control_result[4]=complete;control_result[5]=root_count;control_result[6]=edge_meta[2];control_result[7]=edge_meta[5];
}
