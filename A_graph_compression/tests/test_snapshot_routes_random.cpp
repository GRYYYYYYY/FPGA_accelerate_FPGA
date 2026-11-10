#include "../src/native/site_routes.hpp"
#include "snapshot_test_routes.hpp"
#include <cassert>
#include <iostream>
#include <random>
struct RandomRouteLimits:snapshot_route::RegionLimits {
    static constexpr unsigned nodes=32,degree=16,roots=32,unknown_pips=512,path=8192,expansions=1000;
    static constexpr unsigned signals=4,bits=4,values=4,labels=8192,slots=16384,heap=16384;
    static constexpr unsigned semantics=512,attributes=4,protected_pips=512,config_owners=256,config_history=128,fixed_records=128;
};
struct RandomRouteGraph {
    std::vector<std::vector<Edge>> rows=std::vector<std::vector<Edge>>(24);std::set<unsigned> unknown;
    size_t node_count()const{return rows.size();}
    bool neighbors(unsigned n,std::vector<Edge>& out){if(unknown.count(n))return false;out=rows[n];return true;}
};
bool equal_state(const site_native::Normalized& a,const site_native::Normalized& b){return a.signals==b.signals && a.bits==b.bits && a.values==b.values;}
bool equal_edges(const std::vector<std::pair<uint32_t,Edge>>& a,const std::vector<std::pair<uint32_t,Edge>>& b) {
    if(a.size()!=b.size())return false;
    for(size_t i=0;i<a.size();++i){const auto& e=a[i].second;const auto& f=b[i].second;if(a[i].first!=b[i].first || std::tie(e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir)!=std::tie(f.dst,f.tile,f.pip,f.up,f.down,f.attr,f.dir))return false;}
    return true;
}
bool equal_search(const site_native::SearchResult& a,const site_native::SearchResult& b) {
    return a.status==b.status && a.cost==b.cost && a.expanded==b.expanded && a.blocked==b.blocked && a.unknown_sources==b.unknown_sources && a.unknown_pips==b.unknown_pips && equal_state(a.demands,b.demands) && equal_edges(a.path,b.path);
}
template<class A,class B> bool equal_batch(const A& a,const B& b) {
    if(a.status!=b.status || a.routes.size()!=b.routes.size() || a.iterations.size()!=b.iterations.size() || a.site_demands.size()!=b.site_demands.size())return false;
    for(const auto& r:a.routes){auto p=b.routes.find(r.first);if(p==b.routes.end())return false;const auto& x=r.second;const auto& y=p->second;if(x.source!=y.source || x.sinks!=y.sinks || x.nodes!=y.nodes || x.complete!=y.complete || !equal_edges(x.edges,y.edges))return false;}
    for(const auto& d:a.site_demands){auto p=b.site_demands.find(d.first);if(p==b.site_demands.end() || !equal_state(d.second,p->second))return false;}
    for(size_t i=0;i<a.iterations.size();++i) {
        const auto& x=a.iterations[i];const auto& y=b.iterations[i];
        if(x.conflicts!=y.conflicts || x.site_conflicts!=y.site_conflicts || x.incomplete!=y.incomplete || x.outcomes.size()!=y.outcomes.size())return false;
        for(size_t j=0;j<x.outcomes.size();++j){if(x.outcomes[j].size()!=y.outcomes[j].size())return false;for(size_t k=0;k<x.outcomes[j].size();++k)if(!equal_search(x.outcomes[j][k],y.outcomes[j][k]))return false;}
    }
    return true;
}
int main(int argc,char** argv) {
    assert(argc==2);site_native::SiteInputs sites(argv[1]);std::mt19937_64 rng(2026102403);
    uint64_t snapshots=0,searches=0,node_history=0,site_history=0,site_paths=0,rounds=0;std::map<std::string,unsigned> statuses;
    for(unsigned trial=0;trial<200;++trial) {
        RandomRouteGraph graph;sites.requirements.clear();sites.fixed={true,false,{},{},{}};sites.fixed_signals.clear();
        if(trial%5==0)sites.fixed.bits.emplace_back(0,1,0);
        if(trial%7==0)sites.fixed_signals.emplace_back(2,0);
        std::set<std::pair<uint32_t,uint32_t>> protected_pips;std::set<uint32_t> blocked_attributes,protected_nodes;
        if(trial%11==0)blocked_attributes.insert(3);
        if(trial%13==0)protected_nodes.insert(23);
        unsigned pip=0;
        auto add=[&](unsigned a,unsigned b,bool base){
            unsigned id=pip++,attr=base?0:unsigned(rng()%4),tile=rng()%4,dir=rng()%2;
            if(base && trial%2==0 && a<3)attr=1;
            if(attr==1 && (base || rng()%3)) {
                dir=0;site_native::Demands d{true,false,{},{},{}};
                if(base)d.signals.push_back(0);
                else {
                    if(rng()%2)d.signals.push_back(rng()%3);
                    if(rng()%2)d.bits.emplace_back(rng()%3,1,rng()%2);
                    if(rng()%2)d.values.emplace_back(rng()%3,rng()%2);
                }
                sites.requirements[{tile,id}]=d;
            }
            graph.rows[a].push_back({b,tile,id,unsigned(rng()%8),unsigned(rng()%8),attr,dir});
            if(!base && rng()%17==0)protected_pips.emplace(tile,id);
        };
        std::vector<netlist_native::NetQuery> queries;
        for(unsigned n=0;n<3;++n) {
            add(n,9,true);add(9,n+3,true);add(n,10+n,true);add(10+n,13+n,true);add(13+n,n+3,true);
            queries.push_back({n,n,{n+3}});
            if(trial%3==0){queries.back().sinks.push_back(n+6);add(13+n,n+6,true);add(9,n+6,true);}
        }
        if(trial%4==0)std::reverse(queries.begin(),queries.end());
        for(unsigned n=0;n<24;++n) {
            unsigned degree=rng()%4;
            for(unsigned j=0;j<degree;++j)add(n,rng()%24,false);
            if(n>=9 && rng()%31==0)graph.unknown.insert(n);
        }
        site_native::SiteState fixed(sites.fixed_signals,sites.fixed);snapshot_inputs::SiteBuffers<RandomRouteLimits> metadata(sites,protected_pips,blocked_attributes);
        uint64_t budget=trial%7==0?2:trial%7==1?20:1000;unsigned iterations=trial%9==0?1:8;
        auto expected=site_native::route_batch(graph,queries,protected_nodes,fixed,
            [&](unsigned,const Edge& e){return sites.semantics(e);},
            [&](unsigned,unsigned,const Edge& e){return protected_pips.count({e.tile,e.pip}) || blocked_attributes.count(e.attr);},iterations,budget,8);
        snapshot_route::counters={};controller_adapter::counters={};
        auto actual=snapshot_test_native::route_snapshot_batch<RandomRouteLimits>(graph,queries,protected_nodes,metadata,iterations,budget,8);
        if(!equal_batch(expected,actual)){std::cerr<<"SNAPSHOT_ROUTE_MISMATCH trial="<<trial<<'\n';return 1;}
        const auto c=snapshot_route::counters;const auto cc=controller_adapter::counters;
        assert(c.failures==0 && cc.capacity_failures==0 && cc.invalid==0 && c.snapshots==3*expected.iterations.size());
        uint64_t expected_searches=0;for(const auto& it:expected.iterations)for(const auto& conn:it.outcomes)expected_searches+=conn.size();assert(cc.searches==expected_searches);
        snapshots+=c.snapshots;searches+=cc.searches;node_history+=c.node_history;site_history+=c.site_history;site_paths+=c.site_found_paths;rounds+=actual.iterations.size();++statuses[actual.status];
    }
    assert(node_history && site_history && site_paths);
    std::cout<<"SNAPSHOT_ROUTE_RANDOM_PASS cases=200 snapshots="<<snapshots<<" searches="<<searches<<" rounds="<<rounds<<" node_history_snapshots="<<node_history<<" site_history_snapshots="<<site_history<<" site_paths="<<site_paths;
    for(auto p:statuses)std::cout<<' '<<p.first<<'='<<p.second;
    std::cout<<"\nSNAPSHOT_ROUTE_FULL_RESULTS_PASS\n";
}
