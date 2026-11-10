#include "softfloat32.hpp"
#include <cstring>
#include <cstdio>
#include <stdexcept>
#include <string>
static uint32_t rng=0x1850dc3a;static uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static float fp(uint32_t u){float f;std::memcpy(&f,&u,4);return f;}
static uint32_t bits(float f){uint32_t u;std::memcpy(&u,&f,4);return u;}
// Volatile operand loads give an independent host IEEE calculation.
static uint32_t reference(unsigned op,uint32_t a,uint32_t b){volatile float x=fp(a),y=fp(b);float r;if(op==0)r=x+y;else if(op==1)r=x*y;else r=x/y;return bits(r);}
int main(){
 unsigned long long checks=0,nan_policy=0;
 const uint32_t edge[]={0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f7fffff,0x3f800000,0x3f800001,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345};
 for(unsigned i=0;i<1000256;i++){
  uint32_t a=i<256?edge[i/16]:rnd(),b=i<256?edge[i%16]:rnd();
  for(unsigned op=0;op<3;op++){
   auto expect=reference(op,a,b),got=op==0?softfp::add(a,b):(op==1?softfp::mul(a,b):softfp::div(a,b));
   if(expect!=got){
    // Both NaNs: C++ does not specify payload choice; our explicit policy is first operand.
    if(softfp::nan(a)&&softfp::nan(b)&&softfp::nan(expect)&&got==softfp::quiet(a)){nan_policy++;continue;}
    std::printf("MISMATCH i=%u op=%u a=%08x b=%08x got=%08x expected=%08x\n",i,op,a,b,got,expect);return 1;
   }checks++;
  }
  volatile int32_t iv=int32_t(a);if(softfp::from_int(iv)!=bits(float(iv)))throw std::runtime_error("int conversion");checks++;
  volatile float x=fp(a),y=fp(b);if(softfp::less(a,b)!=(x<y))throw std::runtime_error("comparison");checks++;
 }
 std::printf("SOFTFP_PRIMITIVES_PASS checks=%llu both_nan_payload_policy_cases=%llu inputs=1000256\n",checks,nan_policy);
}
