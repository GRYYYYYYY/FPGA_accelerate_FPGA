#include "cost_center.hpp"
extern "C" void cost_center_step(const std::uint32_t input[4],std::uint32_t output[2]){
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS INTERFACE ap_memory port=input depth=4
#pragma HLS INTERFACE ap_memory port=output depth=2
 std::uint32_t distance;output[0]=cost_center::evaluate(input,distance);output[1]=distance;
}
