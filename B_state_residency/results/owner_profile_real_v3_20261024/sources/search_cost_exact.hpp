#pragma once
#include "softfloat32.hpp"
#include <cstring>
namespace search_cost_exact {
using softfp::U;
inline U bits(float f){U u;std::memcpy(&u,&f,4);return u;}
inline float fp(U u){float f;std::memcpy(&f,&u,4);return f;}
inline float sharing_factor(float weight,int count){return fp(softfp::add(softfp::mul(softfp::from_int(count),bits(weight)),0x3f800000U));}
inline float node_cost(float base,float hist,float present,float sharing,int connections,float distance,int hpwl){
 U bias=softfp::div(softfp::mul(softfp::div(bits(base),softfp::from_int(connections)),bits(distance)),softfp::from_int(hpwl));
 U node=softfp::div(softfp::mul(softfp::mul(bits(base),bits(hist)),bits(present)),bits(sharing));
 return fp(softfp::add(node,softfp::min(bias,softfp::div(node,0x40000000U))));
}
inline float partial_cost(float parent,float node,float wire_weight,int length,float sharing){
 U partial=softfp::add(bits(node),bits(parent));
 return fp(softfp::add(softfp::div(softfp::mul(softfp::from_int(length),bits(wire_weight)),bits(sharing)),partial));
}
inline float heuristic(float weight,int distance,bool landmarks,const std::uint16_t target[8],const std::uint16_t child[8],float scale){
 U h=softfp::mul(softfp::from_int(distance),bits(weight));
 if(landmarks){int best=0;for(int i=0;i<8;i++){int d=int(target[i])-int(child[i])-1;if(d>best)best=d;}
 U alt=softfp::mul(softfp::from_int(best),bits(scale));if(softfp::less(h,alt))h=alt;}
 return fp(h);
}
inline float total_cost(float partial,float h,float sharing){return fp(softfp::add(softfp::div(bits(h),bits(sharing)),bits(partial)));}
}
