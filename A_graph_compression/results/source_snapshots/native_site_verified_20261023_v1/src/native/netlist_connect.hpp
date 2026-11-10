#pragma once
// Canonical-node search component. Site configuration labels are a separate layer.
#include "packed_graph.hpp"
#include <functional>
#include <limits>
#include <queue>
#include <set>

namespace netlist_native {
struct Connection {
    std::string status = "no_path";
    uint64_t cost = 0, expanded = 0, examined = 0, fetched = 0, blocked = 0;
    std::vector<std::pair<uint32_t, Edge>> path;
    std::set<uint32_t> unknown;
};

// IDs must preserve the reference search's canonical-name ordering for ties.
// blocked() includes protected nodes/PIPs, terminal reservations and excluded/test
// attributes. step_cost() includes hop, negotiated occupancy and history costs.
template<class Provider, class Blocked, class StepCost>
Connection connect(Provider& graph, const std::set<uint32_t>& tree,
                   uint32_t target, uint64_t budget,
                   const std::set<uint32_t>& protected_nodes,
                   Blocked blocked, StepCost step_cost) {
    Connection result;
    require(!tree.empty() && target < graph.node_count(), "invalid connection terminals");
    for (auto node : tree) require(node < graph.node_count(), "tree node outside graph");
    if (tree.count(target)) { result.status = "found"; return result; }
    require(!protected_nodes.count(target), "protected target");
    for (auto node : tree) require(!protected_nodes.count(node), "protected tree");
    using Item = std::pair<uint64_t, uint32_t>;
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> queue;
    const auto infinity = std::numeric_limits<uint64_t>::max();
    std::vector<uint64_t> distance(graph.node_count(), infinity);
    std::vector<uint32_t> parent(graph.node_count());
    std::vector<Edge> parent_edge(graph.node_count()), edges;
    for (auto node : tree) { distance[node] = 0; queue.emplace(0, node); }
    while (!queue.empty()) {
        auto [cost, node] = queue.top(); queue.pop();
        if (cost != distance[node]) continue;
        if (node == target) { result.status = "found"; result.cost = cost; break; }
        if (result.expanded >= budget) { result.status = "budget_exhausted"; break; }
        if (!graph.neighbors(node, edges)) { result.unknown.insert(node); continue; }
        ++result.expanded; result.fetched += edges.size();
        for (const auto& edge : edges) {
            ++result.examined;
            require(edge.dst < graph.node_count(), "edge destination outside graph");
            if (tree.count(edge.dst) || protected_nodes.count(edge.dst) || blocked(node, edge)) {
                ++result.blocked; continue;
            }
            const uint64_t step = step_cost(node, edge);
            require(step > 0 && step < infinity - cost, "invalid or overflowing edge cost");
            const auto next = cost + step;
            if (next < distance[edge.dst]) {
                distance[edge.dst] = next; parent[edge.dst] = node;
                parent_edge[edge.dst] = edge; queue.emplace(next, edge.dst);
            }
        }
    }
    if (result.status == "no_path" && !result.unknown.empty()) result.status = "incomplete_domain";
    if (result.status == "found") {
        for (auto node = target; !tree.count(node); node = parent[node])
            result.path.emplace_back(parent[node], parent_edge[node]);
        std::reverse(result.path.begin(), result.path.end());
    }
    return result;
}
} // namespace netlist_native
