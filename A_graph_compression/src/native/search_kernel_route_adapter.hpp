#pragma once
// CPU integration of the actual production search top. Snapshot construction,
// negotiation, occupancy updates and result retention remain host work.
// Adjacency and the entire search execute inside the kernel C model.
#include "site_search.hpp"
#include "site_ledger.hpp"
#include "search_flat_controller_adapter.hpp"
#include "search_snapshot_inputs.hpp"
#include "search_snapshot_provider.hpp"
#include "search_kernel_binding.hpp"
#include "search_kernel_packet.hpp"

namespace kernel_route {
struct RegionLimits:flat_controller_adapter::RegionLimits {
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
    using Core=fpga_search::FlatSearchController<Limits>;
    Adjacency<Graph> adjacency_;
    const snapshot_inputs::SiteBuffers<Limits>& sites_;
    Provider provider_;
    std::vector<uint64_t> forbidden_,nodes_,owners_,history_,packet_;
    ImageView image_{};
    [[noreturn]] static void fail(bool capacity,const char* message) {
        ++counters.failures;
        if(capacity)throw std::length_error(message);
        throw std::invalid_argument(message);
    }
public:
    Context(Graph& graph,const snapshot_inputs::SiteBuffers<Limits>& sites):adjacency_{graph,{}},sites_(sites),provider_(adjacency_) {
        if(!active_image)fail(false,"no production kernel image bound");
        image_=*active_image;
        if(image_.config[2]!=graph.node_count())fail(false,"kernel/native node domains differ");
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
        packet_=search_kernel_host::packet<Limits>(view,0,1,1,{});
        ++kernel_counters.packets;kernel_counters.serialized_words+=packet_.size();
        kernel_counters.max_packet_words=std::max(kernel_counters.max_packet_words,unsigned(packet_.size()));
        counters.node_occupied+=occupied;counters.node_history+=!node_history.empty();counters.site_occupied+=!rows.empty();counters.site_history+=!site_history.empty();
        counters.max_site_owners=std::max(counters.max_site_owners,unsigned(rows.size()));counters.max_site_history=std::max(counters.max_site_history,unsigned(site_history.size()));
    }
    site_native::SearchResult search(const std::set<uint32_t>& roots,uint32_t target,const site_native::Normalized& initial,uint64_t budget) {
        auto& c=flat_controller_adapter::counters;++c.searches;
        site_native::SearchResult out;typename Core::State state{};
        if(roots.size()>Limits::roots || !flat_controller_adapter::pack<Limits>(initial,state)){++c.capacity_failures;out.status="capacity_exhausted";return out;}
        std::vector<uint32_t> sorted_roots(roots.begin(),roots.end());auto& w=flat_controller_adapter::storage<Limits>().workspace;
        if(packet_.size()<32+Core::Index::Storage::Words)fail(false,"kernel search before snapshot bind");
        packet_[6]=target;packet_[7]=sorted_roots.size();packet_[8]=budget;
        const typename Core::Key initial_key{0,state};
        if(!Core::Index::Storage::store(packet_.data()+32,0,initial_key))fail(false,"invalid kernel initial key");
        kernel_counters.max_roots=std::max(kernel_counters.max_roots,unsigned(sorted_roots.size()));
        uint64_t meta[2]={w.epoch,w.key_count},result[81]{};
        invoke<Limits>(image_,sorted_roots.data(),packet_.data(),unsigned(packet_.size()),w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result);
        if(result[15]!=1 || result[0]>uint64_t(fpga_search::SearchStatus::invalid_input) || meta[0]>UINT32_MAX || meta[1]>Limits::labels || result[7]>Limits::path || result[8]>Limits::nodes || result[9]>Limits::unknown_pips || result[10]>Limits::labels || result[11]>Limits::heap || result[12]>Limits::slots)fail(false,"malformed kernel result");
        if(result[13]){if(result[13]!=meta[0] || result[14]!=meta[1])fail(false,"kernel metadata/result mismatch");}
        else if(meta[0]!=w.epoch || meta[1]!=w.key_count)fail(false,"kernel preflight mutated metadata");
        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);
        typename Core::Result r;r.status=fpga_search::SearchStatus(result[0]);r.cost=result[1];r.expanded=result[2];r.blocked=result[3];
        r.pushes=result[4];r.pops=result[5];r.improvements=result[6];r.path_length=unsigned(result[7]);r.unknown_node_count=unsigned(result[8]);r.unknown_pip_count=unsigned(result[9]);r.label_count=unsigned(result[10]);r.max_heap=unsigned(result[11]);r.max_probes=unsigned(result[12]);
        if(r.status==fpga_search::SearchStatus::found){typename Core::Key key{};if(!Core::Index::Storage::load(result+16,0,key) || key.node!=target)fail(false,"invalid kernel demand state");r.demands=key.state;}
        else for(unsigned i=16;i<81;++i)if(result[i])fail(false,"failed kernel result contains demand state");
        c.pushes+=r.pushes;c.pops+=r.pops;c.improvements+=r.improvements;c.max_heap=std::max(c.max_heap,r.max_heap);c.max_labels=std::max(c.max_labels,r.label_count);c.max_probes=std::max(c.max_probes,r.max_probes);
        if(r.status==fpga_search::SearchStatus::invalid_input){++c.invalid;fail(false,"invalid snapshot search input/state");}
        if(r.status==fpga_search::SearchStatus::capacity_exhausted)++c.capacity_failures;
        out.status=flat_controller_adapter::status_name(r.status);out.cost=r.cost;out.expanded=r.expanded;out.blocked=r.blocked;
        if(r.status==fpga_search::SearchStatus::found){++c.found;out.demands=flat_controller_adapter::unpack(r.demands);counters.site_found_paths+=(r.demands.signals.count || r.demands.bits.count || r.demands.values.count);}
        for(unsigned i=0;i<r.path_length;++i){const uint32_t* p=w.path+uint64_t(i)*8;out.path.emplace_back(p[0],Edge{p[1],p[2],p[3],p[4],p[5],p[6],p[7]});}
        if(r.unknown_node_count)for(uint32_t n=0;n<provider_.node_count();++n)if(w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64)))out.unknown_sources.insert(n);
        for(unsigned i=0;i<r.unknown_pip_count;++i)out.unknown_pips.emplace(uint32_t(w.unknown_pips[i]>>32),uint32_t(w.unknown_pips[i]));
        if(out.unknown_sources.size()!=r.unknown_node_count || out.unknown_pips.size()!=r.unknown_pip_count)fail(false,"snapshot unknown export differs");
        return out;
    }
};
} // namespace kernel_route
