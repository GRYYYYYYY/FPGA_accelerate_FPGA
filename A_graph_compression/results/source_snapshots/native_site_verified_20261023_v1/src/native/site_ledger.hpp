#pragma once
#include "site_state.hpp"
#include <iterator>
#include <limits>

namespace site_native {
using ResourceKey=std::pair<unsigned,Id>; // signal, masked bits, categorical
using ResourceValue=std::pair<uint64_t,uint64_t>;
using Entries=std::map<ResourceKey,ResourceValue>;
using SiteHistory=std::map<ResourceKey,uint64_t>;
inline Entries entries(const Normalized& demands) {
    Entries result;
    for (auto r:demands.signals) result[{0,r}]={0,0};
    for (const auto& item:demands.bits) {
        if (item.second.second & ~item.second.first) throw std::invalid_argument("invalid ledger bit requirements");
        result[{1,item.first}]=item.second;
    }
    for (auto [field,value]:demands.values) result[{2,field}]={0,value};
    return result;
}
inline bool incompatible(ResourceKey key,ResourceValue a,ResourceValue b) {
    if (key.first==0) return true;
    if (key.first==1) return (a.second^b.second)&a.first&b.first;
    if (key.first==2) return a.second!=b.second;
    throw std::invalid_argument("unknown site resource kind");
}
class DemandLedger {
    std::map<ResourceKey,std::map<Id,ResourceValue>> users;
    std::map<Id,Entries> by_net;
public:
    void release(Id net) {
        auto found=by_net.find(net);if (found==by_net.end()) return;
        for (const auto& item:found->second) {
            auto owner=users.find(item.first);
            owner->second.erase(net);if (owner->second.empty()) users.erase(owner);
        }
        by_net.erase(found);
    }
    // Conflicts are intentionally retained during negotiated routing.
    void replace(Id net,const Normalized& demands) {
        auto requested=entries(demands);release(net);
        for (const auto& item:requested) users[item.first][net]=item.second;
        by_net[net]=std::move(requested);
    }
    uint64_t penalty(Id net,const Normalized& before,const Normalized& after,
                     uint64_t present,const SiteHistory& history) const {
        auto old=entries(before);uint64_t total=0;
        for (const auto& item:entries(after)) {
            auto previous=old.find(item.first);
            if (previous!=old.end() && previous->second==item.second) continue;
            uint64_t others=0;auto owners=users.find(item.first);
            if (owners!=users.end()) for (const auto& owner:owners->second)
                if (owner.first!=net && incompatible(item.first,item.second,owner.second)) ++others;
            auto h=history.find(item.first);auto past=h==history.end()?0:h->second;
            const auto maximum=std::numeric_limits<uint64_t>::max();
            if (present && others>(maximum-past)/present) throw std::invalid_argument("site penalty overflow");
            auto increment=present*others+past;
            if (increment>maximum-total) throw std::invalid_argument("site penalty sum overflow");
            total+=increment;
        }
        return total;
    }
    std::map<ResourceKey,std::set<Id>> conflicts() const {
        std::map<ResourceKey,std::set<Id>> result;
        for (const auto& item:users) {
            std::set<Id> bad;
            for (auto a=item.second.begin();a!=item.second.end();++a)
                for (auto b=std::next(a);b!=item.second.end();++b)
                    if (incompatible(item.first,a->second,b->second)) {bad.insert(a->first);bad.insert(b->first);}
            if (!bad.empty()) result[item.first]=std::move(bad);
        }
        return result;
    }
};
} // namespace site_native
