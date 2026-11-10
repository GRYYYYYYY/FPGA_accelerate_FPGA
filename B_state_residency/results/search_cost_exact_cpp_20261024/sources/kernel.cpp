#include "cost_api.hpp"
#include "softfloat32.hpp"
void cost_step(const std::uint32_t input[23],std::uint32_t output[5]) {
#pragma HLS INTERFACE ap_ctrl_hs port=return
#pragma HLS INTERFACE ap_memory port=input depth=23
#pragma HLS INTERFACE ap_memory port=output depth=5
 using namespace softfp;
 U sf=add(0x3f800000U,mul(input[0],from_int(std::int32_t(input[1]))));
 U bias=div(mul(div(input[2],from_int(std::int32_t(input[5]))),input[6]),from_int(std::int32_t(input[7])));
 U nc=div(mul(mul(input[2],input[3]),input[4]),sf);
 nc=add(nc,min(bias,div(nc,0x40000000U)));
 U pc=add(input[8],nc);
 pc=add(pc,div(mul(input[9],from_int(std::int32_t(input[10]))),sf));
 U h=mul(input[11],from_int(std::int32_t(input[12])));
 if(input[13]){
  int best=0;for(int i=0;i<8;i++){int d=int(input[15+i]&65535)-int(input[15+i]>>16)-1;if(d>best)best=d;}
  U alt=mul(from_int(best),input[14]);if(less(h,alt))h=alt;
 }
 U total=add(pc,div(h,sf));
 output[0]=sf;output[1]=nc;output[2]=pc;output[3]=h;output[4]=total;
}
