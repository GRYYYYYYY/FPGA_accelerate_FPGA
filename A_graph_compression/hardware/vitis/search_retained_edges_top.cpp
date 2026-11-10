#include "search_retained_edges.hpp"
// config8=[op,net,reset_nodes,count,0,0,0,0]; reset0/replace1/get2/append3.
// result5=[status,total_edges,total_nets,version,returned_edge_count].
extern "C" void search_retained_edges_top(const uint64_t* config,uint64_t* meta,uint32_t* rows,
    const uint32_t* path,uint32_t* output,uint64_t* result){
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=8
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=meta_mem depth=6
#pragma HLS INTERFACE m_axi port=rows offset=slave bundle=store_mem depth=37748736
#pragma HLS INTERFACE m_axi port=path offset=slave bundle=input_mem depth=16777216
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=output_mem depth=16777216
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=5
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=rows bundle=control
#pragma HLS INTERFACE s_axilite port=path bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    using Core=fpga_search::RetainedEdges<>;using Status=fpga_search::RetainedEdgeStatus;
    Status status=Status::invalid;unsigned count=0;
    if(config[0]<=3 && config[1]<=UINT32_MAX && config[2]<=UINT32_MAX && config[3]<=UINT32_MAX && !config[4] && !config[5] && !config[6] && !config[7]){
        if(config[0]==0 && !config[1] && !config[3])status=Core::reset(unsigned(config[2]),meta);
        else if((config[0]==1 || config[0]==3) && !config[2])status=Core::update(uint32_t(config[1]),path,unsigned(config[3]),config[0]==3,meta,rows);
        else if(config[0]==2 && !config[2] && !config[3])status=Core::get(uint32_t(config[1]),meta,rows,output,count);
    }
    result[0]=uint64_t(status);result[1]=status==Status::ok?meta[2]:0;result[2]=status==Status::ok?meta[4]:0;result[3]=status==Status::ok?meta[5]:0;result[4]=status==Status::ok?count:0;
}
