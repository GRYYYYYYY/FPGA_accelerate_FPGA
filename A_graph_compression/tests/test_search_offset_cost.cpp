// Same 10000 native-ledger oracle cases, using offset-based cost buffers.
#include "../src/native/site_ledger.hpp"
#include "search_offset_cost.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
using Cost=fpga_search::SearchOffsetCost<256,64,2048,8,8,8>;
using Status=fpga_search::CostStatus;
using Row=std::array<uint64_t,4>;
using Hist=std::array<uint64_t,2>;
uint64_t key(site_native::ResourceKey k){return (uint64_t(k.first)<<32)|k.second;}
Cost::State pack(const site_native::Normalized& n) {
    Cost::State s{};
    for (auto v:n.signals)s.signals.data[s.signals.count++]=v;
    for (auto v:n.bits)s.bits.data[s.bits.count++]={v.first,v.second.first,v.second.second};
    for (auto v:n.values)s.values.data[s.values.count++]={v.first,v.second};
    return s;
}
std::vector<uint64_t> words(std::vector<Row> rows) {
    std::sort(rows.begin(),rows.end());std::vector<uint64_t> out;
    for(const auto& r:rows)out.insert(out.end(),r.begin(),r.end());
    return out;
}
std::vector<uint64_t> history_words(const site_native::SiteHistory& history) {
    std::vector<uint64_t> out;for(auto p:history){out.push_back(key(p.first));out.push_back(p.second);}return out;
}
site_native::Demands payload(const site_native::Normalized& n) {
    site_native::Demands d{true,false,{},{},{}};
    d.signals.assign(n.signals.begin(),n.signals.end());
    for(auto p:n.bits)d.bits.emplace_back(p.first,p.second.first,p.second.second);
    for(auto p:n.values)d.values.emplace_back(p);
    return d;
}
site_native::Normalized random_state(std::mt19937_64& rng) {
    site_native::Normalized n;
    for(unsigned i=0;i<8;++i) {
        if(rng()%3==0)n.signals.insert(i);
        if(rng()%3==0){uint64_t mask=rng()%256;n.bits[i]={mask,rng()&mask};}
        if(rng()%3==0)n.values[i]=rng()%4;
    }
    return n;
}
int main() {
    std::mt19937_64 rng(2026102401);unsigned allowed=0,rejected=0;
    for(unsigned trial=0;trial<10000;++trial) {
        site_native::DemandLedger ledger;std::vector<Row> rows,fixed_rows;
        for(unsigned owner=0;owner<6;++owner) {
            auto n=random_state(rng);ledger.replace(owner,n);
            for(auto e:site_native::entries(n))rows.push_back({key(e.first),owner,e.second.first,e.second.second});
        }
        auto before=random_state(rng),after=random_state(rng),config=random_state(rng);config.signals.clear();
        std::vector<std::pair<uint32_t,uint32_t>> fixed_signals;
        for(unsigned i=0;i<8;++i)if(rng()%3==0){unsigned owner=rng()%7;fixed_signals.emplace_back(i,owner);fixed_rows.push_back({i,owner,0,0});}
        for(auto e:site_native::entries(config))fixed_rows.push_back({key(e.first),0,e.second.first,e.second.second});
        site_native::SiteState fixed(fixed_signals,payload(config));site_native::SiteHistory history;
        for(unsigned kind=0;kind<3;++kind)for(unsigned field=0;field<8;++field)if(rng()%2)history[{kind,field}]=rng()%50;
        auto ow=words(rows),fw=words(fixed_rows),hw=history_words(history);Cost cost;
        std::vector<uint64_t> flat(13,0xabcdef123456ULL);const uint64_t ow_at=flat.size();flat.insert(flat.end(),ow.begin(),ow.end());
        const uint64_t hw_at=flat.size();flat.insert(flat.end(),hw.begin(),hw.end());const uint64_t fw_at=flat.size();flat.insert(flat.end(),fw.begin(),fw.end());
        assert(cost.bind(flat.data(),{ow_at,hw_at,fw_at,unsigned(rows.size()),unsigned(history.size()),unsigned(fixed_rows.size())})==Status::ok);
        auto a=pack(before),b=pack(after);unsigned net=rng()%7;uint64_t present=rng()%17;
        uint64_t value=123;assert(cost.penalty(flat.data(),net,a,b,present,value)==Status::ok);
        assert(value==ledger.penalty(net,before,after,present,history));
        bool compatible=false;assert(cost.compatible(flat.data(),net,b,compatible)==Status::ok);
        assert(compatible==!fixed.conflicts(net,payload(after)));if(compatible)++allowed;else ++rejected;
        present=1+rng()%16;uint64_t others=rng()%7,past=rng()%50;
        assert(cost.step_cost(flat.data(),net,a,b,present,others,past,value)==Status::ok);
        assert(value==1+present*others+past+ledger.penalty(net,before,after,present,history));
        assert(cost.penalty(flat.data(),net,b,b,UINT64_MAX,value)==Status::ok && value==0);
    }
    std::cout<<"OFFSET_COST_RANDOM_PASS cases=10000 compatible="<<allowed<<" incompatible="<<rejected<<'\n';
}
