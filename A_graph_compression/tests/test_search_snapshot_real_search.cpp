#include "../src/native/search_snapshot_inputs.hpp"
#include "../src/native/search_controller_adapter.hpp"
#include "search_snapshot_provider.hpp"
#include <cassert>
#include <iostream>
// Native graph only supplies adjacency; semantic/compatibility/cost operations
// are performed directly by SearchSnapshotProvider, without native callbacks.
struct RealSnapshotAdjacency {
    Graph graph;std::vector<Edge> temporary;
    explicit RealSnapshotAdjacency(const std::string& path):graph(path,4096){}
    size_t node_count()const{return graph.node_count();}
    bool neighbors(uint32_t n,std::vector<Edge>& out) {
        if(!graph.neighbors(n,out))return false;
        std::stable_sort(out.begin(),out.end(),[](const Edge& a,const Edge& b){
            return std::make_tuple(a.dst,a.tile,a.pip,a.dir,a.dir?a.down:a.up,a.dir?a.up:a.down)<std::make_tuple(b.dst,b.tile,b.pip,b.dir,b.dir?b.down:b.up,b.dir?b.up:b.down);
        });return true;
    }
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* out,unsigned capacity,unsigned& count) {
        if(!neighbors(n,temporary))return fpga_search::RowStatus::unknown;
        if(temporary.size()>capacity)return fpga_search::RowStatus::capacity_exhausted;
        count=temporary.size();
        for(unsigned i=0;i<count;++i){const auto& e=temporary[i];out[i]={e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
        return fpga_search::RowStatus::known;
    }
};
using Limits=controller_adapter::RegionLimits;
using Provider=fpga_search::SearchSnapshotProvider<Limits,RealSnapshotAdjacency,256,65536,1048576,1,1,65536>;
using Core=Provider::Core;
struct SnapshotQuery{uint32_t net,source;std::vector<uint32_t> sinks;};
int main(int argc,char** argv) {
    assert(argc==4);RealSnapshotAdjacency graph(argv[1]);std::ifstream input(argv[2]);assert(input);
    auto integer=[&](){uint64_t value=0;input>>value;assert(input && value<=UINT32_MAX);return uint32_t(value);};
    std::string magic;input>>magic;assert(magic=="NATIVE_ROUTING_V1" && integer()==graph.node_count());
    std::set<uint32_t> protected_nodes,blocked_attributes;std::set<std::pair<uint32_t,uint32_t>> protected_pips;
    auto count=integer();for(unsigned i=0;i<count;++i)protected_nodes.insert(integer());
    count=integer();for(unsigned i=0;i<count;++i){auto tile=integer(),pip=integer();protected_pips.emplace(tile,pip);}
    count=integer();for(unsigned i=0;i<count;++i)blocked_attributes.insert(integer());
    count=integer();std::vector<SnapshotQuery> queries;std::map<uint32_t,uint32_t> reserved;
    for(unsigned i=0;i<count;++i){SnapshotQuery q{integer(),integer(),{}};auto sinks=integer();for(unsigned j=0;j<sinks;++j)q.sinks.push_back(integer());reserved[q.source]=q.net;for(auto s:q.sinks)reserved[s]=q.net;queries.push_back(q);}
    std::string trailing;assert(!(input>>trailing) && queries.size()==1062);
    site_native::SiteInputs sites(argv[3]);site_native::SiteState fixed(sites.fixed_signals,sites.fixed);
    snapshot_inputs::SiteBuffers<Limits> site_buffers(sites,protected_pips,blocked_attributes);
    std::vector<uint64_t> forbidden((graph.node_count()+63)/64),node_costs(2*graph.node_count());
    // An explicitly empty dynamic occupancy/history snapshot. These are
    // independent source-to-sink probes, not sequential negotiated routing.
    Provider provider(graph);Provider::View view{unsigned(graph.node_count()),sites.attributes,forbidden.data(),node_costs.data(),site_buffers.pseudo_attributes.data(),site_buffers.blocked_attributes.data(),site_buffers.protected_pips.data(),site_buffers.semantics_keys.data(),site_buffers.requirements.data(),unsigned(site_buffers.protected_pips.size()),unsigned(site_buffers.semantics_keys.size()),{nullptr,nullptr,site_buffers.fixed.data(),0,0,unsigned(site_buffers.fixed.size()/4)},0,1};
    auto& w=controller_adapter::storage<Limits>().workspace;unsigned checked=0,found=0,site_paths=0,unknown=0;uint64_t expanded=0;
    for(unsigned qi=0;qi<queries.size();qi+=67) {
        const auto& q=queries[qi];assert(!q.sinks.empty());std::set<uint32_t> blocked_nodes=protected_nodes;
        for(auto r:reserved)if(r.second!=q.net)blocked_nodes.insert(r.first);
        std::fill(forbidden.begin(),forbidden.end(),0);for(auto n:blocked_nodes){assert(n<graph.node_count());forbidden[n/64]|=uint64_t(1)<<(n%64);}
        view.net=q.net;assert(provider.bind(view)==fpga_search::CostStatus::ok);
        const unsigned target=q.sinks.front();auto initial=site_native::Demands{true,false,{},{},{}};
        auto expected=site_native::search(graph,{q.source},target,initial,200000,blocked_nodes,
            [&](uint32_t,const Edge& e){return sites.semantics(e);},
            [&](uint32_t,const Edge& e){return protected_pips.count({e.tile,e.pip}) || blocked_attributes.count(e.attr);},
            [&](const site_native::Normalized& n){return !fixed.conflicts(q.net,site_native::payload(n));},
            [](uint32_t,const Edge&,const site_native::Normalized&,const site_native::Normalized&){return uint64_t(1);});
        auto actual=Core::run(provider,w,&q.source,1,target,{},200000);
        assert(expected.status==controller_adapter::status_name(actual.status) && expected.cost==actual.cost && expected.expanded==actual.expanded && expected.blocked==actual.blocked && expected.path.size()==actual.path_length);
        auto d=controller_adapter::unpack(actual.demands);assert(expected.demands.signals==d.signals && expected.demands.bits==d.bits && expected.demands.values==d.values);
        for(unsigned i=0;i<actual.path_length;++i){const auto& p=expected.path[i];const auto& e=w.path[i].edge;assert(p.first==w.path[i].source && std::tie(p.second.dst,p.second.tile,p.second.pip,p.second.up,p.second.down,p.second.attr,p.second.dir)==std::tie(e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir));}
        std::set<uint32_t> unknown_nodes;std::set<std::pair<uint32_t,uint32_t>> unknown_pips;
        if(actual.unknown_node_count)for(uint32_t n=0;n<graph.node_count();++n)if(w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64)))unknown_nodes.insert(n);
        for(unsigned i=0;i<actual.unknown_pip_count;++i)unknown_pips.emplace(w.unknown_pips[i].tile,w.unknown_pips[i].pip);
        assert(expected.unknown_sources==unknown_nodes && expected.unknown_pips==unknown_pips);
        ++checked;found+=actual.status==fpga_search::SearchStatus::found;site_paths+=!d.signals.empty() || !d.bits.empty() || !d.values.empty();unknown+=actual.unknown_node_count || actual.unknown_pip_count;expanded+=actual.expanded;
    }
    assert(checked==16);std::cout<<"SNAPSHOT_REAL_SEARCH_PASS queries="<<checked<<" found="<<found<<" site_paths="<<site_paths<<" with_unknown_evidence="<<unknown<<" expanded="<<expanded<<" attributes="<<sites.attributes<<'\n';
}
