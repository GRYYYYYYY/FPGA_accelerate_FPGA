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
 int occCnt[4]{},ownerNet[4]{},ownerCnt[4]{},uses[4]{},slrTable[65536]{};bool deadEnd[4]{},over[4]{};
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
static uint32_t ids[4];static bool auxnode=false;
static uint32_t mapped(uint32_t v){if(v==0xffffffffu)return v;if(v>=4)throw std::runtime_error("prev fixture");return ids[v];}
static void record(uint32_t op,const search_access::Config&c,const search_access::State&before,uint32_t value,const search_access::State&after){
 if(op==0)auxnode=false;uint32_t oldaux=auxnode?mapped(uint32_t(before.aux)):uint32_t(before.aux);
 if(op==1&&(before.phase==13||before.phase==14))value=mapped(value);
 if(op==1&&before.phase==14)auxnode=true;
 uint32_t newaux=auxnode?mapped(uint32_t(after.aux)):uint32_t(after.aux);
 uint32_t in[20]={op,before.phase,before.bits,oldaux,before.action,value,c.sequence,c.flags,c.child_type,c.parent_type,c.sink_type,uint32_t(c.child_x),uint32_t(c.child_tile),uint32_t(c.sink_tile),uint32_t(c.sink_x),uint32_t(c.sink_y),uint32_t(c.xmin),uint32_t(c.xmax),uint32_t(c.ymin),uint32_t(c.ymax)};
 uint32_t out[6]={0,after.phase,after.bits,newaux,search_access::request(after),after.action};
 std::fprintf(vec,"%u %u",steps++,case_id);for(auto v:in)std::fprintf(vec," %08x",v);for(auto v:out)std::fprintf(vec," %08x",v);std::fprintf(vec,"\n");
}
static search_access::State record_start(const search_access::Config&c){auto s=search_access::start();record(0,c,{0,0,0,0},0,s);return s;}
static bool record_accept(const search_access::Config&c,search_access::State&s,uint32_t v){auto before=s;requests[search_access::request(s)]++;bool ok=search_access::accept(c,s,v);if(!ok)throw std::runtime_error("candidate state");record(1,c,before,v,s);return ok;}
static uint32_t rng=0xab761259;static uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
#include <fstream>
#include <array>
static int16_t s16(const unsigned char*b){return int16_t(uint16_t(b[0])|(uint16_t(b[1])<<8));}
static int32_t s32(const unsigned char*b){return int32_t(uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24));}
int main(int argc,char**argv){
 if(argc!=6)return 2;std::ifstream graph(argv[1],std::ios::binary),rows(argv[2],std::ios::binary);unsigned N=std::stoul(argv[3]),R=std::stoul(argv[4]);bool real=std::stoi(argv[5]);
 std::vector<int>slr(R);for(unsigned y=0;y<R;y++){unsigned char b[8];rows.read((char*)b,8);if(!rows)return 3;slr[y]=s32(b);}
 FILE*ctx=std::fopen("contexts.txt","w");vec=std::fopen("vectors.txt","w");unsigned count=real?512:11664;
 unsigned allowed=0,lookahead=0,early=0,pruned=0;
 for(unsigned k=0;k<count;k++){
  unsigned rep=k%2,ct=(k/2)/(18*18),pt=((k/2)/18)%18,st=(k/2)%18;
  ids[1]=real?(k*65537ull+3)%N:ct;ids[0]=real?(ids[1]+8191)%N:18+pt;ids[2]=real?(ids[1]+16381)%N:36+st;ids[3]=rep?54:0;
  Golden a;auto&c=a.connections[0];a.useHotExpand=rep;a.pruneDeadEnd=rnd()%4==0;a.cfg.useBoundingBox=rnd()&1;c.crossSLRnorth=rnd()&1;c.crossSLRsouth=rnd()&1;
  for(unsigned n=0;n<4;n++){
   unsigned char b[32];graph.seekg(uint64_t(ids[n])*32);graph.read((char*)b,32);if(!graph)return 4;auto&t=a.ns[n];
   t.tileAddr=s32(b);t.type=b[8];t.isLaguna=b[9]&2;t.isPinbounce=b[9]&128;t.beginX=s16(b+10);t.beginY=s16(b+12);t.endX=s16(b+14);t.endY=s16(b+16);
   a.type[n]=RouteNodeType(t.type);a.hot[n]=t;a.dyn[n].prev=3;
  }
  for(unsigned y=0;y<R;y++)a.slrTable[y]=slr[y];
  a.dyn[0].prev=rep?3:-1;a.dyn[1].visited=rnd()%17==0?17:0;a.dyn[1].target=rnd()%11==0?1:0;
  a.deadEnd[1]=rnd()%7==0;int occ=rnd()%4;a.uses[1]=(occ&&(rnd()&1))?1+rnd()%3:0;a.over[1]=occ>1||(occ==1&&a.uses[1]==0);
  c.xMinBB=a.ns[1].endX-(k%7==0?0:2);c.xMaxBB=a.ns[1].endX+2;c.yMinBB=a.ns[1].endY-3;c.yMaxBB=a.ns[1].endY+3;
  std::fprintf(ctx,"%u %u %u %u %u %08x %08x %08x %08x %d %d\n",k,ids[0],ids[1],ids[2],ids[3],mapped(uint32_t(a.dyn[0].prev)),mapped(uint32_t(a.dyn[1].prev)),uint32_t(a.dyn[1].visited),uint32_t(a.dyn[1].target),occ,a.uses[1]);
  Candidate b;static_cast<Base&>(b)=static_cast<Base&>(a);a.queue.owner=&a;b.queue.owner=&b;a.tl_dyn=a.dyn;b.tl_dyn=b.dyn;
  Base::State sa{0,17,&a.queue,false},sb{0,17,&b.queue,false};a.exploreAndExpand(sa,0);b.exploreAndExpand(sb,0);
  if(a.events!=b.events||a.pushes!=b.pushes||a.look!=b.look||sa.earlyTermination!=sb.earlyTermination||a.prunedPushes!=b.prunedPushes){std::fprintf(stderr,"FABRIC_ORACLE_FAIL case=%u\n",k);return 5;}
  allowed+=a.pushes;lookahead+=a.pushes&&a.look;early+=sa.earlyTermination;pruned+=a.prunedPushes;case_id++;
 }
 std::fclose(ctx);std::fclose(vec);for(int r=1;r<=11;r++)std::printf("REQUEST %d %u\n",r,requests[r]);
 std::printf("FABRIC_ORACLE_PASS cases=%u steps=%u allowed=%u lookahead=%u early=%u pruned=%u\n",case_id,steps,allowed,lookahead,early,pruned);return 0;
}
