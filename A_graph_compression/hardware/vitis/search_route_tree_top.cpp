#include "search_route_tree.hpp"
// config8=[op,reset_nodes,reset_source,target,sink_count,0,0,0].
// op0 reset;1 accept raw search result/path;2 emit sorted roots;3 check sinks.
// result6=[status,unique_nodes,version,applied,roots_count,complete].
extern "C" void search_route_tree_top(const uint64_t* config,uint64_t* meta,uint64_t* bits,uint64_t* demands,
    const uint64_t* search_result,const uint32_t* path,const uint32_t* sinks,uint32_t* roots,uint64_t* result) {
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=8
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=meta_mem depth=5
#pragma HLS INTERFACE m_axi port=bits offset=slave bundle=tree_mem depth=16384
#pragma HLS INTERFACE m_axi port=demands offset=slave bundle=state_mem depth=65
#pragma HLS INTERFACE m_axi port=search_result offset=slave bundle=input_mem depth=81
#pragma HLS INTERFACE m_axi port=path offset=slave bundle=path_mem depth=4194304
#pragma HLS INTERFACE m_axi port=sinks offset=slave bundle=input_mem depth=1048576
#pragma HLS INTERFACE m_axi port=roots offset=slave bundle=output_mem depth=1048576
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=6
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=bits bundle=control
#pragma HLS INTERFACE s_axilite port=demands bundle=control
#pragma HLS INTERFACE s_axilite port=search_result bundle=control
#pragma HLS INTERFACE s_axilite port=path bundle=control
#pragma HLS INTERFACE s_axilite port=sinks bundle=control
#pragma HLS INTERFACE s_axilite port=roots bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    using Core=fpga_search::ProductionRouteTree;using Status=fpga_search::RouteTreeStatus;
    Status status=Status::invalid;bool applied=false,done=false;unsigned count=0;
    if(config[0]<=3 && config[1]<=UINT32_MAX && config[2]<=UINT32_MAX && config[3]<=UINT32_MAX &&
       config[4]<=UINT32_MAX && !config[5] && !config[6] && !config[7]) {
        const unsigned op=unsigned(config[0]);
        if(op==0 && !config[3] && !config[4])status=Core::reset(unsigned(config[1]),uint32_t(config[2]),meta,bits,demands);
        else if(op==1 && !config[1] && !config[2] && !config[4])status=Core::accept(uint32_t(config[3]),search_result,path,meta,bits,demands,applied);
        else if(op==2 && !config[1] && !config[2] && !config[3] && !config[4])status=Core::roots(meta,bits,roots,count);
        else if(op==3 && !config[1] && !config[2] && !config[3])status=Core::complete(meta,bits,sinks,unsigned(config[4]),done);
    }
    result[0]=uint64_t(status);result[1]=status==Status::ok?meta[3]:0;result[2]=status==Status::ok?meta[4]:0;
    result[3]=status==Status::ok?applied:0;result[4]=status==Status::ok?count:0;result[5]=status==Status::ok?done:0;
}
