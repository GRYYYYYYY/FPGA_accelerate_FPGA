#include "exclusion_port.hpp"
#include <hls_stream.h>
namespace {
void load_input(std::uint32_t op,std::uint32_t parent,std::uint32_t child,std::uint32_t flags,std::uint32_t created,std::uint32_t lag,std::uint32_t generation,std::uint32_t phase,std::uint32_t value,hls::stream<exclusion_port::Command>& commands){
    exclusion_port::Command c={op,parent,child,flags,created,lag,generation,phase,value};commands.write(c);
}
void compute(hls::stream<exclusion_port::Command>& commands,hls::stream<exclusion_port::Reply>& replies){
    static exclusion_port::Controller<EXCLUSION_GENERATION_BITS> controller;
    const exclusion_port::Command command=commands.read();replies.write(controller.step(command));
}
void store_output(hls::stream<exclusion_port::Reply>& replies,std::uint32_t& status,std::uint32_t& generation,std::uint32_t& request,std::uint32_t& node,std::uint32_t& excluded){
    const exclusion_port::Reply reply=replies.read();status=reply.status;generation=reply.generation;request=reply.request;node=reply.node;excluded=reply.excluded;
}
}
void exclusion_step(std::uint32_t op,std::uint32_t parent,std::uint32_t child,std::uint32_t flags,std::uint32_t created,std::uint32_t has_laguna,std::uint32_t generation,std::uint32_t phase,std::uint32_t value,std::uint32_t& status,std::uint32_t& result_generation,std::uint32_t& request,std::uint32_t& node,std::uint32_t& excluded){
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS DATAFLOW
    hls::stream<exclusion_port::Command> commands;
    hls::stream<exclusion_port::Reply> replies;
#pragma HLS STREAM variable=commands depth=2
#pragma HLS STREAM variable=replies depth=2
    load_input(op,parent,child,flags,created,has_laguna,generation,phase,value,commands);
    compute(commands,replies);
    store_output(replies,status,result_generation,request,node,excluded);
}
