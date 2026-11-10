#pragma once
#include "search_site_state.hpp"

namespace fpga_search {
enum class IndexStatus : uint8_t { found, inserted, capacity_exhausted, invalid, reset_complete, not_found };
template<unsigned S,unsigned B,unsigned V> struct LabelKey {
    uint32_t node;
    SiteState<S,B,V> state;
};

// Full normalized state remains the key: a digest never replaces equality.
template<unsigned S,unsigned B,unsigned V>
bool equal_label_key(const LabelKey<S,B,V>& a,const LabelKey<S,B,V>& b) {
    if (a.node!=b.node || a.state.signals.count!=b.state.signals.count ||
        a.state.bits.count!=b.state.bits.count || a.state.values.count!=b.state.values.count) return false;
    for (unsigned i=0;i<S;++i) {
        if (i>=a.state.signals.count) break;
        if (a.state.signals.data[i]!=b.state.signals.data[i]) return false;
    }
    for (unsigned i=0;i<B;++i) {
        if (i>=a.state.bits.count) break;
        const auto x=a.state.bits.data[i],y=b.state.bits.data[i];
        if (x.field!=y.field || x.mask!=y.mask || x.value!=y.value) return false;
    }
    for (unsigned i=0;i<V;++i) {
        if (i>=a.state.values.count) break;
        const auto x=a.state.values.data[i],y=b.state.values.data[i];
        if (x.field!=y.field || x.value!=y.value) return false;
    }
    return true;
}

inline uint64_t label_hash_word(uint64_t hash,uint64_t word) {
    // Unsigned wrap is intentional. Collisions are resolved by full equality.
    return (hash^word)*1099511628211ULL;
}
template<unsigned S,unsigned B,unsigned V>
uint64_t label_key_hash(const LabelKey<S,B,V>& key) {
    uint64_t h=label_hash_word(14695981039346656037ULL,key.node);
    h=label_hash_word(h,key.state.signals.count);
    for (unsigned i=0;i<S;++i) {
        if (i>=key.state.signals.count) break;
        h=label_hash_word(h,key.state.signals.data[i]);
    }
    h=label_hash_word(h,key.state.bits.count);
    for (unsigned i=0;i<B;++i) {
        if (i>=key.state.bits.count) break;
        auto b=key.state.bits.data[i];h=label_hash_word(h,b.field);
        h=label_hash_word(h,b.mask);h=label_hash_word(h,b.value);
    }
    h=label_hash_word(h,key.state.values.count);
    for (unsigned i=0;i<V;++i) {
        if (i>=key.state.values.count) break;
        auto v=key.state.values.data[i];h=label_hash_word(h,v.field);h=label_hash_word(h,v.value);
    }
    // Fold high bits before selecting a power-of-two bucket.
    h^=h>>32;h*=0xd6e8feb86659fd93ULL;h^=h>>32;return h;
}

template<unsigned Slots,unsigned Labels,unsigned S,unsigned B,unsigned V>
struct LabelIndex {
    static_assert(Slots>0 && Slots<=0x40000000u && !(Slots&(Slots-1)),"slots must be a bounded power of two");
    static_assert(Labels>0 && Labels<0xffffffffu,"label ID overflow");
    using Key=LabelKey<S,B,V>;
    // Caller owns both arrays and all counters. A slot stores epoch:32,id+1:32.
    // One controller writes this table; costs/parents live in separate arrays.
    // Dynamic resource occupancy is keyed by canonical node, not label index.
    static void initialize(uint64_t* slots,uint32_t& epoch,unsigned& count) {
        for (unsigned i=0;i<Slots;++i) slots[i]=0;
        epoch=1;count=0;
    }
    static IndexStatus reset(uint64_t* slots,uint32_t& epoch,unsigned& count) {
        if (!epoch || count>Labels) return IndexStatus::invalid;
        if (epoch==0xffffffffu) {
            // Prevent stale entries from becoming valid when the epoch wraps.
            for (unsigned i=0;i<Slots;++i) slots[i]=0;
            epoch=1;
        } else ++epoch;
        count=0;return IndexStatus::reset_complete;
    }
    static IndexStatus access(uint64_t* slots,Key* keys,uint32_t epoch,
                                    unsigned& count,const Key& requested,
                                    unsigned& index,unsigned& probes,bool insert_allowed) {
        probes=0;
        if (!epoch || count>Labels || !valid_state_array<SignalOps>(requested.state.signals) ||
            !valid_state_array<BitsOps>(requested.state.bits) || !valid_state_array<ValueOps>(requested.state.values)) return IndexStatus::invalid;
        const unsigned first=unsigned(label_key_hash(requested))&(Slots-1);
        for (unsigned probe=0;probe<Slots;++probe) {
            const unsigned slot=(first+probe)&(Slots-1);++probes;
            const uint64_t tag=slots[slot];
            if (uint32_t(tag>>32)!=epoch) {
                if (!insert_allowed) return IndexStatus::not_found;
                if (count==Labels) return IndexStatus::capacity_exhausted;
                const unsigned id=count;
                keys[id]=requested;
                // Publish the key only after its contents have been written.
                slots[slot]=(uint64_t(epoch)<<32)|uint64_t(id+1);
                count=id+1;index=id;return IndexStatus::inserted;
            }
            const uint32_t id_plus_one=uint32_t(tag);
            if (!id_plus_one || id_plus_one>count) return IndexStatus::invalid;
            const unsigned id=id_plus_one-1;
            if (equal_label_key(keys[id],requested)) {index=id;return IndexStatus::found;}
        }
        return insert_allowed?IndexStatus::capacity_exhausted:IndexStatus::not_found;
    }
    static IndexStatus get_or_insert(uint64_t* slots,Key* keys,uint32_t epoch,
                                    unsigned& count,const Key& requested,
                                    unsigned& index,unsigned& probes) {
        return access(slots,keys,epoch,count,requested,index,probes,true);
    }
    static IndexStatus find(uint64_t* slots,Key* keys,uint32_t epoch,
                            unsigned& count,const Key& requested,
                            unsigned& index,unsigned& probes) {
        return access(slots,keys,epoch,count,requested,index,probes,false);
    }
};
} // namespace fpga_search
