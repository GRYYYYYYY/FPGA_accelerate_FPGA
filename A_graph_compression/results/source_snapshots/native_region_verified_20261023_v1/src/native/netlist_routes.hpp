#pragma once
#include "netlist_connect.hpp"

namespace netlist_native {
struct NetQuery { uint32_t net, source; std::vector<uint32_t> sinks; };
struct NetRoute {
    uint32_t source;
    std::vector<uint32_t> sinks;
    std::set<uint32_t> nodes;
    std::vector<std::pair<uint32_t, Edge>> edges;
    bool complete = false;
};
struct RoutingRound {
    uint64_t present;
    std::map<uint32_t, std::set<uint32_t>> conflicts;
    std::set<uint32_t> incomplete, unknown;
    std::vector<std::vector<Connection>> outcomes;
};
struct RoutingBatch {
    std::string status = "incomplete";
    std::map<uint32_t, NetRoute> routes;
    std::vector<RoutingRound> iterations;
    std::map<uint32_t, uint64_t> history;
};

// Canonical-node negotiation only. Callers must additionally enforce all
// physical/site semantics; this is not a physical legality certificate.
template<class Provider, class Blocked>
RoutingBatch route_batch(Provider& graph, const std::vector<NetQuery>& queries,
                         const std::set<uint32_t>& protected_nodes,
                         Blocked blocked, unsigned max_iterations,
                         uint64_t budget, uint64_t present_cap,
                         std::function<void(unsigned,size_t)> progress = {}) {
    require(!queries.empty() && max_iterations && budget && present_cap, "invalid routing budgets/queries");
    std::set<uint32_t> names;
    std::map<uint32_t, uint32_t> reserved;
    for (const auto& q:queries) {
        require(names.insert(q.net).second, "duplicate net query");
        auto terminals=q.sinks; terminals.push_back(q.source);
        for (auto node:terminals) {
            require(node<graph.node_count() && !protected_nodes.count(node), "invalid/protected terminal");
            auto it=reserved.find(node);
            require(it==reserved.end() || it->second==q.net, "conflicting reserved terminal");
            reserved[node]=q.net;
        }
    }
    RoutingBatch result;
    std::vector<std::set<uint32_t>> owners(graph.node_count());
    for (unsigned iteration=0;iteration<max_iterations;++iteration) {
        RoutingRound round;
        round.present=std::min<uint64_t>(uint64_t(1)<<std::min(iteration,20u),present_cap);
        for (const auto& q:queries) {
            auto old=result.routes.find(q.net);
            if (old!=result.routes.end())
                for (auto node:old->second.nodes) require(owners[node].erase(q.net)==1, "missing previous occupancy");
            NetRoute route{q.source,q.sinks,{q.source},{},false};
            std::vector<Connection> connections;
            auto sinks=q.sinks; std::sort(sinks.begin(),sinks.end());
            for (auto target:sinks) {
                auto connection=connect(graph,route.nodes,target,budget,protected_nodes,
                    [&](uint32_t source,const Edge& edge) {
                        auto it=reserved.find(edge.dst);
                        return (it!=reserved.end() && it->second!=q.net) || blocked(q.net,source,edge);
                    }, [&](uint32_t,const Edge& edge) {
                        auto occupancy=owners[edge.dst].size()-owners[edge.dst].count(q.net);
                        auto it=result.history.find(edge.dst);
                        const auto history=it==result.history.end()?0:it->second;
                        const auto limit=std::numeric_limits<uint64_t>::max();
                        require(history<limit && occupancy<=(limit-1-history)/round.present,"routing cost overflow");
                        return uint64_t(1)+round.present*occupancy+history;
                    });
                round.unknown.insert(connection.unknown.begin(),connection.unknown.end());
                if (connection.status=="found") {
                    route.edges.insert(route.edges.end(),connection.path.begin(),connection.path.end());
                    for (const auto& p:connection.path) route.nodes.insert(p.second.dst);
                }
                connections.push_back(std::move(connection));
            }
            route.complete=std::all_of(q.sinks.begin(),q.sinks.end(),[&](uint32_t n){return route.nodes.count(n);});
            for (auto node:route.nodes) owners[node].insert(q.net);
            result.routes.insert_or_assign(q.net,std::move(route));
            round.outcomes.push_back(std::move(connections));
            if (progress && round.outcomes.size()%50==0) progress(iteration,round.outcomes.size());
        }
        for (uint32_t node=0;node<owners.size();++node)
            if (owners[node].size()>1) round.conflicts[node]=owners[node];
        for (const auto& item:result.routes) if (!item.second.complete) round.incomplete.insert(item.first);
        result.iterations.push_back(std::move(round));
        if (progress) progress(iteration,queries.size());
        const auto& last=result.iterations.back();
        if (last.conflicts.empty()) {
            if (last.incomplete.empty()) result.status="routed";
            break;
        }
        for (const auto& item:last.conflicts) {
            auto& history=result.history[item.first]; const uint64_t increment=item.second.size()-1;
            require(history<=std::numeric_limits<uint64_t>::max()-increment,"history overflow");
            history+=increment;
        }
    }
    return result;
}
} // namespace netlist_native
