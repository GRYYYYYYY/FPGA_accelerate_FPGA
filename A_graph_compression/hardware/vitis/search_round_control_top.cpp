#include "search_round_control.hpp"
extern "C" void search_round_control_top(const uint64_t* control,const uint32_t* counts,const uint32_t* complete,uint64_t* result){
#pragma HLS INTERFACE m_axi port=control offset=slave bundle=input_mem depth=8
#pragma HLS INTERFACE m_axi port=counts offset=slave bundle=count_mem depth=1048576
#pragma HLS INTERFACE m_axi port=complete offset=slave bundle=input_mem depth=65536
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_mem depth=8
#pragma HLS INTERFACE s_axilite port=control bundle=control
#pragma HLS INTERFACE s_axilite port=counts bundle=control
#pragma HLS INTERFACE s_axilite port=complete bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    fpga_search::RoundControl<>::run(control,counts,complete,result);
}
