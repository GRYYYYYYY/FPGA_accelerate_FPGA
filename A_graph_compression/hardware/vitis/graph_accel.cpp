#include "graph_accel.hpp"
extern "C" void graph_accel(const uint32_t image[IMAGE_DEPTH],
    const uint32_t config[CFG_WORDS], const uint32_t requests[MAX_REQUESTS],
    uint32_t output[OUTPUT_DEPTH], uint32_t result[RESULT_DEPTH],
    uint32_t counts[2], uint32_t request_count, uint32_t output_capacity_words) {
#pragma HLS INTERFACE m_axi port=image offset=slave bundle=graph depth=33554432
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=control_data depth=32
#pragma HLS INTERFACE m_axi port=requests offset=slave bundle=control_data depth=65536
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=output_data depth=1048576
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_data depth=196608
#pragma HLS INTERFACE m_axi port=counts offset=slave bundle=output_data depth=2
#pragma HLS INTERFACE s_axilite port=image bundle=control
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=requests bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=counts bundle=control
#pragma HLS INTERFACE s_axilite port=request_count bundle=control
#pragma HLS INTERFACE s_axilite port=output_capacity_words bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    uint32_t written=0,failed=0;
    graph_expand_body(image,config,requests,output,result,request_count,output_capacity_words,written,failed);
    counts[0]=written;counts[1]=failed;
}
