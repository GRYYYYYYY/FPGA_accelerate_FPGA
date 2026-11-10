#pragma once
// Include after the native search types. This bridge owns host memory and
// invokes native graph/cost callbacks; only search_controller_words.hpp is the core.
#include "search_controller_words.hpp"
#include <memory>
#include <type_traits>

namespace word_controller_adapter {
struct RegionLimits {
    static constexpr unsigned nodes=1048576,degree=1024,roots=1048576,unknown_pips=1100754,path=524288,expansions=200000;
    static constexpr unsigned signals=32,bits=16,values=8,slots=1048576,labels=524288,heap=131072;
};
struct Counters {
    uint64_t searches=0,pushes=0,pops=0,improvements=0,found=0,capacity_failures=0,invalid=0;
    unsigned max_heap=0,max_labels=0,max_probes=0;
};
inline thread_local Counters counters;
template<class L> struct Storage {
    using Core=fpga_search::WordSearchController<L>;
    std::unique_ptr<uint64_t[]> heap{new uint64_t[3*L::heap]},slots{new uint64_t[L::slots]},records{new uint64_t[10*L::labels]},unknown{new uint64_t[(L::nodes+63)/64]};
    std::unique_ptr<uint64_t[]> keys{new uint64_t[Core::Index::Storage::Words*L::labels]};
    std::unique_ptr<fpga_search::LabelEdge[]> edges{new fpga_search::LabelEdge[L::degree]};
    std::unique_ptr<fpga_search::PipIdentity[]> pips{new fpga_search::PipIdentity[L::unknown_pips]};
    std::unique_ptr<fpga_search::PathEdge[]> path{new fpga_search::PathEdge[L::path]};
    typename Core::Workspace workspace{heap.get(),slots.get(),records.get(),unknown.get(),keys.get(),edges.get(),pips.get(),path.get(),0,0};
};
template<class L> Storage<L>& storage() {static thread_local Storage<L> s;return s;}
template<class State> site_native::Normalized unpack(const State& s) {
    site_native::Normalized n;
    for (unsigned i=0;i<s.signals.count;++i) n.signals.insert(s.signals.data[i]);
    for (unsigned i=0;i<s.bits.count;++i) {auto b=s.bits.data[i];n.bits.emplace(b.field,std::make_pair(b.mask,b.value));}
    for (unsigned i=0;i<s.values.count;++i) {auto v=s.values.data[i];n.values.emplace(v.field,v.value);}
    return n;
}
template<class L> bool pack(const site_native::Normalized& n,typename fpga_search::WordSearchController<L>::State& out) {
    if (n.signals.size()>L::signals || n.bits.size()>L::bits || n.values.size()>L::values) return false;
    out={};
    for (auto s:n.signals) out.signals.data[out.signals.count++]=s;
    for (auto b:n.bits) out.bits.data[out.bits.count++]={b.first,b.second.first,b.second.second};
    for (auto v:n.values) out.values.data[out.values.count++]={v.first,v.second};
    return true;
}
inline Edge native_edge(const fpga_search::LabelEdge& e) {return {e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
inline const char* status_name(fpga_search::SearchStatus status) {
    using S=fpga_search::SearchStatus;
    switch(status) {
        case S::found:return "found";case S::no_path:return "no_path";case S::budget_exhausted:return "budget_exhausted";
        case S::unknown_site_semantics:return "unknown_site_semantics";case S::incomplete_domain:return "incomplete_domain";
        case S::capacity_exhausted:return "capacity_exhausted";case S::invalid_input:return "invalid_input";
    }
    throw std::logic_error("invalid controller status");
}
template<class L,class Graph,class Semantics,class Blocked,class Compatible,class Cost> struct Bridge {
    using State=typename fpga_search::WordSearchController<L>::State;
    Graph& graph;const std::set<uint32_t>& forbidden;
    Semantics& sem;Blocked& block;Compatible& compat;Cost& cost;
    std::vector<Edge> row;
    size_t node_count() const {return graph.node_count();}
    bool blocked_node(uint32_t n) const {return forbidden.count(n)!=0;}
    bool blocked(uint32_t n,const fpga_search::LabelEdge& e) {return block(n,native_edge(e));}
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* out,unsigned capacity,unsigned& count) {
        if (!graph.neighbors(n,row)) return fpga_search::RowStatus::unknown;
        if (row.size()>capacity) return fpga_search::RowStatus::capacity_exhausted;
        count=unsigned(row.size());
        for (unsigned i=0;i<count;++i) {const auto& e=row[i];out[i]={e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
        return fpga_search::RowStatus::known;
    }
    fpga_search::SemanticsStatus semantics(uint32_t n,const fpga_search::LabelEdge& e,State& out) {
        auto s=sem(n,native_edge(e));out={};
        if (s.demands) {
            auto normalized=site_native::normalize(*s.demands);
            if (!pack<L>(normalized,out)) return fpga_search::SemanticsStatus::capacity_exhausted;
        } else if (s.pseudo) return fpga_search::SemanticsStatus::unknown;
        return fpga_search::SemanticsStatus::verified;
    }
    bool compatible(const State& s) {return compat(unpack(s));}
    bool step_cost(uint32_t n,const fpga_search::LabelEdge& e,const State& before,const State& after,uint64_t& out) {
        auto v=cost(n,native_edge(e),unpack(before),unpack(after));
        static_assert(std::is_integral_v<decltype(v)>,"integer costs required");
        if constexpr (std::is_signed_v<decltype(v)>) if (v<=0) return false;
        out=uint64_t(v);return out!=0;
    }
};
template<class L,class Graph,class Semantics,class Blocked,class Compatible,class Cost>
site_native::SearchResult search(Graph& graph,const std::set<uint32_t>& roots,uint32_t target,
        const site_native::Demands& initial,uint64_t budget,const std::set<uint32_t>& forbidden,
        Semantics sem,Blocked blocked,Compatible compatible,Cost step_cost) {
    ++counters.searches;site_native::SearchResult out;
    using Core=fpga_search::WordSearchController<L>;typename Core::State state{};
    if (roots.size()>L::roots || !pack<L>(site_native::normalize(initial),state)) {
        ++counters.capacity_failures;out.status="capacity_exhausted";return out;
    }
    std::vector<uint32_t> sorted_roots(roots.begin(),roots.end());
    Bridge<L,Graph,Semantics,Blocked,Compatible,Cost> provider{graph,forbidden,sem,blocked,compatible,step_cost,{}};
    auto& w=storage<L>().workspace;auto r=Core::run(provider,w,sorted_roots.data(),unsigned(sorted_roots.size()),target,state,budget);
    counters.pushes+=r.pushes;counters.pops+=r.pops;counters.improvements+=r.improvements;
    counters.max_heap=std::max(counters.max_heap,r.max_heap);counters.max_labels=std::max(counters.max_labels,r.label_count);counters.max_probes=std::max(counters.max_probes,r.max_probes);
    if (r.status==fpga_search::SearchStatus::invalid_input) {++counters.invalid;throw std::invalid_argument("invalid bounded search input/state");}
    if (r.status==fpga_search::SearchStatus::capacity_exhausted) ++counters.capacity_failures;
    out.status=status_name(r.status);out.cost=r.cost;out.expanded=r.expanded;out.blocked=r.blocked;
    if (r.status==fpga_search::SearchStatus::found) {++counters.found;out.demands=unpack(r.demands);}
    for (unsigned i=0;i<r.path_length;++i) out.path.emplace_back(w.path[i].source,native_edge(w.path[i].edge));
    if (r.unknown_node_count) for (uint32_t n=0;n<graph.node_count();++n)
        if (w.unknown_nodes[n/64]&(uint64_t(1)<<(n%64))) out.unknown_sources.insert(n);
    for (unsigned i=0;i<r.unknown_pip_count;++i) out.unknown_pips.emplace(w.unknown_pips[i].tile,w.unknown_pips[i].pip);
    if (out.unknown_sources.size()!=r.unknown_node_count || out.unknown_pips.size()!=r.unknown_pip_count) throw std::logic_error("unknown-set export mismatch");
    return out;
}
} // namespace word_controller_adapter
