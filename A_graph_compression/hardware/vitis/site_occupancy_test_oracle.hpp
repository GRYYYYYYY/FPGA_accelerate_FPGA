#pragma once
// CPU-only C++14 test oracle for HLS 2022.2's testbench compiler. The regular
// sanitizer test instead uses the untouched native site_ledger.hpp reference.
// Deliberately use pairwise comparison, not the DUT's OR aggregation.
#include <cstdint>
#include <map>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>
namespace site_native {
using ResourceKey=std::pair<unsigned,uint32_t>;
using ResourceValue=std::pair<uint64_t,uint64_t>;
using Entries=std::map<ResourceKey,ResourceValue>;
using SiteHistory=std::map<ResourceKey,uint64_t>;
struct Normalized {
    std::set<uint32_t> signals;
    std::map<uint32_t,ResourceValue> bits;
    std::map<uint32_t,uint32_t> values;
};
inline Entries entries(const Normalized& d) {
    Entries e;
    for(auto id:d.signals)e[{0,id}]={0,0};
    for(const auto& x:d.bits) {
        if(x.second.second&~x.second.first)throw std::invalid_argument("bad test mask");
        e[{1,x.first}]=x.second;
    }
    for(const auto& x:d.values)e[{2,x.first}]={0,x.second};
    return e;
}
class DemandLedger {
    std::map<uint32_t,Entries> nets;
public:
    void replace(uint32_t net,const Normalized& d){nets[net]=entries(d);}
    std::map<ResourceKey,std::set<uint32_t>> conflicts()const {
        std::map<ResourceKey,std::set<uint32_t>> result;
        for(auto a=nets.begin();a!=nets.end();++a) {
            auto b=a;++b;
            for(;b!=nets.end();++b)for(const auto& x:a->second) {
                const auto found=b->second.find(x.first);if(found==b->second.end())continue;
                const auto& y=found->second;bool bad=false;
                if(x.first.first==0)bad=true;
                else if(x.first.first==1)bad=((x.second.second^y.second)&x.second.first&y.first)!=0;
                else bad=x.second.second!=y.second;
                if(bad){result[x.first].insert(a->first);result[x.first].insert(b->first);}
            }
        }
        return result;
    }
};
}
