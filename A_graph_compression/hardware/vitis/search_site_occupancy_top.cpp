#include "search_site_occupancy.hpp"
// config=[op,net,request_count,0,0,0,0,0]; op0 reset,1 replace,2 analyze,
// 3 advance,4 snapshot. Empty replace releases a net. result always overwritten:
// [status,owner_count,history_count,version,conflict_groups,snapshot_owner_count].
extern "C" void search_site_occupancy_top(const uint64_t* config,uint64_t* meta,
        uint64_t* owners,uint64_t* history,const uint64_t* request,uint32_t* flags,
        uint64_t* summaries,uint64_t* out_owners,uint64_t* out_history,uint64_t* result) {
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=8
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=meta_mem depth=6
#pragma HLS INTERFACE m_axi port=owners offset=slave bundle=owner_mem depth=524288
#pragma HLS INTERFACE m_axi port=history offset=slave bundle=history_mem depth=262144
#pragma HLS INTERFACE m_axi port=request offset=slave bundle=input_mem depth=196608
#pragma HLS INTERFACE m_axi port=flags offset=slave bundle=scratch_mem depth=65536
#pragma HLS INTERFACE m_axi port=summaries offset=slave bundle=scratch_mem depth=131072
#pragma HLS INTERFACE m_axi port=out_owners offset=slave bundle=output_mem depth=262144
#pragma HLS INTERFACE m_axi port=out_history offset=slave bundle=output_mem depth=131072
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=6
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=owners bundle=control
#pragma HLS INTERFACE s_axilite port=history bundle=control
#pragma HLS INTERFACE s_axilite port=request bundle=control
#pragma HLS INTERFACE s_axilite port=flags bundle=control
#pragma HLS INTERFACE s_axilite port=summaries bundle=control
#pragma HLS INTERFACE s_axilite port=out_owners bundle=control
#pragma HLS INTERFACE s_axilite port=out_history bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    using Core=fpga_search::ProductionSiteOccupancy;using Status=fpga_search::SiteOccupancyStatus;
    Status s=Status::invalid;unsigned groups=0,count=0;
    if(config[0]<=4 && config[1]<=UINT32_MAX && config[2]<=UINT32_MAX &&
       !config[3] && !config[4] && !config[5] && !config[6] && !config[7]) {
        const unsigned op=unsigned(config[0]);
        if(op==0 && !config[1] && !config[2])s=Core::reset(meta);
        else if(op==1)s=Core::replace(uint32_t(config[1]),request,unsigned(config[2]),meta,owners);
        else if(op==2 && !config[1] && !config[2])s=Core::analyze(meta,owners,flags,summaries,groups);
        else if(op==3 && !config[1] && !config[2])s=Core::advance(meta,owners,history,flags,summaries,groups);
        else if(op==4 && !config[2])s=Core::snapshot(uint32_t(config[1]),meta,owners,history,out_owners,out_history,count);
    }
    result[0]=uint64_t(s);result[1]=s==Status::ok?meta[2]:0;
    result[2]=s==Status::ok?meta[4]:0;result[3]=s==Status::ok?meta[5]:0;
    result[4]=s==Status::ok?groups:0;result[5]=s==Status::ok?count:0;
}
