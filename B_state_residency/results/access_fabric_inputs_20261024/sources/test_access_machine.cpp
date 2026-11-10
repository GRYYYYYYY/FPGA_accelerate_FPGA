#include "access_machine.hpp"
#include "RouteNodeType.hpp"
#include <vector>
#include <string>
#include <cstdio>
#include <stdexcept>
#include <algorithm>
#include <cstdlib>
using com::xilinx::rapidwright::rwroute::RouteNodeType;
struct Base {
 struct Attr {int tileAddr=0,endX=0,endY=0,beginX=0,beginY=0;uint8_t type=0;bool isLaguna=false,isPinbounce=false;};
 using HotExpand=Attr;
 struct Label {int visited=0,prev=-1;uint8_t target=0;};
 struct Connection {int netIdx=0,sinkRnode=2,xMinBB=-100,xMaxBB=100,yMinBB=-100,yMaxBB=100;bool crossSLRnorth=false,crossSLRsouth=false;bool isCrossSLR()const{return crossSLRnorth||crossSLRsouth;}}connections[1];
 struct Config {bool useBoundingBox=false,useUTurnNodes=false;}cfg;
 struct Event {int op,a,b;bool operator==(const Event&v)const{return op==v.op&&a==v.a&&b==v.b;}};
 mutable std::vector<Event>events;
 struct Queue {Base*owner=nullptr;void clear(){owner->events.push_back({4,0,0});}}queue;
 struct State {int connIdx=0,sequence=17;Queue*queue=nullptr;bool earlyTermination=false;};
 struct Sparse {void prefetch(int){}};Sparse*tl_sparse=nullptr;
 Attr ns[4],hot[4];Label dyn[4];Label*tl_dyn=dyn;RouteNodeType type[4];
 int occCnt[4]{},ownerNet[4]{},ownerCnt[4]{},uses[4]{},slrTable[256]{};bool deadEnd[4]{},over[4]{};
 bool useHotExpand=false,doPrefetch=false,pruneDeadEnd=false;int prunedPushes=0,pushes=0;bool look=false;
 std::vector<int>kids{1};
 const std::vector<int>&getChildren(int){return kids;}
 Label&bTLD(int id,int line)const{events.push_back({1,id,line});return const_cast<Base*>(this)->dyn[id];}
 RouteNodeType searchType(int id)const{return useHotExpand?RouteNodeType(hot[id].type):type[id];}
 bool nodeLaguna(int id)const{return useHotExpand?hot[id].isLaguna:ns[id].isLaguna;}
 bool nodePinbounce(int id)const{return useHotExpand?hot[id].isPinbounce:ns[id].isPinbounce;}
 bool searchWillOverUse(int id,int nw)const{events.push_back({2,id,nw});return over[id];}
 int searchCountUser(int id,int nw)const{events.push_back({3,id,nw});return uses[id];}
 void evaluateCostAndPush(State&st,int,int child,bool ahead){events.push_back({5,child,int(ahead)});pushes++;look=ahead;}
#define TLD(id) bTLD(id,__LINE__)
#include "coordinates.inc"
#undef TLD
};
#define TLD(id) bTLD(id,__LINE__)
struct Golden:Base {
#include "original_access.inc"
};
#undef TLD
static FILE*vec;static unsigned case_id=0,steps=0;static unsigned requests[12]{};
static search_access::State record_start(const search_access::Config&);
static bool record_accept(const search_access::Config&,search_access::State&,uint32_t);
#define TLD(id) bTLD(id,__LINE__)
struct Candidate:Base {
#include "candidate_access.inc"
};
#undef TLD
static void record(uint32_t op,const search_access::Config&c,const search_access::State&before,uint32_t value,const search_access::State&after){
 uint32_t in[20]={op,before.phase,before.bits,uint32_t(before.aux),before.action,value,c.sequence,c.flags,c.child_type,c.parent_type,c.sink_type,uint32_t(c.child_x),uint32_t(c.child_tile),uint32_t(c.sink_tile),uint32_t(c.sink_x),uint32_t(c.sink_y),uint32_t(c.xmin),uint32_t(c.xmax),uint32_t(c.ymin),uint32_t(c.ymax)};
 uint32_t out[6]={0,after.phase,after.bits,uint32_t(after.aux),search_access::request(after),after.action};
 std::fprintf(vec,"%u %u",steps++,case_id);for(auto v:in)std::fprintf(vec," %08x",v);for(auto v:out)std::fprintf(vec," %08x",v);std::fprintf(vec,"\n");
}
static search_access::State record_start(const search_access::Config&c){auto s=search_access::start();record(0,c,{0,0,0,0},0,s);return s;}
static bool record_accept(const search_access::Config&c,search_access::State&s,uint32_t v){auto before=s;requests[search_access::request(s)]++;bool ok=search_access::accept(c,s,v);if(!ok)throw std::runtime_error("candidate state");record(1,c,before,v,s);return ok;}
static uint32_t rng=0xab761259;static uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
int main(){
 vec=std::fopen("vectors.txt","w");if(!vec)return 2;
 unsigned allowed=0,skipped=0,ahead=0,early=0,pruned=0,hot=0,visited=0;
 for(unsigned ct=0;ct<18;ct++)for(unsigned pt=0;pt<18;pt++)for(unsigned st=0;st<18;st++)for(unsigned rep=0;rep<8;rep++){
  Golden a;auto&c=a.connections[0];
  a.type[0]=RouteNodeType(pt);a.type[1]=RouteNodeType(ct);a.type[2]=RouteNodeType(st);a.type[3]=RouteNodeType(12);
  c.crossSLRnorth=rnd()&1;c.crossSLRsouth=rnd()&1;a.useHotExpand=rep&1;a.doPrefetch=rep&2;a.cfg.useBoundingBox=rep&4;a.pruneDeadEnd=rnd()%4==0;
  for(int n=0;n<4;n++){
   a.ns[n].tileAddr=rnd()%3;a.ns[n].endX=rnd()%3;a.ns[n].beginX=rnd()%3;a.ns[n].endY=30+rnd()%3;a.ns[n].beginY=30+rnd()%3;
   a.ns[n].type=uint8_t(a.type[n]);a.ns[n].isLaguna=rnd()&1;a.ns[n].isPinbounce=rnd()&1;
   a.dyn[n].prev=(rnd()%3==0)?-1:3;a.dyn[n].target=(rnd()%11==0)?1:0;a.dyn[n].visited=(rnd()%17==0)?17:0;
   a.deadEnd[n]=rnd()%7==0;a.over[n]=rnd()&1;a.uses[n]=rnd()%3;a.hot[n]=a.ns[n];
  }
  // Local adjacency and strict bbox boundaries appear both on and off the edge.
  if(rep==4)c.xMinBB=a.ns[1].endX;
  if(rep==5)c.yMaxBB=a.ns[1].endY;
  for(int y=0;y<256;y++)a.slrTable[y]=(y<31?0:y<32?1:2);
  Candidate b;static_cast<Base&>(b)=static_cast<Base&>(a);
  a.queue.owner=&a;b.queue.owner=&b;a.tl_dyn=a.dyn;b.tl_dyn=b.dyn;
  Base::State sa{0,17,&a.queue,false},sb{0,17,&b.queue,false};
  a.exploreAndExpand(sa,0);b.exploreAndExpand(sb,0);
  if(a.events!=b.events||a.pushes!=b.pushes||a.look!=b.look||sa.earlyTermination!=sb.earlyTermination||a.prunedPushes!=b.prunedPushes){
   std::fprintf(stderr,"ACCESS_FAIL case=%u ct=%u pt=%u st=%u rep=%u push=%d/%d look=%d/%d early=%d/%d events=%zu/%zu\n",case_id,ct,pt,st,rep,a.pushes,b.pushes,a.look,b.look,sa.earlyTermination,sb.earlyTermination,a.events.size(),b.events.size());
   for(auto v:a.events)std::fprintf(stderr,"G %d %d %d\n",v.op,v.a,v.b);for(auto v:b.events)std::fprintf(stderr,"C %d %d %d\n",v.op,v.a,v.b);return 3;
  }
  allowed+=a.pushes;skipped+=!a.pushes;ahead+=a.pushes&&a.look;early+=sa.earlyTermination;pruned+=a.prunedPushes;hot+=a.useHotExpand;visited+=a.dyn[1].visited==17;case_id++;
 }
 std::fclose(vec);
 for(int r=1;r<=11;r++){if(!requests[r])return 4;std::printf("REQUEST %d %u\n",r,requests[r]);}
 std::printf("ACCESS_UNIT_PASS cases=%u steps=%u allowed=%u skipped=%u lookahead=%u early=%u pruned=%u hot=%u visited=%u\n",case_id,steps,allowed,skipped,ahead,early,pruned,hot,visited);return 0;
}
