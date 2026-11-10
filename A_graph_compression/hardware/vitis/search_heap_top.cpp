#include "search_heap.hpp"
// Component validation ABI: command = [opcode,cost,serial,label],
// response = [success,count,cost,serial,label]. opcode 1 pushes, 2 pops.
// Each call starts empty. Failed/popless operations emit zero payload.
extern "C" void search_heap_top(const uint64_t* commands, uint64_t* responses,
                                unsigned operations) {
#pragma HLS INTERFACE m_axi port=commands offset=slave bundle=input_mem depth=16384
#pragma HLS INTERFACE m_axi port=responses offset=slave bundle=output_mem depth=20480
#pragma HLS INTERFACE s_axilite port=commands bundle=control
#pragma HLS INTERFACE s_axilite port=responses bundle=control
#pragma HLS INTERFACE s_axilite port=operations bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    fpga_search::Entry heap[1023];
    unsigned count=0;
    // Reject an invalid transaction before accessing either buffer.
    if (operations>4096) return;
    for (unsigned i=0;i<operations;++i) {
#pragma HLS LOOP_TRIPCOUNT min=1 max=4096
        const uint64_t opcode=commands[4*i];
        fpga_search::Entry out{0,0,0};bool ok=false;
        if (opcode==1) {
            fpga_search::Entry in{commands[4*i+1],commands[4*i+2],commands[4*i+3]};
            ok=fpga_search::Heap<1023>::push(heap,count,in);
        } else if (opcode==2) ok=fpga_search::Heap<1023>::pop(heap,count,out);
        responses[5*i]=ok?1:0;responses[5*i+1]=count;
        responses[5*i+2]=out.cost;responses[5*i+3]=out.serial;responses[5*i+4]=out.label;
    }
}
