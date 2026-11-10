#include "search_cost.hpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <limits>
#include <stdexcept>
#include <vector>
#include <climits>
struct Base {
 struct Attr {float baseCost=1;int length=1,endX=0,endY=0,beginX=0,beginY=0;int occCnt=0;} ns[4],hot[4];
 using HotExpand=Attr;
 struct Label {float hist=1,upstream=0;int prev=-1;} dyn[4];
 struct NetWrapper {float xCenter=0,yCenter=0;int connectionsSize=1;int doubleHpwl=1;} nets[1];
 struct Connection {int netIdx=0,sinkRnode=2,xMaxBB=200,xMinBB=-1;bool cross=false;bool isCrossSLR()const{return cross;}} connections[1];
 struct Config {int maxDetourToSnapBackToPrevLagunaColumn=0;}cfg;
 struct State {int connIdx=0;float shareWeight=1,rnodeWLWeight=1,estWlWeight=1;uint16_t lmkT[8]{};};
 bool occLocking=false,useHotExpand=false,lmkReady=false;
 float lmkInvScale=0;int superLongLineLength=60;
 std::vector<uint16_t> lmk=std::vector<uint16_t>(32);
 int nextLagunaColumn[256]{},prevLagunaColumn[256]{},slr[4]{},uses[4]{},occupancy[4]{};
 float presentCongestionCosts[32]{};
 std::vector<int> accesses;float g=0,f=0;int pushed=-1;bool look=false,reverse_y=false;
 Label& label(int id){accesses.push_back(id);return dyn[id];}
 int getOccupancy(int id)const{return occupancy[id];}
 float getPresentCongestionCost(int occ)const{return presentCongestionCosts[occ];}
 float getPresentCongestionCostOf(int id)const{return presentCongestionCosts[occupancy[id]];}
 int getEndTileXCoordinate(int id)const{return ns[id].endX;}
 int getEndTileYCoordinate(int id)const{return reverse_y&&id==1&&dyn[id].prev==0?ns[id].beginY:ns[id].endY;}
 int getBeginTileXCoordinate(int id)const{return ns[id].beginX;}
 int getBeginTileYCoordinate(int id)const{return ns[id].beginY;}
 int searchEndY(int id)const{return getEndTileYCoordinate(id);}
 int getSLRIndex(int id)const{return slr[id];}
 int searchCountUser(int id,int)const{return uses[id];}
 void push(State&,int child,float partial,float total,bool ahead){pushed=child;g=partial;f=total;look=ahead;}
};
#define TLD(id) label(id)
struct Golden:Base {
#include "original_cost.inc"
};
struct Candidate:Base {
#include "candidate_cost.inc"
};
#undef TLD
static uint32_t rng=0xc82f51ad;
static uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static uint32_t bits(float x){uint32_t v;std::memcpy(&v,&x,4);return v;}
static float value(uint32_t x){float v;std::memcpy(&v,&x,4);return v;}
static uint64_t cases=0,nans=0,inf=0,cross=0,alt=0,reverse=0,hotpath=0;
static void check(Golden& a,Candidate& b,Base::State& state,bool look){
 a.evaluateCostAndPush(state,0,1,look);b.evaluateCostAndPush(state,0,1,look);
 // IEEE NaN payload equality is checked as well, not just numerical equality.
 if(bits(a.g)!=bits(b.g)||bits(a.f)!=bits(b.f)||a.accesses!=b.accesses||a.pushed!=b.pushed||a.look!=b.look||a.dyn[1].prev!=b.dyn[1].prev)
  throw std::runtime_error("cost mismatch "+std::to_string(cases));
 ++cases;nans+=std::isnan(a.f);inf+=std::isinf(a.f);cross+=a.connections[0].cross;
 alt+=a.lmkReady;reverse+=a.reverse_y;hotpath+=a.useHotExpand&&!a.occLocking;
}
int main(){
 const uint32_t special[]={0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345};
 for(unsigned i=0;i<262144;i++){
  Golden a;Base::State st;
  a.useHotExpand=i&1;a.occLocking=i&2;a.lmkReady=i&4;a.reverse_y=i&8;
  a.connections[0].cross=i&16;a.slr[1]=(i>>5)%3;a.slr[2]=(i>>7)%3;
  a.cfg.maxDetourToSnapBackToPrevLagunaColumn=(i>>9)%8;
  for(int n=0;n<4;n++){
   auto& x=a.ns[n];x.endX=10+rnd()%160;x.endY=rnd()%240;x.beginX=10+rnd()%160;x.beginY=rnd()%240;
   x.length=rnd()%128;x.baseCost=float(1+rnd()%128)/16;
   a.occupancy[n]=1+rnd()%20;x.occCnt=a.occupancy[n];a.hot[n]=x;
   a.dyn[n].hist=float(1+rnd()%32)/4;a.uses[n]=rnd()%16;
  }
  for(int n=0;n<32;n++){a.presentCongestionCosts[n]=float(1+rnd()%64)/8;a.lmk[n]=rnd()%65536;}
  for(int n=0;n<8;n++)st.lmkT[n]=rnd()%65536;
  a.lmkInvScale=float(rnd()%128)/256;
  a.nets[0]={float(rnd()%180)+0.25f,float(rnd()%240)+0.5f,int(1+rnd()%64),int(1+rnd()%512)};
  a.dyn[0].upstream=float(rnd()%4096)/16;
  st.shareWeight=float(rnd()%32)/8;st.rnodeWLWeight=float(rnd()%32)/16;st.estWlWeight=float(rnd()%32)/16;
  for(int x=0;x<256;x++){a.nextLagunaColumn[x]=180;a.prevLagunaColumn[x]=5;}
  if(i&32)for(int x=0;x<256;x++)a.nextLagunaColumn[x]=a.prevLagunaColumn[x]=x;
  // Exercise raw FP corner cases; integer geometry stays within defined C++ range.
  if(i<14*14*8){
   a.ns[1].baseCost=a.hot[1].baseCost=value(special[i%14]);
   a.dyn[1].hist=value(special[(i/14)%14]);
   if(i&64)st.shareWeight=-1; // sharing can become zero/negative; preserve original IEEE behavior.
   if(i&128)a.nets[0].doubleHpwl=0;
  }
  Candidate b;static_cast<Base&>(b)=static_cast<Base&>(a);check(a,b,st,i&256);
 }
 std::printf("SEARCH_COST_UNIT_PASS cases=%llu nan=%llu inf=%llu cross=%llu alt=%llu reverse_y=%llu hot=%llu\n",
 (unsigned long long)cases,(unsigned long long)nans,(unsigned long long)inf,(unsigned long long)cross,(unsigned long long)alt,(unsigned long long)reverse,(unsigned long long)hotpath);
}
