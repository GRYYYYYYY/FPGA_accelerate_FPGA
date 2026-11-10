#include "search_site_request.hpp"
#include "../src/native/site_ledger.hpp"
#include <array>
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>
extern "C" void search_site_request_top(const uint64_t*,uint64_t*,uint64_t*);
constexpr uint64_t Guard=UINT64_C(0x123456789abcdef0);
// Literal ABI packing independent of DUT state-storage helper.
std::array<uint64_t,66> pack(const site_native::Normalized& d){
    std::array<uint64_t,66> s{};s.back()=Guard;
    s[0]=(uint64_t(d.signals.size())<<32)|(uint64_t(d.bits.size())<<40)|(uint64_t(d.values.size())<<48);
    unsigned i=0;for(auto id:d.signals){s[1+i/2]|=uint64_t(id)<<(32*(i%2));++i;}
    i=0;for(auto b:d.bits){s[17+i/2]|=uint64_t(b.first)<<(32*(i%2));s[25+i]=b.second.first;s[41+i]=b.second.second;++i;}
    i=0;for(auto v:d.values)s[57+i++]=(uint64_t(v.second)<<32)|v.first;
    return s;
}
int main(){
    std::mt19937_64 rng(0x41524551);std::vector<uint64_t> request(196609,Guard);
    std::array<uint64_t,3> result{};unsigned rejected=0;
    auto call=[&](const std::array<uint64_t,66>& state,unsigned status,const site_native::Normalized& expected){
        const auto input=state;const auto before=request;result.fill(Guard);
        search_site_request_top(state.data(),request.data(),result.data());
        assert(state==input && result[0]==status && result.back()==Guard && request.back()==Guard);
        if(status){assert(result[1]==0 && request==before);++rejected;return;}
        const auto entries=site_native::entries(expected);assert(result[1]==entries.size());unsigned at=0;
        for(auto e:entries){assert(request[at++]==((uint64_t(e.first.first)<<32)|e.first.second));assert(request[at++]==e.second.first);assert(request[at++]==e.second.second);}
        assert(std::equal(request.begin()+at,request.end(),before.begin()+at));
    };
    for(unsigned trial=0;trial<2000;++trial){
        site_native::Normalized d;
        for(unsigned i=0,n=rng()%33;i<n;++i)d.signals.insert(uint32_t(rng()));
        for(unsigned i=0,n=rng()%17;i<n;++i){uint64_t mask=rng();d.bits[uint32_t(rng())]={mask,rng()&mask};}
        for(unsigned i=0,n=rng()%9;i<n;++i)d.values[uint32_t(rng())]=uint32_t(rng());
        call(pack(d),0,d);
    }
    site_native::Normalized full;
    for(unsigned i=0;i<32;++i)full.signals.insert(i==31?UINT32_MAX:i);
    for(unsigned i=0;i<16;++i)full.bits[i==15?UINT32_MAX:i]={i?UINT64_MAX:0,i?UINT64_C(1)<<63:0};
    for(unsigned i=0;i<8;++i)full.values[i==7?UINT32_MAX:i]=UINT32_MAX-i;
    auto good=pack(full);call(good,0,full);assert(result[1]==56);
    auto bad=good;bad[0]|=1;call(bad,1,{});
    bad=good;bad[0]|=UINT64_C(1)<<56;call(bad,1,{});
    bad=good;bad[0]+=UINT64_C(1)<<32;call(bad,1,{});
    bad=good;bad[0]+=UINT64_C(1)<<40;call(bad,1,{});
    bad=good;bad[0]+=UINT64_C(1)<<48;call(bad,1,{});
    bad=good;bad[1]=0;call(bad,1,{});
    bad=good;bad[17]=0;call(bad,1,{});
    bad=good;bad[41]=1;call(bad,1,{});
    bad=good;bad[58]=bad[57];call(bad,1,{});
    const auto before=request;unsigned count=99;
    assert(fpga_search::SiteRequest<55>::run(good.data(),request.data(),count)==2 && !count && request==before);
    site_native::Normalized small;small.bits[UINT32_MAX]={0,0};auto unused=pack(small);unused[16]=unused[64]=UINT64_MAX;
    call(unused,0,small);call(pack({}),0,{});
    std::cout<<"SITE_REQUEST_CPU_PASS random=2000 max_records=56 invalid=9 capacity=1 zero_mask=1 full_depth=196608\n";
    assert(rejected==9);
}
