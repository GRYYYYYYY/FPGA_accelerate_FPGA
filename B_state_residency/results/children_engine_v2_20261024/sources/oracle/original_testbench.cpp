#include "children_port.hpp"
#include "RouteNodeType.hpp"
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using namespace com::xilinx::rapidwright::rwroute;
using namespace children_port;
struct World {
    struct NodeStatic {bool preserved,isPinfeed,pinfeedLeadsToLaguna,isLaguna,arcLockedInit,isPinbounce;} ns[8]{};
    struct Label{int prev,visited;} labels[8]{};
    bool created[8]{},deadEnd[8]{},isSinkNode[8]{},hasLaguna=false;
    RouteNodeType type[8]{};
    int getNode(int n)const{return created[n]?n:-1;}
#define TLD(n) labels[n]
#include "original_exclusion.inc"
#undef TLD
#include "original_dead.inc"
};
struct Event{unsigned phase,position,node,value,aux;};
static unsigned calls=0,contexts=0,rejects=0,phase_hits[8]{};
static uint32_t gen=0,rng=0x97a32d11;
static Reply expected{OK,0,search_children::DONE,0,0,0,0,0,0,0,0};
static void check(bool c){if(!c){std::fprintf(stderr,"FAIL calls=%u contexts=%u phase=%u pos=%u\n",calls,contexts,expected.request,expected.position);std::abort();}}
static unsigned random32(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static void invoke(Command c,unsigned status){
    Reply actual{};
    children_step(c.op,c.parent,c.count,c.prune,c.query,c.price,c.generation,c.position,c.phase,c.node,c.value,c.aux,c.service_status,actual.status,actual.generation,actual.request,actual.position,actual.node,actual.parent,actual.query,actual.price,actual.emitted,actual.active,actual.fault);
    ++calls;if(status!=OK)++rejects;
    Reply want=expected;want.status=status;
    static_assert(sizeof(Reply)==44,"reply words");
    if(std::memcmp(&actual,&want,sizeof(Reply))!=0){std::fprintf(stderr,"reply actual status=%u gen=%u req=%u pos=%u node=%u emit=%u active=%u fault=%u; expected status=%u gen=%u req=%u pos=%u node=%u emit=%u active=%u fault=%u\n",actual.status,actual.generation,actual.request,actual.position,actual.node,actual.emitted,actual.active,actual.fault,want.status,want.generation,want.request,want.position,want.node,want.emitted,want.active,want.fault);check(false);}
}
static std::vector<Event> oracle(World w,const std::vector<unsigned>& raw,bool prune){
    std::vector<Event> ev;bool alive=false;unsigned i=0;
    auto event=[&](unsigned phase,unsigned node,unsigned value=0,unsigned aux=0){ev.push_back({phase,i,node,value,aux});};
    for(unsigned child:raw){
        bool dead=prune&&w.deadChild(child);event(search_children::NEXT,0,child,dead);if(prune&&!dead)alive=true;
        bool ex=w.isExcluded(0,child);event(search_children::EXCLUDE,child,ex);
        if(!ex){
            event(search_children::CREATE,child);w.created[child]=true;
            bool inaccessible=w.type[child]==RouteNodeType::INACCESSIBLE;
            bool known_dead=!inaccessible&&prune&&w.deadEnd[child];
            event(search_children::CLASSIFY,child,inaccessible,known_dead);
            if(!inaccessible&&!known_dead)event(search_children::EMIT,child);
        }
        ++i;
    }
    if(prune&&!alive){bool can=w.canBeDeadEnd(0);event(search_children::CHECK_DEAD,0,can);if(can)event(search_children::MARK_DEAD,0);}
    event(search_children::PUBLISH,0);return ev;
}
static void wrong_replies(Command c){
    Command bad=c;bad.generation^=0x80000000u;bad.service_status=1;invoke(bad,STALE);
    bad=c;bad.parent^=1;invoke(bad,STALE);
    bad=c;bad.query^=1;invoke(bad,STALE);
    bad=c;bad.price^=1;invoke(bad,STALE);
    bad=c;bad.node^=1;invoke(bad,STALE);
    bad=c;bad.position^=1;invoke(bad,WRONG_POSITION);
    bad=c;bad.phase=(c.phase+1)%9;invoke(bad,WRONG_PHASE);
    bad=c;if(c.phase==search_children::NEXT)bad.value=0x1000000u;else bad.value=2;invoke(bad,BAD);
    bad=c;bad.aux=2;invoke(bad,BAD);
    bad={};bad.op=START;invoke(bad,BUSY);
    bad={};bad.op=SNAPSHOT;invoke(bad,OK);
}
static void exercise(World w,const std::vector<unsigned>& raw,bool prune,bool inject){
    auto ev=oracle(w,raw,prune);unsigned q=contexts%4,p=contexts%16;
    expected={OK,++gen,ev[0].phase,0,0,0,q,p,0,1,0};
    Command start{};start.op=START;start.count=raw.size();start.prune=prune;start.query=q;start.price=p;invoke(start,OK);
    for(unsigned i=0;i<ev.size();++i){
        Event e=ev[i];check(expected.request==e.phase&&expected.position==e.position&&expected.node==e.node);
        Command c{};c.op=RESPONSE;c.parent=0;c.query=q;c.price=p;c.generation=gen;c.position=e.position;c.phase=e.phase;c.node=e.node;c.value=e.value;c.aux=e.aux;
        if(inject)wrong_replies(c);
        ++phase_hits[e.phase];
        if(e.phase==search_children::EMIT)++expected.emitted;
        if(i+1<ev.size()){expected.request=ev[i+1].phase;expected.position=ev[i+1].position;expected.node=ev[i+1].node;}
        else{expected.request=search_children::DONE;expected.position=raw.size();expected.node=0;expected.active=0;}
        invoke(c,OK);
        if(inject){
            unsigned s=!expected.active?NO_REQUEST:c.node!=expected.node?STALE:c.phase!=expected.request?WRONG_PHASE:WRONG_POSITION;
            invoke(c,s);
        }
    }
    ++contexts;
}
static World configure(unsigned flags,unsigned cr,unsigned lag,unsigned typ,unsigned dead){
    World w;w.hasLaguna=lag;
    for(unsigned i=0;i<8;++i){w.ns[i]={bool(flags&64),bool(flags&4),bool(flags&8),bool(flags&2),bool(flags&32),bool(flags&1)};w.created[i]=cr;w.deadEnd[i]=dead;w.type[i]=RouteNodeType(typ);w.isSinkNode[i]=(contexts>>2)&1;w.labels[i]={int(contexts%3)-1,int((contexts+i)%3)};}
    return w;
}
int main(){
    Command c{};c.op=SNAPSHOT;invoke(c,OK);c.op=RESPONSE;invoke(c,NO_REQUEST);c.op=7;invoke(c,BAD);
    for(unsigned k=0;k<4;++k){c={};c.op=START;if(k==0)c.parent=0x1000000u;if(k==1)c.prune=2;if(k==2)c.query=4;if(k==3)c.price=16;invoke(c,BAD);}
    if(CHILDREN_GENERATION_BITS==3){
        for(unsigned n=0;n<7;++n)exercise(configure(0,0,0,17,0),n%2?std::vector<unsigned>{1}:std::vector<unsigned>{},true,true);
        c={};c.op=START;invoke(c,EXHAUSTED);c.op=SNAPSHOT;invoke(c,OK);check(gen==7);
    }else{
        for(unsigned fl=0;fl<256;++fl)for(unsigned cr=0;cr<2;++cr)for(unsigned lag=0;lag<2;++lag)
        for(unsigned prune=0;prune<2;++prune)for(unsigned typ=0;typ<18;++typ)for(unsigned dead=0;dead<2;++dead)
            exercise(configure(fl,cr,lag,typ,dead),{1},prune,contexts<32);
        for(unsigned n=0;n<20000;++n){
            unsigned fl=random32()&255,cr=random32()&1,lag=random32()&1,prune=random32()&1,typ=random32()%18,dead=random32()&1,count=random32()%19;
            World w=configure(fl,cr,lag,typ,dead);std::vector<unsigned> raw;
            for(unsigned i=0;i<count;++i)raw.push_back((i*3+contexts)%8);
            for(unsigned i=0;i<8;++i){unsigned x=random32();w.ns[i].preserved=x&1;w.created[i]=(x>>1)&1;w.deadEnd[i]=(x>>2)&1;w.labels[i].prev=int(x%9)-1;w.labels[i].visited=int(x>>4);}
            exercise(w,raw,prune,n<32);
        }
        check(contexts==93728);
        for(unsigned i=0;i<8;++i)check(phase_hits[i]>0);
        // Matched backend error at PUBLISH must stop, preserving the pending build.
        c={};c.op=START;expected={OK,++gen,search_children::PUBLISH,0,0,0,0,0,0,1,0};invoke(c,OK);
        c={};c.op=RESPONSE;c.generation=gen;c.phase=search_children::PUBLISH;c.service_status=10;expected.fault=1;invoke(c,SERVICE_ERROR);
        c.service_status=0;invoke(c,STOPPED);c.op=START;invoke(c,STOPPED);c.op=SNAPSHOT;invoke(c,OK);
    }
    std::printf("CHILDREN_PORT_PASS generation_bits=%u contexts=%u calls=%u rejected=%u next=%u exclude=%u create=%u classify=%u emit=%u check_dead=%u mark_dead=%u publish=%u\n",CHILDREN_GENERATION_BITS,contexts,calls,rejects,phase_hits[0],phase_hits[1],phase_hits[2],phase_hits[3],phase_hits[4],phase_hits[5],phase_hits[6],phase_hits[7]);
}
