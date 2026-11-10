#include "frontier_api.hpp"
#include "frontier_bounded.hpp"
#include <hls_stream.h>
namespace {
struct Command {std::uint32_t op,key_bits,id;};
struct Response {std::uint32_t status,key_bits,id,size;};
static void load_input(std::uint32_t op,std::uint32_t key_bits,std::uint32_t id,
                       hls::stream<Command>& commands) {
    Command request={op,key_bits,id};commands.write(request);
}
static void compute(hls::stream<Command>& commands,hls::stream<Response>& responses) {
    static frontier::Entry heap[frontier::capacity];
    static std::uint32_t size=0;
    const Command request=commands.read();
    Response response={frontier::OK,0,0,0};frontier::Entry entry={request.key_bits,request.id};
    if(request.op==frontier::CLEAR)size=0;
    else if(request.op==frontier::OFFER) {
        if(!frontier::offer(heap,size,entry))response.status=frontier::FULL;
    } else if(request.op==frontier::POLL) {
        if(!frontier::poll(heap,size,entry))response.status=frontier::EMPTY;
        else {response.key_bits=entry.key_bits;response.id=entry.id;}
    } else if(request.op!=frontier::SIZE)response.status=frontier::BAD;
    response.size=size;responses.write(response);
}
static void store_output(hls::stream<Response>& responses,std::uint32_t& status,
                         std::uint32_t& key_bits,std::uint32_t& id,std::uint32_t& size) {
    const Response response=responses.read();status=response.status;
    key_bits=response.key_bits;id=response.id;size=response.size;
}
}
void frontier_step(std::uint32_t op,std::uint32_t key_bits,std::uint32_t id,
                   std::uint32_t& status,std::uint32_t& result_bits,
                   std::uint32_t& result_id,std::uint32_t& size) {
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS DATAFLOW
    hls::stream<Command> commands;
    hls::stream<Response> responses;
#pragma HLS STREAM variable=commands depth=2
#pragma HLS STREAM variable=responses depth=2
    load_input(op,key_bits,id,commands);
    compute(commands,responses);
    store_output(responses,status,result_bits,result_id,size);
}
