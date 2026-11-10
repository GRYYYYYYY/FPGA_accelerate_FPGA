#include "../src/native/site_ledger.hpp"
#include "search_cost_snapshot.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
using Cost=fpga_search::SearchCostSnapshot<256,64,2048,8,8,8>;
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
        assert(cost.bind({ow.data(),hw.data(),fw.data(),unsigned(rows.size()),unsigned(history.size()),unsigned(fixed_rows.size())})==Status::ok);
        auto a=pack(before),b=pack(after);unsigned net=rng()%7;uint64_t present=rng()%17;
        uint64_t value=123;assert(cost.penalty(net,a,b,present,value)==Status::ok);
        assert(value==ledger.penalty(net,before,after,present,history));
        bool compatible=false;assert(cost.compatible(net,b,compatible)==Status::ok);
        assert(compatible==!fixed.conflicts(net,payload(after)));if(compatible)++allowed;else ++rejected;
        present=1+rng()%16;uint64_t others=rng()%7,past=rng()%50;
        assert(cost.step_cost(net,a,b,present,others,past,value)==Status::ok);
        assert(value==1+present*others+past+ledger.penalty(net,before,after,present,history));
        assert(cost.penalty(net,b,b,UINT64_MAX,value)==Status::ok && value==0);
    }
    std::cout<<"COST_RANDOM_PASS cases=10000 compatible="<<allowed<<" incompatible="<<rejected<<'\n';
    // Full global configuration exceeds path capacity and must remain separate.
    std::vector<Row> wide;for(unsigned i=0;i<954;++i)wide.push_back({(uint64_t(1)<<32)|i,0,1,1});
    auto fw=words(wide);Cost cost;assert(cost.bind({nullptr,nullptr,fw.data(),0,0,954})==Status::ok);
    Cost::State s{};s.bits.count=1;s.bits.data[0]={953,1,1};bool allowed_flag=false;
    assert(cost.compatible(0,s,allowed_flag)==Status::ok && allowed_flag);
    s.bits.data[0].value=0;assert(cost.compatible(0,s,allowed_flag)==Status::ok && !allowed_flag);
    // Zero-mask new fields carry history; exact unchanged fields are free.
    uint64_t hist[2]={(uint64_t(1)<<32)|3,7};s={};s.bits.count=1;s.bits.data[0]={3,0,0};
    assert(cost.bind({nullptr,hist,nullptr,0,1,0})==Status::ok);uint64_t out=91;
    assert(cost.penalty(0,{},s,8,out)==Status::ok && out==7);
    assert(cost.penalty(0,s,s,8,out)==Status::ok && out==0);
    // Own exclusive signal is excluded, different physical signals independent.
    uint64_t owners[8]={3,7,0,0,4,8,0,0};
    assert(cost.bind({owners,nullptr,owners,2,0,2})==Status::ok);s={};s.signals.count=1;s.signals.data[0]=3;
    assert(cost.penalty(7,{},s,8,out)==Status::ok && out==0);
    assert(cost.compatible(7,s,allowed_flag)==Status::ok && allowed_flag);
    assert(cost.penalty(6,{},s,8,out)==Status::ok && out==8);
    assert(cost.compatible(6,s,allowed_flag)==Status::ok && !allowed_flag);
    // Overflow in a resource increment, the site sum, node term and combined term.
    hist[0]=3;hist[1]=1;assert(cost.bind({owners,hist,nullptr,2,1,0})==Status::ok);out=91;
    assert(cost.penalty(0,{},s,UINT64_MAX,out)==Status::overflow && out==91);
    uint64_t sumhist[4]={3,UINT64_MAX,4,1};assert(cost.bind({nullptr,sumhist,nullptr,0,2,0})==Status::ok);
    s.signals.count=2;s.signals.data[1]=4;
    assert(cost.penalty(0,{},s,1,out)==Status::overflow && out==91);
    assert(cost.bind({nullptr,nullptr,nullptr,0,0,0})==Status::ok);
    assert(cost.step_cost(0,{},{},1,0,UINT64_MAX,out)==Status::overflow && out==91);
    assert(cost.step_cost(0,{},{},UINT64_MAX,1,0,out)==Status::overflow && out==91);
    assert(cost.step_cost(0,{},{},0,0,0,out)==Status::invalid && out==91);
    assert(cost.step_cost(0,{},{},1,0,UINT64_MAX-1,out)==Status::ok && out==UINT64_MAX);
    out=91;hist[1]=2;assert(cost.bind({nullptr,hist,nullptr,0,1,0})==Status::ok);
    assert(cost.step_cost(0,{},s,1,0,UINT64_MAX-2,out)==Status::overflow && out==91);
    // Invalid counts are rejected before touching null storage; failed bind
    // invalidates the old snapshot. Invalid output calls preserve output.
    assert(cost.bind({nullptr,nullptr,nullptr,257,0,0})==Status::capacity_exhausted);
    assert(cost.penalty(0,{},{},1,out)==Status::invalid && out==91);
    assert(cost.bind({nullptr,nullptr,nullptr,1,0,0})==Status::invalid);
    using Tiny=fpga_search::SearchCostSnapshot<1,1,1,8,8,8>;Tiny tiny;
    assert(tiny.bind({nullptr,nullptr,nullptr,0,2,0})==Status::capacity_exhausted);
    assert(tiny.bind({nullptr,nullptr,nullptr,0,0,2})==Status::capacity_exhausted);
    uint64_t malformed[8]={3,0,0,0,3,0,0,0};
    assert(cost.bind({malformed,nullptr,nullptr,2,0,0})==Status::invalid);
    malformed[4]=2;assert(cost.bind({malformed,nullptr,nullptr,2,0,0})==Status::invalid);
    malformed[4]=3;malformed[5]=1;assert(cost.bind({malformed,nullptr,nullptr,2,0,0})==Status::ok);
    assert(cost.bind({nullptr,nullptr,malformed,0,0,2})==Status::invalid);
    for(auto row:std::vector<Row>{{uint64_t(3)<<32,0,0,0},{3,UINT64_MAX,0,0},{3,0,1,0},
                                  {uint64_t(1)<<32,0,1,2},{uint64_t(2)<<32,0,1,0},{uint64_t(2)<<32,0,0,UINT64_MAX}})
        assert(cost.bind({row.data(),nullptr,nullptr,1,0,0})==Status::invalid);
    uint64_t nonzero_fixed_owner[4]={uint64_t(1)<<32,1,0,0};
    assert(cost.bind({nullptr,nullptr,nonzero_fixed_owner,0,0,1})==Status::invalid);
    uint64_t bad_history[4]={3,1,3,2};assert(cost.bind({nullptr,bad_history,nullptr,0,2,0})==Status::invalid);
    bad_history[0]=uint64_t(3)<<32;assert(cost.bind({nullptr,bad_history,nullptr,0,1,0})==Status::invalid);
    assert(cost.bind({nullptr,nullptr,nullptr,0,0,0})==Status::ok);
    s={};s.bits.count=9;allowed_flag=true;
    assert(cost.penalty(0,{},s,1,out)==Status::invalid && out==91);
    assert(cost.compatible(0,s,allowed_flag)==Status::invalid && allowed_flag);
    std::cout<<"COST_GLOBAL_CONFIG_PASS fields=954\nCOST_BOUNDARY_PASS\nCOST_ALL_PASS\n";
}
