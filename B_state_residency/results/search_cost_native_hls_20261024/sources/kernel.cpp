#include "cost_api.hpp"
#include "search_cost.hpp"
#include <cstring>
static float fp(std::uint32_t v){float f;std::memcpy(&f,&v,4);return f;}
static std::uint32_t raw(float f){std::uint32_t v;std::memcpy(&v,&f,4);return v;}
void cost_step(const std::uint32_t input[23],std::uint32_t output[5]) {
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS INTERFACE ap_memory port=input depth=23
#pragma HLS INTERFACE ap_memory port=output depth=5
    std::uint16_t target[8],child[8];
    for(int i=0;i<8;i++){target[i]=input[15+i]&65535;child[i]=input[15+i]>>16;}
    float sharing=search_cost::sharing_factor(fp(input[0]),(std::int32_t)input[1]);
    float node=search_cost::node_cost(fp(input[2]),fp(input[3]),fp(input[4]),sharing,
        (std::int32_t)input[5],fp(input[6]),(std::int32_t)input[7]);
    float partial=search_cost::partial_cost(fp(input[8]),node,fp(input[9]),(std::int32_t)input[10],sharing);
    float h=search_cost::heuristic(fp(input[11]),(std::int32_t)input[12],input[13]!=0,target,child,fp(input[14]));
    float total=search_cost::total_cost(partial,h,sharing);
    output[0]=raw(sharing);output[1]=raw(node);output[2]=raw(partial);output[3]=raw(h);output[4]=raw(total);
}
