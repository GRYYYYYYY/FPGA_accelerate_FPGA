#define main original_protocol_test_main
#include "original_testbench.cpp"
#undef main
#include <cassert>
static FILE* output;
static unsigned long long services=0,emissions=0;
static void emit(World w,const std::vector<unsigned>& raw,bool prune){
    auto ev=oracle(w,raw,prune);unsigned kept=0;for(auto e:ev)if(e.phase==search_children::EMIT)++kept;
    std::fprintf(output,"%08x %08x %08x %08x %08x %08x %08x %08x\n",0,unsigned(raw.size()),unsigned(prune),contexts%4,contexts%16,kept,unsigned(ev.size()),contexts+1);
    for(auto e:ev)std::fprintf(output,"%08x %08x %08x %08x %08x\n",e.phase,e.position,e.node,e.value,e.aux);
    ++contexts;services+=ev.size();emissions+=kept;
}
int main(int argc,char**argv){
    assert(argc==2);output=std::fopen(argv[1],"w");assert(output);
    for(unsigned fl=0;fl<256;++fl)for(unsigned cr=0;cr<2;++cr)for(unsigned lag=0;lag<2;++lag)
    for(unsigned prune=0;prune<2;++prune)for(unsigned typ=0;typ<18;++typ)for(unsigned dead=0;dead<2;++dead)
        emit(configure(fl,cr,lag,typ,dead),{1},prune);
    for(unsigned n=0;n<20000;++n){
        unsigned fl=random32()&255,cr=random32()&1,lag=random32()&1,prune=random32()&1,typ=random32()%18,dead=random32()&1,count=random32()%19;
        World w=configure(fl,cr,lag,typ,dead);std::vector<unsigned> raw;
        for(unsigned i=0;i<count;++i)raw.push_back((i*3+contexts)%8);
        for(unsigned i=0;i<8;++i){unsigned x=random32();w.ns[i].preserved=x&1;w.created[i]=(x>>1)&1;w.deadEnd[i]=(x>>2)&1;w.labels[i].prev=int(x%9)-1;w.labels[i].visited=int(x>>4);}
        emit(w,raw,prune);
    }
    std::fclose(output);assert(contexts==93728&&services==813439&&emissions==46896);
    std::printf("CHILDREN_VECTORS_PASS contexts=%u services=%llu emissions=%llu\n",contexts,services,emissions);
}
