// CPU state microbenchmark. Synthetic accesses/paths, NOT a maze router.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using Clock = std::chrono::steady_clock;
double elapsed(Clock::time_point t) {
    return std::chrono::duration<double, std::milli>(Clock::now() - t).count();
}
void require(bool ok, const char* what) { if (!ok) throw std::runtime_error(what); }
uint64_t mix(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

struct SerialState {
    struct Connection {
        int netIdx = 0, sinkRnode = -1, routedIter = -1;
        bool routed = false, alternative = false;
        std::vector<int> rnodes;
        bool hasAltSinks() const { return alternative; }
    };
    // Only the occupancy mirror is modeled; static HotExpand fields are excluded.
    struct HotExpand { int ownerNet; uint16_t ownerCnt; uint8_t occCnt; };
    std::vector<int> ownerNet;
    std::vector<uint16_t> ownerCnt, occCnt;
    std::vector<std::unordered_map<int, int>*> userOverflow;
    std::vector<HotExpand> hot;
    std::vector<float> history;
    std::vector<uint8_t> dirtyMark;
    std::vector<int> dirty, shareMark;
    std::vector<Connection> connections;
    std::vector<std::vector<int>> netConns, laneShareNodes, laneShareCounts;
    std::vector<std::unordered_map<int, int>> netRefs;
    std::mutex shareMu;
    bool trackDirty = true, resident;
    int floodMark = 1, routeIteration = 1;
    static constexpr int SHARE_CAP_H = 1 << 20;
    SerialState(int nodes, int nets, bool reuse) : ownerNet(nodes, -1), ownerCnt(nodes),
        occCnt(nodes), userOverflow(nodes, nullptr), hot(nodes), history(nodes, 1.25f),
        dirtyMark(nodes), shareMark(nodes), netConns(nets),
        laneShareNodes(1, std::vector<int>(nodes)), laneShareCounts(1, std::vector<int>(nodes)),
        netRefs(nets), resident(reuse) {}
    ~SerialState() { for (auto* p : userOverflow) delete p; }
    void markDirty(int id) {
        if (!dirtyMark[id]) { dirtyMark[id] = 1; dirty.push_back(id); }
    }
    void clearDirty() { for (int id : dirty) dirtyMark[id] = 0; dirty.clear(); }
    int countConnectionsOfUser(int id, int net) const { return countUserSlot(id, net); }
    void incrementUser(int id, int net) {
        incUserSlot(id, net);
        if (resident) ++netRefs[net][id];
    }
    void decrementUser(int id, int net) {
        decUserSlot(id, net);
        if (resident) {
            auto& refs = netRefs[net];
            auto it = refs.find(id);
            require(it != refs.end() && it->second > 0, "resident reference underflow");
            if (--it->second == 0) refs.erase(it);
        }
    }
    // This file is generated from exact, hashed upstream source slices.
#include "original_state.inc"
    int gather(int idx) {
        if (!resident) return gatherShareSet(idx, 0);
        int m = 0;
        for (auto [id, count] : netRefs[connections[idx].netIdx]) {
            require(m < SHARE_CAP_H, "share buffer overflow");
            laneShareNodes[0][m] = id;
            laneShareCounts[0][m++] = count;
        }
        return m;
    }
    void verify() const {
        std::vector<std::unordered_map<int, int>> expected(ownerNet.size());
        for (const auto& c : connections) {
            if (!c.routed || c.rnodes.empty()) continue;
            int lo = 0, hi = int(c.rnodes.size());
            if (c.rnodes[0] == c.sinkRnode && !c.hasAltSinks()) { ++lo; --hi; }
            for (int i = lo; i < hi; ++i) ++expected[c.rnodes[i]][c.netIdx];
        }
        for (size_t id = 0; id < expected.size(); ++id) {
            require(occCnt[id] == expected[id].size(), "distinct-net occupancy mismatch");
            require(history[id] == 1.25f, "history overwritten");
            for (auto [net, count] : expected[id]) {
                require(countUserSlot(id, net) == count, "branch reference mismatch");
                if (resident) require(netRefs[net].at(id) == count, "resident index mismatch");
            }
        }
        if (resident) for (size_t net = 0; net < netRefs.size(); ++net)
            for (auto [id, count] : netRefs[net])
                require(expected[id][int(net)] == count, "stale resident index entry");
    }
};
using Node = SerialState::NodeDyn;

struct PagedLabels : SerialState::SparseLabels {
    double lazyPageMs = 0;
    uint64_t misses = 0;
    Node& at(int id) {
#ifdef B_STATE_DIAGNOSTIC
        if (pageEp[size_t(id) >> PBITS] != cur) {
            auto t = Clock::now();
            Node& result = SerialState::SparseLabels::at(id);
            lazyPageMs += elapsed(t); ++misses;
            return result;
        }
#endif
        return SerialState::SparseLabels::at(id);
    }
};

// Storage is reused; distances are invalidated on EVERY begin(), including a price change.
// A physical page slot belongs to only one logical page in a search. Slots recycle on begin.
struct NodeEpochPages {
    int bits, pageSize, used = 0;
    uint32_t epoch = 1, epochMax;
    std::vector<uint32_t> pageEpoch, nodeEpoch;
    std::vector<int> pageSlot;
    std::vector<Node> pool;
    NodeEpochPages(int n, int pb, uint32_t max = UINT32_MAX)
        : bits(pb), pageSize(1 << pb), epochMax(max),
          pageEpoch((n >> pb) + 2), pageSlot(pageEpoch.size(), -1),
          pool(size_t(2048) * pageSize) { nodeEpoch.resize(pool.size()); }
    void reset() {
        used = 0;
        if (epoch == epochMax) {
            std::fill(pageEpoch.begin(), pageEpoch.end(), 0);
            std::fill(nodeEpoch.begin(), nodeEpoch.end(), 0);
            epoch = 1;
        } else ++epoch;
    }
    Node& at(int id) {
        size_t p = size_t(id) >> bits;
        if (pageEpoch[p] != epoch) {
            size_t need = size_t(used + 1) * pageSize;
            if (need > pool.size()) {
                size_t cap = std::max(need, pool.size() * 2);
                pool.resize(cap); nodeEpoch.resize(cap);
            }
            pageEpoch[p] = epoch; pageSlot[p] = used++;
        }
        size_t slot = (size_t(pageSlot[p]) << bits) | (id & (pageSize - 1));
        if (nodeEpoch[slot] != epoch) { pool[slot] = Node{}; nodeEpoch[slot] = epoch; }
        return pool[slot];
    }
    void reclaim() {
        // Quiescent boundary only; no outstanding references may survive.
        std::vector<Node>().swap(pool); std::vector<uint32_t>().swap(nodeEpoch);
        std::fill(pageEpoch.begin(), pageEpoch.end(), 0); used = 0;
    }
};

struct DenseLabels {
    std::vector<Node> values;
    bool clear;
    DenseLabels(int n, bool full) : values(n), clear(full) {}
    void reset() { if (clear) std::fill(values.begin(), values.end(), Node{}); }
    Node& at(int id) { return values[id]; }
};

struct Query { int conn; std::vector<int> ids, path; };
struct Workload {
    int nodes, fanout;
    std::vector<Query> queries;
    uint64_t fingerprint = 0;
    Workload(int n, int q, int touch, int fan, bool scattered, unsigned seed)
        : nodes(n), fanout(fan) {
        std::mt19937 rng(seed);
        for (int j = 0; j < q; ++j) {
            Query item; item.conn = j % (4 * fan);
            int base = int(rng() % unsigned(n));
            for (int k = 0; k < touch; ++k) {
                int id = scattered ? int(rng() % unsigned(n)) : (base + k) % n;
                item.ids.push_back(id); fingerprint = mix(fingerprint ^ uint64_t(id));
            }
            // Paths have a shared trunk, branch resources, and two excluded endpoints.
            item.path.push_back(n - 1);
            for (int k = 0; k < 16; ++k) item.path.push_back(k);
            int branch = 64 + ((item.conn * 64 + j * 17) % (n - 128));
            for (int k = 0; k < 16; ++k) item.path.push_back(branch + k);
            item.path.push_back(n - 2);
            for (int id : item.path) fingerprint = mix(fingerprint ^ uint64_t(id));
            queries.push_back(std::move(item));
        }
    }
    void seedState(SerialState& state) const {
        for (int c = 0; c < 4 * fanout; ++c) {
            SerialState::Connection conn;
            conn.netIdx = c / fanout; conn.sinkRnode = nodes - 1; conn.routed = true;
            conn.rnodes.push_back(nodes - 1);
            for (int k = 0; k < 16; ++k) conn.rnodes.push_back(k);
            int branch = 64 + (c * 64) % (nodes - 128);
            for (int k = 0; k < 16; ++k) conn.rnodes.push_back(branch + k);
            conn.rnodes.push_back(nodes - 2);
            state.netConns[conn.netIdx].push_back(c);
            state.connections.push_back(std::move(conn));
            state.updateUsersAndPresentCongestionCost(state.connections.back());
        }
        state.clearDirty();
    }
};

struct Metrics {
    double reset = 0, label = 0, share = 0, commit = 0, rip = 0, sync = 0, wall = 0;
    uint64_t labels = 0, shares = 0, packets = 0, dirtyNodes = 0;
    void print() const {
        std::cout << "{\"reset_ms\":" << reset << ",\"label_access_including_lazy_init_ms\":" << label
          << ",\"share_prepare_ms\":" << share << ",\"commit_ms\":" << commit
          << ",\"rip_up_ms\":" << rip << ",\"sync_host_pack_ms\":" << sync
          << ",\"phase_sum_ms\":" << reset + label + share + commit + rip + sync
          << ",\"loop_wall_including_checksums_ms\":" << wall
          << ",\"label_checksum\":\"" << labels << "\",\"share_checksum\":\"" << shares
          << "\",\"packet_checksum\":\"" << packets << "\",\"packed_nodes\":" << dirtyNodes << "}";
    }
};

template<class Labels> Metrics replay(Labels& labels, SerialState& state, const Workload& work, int& seq) {
    Metrics m;
    struct Packet { int id; float normal, shared; };
    std::vector<Packet> packets;
    packets.reserve(128);
    auto all = Clock::now();
    for (const auto& query : work.queries) {
        auto& conn = state.connections[query.conn];
        auto t = Clock::now(); state.ripUp(conn); m.rip += elapsed(t);
        t = Clock::now(); labels.reset(); ++seq; m.reset += elapsed(t);
        t = Clock::now(); int count = state.gather(query.conn); m.share += elapsed(t);
        uint64_t shared = 0;
        for (int i = 0; i < count; ++i)
            shared += mix(uint64_t(state.laneShareNodes[0][i]) << 32 | unsigned(state.laneShareCounts[0][i]));
        m.shares = mix(m.shares ^ shared);
        t = Clock::now();
        int target = query.ids.back();
        labels.at(target).target = 1;
        for (int pass = 0; pass < 4; ++pass) for (int id : query.ids) {
            auto& d = labels.at(id);
            if (d.visited != seq) {
                d.lb = float(id % 257); d.upstream = float(id % 31);
                d.prev = id - 1; d.visited = seq;
            }
            m.labels += uint64_t(d.lb + d.upstream) + unsigned(d.prev + 1) + d.target;
        }
        labels.at(target).target = 0; // Mirrors original target cleanup, including stamped dense case.
        m.label += elapsed(t);
        // Path result materialization is synthetic and deliberately outside commit timing.
        conn.rnodes = query.path;
        t = Clock::now(); state.updateUsersAndPresentCongestionCost(conn); m.commit += elapsed(t);
        t = Clock::now();
        packets.clear();
        for (int id : state.dirty) {
            int occ = state.occCnt[id];
            packets.push_back({id, state.history[id] * float(1 + occ),
                              state.history[id] * float(1 + std::max(0, occ - 1))});
        }
        state.clearDirty(); m.sync += elapsed(t);
        uint64_t ph = 0;
        for (auto p : packets) ph += mix((uint64_t(p.id) << 32) ^ unsigned(p.normal * 4) ^
                                          (uint64_t(p.shared * 4) << 16));
        m.packets = mix(m.packets ^ ph); m.dirtyNodes += packets.size();
    }
    m.wall = elapsed(all);
    state.verify(); // Independent reconstruction; excluded from timing.
    return m;
}

uint64_t bytes(const DenseLabels& v) { return v.values.capacity() * sizeof(Node); }
uint64_t bytes(const SerialState::SparseLabels& v) {
    return v.pool.capacity() * sizeof(Node) + v.pageEp.capacity() * sizeof(uint32_t) +
           v.pageSlot.capacity() * sizeof(int32_t);
}
uint64_t bytes(const NodeEpochPages& v) {
    return v.pool.capacity() * sizeof(Node) + v.nodeEpoch.capacity() * sizeof(uint32_t) +
           v.pageEpoch.capacity() * sizeof(uint32_t) + v.pageSlot.capacity() * sizeof(int);
}
template<class Labels> void bench(Labels& labels, SerialState& state, const Workload& work, double allocation) {
    int seq = 0;
    auto first = replay(labels, state, work, seq);
    auto reuse = replay(labels, state, work, seq);
    std::cout << "{\"label_allocation_ms\":" << allocation << ",\"label_capacity_bytes\":" << bytes(labels)
              << ",\"trace_fingerprint\":\"" << work.fingerprint << "\",\"first\":";
    first.print(); std::cout << ",\"reuse\":"; reuse.print(); std::cout << "}\n";
}

void selfTest() {
    SerialState::SparseLabels baseline;
    baseline.initPaged(128, 2);
    NodeEpochPages candidate(128, 2, 3), other(128, 2, 3);
    // Force growth and physical-slot reassignment; no dangling references kept across at().
    baseline.pool.resize(4); candidate.pool.resize(4); candidate.nodeEpoch.resize(4);
    for (int query = 0; query < 20; ++query) {
        baseline.reset(); candidate.reset(); other.reset();
        for (int id : {3, 64, 127, 4, 32, 1}) {
            auto& a = baseline.at(id); auto& b = candidate.at(id);
            require(a.visited == 0 && b.visited == 0 && !a.target && !b.target, "stale label exposed");
            a = b = Node{7, 8, 0, -1, 99, 1};
            require(other.at(id).visited == 0, "independent contexts leaked");
        }
        require(candidate.at(3).lb == baseline.at(3).lb, "growth lost live label");
        if (query % 4 == 0) candidate.reclaim();
    }
    baseline.cur = UINT32_MAX; baseline.reset();
    require(baseline.cur == 1 && baseline.at(3).visited == 0, "original epoch wrap failed");
    // Every new search (also after price changes) must invalidate cached distances.
    candidate.at(9).lb = 100; candidate.at(9).visited = 42;
    candidate.reset(); require(candidate.at(9).visited == 0, "price-version distance survived");

    for (bool resident : {false, true}) {
        SerialState s(256, 3, resident);
        for (int net : {0, 0, 1, 2}) {
            SerialState::Connection c; c.netIdx = net; c.sinkRnode = 255;
            c.rnodes = {255, 3, 4, 254}; c.routed = true;
            int idx = int(s.connections.size()); s.connections.push_back(c);
            s.netConns[net].push_back(idx); s.updateUsersAndPresentCongestionCost(s.connections.back());
        }
        require(s.occCnt[3] == 3 && s.countUserSlot(3, 0) == 2, "distinct net versus branches");
        require(s.occCnt[255] == 0 && s.occCnt[254] == 0, "endpoint exclusion");
        for (int idx : {0, 1, 2, 3}) {
            s.ripUp(s.connections[idx]); s.connections[idx].routed = false;
            s.connections[idx].rnodes.clear(); s.verify();
        }
        require(s.occCnt[3] == 0 && s.userOverflow[3] == nullptr, "owner promotion/removal");
    }
    for (bool resident : {false, true}) {
        Workload w(1024, 120, 32, 4, true, 11);
        SerialState s(1024, 4, resident); w.seedState(s);
        for (const auto& q : w.queries) {
            auto& c = s.connections[q.conn]; s.ripUp(c);
            std::unordered_map<int, int> expected;
            for (size_t i = 0; i < s.connections.size(); ++i) {
                const auto& oc = s.connections[i];
                if (int(i) == q.conn || oc.netIdx != c.netIdx || !oc.routed) continue;
                for (size_t k = 1; k + 1 < oc.rnodes.size(); ++k) ++expected[oc.rnodes[k]];
            }
            int count = s.gather(q.conn);
            require(count == int(expected.size()), "share set size mismatch");
            for (int i = 0; i < count; ++i)
                require(expected.at(s.laneShareNodes[0][i]) == s.laneShareCounts[0][i], "share count mismatch");
            c.rnodes = q.path; s.updateUsersAndPresentCongestionCost(c); s.verify();
        }
    }
    std::cout << "{\"status\":\"passed\",\"checks\":[\"epoch_wrap\",\"pool_growth\","
      "\"quiescent_reclaim\",\"context_isolation\",\"new_search_invalidates_distance\","
      "\"distinct_net_occupancy\",\"branch_references\",\"endpoint_exclusion\","
      "\"owner_promotion\",\"history_preservation\",\"share_set_oracle\"]}\n";
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") { selfTest(); return 0; }
        require(argc == 9, "usage: state_bench variant nodes queries touches fanout pbits seed scattered");
        std::string variant = argv[1];
        int n = std::stoi(argv[2]), q = std::stoi(argv[3]), touch = std::stoi(argv[4]);
        int fan = std::stoi(argv[5]), pb = std::stoi(argv[6]), seed = std::stoi(argv[7]);
        int scattered = std::stoi(argv[8]);
        require(n >= 256 && n <= (1 << 20) && q > 0 && q < 1000000 && touch > 0 &&
                touch <= n && fan > 0 && fan <= 4096 && pb >= 2 && pb <= 12 &&
                (scattered == 0 || scattered == 1), "invalid workload bounds");
        Workload work(n, q, touch, fan, scattered, unsigned(seed));
        SerialState state(n, 4, variant == "cpu_lifetime_residency"); work.seedState(state);
        std::cout.precision(10);
        auto t = Clock::now();
        if (variant == "cpu_dense_init" || variant == "cpu_serial_stamp") {
            DenseLabels labels(n, variant == "cpu_dense_init"); double allocation = elapsed(t);
            bench(labels, state, work, allocation);
        } else if (variant == "cpu_existing_paged") {
            PagedLabels labels; labels.initPaged(n, pb); double allocation = elapsed(t);
            bench(labels, state, work, allocation);
#ifdef B_STATE_DIAGNOSTIC
            std::cerr << "{\"lazy_page_materialization_ms\":" << labels.lazyPageMs
                      << ",\"page_misses\":" << labels.misses
                      << ",\"logical_page_clear_bytes\":" << labels.misses * labels.PSIZE * sizeof(Node) << "}\n";
#endif
        } else if (variant == "cpu_paged_node_epoch" || variant == "cpu_lifetime_residency") {
            NodeEpochPages labels(n, pb); double allocation = elapsed(t);
            bench(labels, state, work, allocation);
        } else throw std::runtime_error("unknown variant");
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 2; }
}
