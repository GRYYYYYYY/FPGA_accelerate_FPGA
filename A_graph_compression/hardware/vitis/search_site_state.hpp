#pragma once
#include <stdint.h>

namespace fpga_search {
// IDs are physical resource identities supplied by the adapter, not template IDs.
enum class StateStatus : uint8_t { ok, invalid, conflict, capacity_exhausted, unverified };
struct ConfigBits {uint32_t field;uint64_t mask,value;};
struct ConfigValue {uint32_t field,value;};
struct SignalOps {
    static uint32_t key(uint32_t a) {return a;}
    static bool valid(uint32_t) {return true;}
    static StateStatus combine(uint32_t a,uint32_t,uint32_t& out) {out=a;return StateStatus::ok;}
};
struct BitsOps {
    static uint32_t key(const ConfigBits& a) {return a.field;}
    static bool valid(const ConfigBits& a) {return !(a.value&~a.mask);}
    static StateStatus combine(const ConfigBits& a,const ConfigBits& b,ConfigBits& out) {
        if ((a.value^b.value)&a.mask&b.mask) return StateStatus::conflict;
        out={a.field,a.mask|b.mask,a.value|b.value};return StateStatus::ok;
    }
};
struct ValueOps {
    static uint32_t key(const ConfigValue& a) {return a.field;}
    static bool valid(const ConfigValue&) {return true;}
    static StateStatus combine(const ConfigValue& a,const ConfigValue& b,ConfigValue& out) {
        if (a.value!=b.value) return StateStatus::conflict;
        out=a;return StateStatus::ok;
    }
};

template<class T,unsigned Capacity> struct StateArray {
    static_assert(Capacity>0 && Capacity<=0x3fffffffu,"invalid state capacity");
    T data[Capacity];
    unsigned count;
};

template<class Ops,class T,unsigned Capacity>
bool valid_state_array(const StateArray<T,Capacity>& a) {
    if (a.count>Capacity) return false;
    for (unsigned i=0;i<Capacity;++i) {
        if (i>=a.count) break;
        if (!Ops::valid(a.data[i])) return false;
        if (i && Ops::key(a.data[i-1])>=Ops::key(a.data[i])) return false;
    }
    return true;
}

// Internal insertion into an already validated, sorted array. Failure is atomic.
template<class Ops,class T,unsigned Capacity>
StateStatus insert_state_item(StateArray<T,Capacity>& a,const T& item) {
    if (a.count>Capacity || !Ops::valid(item)) return StateStatus::invalid;
    unsigned at=0;
    for (unsigned i=0;i<Capacity;++i) {
        if (i>=a.count || Ops::key(a.data[i])>=Ops::key(item)) break;
        ++at;
    }
    if (at<a.count && Ops::key(a.data[at])==Ops::key(item)) {
        T merged{};auto status=Ops::combine(a.data[at],item,merged);
        if (status==StateStatus::ok) a.data[at]=merged;
        return status;
    }
    if (a.count==Capacity) return StateStatus::capacity_exhausted;
    for (unsigned i=Capacity-1;i>0;--i) {
        if (i<=a.count && i>at) a.data[i]=a.data[i-1];
    }
    a.data[at]=item;++a.count;return StateStatus::ok;
}

template<class Ops,class T,unsigned Capacity>
StateStatus merge_state_array(const StateArray<T,Capacity>& a,
                             const StateArray<T,Capacity>& b,StateArray<T,Capacity>& out) {
    if (!valid_state_array<Ops>(a) || !valid_state_array<Ops>(b)) return StateStatus::invalid;
    StateArray<T,Capacity> result{};unsigned i=0,j=0;
    for (unsigned step=0;step<2*Capacity;++step) {
        if (i==a.count && j==b.count) break;
        T item{};
        if (j==b.count || (i<a.count && Ops::key(a.data[i])<Ops::key(b.data[j]))) item=a.data[i++];
        else if (i==a.count || Ops::key(b.data[j])<Ops::key(a.data[i])) item=b.data[j++];
        else {
            auto status=Ops::combine(a.data[i++],b.data[j++],item);
            if (status!=StateStatus::ok) return status;
        }
        if (result.count==Capacity) return StateStatus::capacity_exhausted;
        result.data[result.count++]=item;
    }
    out=result;return StateStatus::ok;
}

template<unsigned Signals,unsigned Bits,unsigned Values> struct SiteState {
    StateArray<uint32_t,Signals> signals;
    StateArray<ConfigBits,Bits> bits;
    StateArray<ConfigValue,Values> values;
};

// Output may alias either input. Zero-mask fields remain present, matching the
// native label-key semantics. No mutation is committed on any failure.
template<unsigned S,unsigned B,unsigned V>
StateStatus merge_site_state(const SiteState<S,B,V>& a,const SiteState<S,B,V>& b,
                             SiteState<S,B,V>& out) {
    SiteState<S,B,V> result{};
    auto status=merge_state_array<SignalOps>(a.signals,b.signals,result.signals);
    if (status!=StateStatus::ok) return status;
    status=merge_state_array<BitsOps>(a.bits,b.bits,result.bits);
    if (status!=StateStatus::ok) return status;
    status=merge_state_array<ValueOps>(a.values,b.values,result.values);
    if (status!=StateStatus::ok) return status;
    out=result;return StateStatus::ok;
}

// Raw buffers are caller-owned and must cover their counts. RawLimit limits
// work, independently of each normalized component's distinct-key capacity.
template<unsigned RawLimit,unsigned S,unsigned B,unsigned V>
StateStatus normalize_site_state(bool verified,bool unresolved,
        const uint32_t* signals,unsigned ns,const ConfigBits* bits,unsigned nb,
        const ConfigValue* values,unsigned nv,SiteState<S,B,V>& out) {
    if (!verified || unresolved) return StateStatus::unverified;
    if (ns>RawLimit || nb>RawLimit || nv>RawLimit) return StateStatus::capacity_exhausted;
    SiteState<S,B,V> result{};
    for (unsigned i=0;i<RawLimit;++i) {
        if (i>=ns) break;
        auto status=insert_state_item<SignalOps>(result.signals,signals[i]);
        if (status!=StateStatus::ok) return status;
    }
    for (unsigned i=0;i<RawLimit;++i) {
        if (i>=nb) break;
        auto status=insert_state_item<BitsOps>(result.bits,bits[i]);
        if (status!=StateStatus::ok) return status;
    }
    for (unsigned i=0;i<RawLimit;++i) {
        if (i>=nv) break;
        auto status=insert_state_item<ValueOps>(result.values,values[i]);
        if (status!=StateStatus::ok) return status;
    }
    out=result;return StateStatus::ok;
}
} // namespace fpga_search
