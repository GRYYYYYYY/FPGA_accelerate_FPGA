#pragma once
#include "search_controller.hpp"
#include "search_offset_cost.hpp"

namespace fpga_search {
// Static provider for the full single-search controller. Adjacency must provide
// node_count() and neighbors(node,LabelEdge*,capacity,count)->RowStatus, retain
// the reference's edge order, and preserve unknown rows and all edge fields.
// This view removes native semantic, fixed-compatibility and cost callbacks.
// Snapshot construction and between-search negotiation are separate operations.
template<class Limits,class Adjacency,unsigned MaxSemantics,unsigned MaxAttributes,
         unsigned MaxProtectedPips,unsigned MaxOwners,unsigned MaxHistory,unsigned MaxFixed>
class SearchOffsetProvider {
public:
    using Core=SearchController<Limits>;
    using State=typename Core::State;
    using Cost=SearchOffsetCost<MaxOwners,MaxHistory,MaxFixed,Limits::signals,Limits::bits,Limits::values>;
    struct View {
        unsigned nodes,attributes;
        // Forbidden nodes are a canonical-node bitset. Node cost words are
        // [other_owner_count,history] per canonical node, excluding current net.
        uint64_t forbidden,node_costs;
        // PIP keys are (tile<<32)|pip. Keys strictly sorted; state normalized.
        uint64_t protected_pips,semantics_keys;
        unsigned protected_count,semantics_count;
        typename Cost::View cost;
        uint32_t net;
        uint64_t present;
    };
private:
    static_assert(MaxSemantics>0 && MaxSemantics<=0x7fffffffu,"invalid semantic capacity");
    static_assert(MaxAttributes>0 && MaxAttributes<=0x7fffffffu,"invalid attribute capacity");
    static_assert(MaxProtectedPips>0 && MaxProtectedPips<=0x7fffffffu,"invalid protected capacity");
    View view_{};Cost cost_;bool ready_=false;
    static unsigned lower(const uint64_t* data,unsigned count,uint64_t key) {
        unsigned lo=0,hi=count;
        for(unsigned step=0;step<32;++step) {
            if(lo>=hi)break;
            const unsigned mid=lo+(hi-lo)/2;
            if(data[mid]<key)lo=mid+1;else hi=mid;
        }
        return lo;
    }
    static uint64_t pip_key(const LabelEdge& e){return (uint64_t(e.tile)<<32)|e.pip;}
public:
    CostStatus bind(const uint64_t* packet,View v,unsigned graph_nodes,const uint8_t* pseudo,const uint8_t* blocked,const State* requirements) {
#pragma HLS INLINE

        ready_=false;
        if(v.nodes>Limits::nodes || v.attributes>MaxAttributes || v.protected_count>MaxProtectedPips || v.semantics_count>MaxSemantics)return CostStatus::capacity_exhausted;
        if(!v.nodes || !v.attributes || !v.present || v.nodes!=graph_nodes || !packet || !pseudo || !blocked || (v.semantics_count && !requirements))return CostStatus::invalid;
        for(unsigned i=0;i<MaxAttributes;++i){if(i>=v.attributes)break;if(pseudo[i]>1 || blocked[i]>1)return CostStatus::invalid;}
        for(unsigned i=0;i<MaxProtectedPips;++i){if(i>=v.protected_count)break;if(i && packet[v.protected_pips+i]<=packet[v.protected_pips+i-1])return CostStatus::invalid;}
        for(unsigned i=0;i<MaxSemantics;++i) {
            if(i>=v.semantics_count)break;
            if((i && packet[v.semantics_keys+i]<=packet[v.semantics_keys+i-1]) || !Core::valid_state(requirements[i]))return CostStatus::invalid;
        }
        const auto status=cost_.bind(packet,v.cost);if(status!=CostStatus::ok)return status;
        view_=v;ready_=true;return CostStatus::ok;
    }
    unsigned node_count()const{
#pragma HLS INLINE
return ready_?view_.nodes:0;}
    bool blocked_node(const uint64_t* packet,uint32_t node)const{
#pragma HLS INLINE
return !ready_ || node>=view_.nodes || ((packet[view_.forbidden+node/64]>>(node%64))&1);}
    bool blocked(const uint64_t* packet,const uint8_t* blocked_flags,uint32_t,const LabelEdge& e)const {
#pragma HLS INLINE

        if(!ready_)return false;
        const uint64_t key=pip_key(e);const unsigned at=lower(packet+view_.protected_pips,view_.protected_count,key);
        return (at<view_.protected_count && packet[view_.protected_pips+at]==key) || (e.attr<view_.attributes && blocked_flags[e.attr]);
    }
    SemanticsStatus semantics(const uint64_t* packet,const uint8_t* pseudo_flags,const State* requirements,uint32_t,const LabelEdge& e,State& out)const {
#pragma HLS INLINE

        if(!ready_ || e.attr>=view_.attributes)return SemanticsStatus::invalid;
        const uint64_t key=pip_key(e);const unsigned at=lower(packet+view_.semantics_keys,view_.semantics_count,key);
        const bool pseudo=pseudo_flags[e.attr]!=0;
        if(at<view_.semantics_count && packet[view_.semantics_keys+at]==key) {
            if(!pseudo || e.dir!=0)return SemanticsStatus::invalid;
            out=requirements[at];return SemanticsStatus::verified;
        }
        out={};return pseudo?SemanticsStatus::unknown:SemanticsStatus::verified;
    }
    bool compatible(const uint64_t* packet,const State& s)const {
#pragma HLS INLINE

        bool allowed=false;return ready_ && cost_.compatible(packet,view_.net,s,allowed)==CostStatus::ok && allowed;
    }
    bool step_cost(const uint64_t* packet,uint32_t,const LabelEdge& e,const State& before,const State& after,uint64_t& out)const {
#pragma HLS INLINE

        if(!ready_ || e.dst>=view_.nodes)return false;
        return cost_.step_cost(packet,view_.net,before,after,view_.present,packet[view_.node_costs+2*e.dst],packet[view_.node_costs+2*e.dst+1],out)==CostStatus::ok;
    }
};
} // namespace fpga_search
