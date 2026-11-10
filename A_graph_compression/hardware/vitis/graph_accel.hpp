#pragma once
#include "graph_body.hpp"
// Vitis ABI: six memory objects, followed by two scalar input arguments.
extern "C" void graph_accel(const uint32_t image[IMAGE_DEPTH],
    const uint32_t config[CFG_WORDS], const uint32_t requests[MAX_REQUESTS],
    uint32_t output[OUTPUT_DEPTH], uint32_t result[RESULT_DEPTH],
    uint32_t counts[2], uint32_t request_count, uint32_t output_capacity_words);

#ifndef __SYNTHESIS__
// Preserve the frozen testbench's golden-data contract while exercising the new top.
inline void graph_expand(const uint32_t* image,const uint32_t* config,const uint32_t* requests,
    uint32_t* output,uint32_t* result,uint32_t n,uint32_t capacity,uint32_t& written,uint32_t& failed) {
    uint32_t counts[2]={0xdecafbad,0xdecafbad};
    graph_accel(image,config,requests,output,result,counts,n,capacity);
    written=counts[0];failed=counts[1];
}
#endif
