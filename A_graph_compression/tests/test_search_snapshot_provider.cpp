#include "../src/native/site_search.hpp"
#include "../src/native/site_ledger.hpp"
#include "../src/native/search_controller_adapter.hpp"
#include "search_snapshot_provider.hpp"
#include <array>
#include <cassert>
#include <iostream>
#include <random>
struct SnapshotLimits {
    static constexpr unsigned nodes=16,degree=8,roots=16,unknown_pips=256,path=4096,expansions=1000;
    static constexpr unsigned signals=4,bits=4,values=4,slots=8192,labels=4096,heap=8192;
};
struct SnapshotAdjacency {
    unsigned nodes=12,counts[16]{};bool unknown[16]{};fpga_search::LabelEdge edges[16][8]{};
    unsigned node_count()const{return nodes;}
    fpga_search::RowStatus neighbors(unsigned node,fpga_search::LabelEdge* out,unsigned capacity,unsigned& count)const {
        if(node>=nodes)return fpga_search::RowStatus::invalid;
        if(unknown[node])return fpga_search::RowStatus::unknown;
        if(counts[node]>capacity)return fpga_search::RowStatus::capacity_exhausted;
        count=counts[node];for(unsigned i=0;i<8;++i){if(i>=count)break;out[i]=edges[node][i];}
        return fpga_search::RowStatus::known;
    }
    bool neighbors(unsigned node,std::vector<Edge>& out)const {
        out.clear();if(unknown[node])return false;
        for(unsigned i=0;i<counts[node];++i)out.push_back(controller_adapter::native_edge(edges[node][i]));
        return true;
    }
};
using Provider=fpga_search::SearchSnapshotProvider<SnapshotLimits,SnapshotAdjacency,256,4,256,256,64,2048>;
using Core=Provider::Core;
using Status=fpga_search::CostStatus;
using Row=std::array<uint64_t,4>;
site_native::Normalized state(std::mt19937_64& rng) {
    site_native::Normalized n;
    for(unsigned i=0;i<3;++i) {
        if(rng()%4==0)n.signals.insert(i);
        if(rng()%4==0)n.bits[i]={1,rng()%2};
        if(rng()%4==0)n.values[i]=rng()%2;
    }
    return n;
}
std::vector<uint64_t> flatten(std::vector<Row> rows) {
    std::sort(rows.begin(),rows.end());std::vector<uint64_t> out;
    for(const auto& r:rows)out.insert(out.end(),r.begin(),r.end());
    return out;
}
uint64_t resource(site_native::ResourceKey key){return (uint64_t(key.first)<<32)|key.second;}
bool same(const site_native::SearchResult& expected,const Core::Result& actual,const Core::Workspace& w,unsigned nodes) {
    if(expected.status!=controller_adapter::status_name(actual.status) || expected.cost!=actual.cost || expected.expanded!=actual.expanded || expected.blocked!=actual.blocked || expected.path.size()!=actual.path_length)return false;
    auto d=controller_adapter::unpack(actual.demands);
    if(expected.demands.signals!=d.signals || expected.demands.bits!=d.bits || expected.demands.values!=d.values)return false;
    for(unsigned i=0;i<actual.path_length;++i) {
        auto p=expected.path[i];const auto& e=w.path[i].edge;
        if(p.first!=w.path[i].source || std::tie(p.second.dst,p.second.tile,p.second.pip,p.second.up,p.second.down,p.second.attr,p.second.dir)!=std::tie(e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir))return false;
    }
    std::set<uint32_t> unknown;
    if(actual.unknown_node_count)for(unsigned n=0;n<nodes;++n)if(w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64)))unknown.insert(n);
    std::set<std::pair<uint32_t,uint32_t>> pips;
    for(unsigned i=0;i<actual.unknown_pip_count;++i)pips.emplace(w.unknown_pips[i].tile,w.unknown_pips[i].pip);
    return expected.unknown_sources==unknown && expected.unknown_pips==pips && unknown.size()==actual.unknown_node_count;
}
int main() {
    std::mt19937_64 rng(2026102402);std::map<std::string,unsigned> statuses;
    for(unsigned trial=0;trial<1000;++trial) {
        SnapshotAdjacency graph;std::map<std::pair<uint32_t,uint32_t>,site_native::Demands> requirements;
        uint64_t forbidden[1]{},node_costs[32]{};std::set<uint32_t> blocked_nodes;
        uint8_t pseudo[4]={0,1,0,0},blocked_attributes[4]={0,0,0,1};
        std::set<uint64_t> protected_set;unsigned pip=0;
        for(unsigned n=0;n<graph.nodes;++n) {
            node_costs[2*n]=rng()%5;node_costs[2*n+1]=rng()%8;
            graph.unknown[n]=rng()%13==0;graph.counts[n]=rng()%8;
            for(unsigned j=0;j<graph.counts[n];++j) {
                auto& e=graph.edges[n][j];e={unsigned(rng()%graph.nodes),unsigned(rng()%4),pip++,unsigned(rng()%5),unsigned(rng()%5),unsigned(rng()%4),unsigned(rng()%2)};
                if(e.attr==1 && rng()%3){e.dir=0;requirements[{e.tile,e.pip}]=site_native::payload(state(rng));}
                if(rng()%17==0)protected_set.insert((uint64_t(e.tile)<<32)|e.pip);
            }
        }
        if(trial%3==0){blocked_nodes.insert(11);forbidden[0]|=uint64_t(1)<<11;}
        std::vector<uint64_t> keys,protected_pips(protected_set.begin(),protected_set.end());std::vector<Core::State> states;
        for(const auto& p:requirements){keys.push_back((uint64_t(p.first.first)<<32)|p.first.second);Core::State s{};assert(controller_adapter::pack<SnapshotLimits>(site_native::normalize(p.second),s));states.push_back(s);}
        site_native::DemandLedger ledger;std::vector<Row> owner_rows,fixed_rows;site_native::SiteHistory history;
        for(unsigned owner=0;owner<4;++owner){auto n=state(rng);ledger.replace(owner,n);for(auto p:site_native::entries(n))owner_rows.push_back({resource(p.first),owner,p.second.first,p.second.second});}
        auto config=state(rng);config.signals.clear();std::vector<std::pair<uint32_t,uint32_t>> fixed_signals;
        if(trial%3==0){fixed_signals.emplace_back(0,1);fixed_rows.push_back({0,1,0,0});}
        for(auto p:site_native::entries(config))fixed_rows.push_back({resource(p.first),0,p.second.first,p.second.second});
        site_native::SiteState fixed(fixed_signals,site_native::payload(config));
        for(unsigned kind=0;kind<3;++kind)for(unsigned id=0;id<3;++id)if(rng()%2)history[{kind,id}]=rng()%8;
        std::vector<uint64_t> history_words;for(auto h:history){history_words.push_back(resource(h.first));history_words.push_back(h.second);}
        auto owners=flatten(owner_rows),fixed_words=flatten(fixed_rows);unsigned net=rng()%5;uint64_t present=1+rng()%8;
        Provider provider(graph);Provider::View view{graph.nodes,4,forbidden,node_costs,pseudo,blocked_attributes,protected_pips.data(),keys.data(),states.data(),unsigned(protected_pips.size()),unsigned(keys.size()),
            {owners.data(),history_words.data(),fixed_words.data(),unsigned(owner_rows.size()),unsigned(history.size()),unsigned(fixed_rows.size())},net,present};
        assert(provider.bind(view)==Status::ok);
        auto semantics=[&](unsigned,const Edge& e){site_native::EdgeSemantics s;s.pseudo=pseudo[e.attr];auto p=requirements.find({e.tile,e.pip});if(p!=requirements.end())s.demands=p->second;return s;};
        auto blocked=[&](unsigned,const Edge& e){return protected_set.count((uint64_t(e.tile)<<32)|e.pip) || blocked_attributes[e.attr];};
        auto compatible=[&](const site_native::Normalized& n){return !fixed.conflicts(net,site_native::payload(n));};
        auto step=[&](unsigned,const Edge& e,const site_native::Normalized& a,const site_native::Normalized& b){return 1+present*node_costs[2*e.dst]+node_costs[2*e.dst+1]+ledger.penalty(net,a,b,present,history);};
        unsigned target=trial%9==0?0:1+rng()%10;uint64_t budget=trial%5==0?1:trial%5==1?8:1000;
        std::set<uint32_t> roots={0};if(trial%7==0)roots.insert(1);
        auto expected=site_native::search(graph,roots,target,{true,false,{},{},{}},budget,blocked_nodes,semantics,blocked,compatible,step);
        std::vector<uint32_t> root_words(roots.begin(),roots.end());auto& w=controller_adapter::storage<SnapshotLimits>().workspace;
        auto actual=Core::run(provider,w,root_words.data(),unsigned(root_words.size()),target,{},budget);
        if(!same(expected,actual,w,graph.nodes)){std::cerr<<"SNAPSHOT_SEARCH_MISMATCH "<<trial<<' '<<expected.status<<' '<<controller_adapter::status_name(actual.status)<<'\n';return 1;}
        ++statuses[expected.status];
        // Verified PIP requirements must retain the native kind/direction checks.
        if(!keys.empty()) {
            fpga_search::LabelEdge e{0,unsigned(keys[0]>>32),unsigned(keys[0]),0,0,0,0};Core::State out{};
            assert(provider.semantics(0,e,out)==fpga_search::SemanticsStatus::invalid);
            e.attr=1;e.dir=1;assert(provider.semantics(0,e,out)==fpga_search::SemanticsStatus::invalid);
            e.dir=0;assert(provider.semantics(0,e,out)==fpga_search::SemanticsStatus::verified);
        }
        auto bad=view;bad.nodes=17;assert(provider.bind(bad)==Status::capacity_exhausted && provider.node_count()==0);
        bad=view;bad.attributes=5;assert(provider.bind(bad)==Status::capacity_exhausted);
        bad=view;bad.semantics_count=257;assert(provider.bind(bad)==Status::capacity_exhausted);
        bad=view;bad.protected_count=257;assert(provider.bind(bad)==Status::capacity_exhausted);
        bad=view;bad.present=0;assert(provider.bind(bad)==Status::invalid);
        bad=view;bad.nodes=11;assert(provider.bind(bad)==Status::invalid);
    }
    std::cout<<"SNAPSHOT_SEARCH_PASS cases=1000";for(const auto& p:statuses)std::cout<<' '<<p.first<<'='<<p.second;
    std::cout<<"\nSNAPSHOT_PROVIDER_BOUNDS_PASS\nSNAPSHOT_PROVIDER_ALL_PASS\n";
}
