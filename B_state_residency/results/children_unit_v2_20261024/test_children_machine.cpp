#include "children_machine.hpp"
#include "RouteNodeType.hpp"
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <vector>
#include <cassert>
using namespace com::xilinx::rapidwright::rwroute;
static int tl_wid=-1;
struct Base {
    struct Attr {bool preserved=false,isPinfeed=false,pinfeedLeadsToLaguna=false,isLaguna=false,arcLockedInit=false,isPinbounce=false;int childCount=0,childStart=0;} ns[8];
    struct Label {int prev=0,visited=0;} labels[8];
    uint8_t created[8]{},deadEnd[8]{},isSinkNode[8]{},rawFetched[8]{};
    RouteNodeType type[8]{};
    std::vector<int>* childrenCache[8]{};
    std::vector<int> rawChildrenStore[8],childIds,events;
    bool pruneDeadEnd=false,lazy=false,occLocking=false,hasLaguna=false;
    double jniDeviceSecs=0;unsigned jniDeviceCalls=0;
    ~Base(){for(auto p:childrenCache)if((uintptr_t)p>1)delete p;}
    int getNode(int id)const{return created[id]?id:-1;}
    const Label& read(int id)const{const_cast<Base*>(this)->events.push_back(100+id);return labels[id];}
    void getOrCreate(int id){events.push_back(200+id);created[id]=1;}
    void lockNode(int){} void unlockNode(int){}
    long keyOf(int id){return id;}
    void fetchChildrenPacked(long id,std::vector<int>& out){events.push_back(400+id);out={int(childIds.size())};out.insert(out.end(),childIds.begin(),childIds.end());}
    void internChildrenBatch(const std::vector<int>& in,int count,std::vector<int>& out){out.assign(in.begin()+1,in.begin()+1+count);}
#define TLD(id) read(id)
#define isExcluded originalExcluded
#include "original_exclusion.inc"
#undef isExcluded
#undef TLD
#include "original_dead.inc"
    bool isExcluded(int p,int c){events.push_back(300+c);return originalExcluded(p,c);}
};
struct Golden:Base {
#include "original_children.inc"
};
struct Candidate:Base {
#include "candidate_children.inc"
};
static unsigned cases=0,cached=0,empty=0,created_dropped=0;
static void check(bool condition){if(!condition)throw std::runtime_error("children semantic mismatch case="+std::to_string(cases));}
static uint32_t rng=0x97a32d11;
static unsigned random32(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static void configure(Base& b,unsigned flags,unsigned cr,unsigned lag,unsigned prune,unsigned typ,unsigned dead,unsigned mode,unsigned count){
    b.hasLaguna=lag;b.pruneDeadEnd=prune;b.lazy=mode&1;b.occLocking=mode&2;
    for(int i=0;i<8;++i){
        b.ns[i]={bool(flags&64),bool(flags&4),bool(flags&8),bool(flags&2),bool(flags&32),bool(flags&1),0,0};
        b.created[i]=cr;b.deadEnd[i]=dead;b.isSinkNode[i]=(mode>>2)&1;b.type[i]=RouteNodeType(typ);
        b.labels[i]={int(cases%3)-1,int((cases+i)%3)};b.rawFetched[i]=(mode>>3)&1;
    }
    b.ns[0].childCount=count;
    for(unsigned i=0;i<count;++i)b.childIds.push_back(count==1?1:int((i*3+cases)%8));
    b.rawChildrenStore[0]=b.childIds;
}
static void compare(Golden& g,Candidate& c){
    auto a=g.getChildren(0),b=c.getChildren(0);
    check(a==b&&g.events==c.events&&g.childIds==c.childIds);
    for(int i=0;i<8;++i){check(g.created[i]==c.created[i]&&g.deadEnd[i]==c.deadEnd[i]&&g.rawFetched[i]==c.rawFetched[i]);}
    check(g.jniDeviceCalls==c.jniDeviceCalls);if(a.empty())++empty;
    if(std::find(g.events.begin(),g.events.end(),201)!=g.events.end()&&std::find(a.begin(),a.end(),1)==a.end())++created_dropped;
    // Change query labels and dynamic created, static eligibility and prune policy.
    // Published cache must still be returned without filtering or any side effect.
    auto old_events=g.events;
    for(int i=0;i<8;++i){g.labels[i]={7,1234};c.labels[i]=g.labels[i];g.created[i]=c.created[i]=!g.created[i];g.ns[i].preserved=c.ns[i].preserved=!g.ns[i].preserved;g.type[i]=c.type[i]=RouteNodeType::INACCESSIBLE;}
    g.pruneDeadEnd=c.pruneDeadEnd=!g.pruneDeadEnd;
    check(g.getChildren(0)==a&&c.getChildren(0)==a&&g.events==old_events&&c.events==old_events);
    check((uintptr_t)g.childrenCache[0]>1&&(uintptr_t)c.childrenCache[0]>1);++cached;++cases;
}
int main(){
    for(unsigned fl=0;fl<256;++fl)for(unsigned cr=0;cr<2;++cr)for(unsigned lag=0;lag<2;++lag)
    for(unsigned prune=0;prune<2;++prune)for(unsigned typ=0;typ<18;++typ)for(unsigned dead=0;dead<2;++dead){
        Golden g;Candidate c;unsigned mode=cases%16;
        configure(g,fl,cr,lag,prune,typ,dead,mode,1);configure(c,fl,cr,lag,prune,typ,dead,mode,1);compare(g,c);
    }
    for(unsigned n=0;n<20000;++n){
        Golden g;Candidate c;unsigned fl=random32()&255,cr=random32()&1,lag=random32()&1,prune=random32()&1,typ=random32()%18,dead=random32()&1,mode=random32()%16,count=random32()%19;
        configure(g,fl,cr,lag,prune,typ,dead,mode,count);configure(c,fl,cr,lag,prune,typ,dead,mode,count);
        for(int i=0;i<8;++i){unsigned x=random32();g.ns[i].preserved=c.ns[i].preserved=x&1;g.created[i]=c.created[i]=(x>>1)&1;g.deadEnd[i]=c.deadEnd[i]=(x>>2)&1;g.labels[i].prev=c.labels[i].prev=int(x%9)-1;g.labels[i].visited=c.labels[i].visited=int(x>>4);}
        compare(g,c);
    }
    // Wrong-phase replies must not advance. Empty publication is explicit.
    search_children::Machine m(1,true);check(!m.excluded(false)&&!m.created()&&!m.classified(false,false)&&!m.emitted()&&!m.can_mark_dead(true)&&!m.marked_dead()&&!m.published());
    check(!m.next(0x1000000u,false)&&m.position==0&&m.request==search_children::NEXT);
    check(m.next(7,true)&&m.excluded(false)&&m.created()&&m.classified(true,false)&&m.can_mark_dead(true)&&m.marked_dead()&&m.published());
    check(m.request==search_children::DONE&&m.position==1&&!m.published()&&!m.next(0,false));
    check(cases==93728&&cached==cases&&created_dropped>0&&empty>0);
    std::printf("CHILDREN_UNIT_PASS cases=%u cached=%u empty=%u created_dropped=%u protocol=1\n",cases,cached,empty,created_dropped);
}
