#pragma once
// CPU integration of the static provider. Snapshot construction, native
// adjacency, negotiation, occupancy updates and result retention remain host work.
#include "site_search.hpp"
#include "site_ledger.hpp"
#include "search_controller_adapter.hpp"
#include "search_snapshot_inputs.hpp"
#include "search_snapshot_provider.hpp"

namespace snapshot_route {
struct RegionLimits:controller_adapter::RegionLimits {
    static constexpr unsigned semantics=256,attributes=65536,protected_pips=1048576;
    static constexpr unsigned config_owners=65536,config_history=65536,fixed_records=65536;
};
struct Counters {
    uint64_t snapshots=0,node_occupied=0,node_history=0,site_occupied=0,site_history=0,site_found_paths=0,failures=0;
    unsigned max_site_owners=0,max_site_history=0;
};
inline thread_local Counters counters;
template<class Graph> struct Adjacency {
    Graph& graph;std::vector<Edge> row;
    size_t node_count()const{return graph.node_count();}
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* out,unsigned capacity,unsigned& count) {
        if(!graph.neighbors(n,row))return fpga_search::RowStatus::unknown;
        if(row.size()>capacity)return fpga_search::RowStatus::capacity_exhausted;
        count=unsigned(row.size());
        for(unsigned i=0;i<count;++i){const auto& e=row[i];out[i]={e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
        return fpga_search::RowStatus::known;
    }
};
template<class Limits,class Graph> class Context {
    using Provider=fpga_search::SearchSnapshotProvider<Limits,Adjacency<Graph>,Limits::semantics,Limits::attributes,Limits::protected_pips,Limits::config_owners,Limits::config_history,Limits::fixed_records>;
    using Core=typename Provider::Core;
    Adjacency<Graph> adjacency_;
    const snapshot_inputs::SiteBuffers<Limits>& sites_;
    Provider provider_;
    std::vector<uint64_t> forbidden_,nodes_,owners_,history_;
    [[noreturn]] static void fail(bool capacity,const char* message) {
        ++counters.failures;
        if(capacity)throw std::length_error(message);
        throw std::invalid_argument(message);
    }
public:
    Context(Graph& graph,const snapshot_inputs::SiteBuffers<Limits>& sites):adjacency_{graph,{}},sites_(sites),provider_(adjacency_) {
        if(graph.node_count()>Limits::nodes)fail(true,"snapshot node domain exceeds capacity");
        forbidden_.resize((graph.node_count()+63)/64);nodes_.resize(2*graph.node_count());
    }
    // Called after releasing the old route. by_net may still contain this net's
    // old demands; explicitly exclude it. Other nets retain current demands.
    void bind(uint32_t net,uint64_t present,const std::vector<std::set<uint32_t>>& node_owners,
              const std::map<uint32_t,uint64_t>& node_history,
              const std::map<uint32_t,site_native::Normalized>& by_net,
              const site_native::SiteHistory& site_history,const std::set<uint32_t>& forbidden) {
        ++counters.snapshots;const size_t count=adjacency_.node_count();
        if(node_owners.size()!=count)fail(false,"snapshot node ownership domain differs");
        std::fill(forbidden_.begin(),forbidden_.end(),0);std::fill(nodes_.begin(),nodes_.end(),0);
        for(auto n:forbidden){if(n>=count)fail(false,"snapshot forbidden node outside domain");forbidden_[n/64]|=uint64_t(1)<<(n%64);}
        bool occupied=false;
        for(size_t n=0;n<count;++n){nodes_[2*n]=node_owners[n].size()-node_owners[n].count(net);occupied=occupied || nodes_[2*n]!=0;}
        for(auto h:node_history){if(h.first>=count)fail(false,"snapshot history node outside domain");nodes_[2*h.first+1]=h.second;}
        using Row=std::array<uint64_t,4>;std::vector<Row> rows;
        for(const auto& owner:by_net) {
            if(owner.first==net)continue;
            for(const auto& e:site_native::entries(owner.second)) {
                if(rows.size()==Limits::config_owners)fail(true,"snapshot site ownership capacity exceeded");
                rows.push_back({(uint64_t(e.first.first)<<32)|e.first.second,owner.first,e.second.first,e.second.second});
            }
        }
        std::sort(rows.begin(),rows.end());owners_.clear();
        for(const auto& row:rows)owners_.insert(owners_.end(),row.begin(),row.end());
        if(site_history.size()>Limits::config_history)fail(true,"snapshot site history capacity exceeded");
        history_.clear();
        for(auto h:site_history){history_.push_back((uint64_t(h.first.first)<<32)|h.first.second);history_.push_back(h.second);}
        if(sites_.pseudo_attributes.size()>Limits::attributes || sites_.semantics_keys.size()>Limits::semantics || sites_.protected_pips.size()>Limits::protected_pips || sites_.fixed.size()/4>Limits::fixed_records)fail(true,"snapshot fixed metadata capacity exceeded");
        typename Provider::View view{unsigned(count),unsigned(sites_.pseudo_attributes.size()),forbidden_.data(),nodes_.data(),sites_.pseudo_attributes.data(),sites_.blocked_attributes.data(),sites_.protected_pips.data(),sites_.semantics_keys.data(),sites_.requirements.data(),unsigned(sites_.protected_pips.size()),unsigned(sites_.semantics_keys.size()),
            {owners_.data(),history_.data(),sites_.fixed.data(),unsigned(rows.size()),unsigned(site_history.size()),unsigned(sites_.fixed.size()/4)},net,present};
        const auto status=provider_.bind(view);
        if(status!=fpga_search::CostStatus::ok)fail(status==fpga_search::CostStatus::capacity_exhausted,"snapshot bind failed");
        counters.node_occupied+=occupied;counters.node_history+=!node_history.empty();counters.site_occupied+=!rows.empty();counters.site_history+=!site_history.empty();
        counters.max_site_owners=std::max(counters.max_site_owners,unsigned(rows.size()));counters.max_site_history=std::max(counters.max_site_history,unsigned(site_history.size()));
    }
    site_native::SearchResult search(const std::set<uint32_t>& roots,uint32_t target,const site_native::Normalized& initial,uint64_t budget) {
        auto& c=controller_adapter::counters;++c.searches;
        site_native::SearchResult out;typename Core::State state{};
        if(roots.size()>Limits::roots || !controller_adapter::pack<Limits>(initial,state)){++c.capacity_failures;out.status="capacity_exhausted";return out;}
        std::vector<uint32_t> sorted_roots(roots.begin(),roots.end());auto& w=controller_adapter::storage<Limits>().workspace;
        auto r=Core::run(provider_,w,sorted_roots.data(),unsigned(sorted_roots.size()),target,state,budget);
        c.pushes+=r.pushes;c.pops+=r.pops;c.improvements+=r.improvements;c.max_heap=std::max(c.max_heap,r.max_heap);c.max_labels=std::max(c.max_labels,r.label_count);c.max_probes=std::max(c.max_probes,r.max_probes);
        if(r.status==fpga_search::SearchStatus::invalid_input){++c.invalid;fail(false,"invalid snapshot search input/state");}
        if(r.status==fpga_search::SearchStatus::capacity_exhausted)++c.capacity_failures;
        out.status=controller_adapter::status_name(r.status);out.cost=r.cost;out.expanded=r.expanded;out.blocked=r.blocked;
        if(r.status==fpga_search::SearchStatus::found){++c.found;out.demands=controller_adapter::unpack(r.demands);counters.site_found_paths+=(r.demands.signals.count || r.demands.bits.count || r.demands.values.count);}
        for(unsigned i=0;i<r.path_length;++i)out.path.emplace_back(w.path[i].source,controller_adapter::native_edge(w.path[i].edge));
        if(r.unknown_node_count)for(uint32_t n=0;n<provider_.node_count();++n)if(w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64)))out.unknown_sources.insert(n);
        for(unsigned i=0;i<r.unknown_pip_count;++i)out.unknown_pips.emplace(w.unknown_pips[i].tile,w.unknown_pips[i].pip);
        if(out.unknown_sources.size()!=r.unknown_node_count || out.unknown_pips.size()!=r.unknown_pip_count)fail(false,"snapshot unknown export differs");
        return out;
    }
};
} // namespace snapshot_route
