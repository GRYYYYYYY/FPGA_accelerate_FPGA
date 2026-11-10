#include "access_machine.hpp"
extern "C" void access_step(const uint32_t input[20],uint32_t output[6]){
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS INTERFACE ap_memory port=input depth=20
#pragma HLS INTERFACE ap_memory port=output depth=6
 using namespace search_access;
 Config c{input[6],input[7],input[8],input[9],input[10],int32_t(input[11]),int32_t(input[12]),int32_t(input[13]),int32_t(input[14]),int32_t(input[15]),int32_t(input[16]),int32_t(input[17]),int32_t(input[18]),int32_t(input[19])};
 State s{input[1],input[2],int32_t(input[3]),input[4]};bool ok=false;
 if(input[0]==0){s=start();ok=valid(c,s);}else if(input[0]==1)ok=accept(c,s,input[5]);
 output[0]=ok?0:1;output[1]=ok?s.phase:0;output[2]=ok?s.bits:0;
 output[3]=ok?uint32_t(s.aux):0;output[4]=ok?request(s):0;output[5]=ok?s.action:0;
}
