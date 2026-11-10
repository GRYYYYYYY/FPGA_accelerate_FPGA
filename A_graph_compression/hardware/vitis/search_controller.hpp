#pragma once
#include "search_heap_external.hpp"
#include "search_label_index.hpp"
#include "search_label_records.hpp"

namespace fpga_search {
enum class SearchStatus : uint8_t { found,no_path,budget_exhausted,unknown_site_semantics,incomplete_domain,capacity_exhausted,invalid_input };
enum class RowStatus : uint8_t { known,unknown,capacity_exhausted,invalid };
enum class SemanticsStatus : uint8_t { verified,unknown,capacity_exhausted,invalid };
struct PipIdentity {uint32_t tile,pip;};
struct PathEdge {uint32_t source;LabelEdge edge;};
inline bool pip_less(const PipIdentity& a,const PipIdentity& b) {return a.tile<b.tile || (a.tile==b.tile && a.pip<b.pip);}

// All storage belongs to the caller. Provider methods are statically bound:
// node_count, blocked_node, blocked, neighbors(node,buffer,capacity,count),
// semantics(node,edge,state), compatible(state), step_cost(node,edge,a,b,cost).
// A complete hardware top must also supply synthesizable provider methods.
template<class Limits> struct SearchController {
    static_assert(Limits::nodes>0 && Limits::nodes<=0x7fffffffu,"invalid node limit");
    static_assert(Limits::degree>0 && Limits::degree<=0x7fffffffu,"invalid degree limit");
    static_assert(Limits::roots>0 && Limits::roots<=0x7fffffffu,"invalid root limit");
    static_assert(Limits::unknown_pips>0 && Limits::unknown_pips<=0x7fffffffu,"invalid PIP limit");
    static_assert(Limits::path>0 && Limits::expansions>0 && Limits::expansions<=UINT32_MAX,"invalid search limit");
    using State=SiteState<Limits::signals,Limits::bits,Limits::values>;
    using Index=LabelIndex<Limits::slots,Limits::labels,Limits::signals,Limits::bits,Limits::values>;
    using Records=LabelRecords<Limits::labels>;
    using Heap=ExternalHeap<Limits::heap>;
    using Key=typename Index::Key;
    struct Workspace {
        uint64_t *heap,*slots,*records,*unknown_nodes;
        Key* keys;
        LabelEdge* edges;
        PipIdentity* unknown_pips;
        PathEdge* path;
        uint32_t epoch;
        unsigned key_count;
    };
    struct Result {
        SearchStatus status=SearchStatus::no_path;
        uint64_t cost=0,expanded=0,blocked=0,pushes=0,pops=0,improvements=0;
        unsigned path_length=0,unknown_node_count=0,unknown_pip_count=0,label_count=0,max_heap=0,max_probes=0;
        State demands{};
    };
    static bool root_member(const uint32_t* roots,unsigned count,uint32_t node) {
        unsigned lo=0,hi=count;
        for (unsigned step=0;step<32;++step) {
            if (lo>=hi) break;
            const unsigned mid=lo+(hi-lo)/2;
            if (roots[mid]<node) lo=mid+1;else hi=mid;
        }
        return lo<count && roots[lo]==node;
    }
    static bool add_unknown_pip(Workspace& w,Result& out,PipIdentity pip) {
        unsigned lo=0,hi=out.unknown_pip_count;
        for (unsigned step=0;step<32;++step) {
            if (lo>=hi) break;
            const unsigned mid=lo+(hi-lo)/2;
            if (pip_less(w.unknown_pips[mid],pip)) lo=mid+1;else hi=mid;
        }
        if (lo<out.unknown_pip_count && !pip_less(pip,w.unknown_pips[lo])) return true;
        if (out.unknown_pip_count==Limits::unknown_pips) return false;
        for (unsigned step=0;step<Limits::unknown_pips;++step) {
            if (step>=out.unknown_pip_count-lo) break;
            const unsigned i=out.unknown_pip_count-step;w.unknown_pips[i]=w.unknown_pips[i-1];
        }
        w.unknown_pips[lo]=pip;++out.unknown_pip_count;return true;
    }
    static bool valid_state(const State& s) {
        return valid_state_array<SignalOps>(s.signals) && valid_state_array<BitsOps>(s.bits) && valid_state_array<ValueOps>(s.values);
    }
    template<class Provider>
    static Result run(Provider& provider,Workspace& w,const uint32_t* roots,unsigned nroots,
                      uint32_t target,const State& initial,uint64_t budget) {
        Result out;const uint64_t nodes=provider.node_count();
        if (nodes>Limits::nodes || nroots>Limits::roots || budget>Limits::expansions) {out.status=SearchStatus::capacity_exhausted;return out;}
        if (!budget || !nroots || target>=nodes || provider.blocked_node(target) || !valid_state(initial) || !provider.compatible(initial)) {
            out.status=SearchStatus::invalid_input;return out;
        }
        for (unsigned i=0;i<Limits::roots;++i) {
            if (i>=nroots) break;
            if (roots[i]>=nodes || provider.blocked_node(roots[i]) || (i && roots[i]<=roots[i-1])) {out.status=SearchStatus::invalid_input;return out;}
        }
        if (!w.epoch) Index::initialize(w.slots,w.epoch,w.key_count);
        else if (Index::reset(w.slots,w.epoch,w.key_count)!=IndexStatus::reset_complete) {out.status=SearchStatus::invalid_input;return out;}
        const unsigned node_words=unsigned((nodes+63)/64);
        for (unsigned i=0;i<(Limits::nodes+63)/64;++i) {if (i>=node_words) break;w.unknown_nodes[i]=0;}
        unsigned record_count=0,heap_count=0;uint64_t serial=0;
        for (unsigned i=0;i<Limits::roots;++i) {
            if (i>=nroots) break;
            const Key key{roots[i],initial};unsigned id=0,probes=0;
            auto status=Index::get_or_insert(w.slots,w.keys,w.epoch,w.key_count,key,id,probes);
            if (probes>out.max_probes) out.max_probes=probes;
            if (status!=IndexStatus::inserted || id!=record_count) {out.status=status==IndexStatus::capacity_exhausted?SearchStatus::capacity_exhausted:SearchStatus::invalid_input;return out;}
            unsigned written=0;
            if (Records::append_root(w.records,record_count,written)!=RecordStatus::ok || written!=id) {out.status=SearchStatus::invalid_input;return out;}
            out.label_count=record_count;
            if (!Heap::push(w.heap,heap_count,{0,serial++,id})) {out.status=SearchStatus::capacity_exhausted;return out;}
            ++out.pushes;if (heap_count>out.max_heap) out.max_heap=heap_count;
        }
        // Each expanded row can enqueue at most degree entries; unknown rows
        // enqueue none. This bounds even stale/unknown pops without changing budget.
        const uint64_t max_pops=uint64_t(Limits::roots)+uint64_t(Limits::expansions)*Limits::degree;
        for (uint64_t visit=0;visit<max_pops;++visit) {
            if (!heap_count) break;
            Entry entry{};
            if (!Heap::pop(w.heap,heap_count,entry) || entry.label>=record_count) {out.status=SearchStatus::invalid_input;return out;}
            ++out.pops;const unsigned index=unsigned(entry.label);uint64_t current_cost=0;
            if (Records::cost(w.records,record_count,index,current_cost)!=RecordStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
            if (entry.cost!=current_cost) continue;
            const Key current=w.keys[index];
            if (current.node==target) {
                unsigned length=0;
                if (Records::validate_path(w.records,record_count,index,length)!=RecordStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                if (length>Limits::path) {out.status=SearchStatus::capacity_exhausted;return out;}
                unsigned cursor=index;
                for (unsigned i=0;i<Limits::path;++i) {
                    if (i>=length) break;
                    LabelRecord r{};
                    if (Records::read(w.records,record_count,cursor,r)!=RecordStatus::ok || r.root) {out.status=SearchStatus::invalid_input;return out;}
                    w.path[i]={w.keys[r.parent].node,r.edge};cursor=r.parent;
                }
                for (unsigned i=0;i<Limits::path/2;++i) {
                    if (i>=length/2) break;
                    const PathEdge temp=w.path[i];w.path[i]=w.path[length-1-i];w.path[length-1-i]=temp;
                }
                out.path_length=length;out.status=SearchStatus::found;out.cost=entry.cost;out.demands=current.state;return out;
            }
            if (out.expanded>=budget) {out.status=SearchStatus::budget_exhausted;return out;}
            unsigned degree=0;auto row=provider.neighbors(current.node,w.edges,Limits::degree,degree);
            if (row==RowStatus::unknown) {
                const unsigned word=current.node/64;const uint64_t bit=uint64_t(1)<<(current.node%64);
                if (!(w.unknown_nodes[word]&bit)) {w.unknown_nodes[word]|=bit;++out.unknown_node_count;}continue;
            }
            if (row==RowStatus::capacity_exhausted || degree>Limits::degree) {out.status=SearchStatus::capacity_exhausted;return out;}
            if (row!=RowStatus::known) {out.status=SearchStatus::invalid_input;return out;}
            ++out.expanded;
            for (unsigned i=0;i<Limits::degree;++i) {
                if (i>=degree) break;
                const LabelEdge edge=w.edges[i];
                if (edge.dst>=nodes) {out.status=SearchStatus::invalid_input;return out;}
                if (root_member(roots,nroots,edge.dst) || provider.blocked_node(edge.dst) || provider.blocked(current.node,edge)) {++out.blocked;continue;}
                State additions{},merged{};auto sem=provider.semantics(current.node,edge,additions);
                if (sem==SemanticsStatus::unknown) {
                    if (!add_unknown_pip(w,out,{edge.tile,edge.pip})) {out.status=SearchStatus::capacity_exhausted;return out;}continue;
                }
                if (sem==SemanticsStatus::capacity_exhausted) {out.status=SearchStatus::capacity_exhausted;return out;}
                if (sem!=SemanticsStatus::verified) {out.status=SearchStatus::invalid_input;return out;}
                auto merged_status=merge_site_state(current.state,additions,merged);
                if (merged_status==StateStatus::conflict) {++out.blocked;continue;}
                if (merged_status==StateStatus::capacity_exhausted) {out.status=SearchStatus::capacity_exhausted;return out;}
                if (merged_status!=StateStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                if (!provider.compatible(merged)) {++out.blocked;continue;}
                uint64_t step=0;
                if (!provider.step_cost(current.node,edge,current.state,merged,step) || !step || step>=UINT64_MAX-entry.cost) {out.status=SearchStatus::invalid_input;return out;}
                const uint64_t following=entry.cost+step;const Key key{edge.dst,merged};unsigned next=0,probes=0;
                auto found=Index::find(w.slots,w.keys,w.epoch,w.key_count,key,next,probes);
                if (probes>out.max_probes) out.max_probes=probes;
                if (found==IndexStatus::not_found) {
                    auto inserted=Index::get_or_insert(w.slots,w.keys,w.epoch,w.key_count,key,next,probes);
                    if (probes>out.max_probes) out.max_probes=probes;
                    if (inserted!=IndexStatus::inserted || next!=record_count) {out.status=inserted==IndexStatus::capacity_exhausted?SearchStatus::capacity_exhausted:SearchStatus::invalid_input;return out;}
                    unsigned written=0;
                    if (Records::append_child(w.records,record_count,following,index,edge,written)!=RecordStatus::ok || written!=next) {out.status=SearchStatus::invalid_input;return out;}
                    out.label_count=record_count;
                } else if (found==IndexStatus::found) {
                    uint64_t previous=0;
                    if (Records::cost(w.records,record_count,next,previous)!=RecordStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                    if (following>=previous) continue;
                    if (Records::improve(w.records,record_count,next,following,index,edge)!=RecordStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                    ++out.improvements;
                } else {out.status=SearchStatus::invalid_input;return out;}
                if (!Heap::push(w.heap,heap_count,{following,serial++,next})) {out.status=SearchStatus::capacity_exhausted;return out;}
                ++out.pushes;if (heap_count>out.max_heap) out.max_heap=heap_count;
            }
        }
        if (heap_count) out.status=SearchStatus::capacity_exhausted;
        else if (out.unknown_pip_count) out.status=SearchStatus::unknown_site_semantics;
        else if (out.unknown_node_count) out.status=SearchStatus::incomplete_domain;
        return out;
    }
};
} // namespace fpga_search
