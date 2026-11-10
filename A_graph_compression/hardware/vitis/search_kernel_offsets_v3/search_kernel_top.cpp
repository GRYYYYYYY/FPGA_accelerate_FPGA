#include "search_kernel.hpp"
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
#ifndef SEARCH_TOP_NAME
#define SEARCH_TOP_NAME search_kernel_top
#endif
// Build separately for Mode 0 (CSR) and Mode 1 (compact), at identical limits.
extern "C" void SEARCH_TOP_NAME(const uint32_t* image,const uint32_t* config,unsigned image_words,
        const uint32_t* roots,const uint64_t* packet,unsigned packet_words,
        uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,
        uint64_t* unknown_nodes,uint64_t* unknown_pips,uint32_t* path,
        uint64_t* meta,uint64_t* result) {
#pragma HLS INTERFACE m_axi port=image offset=slave bundle=graph_mem depth=33554432
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=input_mem depth=32
#pragma HLS INTERFACE m_axi port=roots offset=slave bundle=input_mem depth=1048576
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
#pragma HLS INTERFACE s_axilite port=roots bundle=control
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
    fpga_search::SearchKernel<SEARCH_GRAPH_MODE>::run(image,config,image_words,roots,packet,packet_words,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result);
}
