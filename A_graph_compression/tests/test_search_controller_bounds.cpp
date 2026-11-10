#include "../src/native/site_search.hpp"
#include "../src/native/search_controller_adapter.hpp"
#include <cassert>
#include <iostream>
struct BoundsLimits {
    static constexpr unsigned nodes=16,degree=8,roots=16,unknown_pips=16,path=64,expansions=100;
    static constexpr unsigned signals=8,bits=8,values=8,slots=128,labels=64,heap=128;
};
struct BoundsFixture {
    std::vector<std::vector<Edge>> rows=std::vector<std::vector<Edge>>(4);
    std::set<unsigned> unknown,pseudo;
    std::map<unsigned,site_native::Demands> demands;
    std::map<unsigned,uint64_t> costs;
    size_t node_count() const {return rows.size();}
    bool neighbors(unsigned n,std::vector<Edge>& out) {if(unknown.count(n))return false;out=rows[n];return true;}
    void edge(unsigned a,unsigned b,unsigned pip){rows[a].push_back({b,0,pip,1,2,3,0});}
};
template<class L=BoundsLimits> site_native::SearchResult run(BoundsFixture& g,unsigned target=3,uint64_t budget=100,std::set<uint32_t> roots={0}) {
    auto sem=[&](unsigned,const Edge& e){site_native::EdgeSemantics s;s.pseudo=g.pseudo.count(e.pip);auto p=g.demands.find(e.pip);if(p!=g.demands.end())s.demands=p->second;return s;};
    auto block=[](unsigned,const Edge&){return false;};auto compat=[](const site_native::Normalized&){return true;};
    auto cost=[&](unsigned,const Edge& e,const site_native::Normalized&,const site_native::Normalized&){auto p=g.costs.find(e.pip);return p==g.costs.end()?uint64_t(1):p->second;};
    return controller_adapter::search<L>(g,roots,target,{true,false,{},{},{}},budget,{},sem,block,compat,cost);
}
struct HeapOne:BoundsLimits{static constexpr unsigned heap=1;};
struct LabelOne:BoundsLimits{static constexpr unsigned labels=1;};
struct SlotOne:BoundsLimits{static constexpr unsigned slots=1;};
struct DegreeOne:BoundsLimits{static constexpr unsigned degree=1;};
struct PathOne:BoundsLimits{static constexpr unsigned path=1;};
struct RootOne:BoundsLimits{static constexpr unsigned roots=1;};
struct PipOne:BoundsLimits{static constexpr unsigned unknown_pips=1;};
struct StateOne:BoundsLimits{static constexpr unsigned signals=1;};
struct BudgetOne:BoundsLimits{static constexpr unsigned expansions=1;};
struct NodeOne:BoundsLimits{static constexpr unsigned nodes=1;};
void capacity(const site_native::SearchResult& r){assert(r.status=="capacity_exhausted" && r.path.empty() && r.cost==0);}
int main() {
    BoundsFixture fan;fan.edge(0,1,0);fan.edge(0,2,1);
    capacity(run<HeapOne>(fan));capacity(run<LabelOne>(fan));capacity(run<SlotOne>(fan));capacity(run<DegreeOne>(fan));
    capacity(run<RootOne>(fan,3,100,{0,1}));capacity(run<BudgetOne>(fan,3,2));capacity(run<NodeOne>(fan));
    BoundsFixture chain;chain.edge(0,1,0);chain.edge(1,3,1);capacity(run<PathOne>(chain));
    chain.pseudo={0,1};chain.demands[0]={true,false,{0},{},{}};chain.demands[1]={true,false,{1},{},{}};capacity(run<StateOne>(chain));
    BoundsFixture unknown;unknown.edge(0,1,0);unknown.edge(0,2,1);unknown.pseudo={0,1};capacity(run<PipOne>(unknown));
    // Repeated identity must not consume another slot even when full.
    unknown.rows[0][1].pip=0;auto r=run<PipOne>(unknown);assert(r.status=="unknown_site_semantics" && r.unknown_pips.size()==1);
    // PIP evidence has priority over incomplete neighbor evidence.
    BoundsFixture mixed;mixed.edge(0,1,0);mixed.edge(0,2,1);mixed.pseudo={1};mixed.unknown={1};
    r=run(mixed);assert(r.status=="unknown_site_semantics" && r.unknown_sources==std::set<uint32_t>{1} && r.unknown_pips.size()==1);
    r=run(mixed,3,1);assert(r.status=="budget_exhausted" && r.unknown_sources.empty() && r.unknown_pips.size()==1);
    // Target is checked before the exhausted expansion budget.
    BoundsFixture direct;direct.edge(0,3,0);r=run(direct,3,1);assert(r.status=="found" && r.expanded==1 && r.cost==1);
    // Equal-cost parallel edges retain the first physical edge.
    direct.edge(0,3,1);r=run(direct);assert(r.path.size()==1 && r.path[0].second.pip==0);
    // Stale unknown-node entries must not be expanded twice.
    BoundsFixture stale;stale.edge(0,1,0);stale.edge(0,2,1);stale.edge(2,1,2);stale.costs[0]=10;stale.unknown={1};
    r=run(stale);assert(r.status=="incomplete_domain" && r.expanded==2 && r.unknown_sources==std::set<uint32_t>{1});
    for (uint64_t value:{uint64_t(0),UINT64_MAX}) {
        direct.costs[0]=value;bool rejected=false;try{run(direct);}catch(const std::invalid_argument&){rejected=true;}assert(rejected);
    }
    BoundsFixture overflow;overflow.edge(0,1,0);overflow.edge(1,3,1);overflow.costs[0]=UINT64_MAX-1;
    bool rejected=false;try{run(overflow);}catch(const std::invalid_argument&){rejected=true;}assert(rejected);
    // Raw controller preflight rejects noncanonical caller buffers.
    using Core=fpga_search::SearchController<BoundsLimits>;Core::State initial{};
    auto sem=[](unsigned,const Edge&){return site_native::EdgeSemantics{};};auto block=[](unsigned,const Edge&){return false;};
    auto compat=[](const site_native::Normalized&){return true;};auto cost=[](unsigned,const Edge&,const site_native::Normalized&,const site_native::Normalized&){return 1;};
    std::set<uint32_t> forbidden;
    controller_adapter::Bridge<BoundsLimits,BoundsFixture,decltype(sem),decltype(block),decltype(compat),decltype(cost)> p{fan,forbidden,sem,block,compat,cost,{}};
    auto& w=controller_adapter::storage<BoundsLimits>().workspace;uint32_t roots[2]={1,0};
    assert(Core::run(p,w,roots,2,3,initial,100).status==fpga_search::SearchStatus::invalid_input);
    roots[0]=0;assert(Core::run(p,w,roots,2,3,initial,100).status==fpga_search::SearchStatus::invalid_input);
    initial.signals.count=9;assert(Core::run(p,w,roots,1,3,initial,100).status==fpga_search::SearchStatus::invalid_input);
    std::cout<<"CONTROLLER_CAPACITY_PASS cases=10\nCONTROLLER_SEMANTIC_BOUNDARY_PASS\nCONTROLLER_PREFLIGHT_PASS\nCONTROLLER_BOUNDS_ALL_PASS\n";
}
