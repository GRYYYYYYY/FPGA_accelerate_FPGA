#include "../hardware/vitis/search_node_occupancy.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

using Status=fpga_search::OccupancyStatus;
extern "C" void search_node_occupancy_top(const uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*,uint32_t*,
                                         const uint32_t*,const uint32_t*,uint64_t*,uint64_t*);
template<unsigned Nodes,unsigned Slots> struct Storage {
    using Core=fpga_search::NodeOccupancy<Nodes,Slots>;
    std::array<uint64_t,4> meta{{0,0,0,0}};
    std::vector<uint32_t> counts=std::vector<uint32_t>(Nodes+1,0xf00d);
    std::vector<uint64_t> history=std::vector<uint64_t>(Nodes+1,0xf00d);
    std::vector<uint64_t> keys=std::vector<uint64_t>(Slots+1,0xf00d);
    std::vector<uint32_t> flags=std::vector<uint32_t>(Slots+1,0xf00d);
    std::vector<uint64_t> output=std::vector<uint64_t>(2*Nodes+1,0xf00d);
    bool operator==(const Storage& b)const {
        return meta==b.meta && counts==b.counts && history==b.history && keys==b.keys && flags==b.flags && output==b.output;
    }
    void guard()const {
        assert(counts.back()==0xf00d && history.back()==0xf00d && keys.back()==0xf00d &&
               flags.back()==0xf00d && output.back()==0xf00d);
    }
    void reset(unsigned n=Nodes) {assert(Core::reset(n,meta.data(),counts.data(),history.data(),flags.data())==Status::ok);}
    Status update(uint32_t net,const std::vector<uint32_t>& old,const std::vector<uint32_t>& next) {
        return Core::update(net,old.data(),unsigned(old.size()),next.data(),unsigned(next.size()),
                            meta.data(),counts.data(),keys.data(),flags.data());
    }
    void snapshot(uint32_t net) {
        assert(Core::snapshot(net,meta.data(),counts.data(),history.data(),keys.data(),flags.data(),output.data())==Status::ok);
    }
};

void random_differential() {
    using S=Storage<64,128>;S s;s.reset();std::mt19937_64 rng(2026102404);
    std::vector<std::set<uint32_t>> expected(64);std::vector<uint64_t> past(64);
    unsigned accepted=0,capacity=0,advances=0;
    for(unsigned iteration=0;iteration<12000;++iteration) {
        const uint32_t net=iteration%17==0?UINT32_MAX:uint32_t(rng()%24);
        if(iteration%7==0) {
            uint64_t conflicts=0,actual=999;for(unsigned n=0;n<64;++n)if(expected[n].size()>1){++conflicts;past[n]+=expected[n].size()-1;}
            assert(S::Core::advance(s.meta.data(),s.counts.data(),s.history.data(),actual)==Status::ok && actual==conflicts);++advances;
        } else {
            std::vector<uint32_t> old,next;
            for(unsigned n=0;n<64;++n)if(expected[n].count(net))old.push_back(n);
            std::set<uint32_t> requested;const unsigned count=unsigned(rng()%18);
            for(unsigned i=0;i<count;++i)requested.insert(unsigned(rng()%64));
            next.assign(requested.begin(),requested.end());
            const auto before=s;const auto total=s.meta[2]-old.size()+next.size();const auto status=s.update(net,old,next);
            if(total>128){assert(status==Status::capacity && s==before);++capacity;}
            else {
                assert(status==Status::ok);++accepted;
                for(auto n:old)expected[n].erase(net);
                for(auto n:next)expected[n].insert(net);
            }
        }
        s.snapshot(net);
        std::vector<std::set<uint32_t>> decoded(64);uint64_t pairs=0;
        for(unsigned i=0;i<128;++i)if(s.flags[i]==1){const auto v=s.keys[i];assert(uint32_t(v)<64);assert(decoded[uint32_t(v)].insert(uint32_t(v>>32)).second);++pairs;}
        assert(decoded==expected && pairs==s.meta[2]);
        for(unsigned n=0;n<64;++n) {
            assert(s.counts[n]==expected[n].size() && s.history[n]==past[n]);
            assert(s.output[2*n]==expected[n].size()-expected[n].count(net) && s.output[2*n+1]==past[n]);
        }
        s.guard();
    }
    assert(accepted && capacity && advances);
    std::cout<<"NODE_OCCUPANCY_RANDOM_PASS operations=12000 accepted="<<accepted<<" capacity_rejections="<<capacity<<" rounds="<<advances<<'\n';
}

void boundaries() {
    using S=Storage<8,8>;S s;s.reset();
    // Exactly full table, every net owns the same canonical node.
    for(unsigned net=0;net<8;++net)assert(s.update(net,{}, {0})==Status::ok);
    assert(s.meta[2]==8 && s.counts[0]==8);auto before=s;
    assert(s.update(8,{}, {1})==Status::capacity && s==before);
    // Full table replacement reuses the released slot, and tombstones do not
    // hide remaining colliding owners or make a duplicated acquisition grow.
    assert(s.update(0,{0},{1})==Status::ok);
    assert(s.update(0,{}, {1})==Status::ok && s.meta[2]==8);
    s.snapshot(0);assert(s.output[0]==7 && s.output[2]==0);
    s.snapshot(1);assert(s.output[0]==6 && s.output[2]==1);
    for(unsigned net=0;net<8;++net)assert(s.update(net,{net==0?1u:0u},{})==Status::ok);
    assert(s.meta[2]==0);
    assert(s.update(UINT32_MAX,{}, {0,7})==Status::ok);
    assert(s.update(0,{}, {0,7})==Status::ok); // distinct owner even for key 0
    before=s;
    for(const auto& nodes:std::vector<std::vector<uint32_t>>{{0,0},{7,0},{8}}) {
        assert(s.update(1,{},nodes)==Status::invalid && s==before);
        assert(s.update(1,nodes,{})==Status::invalid && s==before);
    }
    assert(s.update(1,{0},{})==Status::missing_owner && s==before);
    assert(s.update(1,{},std::vector<uint32_t>(9,0))==Status::capacity && s==before);
    // Overflow at a later node must not increment an earlier node first.
    s.history[7]=UINT64_MAX;before=s;uint64_t count=999;
    assert(S::Core::advance(s.meta.data(),s.counts.data(),s.history.data(),count)==Status::overflow && count==999 && s==before);
    s.history[7]=UINT64_MAX-1;count=0;
    assert(S::Core::advance(s.meta.data(),s.counts.data(),s.history.data(),count)==Status::ok && count==2 && s.history[7]==UINT64_MAX);
    s.meta[3]=UINT64_MAX;before=s;
    assert(s.update(0,{0,7},{})==Status::overflow && s==before);
    s.reset(2);s.snapshot(0);assert(s.output[0]==0 && s.output[1]==0 && s.output[2]==0 && s.output[3]==0);
    assert(s.meta[2]==0);s.guard();
    std::cout<<"NODE_OCCUPANCY_BOUNDARIES_PASS\n";
}

void production() {
    Storage<1048576,2097152> s;std::array<uint64_t,8> config{{0,0,1048576,0,0,0,0,0}};
    uint64_t result[4]{};std::vector<uint32_t> old,next;
    auto call=[&](){search_node_occupancy_top(config.data(),s.meta.data(),s.counts.data(),s.history.data(),s.keys.data(),
        s.flags.data(),old.data(),next.data(),s.output.data(),result);};
    call();assert(result[0]==0 && result[1]==0 && result[2]==1);
    config={{1,UINT32_MAX,0,0,1048576,0,0,0}};next.resize(1048576);
    for(unsigned n=0;n<1048576;++n)next[n]=n;
    call();assert(result[0]==0 && result[1]==1048576);
    for(auto net:std::vector<uint64_t>{0,UINT32_MAX}) {
        config={{3,net,0,0,0,0,0,0}};call();assert(result[0]==0);
        for(unsigned n=0;n<1048576;++n)assert(s.output[2*n]==(net==UINT32_MAX?0:1) && s.output[2*n+1]==0);
    }
    config={{1,0,0,0,2,0,0,0}};next={0,1048575};call();assert(result[0]==0 && result[1]==1048578);
    config={{2,0,0,0,0,0,0,0}};call();assert(result[0]==0 && result[3]==2);
    assert(s.history[0]==1 && s.history[1048575]==1 && s.history[1]==0);
    old.resize(1048576);for(unsigned n=0;n<1048576;++n)old[n]=n;
    config={{1,UINT32_MAX,0,1048576,0,0,0,0}};call();assert(result[0]==0 && result[1]==2);
    config={{3,0,0,0,0,0,0,0}};call();assert(result[0]==0);
    for(unsigned n=0;n<1048576;++n)assert(s.output[2*n]==0 && s.output[2*n+1]==(n==0 || n==1048575?1:0));
    // Production ABI rejects oversized scalars/reserved fields/opcode and preserves all buffers.
    const auto before=s;
    for(const auto& bad:std::vector<std::array<uint64_t,8>>{
        {{4,0,0,0,0,0,0,0}},{{1,uint64_t(UINT32_MAX)+1,0,0,0,0,0,0}},
        {{1,0,0,0,1048577,0,0,0}},{{1,0,0,0,0,1,0,0}},{{0,0,0,0,0,0,0,0}}}) {
        config=bad;call();assert(result[0]!=0 && s==before);
    }
    s.guard();std::cout<<"NODE_OCCUPANCY_PRODUCTION_PASS nodes=1048576 peak_pairs=1048578 slots=2097152\n";
}

int main(){random_differential();boundaries();production();std::cout<<"NODE_OCCUPANCY_ALL_PASS\n";}
