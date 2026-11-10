// Full-depth, full-capacity production RTL stimulus. No DUT helper is included.
// Ordered STL maps/pairwise conflicts are a CPU oracle, not synthesized logic.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>

extern "C" void search_site_occupancy_top(const uint64_t*,uint64_t*,uint64_t*,uint64_t*,const uint64_t*,uint32_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*);
constexpr unsigned Capacity=65536;
constexpr uint64_t Guard=UINT64_C(0xa5a5a5a55a5a5a5a),Magic=UINT64_C(0x41534954454f5731);
constexpr uint32_t Guard32=0xdeadbeef;
using Request=std::array<uint64_t,3>;
using Value=std::pair<uint64_t,uint64_t>;
using Entries=std::map<uint64_t,Value>;
using Conflicts=std::map<uint64_t,std::set<uint32_t>>;
uint64_t key(unsigned kind,uint32_t id){return (uint64_t(kind)<<32)|id;}

struct Buffers {
    std::array<uint64_t,7> meta{{Guard,Guard,Guard,Guard,Guard,Guard,Guard}};
    std::vector<uint64_t> owners=std::vector<uint64_t>(8*Capacity+1,Guard);
    std::vector<uint64_t> history=std::vector<uint64_t>(4*Capacity+1,Guard);
    std::vector<uint32_t> flags=std::vector<uint32_t>(Capacity+1,Guard32);
    std::vector<uint64_t> summaries=std::vector<uint64_t>(2*Capacity+1,Guard);
    std::vector<uint64_t> out=std::vector<uint64_t>(4*Capacity+1,Guard);
    std::vector<uint64_t> hout=std::vector<uint64_t>(2*Capacity+1,Guard);
    bool operator==(const Buffers& b)const {
        return meta==b.meta && owners==b.owners && history==b.history && flags==b.flags &&
               summaries==b.summaries && out==b.out && hout==b.hout;
    }
};
struct Bench {
    Buffers actual,expected;
    std::vector<uint64_t> input=std::vector<uint64_t>(3*Capacity+1,Guard);
    std::map<uint32_t,Entries> nets;
    std::map<uint64_t,uint64_t> past;
    unsigned transaction=0;
    std::vector<std::array<uint64_t,4>> rows()const {
        std::vector<std::array<uint64_t,4>> result;
        for(const auto& n:nets)for(const auto& e:n.second)result.push_back({{e.first,n.first,e.second.first,e.second.second}});
        std::sort(result.begin(),result.end());return result;
    }
    Conflicts conflicts()const {
        std::map<uint64_t,std::map<uint32_t,Value>> users;
        for(const auto& n:nets)for(const auto& e:n.second)users[e.first][n.first]=e.second;
        Conflicts result;
        for(const auto& r:users)for(auto a=r.second.begin();a!=r.second.end();++a) {
            auto b=a;++b;
            for(;b!=r.second.end();++b) {
                const auto kind=r.first>>32;bool bad=false;
                if(kind==0)bad=true;
                else if(kind==1)bad=((a->second.second^b->second.second)&a->second.first&b->second.first)!=0;
                else bad=a->second.second!=b->second.second;
                if(bad){result[r.first].insert(a->first);result[r.first].insert(b->first);}
            }
        }
        return result;
    }
    void scratch(const Conflicts& bad) {
        const auto r=rows();
        for(unsigned i=0;i<r.size();++i) {
            const auto b=bad.find(r[i][0]);
            expected.flags[i]=(b!=bad.end() && b->second.count(uint32_t(r[i][1])))?1:0;
        }
        unsigned i=0;for(const auto& b:bad){expected.summaries[2*i]=b.first;expected.summaries[2*i+1]=b.second.size();++i;}
    }
    void seed_history(uint64_t k,uint64_t v) {
        assert(past.count(k));past[k]=v;
        const unsigned base=unsigned(expected.meta[3])*2*Capacity;bool found=false;
        for(unsigned i=0;i<expected.meta[4];++i)if(expected.history[base+2*i]==k) {
            actual.history[base+2*i+1]=v;expected.history[base+2*i+1]=v;found=true;
        }
        assert(found);
    }
    void seed_version(uint64_t v){actual.meta[5]=v;expected.meta[5]=v;}
    void call(unsigned op,uint64_t net,const std::vector<Request>& requests,unsigned status,
              bool too_many=false,bool reserved=false) {
        assert(requests.size()<=Capacity);
        for(unsigned i=0;i<requests.size();++i)for(unsigned w=0;w<3;++w)input[3*i+w]=requests[i][w];
        std::array<uint64_t,9> config{{op,net,requests.size(),0,0,0,0,0,Guard}};
        if(too_many)config[2]=Capacity+1;
        if(reserved)config[7]=1;
        std::array<uint64_t,7> result{{Guard,Guard,Guard,Guard,Guard,Guard,Guard}};
        const auto old_input=input;const auto old_config=config;
        search_site_occupancy_top(config.data(),actual.meta.data(),actual.owners.data(),actual.history.data(),
            input.data(),actual.flags.data(),actual.summaries.data(),actual.out.data(),actual.hout.data(),result.data());
        assert(result[0]==status && result.back()==Guard && input==old_input && config==old_config);
        const auto bad=conflicts();uint64_t groups=0,snapshot_count=0;
        // Advance preflights version before touching scratch; late failures may
        // update scratch but must preserve BOTH persistent banks and outputs.
        if((op==2 && status==0) || (op==3 && expected.meta[5]!=UINT64_MAX && status!=1))scratch(bad);
        if(status==0) {
            if(op==0) {
                nets.clear();past.clear();expected.meta={{Magic,0,0,0,0,1,Guard}};
            } else if(op==1) {
                Entries e;for(const auto& r:requests)assert(e.emplace(r[0],Value{r[1],r[2]}).second);
                nets[uint32_t(net)]=e;
                const auto r=rows();assert(r.size()<=Capacity);
                const unsigned bank=1-unsigned(expected.meta[1]),base=bank*4*Capacity;
                for(unsigned i=0;i<r.size();++i)for(unsigned w=0;w<4;++w)expected.owners[base+4*i+w]=r[i][w];
                expected.meta[1]=bank;expected.meta[2]=r.size();++expected.meta[5];
            } else if(op==2)groups=bad.size();
            else if(op==3) {
                for(const auto& b:bad)past[b.first]+=b.second.size()-1;
                assert(past.size()<=Capacity);
                const unsigned bank=1-unsigned(expected.meta[3]),base=bank*2*Capacity;unsigned i=0;
                for(const auto& h:past){expected.history[base+2*i]=h.first;expected.history[base+2*i+1]=h.second;++i;}
                expected.meta[3]=bank;expected.meta[4]=past.size();++expected.meta[5];groups=bad.size();
            } else if(op==4) {
                for(const auto& r:rows())if(r[1]!=net) {
                    for(unsigned w=0;w<4;++w)expected.out[4*snapshot_count+w]=r[w];
                    ++snapshot_count;
                }
                unsigned i=0;for(const auto& h:past){expected.hout[2*i]=h.first;expected.hout[2*i+1]=h.second;++i;}
            } else assert(false);
            assert(result[1]==expected.meta[2] && result[2]==expected.meta[4] && result[3]==expected.meta[5] &&
                   result[4]==groups && result[5]==snapshot_count);
        } else for(unsigned i=1;i<6;++i)assert(result[i]==0);
        // Exact equality includes inactive banks, stale tails, scratch and guards.
        assert(actual==expected && input.back()==Guard);
        std::cout<<"SITE_OCCUPANCY_RTL_CASE_PASS transaction="<<transaction++<<" op="<<op<<" status="<<status
                 <<" owners="<<actual.meta[2]<<" history="<<actual.meta[4]<<" version="<<actual.meta[5]
                 <<" groups="<<groups<<" snapshot="<<snapshot_count<<" full_depth=1 all_state=1 guards=1\n";
    }
};

int main() {
    Bench t;const uint64_t high=UINT64_C(1)<<63;
    const std::vector<Request> a={{{key(0,0),0,0}},{{key(1,7),1,0}},{{key(1,UINT32_MAX),high,0}},{{key(2,9),0,2}}};
    const std::vector<Request> b={{{key(0,0),0,0}},{{key(1,7),1,1}},{{key(1,UINT32_MAX),high,high}},{{key(2,9),0,3}}};
    const std::vector<Request> c={{{key(0,1),0,0}},{{key(1,7),2,2}},{{key(2,9),0,3}}};
    t.call(0,0,{},0);                                             // 0
    t.call(1,0,a,0);                                              // 1
    t.call(1,UINT32_MAX,b,0);                                      // 2
    t.call(1,3,c,0);                                              // 3: disjoint bit owner excluded
    t.call(2,0,{},0);                                             // 4
    t.call(4,UINT32_MAX,{},0);                                     // 5
    t.call(3,0,{},0);                                             // 6
    t.call(4,0,{},0);                                             // 7
    t.call(1,3,c,0);                                              // 8: same request remains idempotent
    t.call(1,UINT32_MAX,{},0);                                     // 9
    t.call(2,0,{},0);                                             //10
    t.call(3,0,{},0);                                             //11
    t.call(1,0,{{{0,0,0}},{{0,0,0}}},1);                          //12: duplicate
    t.call(1,0,{{{1,0,0}},{{0,0,0}}},1);                          //13: order
    t.call(1,0,{{{key(1,0),0,1}}},1);                             //14: mask
    t.call(1,0,{{{key(2,0),0,UINT64_C(1)<<32}}},1);                //15: categorical width
    t.call(1,0,{{{0,1,0}}},1);                                    //16: signal encoding
    t.call(1,0,{{{key(3,0),0,0}}},1);                             //17: kind
    t.call(1,0,{},2,true);                                        //18: count, without reading excess
    t.call(1,UINT64_C(1)<<32,{},1);                               //19: net width
    t.call(4,0,{},1,false,true);                                  //20: reserved control
    t.call(1,UINT32_MAX,{{{0,0,0}},{{key(1,7),1,1}},{{key(2,9),0,4}}},0); //21
    t.seed_history(key(1,7),UINT64_MAX);
    t.call(3,0,{},3);                                             //22: late overflow, earlier signal unchanged
    t.seed_history(key(1,7),UINT64_MAX-1);
    t.call(3,0,{},0);                                             //23: exact saturation
    t.call(4,3,{},0);                                             //24
    const uint64_t version=t.actual.meta[5];t.seed_version(UINT64_MAX);
    t.call(1,0,a,3);                                             //25: version overflow
    t.call(3,0,{},3);                                             //26
    t.call(4,0,{},0);                                             //27: reads still permitted
    t.seed_version(version);
    t.call(1,3,{},0);                                             //28: recovery
    t.call(0,0,{},0);                                             //29: logical reset, bank tails preserved
    std::vector<Request> full,first,second;
    for(unsigned i=0;i<Capacity;++i)full.push_back({{i,0,0}});
    first.assign(full.begin(),full.begin()+Capacity/2);second.assign(full.begin()+Capacity/2,full.end());
    t.call(1,UINT32_MAX,full,0);                                  //30: FULL request and owner capacity
    t.call(1,0,{{{UINT32_MAX,0,0}}},2);                            //31: true owner capacity rejection
    t.call(4,0,{},0);                                             //32: full owner snapshot
    t.call(1,UINT32_MAX,first,0);                                 //33
    t.call(1,0,first,0);                                          //34: 32768 real conflicting resources
    t.call(3,0,{},0);                                             //35: create first half of history
    t.call(1,UINT32_MAX,{},0);                                    //36
    t.call(1,0,second,0);                                         //37
    t.call(1,UINT32_MAX,second,0);                                //38
    t.call(3,0,{},0);                                             //39: FULL history via actual rounds
    t.call(4,3,{},0);                                             //40: full owner AND history snapshots
    t.call(1,0,{},0);                                             //41
    t.call(1,UINT32_MAX,{{{UINT32_MAX,0,0}}},0);                   //42
    t.call(1,0,{{{UINT32_MAX,0,0}}},0);                            //43
    t.call(3,0,{},2);                                             //44: true history capacity rejection
    t.call(1,0,{},0);                                             //45
    t.call(2,0,{},0);                                             //46: stale scratch tails checked
    t.call(3,0,{},0);                                             //47: full history retained without conflicts
    t.call(4,UINT32_MAX,{},0);                                    //48: self exclusion, all history preserved
    t.call(0,0,{},0);                                             //49
    t.call(4,0,{},0);                                             //50: empty snapshot writes no tails
    t.call(99,0,{},1);                                            //51: unknown opcode
    assert(t.transaction==52);
    std::cout<<"SITE_OCCUPANCY_RTL_ALL_PASS transactions=52 production_owners=65536 production_history=65536 production_requests=65536 full_depth=1\n";
}
