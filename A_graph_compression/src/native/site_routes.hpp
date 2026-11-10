#pragma once
#include "site_search.hpp"
#include "site_ledger.hpp"
#include "netlist_routes.hpp"

namespace site_native {
struct SiteRound {
    std::map<Id,std::set<Id>> conflicts;
    std::map<ResourceKey,std::set<Id>> site_conflicts;
    std::set<Id> incomplete;
    std::vector<std::vector<SearchResult>> outcomes;
};
struct SiteBatch {
    std::string status="incomplete";
    std::map<Id,netlist_native::NetRoute> routes;
    std::map<Id,Normalized> site_demands;
    std::vector<SiteRound> iterations;
};

// A software negotiation engine, not a substitute for physical readback/DRC.
// Adapters must bind physical IDs, full requirements and evidence per instance.
template<class Provider,class Semantics,class Blocked>
SiteBatch route_batch(Provider& graph,const std::vector<netlist_native::NetQuery>& queries,
                     const std::set<Id>& protected_nodes,const SiteState& fixed,
                     Semantics semantics,Blocked blocked,unsigned max_iterations,
                     uint64_t budget,uint64_t present_cap,
                     std::function<void(unsigned,size_t)> progress={}) {
    if (queries.empty() || !max_iterations || !budget || !present_cap) throw std::invalid_argument("invalid routing domain/budgets");
    std::set<Id> names;std::map<Id,Id> reserved;
    for (const auto& q:queries) {
        if (!names.insert(q.net).second) throw std::invalid_argument("duplicate query net");
        auto terminals=q.sinks;terminals.push_back(q.source);
        for (auto node:terminals) {
            if (node>=graph.node_count() || protected_nodes.count(node)) throw std::invalid_argument("invalid/protected terminal");
            auto old=reserved.find(node);
            if (old!=reserved.end() && old->second!=q.net) throw std::invalid_argument("reserved terminal conflict");
            reserved[node]=q.net;
        }
    }
    SiteBatch result;DemandLedger ledger;
    std::vector<std::set<Id>> owners(graph.node_count());
    std::map<Id,uint64_t> history;SiteHistory site_history;
    for (unsigned iteration=0;iteration<max_iterations;++iteration) {
        uint64_t present=std::min<uint64_t>(uint64_t(1)<<std::min(iteration,20u),present_cap);SiteRound round;
        for (const auto& q:queries) {
            auto old=result.routes.find(q.net);
            if (old!=result.routes.end()) for (auto node:old->second.nodes) {
                if (owners[node].erase(q.net)!=1) throw std::invalid_argument("missing old occupancy");
            }
            ledger.release(q.net);Normalized demands;
            netlist_native::NetRoute route{q.source,q.sinks,{q.source},{},false};
            std::set<Id> forbidden=protected_nodes;
            for (auto [node,owner]:reserved) if (owner!=q.net) forbidden.insert(node);
            auto targets=q.sinks;std::sort(targets.begin(),targets.end());std::vector<SearchResult> connections;
            for (auto target:targets) {
                auto connection=site_native::search(graph,route.nodes,target,payload(demands),budget,forbidden,
                    semantics,[&](Id source,const Edge& edge) {return blocked(q.net,source,edge);},
                    [&](const Normalized& requested) {return !fixed.conflicts(q.net,payload(requested));},
                    [&](Id,const Edge& edge,const Normalized& before,const Normalized& after) {
                        uint64_t occupancy=owners[edge.dst].size()-owners[edge.dst].count(q.net);
                        auto past=history.find(edge.dst);uint64_t h=past==history.end()?0:past->second;
                        uint64_t site=ledger.penalty(q.net,before,after,present,site_history);
                        const auto maximum=std::numeric_limits<uint64_t>::max();
                        if (h==maximum || occupancy>(maximum-1-h)/present) throw std::invalid_argument("node cost overflow");
                        uint64_t node=1+present*occupancy+h;
                        if (site>maximum-node) throw std::invalid_argument("combined routing cost overflow");
                        return node+site;
                    });
                if (connection.status=="found") {
                    route.edges.insert(route.edges.end(),connection.path.begin(),connection.path.end());
                    for (const auto& p:connection.path) route.nodes.insert(p.second.dst);
                    demands=connection.demands;
                }
                connections.push_back(std::move(connection));
            }
            route.complete=std::all_of(q.sinks.begin(),q.sinks.end(),[&](Id node){return route.nodes.count(node);});
            for (auto node:route.nodes) owners[node].insert(q.net);
            ledger.replace(q.net,demands);result.site_demands[q.net]=std::move(demands);
            result.routes.insert_or_assign(q.net,std::move(route));round.outcomes.push_back(std::move(connections));
            if (progress && round.outcomes.size()%50==0) progress(iteration,round.outcomes.size());
        }
        for (Id node=0;node<owners.size();++node) if (owners[node].size()>1) round.conflicts[node]=owners[node];
        round.site_conflicts=ledger.conflicts();
        for (const auto& r:result.routes) if (!r.second.complete) round.incomplete.insert(r.first);
        result.iterations.push_back(std::move(round));const auto& last=result.iterations.back();
        if (progress) progress(iteration,queries.size());
        if (last.conflicts.empty() && last.site_conflicts.empty()) {
            if (last.incomplete.empty()) result.status="routed";
            break;
        }
        for (const auto& c:last.conflicts) {
            uint64_t delta=c.second.size()-1;auto& h=history[c.first];
            if (h>std::numeric_limits<uint64_t>::max()-delta) throw std::invalid_argument("node history overflow");
            h+=delta;
        }
        for (const auto& c:last.site_conflicts) {
            uint64_t delta=c.second.size()-1;auto& h=site_history[c.first];
            if (h>std::numeric_limits<uint64_t>::max()-delta) throw std::invalid_argument("site history overflow");
            h+=delta;
        }
    }
    return result;
}
} // namespace site_native
