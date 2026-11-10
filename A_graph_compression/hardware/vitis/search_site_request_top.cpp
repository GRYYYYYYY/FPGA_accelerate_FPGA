#include "search_site_request.hpp"
extern "C" void search_site_request_top(const uint64_t* state,uint64_t* request,uint64_t* result){
#pragma HLS INTERFACE m_axi port=state offset=slave bundle=input_mem depth=65
#pragma HLS INTERFACE m_axi port=request offset=slave bundle=output_mem depth=196608
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=2
#pragma HLS INTERFACE s_axilite port=state bundle=control
#pragma HLS INTERFACE s_axilite port=request bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    unsigned count=0;result[0]=fpga_search::SiteRequest<>::run(state,request,count);result[1]=count;
}
