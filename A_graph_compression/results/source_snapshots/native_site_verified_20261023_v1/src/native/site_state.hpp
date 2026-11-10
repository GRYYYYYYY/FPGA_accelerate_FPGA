#pragma once
// Resource IDs must be interned physical identities, never template identities.
// This transaction layer cannot infer or certify adapter/site legality.
#include <cstdint>
#include <map>
#include <set>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

namespace site_native {
using Id=uint32_t;
struct Demands {
    bool verified=false, additional_unresolved=false;
    std::vector<Id> signals;
    std::vector<std::tuple<Id,uint64_t,uint64_t>> bits;
    std::vector<std::pair<Id,Id>> values;
};
struct Normalized {
    std::set<Id> signals;
    std::map<Id,std::pair<uint64_t,uint64_t>> bits;
    std::map<Id,Id> values;
};
inline Normalized normalize(const Demands& d) {
    if (!d.verified || d.additional_unresolved) throw std::invalid_argument("unverified site requirements");
    Normalized result;
    result.signals.insert(d.signals.begin(),d.signals.end());
    for (auto [field,mask,value]:d.bits) {
        if (value & ~mask) throw std::invalid_argument("invalid bit mask/value");
        auto [old_mask,old_value]=result.bits[field];
        if ((old_value^value)&old_mask&mask) throw std::invalid_argument("contradictory configuration bits");
        result.bits[field]={old_mask|mask,old_value|value};
    }
    for (auto [field,value]:d.values) {
        auto found=result.values.find(field);
        if (found!=result.values.end() && found->second!=value) throw std::invalid_argument("contradictory categorical values");
        result.values[field]=value;
    }
    return result;
}
inline bool bits_conflict(const Normalized& a,const Normalized& b) {
    for (const auto& item:a.bits) {
        auto other=b.bits.find(item.first);
        if (other!=b.bits.end() && ((item.second.second^other->second.second)&item.second.first&other->second.first)) return true;
    }
    return false;
}
inline bool values_conflict(const Normalized& a,const Normalized& b) {
    for (const auto& item:a.values) {
        auto other=b.values.find(item.first);
        if (other!=b.values.end() && other->second!=item.second) return true;
    }
    return false;
}
class SiteState {
    std::map<Id,Id> fixed_signals;
    Normalized fixed;
    std::map<Id,Normalized> dynamic;
    bool incompatible(Id net,const Normalized& requested) const {
        for (auto resource:requested.signals) {
            auto owner=fixed_signals.find(resource);
            if (owner!=fixed_signals.end() && owner->second!=net) return true;
        }
        if (bits_conflict(requested,fixed) || values_conflict(requested,fixed)) return true;
        for (const auto& owner:dynamic) {
            if (owner.first==net) continue;
            for (auto resource:requested.signals) if (owner.second.signals.count(resource)) return true;
            if (bits_conflict(requested,owner.second) || values_conflict(requested,owner.second)) return true;
        }
        return false;
    }
public:
    SiteState(const std::vector<std::pair<Id,Id>>& signals={},const Demands& configuration=Demands{true,false,{},{},{}}) {
        if (!configuration.signals.empty()) throw std::invalid_argument("fixed signals need explicit owners");
        fixed=normalize(configuration);
        for (auto [resource,owner]:signals) {
            auto existing=fixed_signals.find(resource);
            if (existing!=fixed_signals.end() && existing->second!=owner) throw std::invalid_argument("contradictory fixed owner");
            fixed_signals[resource]=owner;
        }
    }
    bool conflicts(Id net,const Demands& requested) const {return incompatible(net,normalize(requested));}
    void replace(Id net,const Demands& requested) {
        auto normalized=normalize(requested);
        if (incompatible(net,normalized)) throw std::invalid_argument("conflicting site transaction");
        // One combined mapped object commits all three components together.
        dynamic.insert_or_assign(net,std::move(normalized));
    }
    void release(Id net) {dynamic.erase(net);}
    const std::map<Id,Normalized>& by_net() const {return dynamic;}
};
} // namespace site_native
