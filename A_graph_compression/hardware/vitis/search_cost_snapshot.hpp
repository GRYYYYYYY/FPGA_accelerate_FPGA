#pragma once
#include "search_site_state.hpp"

namespace fpga_search {
enum class CostStatus : uint8_t {ok,invalid,capacity_exhausted,overflow};

// Read-only snapshot for one search. IDs are canonical physical resources.
// Owners/fixed use four uint64 words: (kind<<32)|field, owner, mask, value.
// kind=0 exclusive signal, 1 masked configuration bits, 2 categorical value.
// Owners are strictly sorted by (key,owner). Fixed keys are unique; owner is
// meaningful only for signals and must be zero for configuration records.
// History uses two words: key, penalty; strictly sorted unique keys.
// Caller owns sufficiently sized, disjoint buffers and must re-bind after edits.
// Global fixed constraints are separate from bounded per-path state capacity.
template<unsigned MaxOwners,unsigned MaxHistory,unsigned MaxFixed,
         unsigned Signals,unsigned Bits,unsigned Values>
class SearchCostSnapshot {
    static_assert(MaxOwners>0 && MaxOwners<=0x3fffffffu,"invalid owner capacity");
    static_assert(MaxFixed>0 && MaxFixed<=0x3fffffffu,"invalid fixed capacity");
    static_assert(MaxHistory>0 && MaxHistory<=0x3fffffffu,"invalid history capacity");
public:
    using State=SiteState<Signals,Bits,Values>;
    struct View {
        const uint64_t *owners,*history,*fixed;
        unsigned owner_count,history_count,fixed_count;
    };
private:
    View view_{};
    bool ready_=false;
    struct Resource {uint64_t key,mask,value;};
    static bool valid_record(const uint64_t* p,bool fixed) {
        const uint64_t kind=p[0]>>32;
        if (kind>2 || p[1]>UINT32_MAX) return false;
        if (kind==0) return p[2]==0 && p[3]==0;
        if (fixed && p[1]!=0) return false;
        if (kind==1) return !(p[3]&~p[2]);
        return p[2]==0 && p[3]<=UINT32_MAX;
    }
    static bool valid_state(const State& s) {
        return valid_state_array<SignalOps>(s.signals) && valid_state_array<BitsOps>(s.bits) && valid_state_array<ValueOps>(s.values);
    }
    static Resource item(const State& s,unsigned i) {
        if (i<s.signals.count) return {s.signals.data[i],0,0};
        i-=s.signals.count;
        if (i<s.bits.count) {auto b=s.bits.data[i];return {(uint64_t(1)<<32)|b.field,b.mask,b.value};}
        auto v=s.values.data[i-s.bits.count];return {(uint64_t(2)<<32)|v.field,0,v.value};
    }
    template<unsigned Stride>
    static unsigned lower_key(const uint64_t* data,unsigned count,uint64_t key) {
        unsigned lo=0,hi=count;
        for (unsigned step=0;step<32;++step) {
            if (lo>=hi) break;
            const unsigned mid=lo+(hi-lo)/2;
            if (data[Stride*mid]<key) lo=mid+1;else hi=mid;
        }
        return lo;
    }
    static bool same_before(const State& before,Resource r) {
        unsigned lo=0,hi=before.signals.count+before.bits.count+before.values.count;
        const unsigned count=hi;
        for (unsigned step=0;step<32;++step) {
            if (lo>=hi) break;
            const unsigned mid=lo+(hi-lo)/2;
            if (item(before,mid).key<r.key) lo=mid+1;else hi=mid;
        }
        if (lo==count) return false;
        const auto old=item(before,lo);
        return old.key==r.key && old.mask==r.mask && old.value==r.value;
    }
    static bool incompatible(Resource r,uint64_t mask,uint64_t value) {
        const unsigned kind=unsigned(r.key>>32);
        if (!kind) return true;
        if (kind==1) return ((r.value^value)&r.mask&mask)!=0;
        return r.value!=value;
    }
public:
    CostStatus bind(View v) {
        ready_=false;
        if (v.owner_count>MaxOwners || v.history_count>MaxHistory || v.fixed_count>MaxFixed) return CostStatus::capacity_exhausted;
        if ((v.owner_count && !v.owners) || (v.history_count && !v.history) || (v.fixed_count && !v.fixed)) return CostStatus::invalid;
        for (unsigned i=0;i<MaxOwners;++i) {
            if (i>=v.owner_count) break;
            const auto p=v.owners+4*i;
            if (!valid_record(p,false)) return CostStatus::invalid;
            if (i && (p[0]<p[-4] || (p[0]==p[-4] && p[1]<=p[-3]))) return CostStatus::invalid;
        }
        for (unsigned i=0;i<MaxFixed;++i) {
            if (i>=v.fixed_count) break;
            const auto p=v.fixed+4*i;
            if (!valid_record(p,true) || (i && p[0]<=p[-4])) return CostStatus::invalid;
        }
        for (unsigned i=0;i<MaxHistory;++i) {
            if (i>=v.history_count) break;
            if ((v.history[2*i]>>32)>2 || (i && v.history[2*i]<=v.history[2*(i-1)])) return CostStatus::invalid;
        }
        view_=v;ready_=true;return CostStatus::ok;
    }
    // Fixed configuration always applies; exclusive signals allow their owner.
    // Negotiable dynamic owners are penalized, not treated as fixed conflicts.
    CostStatus compatible(uint32_t net,const State& requested,bool& output) const {
        if (!ready_ || !valid_state(requested)) return CostStatus::invalid;
        bool allowed=true;const unsigned count=requested.signals.count+requested.bits.count+requested.values.count;
        for (unsigned i=0;i<Signals+Bits+Values;++i) {
            if (i>=count) break;
            const auto r=item(requested,i);const unsigned at=lower_key<4>(view_.fixed,view_.fixed_count,r.key);
            if (at==view_.fixed_count || view_.fixed[4*at]!=r.key) continue;
            const auto p=view_.fixed+4*at;
            if ((r.key>>32)==0) {if (p[1]!=net) allowed=false;}
            else if (incompatible(r,p[2],p[3])) allowed=false;
        }
        output=allowed;return CostStatus::ok;
    }
    CostStatus penalty(uint32_t net,const State& before,const State& after,uint64_t present,uint64_t& output) const {
        if (!ready_ || !valid_state(before) || !valid_state(after)) return CostStatus::invalid;
        uint64_t total=0;const unsigned count=after.signals.count+after.bits.count+after.values.count;
        for (unsigned i=0;i<Signals+Bits+Values;++i) {
            if (i>=count) break;
            const auto r=item(after,i);if (same_before(before,r)) continue;
            const unsigned start=lower_key<4>(view_.owners,view_.owner_count,r.key);uint64_t others=0;
            for (unsigned j=0;j<MaxOwners;++j) {
                if (j>=view_.owner_count-start) break;
                const auto p=view_.owners+4*(start+j);
                if (p[0]!=r.key) break;
                if (p[1]!=net && incompatible(r,p[2],p[3])) ++others;
            }
            const unsigned h=lower_key<2>(view_.history,view_.history_count,r.key);
            const uint64_t past=h<view_.history_count && view_.history[2*h]==r.key?view_.history[2*h+1]:0;
            if (present && others>(UINT64_MAX-past)/present) return CostStatus::overflow;
            const uint64_t increment=present*others+past;
            if (increment>UINT64_MAX-total) return CostStatus::overflow;
            total+=increment;
        }
        output=total;return CostStatus::ok;
    }
    // other_node_owners excludes this net, keyed by canonical destination node.
    // A result UINT64_MAX is permitted here as in native routing; the search
    // controller separately rejects any path addition reaching UINT64_MAX.
    CostStatus step_cost(uint32_t net,const State& before,const State& after,uint64_t present,
                         uint64_t other_node_owners,uint64_t node_history,uint64_t& output) const {
        if (!present) return CostStatus::invalid;
        if (node_history==UINT64_MAX || other_node_owners>(UINT64_MAX-1-node_history)/present) return CostStatus::overflow;
        uint64_t site=0;const auto status=penalty(net,before,after,present,site);
        if (status!=CostStatus::ok) return status;
        const uint64_t node=1+present*other_node_owners+node_history;
        if (site>UINT64_MAX-node) return CostStatus::overflow;
        output=node+site;return CostStatus::ok;
    }
};
} // namespace fpga_search
