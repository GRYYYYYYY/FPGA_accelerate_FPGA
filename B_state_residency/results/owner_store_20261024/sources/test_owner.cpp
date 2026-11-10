#include "owner_store.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <unordered_map>
static void check(bool b){if(!b)throw std::runtime_error("owner verification failure");}
struct Hot {int ownerNet=-1;uint16_t ownerCnt=0;uint8_t occCnt=0;};
struct Original {
    bool trackDirty=false;
    std::vector<int> ownerNet;
    std::vector<uint16_t> ownerCnt,occCnt;
    std::vector<std::unordered_map<int,int>*> userOverflow;
    std::vector<Hot> hot;
    Original(unsigned n):ownerNet(n,-1),ownerCnt(n),occCnt(n),userOverflow(n,nullptr),hot(n){}
    ~Original(){for(auto p:userOverflow)delete p;}
    void markDirty(int){}
#include "original_owner.inc"
};
using namespace owner_state;
static Plan apply(Store& s,unsigned op,unsigned node,unsigned net) {
    auto p=s.prepare(op,node,net);check(p.status==OK);check(s.commit(p)==OK);return p;
}
static void unit() {
    Original original(128);Store s(128,2048);std::mt19937 random(987341);
    uint64_t mutations=0;
    for(unsigned i=0;i<200000;++i) {
        unsigned node=random()%128,net=random()%16;
        bool remove=original.countUserSlot(node,net)>0 && (random()%100)<55;
        auto p=s.prepare(remove?DEC:INC,node,net);check(p.status==OK);
        check(s.commit(p)==OK);++mutations;
        if(remove)original.decUserSlot(node,net);else original.incUserSlot(node,net);
        for(unsigned n=0;n<16;++n) {
            auto q=s.prepare(GET,node,n);check(q.status==OK);
            int count=original.countUserSlot(node,n),occ=original.occCnt[node];
            check(q.count==unsigned(count) && q.occupancy==unsigned(occ));
            check(q.will_overuse==unsigned(occ>1 || (occ==1 && count==0)));
            check(original.hot[node].ownerNet==original.ownerNet[node] && original.hot[node].ownerCnt==original.ownerCnt[node]);
        }
    }
    Store tiny(2,1);
    apply(tiny,INC,0,0);apply(tiny,INC,0,1);
    auto before=tiny.primary;auto pool=tiny.pool;auto meta=tiny.allocator;
    check(tiny.prepare(INC,1,0).status==OK); // primary owners consume no pool slots.
    auto full=tiny.prepare(INC,0,2);check(full.status==CAPACITY);
    check(tiny.commit(full)==CAPACITY && tiny.primary==before && tiny.pool==pool && tiny.allocator==meta);
    auto plan=tiny.prepare(DEC,0,0);
    check(tiny.primary==before && tiny.pool==pool && tiny.allocator==meta);
    check(tiny.commit(plan)==OK); // promotion frees the sole slot.
    check(tiny.commit(plan)==STALE);
    apply(tiny,INC,1,3);apply(tiny,INC,1,4); // free-list reuse on another node.
    check(tiny.prepare(DEC,1,5).status==UNDERFLOW);
    check(tiny.prepare(INC,2,0).status==RANGE);
    check(tiny.prepare(GET,0,0x80000000u).status==RANGE);
    check(tiny.prepare(9,0,0).status==BAD_OP);
    Store refs(1,1);for(unsigned i=0;i<65535;++i)apply(refs,INC,0,0);
    check(refs.prepare(INC,0,0).status==REF_LIMIT);
    for(unsigned i=0;i<65535;++i)apply(refs,INC,0,1);
    check(refs.prepare(INC,0,1).status==REF_LIMIT);
    for(unsigned i=0;i<65535;++i)apply(refs,DEC,0,0);
    check(refs.prepare(GET,0,1).count==65535); // exact-width promotion.
    for(unsigned i=0;i<65535;++i)apply(refs,DEC,0,1);
    check(refs.primary[0]==Record{} && refs.allocator[2]==0);
    Store many(1,255);for(unsigned i=0;i<256;++i)apply(many,INC,0,i);
    check(many.prepare(GET,0,255).occupancy==256); // occupancy is not truncated to hot's 8 bits.
    auto corrupt=many.pool[0];many.pool[0][2]=1;
    check(many.prepare(GET,0,0).status==CORRUPT);many.pool[0]=corrupt;
    many.primary[0][3]=1;check(many.prepare(GET,0,0).status==CORRUPT);
    std::cout<<"OWNER_UNIT_PASS random_mutations="<<mutations<<" queried_nets=3200000 refs_limit=65535 distinct_nets=256 capacity_reuse=1 stale_plan=1\n";
}
static uint32_t u32(const unsigned char* p) {return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
static void write_record(std::ofstream& f,const Record& r) {
    for(uint32_t w:r)for(unsigned shift=0;shift<32;shift+=8)f.put(char(w>>shift));
}
static void replay(const char* input,const char* prefix,unsigned capacity) {
    Store s(9089009,capacity);std::ifstream in(input,std::ios::binary);check(bool(in));
    uint64_t events=0,writes=0,markers=0,peak_live=0,max_writes=0;
    std::array<unsigned char,32> b;
    while(in.read(reinterpret_cast<char*>(b.data()),b.size())) {
        uint32_t r[8];for(unsigned i=0;i<8;++i)r[i]=u32(b.data()+4*i);
        if(r[0]==0){check(r[1]==s.primary.size());++markers;continue;}
        check(r[0]==INC || r[0]==DEC);
        auto p=s.prepare(r[0],r[1],r[2]);
        if(p.status!=OK) {std::cerr<<"REPLAY_FAILURE event="<<events<<" status="<<p.status<<"\n";check(false);}
        check(p.count==r[3] && p.occupancy==r[4]);
        writes+=p.writes.size();max_writes=std::max<uint64_t>(max_writes,p.writes.size());
        check(s.commit(p)==OK);
        auto q=s.prepare(GET,r[1],r[2]);check(q.status==OK && q.count==r[3] && q.occupancy==r[4]);
        check(q.will_overuse==uint32_t(r[4]>1 || (r[4]==1 && r[3]==0)));
        peak_live=std::max<uint64_t>(peak_live,s.allocator[2]);++events;
    }
    check(in.eof() && in.gcount()==0 && markers==1 && events==18515060);
    std::ofstream primary(std::string(prefix)+".primary",std::ios::binary),pool(std::string(prefix)+".pool",std::ios::binary),meta(std::string(prefix)+".allocator",std::ios::binary);
    for(auto r:s.primary)write_record(primary,r);for(auto r:s.pool)write_record(pool,r);write_record(meta,s.allocator);
    primary.flush();pool.flush();meta.flush();check(bool(primary)&&bool(pool)&&bool(meta));
    std::cout<<"OWNER_REPLAY_PASS events="<<events<<" capacity="<<capacity<<" peak_live="<<peak_live<<" planned_record_writes="<<writes<<" max_writes="<<max_writes<<" final_live="<<s.allocator[2]<<"\n";
}
int main(int argc,char** argv) {
    if(argc==1)unit();else {check(argc==4);replay(argv[1],argv[2],unsigned(std::stoul(argv[3])));}
}
