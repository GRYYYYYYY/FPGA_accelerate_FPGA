#include "../src/native/netlist_connect.hpp"
struct Fixture {
    std::vector<std::vector<Edge>> rows;
    std::vector<unsigned> known;
    size_t node_count() const { return rows.size(); }
    bool neighbors(uint32_t n, std::vector<Edge>& out) {
        if (!known[n]) return false;
        out = rows[n]; return true;
    }
};
int main() { try {
    unsigned n, m, target, budget, present, count;
    std::cin >> n >> m >> target >> budget >> present;
    Fixture graph; graph.rows.resize(n); graph.known.resize(n);
    std::vector<unsigned> occupancy(n), history(n), reserved(n);
    std::set<uint32_t> protected_nodes, blocked_pips, tree;
    for (unsigned i=0, protection; i<n; ++i) {
        std::cin >> graph.known[i] >> occupancy[i] >> history[i] >> protection >> reserved[i];
        if (protection) protected_nodes.insert(i);
    }
    for (unsigned i=0, src, dst, pip, flag; i<m; ++i) {
        std::cin >> src >> dst >> pip >> flag;
        graph.rows[src].push_back(Edge{dst,0,pip,0,0,0,0});
        if (flag) blocked_pips.insert(pip);
    }
    std::cin >> count;
    for (unsigned i=0, node; i<count; ++i) { std::cin >> node; tree.insert(node); }
    require(bool(std::cin), "invalid fixture");
    auto r = netlist_native::connect(graph, tree, target, budget, protected_nodes,
        [&](uint32_t, const Edge& e) { return blocked_pips.count(e.pip) || reserved[e.dst]; },
        [&](uint32_t, const Edge& e) { return uint64_t(1)+uint64_t(present)*occupancy[e.dst]+history[e.dst]; });
    std::cout << "{\"status\":\"" << r.status << "\",\"cost\":";
    if (r.status=="found") std::cout << r.cost; else std::cout << "null";
    std::cout << ",\"expanded\":" << r.expanded << ",\"examined\":" << r.examined
              << ",\"fetched\":" << r.fetched << ",\"blocked_edges\":" << r.blocked << ",\"path\":[";
    bool first=true;
    for (auto p:r.path) { if (!first) std::cout << ','; first=false; std::cout << p.second.pip; }
    std::cout << "],\"unknown_sources\":["; first=true;
    for (auto node:r.unknown) { if (!first) std::cout << ','; first=false; std::cout << node; }
    std::cout << "]}\n";
    return 0;
} catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 1; } }
