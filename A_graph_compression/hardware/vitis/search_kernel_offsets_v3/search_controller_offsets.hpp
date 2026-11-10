#pragma once
#include "search_controller_flat.hpp"
#include "search_key_words.hpp"

namespace fpga_search {
// Same complete search algorithm; all external workspace payloads are words.
// PIP word=(tile<<32)|pip. Path edge=8 uint32 words:
// source,dst,tile,pip,up,down,attr,dir. Only count-delimited output is valid.
// edges is a local scratch array, not an external interface.
template<class Limits> struct OffsetSearchController {
    static_assert(Limits::nodes>0 && Limits::nodes<=0x7fffffffu,"invalid node limit");
    static_assert(Limits::degree>0 && Limits::degree<=0x7fffffffu,"invalid degree limit");
    static_assert(Limits::roots>0 && Limits::roots<=0x7fffffffu,"invalid root limit");
    static_assert(Limits::unknown_pips>0 && Limits::unknown_pips<=0x7fffffffu,"invalid PIP limit");
    static_assert(Limits::path>0 && Limits::expansions>0 && Limits::expansions<=UINT32_MAX,"invalid search limit");
    using State=SiteState<Limits::signals,Limits::bits,Limits::values>;
    using Index=WordLabelIndex<Limits::slots,Limits::labels,Limits::signals,Limits::bits,Limits::values>;
    using Records=LabelRecords<Limits::labels>;
    using Heap=ExternalHeap<Limits::heap>;
    using Key=typename Index::Key;
    struct Workspace {
        uint64_t *heap,*slots,*records,*unknown_nodes;
        uint64_t* keys;
        LabelEdge* edges;
        uint64_t* unknown_pips;
        uint32_t* path;
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
#pragma HLS INLINE

        const uint64_t encoded=(uint64_t(pip.tile)<<32)|pip.pip;
        unsigned lo=0,hi=out.unknown_pip_count;
        for (unsigned step=0;step<32;++step) {
            if (lo>=hi) break;
            const unsigned mid=lo+(hi-lo)/2;
            if (w.unknown_pips[mid]<encoded) lo=mid+1;else hi=mid;
        }
        if (lo<out.unknown_pip_count && encoded==w.unknown_pips[lo]) return true;
        if (out.unknown_pip_count==Limits::unknown_pips) return false;
        for (unsigned step=0;step<Limits::unknown_pips;++step) {
            if (step>=out.unknown_pip_count-lo) break;
            const unsigned i=out.unknown_pip_count-step;w.unknown_pips[i]=w.unknown_pips[i-1];
        }
        w.unknown_pips[lo]=encoded;++out.unknown_pip_count;return true;
    }
    static bool valid_state(const State& s) {
        return valid_state_array<SignalOps>(s.signals) && valid_state_array<BitsOps>(s.bits) && valid_state_array<ValueOps>(s.values);
    }
    template<class Provider,class Adjacency>
    static Result run(Provider& provider,Adjacency& adjacency,const uint32_t* image,const uint64_t* packet,const uint8_t* pseudo,const uint8_t* blocked_flags,const State* requirements,Workspace& w,const uint32_t* roots,unsigned nroots,
                      uint32_t target,const State& initial,uint64_t budget) {
#pragma HLS INLINE

        Result out;const uint64_t nodes=provider.node_count();
        if (nodes>Limits::nodes || nroots>Limits::roots || budget>Limits::expansions) {out.status=SearchStatus::capacity_exhausted;return out;}
        if (!budget || !nroots || target>=nodes || provider.blocked_node(packet,target) || !valid_state(initial) || !provider.compatible(packet,initial)) {
            out.status=SearchStatus::invalid_input;return out;
        }
        for (unsigned i=0;i<Limits::roots;++i) {
            if (i>=nroots) break;
            if (roots[i]>=nodes || provider.blocked_node(packet,roots[i]) || (i && roots[i]<=roots[i-1])) {out.status=SearchStatus::invalid_input;return out;}
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
            Key current{};
            if (!Index::Storage::load(w.keys,index,current)) {out.status=SearchStatus::invalid_input;return out;}
            if (current.node==target) {
                unsigned length=0;
                if (Records::validate_path(w.records,record_count,index,length)!=RecordStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                if (length>Limits::path) {out.status=SearchStatus::capacity_exhausted;return out;}
                unsigned cursor=index;
                for (unsigned i=0;i<Limits::path;++i) {
                    if (i>=length) break;
                    LabelRecord r{};
                    if (Records::read(w.records,record_count,cursor,r)!=RecordStatus::ok || r.root) {out.status=SearchStatus::invalid_input;return out;}
                    Key parent_key{};
                    if (!Index::Storage::load(w.keys,r.parent,parent_key)) {out.status=SearchStatus::invalid_input;return out;}
                    const uint64_t at=uint64_t(i)*8;
                    w.path[at]=parent_key.node;w.path[at+1]=r.edge.dst;
                    w.path[at+2]=r.edge.tile;w.path[at+3]=r.edge.pip;
                    w.path[at+4]=r.edge.up;w.path[at+5]=r.edge.down;
                    w.path[at+6]=r.edge.attr;w.path[at+7]=r.edge.dir;cursor=r.parent;
                }
                for (unsigned i=0;i<Limits::path/2;++i) {
                    if (i>=length/2) break;
                    for (unsigned word=0;word<8;++word) {
                        const uint64_t a=uint64_t(i)*8+word,b=uint64_t(length-1-i)*8+word;
                        const uint32_t temp=w.path[a];w.path[a]=w.path[b];w.path[b]=temp;
                    }
                }
                out.path_length=length;out.status=SearchStatus::found;out.cost=entry.cost;out.demands=current.state;return out;
            }
            if (out.expanded>=budget) {out.status=SearchStatus::budget_exhausted;return out;}
            unsigned degree=0;auto row=adjacency.neighbors(image,current.node,w.edges,Limits::degree,degree);
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
                if (root_member(roots,nroots,edge.dst) || provider.blocked_node(packet,edge.dst) || provider.blocked(packet,blocked_flags,current.node,edge)) {++out.blocked;continue;}
                State additions{},merged{};auto sem=provider.semantics(packet,pseudo,requirements,current.node,edge,additions);
                if (sem==SemanticsStatus::unknown) {
                    if (!add_unknown_pip(w,out,{edge.tile,edge.pip})) {out.status=SearchStatus::capacity_exhausted;return out;}continue;
                }
                if (sem==SemanticsStatus::capacity_exhausted) {out.status=SearchStatus::capacity_exhausted;return out;}
                if (sem!=SemanticsStatus::verified) {out.status=SearchStatus::invalid_input;return out;}
                auto merged_status=merge_site_state(current.state,additions,merged);
                if (merged_status==StateStatus::conflict) {++out.blocked;continue;}
                if (merged_status==StateStatus::capacity_exhausted) {out.status=SearchStatus::capacity_exhausted;return out;}
                if (merged_status!=StateStatus::ok) {out.status=SearchStatus::invalid_input;return out;}
                if (!provider.compatible(packet,merged)) {++out.blocked;continue;}
                uint64_t step=0;
                if (!provider.step_cost(packet,current.node,edge,current.state,merged,step) || !step || step>=UINT64_MAX-entry.cost) {out.status=SearchStatus::invalid_input;return out;}
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
