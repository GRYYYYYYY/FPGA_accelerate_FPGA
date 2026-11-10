#pragma once
#include "search_controller.hpp"
#include "search_cost_snapshot.hpp"

namespace fpga_search {
// Static provider for the full single-search controller. Adjacency must provide
// node_count() and neighbors(node,LabelEdge*,capacity,count)->RowStatus, retain
// the reference's edge order, and preserve unknown rows and all edge fields.
// This view removes native semantic, fixed-compatibility and cost callbacks.
// Snapshot construction and between-search negotiation are separate operations.
template<class Limits,class Adjacency,unsigned MaxSemantics,unsigned MaxAttributes,
         unsigned MaxProtectedPips,unsigned MaxOwners,unsigned MaxHistory,unsigned MaxFixed>
class SearchSnapshotProvider {
public:
    using Core=SearchController<Limits>;
    using State=typename Core::State;
    using Cost=SearchCostSnapshot<MaxOwners,MaxHistory,MaxFixed,Limits::signals,Limits::bits,Limits::values>;
    struct View {
        unsigned nodes,attributes;
        // Forbidden nodes are a canonical-node bitset. Node cost words are
        // [other_owner_count,history] per canonical node, excluding current net.
        const uint64_t *forbidden,*node_costs;
        const uint8_t *pseudo_attributes,*blocked_attributes;
        // PIP keys are (tile<<32)|pip. Keys strictly sorted; state normalized.
        const uint64_t *protected_pips,*semantics_keys;
        const State* requirements;
        unsigned protected_count,semantics_count;
        typename Cost::View cost;
        uint32_t net;
        uint64_t present;
    };
private:
    static_assert(MaxSemantics>0 && MaxSemantics<=0x7fffffffu,"invalid semantic capacity");
    static_assert(MaxAttributes>0 && MaxAttributes<=0x7fffffffu,"invalid attribute capacity");
    static_assert(MaxProtectedPips>0 && MaxProtectedPips<=0x7fffffffu,"invalid protected capacity");
    Adjacency& adjacency_;
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
    explicit SearchSnapshotProvider(Adjacency& adjacency):adjacency_(adjacency){}
    CostStatus bind(View v) {
        ready_=false;
        if(v.nodes>Limits::nodes || v.attributes>MaxAttributes || v.protected_count>MaxProtectedPips || v.semantics_count>MaxSemantics)return CostStatus::capacity_exhausted;
        if(!v.nodes || !v.attributes || !v.present || v.nodes!=adjacency_.node_count() || !v.forbidden || !v.node_costs || !v.pseudo_attributes || !v.blocked_attributes ||
           (v.protected_count && !v.protected_pips) || (v.semantics_count && (!v.semantics_keys || !v.requirements)))return CostStatus::invalid;
        for(unsigned i=0;i<MaxAttributes;++i){if(i>=v.attributes)break;if(v.pseudo_attributes[i]>1 || v.blocked_attributes[i]>1)return CostStatus::invalid;}
        for(unsigned i=0;i<MaxProtectedPips;++i){if(i>=v.protected_count)break;if(i && v.protected_pips[i]<=v.protected_pips[i-1])return CostStatus::invalid;}
        for(unsigned i=0;i<MaxSemantics;++i) {
            if(i>=v.semantics_count)break;
            if((i && v.semantics_keys[i]<=v.semantics_keys[i-1]) || !Core::valid_state(v.requirements[i]))return CostStatus::invalid;
        }
        const auto status=cost_.bind(v.cost);if(status!=CostStatus::ok)return status;
        view_=v;ready_=true;return CostStatus::ok;
    }
    unsigned node_count()const{return ready_?view_.nodes:0;}
    bool blocked_node(uint32_t node)const{return !ready_ || node>=view_.nodes || ((view_.forbidden[node/64]>>(node%64))&1);}
    bool blocked(uint32_t,const LabelEdge& e)const {
        if(!ready_)return false;
        const uint64_t key=pip_key(e);const unsigned at=lower(view_.protected_pips,view_.protected_count,key);
        return (at<view_.protected_count && view_.protected_pips[at]==key) || (e.attr<view_.attributes && view_.blocked_attributes[e.attr]);
    }
    RowStatus neighbors(uint32_t node,LabelEdge* out,unsigned capacity,unsigned& count) {
        if(!ready_ || node>=view_.nodes)return RowStatus::invalid;
        return adjacency_.neighbors(node,out,capacity,count);
    }
    SemanticsStatus semantics(uint32_t,const LabelEdge& e,State& out)const {
        if(!ready_ || e.attr>=view_.attributes)return SemanticsStatus::invalid;
        const uint64_t key=pip_key(e);const unsigned at=lower(view_.semantics_keys,view_.semantics_count,key);
        const bool pseudo=view_.pseudo_attributes[e.attr]!=0;
        if(at<view_.semantics_count && view_.semantics_keys[at]==key) {
            if(!pseudo || e.dir!=0)return SemanticsStatus::invalid;
            out=view_.requirements[at];return SemanticsStatus::verified;
        }
        out={};return pseudo?SemanticsStatus::unknown:SemanticsStatus::verified;
    }
    bool compatible(const State& s)const {
        bool allowed=false;return ready_ && cost_.compatible(view_.net,s,allowed)==CostStatus::ok && allowed;
    }
    bool step_cost(uint32_t,const LabelEdge& e,const State& before,const State& after,uint64_t& out)const {
        if(!ready_ || e.dst>=view_.nodes)return false;
        return cost_.step_cost(view_.net,before,after,view_.present,view_.node_costs[2*e.dst],view_.node_costs[2*e.dst+1],out)==CostStatus::ok;
    }
};
} // namespace fpga_search
