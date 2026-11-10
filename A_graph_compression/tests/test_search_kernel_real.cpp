#include "../src/native/search_snapshot_inputs.hpp"
#include "../src/native/search_flat_controller_adapter.hpp"
#include "search_snapshot_provider.hpp"
#include "search_kernel_packet.hpp"
#include "host_contract.hpp"
extern "C" void search_kernel_csr(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
extern "C" void search_kernel_compact(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
#include <cassert>
#include <iostream>
// Oracle uses native adjacency; candidate calls the actual production top with
// static image decoder, packet ABI and flat workspace. Phase 1 adds deterministic
// node occupancy/history penalties. These are probes, not complete negotiation.
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
using Limits=fpga_search::SearchRegionLimits;
using Provider=fpga_search::SearchSnapshotProvider<Limits,RealSnapshotAdjacency,256,65536,1048576,1,1,65536>;
using Core=fpga_search::FlatSearchController<Limits>;
struct SnapshotQuery{uint32_t net,source;std::vector<uint32_t> sinks;};
int main(int argc,char** argv) {
    assert(argc==5);auto image=board_graph::words(argv[1],board_graph::image_words);auto config=board_graph::words(argv[4],32);board_graph::descriptor(image,config,config[0]);
    auto top=config[0]==0?search_kernel_csr:search_kernel_compact;
    RealSnapshotAdjacency graph(argv[1]);std::ifstream input(argv[2]);assert(input);
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
    auto& w=flat_controller_adapter::storage<Limits>().workspace;unsigned checked=0,found=0,site_paths=0,unknown=0;uint64_t expanded=0;
    for(unsigned phase=0;phase<2;++phase) {
    for(unsigned n=0;n<graph.node_count();++n){node_costs[2*n]=phase && n%97==0?2:0;node_costs[2*n+1]=phase?n%13:0;}
    view.present=phase?4:1;
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
            [&](uint32_t,const Edge& e,const site_native::Normalized&,const site_native::Normalized&){return uint64_t(1)+node_costs[2*e.dst]*view.present+node_costs[2*e.dst+1];});
        const auto request=search_kernel_host::packet<Limits>(view,target,1,200000,{});
        uint64_t meta[2]={w.epoch,w.key_count},result[81]{};
        top(image.data(),config.data(),unsigned(image.size()),&q.source,request.data(),unsigned(request.size()),w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result);
        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);assert(result[15]==1 && result[13]==meta[0] && result[14]==meta[1]);
        Core::Result actual;actual.status=fpga_search::SearchStatus(result[0]);actual.cost=result[1];actual.expanded=result[2];actual.blocked=result[3];
        actual.path_length=unsigned(result[7]);actual.unknown_node_count=unsigned(result[8]);actual.unknown_pip_count=unsigned(result[9]);
        if(actual.status==fpga_search::SearchStatus::found){Core::Key key{};assert(Core::Index::Storage::load(result+16,0,key) && key.node==target);actual.demands=key.state;}
        else for(unsigned i=16;i<81;++i)assert(result[i]==0);
        assert(expected.status==flat_controller_adapter::status_name(actual.status) && expected.cost==actual.cost && expected.expanded==actual.expanded && expected.blocked==actual.blocked && expected.path.size()==actual.path_length);
        auto d=flat_controller_adapter::unpack(actual.demands);assert(expected.demands.signals==d.signals && expected.demands.bits==d.bits && expected.demands.values==d.values);
        for(unsigned i=0;i<actual.path_length;++i){const auto& p=expected.path[i];const auto* words=w.path+uint64_t(i)*8;const fpga_search::LabelEdge e{words[1],words[2],words[3],words[4],words[5],words[6],words[7]};assert(p.first==words[0] && std::tie(p.second.dst,p.second.tile,p.second.pip,p.second.up,p.second.down,p.second.attr,p.second.dir)==std::tie(e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir));}
        std::set<uint32_t> unknown_nodes;std::set<std::pair<uint32_t,uint32_t>> unknown_pips;
        if(actual.unknown_node_count)for(uint32_t n=0;n<graph.node_count();++n)if(w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64)))unknown_nodes.insert(n);
        for(unsigned i=0;i<actual.unknown_pip_count;++i)unknown_pips.emplace(uint32_t(w.unknown_pips[i]>>32),uint32_t(w.unknown_pips[i]));
        assert(expected.unknown_sources==unknown_nodes && expected.unknown_pips==unknown_pips);
        ++checked;found+=actual.status==fpga_search::SearchStatus::found;site_paths+=!d.signals.empty() || !d.bits.empty() || !d.values.empty();unknown+=actual.unknown_node_count || actual.unknown_pip_count;expanded+=actual.expanded;
    }
    }
    assert(checked==32);std::cout<<"KERNEL_REAL_SEARCH_PASS queries="<<checked<<" found="<<found<<" site_paths="<<site_paths<<" with_unknown_evidence="<<unknown<<" expanded="<<expanded<<" attributes="<<sites.attributes<<'\n';
}
