#include "geometry.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <cstdint>
extern "C" void geometry_step(const int32_t[13],uint32_t[4]);
struct Original {
 struct Conn {bool cross;int xMinBB,xMaxBB;bool isCrossSLR()const{return cross;}};
 struct Config {int maxDetourToSnapBackToPrevLagunaColumn;};
 struct Column {int value;int operator[](int)const{return value;}};
 int slr[2];int getSLRIndex(int id)const{return slr[id];}
 search_geometry::Result evaluate(const int32_t in[13]){
  int childX=in[0],childY=in[1],sinkX=in[2],sinkY=in[3];
  slr[0]=in[4];slr[1]=in[5];int childRnode=0,sinkRnode=1;
  Conn c{in[6]!=0,in[10],in[11]};int superLongLineLength=in[7];
  Column nextLagunaColumn{in[8]},prevLagunaColumn{in[9]};Config cfg{in[12]};
#include "original_geometry.inc"
  return {0,deltaX,deltaY,distanceToSink};
 }
};
int main(int argc,char**argv){
 Original original;
 if(argc>1&&std::strcmp(argv[1],"--probe-ub")==0){
  int32_t x[13]={100,10,200,20,0,1,1,60,120,(-2147483647-1),0,300,1};
  volatile auto result=original.evaluate(x);return result.distance==0;
 }
 FILE*f=std::fopen("vectors.txt","r"),*obs=std::fopen("observed.txt","w");if(!f||!obs)return 2;
 unsigned group,tmp,expected[4],actual[4];int32_t input[13];unsigned count=0,defined=0,errors=0;
 while(std::fscanf(f,"%u",&group)==1){
  for(int j=0;j<13;j++){if(std::fscanf(f,"%x",&tmp)!=1)return 3;std::memcpy(input+j,&tmp,4);}
  for(int j=0;j<4;j++)if(std::fscanf(f,"%x",expected+j)!=1)return 4;
  if(group==0){
   auto r=original.evaluate(input);uint32_t orig[4]={r.status,uint32_t(r.dx),uint32_t(r.dy),uint32_t(r.distance)};
   if(std::memcmp(orig,expected,16)){std::fprintf(stderr,"ORIGINAL_MISMATCH %u\n",count);return 5;}defined++;
  }
  geometry_step(input,actual);
  std::fprintf(obs,"%u %u %08x %08x %08x %08x\n",count,group,actual[0],actual[1],actual[2],actual[3]);
  if(std::memcmp(actual,expected,16)){std::fprintf(stderr,"GEOMETRY_MISMATCH %u\n",count);errors++;}
  count++;
 }
 std::fclose(f);std::fclose(obs);
 if(!count||!defined||errors)return 6;
 std::printf("GEOMETRY_PASS cases=%u defined_original=%u errors=%u\n",count,defined,errors);return 0;
}
