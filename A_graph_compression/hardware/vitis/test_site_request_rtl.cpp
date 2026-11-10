// Independent literal ABI and ordered-map oracle; no DUT headers/helpers.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>
extern "C" void search_site_request_top(const uint64_t*,uint64_t*,uint64_t*);
constexpr uint64_t Guard=UINT64_C(0x123456789abcdef0);
struct Bench {
    std::array<uint64_t,66> state{};
    std::vector<uint64_t> request=std::vector<uint64_t>(196609,Guard),expected=request;
    std::map<uint64_t,std::pair<uint64_t,uint64_t>> entries;
    unsigned transaction=0;
    void make(unsigned ns,unsigned nb,unsigned nv){
        state.fill(0);state.back()=Guard;entries.clear();
        state[0]=(uint64_t(ns)<<32)|(uint64_t(nb)<<40)|(uint64_t(nv)<<48);
        for(unsigned i=0;i<ns;++i){uint32_t id=i+1==ns?UINT32_MAX:i;state[1+i/2]|=uint64_t(id)<<(32*(i%2));entries[id]={0,0};}
        for(unsigned i=0;i<nb;++i){uint32_t id=i+1==nb?UINT32_MAX:i;uint64_t mask=i?UINT64_MAX:0,value=i?UINT64_C(1)<<63:0;
            state[17+i/2]|=uint64_t(id)<<(32*(i%2));state[25+i]=mask;state[41+i]=value;entries[(UINT64_C(1)<<32)|id]={mask,value};}
        for(unsigned i=0;i<nv;++i){uint32_t id=i+1==nv?UINT32_MAX:i,value=UINT32_MAX-i;state[57+i]=(uint64_t(value)<<32)|id;entries[(UINT64_C(2)<<32)|id]={0,value};}
    }
    void call(unsigned status){
        const auto before=state;std::array<uint64_t,3> result{{Guard,Guard,Guard}};
        if(!status){unsigned at=0;for(auto e:entries){expected[at++]=e.first;expected[at++]=e.second.first;expected[at++]=e.second.second;}}
        search_site_request_top(state.data(),request.data(),result.data());
        assert(state==before && request==expected && result[0]==status && result[1]==(status?0:entries.size()) && result.back()==Guard);
        std::cout<<"SITE_REQUEST_RTL_TX "<<transaction++<<' '<<result[0]<<' '<<result[1]<<'\n';
    }
};
int main(){
    Bench b;
    for(unsigned i=0;i<20;++i){b.make(i%33,i%17,i%9);b.call(0);}
    b.make(32,16,8);b.call(0);b.make(0,0,0);b.call(0);
    b.make(0,1,0);b.call(0);b.state[16]=b.state[64]=UINT64_MAX;b.call(0);
    auto good=[&](){b.make(32,16,8);};
    good();b.state[0]|=1;b.call(1);
    good();b.state[0]|=UINT64_C(1)<<56;b.call(1);
    good();b.state[0]+=UINT64_C(1)<<32;b.call(1);
    good();b.state[0]+=UINT64_C(1)<<40;b.call(1);
    good();b.state[0]+=UINT64_C(1)<<48;b.call(1);
    good();b.state[1]=0;b.call(1);
    good();b.state[17]=0;b.call(1);
    good();b.state[41]=1;b.call(1);
    good();b.state[58]=b.state[57];b.call(1);
    good();b.call(0);
    assert(b.transaction==34);
    std::cout<<"SITE_REQUEST_RTL_GOLDEN_PASS transactions=34 max_records=56 full_depth=196608\n";
}
