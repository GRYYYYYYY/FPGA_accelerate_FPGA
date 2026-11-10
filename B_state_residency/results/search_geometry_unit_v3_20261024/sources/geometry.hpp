#pragma once
#include <cstdint>
namespace search_geometry {
static const int64_t LIMIT=2147483647LL;
struct Scalar {uint32_t status;int32_t value;};
inline int64_t abs64(int64_t x){return x<0?-x:x;}
inline Scalar narrow(int64_t x){return x<0||x>LIMIT?Scalar{2,0}:Scalar{0,int32_t(x)};}
inline Scalar adjust_y(int64_t dy,int64_t slr_difference,int32_t length){
 if(slr_difference==1){
  if(length<0)return {4,0};
  if(dy<length)dy=2*int64_t(length)-dy;
 }
 return narrow(dy);
}
inline Scalar laguna_x(int32_t child_x,int32_t sink_x,int32_t next,int32_t prev,int32_t min_x,int32_t max_x){
 if(next==prev)return narrow(abs64(int64_t(child_x)-sink_x));
 bool has_next=next!=2147483647&&next<max_x;
 bool has_prev=prev!=(-2147483647-1)&&prev>min_x;
 if(!has_next&&!has_prev)return {1,0};
 int64_t dn=abs64(int64_t(next)-child_x),dp=abs64(int64_t(prev)-child_x);
 int64_t tn=dn+abs64(int64_t(sink_x)-next),tp=dp+abs64(int64_t(sink_x)-prev);
 // Original detour conditions select the same value as their fallback.
 // Choose the nearest usable column; equal distances choose the shorter total.
 int64_t dx=!has_prev?tn:!has_next?tp:dn<dp?tn:dp<dn?tp:tn<tp?tn:tp;
 return narrow(dx);
}
inline Scalar sum(int32_t dx,int32_t dy){return narrow(int64_t(dx)+dy);}
struct Result {uint32_t status;int32_t dx,dy,distance;};
inline Result evaluate(const int32_t in[13]){
 Scalar x=narrow(abs64(int64_t(in[0])-in[2]));
 Scalar y=narrow(abs64(int64_t(in[1])-in[3]));
 int64_t ds=abs64(int64_t(in[4])-in[5]);
 if(in[6]&&ds!=0){
  y=adjust_y(abs64(int64_t(in[1])-in[3]),ds,in[7]);
  if(y.status)return {y.status,0,0,0};
  x=laguna_x(in[0],in[2],in[8],in[9],in[10],in[11]);
 }
 if(x.status)return {x.status,0,0,0};
 if(y.status)return {y.status,0,0,0};
 Scalar d=sum(x.value,y.value);if(d.status)return {d.status,0,0,0};
 return {0,x.value,y.value,d.value};
}
}
