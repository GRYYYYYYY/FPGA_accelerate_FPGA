#include "../src/native/site_search.hpp"
#include "../src/native/search_controller_adapter.hpp"
#include <cassert>
#include <iostream>
#include <random>
struct Limits {
    static constexpr unsigned nodes=32,degree=64,roots=32,unknown_pips=512,path=4096,expansions=1000;
    static constexpr unsigned signals=8,bits=8,values=8,slots=8192,labels=4096,heap=8192;
};
struct ControllerFixture {
    std::vector<std::vector<Edge>> rows;std::set<uint32_t> unknown;
    size_t node_count() const {return rows.size();}
    bool neighbors(uint32_t n,std::vector<Edge>& out) {if (unknown.count(n)) return false;out=rows[n];return true;}
};
bool equal(const site_native::SearchResult& a,const site_native::SearchResult& b) {
    if (a.status!=b.status || a.cost!=b.cost || a.expanded!=b.expanded || a.blocked!=b.blocked ||
        a.demands.signals!=b.demands.signals || a.demands.bits!=b.demands.bits || a.demands.values!=b.demands.values ||
        a.unknown_sources!=b.unknown_sources || a.unknown_pips!=b.unknown_pips || a.path.size()!=b.path.size()) return false;
    for (size_t i=0;i<a.path.size();++i) {
        auto x=a.path[i],y=b.path[i];auto e=x.second,f=y.second;
        if (x.first!=y.first || std::tie(e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir)!=std::tie(f.dst,f.tile,f.pip,f.up,f.down,f.attr,f.dir)) return false;
    }
    return true;
}
int main() {
    std::mt19937_64 rng(20261024);unsigned checked=0;std::map<std::string,unsigned> statuses;
    for (unsigned trial=0;trial<1000;++trial) {
        ControllerFixture g;g.rows.resize(4+rng()%17);std::map<unsigned,site_native::Demands> demands;std::set<unsigned> pseudo;
        std::map<unsigned,uint64_t> costs;unsigned pip=0;
        for (unsigned n=0;n<g.node_count();++n) {
            if (rng()%13==0) g.unknown.insert(n);
            unsigned edges=unsigned(rng()%7);
            for (unsigned j=0;j<edges;++j) {
                unsigned dst=unsigned(rng()%g.node_count()),id=pip++;
                g.rows[n].push_back({dst,unsigned(rng()%4),id,unsigned(rng()%8),unsigned(rng()%8),unsigned(rng()%3),unsigned(rng()%2)});
                costs[id]=1+rng()%20;
                if (rng()%5==0) {
                    pseudo.insert(id);
                    if (rng()%3) {
                        site_native::Demands d{true,false,{},{},{}};
                        // Two fields permit path alternatives and merge conflicts.
                        d.bits.emplace_back(rng()%2,1,rng()%2);d.signals.push_back(rng()%2);demands[id]=d;
                    }
                }
            }
        }
        std::set<uint32_t> roots={0};if (trial%7==0) roots.insert(1);
        std::set<uint32_t> forbidden;if (trial%11==0) forbidden.insert(unsigned(g.node_count()-1));
        unsigned target=trial%9==0?0:unsigned(rng()%(g.node_count()-1));
        uint64_t budget=trial%5==0?1:trial%5==1?3:1000;
        auto sem=[&](unsigned,const Edge& e) {site_native::EdgeSemantics s;s.pseudo=pseudo.count(e.pip);auto it=demands.find(e.pip);if(it!=demands.end())s.demands=it->second;return s;};
        auto block=[&](unsigned,const Edge& e) {return trial%17==0 && e.attr==2;};
        auto compat=[&](const site_native::Normalized& n) {return trial%19!=0 || !n.signals.count(1);};
        auto cost=[&](unsigned,const Edge& e,const site_native::Normalized&,const site_native::Normalized&) {return costs.at(e.pip);};
        site_native::Demands initial{true,false,{},{},{}};
        auto a=site_native::search(g,roots,target,initial,budget,forbidden,sem,block,compat,cost);
        auto b=controller_adapter::search<Limits>(g,roots,target,initial,budget,forbidden,sem,block,compat,cost);
        if (!equal(a,b)) {std::cerr<<"CONTROLLER_MISMATCH trial="<<trial<<" expected="<<a.status<<" actual="<<b.status<<" expanded="<<a.expanded<<'/'<<b.expanded<<'\n';return 1;}
        ++checked;++statuses[b.status];
    }
    std::cout<<"CONTROLLER_RANDOM_PASS cases="<<checked;
    for (const auto& s:statuses) std::cout<<' '<<s.first<<'='<<s.second;
    std::cout<<'\n';
    // New searches reuse old storage; an unknown result must not leak into a
    // subsequent zero-edge found result. Also force an epoch rollover.
    auto& w=controller_adapter::storage<Limits>().workspace;w.epoch=UINT32_MAX;
    ControllerFixture g;g.rows.resize(2);site_native::Demands initial{true,false,{},{},{}};
    auto sem=[](unsigned,const Edge&){return site_native::EdgeSemantics{};};
    auto block=[](unsigned,const Edge&){return false;};auto compat=[](const site_native::Normalized&){return true;};
    auto cost=[](unsigned,const Edge&,const site_native::Normalized&,const site_native::Normalized&){return 1;};
    auto r=controller_adapter::search<Limits>(g,{0},0,initial,1,{},sem,block,compat,cost);
    assert(r.status=="found" && r.path.empty() && r.unknown_sources.empty() && r.unknown_pips.empty() && w.epoch==1);
    std::cout<<"CONTROLLER_RESET_PASS\nCONTROLLER_ALL_PASS\n";
}
