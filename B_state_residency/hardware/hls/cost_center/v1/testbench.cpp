#include "cost_center.hpp"
#include <cstdio>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <array>
#include <random>
#include <fstream>
#include <vector>
#include <stdexcept>
extern "C" void cost_center_step(const uint32_t[4],uint32_t[2]);
static float fp(uint32_t u){float f;std::memcpy(&f,&u,4);return f;}
static uint32_t bits(float f){uint32_t u;std::memcpy(&u,&f,4);return u;}
struct Original {
 struct Net {float xCenter,yCenter;}nw;int32_t x,y;
 int32_t getEndTileXCoordinate(int)const{return x;}
 int32_t getEndTileYCoordinate(int)const{return y;}
 float run(const uint32_t in[4]){
  x=int32_t(in[0]);y=int32_t(in[1]);nw={fp(in[2]),fp(in[3])};int id=0;
#include "original_center.inc"
  return distToCenter;
 }
};
static void check(bool v){if(!v)throw std::runtime_error("center mismatch");}
int main(int argc,char**argv){
 check(argc==5);std::ofstream vectors(argv[4]);Original oracle;uint64_t count=0,rejected=0,real_count=0,sll_alt=0;
 auto test=[&](std::array<uint32_t,4> in){
  const bool finite=(in[2]&0x7f800000U)!=0x7f800000U&&(in[3]&0x7f800000U)!=0x7f800000U;
  uint32_t expected[2]={finite?0U:1U,finite?bits(oracle.run(in.data())):0U},out[2];cost_center_step(in.data(),out);check(out[0]==expected[0]&&out[1]==expected[1]);
  for(auto u:in)vectors<<std::hex<<u<<' ';vectors<<expected[0]<<' '<<expected[1]<<'\n';++count;rejected+=!finite;
 };
 const uint32_t special[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f000000,0xbf000000,0x3f800000,0xbf800000,0x4b800000,0xcb800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00001,0x7f800001};
 const int32_t coords[]={0,1,-1,32767,-32768,16777215,16777217,2147483647,(-2147483647-1)};
 for(auto x:coords)for(auto y:coords)for(auto a:special)for(auto b:special)test({uint32_t(x),uint32_t(y),a,b});
 std::mt19937 rng(20261025);for(int i=0;i<50000;++i)test({rng(),rng(),rng(),rng()});
 std::ifstream graph(argv[1],std::ios::binary),nets(argv[2],std::ios::binary);check(bool(graph)&&bool(nets));uint32_t n=std::stoul(argv[3]);
 for(uint32_t net=0;net<27960;++net){
  uint32_t record[4];nets.read((char*)record,16);check(bool(nets));uint32_t node=(uint64_t(net)*65537+17)%n;unsigned char attr[32];graph.seekg(uint64_t(node)*32);graph.read((char*)attr,32);check(bool(graph));
  auto s16=[&](int i){return int32_t(int16_t(uint16_t(attr[i])|(uint16_t(attr[i+1])<<8)));};
  test({uint32_t(s16(14)),uint32_t(s16(16)),record[0],record[1]});++real_count;
  if(attr[8]==5){test({uint32_t(s16(14)),uint32_t(s16(12)),record[0],record[1]});++sll_alt;}
 }
 std::printf("COST_CENTER_CPU_PASS cases=%llu rejected=%llu real_samples=%llu sll_alternate=%llu\n",(unsigned long long)count,(unsigned long long)rejected,(unsigned long long)real_count,(unsigned long long)sll_alt);
}
