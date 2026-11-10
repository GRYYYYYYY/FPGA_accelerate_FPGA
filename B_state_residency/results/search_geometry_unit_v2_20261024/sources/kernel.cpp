#include "geometry.hpp"
extern "C" void geometry_step(const int32_t input[13],uint32_t output[4]){
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS INTERFACE ap_memory port=input depth=13
#pragma HLS INTERFACE ap_memory port=output depth=4
 const search_geometry::Result r=search_geometry::evaluate(input);
 output[0]=r.status;output[1]=uint32_t(r.dx);output[2]=uint32_t(r.dy);output[3]=uint32_t(r.distance);
}
