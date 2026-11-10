#include "search_heap_external.hpp"
// Component verification ABI, not a host launch per search operation.
// heap: 3*131072 uint64 words. meta: [in/out count, output status].
// Status 0=valid call, 1=invalid count, 2=invalid operations; rejected calls
// preserve count/heap/responses. Empty/full/unknown op is a failed response.
extern "C" void search_heap_external_top(uint64_t* heap,uint64_t* meta,
        const uint64_t* commands,uint64_t* responses,unsigned operations) {
#pragma HLS INTERFACE m_axi port=heap offset=slave bundle=heap_mem depth=393216
#pragma HLS INTERFACE m_axi port=meta offset=slave bundle=meta_mem depth=2
#pragma HLS INTERFACE m_axi port=commands offset=slave bundle=input_mem depth=16384
#pragma HLS INTERFACE m_axi port=responses offset=slave bundle=output_mem depth=20480
#pragma HLS INTERFACE s_axilite port=heap bundle=control
#pragma HLS INTERFACE s_axilite port=meta bundle=control
#pragma HLS INTERFACE s_axilite port=commands bundle=control
#pragma HLS INTERFACE s_axilite port=responses bundle=control
#pragma HLS INTERFACE s_axilite port=operations bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    const uint64_t initial=meta[0];
    if (initial>fpga_search::ExternalHeapCapacity) {meta[1]=1;return;}
    if (operations>4096) {meta[1]=2;return;}
    unsigned count=unsigned(initial);
    for (unsigned i=0;i<operations;++i) {
#pragma HLS PIPELINE off
#pragma HLS LOOP_TRIPCOUNT min=0 max=4096
        const uint64_t opcode=commands[4*i];fpga_search::Entry out{0,0,0};bool ok=false;
        if (opcode==1) {
            fpga_search::Entry entry{commands[4*i+1],commands[4*i+2],commands[4*i+3]};
            ok=fpga_search::ExternalHeap<fpga_search::ExternalHeapCapacity>::push(heap,count,entry);
        } else if (opcode==2) ok=fpga_search::ExternalHeap<fpga_search::ExternalHeapCapacity>::pop(heap,count,out);
        responses[5*i]=ok?1:0;responses[5*i+1]=count;
        responses[5*i+2]=out.cost;responses[5*i+3]=out.serial;responses[5*i+4]=out.label;
    }
    meta[0]=count;meta[1]=0;
}
