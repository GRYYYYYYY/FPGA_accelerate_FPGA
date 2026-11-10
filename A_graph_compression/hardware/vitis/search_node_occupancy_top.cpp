#include "search_node_occupancy.hpp"
// Component ABI: op0 reset,1 update,2 advance history,3 snapshot.
// config=[op,net,node_count_for_reset,old_count,new_count,0,0,0].
// result=[status,live_pairs,version,conflict_node_count]; rejected operations
// leave persistent buffers/output unchanged. Result is always overwritten.
extern "C" void search_node_occupancy_top(const uint64_t* config,uint64_t* meta,
        uint32_t* counts,uint64_t* history,uint64_t* keys,uint32_t* flags,
        const uint32_t* old_nodes,const uint32_t* new_nodes,uint64_t* output,uint64_t* result) {
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=8
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=meta_mem depth=4
#pragma HLS INTERFACE m_axi port=counts offset=slave bundle=count_mem depth=1048576
#pragma HLS INTERFACE m_axi port=history offset=slave bundle=history_mem depth=1048576
#pragma HLS INTERFACE m_axi port=keys offset=slave bundle=table_mem depth=2097152
#pragma HLS INTERFACE m_axi port=flags offset=slave bundle=table_mem depth=2097152
#pragma HLS INTERFACE m_axi port=old_nodes offset=slave bundle=input_mem depth=1048576
#pragma HLS INTERFACE m_axi port=new_nodes offset=slave bundle=input_mem depth=1048576
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=output_mem depth=2097152
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=4
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=counts bundle=control
#pragma HLS INTERFACE s_axilite port=history bundle=control
#pragma HLS INTERFACE s_axilite port=keys bundle=control
#pragma HLS INTERFACE s_axilite port=flags bundle=control
#pragma HLS INTERFACE s_axilite port=old_nodes bundle=control
#pragma HLS INTERFACE s_axilite port=new_nodes bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    using Core=fpga_search::ProductionNodeOccupancy;using Status=fpga_search::OccupancyStatus;
    Status status=Status::invalid;uint64_t conflicts=0;
    if(config[0]<=3 && config[1]<=UINT32_MAX && config[2]<=UINT32_MAX &&
       config[3]<=UINT32_MAX && config[4]<=UINT32_MAX && !config[5] && !config[6] && !config[7]) {
        const unsigned op=unsigned(config[0]);
        if(op==0 && !config[3] && !config[4])status=Core::reset(unsigned(config[2]),meta,counts,history,flags);
        else if(op==1 && !config[2])status=Core::update(uint32_t(config[1]),old_nodes,unsigned(config[3]),
            new_nodes,unsigned(config[4]),meta,counts,keys,flags);
        else if(op==2 && !config[2] && !config[3] && !config[4])status=Core::advance(meta,counts,history,conflicts);
        else if(op==3 && !config[2] && !config[3] && !config[4])status=Core::snapshot(uint32_t(config[1]),
            meta,counts,history,keys,flags,output);
    }
    result[0]=uint64_t(status);result[1]=status==Status::ok?meta[2]:0;
    result[2]=status==Status::ok?meta[3]:0;result[3]=status==Status::ok?conflicts:0;
}
