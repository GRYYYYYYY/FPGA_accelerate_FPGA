#pragma once
// Exact product-state search component; adapters supply evidenced site demands.
#include "packed_graph.hpp"
#include "site_state.hpp"
#include <limits>
#include <optional>
#include <queue>
#include <type_traits>

namespace site_native {
struct EdgeSemantics {bool pseudo=false;std::optional<Demands> demands;};
inline Demands payload(const Normalized& state) {
    Demands d;d.verified=true;d.signals.assign(state.signals.begin(),state.signals.end());
    for (const auto& item:state.bits) d.bits.emplace_back(item.first,item.second.first,item.second.second);
    for (auto item:state.values) d.values.push_back(item);
    return d;
}
inline Normalized merge(const Normalized& a,const Normalized& b) {
    Normalized result=a;result.signals.insert(b.signals.begin(),b.signals.end());
    for (const auto& item:b.bits) {
        auto& old=result.bits[item.first];auto [mask,value]=item.second;
        if ((old.second^value)&old.first&mask) throw std::invalid_argument("incompatible path bits");
        old={old.first|mask,old.second|value};
    }
    for (auto [field,value]:b.values) {
        auto old=result.values.find(field);
        if (old!=result.values.end() && old->second!=value) throw std::invalid_argument("incompatible path categories");
        result.values[field]=value;
    }
    return result;
}
struct SearchResult {
    std::string status="no_path";
    uint64_t cost=0,expanded=0,blocked=0;
    Normalized demands;
    std::vector<std::pair<Id,Edge>> path;
    std::set<Id> unknown_sources;
    std::set<std::pair<Id,Id>> unknown_pips;
};
struct SearchKey {Id node;Normalized demands;};
struct SearchKeyLess {
    bool operator()(const SearchKey& a,const SearchKey& b) const {
        if (a.node!=b.node) return a.node<b.node;
        return std::tie(a.demands.signals,a.demands.bits,a.demands.values)
             < std::tie(b.demands.signals,b.demands.bits,b.demands.values);
    }
};

// roots/resource IDs must follow the reference's lexical ordering. Neighbor
// order is provider-owned; serial tie-breaking preserves that order exactly.
// This native hop/congestion implementation accepts positive integer costs.
template<class Provider,class Semantics,class Blocked,class Compatible,class Cost>
SearchResult search(Provider& graph,const std::set<Id>& roots,Id target,
                    const Demands& initial,uint64_t budget,const std::set<Id>& blocked_nodes,
                    Semantics semantics,Blocked blocked,Compatible compatible,Cost step_cost) {
    if (!budget || roots.empty() || target>=graph.node_count() || blocked_nodes.count(target))
        throw std::invalid_argument("invalid search domain/budget");
    auto initial_state=normalize(initial);
    if (!compatible(initial_state)) throw std::invalid_argument("initial site state conflicts");
    struct Label {SearchKey key;uint64_t cost;size_t parent;Edge edge;bool root;};
    std::vector<Label> labels;
    std::map<SearchKey,size_t,SearchKeyLess> ids;
    using Entry=std::tuple<uint64_t,uint64_t,size_t>;
    std::priority_queue<Entry,std::vector<Entry>,std::greater<Entry>> queue;
    uint64_t serial=0;
    for (auto root:roots) {
        if (root>=graph.node_count() || blocked_nodes.count(root)) throw std::invalid_argument("protected/invalid root");
        SearchKey key{root,initial_state};size_t index=labels.size();ids.emplace(key,index);
        labels.push_back({key,0,0,{},true});queue.emplace(0,serial++,index);
    }
    SearchResult result;std::vector<Edge> edges;
    while (!queue.empty()) {
        auto [cost,sequence,index]=queue.top();queue.pop();(void)sequence;
        if (cost!=labels[index].cost) continue;
        // Copy before label-vector growth; later insertions must not invalidate it.
        const auto current=labels[index].key;
        if (current.node==target) {
            result.status="found";result.cost=cost;result.demands=current.demands;
            for (size_t cursor=index;!labels[cursor].root;cursor=labels[cursor].parent)
                result.path.emplace_back(labels[labels[cursor].parent].key.node,labels[cursor].edge);
            std::reverse(result.path.begin(),result.path.end());return result;
        }
        if (result.expanded>=budget) {result.status="budget_exhausted";return result;}
        if (!graph.neighbors(current.node,edges)) {result.unknown_sources.insert(current.node);continue;}
        ++result.expanded;
        for (const auto& edge:edges) {
            if (edge.dst>=graph.node_count()) throw std::invalid_argument("invalid edge destination");
            if (roots.count(edge.dst) || blocked_nodes.count(edge.dst) || blocked(current.node,edge)) {++result.blocked;continue;}
            auto requirement=semantics(current.node,edge);Normalized additions;
            if (requirement.demands) additions=normalize(*requirement.demands);
            else if (requirement.pseudo) {result.unknown_pips.emplace(edge.tile,edge.pip);continue;}
            Normalized merged;
            try {merged=merge(current.demands,additions);}
            catch (const std::invalid_argument&) {++result.blocked;continue;}
            if (!compatible(merged)) {++result.blocked;continue;}
            auto step=step_cost(current.node,edge,current.demands,merged);
            static_assert(std::is_integral_v<decltype(step)>,"native search requires integer costs");
            if constexpr (std::is_signed_v<decltype(step)>)
                if (step<=0) throw std::invalid_argument("nonpositive edge cost");
            uint64_t positive=uint64_t(step);
            if (!positive || positive>=std::numeric_limits<uint64_t>::max()-cost) throw std::invalid_argument("invalid/overflowing edge cost");
            auto following=cost+positive;SearchKey key{edge.dst,std::move(merged)};
            auto found=ids.find(key);size_t next;
            if (found==ids.end()) {
                next=labels.size();ids.emplace(key,next);labels.push_back({std::move(key),following,index,edge,false});
            } else {
                next=found->second;if (following>=labels[next].cost) continue;
                labels[next].cost=following;labels[next].parent=index;labels[next].edge=edge;
            }
            queue.emplace(following,serial++,next);
        }
    }
    if (!result.unknown_pips.empty()) result.status="unknown_site_semantics";
    else if (!result.unknown_sources.empty()) result.status="incomplete_domain";
    return result;
}
} // namespace site_native
