#include "search_cost.hpp"
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <stdexcept>
static float fp(uint32_t v){float f;std::memcpy(&f,&v,4);return f;}
static uint32_t raw(float f){uint32_t v;std::memcpy(&v,&f,4);return v;}
static uint32_t rng=0xac18533d;static uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static FILE* file;static unsigned cases=0;
static void emit(unsigned group,const uint32_t x[23]){
 uint16_t target[8],child[8];for(int i=0;i<8;i++){target[i]=x[15+i]&65535;child[i]=x[15+i]>>16;}
 float sf=search_cost::sharing_factor(fp(x[0]),int32_t(x[1]));
 float nc=search_cost::node_cost(fp(x[2]),fp(x[3]),fp(x[4]),sf,int32_t(x[5]),fp(x[6]),int32_t(x[7]));
 float pc=search_cost::partial_cost(fp(x[8]),nc,fp(x[9]),int32_t(x[10]),sf);
 float h=search_cost::heuristic(fp(x[11]),int32_t(x[12]),x[13]!=0,target,child,fp(x[14]));
 float total=search_cost::total_cost(pc,h,sf);
 std::fprintf(file,"%u",group);for(int i=0;i<23;i++)std::fprintf(file," %08x",x[i]);
 for(float f:{sf,nc,pc,h,total})std::fprintf(file," %08x",raw(f));std::fprintf(file,"\n");++cases;
}
static void base(uint32_t x[23]){
 x[0]=raw(1);x[1]=0;x[2]=raw(1);x[3]=raw(1);x[4]=raw(1);x[5]=1;x[6]=raw(0);x[7]=1;
 x[8]=raw(0);x[9]=raw(0);x[10]=1;x[11]=raw(1);x[12]=1;x[13]=0;x[14]=raw(1);
 for(int i=15;i<23;i++)x[i]=0;
}
int main(int argc,char** argv){
 if(argc!=2)return 2;file=std::fopen(argv[1],"w");if(!file)return 3;
 uint32_t x[23];
 for(int n=0;n<4096;n++){
  base(x);for(int i:{0,2,3,4,6,8,9,11,14})x[i]=raw(float(rnd()%65536)/256);
  x[1]=rnd()%256;x[5]=1+rnd()%256;x[7]=1+rnd()%16384;x[10]=rnd()%1024;x[12]=rnd()%8192;x[13]=n%2;
  for(int i=15;i<23;i++)x[i]=rnd();emit(0,x);
 }
 const uint32_t special[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345};
 for(int i:{0,2,3,4,6,8,9,11,14})for(uint32_t v:special){base(x);x[i]=v;x[1]=1;x[13]=1;for(int k=15;k<23;k++)x[k]=5;emit(1,x);}
 for(int n=0;n<512;n++){
  base(x);for(int i:{0,2,3,4,6,8,9,11,14})x[i]=rnd();x[1]=int32_t(rnd());x[5]=int32_t(rnd());x[7]=int32_t(rnd());x[10]=int32_t(rnd());x[12]=int32_t(rnd());x[13]=n%2;
  for(int i=15;i<23;i++)x[i]=rnd();emit(2,x);
 }
 // Normal operands can produce subnormal intermediate results.
 for(int n=1;n<=24;n++){base(x);x[2]=0x00800000;x[5]=1u<<n;x[6]=raw(1);x[3]=raw(0.5f);emit(3,x);}
 std::fclose(file);std::printf("COST_VECTORS cases=%u normal=4096 special=144 random=512 underflow=24\n",cases);
}
