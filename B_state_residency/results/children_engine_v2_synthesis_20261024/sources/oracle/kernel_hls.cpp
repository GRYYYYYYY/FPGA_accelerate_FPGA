#include "children_port.hpp"
void children_step(std::uint32_t op,std::uint32_t parent,std::uint32_t count,std::uint32_t prune,std::uint32_t query,std::uint32_t price,std::uint32_t generation,std::uint32_t position,std::uint32_t phase,std::uint32_t node,std::uint32_t value,std::uint32_t aux,std::uint32_t service_status,std::uint32_t& status,std::uint32_t& result_generation,std::uint32_t& request,std::uint32_t& result_position,std::uint32_t& result_node,std::uint32_t& result_parent,std::uint32_t& result_query,std::uint32_t& result_price,std::uint32_t& emitted,std::uint32_t& active,std::uint32_t& fault){
#pragma HLS INTERFACE ap_ctrl_hs port=return
    static children_port::Controller<CHILDREN_GENERATION_BITS> controller;
    const children_port::Command command={op,parent,count,prune,query,price,generation,position,phase,node,value,aux,service_status};
    const children_port::Reply reply=controller.step(command);
    status=reply.status;result_generation=reply.generation;request=reply.request;result_position=reply.position;result_node=reply.node;result_parent=reply.parent;result_query=reply.query;result_price=reply.price;emitted=reply.emitted;active=reply.active;fault=reply.fault;
}
