// Pure-C++ port of RapidWright's RWRoute / PartialRouter routing loop
// (non-timing-driven, UltraScale+). Reads a ".rrt" problem produced by the Java
// RWRouteCppProblemExport, runs the negotiated-congestion maze router, and writes a
// ".result" (per-connection rnode paths) consumed by the Java RWRouteCppImport.
//
// Names mirror com.xilinx.rapidwright.rwroute.* where practical.
#include "BinIO.hpp"
#include "RouteNodeType.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <queue>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#if defined(__linux__)
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <sched.h>
#endif

#ifdef WITH_CUDA
#include "gpu_bbox.hpp"    // Track D / D1: GPU coarse-grid corridor solver
#include "gpu_route.hpp"   // GPU detailed-routing engine (G0+: resident graph, frontier routing)
#endif

#include "DeviceModel.hpp"   // pure C++ (no JNI dep); standalone needs it for --gen-dmc

#ifdef WITH_JNI
#include <jni.h>
#include <cstdlib>
#endif

#include "real_profile.hpp"
#include "real_trace.hpp"
#define TLD(id) bTLD((id), __LINE__)
namespace rw = com::xilinx::rapidwright::rwroute;
using rw::RouteNodeType;

// ----------------------------------------------------------------------------- config
struct Config {
    int maxIterations;
    int boundingBoxExtensionX, boundingBoxExtensionY;
    bool enlargeBoundingBox;
    int extensionXIncrement, extensionYIncrement;
    bool useBoundingBox;
    float wirelengthWeight, shareExponent;
    float initialPresentCongestionFactor, presentCongestionMultiplier;
    float historicalCongestionFactor, maxPresentCongestionFactor;
    int maxDetourToSnapBackToPrevLagunaColumn;
    int superLongLineLengthInTiles;
    bool useUTurnNodes;
};

// --------------------------------------------------------------------------- RouteNode
// Per-node static attributes, split by ACCESS PATTERN for cache density (Track A2):
//  - NodeStatic = HOT: read on the maze-search hot path (cost / accessibility / adjacency). Kept dense
//    (~32B) so ~2 nodes share a 64B line. `arcLockedInit` doubles as the read-only arc-locked flag (it
//    never changes after init), so it lives here -- which lets NodeDyn become pure per-connection scratch.
//  - NodeCold = touched only at load / output / sort / init; kept out of the hot array.
struct NodeStatic {
    int tileAddr;        // hot: "same tile" checks in graph/sink accessibility
    int childStart, childCount;
    float baseCost;
    int16_t beginX, beginY, endX, endY, length;
    bool isLaguna, isPinfeed, pinfeedLeadsToLaguna, preserved, isPinbounce, arcLockedInit;
};
struct NodeCold {
    int wireIndex;       // key construction (with tileAddr) / output
    int hashCode;        // connection sort / output
    int prevInit;        // prev node id captured at init (existing-route), or -1
    RouteNodeType type;  // export-time type, consumed once to seed the runtime type[] array
    bool createdAtInit;
};
struct ChildAttrs { NodeStatic hot; NodeCold cold; };  // unpackChild result (hot+cold pair)

// HotExpand: per-node bundle read on every child expansion (~28B, one cache line). Static attrs + occupancy
// owner-slot mirrored here so exploreAndExpand/evaluateCostAndPush stop chasing ns/type/occCnt/ownerNet/ownerCnt.
enum HotFlag : uint8_t { HF_LAGUNA = 1, HF_PINFEED = 2, HF_PF_LAG = 4, HF_PINBOUNCE = 8, HF_PRESERVED = 16 };
struct HotExpand {
    float baseCost;
    int32_t tileAddr;
    int32_t ownerNet;                       // -1 = empty
    int16_t beginX, beginY, endX, endY, length;
    uint16_t ownerCnt;
    uint8_t type;                           // RouteNodeType
    uint8_t occCnt;                         // mirror of occCnt (capped 255 for presentCong table)
    uint8_t flags;
};
static_assert(sizeof(HotExpand) <= 32, "HotExpand must fit one cache line");

// Env-knob helpers (Track B sweeps: override params without recompiling Java).
static inline float rwEnvF(const char* k, float d) { const char* e = std::getenv(k); return e ? (float) std::atof(e) : d; }
static inline int   rwEnvI(const char* k, int d)   { const char* e = std::getenv(k); return e ? std::atoi(e) : d; }
// Global thread budget (RW_MAX_THREADS, default 48): single cap consulted by every parallel phase.
// Raised from the historical hard 32 on user request (target environment allows 48); phase-level
// worker counts still min() against hardware_concurrency at their call sites.
static inline int rwMaxThreads() { static const int v = std::max(1, rwEnvI("RW_MAX_THREADS", 48)); return v; }

static constexpr short CAPACITY = 1;

struct Router {
    Config cfg;
    bool hasLaguna = false;
    int superLongLineLength = 60;
    std::vector<int> intYToSLRIndex;
    std::vector<int> nextLagunaColumn, prevLagunaColumn;
    std::vector<uint8_t> intYToNorthboundLaguna;

    // static node data
    std::vector<NodeStatic> ns;          // HOT per-node attrs (maze-search path)
    std::vector<NodeCold> nc;            // COLD per-node attrs (parallel to ns; load/output/sort/init)
    std::vector<int> childIds;  // flat

    // mutable per-node routing state. The HOT per-expansion fields are folded into ONE struct (AoS) so a
    // node's routing state lives in ~1 cache line instead of ~7 scattered SoA arrays — the maze search is
    // random access over millions of nodes (cache-miss bound). Mirrors Java's RouteNode (fields together).
    struct NodeDyn {       // pure per-connection scratch (+ cross-iteration hist); rewritten every push
        float lb;          // lowerBoundTotalPathCost
        float upstream;    // upstreamPathCost
        float hist;        // historicalCongestionCost (1.0 default)
        int   prev;        // prev node id (-1 default)
        int   visited;     // per-connection sequence guard (0 default)
        uint8_t target;    // isTargetFlag
    };
    std::vector<NodeDyn> dyn;
    std::vector<RouteNodeType> type;   // copy of ns.type (kept separate; mutable for exclusive sinks)
    std::vector<uint8_t> created;
    // Flat owner-slot per node: ownerNet (-1=empty) + ownerCnt for O(1) countConnectionsOfUser on the
    // common case (occCnt<=1, legal routing). Multi-net (overuse) nodes spill to userOverflow map.
    std::vector<int> ownerNet;
    std::vector<uint16_t> ownerCnt;
    std::vector<std::unordered_map<int,int>*> userOverflow;
    // A5: flat per-node occupancy = #distinct nets using the node, kept in sync on inc/dec so the HOT
    // getOccupancy() is a single array read instead of pointer-chase + hashmap.
    std::vector<uint16_t> occCnt;
    // HotExpand read bundle (RW_HOTEXPAND=1): one load covers type/coords/cost/occ/sharing for child expansion.
    std::vector<HotExpand> hot;
    bool useHotExpand = rwEnvI("RW_HOTEXPAND", 1) != 0;
    // children cache (lazy)
    std::vector<std::vector<int>*> childrenCache;

    // ---- lazy (JNI) device source: nodes interned on demand, raw adjacency pulled per node ----
    bool doPrefetch = rwEnvI("RW_PREFETCH", 1) != 0;   // §prefetch child node data in the maze search (default on)
    bool lazy = false;
    bool flatGraphBuilt = false;   // lazy path: flat childIds CSR materialized (from rawChildrenStore) for GPU upload
    bool floodDeferLazy = false;   // lazy path: defer the GPU flood graph upload until after iter-1 interns it
    std::function<void(long, std::vector<int>&)> fetchChildrenPacked;  // key -> [cnt, (11 ints)*cnt]
    std::vector<uint8_t> rawFetched;
    std::vector<std::vector<int>> rawChildrenStore;
    double jniDeviceSecs = 0.0; long jniDeviceCalls = 0;  // instrumentation: time in JNI device pulls
    std::unordered_set<long long> preserveSet;  // design-specific preserved node keys (for C++ device model)
    std::vector<int> fetchPacked, fetchRaw;     // reused per-getChildren buffers (avoid per-call alloc)
    // bloom filter over preserveSet keys: cheap negative pre-check before the hash set lookup
    std::vector<uint64_t> bloomBits; uint64_t bloomMask = 0; bool preserveReady = false;
    void buildBloom() {
        size_t bits = 64; while (bits < preserveSet.size() * 16 + 64) bits <<= 1;
        bloomMask = bits - 1; bloomBits.assign(bits / 64, 0);
        for (long long k : preserveSet) {
            uint64_t h = (uint64_t) k * 0x9E3779B97F4A7C15ull;
            uint64_t h1 = h & bloomMask, h2 = (h >> 29) & bloomMask;
            bloomBits[h1 >> 6] |= (1ull << (h1 & 63)); bloomBits[h2 >> 6] |= (1ull << (h2 & 63));
        }
        preserveReady = true;
    }
    inline bool maybePreserved(long long k) const {
        uint64_t h = (uint64_t) k * 0x9E3779B97F4A7C15ull;
        uint64_t h1 = h & bloomMask, h2 = (h >> 29) & bloomMask;
        return ((bloomBits[h1 >> 6] >> (h1 & 63)) & 1) && ((bloomBits[h2 >> 6] >> (h2 & 63)) & 1);
    }

    float presentCongestionCosts[256];

    // nets / connections
    struct NetWrapper {
        float xCenter, yCenter;
        int doubleHpwl;
        int connectionsSize;
        int sourceRnode;
    };
    struct Connection {
        int connId, netIdx;
        int sourceRnode, sinkRnode;
        std::vector<int> altSinks;
        short xMinBB, xMaxBB, yMinBB, yMaxBB;
        short hpwl;
        bool crossSLRnorth, crossSLRsouth;
        bool routedAtInit;
        // mutable
        std::vector<int> rnodes;       // current route (sink->source); the initial route is loaded
                                       // straight in here (A3) -- no separate permanent initRnodes
        bool routed = false;
        bool abandoned = false;
        int routedIter = -1;           // routeIteration at the last occupancy commit (incremental updateCost)
        bool isCrossSLR() const { return crossSLRnorth || crossSLRsouth; }
        bool hasAltSinks() const { return !altSinks.empty(); }
    };
    std::vector<NetWrapper> nets;
    std::vector<Connection> connections;
    // Lock-free open-addressing key->id map (fixed power-of-2 capacity; no rehash while routing in
    // parallel): a writer claims a slot by CAS on the key, creates the node, then publishes id+1 into
    // the value slot with release; readers are pure loads (no RMW), so lookups scale across workers.
    // Growth happens only at serial points (kiGrow: reset + reinsert, keys recomputable via keyOf).
    struct KIMap {
        std::atomic<uint64_t>* keys = nullptr;
        std::atomic<int>* vals = nullptr;      // id+1; 0 = empty/claimed-unpublished
        size_t cap = 0, mask = 0;
        void reset(size_t want) {
            drop();
            cap = 1; while (cap < want) cap <<= 1;
            mask = cap - 1;
            keys = (std::atomic<uint64_t>*) mmap(nullptr, cap * sizeof(uint64_t), PROT_READ | PROT_WRITE,
                                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            vals = (std::atomic<int>*) mmap(nullptr, cap * sizeof(int), PROT_READ | PROT_WRITE,
                                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        }
        void drop() {
            if (keys) { munmap((void*) keys, cap * sizeof(uint64_t)); keys = nullptr; }
            if (vals) { munmap((void*) vals, cap * sizeof(int)); vals = nullptr; }
        }
        inline size_t home(long long key) const {
            uint64_t h = ((uint64_t) key + 1) * 0x9E3779B97F4A7C15ull;
            return (size_t)(h ^ (h >> 31)) & mask;
        }
        inline int find(long long key) const {   // -1 if absent; spins out a racing publisher
            if (!keys) return -1;
            const uint64_t want = (uint64_t) key + 1;
            for (size_t i = home(key);; i = (i + 1) & mask) {
                uint64_t k = keys[i].load(std::memory_order_acquire);
                if (k == 0) return -1;
                if (k == want) {
                    int v;
                    while ((v = vals[i].load(std::memory_order_acquire)) == 0) {}
                    return v - 1;
                }
            }
        }
        inline void putSerial(long long key, int id) {   // load/rehash time only (single-threaded)
            const uint64_t want = (uint64_t) key + 1;
            for (size_t i = home(key);; i = (i + 1) & mask) {
                uint64_t k = keys[i].load(std::memory_order_relaxed);
                if (k == want) { vals[i].store(id + 1, std::memory_order_relaxed); return; }
                if (k == 0) {
                    keys[i].store(want, std::memory_order_relaxed);
                    vals[i].store(id + 1, std::memory_order_relaxed);
                    return;
                }
            }
        }
        inline bool claim(long long key) {   // marker use (vals unused): true iff WE newly claimed key
            const uint64_t want = (uint64_t) key + 1;
            size_t probes = 0;
            for (size_t i = home(key);;) {
                uint64_t k = keys[i].load(std::memory_order_acquire);
                if (k == want) return false;
                if (k == 0) {
                    uint64_t exp = 0;
                    if (keys[i].compare_exchange_strong(exp, want, std::memory_order_acq_rel)) return true;
                    continue;
                }
                i = (i + 1) & mask;
                if (++probes > cap) { std::fprintf(stderr, "FATAL: KIMap overfull (cap=%zu)\n", cap); std::abort(); }
            }
        }
        inline void putParallel(long long key, int id) {   // distinct keys per caller (bulk fill)
            const uint64_t want = (uint64_t) key + 1;
            for (size_t i = home(key);;) {
                uint64_t k = keys[i].load(std::memory_order_acquire);
                if (k == want) { vals[i].store(id + 1, std::memory_order_release); return; }
                if (k == 0) {
                    uint64_t exp = 0;
                    if (keys[i].compare_exchange_strong(exp, want, std::memory_order_acq_rel)) {
                        vals[i].store(id + 1, std::memory_order_release);
                        return;
                    }
                    continue;
                }
                i = (i + 1) & mask;
            }
        }
    };
    KIMap keyToId;                       // (tileAddr<<20|wire) -> node id
    std::atomic<int> nodeCountA{0};      // published node count (readers see a fully-built prefix)
    std::atomic<bool> internLock{false}; // guards the node-array appends during lazy interning
    bool fetchParSafe = false;           // fetchChildrenPacked callable from workers (compact device: read-only)
    std::vector<int> sortedIndirect;     // indices into connections
    std::vector<int> indirectAll;        // indices into connections (full set, for output)

    float presentCongestionFactor, historicalCongestionFactor, wlWeight;
    int routeIteration = 0;
    long connectionsRouted = 0;
    bool dumpMode = false;               // when set, push() records the A* explored nodes (for visualization)
    std::vector<int> dumpExplored;
    std::atomic<long long> totalPushes{0};   // instrumentation: total nodes pushed to the heap (search fan-out)
    static thread_local long long tl_pushes; // per-thread accumulator (flushed into totalPushes; avoids a hot atomic)
    // Directedness: multiplier on the A* distance-to-sink heuristic. >1 = weighted/inadmissible A* that
    // heads more straight at the sink (the robust form of "monotone" search) -> fewer explored nodes,
    // at the cost of slightly longer paths. 1.0 = the exact RWRoute heuristic. Env RW_DIRECT.
    float directedness = rwEnvF("RW_DIRECT", 1.0f);
    float batchDirect = rwEnvF("RW_BATCH_DIRECT", 1.0f);   // extra directedness for batch-CREW searches only
                                                       // (global RW_DIRECT verdict was negative -- congestion
                                                       // feedback; crew commits pass the rollback filter and
                                                       // publisher requeues stay exact, so retry surgically)
    std::vector<uint8_t> overUsed;       // per-node membership flag in overUsedRnodes
    std::vector<int> overUsedList;       // ids currently overused
    long long currentTotalOveruse = 0;   // sum of node overuse at end of last updateCost (GRoute progress factor)

    // ---- §5 measurement 1: per-iteration search VOLUME (pops = heap polls = nodes expanded) -------
    // Resolves "is the per-connection cost blow-up in congested iters PURE volume growth, or volume x
    // rising per-pop cost?" We time routeIndirectConnections() alone (search only, no updateCost/rip-up
    // overhead) and count pops, so ns/pop is clean. Env RW_MEASURE_POPS=1 (the pops++ itself is free).
    bool      measurePops = rwEnvI("RW_MEASURE_POPS", 0) != 0;
    std::atomic<long long> iterPops{0};   // total pops (node expansions) this iteration (1 add per SEARCH)
    std::atomic<long long> iterMaxPops{0};// max pops on a single connection this iteration
    std::atomic<long long> iterPopHist[28] = {}; // log2 histogram of per-connection pops (bucket b = [2^b,2^(b+1)))
    // §GPU-flood supply-side: for "monster" searches (pops >= frontierMin), profile the FRONTIER (heap)
    // width per pop. GPU single-connection flood parallelism ~= average wavefront width; if the frontier
    // stays narrow even when a search floods 2M nodes, GPU flooding is starved regardless of kernel quality.
    long long frontierMin = rwEnvI("RW_FRONTIER_MIN", 50000);
    int priceVarIter = rwEnvI("RW_PRICEVAR", -1);   // §coarse-h capture: at this iter, dump per-tile priced-cost variance then exit
    int floodProtoIter = rwEnvI("RW_FLOODPROTO", -1);  // §GPU-flood kernel prototype: at this iter, shadow-compare CPU A* vs GPU flood
    // §alpha probe (batch-presearch gate): presearch a sample at iter-START prices, then after the iteration
    // check how many presearched paths are still valid at commit-time prices. High alpha => batch-presearch
    // (compute paths on GPU ahead, revalidate on commit) can shrink the <4k masses. Env RW_ALPHA_PROBE=<iter>.
    int alphaProbeIter = rwEnvI("RW_ALPHA_PROBE", -1);
    bool alphaDone = false;
    std::vector<int> alphaSample;
    std::vector<std::vector<int>> alphaPathStart;
    std::vector<int> alphaSlot;        // connIdx -> sample index (-1 if not sampled)
    std::vector<char> alphaCommitCF;   // per-sample: was ps conflict-free at COMMIT time (prior commits only)?
    std::vector<char> alphaCostAcc;    // per-sample: was ps within 5% of the fresh search cost at commit time?
    std::vector<char> alphaSeen;       // per-sample: did this connection actually reach the CPU router this iter?
    std::vector<int>  alphaPops;       // per-sample: pops of the fresh search (to split masses <4k vs monsters)
    // Per-search outputs: thread_local because partition-parallel leaf workers search concurrently.
    static thread_local long long lastPops; static thread_local float lastFoundLb;
    std::vector<int> bigConnsThisIter;                 // connIdxs with pops>=16k this iteration (flood-proto sample)
    std::vector<long long> connLastPops;               // persistent per-conn last CPU pops (hybrid flood dispatch predictor)
    // Live-price push: nodes whose occupancy changed since the last GPU cong flush (so the flood sees LIVE
    // prices, not start-of-iteration frozen ones -> lets the phase gate be removed). Dedup via epoch stamp.
    // The pending list + epoch are PER-THREAD (partition-parallel workers commit concurrently); the per-node
    // stamp array is single-writer (bbox disjointness) and epochs are globally unique (dirtyEpochSrc), so a
    // stamp written by any thread never falsely equals another thread's current epoch.
    bool trackDirty = false; std::vector<uint32_t> dirtyStamp;
    std::atomic<uint32_t> dirtyEpochSrc{1};
    static thread_local uint32_t tl_dirtyEpoch;        // this thread's current epoch (0 = unset -> markDirty no-ops until reset)
    static thread_local std::vector<int> tl_dirtyList; // this thread's pending dirty nodes
    inline void markDirty(int id) { if (id >= (int) dirtyStamp.size() || tl_dirtyEpoch == 0) return;   // lazy: node interned after GPU upload -> not GPU-tracked
        if (dirtyStamp[id] != tl_dirtyEpoch) { dirtyStamp[id] = tl_dirtyEpoch; tl_dirtyList.push_back(id); } }
    void resetDirtyLocal() { tl_dirtyList.clear(); tl_dirtyEpoch = dirtyEpochSrc.fetch_add(1, std::memory_order_relaxed); }
    long long floodBudget = 16384;   // §budget-abort: CPU A* bails after this many pops -> GPU flood (treats first-search miss)
    static thread_local bool lastAborted; // set by routeIndirectConnection when it hit the budget without reaching a sink
    bool floodHedge = false;         // §hedge: RW_GPU_FLOOD_HEDGE -- CPU + flood race concurrently (no probe, no over-flood)
    long floodHedgePoint = 4000;     // launch the concurrent flood once the CPU search passes this many pops
    std::atomic<int> hedgeFloodDone{0};   // flood thread sets this when done; main polls it
    int hedgeReached = 0, hedgePlen = 0; float hedgeCost = -1.0f; double hedgeKms = 0.0;
#ifdef WITH_CUDA
    std::vector<float> floodCong, floodCongShare;      // per-iter congestion: hist*present(occ) and hist*present(occ-1)
    std::vector<std::vector<int>> netConns;            // net -> its connection idxs (for same-net sharing gather)
    std::vector<int> shareMark;                        // share-set dedup stamp (shared; guarded by shareMu)
    int floodMark = 1;
    static const int SHARE_CAP_H = 1 << 20;
    bool floodReady = false, floodActive = false;
    std::atomic<bool> floodEverEligible{false};        // set by any search thread, read by the loop gate
    long long floodMin = 16384;                        // route on GPU flood iff connLastPops >= this (RW_GPU_FLOOD_MIN)
    long floodOverGate = 100;                           // flood only while overused > this (endgame -> CPU; RW_GPU_FLOOD_GATE; 0=no gate)
    bool floodLive = false;                             // RW_GPU_FLOOD_LIVE: push live congCost per commit (root-cause fix for staleness)
    static thread_local std::vector<float> tl_dscA, tl_dscB;  // reused scatter value buffers for the live-price push
    float floodLenW = 0.2f; int floodMaxSteps = 4000, floodMaxPath = 8192;
    std::atomic<long long> floodedCount{0}, floodFallback{0};
    // §multi-lane flood: a pool of `floodLaneCnt` GPU lanes (per-lane device scratch + stream, see
    // gpu_route.cu). Concurrent floods come only from DAG-unordered leaves whose territories are
    // disjoint, so per-lane shareCount + global prices stay deterministic. gatherShareSet still uses
    // the one shared shareMark stamp array -> guarded by shareMu (pure CPU, tens of microseconds).
    // A completed leaf publishes its remaining dirty prices (flush + lane stream sync) BEFORE its
    // successors are released, so successor floods on ANY lane see them (replaces pendingDirty).
    int floodLaneCnt = 1;
    std::mutex laneMu; std::condition_variable laneCv; uint32_t laneFreeMask = 0;
    std::mutex shareMu;                                // guards shareMark/floodMark (gather only)
    std::mutex refreshMu;                              // serializes full-refresh (needs all lanes idle)
    std::vector<int> laneShareNodes[8], laneShareCounts[8];  // per-lane share scatter host staging
    std::vector<int> laneFloodPath[8];                 // per-lane flood output path host buffer
    int acquireLane() {
        auto w0 = std::chrono::steady_clock::now();
        std::unique_lock<std::mutex> lk(laneMu);
        laneCv.wait(lk, [&] { return laneFreeMask != 0; });
        int l = __builtin_ctz(laneFreeMask);
        laneFreeMask &= ~(1u << l);
        laneWaitNs.fetch_add((long long) std::chrono::duration<double, std::nano>(
            std::chrono::steady_clock::now() - w0).count(), std::memory_order_relaxed);
        return l;
    }
    void releaseLane(int l) {
        { std::lock_guard<std::mutex> lk(laneMu); laneFreeMask |= (1u << l); }
        laneCv.notify_one();
    }
    void waitAllLanesFreeAnd(const std::function<void()>& fn) {   // full-refresh helper (caller holds NO lane)
        std::unique_lock<std::mutex> lk(laneMu);
        uint32_t all = (floodLaneCnt >= 32) ? 0xFFFFFFFFu : ((1u << floodLaneCnt) - 1u);
        laneCv.wait(lk, [&] { return laneFreeMask == all; });
        laneFreeMask = 0;                              // hold ALL lanes across fn
        lk.unlock();
        fn();
        lk.lock();
        laneFreeMask = all;
        lk.unlock();
        laneCv.notify_all();
    }
#endif

    // ---- GRoute-style structural pruning (memoized dead-end removal) -----------------------------
    // A node is a structural DEAD-END if every one of its raw children is preserved / INACCESSIBLE /
    // already-dead / an unused sink pin, AND the node itself can never be a destination (not a
    // sink/pinfeed/laguna). Such a node can never lie on any usable source->sink path, so it can be
    // skipped at expansion. deadEnd is derived from STATIC attrs only (never transient per-connection
    // state) and is monotonic, so it is safe to memoize across all connections/iterations; isSinkNode
    // protects every real sink/altSink, so the prune can never make a connection unroutable.
    //
    // EMPIRICAL RESULT (RW_PRUNE, CPU): a NET LOSS, so DEFAULT OFF. Our router already realises GRoute's
    // pruning benefit through (1) expansion-time filtering of preserved/inaccessible/unused-sink children
    // (= GRoute criteria 1 & 3) and (2) the bounding box + D0/D1 coarse-grid tightening (= GRoute's
    // search-space reduction). So only <0.1% of pushes are residual dead-ends, while the per-child
    // deadEnd[] probe adds a random read on the cache-miss-bound hot path -> oc_des +2.9%, mcml +6.5%,
    // RLE +6.4% (and RLE 19->23 iters). Kept gated (RW_PRUNE=1) because the STATIC dead-end set is a
    // useful foundation for the GPU phase (precomputed offline it cuts labels / warp divergence, where
    // the per-probe cost is paid very differently).
    std::vector<uint8_t> deadEnd;        // 1 => node leads nowhere usable (structural, memoized)
    std::vector<uint8_t> isSinkNode;     // 1 => node is some connection's sink/altSink (never prune)
    long prunedPushes = 0;               // instrumentation: child expansions skipped by the dead-end prune
    bool pruneDeadEnd = rwEnvI("RW_PRUNE", 0) != 0;   // env RW_PRUNE (default OFF; see note above)

    // ----- connection state -----
    // D-ary min-heap with the key (lb) INLINED next to the node id. Replaces the OpenJDK-mirroring
    // binary JavaPQ now that bit-exactness is no longer required. Synergy rationale:
    //  (1) lb is stored IN the heap, so sift comparisons hit contiguous memory instead of chasing
    //      dyn[id].lb -- this is what makes going d-ary pay off (a shallower tree = fewer cache
    //      misses per pop). It also DECOUPLES the queue from NodeDyn's layout, so a later hot/cold
    //      split of NodeDyn (Track A2) cannot perturb the queue or its performance.
    //  (2) arity D is tunable via env RW_HEAP_D (default 4). D=2 reproduces the binary-heap pop order
    //      with the SAME comparator semantics as the old JavaPQ (<=/>= tie breaks, leftmost-min child),
    //      i.e. a proven-equivalent safe fallback; higher D trades a wider child scan for fewer levels.
    // Correctness: lb is set exactly once per (node,connection) before offer and never changes before
    //  poll (the `visited==seq` guard blocks any re-offer/decrease-key), so the inlined snapshot always
    //  equals the live value. The only behavioural change vs JavaPQ is equal-lb tie order, which merely
    //  decides which of several equal-cost paths claims a shared node (-> at most a small iteration-count
    //  change, watched via the M-tier time metric).
    struct DaryPQ {
        using E=frontier::Entry;
        std::vector<E>& h; int sz=0; int D;
        DaryPQ(std::vector<E>& storage,int arity):h(storage),D(arity) {
            if(D!=8)throw std::runtime_error("bounded frontier requires arity8");
            if(h.size()<frontier::capacity)h.resize(frontier::capacity);
        }
        inline bool empty()const{return sz==0;}
        inline void clear(){if(btrace::current)btrace::current->frontierCleared+=(uint64_t)sz;sz=0;}
        inline void offer(float lb,int id){
            uint32_t bits;std::memcpy(&bits,&lb,4);E entry={bits,(uint32_t)id};uint32_t size=(uint32_t)sz;
            if(!frontier::offer(h.data(),size,entry))throw std::runtime_error("bounded frontier full");
            sz=(int)size;
            if(btrace::current){++btrace::current->frontierPushes;btrace::current->frontierPeak=std::max(btrace::current->frontierPeak,(uint64_t)sz);}
        }
        inline int poll(){
            E entry;uint32_t size=(uint32_t)sz;
            if(!frontier::poll(h.data(),size,entry))throw std::runtime_error("bounded frontier empty");
            sz=(int)size;if(btrace::current)++btrace::current->frontierPolls;
            return (int)entry.id;
        }
    };







    std::vector<DaryPQ::E> pqStorage;     // reused DaryPQ backing across connections (no per-conn alloc)
    int heapArity = [](){ const char* e = std::getenv("RW_HEAP_D"); int v = e ? std::atoi(e) : 8;
                          return (v >= 2 && v <= 64) ? v : 8; }();   // env RW_HEAP_D (Track A4: D=8 banked)

    // ===== Phase-1 parallel prototype (RW_PAR_ITER1=T): route iteration 1 across T threads. Each thread gets
    // its OWN search scratch (thread-local dyn copy + heap + visited sequence) so the A* labels never race;
    // occupancy is shared and LIVE (each commit visible to the others) via striped spinlocks over the
    // owner-slot + occCnt, plus a locked lazy childrenCache publish. Serial path is byte-identical (occLocking=false
    // => no locks; tl_* alias the shared members). This is the end-to-end gate for GRoute-style hyper-parallel. =====
    static thread_local NodeDyn* tl_dyn;               // per-thread search scratch (aliases dyn[] when serial)

    // ===== Sparse per-search labels (overlap-tolerant mode) ======================================
    // The ledger-18 prescription (Potter prerequisite): whole-graph-roaming workers must NOT carry
    // node-indexed label arrays (dense tl_dyn copies = GB/worker; mmap shadows OOM'd at 83GB, E18).
    // Open-addressing, epoch-stamped: reset() is O(1) per connection (bump the epoch -- stale slots
    // become claimable), linear probing, geometric growth carrying only current-epoch entries.
    // Working set = actually-touched labels (KB..MB), cache-resident. Miss default matches the
    // SERIAL init state exactly: {lb 0, upstream 0, hist unused (global), prev -1, visited 0, target 0}.
    struct SparseLabels {
        std::vector<int> ids;
        std::vector<uint32_t> ep;
        std::vector<NodeDyn> val;
        uint32_t cur = 1;
        size_t mask = 0, used = 0;
        // ---- paged mode (E-C post-mortem): the hash path costs 2-5 DRAM touches per access (ep/ids/val
        // in separate arrays + probing) and the search does 20-50 label accesses per pop -> crew ran
        // ~40x slower per worker than the flat-array serial core. Paged = flat-shadow speed at
        // O(touched-per-connection) memory: page table direct-indexed (L2-resident), pool slots
        // recycled per connection (epoch bump), pages zeroed once on first touch in a connection
        // (shadow zero-page semantics: lb/upstream/prev/visited/target = 0; .target is raw-trusted).
        int PBITS = 9, PSIZE = 1 << 9;                 // 512 nodes = 12KB per page: the zero-fill on first
                                                       // touch is the dominant per-connection tax for cheap
                                                       // searches, and it scales with page size x pages touched
        bool paged = false;
        std::vector<uint32_t> pageEp;
        std::vector<int32_t>  pageSlot;
        std::vector<NodeDyn>  pool;
        int poolUsed = 0;
        void initPaged(size_t nNodes, int pbits) {
            PBITS = pbits; PSIZE = 1 << pbits;
            size_t np = (nNodes >> PBITS) + 2;
            pageEp.assign(np, 0); pageSlot.assign(np, -1);
            pool.resize((size_t) 2048 * PSIZE);        // 24 MB initial at 12KB pages; doubles on demand
            paged = true; poolUsed = 0; cur = 1;
        }
        void init(size_t cap) {                        // cap: power of two
            ids.assign(cap, -1); ep.assign(cap, 0); val.resize(cap);
            mask = cap - 1; used = 0; cur = 1;
        }
        void prefetch(int id) const {                  // probe-only (never inserts): page live -> warm the line
            if (!paged) return;
            size_t p = (size_t) id >> PBITS;
            if (pageEp[p] == cur)
                __builtin_prefetch(pool.data() + (((size_t) pageSlot[p] << PBITS) | ((size_t) id & (size_t) (PSIZE - 1))), 1, 3);
        }
        void reset() {
            cur++; used = 0; poolUsed = 0;
            if (cur == 0) {
                std::fill(ep.begin(), ep.end(), 0);
                std::fill(pageEp.begin(), pageEp.end(), 0);
                cur = 1;
            }
        }
        NodeDyn& at(int id) {
            if (paged) {
                size_t p = (size_t) id >> PBITS;
                if (pageEp[p] != cur) {
                    if ((size_t) (poolUsed + 1) * PSIZE > pool.size()) pool.resize(pool.size() * 2);
                    pageEp[p] = cur; pageSlot[p] = poolUsed++;
                    std::memset(pool.data() + (size_t) pageSlot[p] * PSIZE, 0, sizeof(NodeDyn) * (size_t) PSIZE);
                }
                return pool[((size_t) pageSlot[p] << PBITS) | ((size_t) id & (size_t) (PSIZE - 1))];
            }
            for (size_t i = ((size_t) id * 0x9E3779B97F4A7C15ULL) & mask;; i = (i + 1) & mask) {
                if (ep[i] == cur && ids[i] == id) return val[i];
                if (ep[i] != cur) {                    // stale or never used: claimable
                    if (used + (used >> 1) > mask) { grow(); return at(id); }   // keep load < ~2/3
                    ids[i] = id; ep[i] = cur; used++;
                    val[i] = NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0};
                    return val[i];
                }
            }
        }
        void grow() {
            std::vector<int> oi; std::vector<NodeDyn> ov;
            oi.reserve(used); ov.reserve(used);
            for (size_t i = 0; i <= mask; i++)
                if (ep[i] == cur && ids[i] >= 0) { oi.push_back(ids[i]); ov.push_back(val[i]); }
            init((mask + 1) << 1);
            cur = 2;                                    // fresh epoch space after init reset cur=1
            for (size_t k = 0; k < oi.size(); k++) {
                for (size_t i = ((size_t) oi[k] * 0x9E3779B97F4A7C15ULL) & mask;; i = (i + 1) & mask) {
                    if (ep[i] != cur) { ids[i] = oi[k]; ep[i] = cur; val[i] = ov[k]; used++; break; }
                }
            }
        }
    };
    static thread_local SparseLabels* tl_sparse;       // non-null => search labels live here, not tl_dyn

    static inline NodeDyn& bTLD(int id, int line) { btrace::label(id,line); return tl_sparse ? tl_sparse->at(id) : tl_dyn[id]; }
    static thread_local std::vector<DaryPQ::E>* tl_pq; // per-thread heap backing (aliases pqStorage when serial)
    static thread_local long tl_seq;                   // per-thread visited-stamp sequence
    static thread_local int tl_wid;                    // partition-parallel worker id (-1 = not a leaf worker)
    std::atomic<int> gSearchSeq{0};                    // global visited-stamp source (partition-parallel: dyn[] is
                                                       // SHARED, so stamps must be unique across threads AND time)
    bool occLocking = false;                            // true => occupancy/cache access takes striped locks
    struct NodeSpin { std::atomic<bool> f; NodeSpin() : f(false) {} };
    static const int NLOCK = 1 << 16;
    mutable std::vector<NodeSpin> nodeLocks;            // striped spinlocks (built on first parallel iter)
    inline void lockNode(int id) const { auto& f = nodeLocks[(unsigned) id & (NLOCK - 1)].f;
        while (f.exchange(true, std::memory_order_acquire)) { while (f.load(std::memory_order_relaxed)) {} } }
    inline void unlockNode(int id) const { nodeLocks[(unsigned) id & (NLOCK - 1)].f.store(false, std::memory_order_release); }
    std::vector<std::vector<NodeDyn>> threadDyn;       // per-thread scratch arrays (copies of dyn)
    std::vector<std::vector<DaryPQ::E>> threadPq;
    int parIter1 = rwEnvI("RW_PAR_ITER1", 0);          // >1 => route iteration 1 with this many threads
    int overlapT = std::min((int) rwEnvI("RW_OVERLAP", 0), rwMaxThreads());   // >1 => overlap-tolerant LIVE parallel routing
                                                       // (every iteration; supersedes RPTT when set)
    // ===== RPTT partition-parallel (RW_PAR_PART=T; 0=off default). See routeIndirectConnectionsPartitioned. =====
    int parPart = std::min(rwEnvI("RW_PAR_PART", 0), rwMaxThreads());        // worker threads (hard cap = RW_MAX_THREADS)
    bool parOverlapEdges = rwEnvI("RW_PAR_OVERLAP", 1) != 0;     // 1=DAG edges filtered by leaf union-bbox overlap (CUFR default), 0=full tree edges
    bool parReport = rwEnvI("RW_PAR_REPORT", 0) != 0;            // print tree/task/span diagnostics
    // Straddler order: CUFR routes middle BEFORE the sides (long straddlers first). Default here is
    // MIDLAST (sides first, middle after) -- closer to the serial hpwl-ascending heuristic; measured
    // on THEIA_jpeg: WL +0.2% vs serial (mid-first +3.1%), iter-1 overuse parity, and faster overall.
    bool parMidLast = rwEnvI("RW_PAR_MIDLAST", 1) != 0;
    bool parNuma = rwEnvI("RW_PAR_NUMA", 1) != 0;                // interleave hot arrays + pin workers across sockets
    bool parPin  = rwEnvI("RW_PAR_PIN", 1) != 0;
    // Approximate lock-free sharing (RW_PAR_APX=1): a per-node single-owner slot (owner net + its connection
    // count). Maintained under the commit lock (exact for the owner), READ lock-free in the hot path so the
    // ~500 countConnectionsOfUser reads/search stop contending. Approximate only for multi-net (overuse)
    // nodes, where the non-owner net reads 0 (no share discount) -- occCnt/overuse stays EXACT.
    bool apxShare = rwEnvI("RW_PAR_APX", 1) != 0;
    // RW_PAR_NOSHARE=1: discriminator probe -- during parallel iter-1 every thread sees EMPTY occupancy
    // (reads=0, commits=no-op), so there is ZERO shared-occupancy read/write. Isolates the memory-bandwidth
    // wall (read-only graph random access) from hot-node cache-line contention. Timing-only (routing is
    // garbage); exits after iteration 1.
    bool parNoShare = rwEnvI("RW_PAR_NOSHARE", 0) != 0;
    std::vector<std::atomic<int>> apxOwner, apxCnt, apxOcc;   // owner net, its count, distinct-net occupancy
    inline int apxCount(int id, int nw) const {
        int o = apxOwner[id].load(std::memory_order_relaxed);
        return o == nw ? apxCnt[id].load(std::memory_order_relaxed) : 0;
    }

    // ----------------------------------------------------------------- node helpers
    int numNodes() const { return nodeCountA.load(std::memory_order_acquire); }   // == ns.size() at serial points
    void kiGrow(size_t want) {           // serial-only: rebuild the key->id table (keys recomputable)
        if (keyToId.cap >= want) return;
        keyToId.reset(want);
        const int n = numNodes();
        for (int i = 0; i < n; i++) keyToId.putSerial(keyOf(i), i);
    }
    bool isPreserved(int id) const { return ns[id].preserved; }

    // A node is eligible to be marked dead-end only if it can never be a routing DESTINATION. Sinks
    // (real sink/altSink of a connection, any EXCLUSIVE_SINK type) and Laguna/pinfeed access nodes are
    // always kept. Conservative on purpose: better to keep a useless node than to drop a needed one.
    inline bool canBeDeadEnd(int id) const {
        if (isSinkNode[id]) return false;
        if (isAnyExclusiveSink(type[id])) return false;
        const NodeStatic& a = ns[id];
        return !(a.isPinfeed || a.isPinbounce || a.isLaguna || a.pinfeedLeadsToLaguna);
    }
    // Is `child` STRUCTURALLY incapable of contributing to any usable path (so a parent whose children
    // are ALL such is itself a dead-end)? Static attrs only: preserved (reserved for another net),
    // INACCESSIBLE, already-dead, or an EXCLUSIVE_SINK pin that no connection actually targets (GRoute's
    // "dead-end at an unused site pin"). Pass-throughs and real/pinbounce/laguna access nodes stay alive.
    inline bool deadChild(int child) const {
        if (ns[child].preserved || deadEnd[child]) return true;
        RouteNodeType t = type[child];
        if (t == RouteNodeType::INACCESSIBLE) return true;
        if (isAnyExclusiveSink(t) && !isSinkNode[child]) return true;
        return false;
    }

    int getOccupancy(int id) const {   // A5: O(1) flat read; parallel apx mode reads the lock-free atomic occ
        if (occLocking && parNoShare) return 0;                  // discriminator: empty occupancy, no shared read
        return (occLocking && apxShare) ? apxOcc[id].load(std::memory_order_relaxed) : occCnt[id];
    }
    inline int countUserSlot(int id, int nw) const {
        int o = ownerNet[id];
        if (o == nw) return ownerCnt[id];
        auto* ov = userOverflow[id];
        if (!ov) return 0;
        auto it = ov->find(nw);
        return it == ov->end() ? 0 : it->second;
    }
    inline void promoteOverflowOwner(int id) {
        auto* ov = userOverflow[id];
        if (!ov || ov->empty()) return;
        auto it = ov->begin();
        ownerNet[id] = it->first;
        ownerCnt[id] = (uint16_t) it->second;
        ov->erase(it);
        if (ov->empty()) { delete ov; userOverflow[id] = nullptr; }
    }
    static uint8_t packHotFlags(const NodeStatic& a) {
        uint8_t f = 0;
        if (a.isLaguna) f |= HF_LAGUNA;
        if (a.isPinfeed) f |= HF_PINFEED;
        if (a.pinfeedLeadsToLaguna) f |= HF_PF_LAG;
        if (a.isPinbounce) f |= HF_PINBOUNCE;
        if (a.preserved) f |= HF_PRESERVED;
        return f;
    }
    void initHotFromStatic(int id) {
        const NodeStatic& a = ns[id];
        HotExpand& h = hot[id];
        h.baseCost = a.baseCost;
        h.tileAddr = a.tileAddr;
        h.beginX = a.beginX; h.beginY = a.beginY;
        h.endX = a.endX; h.endY = a.endY;
        h.length = a.length;
        h.type = (uint8_t) type[id];
        h.flags = packHotFlags(a);
        h.ownerNet = ownerNet[id];
        h.ownerCnt = ownerCnt[id];
        h.occCnt = (uint8_t) std::min(255, (int) occCnt[id]);
    }
    inline void syncHotOcc(int id) {
        HotExpand& h = hot[id];
        h.ownerNet = ownerNet[id];
        h.ownerCnt = ownerCnt[id];
        h.occCnt = (uint8_t) std::min(255, (int) occCnt[id]);
    }
    inline int countUserHot(int id, int nw) const {
        const HotExpand& h = hot[id];
        if (h.ownerNet == nw) return h.ownerCnt;
        auto* ov = userOverflow[id];
        if (!ov) return 0;
        auto it = ov->find(nw);
        return it == ov->end() ? 0 : it->second;
    }
    inline RouteNodeType searchType(int id) const {
        return useHotExpand ? (RouteNodeType) hot[id].type : type[id];
    }
    inline bool nodeLaguna(int id) const {
        return useHotExpand ? (hot[id].flags & HF_LAGUNA) != 0 : ns[id].isLaguna;
    }
    inline bool nodePinbounce(int id) const {
        return useHotExpand ? (hot[id].flags & HF_PINBOUNCE) != 0 : ns[id].isPinbounce;
    }
    inline bool nodePreserved(int id) const {
        return useHotExpand ? (hot[id].flags & HF_PRESERVED) != 0 : ns[id].preserved;
    }
    int searchEndY(int id) const {
        if (!useHotExpand) return getEndTileYCoordinate(id);
        const HotExpand& h = hot[id];
        if (h.type == (uint8_t) RouteNodeType::SUPER_LONG_LINE) {
            int p = TLD(id).prev;
            if (p != -1 && ns[p].endY == h.endY) return h.beginY;
        }
        return h.endY;
    }
    bool searchInBB(int id, const Connection& c) const {
        if (!useHotExpand) return isInConnectionBoundingBox(id, c);
        const HotExpand& h = hot[id];
        int ey = searchEndY(id);
        return h.endX > c.xMinBB && h.endX < c.xMaxBB && ey > c.yMinBB && ey < c.yMaxBB;
    }
    inline int searchCountUser(int id, int nw) const {
        if (occLocking || !useHotExpand) return countConnectionsOfUser(id, nw);
        return countUserHot(id, nw);
    }
    inline bool searchWillOverUse(int id, int nw) const {
        if (occLocking || !useHotExpand) return willOverUse(id, nw);
        const HotExpand& h = hot[id];
        int occ = h.occCnt;
        return occ > CAPACITY || (occ == CAPACITY && countUserHot(id, nw) == 0);
    }
    float getNodeCostSearch(int id, const Connection& c, int countSameSourceUsers, float sharingFactor) const {
        if (occLocking || !useHotExpand) return getNodeCost(id, c, countSameSourceUsers, sharingFactor);
        const HotExpand& h = hot[id];
        int occ = h.occCnt;
        float presentCongestionCost = countSameSourceUsers
            ? presentCongestionCosts[occ > 0 ? occ - 1 : 0]
            : presentCongestionCosts[occ];
        float baseCost = h.baseCost;
        const NetWrapper& nw = nets[c.netIdx];
        int ey = searchEndY(id);
        float distToCenter = std::abs(h.endX - nw.xCenter) + std::abs(ey - nw.yCenter);
        return search_cost_exact::node_cost(baseCost, dyn[id].hist, presentCongestionCost,
                                      sharingFactor, nw.connectionsSize, distToCenter, nw.doubleHpwl);

    }
    inline void incUserSlot(int id, int nw) {
        int& on = ownerNet[id];
        if (on < 0) {
            on = nw; ownerCnt[id] = 1;
            occCnt[id]++; if (trackDirty) markDirty(id);
        } else if (on == nw) {
            ownerCnt[id]++;
        } else {
            auto*& ov = userOverflow[id];
            if (!ov) ov = new std::unordered_map<int,int>();
            int& c = (*ov)[nw];
            if (c == 0) { occCnt[id]++; if (trackDirty) markDirty(id); }
            c++;
        }
        syncHotOcc(id);
    }
    inline void decUserSlot(int id, int nw) {
        if (ownerNet[id] == nw) {
            if (--ownerCnt[id] == 0) {
                ownerNet[id] = -1;
                occCnt[id]--; if (trackDirty) markDirty(id);
                promoteOverflowOwner(id);
            }
        } else {
            auto* ov = userOverflow[id];
            auto it = ov->find(nw);
            if (it->second == 1) {
                ov->erase(it);
                occCnt[id]--; if (trackDirty) markDirty(id);
                if (ov->empty()) { delete ov; userOverflow[id] = nullptr; }
            } else it->second--;
        }
        syncHotOcc(id);
    }
    int countConnectionsOfUser(int id, int nw) const {
        if (occLocking) {                    // parallel hot path: lock-free approximate owner-slot read
            if (parNoShare) return 0;        // discriminator: no shared read
            if (apxShare) return apxCount(id, nw);
            lockNode(id); int r = countUserSlot(id, nw);
            unlockNode(id); return r;
        }
        return countUserSlot(id, nw);
    }
    void incrementUser(int id, int nw) {
        if (occLocking && parNoShare) return;         // discriminator: no shared write
        if (occLocking && apxShare) {                 // parallel: lock-free, allocation-free approximate commit
            int cur = apxOwner[id].load(std::memory_order_acquire);
            if (cur == nw) apxCnt[id].fetch_add(1, std::memory_order_relaxed);   // same net -> distinct occ unchanged
            else if (cur == -1) {
                int exp = -1;
                if (apxOwner[id].compare_exchange_strong(exp, nw, std::memory_order_acq_rel)) {
                    apxCnt[id].store(1, std::memory_order_relaxed); apxOcc[id].fetch_add(1, std::memory_order_relaxed);
                } else if (apxOwner[id].load(std::memory_order_relaxed) == nw) apxCnt[id].fetch_add(1, std::memory_order_relaxed);
                else apxOcc[id].fetch_add(1, std::memory_order_relaxed);
            } else apxOcc[id].fetch_add(1, std::memory_order_relaxed);           // different net -> distinct occ++
            return;
        }
        if (occLocking) lockNode(id);                 // RW_PAR_APX=0: exact locked owner-slot (for A/B contention test)
        incUserSlot(id, nw);
        if (occLocking) unlockNode(id);
    }
    void decrementUser(int id, int nw) {
        if (occLocking && parNoShare) return;         // discriminator: no shared write
        if (occLocking && apxShare) {                 // parallel: lock-free approximate (decrements are rare at iter-1)
            int cur = apxOwner[id].load(std::memory_order_relaxed);
            if (cur == nw) { if (apxCnt[id].fetch_sub(1, std::memory_order_relaxed) == 1) { apxOwner[id].store(-1, std::memory_order_relaxed); apxOcc[id].fetch_sub(1, std::memory_order_relaxed); } }
            else apxOcc[id].fetch_sub(1, std::memory_order_relaxed);
            return;
        }
        if (occLocking) lockNode(id);
        decUserSlot(id, nw);
        if (occLocking) unlockNode(id);
    }
    bool isOverUsed(int id) const { return CAPACITY < getOccupancy(id); }
    bool willOverUse(int id, int nw) const {
        int occ = getOccupancy(id);
        return occ > CAPACITY || (occ == CAPACITY && countConnectionsOfUser(id, nw) == 0);
    }
    float getPresentCongestionCost(int occupancy) const { return presentCongestionCosts[occupancy]; }
    float getPresentCongestionCostOf(int id) const { return presentCongestionCosts[getOccupancy(id)]; }

    int getNode(int id) const { return created[id] ? id : -1; }  // mirror getNode()=null if not created

    void getOrCreate(int id) { created[id] = 1; }

    long long keyOf(int id) const {
        return ((long long) ns[id].tileAddr << 20) | (nc[id].wireIndex & 0xFFFFF);
    }

    // Lazy node interning (JNI mode): create a node slot for a (key, hot+cold attrs) if unseen.
    int internNode(const NodeStatic& a, const NodeCold& cd) {
        const long long key = ((long long) a.tileAddr << 20) | (cd.wireIndex & 0xFFFFF);
        const uint64_t want = (uint64_t) key + 1;
        for (size_t i = keyToId.home(key);;) {
            uint64_t k = keyToId.keys[i].load(std::memory_order_acquire);
            if (k == want) {                              // exists (or a racing creator: wait for publish)
                int v;
                while ((v = keyToId.vals[i].load(std::memory_order_acquire)) == 0) {}
                return v - 1;
            }
            if (k == 0) {
                uint64_t exp = 0;
                if (!keyToId.keys[i].compare_exchange_strong(exp, want, std::memory_order_acq_rel))
                    continue;                             // slot got claimed under us -> re-examine it
                // Claimed: create the node. Array appends under the intern spinlock; the id is only
                // visible to other threads once vals[i] is published (release) below.
                while (internLock.exchange(true, std::memory_order_acquire)) {}
                const int id = (int) ns.size();
                if (tl_wid >= 0 && ns.size() == ns.capacity()) {   // a parallel realloc would dangle every reader
                    std::fprintf(stderr, "FATAL: lazy node capacity %zu exhausted during parallel routing\n", ns.capacity());
                    std::abort();
                }
                ns.push_back(a);
                nc.push_back(cd);
                // Preserved bit set ONCE per distinct node here (not per child-occurrence): seeds carry it
                // from Java (a.preserved); children get it from the design preserve set, bloom-pre-checked.
                if (!ns.back().preserved && preserveReady && maybePreserved(key) && preserveSet.count(key))
                    ns.back().preserved = true;
                type.push_back(cd.type);
                // hot[] must mirror ns[]; eager load calls initHotFromStatic in bulk, lazy internNode here.
                dyn.push_back(NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0});
                created.push_back(cd.createdAtInit ? 1 : 0);
                ownerNet.push_back(-1);
                ownerCnt.push_back(0);
                userOverflow.push_back(nullptr);
                occCnt.push_back(0);
                hot.push_back(HotExpand{});
                childrenCache.push_back(nullptr);
                overUsed.push_back(0);
                deadEnd.push_back(0);
                isSinkNode.push_back(0);
                rawFetched.push_back(0);
                rawChildrenStore.push_back({});
                initHotFromStatic(id);
                nodeCountA.store(id + 1, std::memory_order_release);
                internLock.store(false, std::memory_order_release);
                // Serial lazy interning may realloc dyn; refresh the cached alias. (Parallel interning
                // never reallocs -- capacity is guaranteed by ensureLazyHeadroom + the FATAL guard above.)
                if (!occLocking && tl_wid < 0) tl_dyn = dyn.data();
                keyToId.vals[i].store(id + 1, std::memory_order_release);
                return id;
            }
            i = (i + 1) & keyToId.mask;
        }
    }

    // Batched lazy interning: resolve/create ALL children of one fetch with a single intern-lock
    // acquisition. The expensive parts (map probe/claim, attr unpack, preserved lookup, hot-bundle
    // init) run OUTSIDE the lock; the locked region is just the array appends, so the 16 vector
    // tails stop ping-ponging between cores on every node (one migration per fetch, not per child).
    void internChildrenBatch(const std::vector<int>& packed, int cnt, std::vector<int>& out) {
        struct NewChild { ChildAttrs ca; long long key; size_t slot; int outPos; };
        static thread_local std::vector<NewChild> fresh;
        fresh.clear();
        for (int k = 0; k < cnt; k++) {
            const int* p = &packed[1 + k * 11];
            const long long key = ((long long) p[0] << 20) | (p[1] & 0xFFFFF);
            const uint64_t want = (uint64_t) key + 1;
            int resolved;
            for (size_t i = keyToId.home(key);;) {
                uint64_t kk = keyToId.keys[i].load(std::memory_order_acquire);
                if (kk == want) {
                    // Existing -- or claimed. If *I* claimed it earlier in this batch its value is not
                    // published yet and spinning would self-deadlock: alias to the earlier position.
                    int mine = -1;
                    for (auto& f : fresh) if (f.key == key) { mine = f.outPos; break; }
                    if (mine >= 0) { resolved = -3 - mine; break; }
                    int v;
                    while ((v = keyToId.vals[i].load(std::memory_order_acquire)) == 0) {}
                    resolved = v - 1;
                    break;
                }
                if (kk == 0) {
                    uint64_t exp = 0;
                    if (!keyToId.keys[i].compare_exchange_strong(exp, want, std::memory_order_acq_rel))
                        continue;                              // slot got claimed under us -> re-examine
                    ChildAttrs ca = unpackChild(p);
                    if (!ca.hot.preserved && preserveReady && maybePreserved(key) && preserveSet.count(key))
                        ca.hot.preserved = true;               // preserved bit resolved outside the lock
                    fresh.push_back(NewChild{ca, key, i, (int) out.size()});
                    resolved = -2;                             // patched to a real id below
                    break;
                }
                i = (i + 1) & keyToId.mask;
            }
            out.push_back(resolved);
        }
        if (!fresh.empty()) {
            while (internLock.exchange(true, std::memory_order_acquire)) {}
            const int base = (int) ns.size();
            if (tl_wid >= 0 && ns.size() + fresh.size() > ns.capacity()) {
                std::fprintf(stderr, "FATAL: lazy node capacity %zu exhausted during parallel routing\n", ns.capacity());
                std::abort();
            }
            for (auto& f : fresh) {
                ns.push_back(f.ca.hot);
                nc.push_back(f.ca.cold);
                type.push_back(f.ca.cold.type);
                dyn.push_back(NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0});
                created.push_back(f.ca.cold.createdAtInit ? 1 : 0);
                ownerNet.push_back(-1);
                ownerCnt.push_back(0);
                userOverflow.push_back(nullptr);
                occCnt.push_back(0);
                hot.push_back(HotExpand{});
                childrenCache.push_back(nullptr);
                overUsed.push_back(0);
                deadEnd.push_back(0);
                isSinkNode.push_back(0);
                rawFetched.push_back(0);
                rawChildrenStore.push_back({});
            }
            nodeCountA.store(base + (int) fresh.size(), std::memory_order_release);
            internLock.store(false, std::memory_order_release);
            if (!occLocking && tl_wid < 0) tl_dyn = dyn.data();   // serial lazy may have realloc'd
            for (size_t j = 0; j < fresh.size(); j++) {
                const int id = base + (int) j;
                initHotFromStatic(id);                            // ids are ours until vals publish
                out[fresh[j].outPos] = id;
                keyToId.vals[fresh[j].slot].store(id + 1, std::memory_order_release);
            }
        }
        for (int k = 0; k < cnt; k++)                             // in-batch duplicate aliases
            if (out[k] <= -3) out[k] = out[-3 - out[k]];
    }

    // Parse a packed child record (11 ints) into hot+cold attrs.
    static ChildAttrs unpackChild(const int* p) {
        ChildAttrs r{};
        NodeStatic& a = r.hot; NodeCold& cd = r.cold;
        a.tileAddr = p[0];
        cd.wireIndex = p[1];
        cd.type = (RouteNodeType) p[2];
        int flags = p[3];
        a.isLaguna = flags & 1;
        a.isPinfeed = flags & 2;
        a.pinfeedLeadsToLaguna = flags & 4;
        a.isPinbounce = flags & 8;
        a.preserved = flags & 16;
        a.arcLockedInit = false;
        cd.createdAtInit = false;
        a.beginX = (int16_t) p[4];
        a.beginY = (int16_t) p[5];
        a.endX = (int16_t) p[6];
        a.endY = (int16_t) p[7];
        a.length = (int16_t) p[8];
        std::memcpy(&a.baseCost, &p[9], sizeof(float));
        cd.hashCode = p[10];
        cd.prevInit = -1;
        a.childStart = a.childCount = 0;
        return r;
    }

    // RouteNode.getEndTileYCoordinate(): SLL reverse uses prev.
    int getEndTileYCoordinate(int id) const {
        if (type[id] == RouteNodeType::SUPER_LONG_LINE) {
            int p = TLD(id).prev;
            if (p != -1 && ns[p].endY == ns[id].endY) return ns[id].beginY;
        }
        return ns[id].endY;
    }
    int getEndTileXCoordinate(int id) const { return ns[id].endX; }
    int getBeginTileXCoordinate(int id) const { return ns[id].beginX; }
    int getBeginTileYCoordinate(int id) const { return ns[id].beginY; }
    int getSLRIndex(int id) const { return intYToSLRIndex[getEndTileYCoordinate(id)]; }

    bool isInConnectionBoundingBox(int id, const Connection& c) const {
        int ex = ns[id].endX, ey = getEndTileYCoordinate(id);
        return ex > c.xMinBB && ex < c.xMaxBB && ey > c.yMinBB && ey < c.yMaxBB;
    }

    // ----------------------------------------------------------------- isExcluded
    bool isPartOfExistingRoute(int parent, int child) const {
        int endR = getNode(child);
        if (endR == -1) return false;
        int p = TLD(endR).prev;
        if (p != -1) {
            if (TLD(endR).visited == TLD(parent).visited) return false;
            if (p == parent && ns[child].preserved) return true;
        }
        return false;
    }

    bool isExcluded(int parent, int child) {
        const auto& a=ns[child];
        const uint8_t flags=(a.preserved?64:0)|(a.isPinfeed?4:0)|(a.pinfeedLeadsToLaguna?8:0)|(a.isLaguna?2:0)|(a.arcLockedInit?32:0);
        search_filter::Machine machine(parent,flags,getNode(child)!=-1,hasLaguna);
        while(machine.request!=search_filter::DONE) {
            uint32_t value=0;
            switch(machine.request) {
            case search_filter::CHILD_PREV:value=(uint32_t)bTLD(child,1046).prev;break;
            case search_filter::CHILD_VISITED:value=(uint32_t)bTLD(child,1048).visited;break;
            case search_filter::PARENT_VISITED:value=(uint32_t)bTLD(parent,1048).visited;break;
            case search_filter::ARC_PREV:value=(uint32_t)bTLD(child,1069).prev;break;
            default:throw std::runtime_error("invalid exclusion request");
            }
            machine.accept(value);
        }
        return machine.excluded;
    }


    // ----------------------------------------------------------------- getChildren
    const std::vector<int>& getChildren(int id) {
        {   // acquire: batch workers touch the SAME nodes concurrently (no territory disjointness).
            // Sentinel-claim protocol (non-occLocking): first thread CASes a 0x1 sentinel and builds;
            // others spin for the publish instead of building duplicates (16x redundant first-touch
            // builds measured 6.5x iter-1 work in batch mode).
            std::vector<int>* c = __atomic_load_n(&childrenCache[id], __ATOMIC_ACQUIRE);
            if ((uintptr_t) c > 1) return *c;
            if (!occLocking) {
                std::vector<int>* expected = nullptr;
                if (c == (std::vector<int>*) 1 ||
                    !__atomic_compare_exchange_n(&childrenCache[id], &expected, (std::vector<int>*) 1,
                                                 false, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE)) {
                    for (;;) {
                        std::vector<int>* p = __atomic_load_n(&childrenCache[id], __ATOMIC_ACQUIRE);
                        if ((uintptr_t) p > 1) return *p;
                        __builtin_ia32_pause();
                    }
                }
            }
        }
        // Lazy (JNI): pull raw allowed-tile adjacency, interning children. Interning may grow the
        // node arrays, so finish ALL interning before index-assigning rawChildrenStore (realloc-safe).
        if (lazy && !rawFetched[id]) {
            // Per-thread fetch buffers: leaf workers fetch concurrently (compact device is read-only).
            static thread_local std::vector<int> tl_fetchPacked, tl_fetchRaw;
            if (tl_wid < 0) {   // timing is main-thread-only (workers skip the clock, not the fetch)
                auto _t0 = std::chrono::steady_clock::now();
                fetchChildrenPacked(keyOf(id), tl_fetchPacked);
                jniDeviceSecs += std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count();
                jniDeviceCalls++;
            } else {
                fetchChildrenPacked(keyOf(id), tl_fetchPacked);
            }
            int cnt = tl_fetchPacked.empty() ? 0 : tl_fetchPacked[0];
            tl_fetchRaw.clear();
            internChildrenBatch(tl_fetchPacked, cnt, tl_fetchRaw);   // one lock per fetch, not per child
            rawChildrenStore[id] = tl_fetchRaw;
            rawFetched[id] = 1;
        }
        std::vector<int>* out = new std::vector<int>();
        search_children::Machine walk(lazy ? rawChildrenStore[id].size() : ns[id].childCount, pruneDeadEnd);
        while (walk.request != search_children::PUBLISH) {
            bool ok = false; int child = (int)walk.child;
            switch (walk.request) {
            case search_children::NEXT: {
                int next = lazy ? rawChildrenStore[id][walk.position] : childIds[ns[id].childStart + walk.position];
                ok = walk.next(next, pruneDeadEnd && deadChild(next)); break;
            }
            case search_children::EXCLUDE: ok = walk.excluded(isExcluded(id, child)); break;
            case search_children::CREATE: getOrCreate(child); ok = walk.created(); break;
            case search_children::CLASSIFY: {
                bool inaccessible = type[child] == RouteNodeType::INACCESSIBLE;
                ok = walk.classified(inaccessible, !inaccessible && pruneDeadEnd && deadEnd[child]); break;
            }
            case search_children::EMIT: out->push_back(child); ok = walk.emitted(); break;
            case search_children::CHECK_DEAD: ok = walk.can_mark_dead(canBeDeadEnd(id)); break;
            case search_children::MARK_DEAD: deadEnd[id] = 1; ok = walk.marked_dead(); break;
            default: break;
            }
            if (!ok) throw std::runtime_error("invalid first-touch filtering response");
        }
        // The unchanged ownership/publish block below commits this complete list.







        if (occLocking) {                     // parallel: publish under the node lock (double-checked); the
            lockNode(id);                     // filter above is lock-free and, at first-touch, state-independent
            if (childrenCache[id]) { unlockNode(id); delete out; return *childrenCache[id]; }
            childrenCache[id] = out; unlockNode(id);
        } else {
            // We hold the 0x1 sentinel claim: publish the built list (release) for any spinners.
            __atomic_store_n(&childrenCache[id], out, __ATOMIC_RELEASE);
        }
        return *out;
    }

    // ----------------------------------------------------------- RouteNodeGraph.isAccessible
    bool graphIsAccessible(int childRnode, int parentRnode, const Connection& c) {
        RouteNodeType t = searchType(childRnode);
        if (!isAnyLocal(t)) {
            switch (t) {
                case RouteNodeType::NON_LOCAL: {
                    RouteNodeType pt = searchType(parentRnode);
                    if (isAnyLocal(pt)) {
                        // LOCAL -> NON_LOCAL : only legal into a Laguna mux (leading-to-laguna parent)
                        bool childLaguna = nodeLaguna(childRnode);
                        if (childLaguna) {
                            int sinkRnode = c.sinkRnode;
                            if (!c.isCrossSLR() || getSLRIndex(childRnode) == getSLRIndex(sinkRnode)) {
                                return false;
                            }
                        }
                        // else CLE output via routethru: not reachable here (lutRoutethru off) -> fall through true
                    } else if (pt == RouteNodeType::SUPER_LONG_LINE &&
                               TLD(parentRnode).prev != -1 && ns[TLD(parentRnode).prev].tileAddr == ns[childRnode].tileAddr) {
                        // UBUMP -> RXD: do not go back the way we came
                        return false;
                    }
                    break;
                }
                case RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA:
                case RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA:
                    break;
                default:
                    break;  // (Versal-only types unreachable on US+)
            }
            return true;
        }

        int sinkRnode = c.sinkRnode;
        int childX = useHotExpand ? hot[childRnode].endX : getEndTileXCoordinate(childRnode);

        // (b) needs to cross an SLR and this is a local node servicing a Laguna
        if (c.isCrossSLR() && isLocalLeadingToLaguna(t) &&
            getSLRIndex(childRnode) != getSLRIndex(sinkRnode)) {
            if ((leadsToNorthboundLaguna(t) && !c.crossSLRnorth) ||
                (leadsToSouthboundLaguna(t) && !c.crossSLRsouth)) {
                return false;
            }
            return true;
        }

        // (c) on the same side as the sink
        bool childSameTile = useHotExpand
            ? (hot[childRnode].tileAddr == hot[sinkRnode].tileAddr)
            : (ns[childRnode].tileAddr == ns[sinkRnode].tileAddr);
        switch (searchType(sinkRnode)) {
            case RouteNodeType::LOCAL_EAST:        // fall-through
            case RouteNodeType::EXCLUSIVE_SINK_EAST:
                if (isWestLocal(t) || t == RouteNodeType::LOCAL_RESERVED) return false;
                break;
            case RouteNodeType::LOCAL_WEST:        // fall-through
            case RouteNodeType::EXCLUSIVE_SINK_WEST:
                if (isEastLocal(t) || t == RouteNodeType::LOCAL_RESERVED) return false;
                break;
            case RouteNodeType::EXCLUSIVE_SINK_BOTH:
                // US+: CTRL sink; only LOCAL_BOTH in the sink tile
                if (!childSameTile) return false;
                if (t != RouteNodeType::LOCAL_BOTH) return false;
                break;
            case RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL:
                if (isAnyLocal(t)) return false;
                break;
            default:
                break;
        }

        // (d) in the sink tile
        if (childSameTile) return true;

        // (e) when in same X as the sink tile, but Y +/- 1
        return childX == getBeginTileXCoordinate(sinkRnode) &&
               std::abs(getEndTileYCoordinate(childRnode) - getBeginTileYCoordinate(sinkRnode)) <= 1;
    }

    bool isAccessible(int child, const Connection& c) const {
        return !cfg.useBoundingBox || searchInBB(child, c);
    }
    bool isAccessibleSink(int child, const Connection& c) const {
        if (TLD(child).target) return true;
        if (searchCountUser(child, c.netIdx) == 0 || !nodePinbounce(child)) return false;
        return true;  // PINBOUNCE exclusive sink of another connection on the same net
    }

    // ----------------------------------------------------------------- cost
    float getNodeCost(int id, const Connection& c, int countSameSourceUsers, float sharingFactor) const {
        bool hasSame = (countSameSourceUsers != 0);
        float presentCongestionCost;
        if (hasSame) {
            int occWithout = getOccupancy(id) - 1;
            presentCongestionCost = getPresentCongestionCost(occWithout);
        } else {
            presentCongestionCost = getPresentCongestionCostOf(id);
        }
        float baseCost = ns[id].baseCost;
        const NetWrapper& nw = nets[c.netIdx];
        float distToCenter = std::abs(getEndTileXCoordinate(id) - nw.xCenter) +
                             std::abs(getEndTileYCoordinate(id) - nw.yCenter);
        return search_cost_exact::node_cost(baseCost, dyn[id].hist, presentCongestionCost,
                                      sharingFactor, nw.connectionsSize, distToCenter, nw.doubleHpwl);

    }

    // §alpha probe: re-price a stored path (rnodes = sink..source) with the SAME g-cost the A* accumulates,
    // at the CURRENT prices. Used to test whether a presearched path is still cost-competitive at commit time.
    float repriceG(const std::vector<int>& p, const Connection& c) {
        float g = 0.0f; int ni = c.netIdx; float rnWL = 1.0f * (1.0f - wlWeight);
        for (int i = (int) p.size() - 2; i >= 0; i--) {          // every node except the source (p.back())
            int nd = p[i]; int cs = countConnectionsOfUser(nd, ni);
            float sf = 1.0f + 1.0f * cs;                          // shareWeight = pow(1,e) = 1 (non-timing)
            g += getNodeCost(nd, c, cs, sf);
            g += rnWL * ns[nd].length / sf;
        }
        return g;
    }

    struct State {
        DaryPQ* queue;
        std::vector<int> targets;
        int connIdx;
        int sequence;
        float shareWeight, rnodeWLWeight, estWlWeight;  // rnodeCostWeight=1 (non-timing)
        bool earlyTermination;
        uint16_t lmkT[8];                              // ALT: quantized landmark distances of the sink
    };

    // ===== ALT landmark heuristic (huge cases): 8 GPU whole-device static SSSPs, quantized u16,
    // landmark-major interleave (16B/node = one cache line per child evaluation). h_alt(v,t) =
    // max_l (D_l(t) - D_l(v)) by triangle inequality on the DIRECTED static graph; mirrors the
    // banked heuristic's /sharingFactor treatment (same non-strict-admissibility tradeoff).
    std::vector<uint16_t> lmk;                         // [node*8+l]
    float lmkInvScale = 0.0f;
    bool lmkReady = false;

#ifdef WITH_CUDA
    void computeLandmarks() {
        auto _t0 = std::chrono::steady_clock::now();
        const int N = numNodes();
        int maxX = 0, maxY = 0;
        for (int i = 0; i < N; i++) { if (ns[i].endX > maxX) maxX = ns[i].endX; if (ns[i].endY > maxY) maxY = ns[i].endY; }
        const int ax[8] = {0, maxX, 0, maxX, maxX / 2, maxX / 2, 0, maxX};
        const int ay[8] = {0, 0, maxY, maxY, 0, maxY, maxY / 2, maxY / 2};
        int anchor[8]; long bestD[8];
        for (int l = 0; l < 8; l++) { anchor[l] = -1; bestD[l] = 1L << 60; }
        for (int i = 0; i < N; i++) {                  // nearest CREATED-or-not node to each anchor point
            for (int l = 0; l < 8; l++) {
                long d = std::labs(ns[i].endX - ax[l]) + std::labs(ns[i].endY - ay[l]);
                if (d < bestD[l]) { bestD[l] = d; anchor[l] = i; }
            }
        }
        std::vector<std::vector<float>> tmp(8);
        float maxFinite = 0.0f;
        const float lenW = 1.0f * (1.0f - wlWeight);
        for (int l = 0; l < 8; l++) {
            tmp[l].resize((size_t) N);
            if (gpuLandmarkSSSP(anchor[l], 4000, lenW, tmp[l].data()) != 0) {
                std::fprintf(stderr, "[lmk] SSSP %d failed -> landmarks OFF\n", l);
                return;
            }
            for (int i = 0; i < N; i++) { float c = tmp[l][(size_t) i]; if (c < 1e30f && c > maxFinite) maxFinite = c; }
        }
        const float scale = 65000.0f / std::max(maxFinite, 1.0f);
        lmkInvScale = 1.0f / scale;
        lmk.assign((size_t) N * 8, 65535);
        parForN((size_t) N, std::max(1, parPart), [&](int, size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++)
                for (int l = 0; l < 8; l++) {
                    float c = tmp[(size_t) l][i];
                    if (c < 1e30f) lmk[i * 8 + (size_t) l] = (uint16_t) std::min(65000.0f, c * scale);
                }
        });
        lmkReady = true;
        std::fprintf(stderr, "[lmk] 8 landmarks ready in %.2fs (scale=%.4f, maxCost=%.1f)\n",
                     std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count(),
                     scale, maxFinite);
    }
#endif

    inline void fillLmkT(State& st, int sinkRnode) {
        if (!lmkReady || sinkRnode < 0) { for (int l = 0; l < 8; l++) st.lmkT[l] = 0; return; }
        const uint16_t* tv = &lmk[(size_t) sinkRnode * 8];
        for (int l = 0; l < 8; l++) st.lmkT[l] = (tv[l] == 65535) ? 0 : tv[l];   // INF sink dist -> lm skipped
    }

    void push(State& st, int child, float newPartial, float newTotal, bool lookahead) {
        TLD(child).lb = newTotal;
        TLD(child).upstream = newPartial;
        TLD(child).visited = st.sequence;
        tl_pushes++;
        if (dumpMode) dumpExplored.push_back(child);   // record every node the A* pushes (visualization)
        if (lookahead) {
            exploreAndExpand(st, child);
        } else {
            st.queue->offer(newTotal, child);
        }
    }

    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {
        Connection& c = connections[st.connIdx];
        int countSourceUses = searchCountUser(childRnode, c.netIdx);
        float sharingFactor = search_cost_exact::sharing_factor(st.shareWeight, countSourceUses);
        TLD(childRnode).prev = rnode;

        float newPartial = TLD(rnode).upstream;
        float nodeCost = getNodeCostSearch(childRnode, c, countSourceUses, sharingFactor);
        newPartial = search_cost_exact::partial_cost(newPartial, nodeCost, st.rnodeWLWeight, (useHotExpand ? hot[childRnode].length : ns[childRnode].length), sharingFactor);

        int childX = useHotExpand ? hot[childRnode].endX : getEndTileXCoordinate(childRnode);
        int childY = searchEndY(childRnode);
        int sinkRnode = c.sinkRnode;
        int sinkX = getBeginTileXCoordinate(sinkRnode);
        int sinkY = getBeginTileYCoordinate(sinkRnode);
        int deltaX = std::abs(childX - sinkX);
        int deltaY = std::abs(childY - sinkY);
        if (c.isCrossSLR()) {
            int deltaSLR = std::abs(getSLRIndex(sinkRnode) - getSLRIndex(childRnode));
            if (deltaSLR != 0) {
                if (deltaSLR == 1) {
                    int overshootByY = deltaY - superLongLineLength;
                    if (overshootByY < 0) deltaY = superLongLineLength - overshootByY;
                }
                int nextLag = nextLagunaColumn[childX];
                int prevLag = prevLagunaColumn[childX];
                if (nextLag == prevLag) {
                    // on top of the column
                } else {
                    const int IMAX = std::numeric_limits<int>::max();
                    const int IMIN = std::numeric_limits<int>::min();
                    int dToNext, dToPrev, dAndFromNext, dAndFromPrev;
                    if (nextLag == IMAX || nextLag >= c.xMaxBB) { dToNext = IMAX; dAndFromNext = IMAX; }
                    else { dToNext = std::abs(nextLag - childX); dAndFromNext = dToNext + std::abs(sinkX - nextLag); }
                    if (prevLag == IMIN || prevLag <= c.xMinBB) { dToPrev = IMAX; dAndFromPrev = IMAX; }
                    else { dToPrev = std::abs(prevLag - childX); dAndFromPrev = dToPrev + std::abs(sinkX - prevLag); }
                    int det = cfg.maxDetourToSnapBackToPrevLagunaColumn;
                    if (dToNext == dToPrev) deltaX = std::min(dAndFromNext, dAndFromPrev);
                    else if (dToNext < dToPrev && dAndFromNext <= dAndFromPrev + det) deltaX = dAndFromNext;
                    else if (dToPrev < dToNext && dAndFromPrev <= dAndFromNext + det) deltaX = dAndFromPrev;
                    else deltaX = (dToNext < dToPrev) ? dAndFromNext : dAndFromPrev;
                }
            }
        }
        int distanceToSink = deltaX + deltaY;
        float hBase = search_cost_exact::heuristic(st.estWlWeight, distanceToSink, lmkReady,
            st.lmkT, lmkReady ? &lmk[(size_t)childRnode * 8] : nullptr, lmkInvScale);
        float newTotal = search_cost_exact::total_cost(newPartial, hBase, sharingFactor);






        push(st, childRnode, newPartial, newTotal, lookahead);
    }

    void exploreAndExpand(State& st, int rnode) {
        Connection& c = connections[st.connIdx];
        int seq = st.sequence;
        int nw = c.netIdx;
        bool rnodeIsLaguna = nodeLaguna(rnode);

        const std::vector<int>& kids = getChildren(rnode);
        int nk = (int) kids.size();
        for (int ki = 0; ki < nk; ki++) {
            if (doPrefetch && ki + 1 < nk) {
                int nx = kids[ki + 1];
                __builtin_prefetch(&tl_dyn[nx], 1, 3);   // serial/shadow: the label line; sparse crew: tl_dyn
                                                         // aliases the GLOBAL dyn -> warms the hist read
                if (tl_sparse) tl_sparse->prefetch(nx);  // paged probe-only, never inserts (hash mode: no-op)
                if (useHotExpand) {
                    __builtin_prefetch(&hot[nx], 0, 3);   // one line: type/coords/cost/occ/sharing
                } else {
                    __builtin_prefetch(&ns[nx], 0, 3);
                    __builtin_prefetch(&occCnt[nx], 0, 3);
                    __builtin_prefetch(&type[nx], 0, 3);
                    __builtin_prefetch(&ownerNet[nx], 0, 3);
                    __builtin_prefetch(&ownerCnt[nx], 0, 3);
                }
            }
            int childRNode = kids[ki];
            if (TLD(childRNode).visited == seq) continue;
            if (pruneDeadEnd && deadEnd[childRNode]) { prunedPushes++; continue; }
            bool lookahead = false;
            if (TLD(childRNode).target) {
                if (isAnyExclusiveSink(searchType(childRNode))) {
                    st.earlyTermination = true;
                } else {
                    st.earlyTermination = !searchWillOverUse(childRNode, nw);
                }
                if (st.earlyTermination) {
                    st.queue->clear();
                }
            } else {
                if (!isAccessible(childRNode, c)) continue;
                RouteNodeType childType = searchType(childRNode);
                switch (childType) {
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA:
                        lookahead = !searchWillOverUse(childRNode, nw);
                        // fall-through
                    case RouteNodeType::LOCAL_BOTH:
                    case RouteNodeType::LOCAL_EAST:
                    case RouteNodeType::LOCAL_WEST:
                    case RouteNodeType::LOCAL_RESERVED:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        break;
                    case RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA:
                        if (c.isCrossSLR() && getSLRIndex(c.sinkRnode) != getSLRIndex(childRNode) &&
                            ((c.crossSLRnorth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA) ||
                             (c.crossSLRsouth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA))) {
                            lookahead = !searchWillOverUse(childRNode, nw);
                        }
                        // fall-through
                    case RouteNodeType::NON_LOCAL:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        if (!cfg.useUTurnNodes /* && delay>10000 (delay==0) */) { /* never triggers */ }
                        lookahead = lookahead || (rnodeIsLaguna || nodeLaguna(childRNode));
                        break;
                    case RouteNodeType::EXCLUSIVE_SINK_BOTH:
                    case RouteNodeType::EXCLUSIVE_SINK_EAST:
                    case RouteNodeType::EXCLUSIVE_SINK_WEST:
                    case RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL:
                        if (!isAccessibleSink(childRNode, c)) continue;
                        break;
                    case RouteNodeType::SUPER_LONG_LINE:
                        break;
                    default:
                        break;
                }
            }
            evaluateCostAndPush(st, rnode, childRNode, lookahead);
            if (st.earlyTermination) break;
        }
    }

    // ----------------------------------------------------------------- rip up / save
    bool isValidSink(const Connection& c, int rnode) const {
        if (c.sinkRnode == rnode) return true;
        for (int a : c.altSinks) if (a == rnode) return true;
        return false;
    }

    void ripUp(Connection& c) {
        bprof::Scope b_scope(bprof::RIP);
        if (c.rnodes.empty()) return;
        int sinkRnode = c.rnodes[0];
        int begin = 0, end = (int)c.rnodes.size();
        if (sinkRnode == c.sinkRnode && !c.hasAltSinks()) { begin = 1; end = (int)c.rnodes.size() - 1; }
        for (int i = begin; i < end; i++) decrementUser(c.rnodes[i], c.netIdx);
    }

    void updateUsersAndPresentCongestionCost(Connection& c) {
        bprof::Scope b_scope(bprof::COMMIT);
        if (c.rnodes.empty()) return;
        c.routedIter = routeIteration;   // stamp: this conn's rnodes are incremental-updateCost candidates
        int sinkRnode = c.rnodes[0];
        int begin = 0, end = (int)c.rnodes.size();
        if (sinkRnode == c.sinkRnode && !c.hasAltSinks()) { begin = 1; end = (int)c.rnodes.size() - 1; }
        for (int i = begin; i < end; i++) incrementUser(c.rnodes[i], c.netIdx);
    }

    bool saveRouting(Connection& c, int rnode) {
        bprof::Scope b_scope(bprof::BACKTRACE);
        if (!isValidSink(c, rnode)) {
            rnode = c.rnodes.empty() ? rnode : c.rnodes[0];
        }
        c.rnodes.clear();
        int cur = rnode;
        while (cur != -1) {
            // addRnode (bounding box expansion not needed for routing decisions)
            c.rnodes.push_back(cur);
            cur = TLD(cur).prev;
        }
        int sourceRnode = c.rnodes.back();
        return sourceRnode == c.sourceRnode;
    }

    static thread_local bool tl_deferCommit;   // §batch: worker saves the path but the OCCUPANCY commit
                                               // happens serially at batch end (snapshot semantics)
    void finishRouteConnection(Connection& c, int rnode) {
        bool routed = saveRouting(c, rnode);
        c.routed = routed;
        if (routed && !tl_deferCommit) updateUsersAndPresentCongestionCost(c);
    }

    void setAllTargets(Connection& c, State& st) {
        bprof::Scope b_scope(bprof::TARGET_SET);
        TLD(c.sinkRnode).target = 1;
        st.targets.push_back(c.sinkRnode);
        for (int a : c.altSinks) { TLD(a).target = 1; st.targets.push_back(a); }
    }

    void prepareRouteConnection(State& st) {
        Connection& c = connections[st.connIdx];
        ripUp(c);
        setAllTargets(c, st);
        int sourceRnode = c.sourceRnode;
        push(st, sourceRnode, 0.0f, 0.0f, false);
    }

    int corridorM = (int) rwEnvI("RW_CORRIDOR", -1);   // >=0: reroute inside old-path envelope + margin
    std::vector<uint64_t> corrStash;                   // batched reroutes: old-path envelope packed x0|x1|y0|y1,
    std::vector<int> corrStamp;                        // valid iff corrStamp[conn] == routeIteration (one-shot)
    std::atomic<long long> corridorHit{0}, corridorFallback{0};
    long endgameAt = rwEnvI("RW_ENDGAME", -1);         // <0: banked per-band; 0: off; >0: threshold
    bool endgameDone = false;
    float pfRamp1 = rwEnvF("RW_PF_RAMP1", -1.0f);      // >1: iter-1 progressive present-factor ramp;
                                                       // -1 = banked default (3.0 on the 20per band, see below)
    std::atomic<int> rampStage{0};
    std::atomic<int> routedTotal{0};                   // iter progress for the ramp (batched leaves advance it per batch)
    int rampStages = (int) rwEnvI("RW_PF_RAMP1_STAGES", 3);
    int rampTotalWork = 0;

    void routeIndirectConnection(int connIdx, long long budget = -1) {
        btrace::Attempt b_attempt; b_attempt.previousPath = connections[connIdx].rnodes;
        Connection& c = connections[connIdx];
        // Dynamic corridor (RW_CORRIDOR=margin, default OFF): a REROUTE carries last iteration's path,
        // and detours are usually local -- search first inside the old-path envelope + margin (always
        // a SUBSET of the original bbox, so RPTT partition disjointness is preserved), and fall back
        // to the full box if the corridor cannot route (the failure branch clears c.rnodes, so the
        // recursive retry naturally skips the corridor gate). Mid-iteration searches at high pf were
        // measured 3-10x iter-1's per-conn cost (congested wandering); the corridor caps the wander.
        short oxmin = c.xMinBB, oxmax = c.xMaxBB, oymin = c.yMinBB, oymax = c.yMaxBB;
        bool corridor = false;
        bool corrValid = false;
        int exmin = INT32_MAX, exmax = INT32_MIN, eymin = INT32_MAX, eymax = INT32_MIN;
        if (corridorM >= 0 && routeIteration >= 2 && !c.rnodes.empty()) {
            for (int id : c.rnodes) {
                const auto& a = ns[(size_t) id];
                exmin = std::min(exmin, (int) std::min(a.beginX, a.endX));
                exmax = std::max(exmax, (int) std::max(a.beginX, a.endX));
                eymin = std::min(eymin, (int) std::min(a.beginY, a.endY));
                eymax = std::max(eymax, (int) std::max(a.beginY, a.endY));
            }
            corrValid = true;
        } else if (corridorM >= 0 && routeIteration >= 2 &&
                   connIdx < (int) corrStamp.size() && corrStamp[(size_t) connIdx] == routeIteration) {
            // Batched reroute: the publisher ripped and CLEARED rnodes before the crew search -- the
            // envelope was stashed at rip time. One-shot: the full-box retry after a corridor failure
            // (and any bounce retry) must not re-enter the corridor.
            uint64_t p = corrStash[(size_t) connIdx];
            exmin = (short) (p & 0xFFFF); exmax = (short) ((p >> 16) & 0xFFFF);
            eymin = (short) ((p >> 32) & 0xFFFF); eymax = (short) ((p >> 48) & 0xFFFF);
            corrStamp[(size_t) connIdx] = 0;
            corrValid = true;
        }
        if (corrValid) {
            int nxmin = std::max((int) oxmin, exmin - corridorM);
            int nxmax = std::min((int) oxmax, exmax + corridorM);
            int nymin = std::max((int) oymin, eymin - corridorM);
            int nymax = std::min((int) oymax, eymax + corridorM);
            long oldA = (long) (oxmax - oxmin + 1) * (long) (oymax - oymin + 1);
            long newA = (long) (nxmax - nxmin + 1) * (long) (nymax - nymin + 1);
            if (newA * 3 <= oldA * 2) {                  // only pay the retry risk for a real shrink
                c.xMinBB = (short) nxmin; c.xMaxBB = (short) nxmax;
                c.yMinBB = (short) nymin; c.yMaxBB = (short) nymax;
                corridor = true;
            }
        }
        DaryPQ queue(*tl_pq, heapArity);
        State st;
        st.queue = &queue;
        st.connIdx = connIdx;
        // Partition-parallel shares dyn[] across workers, so visited stamps must be globally unique
        // (a per-thread counter could collide with a stamp another thread left on a node in an earlier
        // iteration). Serial/PHASE1 paths keep the per-thread counter (byte-identical default).
        st.sequence = parPart > 0 ? (gSearchSeq.fetch_add(1, std::memory_order_relaxed) + 1) : (int)(++tl_seq);
        st.shareWeight = std::pow(1.0f, cfg.shareExponent);
        st.rnodeWLWeight = 1.0f * (1.0f - wlWeight);
        st.estWlWeight = 1.0f * wlWeight * directedness;   // >1 => more directed (fewer explored, RW_DIRECT)
        if (tl_wid >= 64 && batchDirect > 1.0f) st.estWlWeight *= batchDirect;   // crew searches only
        fillLmkT(st, c.sinkRnode);
        st.earlyTermination = false;

        prepareRouteConnection(st);

        int rnode = -1;
        bool found = false, aborted = false;
        long long pops = 0, sumFront = 0, maxFront = 0;
        // §prune ceiling test: the TIGHTEST admissible upper bound is C* itself (foundLb). A B&B that prunes
        // g+h>UB can only cut EXPANSIONS whose f exceeds UB>=C*. With a consistent h, A* never expands f>C*,
        // so maxPoppedF (max f among expanded non-target nodes) <= foundF => B&B-UB cuts ZERO expansions.
        // Measuring maxPoppedF/foundF thus bounds the entire "h-bounded pruning" idea for free (no old path).
        float maxPoppedLb = -1.0f, foundLb = -1.0f;
        // §h-slack: how much of the true priced optimal cost the base-Manhattan h captures. h(n)=lb-upstream,
        // g(n)=upstream. If h << (C*-g) broadly => h is loose => a tighter admissible (priced coarse) h has
        // room to shrink the f<=C* expanded set. If h ~= (C*-g) => no room => monsters only via GPU accel.
        double sumH = 0, sumG = 0;
        float srcH = measurePops ? st.estWlWeight * (float)(
                         std::abs(getEndTileXCoordinate(c.sourceRnode) - getBeginTileXCoordinate(c.sinkRnode)) +
                         std::abs(getEndTileYCoordinate(c.sourceRnode) - getBeginTileYCoordinate(c.sinkRnode))) : 0.0f;
        while (!queue.empty()) {
            rnode = queue.poll();
            pops++;
            if ((pops & ((1 << 22) - 1)) == 0)   // watchdog: a sane search never gets near 4M pops
                std::fprintf(stderr, "[watchdog] conn=%d iter=%d pops=%lld qsz=%lld node=%d wid=%d\n",
                             connections[connIdx].connId, routeIteration, pops, (long long) queue.sz, rnode, tl_wid);
            float lbp = TLD(rnode).lb;
            if (TLD(rnode).target) { found = true; foundLb = lbp; break; }
            if (budget > 0 && pops > budget) { aborted = true; break; }   // §budget-abort: bail this search to GPU flood
            if (measurePops) {
                long long f = queue.sz; sumFront += f; if (f > maxFront) maxFront = f;
                if (lbp > maxPoppedLb) maxPoppedLb = lbp;
                sumH += (double)(lbp - TLD(rnode).upstream); sumG += (double) TLD(rnode).upstream;
            }
            exploreAndExpand(st, rnode);
        }
        lastPops = pops; lastFoundLb = foundLb;   // per-connection search cost, for the flood-proto harness
        if (connIdx < (int) connLastPops.size()) connLastPops[connIdx] = pops;   // per-index => thread-safe
        if (pops >= 16384 && !occLocking && tl_wid < 0) bigConnsThisIter.push_back(connIdx);   // shared vector: serial only
#ifdef WITH_CUDA
        // A budget-abort IS proof of an expensive search: without `aborted` here, budgeted iter-1
        // probes cap pops below floodMin and the flood would never become eligible for the whole run.
        if (pops >= floodMin || aborted) floodEverEligible = true;
#endif
        if (measurePops) {                 // atomic, once per SEARCH: worker-safe diagnostics
            iterPops.fetch_add(pops, std::memory_order_relaxed);
            long long m = iterMaxPops.load(std::memory_order_relaxed);
            while (pops > m && !iterMaxPops.compare_exchange_weak(m, pops, std::memory_order_relaxed)) {}
            int b = 0; long long v = pops; while (v > 1 && b < 27) { v >>= 1; b++; }
            iterPopHist[b].fetch_add(1, std::memory_order_relaxed);
            if (pops >= frontierMin) {
                // GPU-flood supply profile: meanFront = time-averaged available parallelism; ratio pops/meanFront
                // ~= number of sequential wavefront steps a GPU flood must serialize.
                double meanFront = (double) sumFront / pops;
                double ratio = (foundLb > 0) ? (double) maxPoppedLb / foundLb : -1.0;
                double meanH = sumH / pops, meanG = sumG / pops;
                double srcHr = (foundLb > 0) ? srcH / foundLb : -1.0;                       // source base-h / C*
                double aggSlack = (foundLb > meanG) ? meanH / (foundLb - meanG) : -1.0;      // avg h / avg remaining budget
                std::fprintf(stderr, "MONSTER iter=%d conn=%d pops=%lld meanFront=%.0f maxFront=%lld hpwl=%d bbox=%dx%d foundF=%.1f maxPoppedF=%.1f ratio=%.3f srcHratio=%.3f aggHslack=%.3f\n",
                             routeIteration, connections[connIdx].connId, pops, meanFront, maxFront,
                             (int) connections[connIdx].hpwl,
                             (connections[connIdx].xMaxBB - connections[connIdx].xMinBB),
                             (connections[connIdx].yMaxBB - connections[connIdx].yMinBB),
                             foundLb, maxPoppedLb, ratio, srcHr, aggSlack);
            }
        }

        if (found) {
            queue.clear();
            finishRouteConnection(c, rnode);
            if (!c.routed) {
                std::fprintf(stderr, "ERROR: Unable to save routing for connection %d\n", c.connId);
            }
        } else {
            c.rnodes.clear();
            c.routed = false;
        }

        { bprof::Scope b_scope(bprof::TARGET_CLEAR);
        for (int t : st.targets) TLD(t).target = 0;
        st.targets.clear(); }
        bTraceFinish(b_attempt,connIdx,pops,aborted);
        lastAborted = aborted;   // caller floods this connection on the GPU if it was budget-aborted

        if (corridor) {
            c.xMinBB = oxmin; c.xMaxBB = oxmax; c.yMinBB = oymin; c.yMaxBB = oymax;   // box is persistent state
            if (!c.routed) {                            // corridor missed: one full-box retry (rnodes now empty)
                corridorFallback.fetch_add(1, std::memory_order_relaxed);
                routeIndirectConnection(connIdx, budget);
                return;
            }
            corridorHit.fetch_add(1, std::memory_order_relaxed);
        }
    }

    bool shouldRoute(const Connection& c) const {
        if (!c.routed) return true;
        // isCongested
        for (int rn : c.rnodes) if (isOverUsed(rn)) return true;
        return false;
    }

    int routeIndirectConnections() {
        int n = 0;
        for (int idx : sortedIndirect) {
            if (connections[idx].abandoned) continue;
            if (shouldRoute(connections[idx])) {
#ifdef WITH_CUDA
                if (floodActive && idx < (int) connLastPops.size() && connLastPops[idx] >= floodMin) {
                    gpuFloodRoute(idx); n++; continue;   // predicted-expensive -> GPU flood directly (no probe)
                }
                if (floodActive && floodHedge) {         // hedge: CPU + concurrent flood race, no probe/over-flood
                    routeConnectionHedge(idx); n++; continue;
                }
                if (floodActive && floodBudget > 0) {    // budget-abort: cap the CPU search; if it blows the
                    routeIndirectConnection(idx, floodBudget);   // budget it was a first-search miss -> flood it
                    if (lastAborted) gpuFloodRoute(idx);
                    n++; continue;
                }
#endif
                int aslot = -1;
                if (alphaProbeIter > 0 && idx < (int) alphaSlot.size() && alphaSlot[idx] >= 0) {
                    // COMMIT-TIME conflict test: rip c (match the fresh-search occupancy) and check whether the
                    // iter-start presearched path still avoids every foreign net at this point in the iteration.
                    aslot = alphaSlot[idx]; Connection& c = connections[idx]; auto& ps = alphaPathStart[aslot]; int ni = c.netIdx;
                    alphaSeen[aslot] = 1;                             // this sampled connection actually reached the router
                    std::vector<int> savedOld = c.rnodes; bool savedRouted = c.routed;
                    ripUp(c);
                    bool cf = !ps.empty();
                    for (int j = 1; j + 1 < (int) ps.size() && cf; j++) {
                        int nd = ps[j]; int own = countConnectionsOfUser(nd, ni) > 0 ? 1 : 0;
                        if (getOccupancy(nd) - own > 0) cf = false;   // a foreign net occupies this node
                    }
                    alphaCommitCF[aslot] = cf ? 1 : 0;
                    c.rnodes = savedOld; c.routed = savedRouted;      // restore; routeIndirectConnection rips it again
                    if (!c.rnodes.empty()) updateUsersAndPresentCongestionCost(c);
                }
                routeIndirectConnection(idx); n++;
                if (aslot >= 0) {
                    alphaPops[aslot] = (int) lastPops;                // fresh-search volume => masses (<4k) vs monster
                    // COST alpha: reprice BOTH the presearched path and the just-committed fresh path with the SAME
                    // function at the SAME state => an exact match is cost-equal by construction; accept if the
                    // presearched path is within 5% of the fresh path (would commit it with no quality loss).
                    Connection& c = connections[idx]; auto& ps = alphaPathStart[aslot];
                    if (c.routed && !c.rnodes.empty()) {
                        float fg = repriceG(c.rnodes, c), pg = repriceG(ps, c);
                        alphaCostAcc[aslot] = (fg > 0 && pg <= fg * 1.05f) ? 1 : 0;
                    } else alphaCostAcc[aslot] = 0;
                }
            }
        }
        return n;   // #connections actually (re)routed this iteration (for long-tail profiling)
    }

    // ===== Phase-1 parallel prototype: route the connections that (re)route this iteration across `T` threads.
    // Each thread owns its search scratch (tl_dyn copy of dyn + tl_pq + tl_seq); occupancy is shared and LIVE
    // (striped locks, occLocking=true) so a commit by one thread is immediately visible to the others -- the
    // GRoute occupancy model. Dynamic work-stealing (atomic cursor) balances the skewed per-connection cost.
    int routeIndirectConnectionsParallel(int T) {
        std::vector<int> work;
        for (int idx : sortedIndirect)
            if (!connections[idx].abandoned && shouldRoute(connections[idx])) work.push_back(idx);
        if (nodeLocks.empty()) nodeLocks = std::vector<NodeSpin>(NLOCK);
        int N = numNodes();
        if (apxShare && !parNoShare) {                    // seed lock-free approx occupancy from the exact state
            if ((int) apxOwner.size() != N) { apxOwner = std::vector<std::atomic<int>>(N); apxCnt = std::vector<std::atomic<int>>(N); apxOcc = std::vector<std::atomic<int>>(N); }
            for (int i = 0; i < N; i++) {
                apxOcc[i].store(occCnt[i], std::memory_order_relaxed);
                int o = ownerNet[i];
                if (o >= 0) { apxOwner[i].store(o, std::memory_order_relaxed); apxCnt[i].store(ownerCnt[i], std::memory_order_relaxed); }
                else { apxOwner[i].store(-1, std::memory_order_relaxed); apxCnt[i].store(0, std::memory_order_relaxed); }
            }
        }
        std::vector<std::vector<int>> oldPaths;           // for the exact post-join rebuild (apx did not touch occCnt/owner-slot)
        if (apxShare && !parNoShare) { oldPaths.resize(work.size()); for (size_t i = 0; i < work.size(); i++) oldPaths[i] = connections[work[i]].rnodes; }
        if ((int) threadDyn.size() < T) { threadDyn.resize(T); threadPq.resize(T); }
        auto _c0 = std::chrono::steady_clock::now();
        for (int t = 0; t < T; t++) { threadDyn[t] = dyn; threadPq[t].clear(); }   // per-thread scratch = copy of dyn (prevInit, hist)
        double _copyS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _c0).count();
        auto _w0 = std::chrono::steady_clock::now();
        std::atomic<size_t> cursor{0};
        std::atomic<int> done{0};
        occLocking = true;
        auto worker = [&](int t) {
            tl_dyn = threadDyn[t].data(); tl_pq = &threadPq[t]; tl_seq = 0;
            for (;;) {
                size_t i = cursor.fetch_add(1, std::memory_order_relaxed);
                if (i >= work.size()) break;
                routeIndirectConnection(work[i]);
            }
            done.fetch_add(1, std::memory_order_relaxed);
        };
        std::vector<std::thread> ths;
        for (int t = 0; t < T; t++) ths.emplace_back(worker, t);
        for (auto& th : ths) th.join();
        occLocking = false;
        tl_dyn = dyn.data(); tl_pq = &pqStorage;              // restore main-thread serial aliases
        double _workS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _w0).count();
        double _rebS = 0.0;
        if (apxShare && !parNoShare) {                        // exact rebuild: apply each work conn's (new - old) path delta
            auto _r0 = std::chrono::steady_clock::now();
            for (size_t i = 0; i < work.size(); i++) {
                Connection& c = connections[work[i]];
                std::vector<int> newPath = c.rnodes;
                c.rnodes = oldPaths[i]; ripUp(c);             // remove old (serial, exact map)
                c.rnodes = newPath; if (c.routed && !newPath.empty()) updateUsersAndPresentCongestionCost(c);
            }
            _rebS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _r0).count();
        }
        std::fprintf(stderr, "[par-iter1] T=%d conns=%zu apx=%d noshare=%d scratchCopy=%.2fs parallelSearch=%.2fs exactRebuild=%.2fs\n",
                     T, work.size(), (int) apxShare, (int) parNoShare, _copyS, _workS, _rebS);
        if (parNoShare) { std::fflush(stderr); std::exit(0); }   // discriminator: timing-only, stop after iter-1
        return (int) work.size();
    }

    // ===== Overlap-tolerant LIVE parallel routing (RW_OVERLAP=T) ==================================
    // The TRUE-overlap variant the snapshot family could not be (ledger 18/20/21): workers route
    // concurrently against LIVE lock-free approximate occupancy (PHASE1 apx machinery), so every
    // finished commit is immediately visible to subsequent expansions -- in-flight blindness is
    // bounded by the worker count (~T conns), not a batch or an iteration. Per-worker search labels
    // live in the P1 mmap-lazy shadow NodeDyn (zero pages = unvisited; hist reads are global by
    // design); shadows are MADV_DONTNEED-reset at every boundary so residency stays bounded by the
    // per-iteration touch set. The shared exact occupancy is rebuilt serially from path deltas after
    // the join (identical to PHASE1), so iteration boundaries see exact state. DETERMINISM IS
    // DELIBERATELY GIVEN UP in this mode (in-flight timing affects which staleness a search sees);
    // legality is enforced by the usual gates (in-memory verify + external checker + Vivado).
    int routeIndirectConnectionsOverlap(int T) {
        std::vector<int> work;
        for (int idx : sortedIndirect)
            if (!connections[idx].abandoned && shouldRoute(connections[idx])) work.push_back(idx);
        if (work.empty()) return 0;
        {   // Conflict-aware interleave (P1' ordering, reused): round-robin over direction-octant x
            // length-band buckets so concurrently-IN-FLIGHT conns want different corridors.
            std::vector<std::vector<int>> bk(32);
            for (int idx : work) {
                const Connection& c = connections[idx];
                int dx = getBeginTileXCoordinate(c.sinkRnode) - getEndTileXCoordinate(c.sourceRnode);
                int dy = getBeginTileYCoordinate(c.sinkRnode) - getEndTileYCoordinate(c.sourceRnode);
                int dir = (dx >= 0 ? 1 : 0) | (dy >= 0 ? 2 : 0) | (std::abs(dx) > std::abs(dy) ? 4 : 0);
                int h = (int) c.hpwl;
                int band = h < 8 ? 0 : h < 24 ? 1 : h < 64 ? 2 : 3;
                bk[(size_t) (dir * 4 + band)].push_back(idx);
            }
            std::vector<int> cw; cw.reserve(work.size());
            for (size_t round = 0; cw.size() < work.size(); round++)
                for (auto& v : bk)
                    if (round < v.size()) cw.push_back(v[(size_t) round]);
            work.swap(cw);
        }
        // Per-worker SPARSE labels (ledger-18 prescription): node-indexed shadows OOM'd (E18: THP
        // faulted 2MB/touch -> 83GB; 4KB pages + windowed DONTNEED still ~50GB + 500s of kernel time,
        // E18b) -- roaming workers need working sets proportional to what they TOUCH, not the graph.
        if ((int) overlapLabels.size() < T) overlapLabels.resize((size_t) T);
        if ((int) overlapPq.size() < T) overlapPq.resize((size_t) T);
        for (int t = 0; t < T; t++)
            if (overlapLabels[(size_t) t].mask == 0) overlapLabels[(size_t) t].init(1 << 17);
        if (nodeLocks.empty()) nodeLocks = std::vector<NodeSpin>(NLOCK);
        const int N = numNodes();
        if ((int) apxOwner.size() != N) { apxOwner = std::vector<std::atomic<int>>(N); apxCnt = std::vector<std::atomic<int>>(N); apxOcc = std::vector<std::atomic<int>>(N); }
        {   // seed lock-free approx occupancy from the exact state (parallel: workers are idle here)
            const int ST = std::max(1, T);
            parForN((size_t) N, ST, [&](int, size_t lo, size_t hi) {
                for (size_t i = lo; i < hi; i++) {
                    apxOcc[i].store(occCnt[i], std::memory_order_relaxed);
                    int o = ownerNet[i];
                    if (o >= 0) { apxOwner[i].store(o, std::memory_order_relaxed); apxCnt[i].store(ownerCnt[i], std::memory_order_relaxed); }
                    else { apxOwner[i].store(-1, std::memory_order_relaxed); apxCnt[i].store(0, std::memory_order_relaxed); }
                }
            });
        }
        std::vector<std::vector<int>> oldPaths(work.size());   // exact post-join rebuild needs the deltas
        for (size_t i = 0; i < work.size(); i++) oldPaths[i] = connections[work[i]].rnodes;
        const bool savedApx = apxShare;
        apxShare = true;
        occLocking = true;
        std::atomic<size_t> cursor{0};
        auto _w0 = std::chrono::steady_clock::now();
        std::vector<std::thread> ths;
        for (int t = 0; t < T; t++) ths.emplace_back([&, t]() {
            tl_dyn = dyn.data();                         // labels are read via TLD -> the sparse store
            tl_sparse = &overlapLabels[(size_t) t];
            tl_pq = &overlapPq[(size_t) t];
            tl_wid = 64 + t; tl_seq = 0;
            for (;;) {
                size_t i = cursor.fetch_add(1, std::memory_order_relaxed);
                if (i >= work.size()) break;
                tl_sparse->reset();                      // O(1): epoch bump invalidates all labels
                routeIndirectConnection(work[i]);        // ripUp + search + IMMEDIATE apx commit (live)
            }
            tl_sparse = nullptr;
        });
        for (auto& th : ths) th.join();
        occLocking = false;
        apxShare = savedApx;
        tl_dyn = dyn.data(); tl_pq = &pqStorage; tl_wid = -1;
        double _workS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _w0).count();
        auto _r0 = std::chrono::steady_clock::now();
        for (size_t i = 0; i < work.size(); i++) {       // exact rebuild: apply (new - old) path deltas
            Connection& c = connections[work[i]];
            std::vector<int> newPath = c.rnodes;
            bool newRouted = c.routed;
            c.rnodes = oldPaths[i]; ripUp(c);            // remove old occupancy (serial, exact map)
            c.rnodes = std::move(newPath);
            c.routed = newRouted;
            if (c.routed && !c.rnodes.empty()) updateUsersAndPresentCongestionCost(c);
        }
        double _rebS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _r0).count();
        std::fprintf(stderr, "[overlap] iter=%d T=%d conns=%zu search=%.2fs rebuild=%.2fs\n",
                     routeIteration, T, work.size(), _workS, _rebS);
        return (int) work.size();
    }

    // batchEnsure with an explicit crew size (the overlap mode may want more workers than batchT).
    bool batchEnsureT(int T) {
        if (T > (int) bws.size() && batchTried) { batchTried = false; batchOk = false; }   // grow: re-ensure
        int saved = batchT;
        batchT = std::max(batchT, T);
        bool ok = batchEnsure();
        batchT = saved;
        return ok;
    }

    // ===================== RPTT partition-parallel routing (RW_PAR_PART=T) =========================
    // CUFR/ParaDRo scheme, adapted:
    //   * Recursive ternary partition tree over connection bboxes (balance-driven cutline selection;
    //     straddlers -> "middle" child keeping the parent box). Built ONCE from the full sorted
    //     connection list and reused every iteration -- re-partitioning per iteration destroys
    //     negotiation convergence (measured in the Java CUFR work).
    //   * One task per tree LEAF; a leaf routes its connections serially in global sorted order.
    //     DAG edge middle-leaf -> side-leaf for every internal node (kept only when the two leaves'
    //     conn-bbox unions overlap, RW_PAR_OVERLAP=1), executed by T workers with critical-path-first
    //     dispatch and an EMA per-leaf cost model refreshed every iteration (Java CUFR scheduler).
    //   * Correctness: the A* search is strictly bbox-bounded, so bbox-disjoint connections touch
    //     disjoint node sets -- all per-node state (dyn labels, occupancy owner slots, children cache)
    //     stays single-writer WITHOUT locks or atomics; bbox-overlapping connections always sit on an
    //     ancestor-descendant chain of the tree (two boxes sharing a column cannot be separated by any
    //     cut) and every overlapping leaf pair is ordered by a DAG edge => the result is deterministic
    //     and independent of thread count / dispatch timing.
    //   * SLL caveat: SUPER_LONG_LINE nodes report a prev-dependent DYNAMIC end-Y coordinate, so a
    //     Y-cut could otherwise put one SLL inside two Y-disjoint bboxes (approached from opposite
    //     ends). X coordinates are fully static, hence: X-cuts anywhere, Y-cuts only where the node's
    //     conn X-span contains no laguna/SLL column.
    //   * GPU flood: leaf workers hand monsters/budget-aborts to the single-connection flood under a
    //     global GPU mutex with per-thread live-price dirty lists; each flood's rip-up/commit stays in
    //     the calling leaf's territory, so disjointness is preserved. (Java CUFR has no flood assist --
    //     this is how the un-cuttable hotspot leaf, its hard serial ceiling, gets extra acceleration.)
    struct PTNode {
        int x0, y0, x1, y1;          // conn-bbox span of this node (mid keeps the parent box)
        std::vector<int> conns;      // connection idxs owned by this node, in global sorted order
        int left = -1, right = -1, mid = -1;
    };
    struct PTask {
        int node = -1;               // ptree leaf index
        int ux0 = 0, uy0 = 0, ux1 = 0, uy1 = 0;   // union of member conn bboxes
        std::vector<int> out;        // dependent task ids (every edge goes low -> high index)
        int indegInit = 0;
        double estNs = 0;            // EMA leaf cost (ns); seeded flat per connection like Java CUFR
        double crit = 0;             // critical-path priority, recomputed every iteration
    };
    std::vector<PTNode> ptree;
    std::vector<PTask> ptasks;
    std::unique_ptr<std::atomic<int>[]> taskIndeg;
    bool ptBuilt = false;
    // [par-stats] per-iteration instrumentation (research front b: where does the speedup go)
    std::vector<double> ptActNs;                       // actual per-task ns this iteration
    std::atomic<long long> parIdleNs{0};               // worker time blocked on the ready queue
    std::atomic<long long> laneWaitNs{0};              // time blocked waiting for a free GPU lane

    void ptBuildTree() {
        // SLL hazard model (the only dynamic-position nodes): a Y-cut at p is unsafe iff some
        // SUPER_LONG_LINE's Y-interval strictly straddles the cut (endpoints on both sides -- then a
        // below-conn can reach it via its low endpoint and an above-conn via its high endpoint, both
        // passing the dynamic getEndTileYCoordinate bbox check) AND the node's conn X-span contains a
        // laguna column. SLL intervals cluster around the SLR boundaries, so most Y positions stay
        // cuttable even where the X-span is wide.
        int maxX = 0, maxY = 0;
        for (int i = 0, N = numNodes(); i < N; i++) {
            if (ns[i].endX > maxX) maxX = ns[i].endX;
            if (ns[i].endY > maxY) maxY = ns[i].endY;
            if (ns[i].beginY > maxY) maxY = ns[i].beginY;
        }
        std::vector<int> lagPre((size_t) maxX + 3, 0);
        std::vector<char> sllBad((size_t) maxY + 2, 0);
        {
            std::vector<char> lag((size_t) maxX + 2, 0);
            for (int i = 0, N = numNodes(); i < N; i++) {
                if (ns[i].isLaguna || type[i] == RouteNodeType::SUPER_LONG_LINE) {
                    int bx = ns[i].beginX, ex = ns[i].endX;
                    if (bx >= 0 && bx <= maxX + 1) lag[bx] = 1;
                    if (ex >= 0 && ex <= maxX + 1) lag[ex] = 1;
                }
                if (type[i] == RouteNodeType::SUPER_LONG_LINE) {
                    int ya = std::min((int) ns[i].beginY, (int) ns[i].endY);
                    int yb = std::max((int) ns[i].beginY, (int) ns[i].endY);
                    for (int y = std::max(ya, 0); y <= std::min(yb - 1, maxY + 1); y++) sllBad[y] = 1;
                }
            }
            if (lazy) {
                // Lazy graph: only interned nodes (mostly seeds at build time) are scannable, so the
                // node scan alone UNDERCOUNTS laguna/SLL geography and could legalize an unsafe Y-cut.
                // Union in the DEVICE-level knowledge from the problem header: laguna columns from
                // nextLagunaColumn, and conservative SLL bands (SLR boundary +- SLL length) for sllBad.
                for (int x = 0; x < (int) nextLagunaColumn.size() && x <= maxX + 1; x++)
                    if (nextLagunaColumn[x] == x) lag[x] = 1;
                for (size_t y = 1; y < intYToSLRIndex.size(); y++)
                    if (intYToSLRIndex[y] != intYToSLRIndex[y - 1]) {
                        int lo = (int) y - superLongLineLength - 1, hi = (int) y + superLongLineLength;
                        for (int p = std::max(lo, 0); p <= std::min(hi, maxY + 1); p++) sllBad[(size_t) p] = 1;
                    }
            }
            for (int x = 0; x <= maxX + 1; x++) lagPre[x + 1] = lagPre[x] + (lag[x] ? 1 : 0);
        }
        auto lagInside = [&](int lo, int hi) {   // any laguna/SLL column strictly inside (lo, hi)?
            int a = std::max(lo + 1, 0), b = std::min(hi - 1, maxX + 1);
            return a <= b && lagPre[b + 1] - lagPre[a] > 0;
        };
        auto sllBadAt = [&](int y) { return y >= 0 && y <= maxY + 1 && sllBad[(size_t) y]; };

        const int devX = maxX + 1, devY = maxY + 1;      // device-ish bounds (Java clampX/clampY analog)
        auto clampDX = [&](int x) { return std::min(std::max(x, 0), devX); };
        auto clampDY = [&](int y) { return std::min(std::max(y, 0), devY); };

        ptree.clear();
        {
            PTNode root; root.x0 = 0; root.y0 = 0; root.x1 = devX; root.y1 = devY;   // region box (Java root = device box)
            for (int idx : sortedIndirect)
                if (!connections[idx].abandoned) root.conns.push_back(idx);
            ptree.push_back(std::move(root));
        }
        std::vector<int> stk{0};
        while (!stk.empty()) {
            const int ni = stk.back(); stk.pop_back();
            std::vector<int> conns = std::move(ptree[ni].conns);   // ptree may reallocate below
            const int n = (int) conns.size();
            const int bx0 = ptree[ni].x0, bx1 = ptree[ni].x1, by0 = ptree[ni].y0, by1 = ptree[ni].y1;
            if (n <= 4) { ptree[ni].conns = std::move(conns); continue; }   // tiny leaf
            // conn X-span (for the SLL/laguna Y-cut legality test only)
            int sx0 = std::numeric_limits<int>::max(), sx1 = std::numeric_limits<int>::min();
            for (int idx : conns) {
                const Connection& c = connections[idx];
                sx0 = std::min(sx0, (int) c.xMinBB); sx1 = std::max(sx1, (int) c.xMaxBB);
            }
            const bool lagX = lagInside(sx0, sx1);   // X-span holds a laguna column -> SLL-straddling Y cuts unsafe
            // Balance-driven cutline (CUFR Algorithm 2, faithful port): cut between pos and pos+1;
            // before[p] = #conns whose (node-clamped) interval has STARTED by p (touches the left side),
            // after[p]  = #conns whose interval ENDS past p (touches the right side) -- straddlers count on
            // BOTH sides. Skip the degenerate ends (before == value at last pos / after == value at pos 0);
            // score = |before-after| / max(before,after), lower is better, best across both axes.
            const int W = bx1 - bx0 + 1, H = by1 - by0 + 1;
            int bestAxis = -1, bestPos = 0; double bestScore = std::numeric_limits<double>::max();
            long endSkips = 0, sllSkips = 0;             // [pt-leaf] why did a big region end up un-cuttable?
            for (int axis = 0; axis < 2; axis++) {
                const int lo = axis ? by0 : bx0;
                const int len = (axis ? H : W) - 1;      // cut positions p in [0, len-1] (between lo+p, lo+p+1)
                if (len < 1) continue;
                std::vector<int> startAt((size_t) len + 1, 0), endAt((size_t) len + 1, 0);
                for (int idx : conns) {
                    const Connection& c = connections[idx];
                    int mn, mx;
                    if (axis) { mn = std::max(by0, clampDY(c.yMinBB)) - by0; mx = std::min(by1, clampDY(c.yMaxBB)) - by0; }
                    else      { mn = std::max(bx0, clampDX(c.xMinBB)) - bx0; mx = std::min(bx1, clampDX(c.xMaxBB)) - bx0; }
                    if (mn <= len - 1) startAt[(size_t) std::max(mn, 0)]++;          // contributes to before[p>=mn]
                    if (mx >= 1) endAt[(size_t) std::min(mx, len)]++;                // contributes to after[p<mx]
                }
                std::vector<int> before((size_t) len, 0), after((size_t) len, 0);
                int acc = 0;
                for (int p = 0; p < len; p++) { acc += startAt[(size_t) p]; before[(size_t) p] = acc; }
                acc = 0;
                for (int p = len - 1; p >= 0; p--) { acc += endAt[(size_t) p + 1]; after[(size_t) p] = acc; }
                const int maxB = before[(size_t) len - 1], maxA = after[0];
                for (int p = 0; p < len; p++) {
                    const int b = before[(size_t) p], a = after[(size_t) p];
                    if (b == maxB || a == maxA) { endSkips++; continue; }            // touches-everything end cut
                    if (axis == 1 && lagX && sllBadAt(lo + p)) { sllSkips++; continue; }  // SLL straddles this Y position
                    const double score = (double) std::abs(b - a) / (double) std::max(std::max(b, a), 1);
                    if (score < bestScore) { bestScore = score; bestAxis = axis; bestPos = lo + p; }
                }
            }
            if (bestAxis < 0) {
                if (n > 2000)
                    std::fprintf(stderr, "[pt-leaf] UNCUT n=%d box=%d..%d x %d..%d endSkip=%ld sllSkip=%ld lagX=%d\n",
                                 n, bx0, bx1, by0, by1, endSkips, sllSkips, (int) lagX);
                ptree[ni].conns = std::move(conns); continue;                        // un-cuttable -> leaf
            }
            PTNode L, R, M;
            for (int idx : conns) {
                const Connection& c = connections[idx];
                const int mn = bestAxis ? clampDY(c.yMinBB) : clampDX(c.xMinBB);
                const int mx = bestAxis ? clampDY(c.yMaxBB) : clampDX(c.xMaxBB);
                if (mx <= bestPos) L.conns.push_back(idx);
                else if (mn >= bestPos + 1) R.conns.push_back(idx);
                else M.conns.push_back(idx);
            }
            if (L.conns.empty() || R.conns.empty()) {
                if (n > 2000)
                    std::fprintf(stderr, "[pt-leaf] NOPROG n=%d box=%d..%d x %d..%d axis=%d pos=%d (L=%zu R=%zu M=%zu)\n",
                                 n, bx0, bx1, by0, by1, bestAxis, bestPos, L.conns.size(), R.conns.size(), M.conns.size());
                ptree[ni].conns = std::move(conns); continue;                        // no progress
            }
            if (bestAxis == 0) {
                L.x0 = bx0; L.x1 = bestPos;     L.y0 = by0; L.y1 = by1;
                R.x0 = bestPos + 1; R.x1 = bx1; R.y0 = by0; R.y1 = by1;
            } else {
                L.x0 = bx0; L.x1 = bx1; L.y0 = by0; L.y1 = bestPos;
                R.x0 = bx0; R.x1 = bx1; R.y0 = bestPos + 1; R.y1 = by1;
            }
            M.x0 = bx0; M.x1 = bx1; M.y0 = by0; M.y1 = by1;   // straddlers roam the whole parent box
            const int li = (int) ptree.size(); ptree.push_back(std::move(L)); ptree[ni].left = li; stk.push_back(li);
            const int ri = (int) ptree.size(); ptree.push_back(std::move(R)); ptree[ni].right = ri; stk.push_back(ri);
            if (!M.conns.empty()) {
                const int mi = (int) ptree.size(); ptree.push_back(std::move(M)); ptree[ni].mid = mi; stk.push_back(mi);
            }
        }
    }

    // Collect leaves DFS mid -> left -> right (so every DAG edge runs low -> high task index) and add
    // the middle-gates-sides dependency edges, overlap-filtered when RW_PAR_OVERLAP=1.
    std::pair<int,int> ptCollect(int ni) {
        PTNode& nd = ptree[ni];
        const int first = (int) ptasks.size();
        if (nd.left < 0 && nd.right < 0 && nd.mid < 0) {
            PTask t; t.node = ni;
            t.ux0 = t.uy0 = std::numeric_limits<int>::max();
            t.ux1 = t.uy1 = std::numeric_limits<int>::min();
            for (int idx : nd.conns) {
                const Connection& c = connections[idx];
                t.ux0 = std::min(t.ux0, (int) c.xMinBB); t.ux1 = std::max(t.ux1, (int) c.xMaxBB);
                t.uy0 = std::min(t.uy0, (int) c.yMinBB); t.uy1 = std::max(t.uy1, (int) c.yMaxBB);
            }
            t.estNs = 100000.0 * (double) nd.conns.size();   // flat 100us/conn seed (Java CUFR)
            ptasks.push_back(std::move(t));
            return {first, first + 1};
        }
        // Straddlers (mid) must never run concurrently with their sides. Default (CUFR): mid subtree
        // collected FIRST, edges mid-leaf -> side-leaf. RW_PAR_MIDLAST=1: sides first, edges side -> mid.
        std::pair<int,int> gate{first, first};   // the range collected first (gates the later range)
        if (!parMidLast) {
            if (nd.mid >= 0) gate = ptCollect(nd.mid);
            if (nd.left >= 0) ptCollect(nd.left);
            if (nd.right >= 0) ptCollect(nd.right);
        } else {
            if (nd.left >= 0) ptCollect(nd.left);
            if (nd.right >= 0) ptCollect(nd.right);
            gate = {first, (int) ptasks.size()};
            if (nd.mid >= 0) ptCollect(nd.mid);
        }
        const int last = (int) ptasks.size();
        for (int g = gate.first; g < gate.second; g++) {
            PTask& tg = ptasks[g];
            for (int s = gate.second; s < last; s++) {
                PTask& ts = ptasks[s];
                if (parOverlapEdges &&
                    !(tg.ux0 < ts.ux1 && ts.ux0 < tg.ux1 && tg.uy0 < ts.uy1 && ts.uy0 < tg.uy1))
                    continue;                                  // spatially disjoint -> false dependency, drop
                tg.out.push_back(s); ts.indegInit++;
            }
        }
        return {first, last};
    }

    void ptReport() {
        size_t maxLeaf = 0; long tot = 0;
        for (auto& t : ptasks) { size_t s = ptree[t.node].conns.size(); tot += (long) s; if (s > maxLeaf) maxLeaf = s; }
        std::vector<double> f(ptasks.size(), 0.0);
        double span = 0;
        for (int i = (int) ptasks.size() - 1; i >= 0; i--) {
            double m = 0; for (int s : ptasks[i].out) m = std::max(m, f[(size_t) s]);
            f[(size_t) i] = (double) ptree[ptasks[(size_t) i].node].conns.size() + m;
            span = std::max(span, f[(size_t) i]);
        }
        std::fprintf(stderr, "[par] report: leaves=%zu conns=%ld maxLeaf=%zu span=%.0f structCeiling=%.2fx\n",
                     ptasks.size(), tot, maxLeaf, span, span > 0 ? (double) tot / span : 0.0);
    }

    // ===== §batch-snapshot parallel (overlap-tolerant P1, ledger §18) =========================
    // The un-cuttable straddler cores (pairwise-overlapping bboxes) are the whole critical chain
    // (crit/wall=1.0). Inside such a leaf we route in BATCHES: serial rip-up of the batch -> all
    // workers search CONCURRENTLY against the frozen occupancy snapshot (occupancy/hot[]/hist are
    // only mutated by commits, which are deferred) -> serial commit in original order. End state
    // depends only on batch composition + commit order => fully deterministic. Each worker gets a
    // PRIVATE lazily-committed mmap shadow of the NodeDyn scratch (tl_dyn is a thread-local alias,
    // so the whole search core is reused unchanged); the only persistent NodeDyn field (hist) is
    // read from the global array. WL cost = one-batch price staleness, bounded by RW_BATCH_B.
    // DEFAULT OFF (RW_BATCH_MIN=2000 to enable): P1 measured verdict -- batched cores get 2-3x faster
    // individually (22494 conns: 0.87s vs ~2-3s serial, pops normal), BUT snapshot routing inside
    // pairwise-overlapping cores collides BY CONSTRUCTION (all conns cross one point): iter-1 overuse
    // 66k->167k (B=192) / 127k (B=24), iter-8 still 15k overused (normal: 81) -> convergence broken at
    // any batch width. Next design (P1'): conflict-aware member selection + within-iteration pricing.
    int batchMin = (int) rwEnvI("RW_BATCH_MIN", 0);    // batch leaves with >= this many conns (0=off)
    int batchB   = (int) rwEnvI("RW_BATCH_B", 32);     // batch width = K-step pricing granularity (batches
                                                       // commit before the next starts -> price staleness <= B)
    int batchIterMin = (int) rwEnvI("RW_BATCH_ITER_MIN", 3);   // conservative: batch only once congestion has
                                                       // taken shape (iter-1/2 snapshot errors were fatal, ledger 20)
    int batchIterMax = (int) rwEnvI("RW_BATCH_ITER_MAX", 1 << 30);   // fuse: stop batching past this iteration
                                                       // (mid-tail reroute sets are conflict-selected hotspots)
    int batchT   = (int) rwEnvI("RW_BATCH_T", 16);     // worker crew per batched leaf
    int batchSparse = (int) rwEnvI("RW_BATCH_SPARSE", 1);   // 1: per-worker SparseLabels instead of mmap
                                                       // NodeDyn shadows -- fat-core crews roam most of the
                                                       // device, THP shadows fault multi-GB/worker (E18);
                                                       // sparse keeps the working set O(touched) (E19 rx)
    int batchLpf = (int) rwEnvI("RW_BATCH_LPF", 1);    // long-pole-first claim order inside a batch (schedule
                                                       // only -- commit order stays fixed, results unchanged)
    int batchRollback = (int) rwEnvI("RW_BATCH_ROLLBACK", 1);   // optimistic-concurrency commit: a conn whose
                                                       // path touches a node re-priced by an EARLIER commit of
                                                       // this batch was searched on stale prices -> reroute it
                                                       // serially with live prices instead of committing blind.
                                                       // Diverse cores pay ~nothing; hotspot sets degrade toward
                                                       // exact serial semantics instead of poisoning convergence.
    int batchPaged = (int) rwEnvI("RW_BATCH_PAGED", 1);   // sparse-label engine: 1 = paged pool (flat-array
                                                       // speed, ~O(touched/conn) memory), 0 = hash table
    long long batchBudget = rwEnvI("RW_BATCH_BUDGET", 1 << 20);   // crew search pops cap: pf-max runaway
                                                       // monsters (measured 12.6M pops, ~50M nodes touched)
                                                       // balloon 24 paged pools to ~80GB (E-L OOM) and stall
                                                       // the batch wall; over-budget conns fall back to the
                                                       // exact serial path on the publisher
    struct BatchWorker { NodeDyn* shadow = nullptr; std::vector<DaryPQ::E> pq; };
    std::vector<BatchWorker> bws;
    std::vector<SparseLabels> batchLabels;              // crew-private label stores (separate from the live
                                                        // overlap mode's hash-configured overlapLabels)
    std::vector<SparseLabels> overlapLabels;            // overlap-tolerant mode: per-worker sparse labels
    std::vector<std::vector<DaryPQ::E>> overlapPq;
    std::mutex batchSectionMu;                          // one batched leaf at a time (cores are chained anyway)
    bool batchTried = false, batchOk = false;
    long long batchedConns = 0, batchedLeaves = 0;

    bool batchEnsure() {
        if (batchTried) return batchOk;
        batchTried = true;
        if (batchT < 2) return batchOk = false;
        if (batchSparse) {                               // E19 prescription: labels proportional to touch set
            if ((int) batchLabels.size() < batchT) batchLabels.resize((size_t) batchT);
            if ((int) overlapPq.size() < batchT) overlapPq.resize((size_t) batchT);
            for (int t = 0; t < batchT; t++) {
                SparseLabels& L = batchLabels[(size_t) t];
                if (batchPaged) { if (!L.paged) L.initPaged(ns.capacity(), (int) rwEnvI("RW_BATCH_PBITS", 9)); }
                else if (L.mask == 0) L.init(1 << 17);
            }
            std::fprintf(stderr, "[batch] ON (%s labels): min=%d B=%d T=%d lpf=%d rollback=%d\n",
                         batchPaged ? "paged" : "sparse", batchMin, batchB, batchT, batchLpf, batchRollback);
            return batchOk = true;
        }
        bws.resize((size_t) batchT);
        size_t bytes = sizeof(NodeDyn) * ns.capacity();  // capacity: ids are stable post-prepass (eager)
        for (auto& w : bws) {
            void* p = mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
            if (p == MAP_FAILED) { std::fprintf(stderr, "[batch] shadow mmap failed -> serial\n"); return batchOk = false; }
            madvise(p, bytes, MADV_HUGEPAGE);            // 4KB pages tax every scratch access (TLB+fault); THP kills it
            w.shadow = (NodeDyn*) p;                     // zero pages: lb/upstream/prev/visited/target all 0
        }
        std::fprintf(stderr, "[batch] ON: min=%d B=%d T=%d shadow=%.1fGB virtual/worker\n",
                     batchMin, batchB, batchT, sizeof(NodeDyn) * ns.capacity() / 1e9);
        return batchOk = true;
    }

    int routeLeafBatched(PTNode& nd) {
        std::lock_guard<std::mutex> sg(batchSectionMu);
        if (!batchEnsure()) return -1;
        std::vector<int> mem;
        mem.reserve(nd.conns.size());
        for (int idx : nd.conns) {
            const Connection& c = connections[idx];
            if (!c.abandoned && shouldRoute(c)) mem.push_back(idx);
        }
        const int n = (int) mem.size();
        if (n < (int) rwEnvI("RW_BATCH_NMIN", 64)) return -2;   // too few to pay the crew cost -> serial.
                                                         // NOT batchB: straggler iterations reroute 100-500
                                                         // monster conns (~200ms each) -- a 16..24-way crew on
                                                         // those is the whole point (B adapts to n per batch)
        {   // Net-aware ROUND-ROBIN batching: same-net conns must land in DIFFERENT batches, else the
            // deferred commits strip the same-net sharing discount and every batch-mate re-searches the
            // trunk from scratch (measured 7x iter-1 work). Round k takes the k-th conn of each net
            // (net order = first appearance in the leaf) -> deterministic, sharing restored across batches.
            std::vector<int> netOrder; netOrder.reserve(mem.size());
            std::unordered_map<int, std::vector<int>> byNet;
            for (int idx : mem) {
                auto it = byNet.find(connections[idx].netIdx);
                if (it == byNet.end()) { netOrder.push_back(connections[idx].netIdx); byNet[connections[idx].netIdx].push_back(idx); }
                else it->second.push_back(idx);
            }
            std::vector<int> rr; rr.reserve(mem.size());
            for (size_t round = 0; rr.size() < mem.size(); round++)
                for (int nid : netOrder) {
                    auto& v = byNet[nid];
                    if (round < v.size()) rr.push_back(v[round]);
                }
            mem.swap(rr);
        }
        {   // Interleave for intra-batch conflict avoidance. Two keys:
            // POSBAND (default, E-D post-mortem): cut-straddler cores ALL cross the same cut line, and
            // under identical prices same-height conns funnel through the same cheap crossing trunks
            // (68% intra-batch collisions measured on the 632k core). Batch-mates at different route
            // midpoints (y major, x minor) cross elsewhere -> bucket by normalized midpoint.
            // POSBAND=0: the P1' direction-octant x length-band key (clusters same-net conns -- only
            // safe now that the stale check exempts same-net sharing).
            std::vector<std::vector<int>> bk(32);
            const bool posBand = rwEnvI("RW_BATCH_POSBAND", 1) != 0;
            int yLo = INT32_MAX, yHi = INT32_MIN, xLo = INT32_MAX, xHi = INT32_MIN;
            if (posBand)
                for (int idx : mem) {
                    const Connection& c = connections[idx];
                    int my = (getEndTileYCoordinate(c.sourceRnode) + getBeginTileYCoordinate(c.sinkRnode)) >> 1;
                    int mx = (getEndTileXCoordinate(c.sourceRnode) + getBeginTileXCoordinate(c.sinkRnode)) >> 1;
                    yLo = std::min(yLo, my); yHi = std::max(yHi, my);
                    xLo = std::min(xLo, mx); xHi = std::max(xHi, mx);
                }
            for (int idx : mem) {
                const Connection& c = connections[idx];
                int key;
                if (posBand) {
                    int my = (getEndTileYCoordinate(c.sourceRnode) + getBeginTileYCoordinate(c.sinkRnode)) >> 1;
                    int mx = (getEndTileXCoordinate(c.sourceRnode) + getBeginTileXCoordinate(c.sinkRnode)) >> 1;
                    int yb = yHi > yLo ? (int) ((long long) (my - yLo) * 8 / (yHi - yLo + 1)) : 0;
                    int xb = xHi > xLo ? (int) ((long long) (mx - xLo) * 4 / (xHi - xLo + 1)) : 0;
                    key = yb * 4 + xb;
                } else {
                    int dx = getBeginTileXCoordinate(c.sinkRnode) - getEndTileXCoordinate(c.sourceRnode);
                    int dy = getBeginTileYCoordinate(c.sinkRnode) - getEndTileYCoordinate(c.sourceRnode);
                    int dir = (dx >= 0 ? 1 : 0) | (dy >= 0 ? 2 : 0) | (std::abs(dx) > std::abs(dy) ? 4 : 0);
                    int h = (int) c.hpwl;
                    key = dir * 4 + (h < 8 ? 0 : h < 24 ? 1 : h < 64 ? 2 : 3);
                }
                bk[(size_t) key].push_back(idx);
            }
            std::vector<int> cw; cw.reserve(mem.size());
            for (size_t round = 0; cw.size() < mem.size(); round++)
                for (auto& v : bk)
                    if (round < v.size()) cw.push_back(v[(size_t) round]);
            mem.swap(cw);
        }
        std::mutex abortMu; std::vector<int> crewAborted;   // budget-aborted runaways -> publisher serial path
        std::vector<int> bv, claim, bounced;             // bv: per-batch members in COMMIT order (bounced-first,
                                                         // then fresh stream); claim: LPF-sorted copy for the
                                                         // dynamic claim order (schedule only, results identical)
        std::unordered_map<int, int> bounceCnt;
        const int bounceMax = (int) rwEnvI("RW_BATCH_BOUNCE", 2);   // stale commits re-enter the NEXT batch (fresh
                                                         // prices, parallel) this many times before the exact
                                                         // serial fallback on the publisher
        long long bounces = 0;
        std::mutex bm; std::condition_variable bcv, dcv;
        int hi = 0, gen = 0, active = 0; bool crewDone = false;
        bool monsterGen = false;                         // this generation = over-budget monsters: unbudgeted,
                                                         // claimed by the first MLANES workers only (bounded
                                                         // pools) -- parallel instead of publisher-serial
        const int monsterLanes = std::max(1, std::min((int) rwEnvI("RW_BATCH_MLANES", 6), batchT));
        std::atomic<int> cursor{0}, remain{0};
        std::atomic<long long> bAborts{0}, bFloodOk{0}, bNoFlood{0}, bPops{0};
        std::atomic<long long> aSearchNs{0}, aResetNs{0};   // summed across crew workers
        double tRip = 0, tWait = 0, tCommit = 0;            // publisher serial phases
        auto _lt0 = std::chrono::steady_clock::now();
        auto workerFn = [&](int w) {
#if defined(__linux__)
            if (parPin) {   // crew on physical cores DISJOINT from the RPTT worker pins (cores 0..T/2-1
                unsigned hw = std::max(4u, std::thread::hardware_concurrency());   // and hw/4..hw/4+T/2-1)
                int cpu = (w % 2) * (int) (hw / 4) + (int) (hw / 8) + w / 2;
                cpu_set_t cs; CPU_ZERO(&cs); CPU_SET(cpu, &cs);
                sched_setaffinity(0, sizeof(cs), &cs);
            }
#endif
            if (batchSparse) {
                tl_dyn = dyn.data();                     // labels resolve via TLD -> the sparse store
                tl_sparse = &batchLabels[(size_t) w];
                tl_pq = &overlapPq[(size_t) w];
            } else {
                tl_dyn = bws[(size_t) w].shadow;         // PRIVATE scratch: overlapping conns never collide
                tl_pq = &bws[(size_t) w].pq;
            }
            tl_wid = 64 + w;
            tl_deferCommit = true;
            int myGen = 0;
            for (;;) {
                int myHi; bool myMonster;
                {
                    std::unique_lock<std::mutex> lk(bm);
                    bcv.wait(lk, [&] { return crewDone || gen != myGen; });
                    if (crewDone) break;
                    myGen = gen; myHi = hi; myMonster = monsterGen; active++;
                }
                const bool spectator = myMonster && w >= monsterLanes;   // pool growth stays bounded; must not
                const long long myBudget = myMonster ? -1 : batchBudget; // touch cursor (fetch_add would steal
                int i;                                                   // and DROP an index -> remain never 0)
                while (!spectator && (i = cursor.fetch_add(1, std::memory_order_relaxed)) < myHi) {
                    int idx = claim[(size_t) i];
                    auto _c0 = std::chrono::steady_clock::now();
                    if (tl_sparse) tl_sparse->reset();             // O(1): epoch bump invalidates all labels
                    TLD(connections[idx].sourceRnode).prev = -1;   // zero-page default is 0, walker needs -1
                    auto _c1 = std::chrono::steady_clock::now();
                    aResetNs.fetch_add((long long) std::chrono::duration<double, std::nano>(_c1 - _c0).count(),
                                       std::memory_order_relaxed);
#ifdef WITH_CUDA
                    if (floodActive && floodBudget > 0) {   // same budget discipline as the serial leaf path
                        routeIndirectConnection(idx, floodBudget);
                        if (lastAborted) {                  // monster -> lane flood (commit deferred)
                            bAborts.fetch_add(1, std::memory_order_relaxed);
                            int lane = acquireLane();
                            bool ok = gpuFloodTryLane(idx, lane);
                            releaseLane(lane);
                            if (ok) bFloodOk.fetch_add(1, std::memory_order_relaxed);
                            else {
                                connections[idx].rnodes.clear(); connections[idx].routed = false;
                                routeIndirectConnection(idx);   // rare: unbudgeted CPU rescue
                            }
                        }
                    } else {
                        bNoFlood.fetch_add(1, std::memory_order_relaxed);
                        routeIndirectConnection(idx, myBudget);
                        if (lastAborted) {                   // runaway monster: cap the pool + the batch wall
                            connections[idx].rnodes.clear();
                            connections[idx].routed = false;
                            bAborts.fetch_add(1, std::memory_order_relaxed);
                            std::lock_guard<std::mutex> alk(abortMu);
                            crewAborted.push_back(idx);      // publisher reroutes exactly, after commits
                        }
                    }
                    bPops.fetch_add(lastPops, std::memory_order_relaxed);
#else
                    routeIndirectConnection(idx, myBudget);   // commit deferred (tl_deferCommit)
                    if (lastAborted) {
                        connections[idx].rnodes.clear();
                        connections[idx].routed = false;
                        bAborts.fetch_add(1, std::memory_order_relaxed);
                        std::lock_guard<std::mutex> alk(abortMu);
                        crewAborted.push_back(idx);
                    }
#endif
                    aSearchNs.fetch_add((long long) std::chrono::duration<double, std::nano>(
                                            std::chrono::steady_clock::now() - _c1).count(),
                                        std::memory_order_relaxed);
                    remain.fetch_sub(1, std::memory_order_acq_rel);
                }
                {   // park: the publisher may only reset the cursor once EVERY worker has parked --
                    // a straggler in the old claim loop would otherwise steal (and drop) a new index.
                    std::lock_guard<std::mutex> lk(bm);
                    if (--active == 0) dcv.notify_one();
                }
            }
            tl_deferCommit = false; tl_wid = -1; tl_sparse = nullptr;
        };
        std::vector<std::thread> crew;
        for (int w = 0; w < batchT; w++) crew.emplace_back(workerFn, w);
        std::unordered_map<int, int> deltaNodes;         // node -> committing netIdx within the current batch.
                                                         // SAME-net trunk sharing is legal (sharing discount;
                                                         // the stale search only over-priced it) -- flagging it
                                                         // was self-inflicted rollback: same-net conns cluster
                                                         // in dir x hpwl buckets and co-batch.
        long long requeued = 0;
        int done = 0;
        while (done < n || !bounced.empty()) {
            bv.clear();
            bv.insert(bv.end(), bounced.begin(), bounced.end());   // bounced re-enter FIRST (commit priority)
            bounced.clear();
            const int fresh = done < n ? std::min(n - done, std::max(0, batchB - (int) bv.size())) : 0;
            for (int k = 0; k < fresh; k++) bv.push_back(mem[(size_t) (done + k)]);
            claim = bv;
            if (batchLpf)                                // long-pole first (LPT): a batch's wall is its longest
                std::stable_sort(claim.begin(), claim.end(),                // search -- run monsters first, pack
                    [&](int a, int b) {                                     // the small fry around them
                        long long pa = a < (int) connLastPops.size() ? connLastPops[(size_t) a] : 0;
                        long long pb = b < (int) connLastPops.size() ? connLastPops[(size_t) b] : 0;
                        if (pa == 0) pa = (long long) connections[(size_t) a].hpwl;   // iter-1: no pops history
                        if (pb == 0) pb = (long long) connections[(size_t) b].hpwl;   // yet -- hpwl is the proxy
                        return pa > pb;                  // stable: ties keep bv order -> deterministic
                    });
            auto _p0 = std::chrono::steady_clock::now();
            if (corridorM >= 0 && corrStamp.size() != connections.size()) {
                corrStash.assign(connections.size(), 0);
                corrStamp.assign(connections.size(), 0);
            }
            for (int idx : bv) {                         // serial rip-up: exact occupancy at snapshot start
                Connection& c = connections[idx];        // (bounced members were ripped in their first batch;
                if (corridorM >= 0 && routeIteration >= 2 && !c.rnodes.empty()) {
                    int ex0 = INT32_MAX, ex1 = INT32_MIN, ey0 = INT32_MAX, ey1 = INT32_MIN;
                    for (int id : c.rnodes) {            // stash the envelope: the crew searches after clear
                        const auto& a = ns[(size_t) id];
                        ex0 = std::min(ex0, (int) std::min(a.beginX, a.endX));
                        ex1 = std::max(ex1, (int) std::max(a.beginX, a.endX));
                        ey0 = std::min(ey0, (int) std::min(a.beginY, a.endY));
                        ey1 = std::max(ey1, (int) std::max(a.beginY, a.endY));
                    }
                    corrStash[(size_t) idx] = (uint64_t) (uint16_t) ex0 | ((uint64_t) (uint16_t) ex1 << 16) |
                                              ((uint64_t) (uint16_t) ey0 << 32) | ((uint64_t) (uint16_t) ey1 << 48);
                    corrStamp[(size_t) idx] = routeIteration;
                }
                ripUp(c);                                //  empty rnodes make this a no-op
                c.rnodes.clear(); c.routed = false;
            }
            tRip += std::chrono::duration<double>(std::chrono::steady_clock::now() - _p0).count();
#ifdef WITH_CUDA
            // Publish rip deltas ONLY if the crew actually floods (floodBudget>0): with a CPU-only crew
            // this per-batch refresh+sync serialized EVERY batch against the (often saturated) GPU --
            // measured as the dominant term of E-C/E-D/E-F core walls (e.g. 632k core: ~10k batches x
            // ~90ms sync ~= 900s of pure tax). The leaf-end flush in the RPTT worker still runs once.
            if (floodActive && floodLive && floodBudget > 0 && !tl_dirtyList.empty()) {
                maybeRefreshBeforeLane();                              // must see the snapshot prices
                int lane = acquireLane();
                flushDirtyToGpu(lane);
                gpuFloodSyncLane(lane);
                releaseLane(lane);
            }
#endif
            {
                std::lock_guard<std::mutex> lk(bm);
                hi = (int) bv.size();
                cursor.store(0, std::memory_order_relaxed);
                remain.store((int) bv.size(), std::memory_order_relaxed);
                gen++;
            }
            bcv.notify_all();
            auto _p1 = std::chrono::steady_clock::now();
            {
                std::unique_lock<std::mutex> lk(bm);
                dcv.wait(lk, [&] { return active == 0 && remain.load(std::memory_order_acquire) == 0; });
            }
            auto _p2 = std::chrono::steady_clock::now();
            tWait += std::chrono::duration<double>(_p2 - _p1).count();
            if (batchRollback) {
                deltaNodes.clear();
                for (int idx : bv) {                     // serial commit in bv order -> deterministic
                    Connection& c = connections[idx];
                    bool stale = false;
                    if (c.routed)
                        for (int nid : c.rnodes) {
                            auto it = deltaNodes.find(nid);
                            if (it != deltaNodes.end() && it->second != c.netIdx) { stale = true; break; }
                        }
                    if (stale) {                         // searched on stale prices
                        c.rnodes.clear(); c.routed = false;
                        int& bcn = bounceCnt[idx];
                        if (bcn < bounceMax) {           // re-enter the next batch: fresh prices, parallel search
                            bcn++; bounces++; bounced.push_back(idx);
                            continue;
                        }
                        routeIndirectConnection(idx);    // exact serial fallback: live prices, immediate commit
                        requeued++;
                    } else if (c.routed) {
                        updateUsersAndPresentCongestionCost(c);
                    }
                    for (int nid : connections[idx].rnodes) deltaNodes[nid] = c.netIdx;
                }
            } else {
                for (int idx : bv) {                     // serial commit in bv order -> deterministic
                    Connection& c = connections[idx];
                    if (c.routed) updateUsersAndPresentCongestionCost(c);
                }
            }
            if (!crewAborted.empty()) {                  // budget-aborted runaways: rerun UNBUDGETED on a
                std::sort(crewAborted.begin(), crewAborted.end());   // small crew (bounded pools) instead of
                bv = crewAborted; claim = crewAborted;               // publisher-serial (E-M/TRY5: the serial
                crewAborted.clear();                                 // monster segment dominated the mid-tail).
                {                                                    // Sorted: arrival order nondeterministic.
                    std::lock_guard<std::mutex> lk(bm);
                    hi = (int) bv.size();
                    cursor.store(0, std::memory_order_relaxed);
                    remain.store((int) bv.size(), std::memory_order_relaxed);
                    monsterGen = true;
                    gen++;
                }
                bcv.notify_all();
                {
                    std::unique_lock<std::mutex> lk(bm);
                    dcv.wait(lk, [&] { return active == 0 && remain.load(std::memory_order_acquire) == 0; });
                    monsterGen = false;
                }
                deltaNodes.clear();                      // monsters searched post-commit state; conflicts only
                for (int idx : bv) {                     // among themselves -- rollback in sorted order, the
                    Connection& c = connections[idx];    // rare stale monster reroutes serially (exact)
                    bool stale = false;
                    if (c.routed)
                        for (int nid : c.rnodes) {
                            auto it = deltaNodes.find(nid);
                            if (it != deltaNodes.end() && it->second != c.netIdx) { stale = true; break; }
                        }
                    if (stale) {
                        c.rnodes.clear(); c.routed = false;
                        routeIndirectConnection(idx);
                        requeued++;
                    } else if (c.routed) {
                        updateUsersAndPresentCongestionCost(c);
                    }
                    for (int nid : connections[idx].rnodes) deltaNodes[nid] = c.netIdx;
                }
            }
            tCommit += std::chrono::duration<double>(std::chrono::steady_clock::now() - _p2).count();
            {   // per-batch iter progress (leaf-completion granularity would fire the iter-1 pf ramp far
                // too late for a 1M-conn core); crew is parked here, so the table rewrite is quiet.
                // Advance by FRESH stream consumption only (bounced members were counted once already).
                int doneSoFar = routedTotal.fetch_add(fresh, std::memory_order_relaxed) + fresh;
                if (pfRamp1 > 1.0f && routeIteration == 1 && rampTotalWork > 0) {
                    const int S = rampStages;
                    int stage = (int) ((long long) doneSoFar * (S + 1) / rampTotalWork);
                    if (stage > S) stage = S;
                    int cur = rampStage.load(std::memory_order_relaxed);
                    if (stage > cur && rampStage.compare_exchange_strong(cur, stage)) {
                        float mult = 1.0f + (pfRamp1 - 1.0f) * (float) stage / (float) S;
                        updatePresentCongestionCosts(cfg.initialPresentCongestionFactor * mult);
                        std::fprintf(stderr, "[ramp1] stage=%d/%d done=%d/%d pfTable=%.1f (in-batch)\n",
                                     stage, S, doneSoFar, rampTotalWork,
                                     cfg.initialPresentCongestionFactor * mult);
                    }
                }
            }
            done += fresh;
        }
        {
            std::lock_guard<std::mutex> lk(bm);
            crewDone = true;
        }
        bcv.notify_all();
        for (auto& t : crew) t.join();
        if (batchSparse && batchPaged)                   // release runaway pool capacity between leaves
            for (int w = 0; w < batchT; w++) {
                SparseLabels& L = batchLabels[(size_t) w];
                if (L.paged && L.pool.size() > (size_t) 4096 * (size_t) L.PSIZE) {
                    L.pool.resize((size_t) 4096 * (size_t) L.PSIZE);   // 48MB steady cap per worker
                    L.pool.shrink_to_fit();
                    L.reset();                           // epoch bump: stale pageSlots may exceed the new pool
                }
            }
        batchedConns += n; batchedLeaves++;
        std::fprintf(stderr, "[batch-leaf] iter=%d n=%d bounced=%lld requeued=%lld aborts=%lld floodOk=%lld noFloodPath=%lld pops/conn=%lld in %.2fs (rip=%.1f wait=%.1f commit=%.1f searchSum=%.1f resetSum=%.1f)\n",
                     routeIteration, n, bounces, requeued, bAborts.load(), bFloodOk.load(), bNoFlood.load(),
                     bPops.load() / std::max(1, n),
                     std::chrono::duration<double>(std::chrono::steady_clock::now() - _lt0).count(),
                     tRip, tWait, tCommit, aSearchNs.load() / 1e9, aResetNs.load() / 1e9);
        return 0;   // progress already accounted per batch (routedTotal) -- caller must not re-add
    }

    int routeLeaf(PTNode& nd) {
        // Endgame gate: with few overused nodes left, the survivors are ping-pong pairs -- batching
        // puts them in one mutually-blind snapshot and the bounced-first re-entry flips their order
        // every iteration, defeating the fixed-order+hist tie-breaking PathFinder needs (E-M run:
        // oscillated at 20-60 overused from iter ~45 to the 100-iteration cap; serial-endgame E-I/E-K
        // converged at 50). Serial order below the gate restores convergence.
        static const int batchOverMin = (int) rwEnvI("RW_BATCH_OVER_MIN", 128);
        if (batchMin > 0 && routeIteration >= batchIterMin && routeIteration <= batchIterMax &&
            (routeIteration <= 1 || (int) overUsedList.size() >= batchOverMin) &&
            !lazy && flatGraphBuilt && (int) nd.conns.size() >= batchMin) {
            int r = routeLeafBatched(nd);
            if (r >= 0) return r;                        // -1/-2 -> fall through to the serial path
        }
        int n = 0;
        for (int idx : nd.conns) {
            Connection& c = connections[idx];
            if (c.abandoned || !shouldRoute(c)) continue;
#ifdef WITH_CUDA
            if (floodActive) {
                if (idx < (int) connLastPops.size() && connLastPops[idx] >= floodMin) { gpuFloodRoute(idx); n++; continue; }
                if (floodBudget > 0) {
                    routeIndirectConnection(idx, floodBudget);
                    if (lastAborted) gpuFloodRoute(idx);
                    n++; continue;
                }
            }
#endif
            routeIndirectConnection(idx); n++;
        }
        return n;
    }

    int routeIndirectConnectionsPartitioned() {
        if (pfRamp1 < 0.0f) {
            // Banked (2026-07-09 sweep): 3.0 on the 20per connection band -- iter-1 overuse 265.8k ->
            // 113k, every mid-iteration reroute set shrinks to ~1/3, e2e -22s under identical load,
            // wl +0.84%, legal. 4.0 equivalent time at wl +1.39%; 6.0 NEGATIVE (iter-1 itself +21s
            // eats the gain). Off elsewhere: other cases keep bit-identical results.
            pfRamp1 = connections.size() >= 2200000 ? 3.0f : 0.0f;   // >=3.5M banked too (50per E-A/E-J:
                                                     // 446k->187k iter-1 overuse; softening to 2.0 NEGATIVE)
        }
        if (pfRamp1 > 1.0f && routeIteration == 1) {   // iter-1 pf ramp: size the work, arm the stages
            int w = 0;
            for (int idx : sortedIndirect)
                if (!connections[idx].abandoned && shouldRoute(connections[idx])) w++;
            rampTotalWork = w;
            rampStage.store(0, std::memory_order_relaxed);
        }
        if (lazy) {
            // Serial-boundary growth: guarantee workers can intern without ever reallocating the node
            // arrays (a realloc under a concurrent reader is fatal). 80% watermark, doubling growth.
            size_t used = (size_t) numNodes();
            if (used * 5 >= ns.capacity() * 4) {
                size_t want = std::max(ns.capacity() * 2, (size_t) 1 << 22);
                std::fprintf(stderr, "[par] lazy headroom: node arrays %zu -> %zu (used %zu)\n",
                             ns.capacity(), want, used);
                reserveNodes(want);
                tl_dyn = dyn.data();
            }
        }
        if (!ptBuilt) {
            auto _b0 = std::chrono::steady_clock::now();
            ptBuildTree();
            ptasks.clear();
            ptCollect(0);
            taskIndeg = std::make_unique<std::atomic<int>[]>(ptasks.size());
            long edges = 0; for (auto& t : ptasks) edges += (long) t.out.size();
            std::fprintf(stderr, "[par] tree: nodes=%zu leaves=%zu edges=%ld overlap=%d built=%.2fs\n",
                         ptree.size(), ptasks.size(), edges, (int) parOverlapEdges,
                         std::chrono::duration<double>(std::chrono::steady_clock::now() - _b0).count());
            if (parReport) ptReport();
            ptBuilt = true;
        }
        const int nT = (int) ptasks.size();
        for (int i = nT - 1; i >= 0; i--) {            // edges run low->high: reverse pass = reverse topo
            double m = 0;
            for (int s : ptasks[i].out) if (ptasks[(size_t) s].crit > m) m = ptasks[(size_t) s].crit;
            ptasks[(size_t) i].crit = ptasks[(size_t) i].estNs + m;
            taskIndeg[i].store(ptasks[(size_t) i].indegInit, std::memory_order_relaxed);
        }
        std::priority_queue<std::pair<double,int>> ready;
        std::mutex mu; std::condition_variable cv;
        int remaining = nT;                            // guarded by mu
        for (int i = 0; i < nT; i++) if (ptasks[(size_t) i].indegInit == 0) ready.push({ptasks[(size_t) i].crit, i});
        routedTotal.store(0, std::memory_order_relaxed);   // member: batched leaves advance it per batch
        ptActNs.assign((size_t) nT, 0.0);              // per-task ACTUAL ns this iteration (single writer)
        parIdleNs.store(0, std::memory_order_relaxed); // worker time blocked on the ready queue
        laneWaitNs.store(0, std::memory_order_relaxed);
        auto itWall0 = std::chrono::steady_clock::now();
        const int T = std::max(1, std::min(parPart, nT));
        if ((int) threadPq.size() < T) threadPq.resize(T);
        auto worker = [&](int wid) {
#if defined(__linux__)
            if (parPin) {   // spread workers across both sockets (pairs with the interleaved arrays)
                unsigned hw = std::max(4u, std::thread::hardware_concurrency());
                int cpu = (wid % 2) * (int) (hw / 4) + wid / 2;   // 2-socket+HT: physical cores [0, hw/2)
                cpu_set_t cs; CPU_ZERO(&cs); CPU_SET(cpu, &cs);
                sched_setaffinity(0, sizeof(cs), &cs);
            }
#endif
            tl_dyn = dyn.data(); tl_pq = &threadPq[(size_t) wid]; tl_wid = wid;
            resetDirtyLocal();
            for (;;) {
                int t = -1;
                {
                    auto w0 = std::chrono::steady_clock::now();
                    std::unique_lock<std::mutex> lk(mu);
                    cv.wait(lk, [&] { return remaining == 0 || !ready.empty(); });
                    if (ready.empty()) break;          // remaining == 0 -> all done
                    t = ready.top().second; ready.pop();
                    parIdleNs.fetch_add((long long) std::chrono::duration<double, std::nano>(
                        std::chrono::steady_clock::now() - w0).count(), std::memory_order_relaxed);
                }
                auto t0 = std::chrono::steady_clock::now();
                int n = routeLeaf(ptree[ptasks[(size_t) t].node]);
                int doneSoFar = routedTotal.fetch_add(n, std::memory_order_relaxed) + n;
                // iter-1 progressive pf (RW_PF_RAMP1=finalMult, default off): the first conns route at
                // the loose initial pf and blindly pile into corridors that the NEXT 8 iterations must
                // unwind; stiffening the present table in 3 steps (25/50/75% of iter-1 work) makes the
                // later majority congestion-aware from the start. Only the 256-float table is rewritten
                // (torn reads are transient and monotone); the pf SCALAR is untouched, so the iter-2+
                // schedule is unchanged. Non-deterministic (worker timing picks the crossing) ->
                // legality-gated, case-banked like hist-tail.
                if (pfRamp1 > 1.0f && routeIteration == 1 && rampTotalWork > 0) {
                    const int S = rampStages;
                    int stage = (int) ((long long) doneSoFar * (S + 1) / rampTotalWork);
                    if (stage > S) stage = S;
                    int cur = rampStage.load(std::memory_order_relaxed);
                    if (stage > cur && rampStage.compare_exchange_strong(cur, stage)) {
                        float mult = 1.0f + (pfRamp1 - 1.0f) * (float) stage / (float) S;
                        updatePresentCongestionCosts(cfg.initialPresentCongestionFactor * mult);
                        std::fprintf(stderr, "[ramp1] stage=%d/%d done=%d/%d pfTable=%.1f\n",
                                     stage, S, doneSoFar, rampTotalWork, cfg.initialPresentCongestionFactor * mult);
                    }
                }
#ifdef WITH_CUDA
                if (trackDirty) {   // publish this leaf's remaining live-price marks BEFORE successors wake:
                    if (!tl_dirtyList.empty() && floodActive) {   // scatter + lane stream sync => visible to any
                        maybeRefreshBeforeLane();                 // oversize dirty -> full refresh instead of truncation
                        if (!tl_dirtyList.empty()) {
                            int lane = acquireLane();             // lane's later kernels (deterministic per DAG order)
                            flushDirtyToGpu(lane);
                            gpuFloodSyncLane(lane);
                            releaseLane(lane);
                        }
                    }
                    resetDirtyLocal();
                }
#endif
                const double el = std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - t0).count();
                PTask& tk = ptasks[(size_t) t];
                tk.estNs = (tk.estNs + el) * 0.5;      // EMA cost feedback (single owner per task)
                ptActNs[(size_t) t] = el;              // actual, for the post-iteration critical-path report
                int woke = 0; bool last = false;
                {
                    std::lock_guard<std::mutex> lk(mu);
                    for (int s : tk.out)
                        if (taskIndeg[s].fetch_sub(1, std::memory_order_relaxed) == 1) {
                            ready.push({ptasks[(size_t) s].crit, s});
                            woke++;
                        }
                    last = (--remaining == 0);
                }
                if (last) cv.notify_all();                        // release the exit barrier
                else for (int i = 0; i < woke; i++) cv.notify_one();   // no thundering herd
            }
            totalPushes.fetch_add(tl_pushes, std::memory_order_relaxed); tl_pushes = 0;
            tl_wid = -1;
        };
        std::vector<std::thread> ths;
        for (int t = 0; t < T; t++) ths.emplace_back(worker, t);
        for (auto& th : ths) th.join();
        tl_dyn = dyn.data(); tl_pq = &pqStorage;       // restore main-thread serial aliases
        {   // [par-stats] where does the 32-core speedup go? ACTUAL critical path (longest chain of
            // measured task times through the DAG) vs wall vs total work. util = work/(T*wall);
            // crit/wall ~1 => scheduler is at the DAG bound, the DAG itself is the limiter.
            double wall = std::chrono::duration<double>(std::chrono::steady_clock::now() - itWall0).count();
            double sum = 0, cpMax = 0; int cpEnd = -1;
            std::vector<double> cpIn((size_t) nT, 0.0);
            std::vector<int> pred((size_t) nT, -1);
            for (int i = 0; i < nT; i++) {             // ptasks indices are topo-ordered (edges low->high)
                double cp = cpIn[(size_t) i] + ptActNs[(size_t) i];
                if (cp > cpMax) { cpMax = cp; cpEnd = i; }
                sum += ptActNs[(size_t) i];
                for (int s : ptasks[(size_t) i].out)
                    if (cp > cpIn[(size_t) s]) { cpIn[(size_t) s] = cp; pred[(size_t) s] = i; }
            }
            std::fprintf(stderr, "[par-stats] iter=%d wall=%.2fs work=%.2fs util=%.0f%% crit=%.2fs crit/wall=%.2f idle=%.1fs laneWait=%.1fs\n",
                         routeIteration, wall, sum / 1e9, 100.0 * sum / 1e9 / (wall * T), cpMax / 1e9,
                         wall > 0 ? cpMax / 1e9 / wall : 0.0,
                         parIdleNs.load() / 1e9, laneWaitNs.load() / 1e9);
            if (cpEnd >= 0 && cpMax > 0.5e9) {         // decompose the chain when it matters (>0.5s)
                // walk the actual critical chain, print its heaviest segments: which tasks to attack
                std::vector<int> chain; for (int u = cpEnd; u != -1; u = pred[(size_t) u]) chain.push_back(u);
                std::fprintf(stderr, "[par-crit] chain len=%zu, heaviest:", chain.size());
                std::vector<int> byNs(chain);
                std::sort(byNs.begin(), byNs.end(), [&](int a, int b) { return ptActNs[(size_t) a] > ptActNs[(size_t) b]; });
                for (size_t k = 0; k < byNs.size() && k < 6; k++) {
                    int tsk = byNs[k]; const PTNode& nd = ptree[(size_t) ptasks[(size_t) tsk].node];
                    std::fprintf(stderr, "  %s(conns=%zu,%.2fs)",
                                 (nd.left >= 0 || nd.right >= 0 || nd.mid >= 0) ? "MID" : "leaf",
                                 nd.conns.size(), ptActNs[(size_t) tsk] / 1e9);
                }
                std::fprintf(stderr, "\n");
            }
        }
        return routedTotal.load();
    }

    // ===== Lazy prepass materialization + spatial renumbering (RW_PAR_PREPASS; JNI big cases) =====
    // Before routing, discover the whole search-reachable universe with a parallel BFS closure over raw
    // children, bounded by the union tile cover of all connection bboxes, then intern everything in one
    // bulk pass with ids assigned in (tileAddr, wire) order == device-grid order: spatially close nodes
    // get close ids, so the maze's random per-node accesses (ns/dyn/hot/occ) hit warm cache lines and
    // TLB entries far more often -- the main lever against the multi-thread memory wall. It also removes
    // every fetch/intern from the search hot path (the lazy iter-1 tax), switches the router to the
    // contiguous non-lazy CSR (childStart/childIds), and gives the GPU flood the complete subgraph from
    // iteration 1. Soundness: a node can only be POPPED if its (dynamic) end tile lies strictly inside
    // some connection bbox, and every such tile is in the cover; the closure expands exactly the nodes
    // whose end (or begin, for the prev-dependent SLLs) tile is covered, so every poppable node is
    // materialized WITH its full child list; un-expanded fringe children are never popped.
    static void parForN(size_t n, int T, const std::function<void(int, size_t, size_t)>& fn) {
        if (n == 0) return;
        T = std::max(1, std::min<int>(T, (int) n));
        std::vector<std::thread> th;
        size_t chunk = (n + T - 1) / T;
        for (int t = 0; t < T; t++) {
            size_t lo = (size_t) t * chunk, hi = std::min(n, lo + chunk);
            if (lo >= hi) break;
            th.emplace_back([&fn, t, lo, hi] { fn(t, lo, hi); });
        }
        for (auto& x : th) x.join();
    }

    std::vector<uint8_t> prepassCoverStore; int prepassW = 0, prepassH = 0;   // kept for early-cover verify

    int earlyTotal = -1;                               // numNodes() at early-prepass end (late-seed patch base)

    void lazyPrepassMaterialize(std::vector<uint8_t>* extCover = nullptr, int extW = 0, int extH = 0,
                                const std::vector<long long>* extSeeds = nullptr) {
        auto _t0 = std::chrono::steady_clock::now();
        const int T = std::max(1, parPart);
        // 1) tile cover bitmap. Normal path: built from post-D0 conn bboxes (strict interior).
        //    Early path (prepass-early): caller passes a per-net pin-rect cover (superset, margins).
        int W, H;
        std::vector<uint8_t> cover;
        if (extCover) { W = extW; H = extH; cover = std::move(*extCover); }
        else {
        W = 0; H = 0;
        for (const auto& c : connections) { W = std::max(W, (int) c.xMaxBB); H = std::max(H, (int) c.yMaxBB); }
        W += 2; H += 2;
        cover.assign((size_t) W * H, 0);
        parForN(connections.size(), T, [&](int, size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++) {
                const Connection& c = connections[(int) i];
                if (c.abandoned) continue;
                int x0 = std::max((int) c.xMinBB + 1, 0), x1 = std::min((int) c.xMaxBB - 1, W - 1);
                int y0 = std::max((int) c.yMinBB + 1, 0), y1 = std::min((int) c.yMaxBB - 1, H - 1);
                for (int y = y0; y <= y1; y++) {
                    uint8_t* row = &cover[(size_t) y * W];
                    for (int x = x0; x <= x1; x++) row[x] = 1;   // benign same-value races
                }
            }
        });
        }
        prepassCoverStore = cover; prepassW = W; prepassH = H;
        auto covered = [&](int x, int y) { return x >= 0 && x < W && y >= 0 && y < H && cover[(size_t) y * W + x]; };
        auto recExpandable = [&](const int* p) {   // child record: endX/endY at p[6],p[7]; begin at p[4],p[5]
            if (covered(p[6], p[7])) return true;
            return (RouteNodeType) p[2] == RouteNodeType::SUPER_LONG_LINE && covered(p[4], p[5]);
        };
        // 2) parallel BFS closure over KEYS (claim-only marker table; ids come later, sorted).
        // Capacity must bound the CLOSURE (unknown upfront), not the seed count: size for the whole
        // device (~104M nodes) -- mmap is lazily committed, so unused slots cost address space only.
        // An overfull open-addressing table has no empty slots left and claim() would spin forever.
        KIMap seen; seen.reset((size_t) 1 << 28);
        std::vector<long long> cur;
        for (int id = 0, N = numNodes(); id < N; id++) {
            long long k = keyOf(id);
            seen.claim(k);
            bool exp = covered(ns[id].endX, ns[id].endY) ||
                       (type[id] == RouteNodeType::SUPER_LONG_LINE && covered(ns[id].beginX, ns[id].beginY));
            if (exp) cur.push_back(k);
        }
        std::vector<long long> seedWave;               // early path: BFS from raw pin keys WITHOUT interning
        if (extSeeds) {                                // them (they stay fetch-handles; loadLazy interns them
            for (long long k : *extSeeds) seedWave.push_back(k);   // later and patchLateSeeds appends their edges)
            std::sort(seedWave.begin(), seedWave.end());
            seedWave.erase(std::unique(seedWave.begin(), seedWave.end()), seedWave.end());
        }
        // Waves: single fetch per expanded key for DISCOVERY; the CSR pass refetches (measured cheaper
        // than retaining ~2.5GB of child keys: the single-fetch variant cost +1.4s on k_800's prepass).
        std::vector<long long> allExpanded;                       // every key we fetch children for
        std::vector<std::vector<long long>> tNext((size_t) T), tKeys((size_t) T);
        std::vector<std::vector<int>> tRecs((size_t) T);          // 11 ints per newly discovered key
        int waves = 0;
        if (!seedWave.empty()) {                                  // pre-wave: expand seeds, EXCLUDED from allExpanded
            parForN(seedWave.size(), T, [&](int w, size_t lo, size_t hi) {
                std::vector<int> buf;
                for (size_t i = lo; i < hi; i++) {
                    fetchChildrenPacked(seedWave[i], buf);
                    int cnt = buf.empty() ? 0 : buf[0];
                    for (int k = 0; k < cnt; k++) {
                        const int* p = &buf[1 + k * 11];
                        long long ck = ((long long) p[0] << 20) | (p[1] & 0xFFFFF);
                        if (!seen.claim(ck)) continue;
                        tKeys[(size_t) w].push_back(ck);
                        tRecs[(size_t) w].insert(tRecs[(size_t) w].end(), p, p + 11);
                        if (recExpandable(p)) tNext[(size_t) w].push_back(ck);
                    }
                }
            });
            for (auto& v : tNext) { cur.insert(cur.end(), v.begin(), v.end()); v.clear(); }
        }
        std::vector<int> cntAll;                                  // child count per allExpanded entry:
        cntAll.reserve(1 << 20);                                  // recorded at DISCOVERY, kills the whole
        auto _tDisc0 = std::chrono::steady_clock::now();          // CSR count refetch pass (was fetch #2 of 3)
        while (!cur.empty()) {
            waves++;
            allExpanded.insert(allExpanded.end(), cur.begin(), cur.end());
            std::vector<int> cntCur(cur.size());
            parForN(cur.size(), T, [&](int w, size_t lo, size_t hi) {
                std::vector<int> buf;
                for (size_t i = lo; i < hi; i++) {
                    fetchChildrenPacked(cur[i], buf);
                    int cnt = buf.empty() ? 0 : buf[0];
                    cntCur[i] = cnt;
                    for (int k = 0; k < cnt; k++) {
                        const int* p = &buf[1 + k * 11];
                        long long ck = ((long long) p[0] << 20) | (p[1] & 0xFFFFF);
                        if (!seen.claim(ck)) continue;            // already known (or racing claim lost)
                        tKeys[(size_t) w].push_back(ck);
                        tRecs[(size_t) w].insert(tRecs[(size_t) w].end(), p, p + 11);
                        if (recExpandable(p)) tNext[(size_t) w].push_back(ck);
                    }
                }
            });
            cntAll.insert(cntAll.end(), cntCur.begin(), cntCur.end());
            cur.clear();
            for (auto& v : tNext) { cur.insert(cur.end(), v.begin(), v.end()); v.clear(); }
        }
        seen.drop();
        double discS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _tDisc0).count();
        // 3) order the new keys spatially: counting-sort by tileAddr (device-grid linear index), then
        //    by wire within a tile -- deterministic, independent of wave/thread interleaving.
        size_t M = 0;
        std::vector<size_t> tOff((size_t) T + 1, 0);
        for (int t = 0; t < T; t++) { tOff[(size_t) t] = M; M += tKeys[(size_t) t].size(); }
        tOff[(size_t) T] = M;
        std::vector<std::pair<long long, uint32_t>> order(M);     // (key, global rec index)
        parForN((size_t) T, T, [&](int, size_t lo, size_t hi) {
            for (size_t t = lo; t < hi; t++)
                for (size_t j = 0; j < tKeys[t].size(); j++)
                    order[tOff[t] + j] = {tKeys[t][j], (uint32_t) (tOff[t] + j)};
        });
        {   // Parallel counting sort by tileAddr (key>>20 == device-grid tile index), then per-tile sort
            // by full key: deterministic result, ~10x faster than a serial std::sort over 40M+ pairs.
            size_t NT = 1;
            for (size_t i = 0; i < M; i++) NT = std::max(NT, (size_t) (order[i].first >> 20) + 1);
            std::vector<std::atomic<uint64_t>> tileCnt(NT);
            parForN(M, T, [&](int, size_t lo, size_t hi) {
                for (size_t i = lo; i < hi; i++)
                    tileCnt[(size_t) (order[i].first >> 20)].fetch_add(1, std::memory_order_relaxed);
            });
            std::vector<uint64_t> tileOff(NT + 1, 0);
            for (size_t i = 0; i < NT; i++) tileOff[i + 1] = tileOff[i] + tileCnt[i].load(std::memory_order_relaxed);
            std::vector<std::atomic<uint64_t>> cursor(NT);
            for (size_t i = 0; i < NT; i++) cursor[i].store(tileOff[i], std::memory_order_relaxed);
            std::vector<std::pair<long long, uint32_t>> sorted(M);
            parForN(M, T, [&](int, size_t lo, size_t hi) {
                for (size_t i = lo; i < hi; i++) {
                    size_t tile = (size_t) (order[i].first >> 20);
                    sorted[cursor[tile].fetch_add(1, std::memory_order_relaxed)] = order[i];
                }
            });
            parForN(NT, T, [&](int, size_t lo, size_t hi) {       // within-tile order: sort by full key
                for (size_t t2 = lo; t2 < hi; t2++)
                    std::sort(sorted.begin() + (ptrdiff_t) tileOff[t2], sorted.begin() + (ptrdiff_t) tileOff[t2 + 1]);
            });
            order.swap(sorted);
        }
        // 4) bulk intern in sorted order: resize once, fill in parallel (distinct ids per worker)
        const int S = numNodes();
        kiGrow((size_t) (S + M) * 2);
        const size_t total = (size_t) S + M;
        if (ns.capacity() < total) reserveNodes(total + (total >> 4));
        ns.resize(total); nc.resize(total); type.resize(total);
        dyn.resize(total, NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0});
        created.resize(total, 0);
        ownerNet.resize(total, -1); ownerCnt.resize(total, 0); userOverflow.resize(total, nullptr);
        occCnt.resize(total, 0); hot.resize(total); childrenCache.resize(total, nullptr);
        overUsed.resize(total, 0); deadEnd.resize(total, 0); isSinkNode.resize(total, 0);
        rawFetched.resize(total, 0); rawChildrenStore.resize(total);
        auto recOf = [&](uint32_t g) -> const int* {              // global rec index -> 11-int record
            int t = 0; while ((size_t) t + 1 <= (size_t) T && tOff[(size_t) t + 1] <= g) t++;
            return &tRecs[(size_t) t][(g - tOff[(size_t) t]) * 11];
        };
        parForN(M, T, [&](int, size_t lo, size_t hi) {
            for (size_t r = lo; r < hi; r++) {
                const int id = S + (int) r;
                const int* p = recOf(order[r].second);
                ChildAttrs ca = unpackChild(p);
                long long key = order[r].first;
                if (!ca.hot.preserved && preserveReady && maybePreserved(key) && preserveSet.count(key))
                    ca.hot.preserved = true;
                ns[(size_t) id] = ca.hot; nc[(size_t) id] = ca.cold; type[(size_t) id] = ca.cold.type;
                initHotFromStatic(id);
                keyToId.putParallel(key, id);
            }
        });
        nodeCountA.store((int) total, std::memory_order_release);
        // 5) contiguous CSR (childStart/childCount/childIds) in NODE-ID ORDER. gpuUploadGraph derives
        // adjOff[i+1]-adjOff[i] as the child count, so childStart MUST be monotone in id (a wave-order
        // layout feeds the kernel garbage ranges). Id order == spatial order here, so the child arrays
        // land spatially local too.
        const size_t E = allExpanded.size();
        auto _tCsr0 = std::chrono::steady_clock::now();
        std::vector<int> expId(E);
        std::vector<int> cntById(total, 0);
        parForN(E, T, [&](int, size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++) {                    // counts recorded at discovery: NO refetch
                int id = keyToId.find(allExpanded[i]);
                expId[i] = id;
                cntById[(size_t) id] = cntAll[i];                 // one writer per id (expanded once)
            }
        });
        std::vector<long long> startById(total + 1, 0);
        for (size_t i = 0; i < total; i++) startById[i + 1] = startById[i] + cntById[i];
        childIds.clear();
        childIds.reserve((size_t) startById[total]);
        bindInterleave(childIds);                                 // bind the fresh VMA BEFORE first touch
        adviseHuge(childIds);                                     // CSR is the hottest read after dyn/hot
                                                                  // (1.85GB at 50per scale; was 4KB pages)
        childIds.resize((size_t) startById[total], 0);
        std::atomic<long long> untranslated{0};
        parForN(E, T, [&](int, size_t lo, size_t hi) {
            std::vector<int> buf;
            for (size_t i = lo; i < hi; i++) {
                const int id = expId[i];
                fetchChildrenPacked(allExpanded[i], buf);
                int cnt = buf.empty() ? 0 : buf[0];
                long long base = startById[(size_t) id];
                int out = 0;                                      // compact: NEVER emit an unresolved child
                for (int k = 0; k < cnt; k++) {
                    const int* p = &buf[1 + k * 11];
                    int cid = keyToId.find(((long long) p[0] << 20) | (p[1] & 0xFFFFF));
                    if (cid < 0) { untranslated.fetch_add(1, std::memory_order_relaxed); continue; }
                    childIds[(size_t) base + out++] = cid;
                }
                for (int k = out; k < cnt; k++) childIds[(size_t) base + k] = id;   // pad gap: self-edge never relaxes
                ns[(size_t) id].childStart = (int) base;
                ns[(size_t) id].childCount = out;
            }
        });
        parForN(total, T, [&](int, size_t lo, size_t hi) {        // un-expanded ids: empty but MONOTONE slots
            for (size_t id = lo; id < hi; id++)
                if (!cntById[id]) { ns[id].childStart = (int) startById[id]; ns[id].childCount = 0; }
        });
        if (untranslated.load() > 0)
            std::fprintf(stderr, "[par] prepass WARNING: %lld child keys had no id (dropped from CSR)\n",
                         untranslated.load());
        lazy = false;                                             // non-lazy from here: CSR path, no interning
        flatGraphBuilt = true;                                    // setupFloodGpuNow must NOT rebuild childIds
        std::fprintf(stderr,
            "[par] prepass: seeds=%d +new=%zu total=%zu expanded=%zu edges=%lld waves=%d cover=%dx%d in %.2fs (disc=%.2fs csr=%.2fs; 2-fetch, spatial ids, lazy->eager)\n",
            S, M, total, E, startById[total], waves, W, H,
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count(),
            discS, std::chrono::duration<double>(std::chrono::steady_clock::now() - _tCsr0).count());
    }

    // ===== prepass-early (hide the prepass behind Java initialize) ==============================
    // Runs the SAME closure/CSR build, but seeded from Java-projected pin INT nodes and covered by
    // per-net pin rects dilated by (bbExt + laguna-snap) margins -- a SUPERSET of every conn bbox
    // interior, verified after loadLazy (verifyEarlyCover). Ids stay device-ordered (deterministic
    // given the pin set). Seeds interned AFTER the CSR (rare alt sources) get their child ranges
    // APPENDED by patchLateSeeds (monotone childStart preserved for the GPU upload).
    void prepassEarly(const std::vector<long long>& seedKeys, const std::vector<int>& rects) {
        const int MX = 20, MY = 64;                    // bbExt 12/60 + snap slack. 28/70 inflated the closure
                                                       // 41->50.6M (X margin dominates on a 149-col device) and
                                                       // degraded floods; rare cover misses hit the verified fallback
        int W = 0, H = 0;
        for (size_t i = 0; i + 3 < rects.size(); i += 4) { W = std::max(W, rects[i + 2] + MX); H = std::max(H, rects[i + 3] + MY); }
        W += 2; H += 2;
        std::vector<uint8_t> cover((size_t) W * H, 0);
        for (size_t i = 0; i + 3 < rects.size(); i += 4) {
            int x0 = std::max(rects[i] - MX, 0), x1 = std::min(rects[i + 2] + MX, W - 1);
            int y0 = std::max(rects[i + 1] - MY, 0), y1 = std::min(rects[i + 3] + MY, H - 1);
            for (int y = y0; y <= y1; y++) memset(&cover[(size_t) y * W + x0], 1, (size_t) (x1 - x0 + 1));
        }
        lazyPrepassMaterialize(&cover, W, H, &seedKeys);
        earlyTotal = numNodes();
    }

#ifdef WITH_JNI
    // ===== prepass-fulldev (20per-class): adopt the ENTIRE device model as the eager routing graph =
    // For inputs whose pin cover is ~the whole device anyway (THEIA_20per: 103.2M of 103.8M nodes),
    // the cover-based closure build (BFS discovery + 2-fetch CSR, ~24.5s) reduces to a direct array
    // transform of the DeviceModel: its dense ids are assigned in ascending (tileAddr, canonical wire)
    // order -- exactly the spatial order the prepass sorts into -- and srcKids already stores child
    // DENSE ids, so nodes and CSR copy over with no fetching at all (~4s). Runs at PREWARM time
    // (window: readCheckpoint+preprocess+initialize ~40s), so the old ~12s residual wait vanishes.
    // Search equivalence: every connection search is bbox-bounded and the old cover was a superset of
    // every conn bbox interior, so any node reachable within a bbox has identical adjacency in both
    // builds -> routing results identical (oracle: wl/totalPIPs must match the cover-based build).
    void prepassFullDevice(dev::DeviceModel* dm) {
        auto _t0 = std::chrono::steady_clock::now();
        const int T = std::max(1, parPart);
        const size_t M = (size_t) dm->nNodes;
        int W = 0, H = 0;                              // full-device cover extent (all-ones bitmap)
        {
            std::vector<int> tw((size_t) T, 0), th2((size_t) T, 0);
            parForN(M, T, [&](int w, size_t lo, size_t hi) {
                int mx = 0, my = 0;
                for (size_t i = lo; i < hi; i++) {
                    const dev::NodeRec& R = dm->nrecP[i];
                    if (R.ex > mx) mx = R.ex; if (R.bx > mx) mx = R.bx;
                    if (R.ey > my) my = R.ey; if (R.by > my) my = R.by;
                }
                tw[(size_t) w] = mx; th2[(size_t) w] = my;
            });
            for (int t = 0; t < T; t++) { W = std::max(W, tw[(size_t) t]); H = std::max(H, th2[(size_t) t]); }
            W += 2; H += 2;
        }
        prepassCoverStore.assign((size_t) W * H, 1); prepassW = W; prepassH = H;
        const int S = numNodes();                      // 0 in the prewarm router; keep general anyway
        kiGrow((size_t) (S + M) * 2);
        const size_t total = (size_t) S + M;
        if (ns.capacity() < total) reserveNodes(total + (total >> 4));
        ns.resize(total); nc.resize(total); type.resize(total);
        dyn.resize(total, NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0});
        created.resize(total, 0);
        ownerNet.resize(total, -1); ownerCnt.resize(total, 0); userOverflow.resize(total, nullptr);
        occCnt.resize(total, 0); hot.resize(total); childrenCache.resize(total, nullptr);
        overUsed.resize(total, 0); deadEnd.resize(total, 0); isSinkNode.resize(total, 0);
        rawFetched.resize(total, 0); rawChildrenStore.resize(total);
        parForN(M, T, [&](int, size_t lo, size_t hi) {
            int rec[11];
            for (size_t r = lo; r < hi; r++) {
                const int id = S + (int) r;
                const dev::NodeRec& R = dm->nrecP[r];
                long long key = (long long) R.baseKey;
                rec[0] = (int) (key >> 20); rec[1] = (int) (key & 0xFFFFF);
                rec[2] = R.type; rec[3] = R.flags4;
                rec[4] = R.bx; rec[5] = R.by; rec[6] = R.ex; rec[7] = R.ey;
                rec[8] = R.len; std::memcpy(&rec[9], &R.baseCost, sizeof(float)); rec[10] = R.hash;
                ChildAttrs ca = unpackChild(rec);   // EXACT same transform as the fetch path
                if (!ca.hot.preserved && preserveReady && maybePreserved(key) && preserveSet.count(key))
                    ca.hot.preserved = true;
                ns[(size_t) id] = ca.hot; nc[(size_t) id] = ca.cold; type[(size_t) id] = ca.cold.type;
                initHotFromStatic(id);
                keyToId.putParallel(key, id);
            }
        });
        nodeCountA.store((int) total, std::memory_order_release);
        // contiguous CSR straight from the device model (srcKids entries ARE dense ids == our ids)
        std::vector<int> cntById(total, 0);
        parForN(M, T, [&](int, size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++) {
                long long key = (long long) dm->nrecP[i].baseKey;
                int32_t src = dm->srcIdOfP[(size_t) dm->wbP[key >> 20] + (key & 0xFFFFF)];
                cntById[(size_t) S + i] = src >= 0 ? (int) (dm->srcOffP[(size_t) src + 1] - dm->srcOffP[(size_t) src]) : 0;
            }
        });
        std::vector<long long> startById(total + 1, 0);
        for (size_t i = 0; i < total; i++) startById[i + 1] = startById[i] + cntById[i];
        childIds.clear();
        childIds.reserve((size_t) startById[total]);
        bindInterleave(childIds);
        adviseHuge(childIds);
        childIds.resize((size_t) startById[total], 0);
        parForN(M, T, [&](int, size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++) {
                const size_t id = (size_t) S + i;
                const int cnt = cntById[id];
                const long long base = startById[id];
                if (cnt > 0) {
                    long long key = (long long) dm->nrecP[i].baseKey;
                    int32_t src = dm->srcIdOfP[(size_t) dm->wbP[key >> 20] + (key & 0xFFFFF)];
                    const int32_t* kids = &dm->srcKidsP[(size_t) dm->srcOffP[(size_t) src]];
                    for (int k = 0; k < cnt; k++) childIds[(size_t) base + k] = S + kids[k];
                }
                ns[id].childStart = (int) base;
                ns[id].childCount = cnt;
            }
        });
        lazy = false;
        flatGraphBuilt = true;
        earlyTotal = numNodes();
        std::fprintf(stderr,
            "[par] prepass-fulldev: nodes=%zu edges=%lld cover=%dx%d in %.2fs (direct device-model adoption)\n",
            total, startById[total], W, H,
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count());
    }
#endif

    bool verifyEarlyCover() {                          // every conn bbox interior inside the early cover?
        const int W = prepassW, H = prepassH;
        std::vector<long long> pre((size_t) (W + 1) * (H + 1), 0);   // 2D prefix sum -> O(1) area query
        for (int y = 0; y < H; y++)
            for (int x = 0; x < W; x++)
                pre[(size_t) (y + 1) * (W + 1) + x + 1] = pre[(size_t) y * (W + 1) + x + 1]
                    + pre[(size_t) (y + 1) * (W + 1) + x] - pre[(size_t) y * (W + 1) + x]
                    + prepassCoverStore[(size_t) y * W + x];
        long long bad = 0;
        for (const auto& c : connections) {
            if (c.abandoned) continue;
            int x0 = std::max((int) c.xMinBB + 1, 0), x1 = std::min((int) c.xMaxBB - 1, W - 1);
            int y0 = std::max((int) c.yMinBB + 1, 0), y1 = std::min((int) c.yMaxBB - 1, H - 1);
            if (x1 < x0 || y1 < y0) continue;
            long long area = (long long) (x1 - x0 + 1) * (y1 - y0 + 1);
            long long got = pre[(size_t) (y1 + 1) * (W + 1) + x1 + 1] - pre[(size_t) y0 * (W + 1) + x1 + 1]
                          - pre[(size_t) (y1 + 1) * (W + 1) + x0] + pre[(size_t) y0 * (W + 1) + x0];
            if (got != area) bad++;
        }
        if (bad) std::fprintf(stderr, "[par] prepass-early cover MISS on %lld conns -> full re-prepass\n", bad);
        return bad == 0;
    }

    void patchLateSeeds(int firstLateId) {             // append CSR ranges for seeds interned after the build
        const int N = numNodes();
        const int M = N - firstLateId;
        if (M <= 0) return;
        const int T = std::max(1, parPart);
        if (T > 1 && M > 10000) {
            // The 570k serial fetchChildrenPacked calls were the cost (~2.3s): prefetch + translate in
            // parallel (read-only device-model walks), then append serially IN ID ORDER -- the childIds
            // layout and every childStart/childCount come out byte-identical to the serial loop.
            std::vector<std::vector<int>> cids((size_t) M);
            parForN((size_t) M, T, [&](int, size_t lo, size_t hi) {
                std::vector<int> buf;
                for (size_t i = lo; i < hi; i++) {
                    fetchChildrenPacked(keyOf(firstLateId + (int) i), buf);
                    int cnt = buf.empty() ? 0 : buf[0];
                    auto& out = cids[i];
                    out.reserve((size_t) cnt);
                    for (int k = 0; k < cnt; k++) {
                        const int* p = &buf[1 + k * 11];
                        int cid = keyToId.find(((long long) p[0] << 20) | (p[1] & 0xFFFFF));
                        if (cid >= 0) out.push_back(cid);
                    }
                }
            });
            for (int i = 0; i < M; i++) {
                long long base = (long long) childIds.size();
                childIds.insert(childIds.end(), cids[(size_t) i].begin(), cids[(size_t) i].end());
                ns[(size_t) (firstLateId + i)].childStart = (int) base;
                ns[(size_t) (firstLateId + i)].childCount = (int) cids[(size_t) i].size();
            }
            std::fprintf(stderr, "[par] prepass-early: patched %d late seeds (parallel prefetch)\n", M);
            return;
        }
        std::vector<int> buf;
        for (int id = firstLateId; id < N; id++) {
            fetchChildrenPacked(keyOf(id), buf);
            int cnt = buf.empty() ? 0 : buf[0];
            long long base = (long long) childIds.size();
            int out = 0;
            for (int k = 0; k < cnt; k++) {
                const int* p = &buf[1 + k * 11];
                long long ck = ((long long) p[0] << 20) | (p[1] & 0xFFFFF);
                int cid = keyToId.find(ck);
                if (cid >= 0) { childIds.push_back(cid); out++; }
            }
            ns[(size_t) id].childStart = (int) base;
            ns[(size_t) id].childCount = out;
        }
        std::fprintf(stderr, "[par] prepass-early: patched %d late seeds\n", M);
    }

    // enlargeBoundingBox is a no-op (--fixBoundingBox); swapOutputPin needs an alternate
    // output pin, which the export does not (yet) provide, so it returns false. With a fixed
    // bounding box the connection is then abandoned (mirrors abandonConnectionIfUnroutable()).
    bool handleUnroutableConnection(int idx) {
        Connection& c = connections[idx];
        if (cfg.enlargeBoundingBox) {
            c.xMinBB -= cfg.extensionXIncrement; c.xMaxBB += cfg.extensionXIncrement;
            c.yMinBB -= cfg.extensionYIncrement; c.yMaxBB += cfg.extensionYIncrement;
            if (c.xMinBB < 0) c.xMinBB = -1;
            if (c.yMinBB < 0) c.yMinBB = -1;
        }
        // swapOutputPin needs an alternate output pin (not exported yet) -> returns false.
        if (cfg.useBoundingBox && !cfg.enlargeBoundingBox) {
            c.abandoned = true;  // abandonConnectionIfUnroutable()
        }
        return false;
    }

    void updatePresentCongestionCosts(float factor) {
        for (int occ = 0; occ < 256; occ++) {
            int overuse = occ - CAPACITY;
            if (overuse < 0) presentCongestionCosts[occ] = 1;  // initialPresentCongestionCost
            else presentCongestionCosts[occ] = 1 + (overuse + 1) * factor;
        }
    }

    bool incUpdateCost = rwEnvI("RW_INC_UPDATECOST", 1) != 0;   // incremental boundary scan (bit-exact superset)
    std::vector<int> updCand;                                   // candidate scratch (reused across iterations)

    void updateCost() {
        bprof::Scope b_scope(bprof::UPDATE_COST);
        const int Nn = numNodes();
        // Incremental candidate path: a node can only be overused at THIS boundary if it was overused
        // at the previous one (previous overUsedList) or its occupancy was incremented since -- and all
        // increments flow through updateUsersAndPresentCongestionCost, which stamps its connection.
        // (>= routeIteration-1 also catches post-boundary commits from handleUnroutableConnection /
        // alpha-probe restores.) Candidates are sorted+deduped, so membership, hist bumps, list order
        // and the overuse total are BYTE-IDENTICAL to the full ascending scan. Falls back to the full
        // scan whenever the candidate estimate is large (early iterations) -- the sort would cost more
        // than the O(N) parallel sweep there.
        if (incUpdateCost && routeIteration > 2) {
            updCand.clear();
            updCand.insert(updCand.end(), overUsedList.begin(), overUsedList.end());
            const size_t cap = (size_t) Nn / 64;
            bool small = true;
            for (const Connection& c : connections) {
                if (c.routedIter < routeIteration - 1) continue;
                if (updCand.size() + c.rnodes.size() > cap) { small = false; break; }
                updCand.insert(updCand.end(), c.rnodes.begin(), c.rnodes.end());
            }
            if (small) {
                std::sort(updCand.begin(), updCand.end());
                updCand.erase(std::unique(updCand.begin(), updCand.end()), updCand.end());
                for (int id : overUsedList) overUsed[id] = 0;
                overUsedList.clear();
                long long tot = 0;
                for (int id : updCand) {
                    if (id < 0 || id >= Nn || !created[id]) continue;
                    int overuse = getOccupancy(id) - CAPACITY;
                    if (overuse > 0) {
                        overUsed[id] = 1;
                        overUsedList.push_back(id);
                        dyn[id].hist += overuse * historicalCongestionFactor;
                        tot += overuse;
                    }
                }
                currentTotalOveruse = tot;
                return;
            }
        }
        for (int id : overUsedList) overUsed[id] = 0;
        overUsedList.clear();
        // Iteration-boundary O(N) scan was SERIAL (jpeg 8.4s / THEIA 13.8s total across iterations,
        // measured as iter-wall minus par-stats sums). Parallelize: per-range lists concatenated in
        // thread order == ascending-id order == byte-identical to the serial list; hist writes are
        // id-disjoint. Serial fallback for tiny N or parPart==0 keeps the old path bit-exact.
        const int N = numNodes();
        const int T = std::max(1, parPart);
        if (T > 1 && N > (1 << 20)) {
            std::vector<std::vector<int>> tOver((size_t) T);
            std::vector<long long> tTot((size_t) T, 0);
            parForN((size_t) N, T, [&](int w, size_t lo, size_t hi) {
                std::vector<int>& ov = tOver[(size_t) w];
                long long tot = 0;
                for (size_t id = lo; id < hi; id++) {
                    if (!created[id]) continue;
                    int overuse = getOccupancy((int) id) - CAPACITY;
                    if (overuse > 0) {
                        overUsed[id] = 1;
                        ov.push_back((int) id);
                        dyn[id].hist += overuse * historicalCongestionFactor;
                        tot += overuse;
                    }
                }
                tTot[(size_t) w] = tot;
            });
            long long tot = 0;
            for (int w = 0; w < T; w++) {
                overUsedList.insert(overUsedList.end(), tOver[(size_t) w].begin(), tOver[(size_t) w].end());
                tot += tTot[(size_t) w];
            }
            currentTotalOveruse = tot;
            return;
        }
        long long tot = 0;
        for (int id = 0; id < N; id++) {
            if (!created[id]) continue;
            int overuse = getOccupancy(id) - CAPACITY;
            if (overuse > 0) {
                overUsed[id] = 1;
                overUsedList.push_back(id);
                dyn[id].hist += overuse * historicalCongestionFactor;
                tot += overuse;
            }
        }
        currentTotalOveruse = tot;   // GRoute progress factor: sum of node overuse at end of this iteration
    }

    void updateCostFactors() {
        presentCongestionFactor *= cfg.presentCongestionMultiplier;
        presentCongestionFactor = std::min(presentCongestionFactor, cfg.maxPresentCongestionFactor);
        updateCost();
    }

    void sortConnections() {
        sortedIndirect = indirectAll;
        auto cmp = [&](int a, int b) {
            const Connection& c1 = connections[a];
            const Connection& c2 = connections[b];
            if (c1.hpwl != c2.hpwl) return c1.hpwl < c2.hpwl;
            int f1 = nets[c1.netIdx].connectionsSize, f2 = nets[c2.netIdx].connectionsSize;
            if (f1 != f2) return f1 > f2;
            return nc[c1.sinkRnode].hashCode < nc[c2.sinkRnode].hashCode;
        };
        // Parallel stable sort: stable_sort per position-range, then pairwise stable merges
        // (std::merge takes from the LEFT range on ties = range order = original position order),
        // so the result is the unique stable-sort permutation -- BYTE-IDENTICAL to the serial
        // std::stable_sort (20per: 1.45s -> ~0.3s; comparator cost is dominated by the random
        // Connection-array cache misses, so range-parallelism is near-linear).
        const size_t n = sortedIndirect.size();
        const int T = std::min(8, std::max(1, parPart));
        if (T > 1 && n > (1 << 20)) {
            std::vector<size_t> cut((size_t) T + 1);
            for (int t = 0; t <= T; t++) cut[(size_t) t] = n * (size_t) t / (size_t) T;
            parForN((size_t) T, T, [&](int, size_t lo, size_t hi) {
                for (size_t t = lo; t < hi; t++)
                    std::stable_sort(sortedIndirect.begin() + (ptrdiff_t) cut[t],
                                     sortedIndirect.begin() + (ptrdiff_t) cut[t + 1], cmp);
            });
            std::vector<int> tmp(n);
            std::vector<size_t> c2v(cut);
            for (int width = 1; width < T; width <<= 1) {
                std::vector<std::pair<size_t, size_t>> jobs;   // (left cut idx step)
                for (int t = 0; t + width < T; t += 2 * width) jobs.push_back({(size_t) t, (size_t) width});
                parForN(jobs.size(), (int) std::min((size_t) T, jobs.size()), [&](int, size_t lo, size_t hi) {
                    for (size_t j = lo; j < hi; j++) {
                        size_t t = jobs[j].first, w = jobs[j].second;
                        size_t a = c2v[t], b = c2v[t + w], c = c2v[std::min((size_t) T, t + 2 * w)];
                        std::merge(sortedIndirect.begin() + (ptrdiff_t) a, sortedIndirect.begin() + (ptrdiff_t) b,
                                   sortedIndirect.begin() + (ptrdiff_t) b, sortedIndirect.begin() + (ptrdiff_t) c,
                                   tmp.begin() + (ptrdiff_t) a, cmp);
                        std::copy(tmp.begin() + (ptrdiff_t) a, tmp.begin() + (ptrdiff_t) c,
                                  sortedIndirect.begin() + (ptrdiff_t) a);
                    }
                });
            }
            return;
        }
        std::stable_sort(sortedIndirect.begin(), sortedIndirect.end(), cmp);
    }

    // ---- Track D: coarse-grid global routing -> tighten per-connection detailed-routing bbox ----
    // Builds a CELLxCELL congestion grid from node end-coords + occupancy, routes each LONG
    // connection's source->sink congestion-weighted shortest path on the coarse mesh (corridor),
    // and shrinks its bbox to the corridor (+margin), INTERSECTED with the original box (never grows).
    // Short connections use the source/sink cell rectangle. Cross-SLR connections are skipped (need
    // the tall default box). D0 here is CPU (multi-threaded Dijkstra); D1 will swap the corridor solve
    // to a CUDA kernel. Opt-in via RW_BBOX so the banked control is unchanged until validated.
    void tightenBoundingBoxesCoarse() {
        if (!cfg.useBoundingBox) return;
        const int CELL    = std::max(1, rwEnvI("RW_GPU_CELL", 4));
        const int SPAN    = rwEnvI("RW_GPU_SPAN", 16);
        const int MARGINc = rwEnvI("RW_GPU_MARGIN", 1);
        const int BBM     = std::max(8, rwEnvI("RW_GPU_BBMARGIN", 32)); // Dijkstra search margin (cells)
        const int N = (int) ns.size();
        if (N <= 1) return;
        auto _t0 = std::chrono::steady_clock::now();

        // 1) extent over all node end-coords (parallel min/max reduction: exact, order-independent)
        const int PT = std::max(1, rwMaxThreads());
        int xmin = std::numeric_limits<int>::max(), xmax = std::numeric_limits<int>::min();
        int ymin = std::numeric_limits<int>::max(), ymax = std::numeric_limits<int>::min();
        {
            std::vector<std::array<int, 4>> ext((size_t) PT, {INT32_MAX, INT32_MIN, INT32_MAX, INT32_MIN});
            parForN((size_t) N, PT, [&](int t, size_t lo, size_t hi) {
                auto& e4 = ext[(size_t) t];
                for (size_t i = lo; i < hi; i++) {
                    int x = ns[i].endX, y = ns[i].endY;
                    if (x < e4[0]) e4[0] = x; if (x > e4[1]) e4[1] = x;
                    if (y < e4[2]) e4[2] = y; if (y > e4[3]) e4[3] = y;
                }
            });
            for (auto& e4 : ext) {
                xmin = std::min(xmin, e4[0]); xmax = std::max(xmax, e4[1]);
                ymin = std::min(ymin, e4[2]); ymax = std::max(ymax, e4[3]);
            }
        }
        if (xmin > xmax) return;
        const int gW = (xmax - xmin) / CELL + 1, gH = (ymax - ymin) / CELL + 1;
        const long NC = (long) gW * gH;
        if (NC <= 1 || NC > 20000000L) return;
        auto cellOf = [&](int tx, int ty) -> int {
            int gx = (tx - xmin) / CELL, gy = (ty - ymin) / CELL;
            if (gx < 0 || gx >= gW || gy < 0 || gy >= gH) return -1;
            return gy * gW + gx;
        };

        // 2) per-cell cost of entering = 1 + #occupied rnodes in the cell (initial congestion map).
        // Parallel per-thread int histograms + reduce: exact (integer counts), bit-identical to serial.
        std::vector<float> nodeCosts((size_t) NC, 1.0f);
        if (NC <= (1L << 20)) {
            std::vector<std::vector<int>> th((size_t) PT);
            parForN((size_t) N, PT, [&](int t, size_t lo, size_t hi) {
                auto& h = th[(size_t) t];
                h.assign((size_t) NC, 0);
                for (size_t i = lo; i < hi; i++)
                    if (occCnt[i] > 0) { int c = cellOf(ns[i].endX, ns[i].endY); if (c >= 0) h[(size_t) c]++; }
            });
            for (auto& h : th)
                if (!h.empty())
                    for (long c = 0; c < NC; c++) nodeCosts[(size_t) c] += (float) h[(size_t) c];
        } else {
            for (int i = 0; i < N; i++) {
                if (occCnt[i] > 0) { int c = cellOf(ns[i].endX, ns[i].endY); if (c >= 0) nodeCosts[(size_t) c] += 1.0f; }
            }
        }

        // 3) candidate connections (skip cross-SLR / off-grid); record src/sink cell
        std::vector<int> cand; std::vector<int> srcC, sinkC;
        cand.reserve(sortedIndirect.size());
        for (int idx : sortedIndirect) {
            Connection& c = connections[idx];
            if (c.isCrossSLR()) continue;
            int sc = cellOf(getEndTileXCoordinate(c.sourceRnode), getEndTileYCoordinate(c.sourceRnode));
            int tc = cellOf(getEndTileXCoordinate(c.sinkRnode),   getEndTileYCoordinate(c.sinkRnode));
            if (sc < 0 || tc < 0) continue;
            cand.push_back(idx); srcC.push_back(sc); sinkC.push_back(tc);
        }
        const int M = (int) cand.size();
        if (M == 0) return;
        // corridor cell-range per candidate: default = src/sink rectangle (short conns keep this)
        std::vector<int> cMinX(M), cMaxX(M), cMinY(M), cMaxY(M);
        for (int i = 0; i < M; i++) {
            int sgx = srcC[i] % gW, sgy = srcC[i] / gW, tgx = sinkC[i] % gW, tgy = sinkC[i] / gW;
            cMinX[i] = std::min(sgx, tgx); cMaxX[i] = std::max(sgx, tgx);
            cMinY[i] = std::min(sgy, tgy); cMaxY[i] = std::max(sgy, tgy);
        }

        // 4) LONG connections get a congestion-weighted shortest-path corridor (multi-threaded Dijkstra)
        std::vector<int> longIdx;
        for (int i = 0; i < M; i++) if (connections[cand[i]].hpwl >= SPAN) longIdx.push_back(i);
        const int ML = (int) longIdx.size();
        bool gpuDone = false; const char* solver = "cpu";
        double tPrep = std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count();
        std::vector<int> gpuCorrCmp;                     // RW_BBOX_GPU=2: stash for the CPU-vs-GPU diff
#ifdef WITH_CUDA
        // D1: solve the long-connection corridors on the GPU (CUDA). Build the coarse mesh CSR + xy,
        // run the batched (window-bounded) Bellman-Ford kernel; any failure falls through to the CPU
        // Dijkstra below. Default GPU only on the huge band (>=3.5M conns): BF and Dijkstra tie-break
        // equal-cost paths differently, so corridors (hence bboxes, hence routing) may diverge -- the
        // huge band already diverges from gold, everything else keeps the bit-identical CPU solve.
        // RW_BBOX_GPU: 0=cpu, 1=gpu, 2=run both + report corridor diffs (CPU result wins).
        // Default CPU: on this host's永-saturated GPUs the solve measured ~7x SLOWER than the T=48
        // CPU Dijkstra (50per probe: gpu ~29s vs cpu ~4s; corridor tie-break drift 2.5% of 1.13M).
        // On an exclusive-GPU machine set RW_BBOX_GPU=1 (windowed kernel, huge band only -- the
        // drift diverges routing, acceptable only where we already diverge from gold).
        const int bboxGpu = (int) rwEnvI("RW_BBOX_GPU", 0);
        if (ML > 0 && bboxGpu && gpuBboxAvailable()) {
            std::vector<int> adjOff((size_t) NC + 1);
            std::vector<int> adjList; adjList.reserve((size_t) NC * 4);
            std::vector<short> xy((size_t) NC * 2);
            for (long c = 0; c < NC; c++) {
                int gx = (int)(c % gW), gy = (int)(c / gW);
                adjOff[(size_t) c] = (int) adjList.size();
                if (gx > 0)      adjList.push_back((int) c - 1);
                if (gx < gW - 1) adjList.push_back((int) c + 1);
                if (gy > 0)      adjList.push_back((int) c - gW);
                if (gy < gH - 1) adjList.push_back((int) c + gW);
                xy[2 * (size_t) c] = (short) gx; xy[2 * (size_t) c + 1] = (short) gy;
            }
            adjOff[(size_t) NC] = (int) adjList.size();
            std::vector<int> pairs((size_t) ML * 2), corr((size_t) ML * 4, -1);
            for (int li = 0; li < ML; li++) { int i = longIdx[li]; pairs[2 * li] = srcC[i]; pairs[2 * li + 1] = sinkC[i]; }
            int maxHops = gW + gH + 16;
            const int keepCtx = rwEnvI("RW_GPU_FLOOD", 0) != 0;   // flood re-creates the context right after
            int rc = gpuSolveCorridors(gW, gH, adjOff.data(), adjList.data(), nodeCosts.data(), xy.data(),
                                       (int) NC, pairs.data(), ML, maxHops, BBM, keepCtx, corr.data());
            if (rc == 0 && bboxGpu == 2) {
                gpuCorrCmp = std::move(corr);            // stash only: the CPU solve below stays authoritative
            } else if (rc == 0) {
                for (int li = 0; li < ML; li++) if (corr[4 * li] >= 0) {
                    int i = longIdx[li];
                    cMinX[i] = corr[4 * li]; cMaxX[i] = corr[4 * li + 1];
                    cMinY[i] = corr[4 * li + 2]; cMaxY[i] = corr[4 * li + 3];
                }
                gpuDone = true; solver = "gpu";
            }
        }
#endif
        int T = gpuDone ? 0 : std::max(1, std::min(rwMaxThreads(), (int) std::thread::hardware_concurrency()));
        if (ML < 256 && T > 1) T = 1;
        auto worker = [&](int t) {
            std::vector<float> dist((size_t) NC, 0.0f);
            std::vector<int> stamp((size_t) NC, -1), prev((size_t) NC, -1);
            std::vector<std::pair<float,int>> heap;
            std::greater<std::pair<float,int>> gt;
            for (int li = t; li < ML; li += T) {
                int i = longIdx[li]; int s = srcC[i], d = sinkC[i];
                int sgx = s % gW, sgy = s / gW, tgx = d % gW, tgy = d / gW;
                int bxlo = std::min(sgx, tgx) - BBM, bxhi = std::max(sgx, tgx) + BBM;
                int bylo = std::min(sgy, tgy) - BBM, byhi = std::max(sgy, tgy) + BBM;
                heap.clear();
                stamp[s] = li; dist[s] = 0.0f; prev[s] = -1;
                heap.push_back({0.0f, s}); std::push_heap(heap.begin(), heap.end(), gt);
                bool found = false;
                while (!heap.empty()) {
                    std::pop_heap(heap.begin(), heap.end(), gt);
                    auto top = heap.back(); heap.pop_back();
                    int v = top.second; float dv = top.first;
                    if (stamp[v] == li && dv > dist[v]) continue;   // stale
                    if (v == d) { found = true; break; }
                    int vgx = v % gW, vgy = v / gW;
                    int nb[4]; int nn = 0;
                    if (vgx > bxlo && vgx > 0)        nb[nn++] = v - 1;
                    if (vgx < bxhi && vgx < gW - 1)   nb[nn++] = v + 1;
                    if (vgy > bylo && vgy > 0)        nb[nn++] = v - gW;
                    if (vgy < byhi && vgy < gH - 1)   nb[nn++] = v + gW;
                    for (int k = 0; k < nn; k++) {
                        int u = nb[k]; float nd = dv + nodeCosts[(size_t) u];
                        if (stamp[u] != li || nd < dist[u]) {
                            stamp[u] = li; dist[u] = nd; prev[u] = v;
                            heap.push_back({nd, u}); std::push_heap(heap.begin(), heap.end(), gt);
                        }
                    }
                }
                if (found) {
                    int mnx = gW, mxx = -1, mny = gH, mxy = -1, cur = d, guard = 0;
                    while (cur != -1 && guard++ <= NC) {
                        int gx = cur % gW, gy = cur / gW;
                        if (gx < mnx) mnx = gx; if (gx > mxx) mxx = gx;
                        if (gy < mny) mny = gy; if (gy > mxy) mxy = gy;
                        if (cur == s) break;
                        cur = prev[cur];
                    }
                    if (cur == s) { cMinX[i] = mnx; cMaxX[i] = mxx; cMinY[i] = mny; cMaxY[i] = mxy; }
                }
            }
        };
        std::vector<std::thread> th;
        for (int t = 0; t < T; t++) th.emplace_back(worker, t);
        for (auto& x : th) x.join();
        if (!gpuCorrCmp.empty()) {                       // RW_BBOX_GPU=2: quantify GPU-vs-CPU corridor drift
            long diff = 0, gpuMiss = 0;
            for (int li = 0; li < ML; li++) {
                int i = longIdx[li];
                if (gpuCorrCmp[4 * li] < 0) { gpuMiss++; continue; }
                if (gpuCorrCmp[4 * li] != cMinX[i] || gpuCorrCmp[4 * li + 1] != cMaxX[i] ||
                    gpuCorrCmp[4 * li + 2] != cMinY[i] || gpuCorrCmp[4 * li + 3] != cMaxY[i]) diff++;
            }
            std::fprintf(stderr, "INFO: [bbox] gpu-vs-cpu corridors: differ=%ld gpuMiss=%ld of %d\n",
                         diff, gpuMiss, ML);
        }

        // 5) tighten: corridor cells -> tile box (+margin), union src/sink tiles, intersect original
        int tightened = 0;
        for (int i = 0; i < M; i++) {
            Connection& c = connections[cand[i]];
            int nxMin = xmin + (cMinX[i] - MARGINc) * CELL;
            int nxMax = xmin + (cMaxX[i] + 1 + MARGINc) * CELL;
            int nyMin = ymin + (cMinY[i] - MARGINc) * CELL;
            int nyMax = ymin + (cMaxY[i] + 1 + MARGINc) * CELL;
            int sx = getEndTileXCoordinate(c.sourceRnode), sy = getEndTileYCoordinate(c.sourceRnode);
            int tx = getEndTileXCoordinate(c.sinkRnode),   ty = getEndTileYCoordinate(c.sinkRnode);
            nxMin = std::min(nxMin, std::min(sx, tx)); nxMax = std::max(nxMax, std::max(sx, tx));
            nyMin = std::min(nyMin, std::min(sy, ty)); nyMax = std::max(nyMax, std::max(sy, ty));
            int fxMin = std::max((int) c.xMinBB, nxMin), fxMax = std::min((int) c.xMaxBB, nxMax);
            int fyMin = std::max((int) c.yMinBB, nyMin), fyMax = std::min((int) c.yMaxBB, nyMax);
            if (fxMin <= fxMax && fyMin <= fyMax) {
                c.xMinBB = (short) fxMin; c.xMaxBB = (short) fxMax;
                c.yMinBB = (short) fyMin; c.yMaxBB = (short) fyMax; tightened++;
            }
        }
        double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count();
        std::fprintf(stderr, "INFO: [bbox] coarse tighten cell=%d span=%d margin=%d grid=%dx%d cand=%d long=%d solver=%s tightened=%d prep=%.2fs solve=%.2fs\n",
                     CELL, SPAN, MARGINc, gW, gH, M, ML, solver, tightened, tPrep, secs - tPrep);
    }

#ifdef WITH_CUDA
    // Build the CSR + per-node attrs from the eager graph and upload the resident GPU routing graph.
    bool gpuUploadGraph() {
        if (lazy && !flatGraphBuilt) { std::fprintf(stderr, "[gpu-route] needs the eager graph\n"); return false; }
        if (!gpuRouteAvailable()) { std::fprintf(stderr, "[gpu-route] no CUDA device\n"); return false; }
        int N = numNodes(); long E = (long) childIds.size();
        std::vector<int> adjOff((size_t) N + 1);
        for (int i = 0; i < N; i++) adjOff[i] = ns[i].childStart;
        adjOff[N] = (int) E;
        std::vector<short> endX(N), endY(N), length(N);
        std::vector<float> baseCost(N);
        std::vector<unsigned char> blocked(N);
        for (int i = 0; i < N; i++) {
            endX[i] = ns[i].endX; endY[i] = ns[i].endY; length[i] = ns[i].length; baseCost[i] = ns[i].baseCost;
            if (ns[i].preserved || type[i] == RouteNodeType::INACCESSIBLE) blocked[i] = 1;
            else if (isAnyExclusiveSink(type[i])) blocked[i] = 2; else blocked[i] = 0;
        }
        return gpuRouteInit(N, E, adjOff.data(), childIds.data(), endX.data(), endY.data(),
                            baseCost.data(), length.data(), blocked.data()) == 0;
    }

    // Lazy (JNI) path: build the flat CSR (childIds + ns[].childStart) from the per-node rawChildrenStore that
    // iteration 1 already fetched, so gpuUploadGraph can run. Nodes interned-but-not-expanded (rawFetched=0)
    // contribute 0 edges -> the flood dead-ends there and the CPU fallback handles them (never illegal). The
    // CPU keeps using the lazy rawChildrenStore path; childStart/childIds are consumed only by the GPU upload.
    void materializeFlatGraphFromLazy() {
        int N = numNodes();
        long long total = 0;
        for (int i = 0; i < N; i++) if (rawFetched[i]) total += (long long) rawChildrenStore[i].size();
        childIds.clear(); childIds.reserve((size_t) total);
        for (int i = 0; i < N; i++) {
            ns[i].childStart = (int) childIds.size();
            if (rawFetched[i]) { for (int c : rawChildrenStore[i]) childIds.push_back(c); ns[i].childCount = (int) rawChildrenStore[i].size(); }
            else ns[i].childCount = 0;
        }
        flatGraphBuilt = true;
    }
#ifdef WITH_CUDA
    // Deferred flood setup for the lazy path: materialize the flat graph, resize the node-sized flood buffers
    // to the (now larger) node count, upload the resident GPU graph, and init the flood. One-shot after iter-1.
    bool setupFloodGpuNow() {
        auto _t0 = std::chrono::steady_clock::now();
        materializeFlatGraphFromLazy();
        shareMark.assign((size_t) numNodes(), 0); floodMark = 1;
        if (floodLive) { dirtyStamp.assign((size_t) numNodes(), 0); resetDirtyLocal(); }
        bool ok = numNodes() > 0 && gpuUploadGraph() && gpuFloodInit(floodMaxPath, floodLaneCnt) == 0;
        double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count();
        if (ok) { floodReady = true;
            std::fprintf(stderr, "[gpu-flood] lazy materialize+upload OK N=%d E=%zu in %.2fs -> hybrid ON\n",
                         numNodes(), childIds.size(), s); }
        else std::fprintf(stderr, "[gpu-flood] lazy materialize/upload FAILED (%.2fs) -> pure CPU\n", s);
        return ok;
    }
#endif

    // ---- GPU detailed routing, Stage G2.2: negotiated-congestion loop (hybrid) --------------------
    // Each iteration the GPU routes the batch of connections that need (re)routing; the CPU keeps the
    // EXACT occupancy (rip-up/increment via the existing machinery), folds present+historical congestion
    // into the per-node cost it uploads, and finishes on the CPU any connection the GPU could not place
    // (cap-exceeded / no path / has alt sinks). Converges when nothing is overused; because the CPU owns
    // occupancy and finishes the tail with the full router, the final routing is always CPU-legal.
    // Refresh the GPU-resident per-node congestion multiplier from the CURRENT CPU occupancy (hist*present).
    // Called at the start of each flooding iteration => the flood sees start-of-iteration prices (hist is
    // fixed per iteration; present freezes at iter start). Occupancy itself is always kept EXACT on the CPU.
    // fillT: fill-loop thread count. The ITERATION-BOUNDARY caller passes parPart (workers idle there,
    // so the parallel fill stays inside the 32-thread budget); the mid-route oversize-dirty caller
    // (maybeRefreshBeforeLane) must pass 1 -- the 32 workers are still routing then, and extra fill
    // threads would break the <=32-threads-total invariant.
    void refreshFloodCost(int fillT = 1) {
        int N = numNodes();
        if ((int) floodCong.size() != N) floodCong.assign((size_t) N, 1.0f);
        if ((int) floodCongShare.size() != N) floodCongShare.assign((size_t) N, 1.0f);
        // Fill in parallel: pure per-i computation into disjoint ranges = byte-identical to the
        // serial loop. This runs at EVERY flooding iteration boundary (20per: 51 iterations over a
        // 103M-node closure -> the serial fill alone was ~0.2-0.3s/iter of the ~0.4s boundary gap).
        // (A "defer the refresh to the first flood of the iteration" variant would skip tail
        // iterations entirely but is NOT bit-exact: the present-cost table is rebuilt after this
        // point, and leaf-completion publishes would be overwritten by a later refresh -- keep the
        // boundary timing.)
        const int T = std::max(1, fillT);
        auto fill = [&](size_t lo, size_t hi) {
            for (size_t i = lo; i < hi; i++) {
                if (!created[i]) { floodCong[i] = 1.0f; floodCongShare[i] = 1.0f; continue; }
                int occ = getOccupancy((int) i); int oc = occ > 255 ? 255 : occ;
                int ocs = occ - 1; if (ocs < 0) ocs = 0; if (ocs > 255) ocs = 255;
                float h = dyn[i].hist;
                floodCong[i]      = h * presentCongestionCosts[oc];    // no-share: present(occ)
                floodCongShare[i] = h * presentCongestionCosts[ocs];   // same-net share: present(occ-1)
            }
        };
        if (T > 1 && N > (1 << 20)) parForN((size_t) N, T, [&](int, size_t lo, size_t hi) { fill(lo, hi); });
        else                        fill(0, (size_t) N);
        gpuRouteUpdateCost(floodCong.data());
        gpuFloodUpdateCostShare(floodCongShare.data());
    }

    // Gather this net's OTHER connections' used nodes (with per-net use count) so the flood applies the exact
    // sharing discount (sharingFactor = 1 + countSourceUses). Call AFTER ripUp(c) so c's own nodes are excluded.
    // Returns the count m; fills laneShareNodes/laneShareCounts[lane][0..m).
    int gatherShareSet(int idx, int lane) {   // fills THIS LANE's host staging; shareMark under shareMu
        std::lock_guard<std::mutex> sg(shareMu);
        Connection& c = connections[idx]; int ni = c.netIdx; int m = 0; int mk = floodMark++;
        if (ni >= (int) netConns.size()) return 0;
        std::vector<int>& snb = laneShareNodes[lane];
        std::vector<int>& scb = laneShareCounts[lane];
        for (int cc : netConns[ni]) {
            if (cc == idx) continue;
            Connection& oc = connections[cc];
            if (!oc.routed) continue;
            for (int nd : oc.rnodes) {
                if (nd < 0 || nd >= (int) shareMark.size() || shareMark[nd] == mk) continue;
                shareMark[nd] = mk;
                int cnt = countConnectionsOfUser(nd, ni);
                if (cnt > 0 && m < SHARE_CAP_H) { snb[m] = nd; scb[m] = cnt; m++; }
            }
        }
        return m;
    }

    // Route ONE expensive connection via the GPU flood (zero-staleness: rip up on CPU, flood against the
    // current price snapshot, commit the path on the CPU immediately with exact occupancy). Falls back to
    // the CPU A* if the flood does not return a legal source-anchored path to a valid sink.
    // Live-price flush: push the congestion of every node whose occupancy changed since the last flush,
    // so the next flood sees LIVE prices (not start-of-iteration frozen). ~one batched scatter per flood.
    // Oversize dirty list -> full refresh needs ALL lanes idle; call BEFORE acquiring a lane (deadlock-free:
    // refresh holders own no lane, lane holders never wait on refreshMu).
    void maybeRefreshBeforeLane() {
        if ((int) tl_dirtyList.size() <= SHARE_CAP_H) return;
        std::lock_guard<std::mutex> rg(refreshMu);
        waitAllLanesFreeAnd([&] { refreshFloodCost(); });
        resetDirtyLocal();
    }

    void flushDirtyToGpu(int lane) {   // flushes THIS thread's dirty nodes on the given lane's stream
        if (tl_dirtyList.empty()) return;
        int m = (int) tl_dirtyList.size(); if (m > SHARE_CAP_H) m = SHARE_CAP_H;  // pre-lane refresh keeps us under cap
        tl_dscA.clear(); tl_dscB.clear();
        for (int id : tl_dirtyList) {
            int occ = getOccupancy(id); int oc = occ > 255 ? 255 : occ; int ocs = occ - 1; if (ocs < 0) ocs = 0; if (ocs > 255) ocs = 255;
            float h = dyn[id].hist;
            tl_dscA.push_back(h * presentCongestionCosts[oc]);
            tl_dscB.push_back(h * presentCongestionCosts[ocs]);
        }
        gpuFloodScatterCong(lane, tl_dirtyList.data(), tl_dscA.data(), tl_dscB.data(), m);
        resetDirtyLocal();
    }

    // Flood one already-ripped connection on the given lane; commit obeys tl_deferCommit.
    bool gpuFloodTryLane(int idx, int lane) {
        Connection& c = connections[idx];
        int m = gatherShareSet(idx, lane);            // this net's shareable nodes (exact sharing discount)
        NetWrapper& nw = nets[c.netIdx];
        int tgt[64]; int K = 0;
        if (c.sinkRnode >= 0) tgt[K++] = c.sinkRnode;
        for (int a : c.altSinks) { if (K >= 64) break; if (a >= 0) tgt[K++] = a; }
        std::vector<int>& pathBuf = laneFloodPath[lane];
        if ((int) pathBuf.size() < floodMaxPath) pathBuf.assign((size_t) floodMaxPath, 0);
        int reached = 0, plen = 0; float gc = -1; double kms = 0;
        int rc = gpuFloodConnection(lane, c.sourceRnode, tgt, K, c.xMinBB, c.xMaxBB, c.yMinBB, c.yMaxBB,
                                    floodLenW, floodMaxSteps, nw.xCenter, nw.yCenter, nw.connectionsSize,
                                    nw.doubleHpwl, laneShareNodes[lane].data(), laneShareCounts[lane].data(), m,
                                    &reached, &gc, &plen, pathBuf.data(), &kms);
        if (kms > 10.0)   // a healthy flood is ~2-3ms; sustained slowness means a sick device graph
            std::fprintf(stderr, "[flood-slow] conn=%d iter=%d kms=%.1f rc=%d reached=%d plen=%d\n",
                         c.connId, routeIteration, kms, rc, reached, plen);
        {   // live flood counter: FLOOD totals only print at iteration end
            long long fc = floodedCount.load(std::memory_order_relaxed) + floodFallback.load(std::memory_order_relaxed);
            if ((fc & 1023) == 1023)
                std::fprintf(stderr, "[flood-live] iter=%d floods=%lld\n", routeIteration, fc);
        }
        if (rc == 0 && reached && plen > 0 && plen <= floodMaxPath &&
            pathBuf[plen - 1] == c.sourceRnode && isValidSink(c, pathBuf[0])) {
            c.rnodes.assign(pathBuf.begin(), pathBuf.begin() + plen);   // [sink..source], matches saveRouting
            c.routed = true;
            if (!tl_deferCommit) updateUsersAndPresentCongestionCost(c);   // CPU: commit exact occupancy
            floodedCount++;
            return true;
        }
        return false;
    }

    long floodBboxCap = rwEnvI("RW_FLOOD_BBOX_CAP", 40000);   // bbox AREA cap (tiles^2)
    long floodSpanCap = rwEnvI("RW_FLOOD_SPAN_CAP", 400);     // bbox W+H cap: flood cost ~ wavefront STEPS
                                                       // (x full-N fills). THEIA_50per's thin device-tall
                                                       // conns (20x900 box, plen 330) passed the area cap
                                                       // yet took 6-11 SECONDS per flood vs ~50ms CPU.
    void gpuFloodRoute(int idx) {
        Connection& c = connections[idx];
        long bw = c.xMaxBB - c.xMinBB, bh = c.yMaxBB - c.yMinBB;
        if ((floodBboxCap > 0 && bw * bh > floodBboxCap) ||
            (floodSpanCap > 0 && bw + bh > floodSpanCap)) {
            ripUp(c);
            c.rnodes.clear(); c.routed = false;
            routeIndirectConnection(idx);             // giant-bbox conn: unbudgeted CPU beats a giant flood
            floodFallback++;
            return;
        }
        // Multi-lane: rip-up/commit are own-territory CPU work (no lock); the GPU part runs on an
        // acquired lane (own device scratch + stream) so up to floodLaneCnt floods overlap. Only
        // gatherShareSet takes the small shared shareMu. CPU fallback runs with no lane held.
        ripUp(c);                                     // CPU: release the connection's current path (exact occupancy)
        maybeRefreshBeforeLane();                     // oversize dirty -> full refresh (needs all lanes idle)
        int lane = acquireLane();
        if (floodLive) flushDirtyToGpu(lane);         // push live prices (incl. this rip) so the flood is not stale
        bool ok = gpuFloodTryLane(idx, lane);
        releaseLane(lane);
        if (!ok) {   // CPU fallback: unbudgeted A* -- must not serialize other workers' floods behind it
            std::fprintf(stderr, "[flood-fallback] conn=%d iter=%d wid=%d\n", c.connId, routeIteration, tl_wid);
            c.rnodes.clear(); c.routed = false;           // (ripUp above already released the old path)
            routeIndirectConnection(idx);
            floodFallback++;
        }
    }

    // §hedge dispatch: run the CPU A* and (once it proves not-cheap at floodHedgePoint) a concurrent GPU flood;
    // whichever reaches a sink first wins, committed sequentially with exact occupancy (zero staleness). Cheap
    // connections finish on CPU before the hedge point (no flood -> no over-flooding); expensive ones let the
    // flood win (no sequential probe-then-flood). Same price snapshot for both. Falls back to unroutable pass.
    void routeConnectionHedge(int idx) {
        Connection& c = connections[idx];
        ripUp(c);                                        // release current path (occ); exclude self from share gather
        maybeRefreshBeforeLane();
        int hlane = acquireLane();                       // serial-mode hedge: never contended, but keep the pool honest
        int m = gatherShareSet(idx, hlane);
        if (floodLive) flushDirtyToGpu(hlane);
        NetWrapper& nw = nets[c.netIdx];
        int tgt[64]; int K = 0; if (c.sinkRnode >= 0) tgt[K++] = c.sinkRnode;
        for (int a : c.altSinks) { if (K >= 64) break; if (a >= 0) tgt[K++] = a; }
        std::vector<int>& pathBuf = laneFloodPath[hlane];
        if ((int) pathBuf.size() < floodMaxPath) pathBuf.assign((size_t) floodMaxPath, 0);

        DaryPQ queue(*tl_pq, heapArity);
        State st; st.queue = &queue; st.connIdx = idx; st.sequence = (int)(++tl_seq);
        st.shareWeight = std::pow(1.0f, cfg.shareExponent); st.rnodeWLWeight = 1.0f * (1.0f - wlWeight);
        st.estWlWeight = 1.0f * wlWeight * directedness; st.earlyTermination = false;
        if (tl_wid >= 64 && batchDirect > 1.0f) st.estWlWeight *= batchDirect;   // crew searches only
        fillLmkT(st, c.sinkRnode);
        setAllTargets(c, st);
        push(st, c.sourceRnode, 0.0f, 0.0f, false);

        hedgeFloodDone.store(0); hedgeReached = 0; hedgePlen = 0;
        std::thread* ft = nullptr;
        bool cpuFound = false, floodWon = false; int rnode = -1; long long pops = 0;
        auto floodValid = [&]() { return hedgeReached && hedgePlen > 0 && hedgePlen <= floodMaxPath &&
                                         pathBuf[hedgePlen - 1] == c.sourceRnode && isValidSink(c, pathBuf[0]); };
        while (!queue.empty()) {
            rnode = queue.poll(); pops++;
            if (TLD(rnode).target) { cpuFound = true; break; }
            if (!ft && pops >= floodHedgePoint) {        // proven not-cheap -> launch concurrent flood
                ft = new std::thread([&, hlane]() {
                    gpuFloodConnection(hlane, c.sourceRnode, tgt, K, c.xMinBB, c.xMaxBB, c.yMinBB, c.yMaxBB,
                                       floodLenW, floodMaxSteps, nw.xCenter, nw.yCenter, nw.connectionsSize,
                                       nw.doubleHpwl, laneShareNodes[hlane].data(), laneShareCounts[hlane].data(), m,
                                       &hedgeReached, &hedgeCost, &hedgePlen, laneFloodPath[hlane].data(), &hedgeKms);
                    hedgeFloodDone.store(1);
                });
            }
            if (ft && hedgeFloodDone.load()) { if (floodValid()) { floodWon = true; break; } }   // flood beat CPU
            exploreAndExpand(st, rnode);
        }
        if (ft) { ft->join(); delete ft; }               // flood done -> GPU buffers free for the next connection
        releaseLane(hlane);
        if (!cpuFound && !floodWon && floodValid()) floodWon = true;   // CPU drained/stopped; flood has a valid path

        if (cpuFound) { queue.clear(); finishRouteConnection(c, rnode); }
        else if (floodWon) { c.rnodes.assign(pathBuf.begin(), pathBuf.begin() + hedgePlen);
                             c.routed = true; updateUsersAndPresentCongestionCost(c); floodedCount++; }
        else { c.rnodes.clear(); c.routed = false; }     // neither reached -> unroutable pass handles it
        for (int t : st.targets) TLD(t).target = 0; st.targets.clear();
        if (idx < (int) connLastPops.size()) connLastPops[idx] = pops;
    }

    // §GPU-flood kernel prototype (shadow mode). At a congested iteration, freeze the price snapshot and,
    // for a sample of connections, time the CPU A* (save/restore path => occupancy-neutral) vs a single-
    // connection GPU flood on the SAME prices; report per-band gross G (cpu/kernel), net (cpu/wall), path
    // legality. No routing loop mutation. Cost is approximate (baseCost*cong + lenW*length; no sharing/bias)
    // so this measures the TIMING (G, S) gate, not commit fidelity.
    void floodProto() {
        std::fprintf(stderr, "[gpu-flood] prototype: uploading resident graph + price snapshot (iter %d)\n", routeIteration);
        if (!gpuUploadGraph()) { std::fprintf(stderr, "[gpu-flood] upload failed\n"); std::exit(1); }
        int N = numNodes();
        std::vector<float> cong((size_t) N, 1.0f);
        for (int i = 0; i < N; i++) { if (!created[i]) continue; int occ = getOccupancy(i); if (occ > 255) occ = 255;
            cong[i] = dyn[i].hist * presentCongestionCosts[occ]; }
        gpuRouteUpdateCost(cong.data());
        const int maxPathLen = 8192, maxSteps = 4000;
        if (gpuFloodInit(maxPathLen, 1) != 0) { std::fprintf(stderr, "[gpu-flood] flood init failed\n"); std::exit(1); }
        float lenW = 1.0f * (1.0f - wlWeight);

        // sample = the actual iter-6 monsters/band (recorded by measured pops during routeIndirectConnections)
        // + a spread of smaller routed connections for <16k context.
        std::vector<int> sample = bigConnsThisIter;
        std::fprintf(stderr, "[gpu-flood] recorded %zu connections with pops>=16k this iter\n", bigConnsThisIter.size());
        int added = 0;
        int stepc = std::max(1, (int) sortedIndirect.size() / 150);
        for (int i = 0; i < (int) sortedIndirect.size() && added < 150; i += stepc) {
            Connection& c = connections[sortedIndirect[i]];
            if (c.abandoned || !c.routed || c.rnodes.empty()) continue;
            sample.push_back(sortedIndirect[i]); added++;
        }

        double sCpu[3] = {0}, sKer[3] = {0}, sWall[3] = {0}; long n[3] = {0}, reachMatch[3] = {0}, badPath[3] = {0};
        double maxG[3] = {0};
        std::vector<int> path(maxPathLen); int tgtBuf[64];
        bool warmed = false;
        for (int idx : sample) {
            Connection& c = connections[idx];
            std::vector<int> oldPath = c.rnodes; bool oldRouted = c.routed;
            auto t0 = std::chrono::steady_clock::now();
            routeIndirectConnection(idx);
            double tCpu = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
            long long pops = lastPops; bool cpuReached = c.routed;
            ripUp(c); c.rnodes = oldPath; c.routed = oldRouted;
            if (!c.rnodes.empty()) updateUsersAndPresentCongestionCost(c);

            int K = 0; if (c.sinkRnode >= 0) tgtBuf[K++] = c.sinkRnode;
            for (int a : c.altSinks) { if (K >= 64) break; if (a >= 0) tgtBuf[K++] = a; }
            int reached = 0, plen = 0; float gcost = -1; double kms = 0;
            NetWrapper& nwp = nets[c.netIdx];
            if (!warmed) {   // discard first flood (CUDA JIT / context warmup)
                gpuFloodConnection(0, c.sourceRnode, tgtBuf, K, c.xMinBB, c.xMaxBB, c.yMinBB, c.yMaxBB, lenW, maxSteps,
                                   nwp.xCenter, nwp.yCenter, nwp.connectionsSize, nwp.doubleHpwl, nullptr, nullptr, 0,
                                   &reached, &gcost, &plen, path.data(), &kms); warmed = true;
            }
            auto w0 = std::chrono::steady_clock::now();
            gpuFloodConnection(0, c.sourceRnode, tgtBuf, K, c.xMinBB, c.xMaxBB, c.yMinBB, c.yMaxBB, lenW, maxSteps,
                               nwp.xCenter, nwp.yCenter, nwp.connectionsSize, nwp.doubleHpwl, nullptr, nullptr, 0,
                               &reached, &gcost, &plen, path.data(), &kms);
            double tWall = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - w0).count();
            bool bad = false;
            if (reached) {
                if (plen < 1 || path[std::min(plen, maxPathLen) - 1] != c.sourceRnode) bad = true;
                else { bool ok = false; for (int j = 0; j < K; j++) if (path[0] == tgtBuf[j]) ok = true; if (!ok) bad = true; }
            }
            int b = pops < 16384 ? 0 : pops < 65536 ? 1 : 2;
            n[b]++; sCpu[b] += tCpu; sKer[b] += kms; sWall[b] += tWall;
            if (kms > 1e-6 && tCpu / kms > maxG[b]) maxG[b] = tCpu / kms;
            if ((reached != 0) == cpuReached) reachMatch[b]++;
            if (bad) badPath[b]++;
        }
        std::fprintf(stderr, "FLOODPROTO iter=%d pf=%.1f samples=%zu lenW=%.3f\n",
                     routeIteration, presentCongestionFactor, sample.size(), lenW);
        const char* nm[3] = {"<16k", "16-65k", ">65k"};
        for (int b = 0; b < 3; b++) { if (!n[b]) continue;
            std::fprintf(stderr, "  band %-7s n=%ld  CPU=%.2fms  GPUkernel=%.2fms  GPUwall=%.2fms  "
                                 "Ggross=%.1fx  Gnet=%.1fx  maxGgross=%.1fx  reachMatch=%ld/%ld  badPath=%ld\n",
                         nm[b], n[b], sCpu[b] / n[b], sKer[b] / n[b], sWall[b] / n[b],
                         sKer[b] > 0 ? sCpu[b] / sKer[b] : 0.0, sWall[b] > 0 ? sCpu[b] / sWall[b] : 0.0,
                         maxG[b], reachMatch[b], n[b], badPath[b]);
        }
        gpuFloodFree();
        std::exit(0);
    }

    void routeGpuLoop() {
        if (!gpuUploadGraph()) { std::fprintf(stderr, "[gpu-route] upload failed; using CPU loop\n"); routeCpuLoop(); return; }
        routeIteration = 1;
        historicalCongestionFactor = cfg.historicalCongestionFactor;
        presentCongestionFactor = cfg.initialPresentCongestionFactor;
        wlWeight = cfg.wirelengthWeight;
        int   cap        = std::max(16, rwEnvI("RW_GPU_CAP", 4096));
        float directed   = rwEnvF("RW_GPU_DIRECT", 2.0f);
        float lenW       = rwEnvF("RW_GPU_LENW", 1.0f - cfg.wirelengthWeight);
        float liveFac    = rwEnvF("RW_GPU_LIVEFAC", 1.0f);   // within-batch live occupancy spreading (anti-pileup)
        int   maxPathLen = std::max(8, rwEnvI("RW_GPU_MAXPATH", 1024));
        int   minBatch   = std::max(1, rwEnvI("RW_GPU_MINBATCH", 512));   // below this -> CPU sequential endgame
        int   K          = std::max(1, rwEnvI("RW_GPU_K", 8));            // max targets/conn (primary + alt sinks)
        int   overGate   = rwEnvI("RW_GPU_OVERGATE", 5000);              // overused below this -> CPU sequential tail
        bool  iter1Only  = rwEnvI("RW_GPU_ITER1ONLY", 0) != 0;           // measurement: GPU does ONLY iter-1, then pure CPU
        long  lastOverused = (long) 4e9;                                 // GRoute Phase1->Phase2: GPU while overuse high
        int N = numNodes();
        std::vector<float> congCost((size_t) N, 1.0f);
        long long gpuRouted = 0, cpuFallback = 0;

        while (routeIteration < cfg.maxIterations) {
            auto _it0 = std::chrono::steady_clock::now();
            updatePresentCongestionCosts(presentCongestionFactor);

            // GPU routes ALL connections needing (re)routing, with multi-target (primary + alt sinks) so
            // lutPinSwapping connections spread across their sink choices + within-batch live occupancy so
            // they avoid piling on the same nodes. (Both validated to cut iter-1 overuse ~48%.)
            std::vector<int> gpuBatch, cpuBatch;
            for (int idx : sortedIndirect) {
                Connection& c = connections[idx];
                if (c.abandoned || !shouldRoute(c)) continue;
                gpuBatch.push_back(idx);
            }
            // Phase transition (GRoute Phase1 -> Phase2): the GPU's batched/stale routing clears the bulk
            // fast but OSCILLATES on the last few overused nodes; once the GPU batch is small, route it on
            // the CPU sequentially (deterministic) so the endgame converges.
            int B = (int) gpuBatch.size();
            bool useGpu = (lastOverused > (long) overGate) && (B >= minBatch);   // GPU for the high-overuse bulk only
            if (iter1Only) useGpu = (routeIteration == 1);   // isolate GPU iter-1 net benefit: GPU iter-1, CPU tail
            double _gk = 0.0; int nCpu = (int) cpuBatch.size();
            if (useGpu) {
                for (int idx : gpuBatch) { ripUp(connections[idx]); connections[idx].rnodes.clear(); connections[idx].routed = false; }
                for (int i = 0; i < N; i++) { int occ = occCnt[i]; if (occ > 255) occ = 255;
                    congCost[i] = dyn[i].hist * presentCongestionCosts[occ]; }
                gpuRouteUpdateCost(congCost.data());
                std::vector<int> src(B);
                std::vector<short> bb((size_t) B * 4);
                std::vector<int> tgt((size_t) B * K, -1);
                std::vector<short> tgtX((size_t) B * K, 0), tgtY((size_t) B * K, 0);
                for (int i = 0; i < B; i++) { Connection& c = connections[gpuBatch[i]];
                    src[i] = c.sourceRnode;
                    bb[4*i]=c.xMinBB; bb[4*i+1]=c.xMaxBB; bb[4*i+2]=c.yMinBB; bb[4*i+3]=c.yMaxBB;
                    size_t bz = (size_t) i * K; int jj = 0;
                    if (c.sinkRnode >= 0) { tgt[bz]=c.sinkRnode; tgtX[bz]=ns[c.sinkRnode].beginX; tgtY[bz]=ns[c.sinkRnode].beginY; jj=1; }
                    for (int a : c.altSinks) { if (jj>=K) break; if (a<0) continue; tgt[bz+jj]=a; tgtX[bz+jj]=ns[a].beginX; tgtY[bz+jj]=ns[a].beginY; jj++; } }
                std::vector<int> reached(B), labels(B), plen(B), path((size_t) B * maxPathLen);
                auto _g0 = std::chrono::steady_clock::now();
                gpuRouteForward(B, src.data(), tgt.data(), tgtX.data(), tgtY.data(), K, bb.data(), cap, directed,
                                lenW, liveFac, maxPathLen, reached.data(), labels.data(), plen.data(), path.data());
                _gk = std::chrono::duration<double>(std::chrono::steady_clock::now() - _g0).count();
                for (int i = 0; i < B; i++) {
                    int idx = gpuBatch[i]; Connection& c = connections[idx];
                    if (reached[i] && plen[i] > 0) {
                        const int* p = &path[(size_t) i * maxPathLen];
                        c.rnodes.assign(p, p + plen[i]); c.routed = true;
                        updateUsersAndPresentCongestionCost(c); gpuRouted++;
                    } else { routeIndirectConnection(idx); cpuFallback++; nCpu++; }   // ripUp no-op (rnodes cleared)
                }
            } else {
                for (int idx : gpuBatch) { routeIndirectConnection(idx); cpuFallback++; }   // endgame: CPU sequential
                nCpu += B; B = 0;
            }
            for (int idx : cpuBatch) routeIndirectConnection(idx);

            updateCostFactors();
            lastOverused = (long) overUsedList.size();   // drives the GPU(bulk) -> CPU(tail) transition next iter
            std::vector<int> unroutable;
            for (int idx : sortedIndirect) { Connection& c = connections[idx];
                if (!c.routed && !c.abandoned) unroutable.push_back(idx); }
            for (int idx : unroutable) handleUnroutableConnection(idx);

            double _itw = std::chrono::duration<double>(std::chrono::steady_clock::now() - _it0).count();
            std::printf("%4d   overused=%d  totalOveruse=%lld  unroutable=%d  gpu=%d  cpu=%d  gpuKernel=%.2fs  wall=%.2fs\n",
                        routeIteration, (int) overUsedList.size(), currentTotalOveruse, (int) unroutable.size(),
                        B, nCpu, _gk, _itw);
            std::fflush(stdout);
            if (overUsedList.empty() && unroutable.empty()) break;
            routeIteration++;
        }
        std::fprintf(stderr, "GPU_ROUTE_SUMMARY iters=%d overused=%d gpuRouted=%lld cpuFallback=%lld\n",
                     routeIteration, (int) overUsedList.size(), gpuRouted, cpuFallback);
        gpuRouteShutdown();
    }

    // ---- GPU detailed routing, Stage G0/G1/G2.1 experiment -----------------------------------------
    // Upload the eager RRG to the device and verify the resident graph against the CPU. Builds the CSR
    // (adjOff from ns[].childStart + a childIds size sentinel) and per-node end-tile coords, runs the
    // GPU per-connection "children-strictly-in-bbox" kernel, and cross-checks EVERY connection against
    // the identical CPU computation. This proves graph upload + CSR indexing + coord/bbox round-trip
    // before the frontier-routing kernel (G1) lands. Eager-only (lazy/JNI has no flat childIds).
    void gpuRouteExperiment() {
        if (lazy) { std::fprintf(stderr, "[gpu-route] needs the eager graph (skipped in lazy mode)\n"); return; }
        if (!gpuRouteAvailable()) { std::fprintf(stderr, "[gpu-route] no CUDA device available\n"); return; }
        int N = numNodes();
        long E = (long) childIds.size();
        std::vector<int> adjOff((size_t) N + 1);
        for (int i = 0; i < N; i++) adjOff[i] = ns[i].childStart;
        adjOff[N] = (int) E;
        std::vector<short> endX(N), endY(N), length(N);
        std::vector<float> baseCost(N);
        std::vector<unsigned char> blocked(N);
        for (int i = 0; i < N; i++) {
            endX[i] = ns[i].endX; endY[i] = ns[i].endY; length[i] = ns[i].length; baseCost[i] = ns[i].baseCost;
            // 1 = hard-blocked (preserved / inaccessible); 2 = exclusive-sink (usable only as the target)
            if (ns[i].preserved || type[i] == RouteNodeType::INACCESSIBLE) blocked[i] = 1;
            else if (isAnyExclusiveSink(type[i])) blocked[i] = 2;
            else blocked[i] = 0;
        }

        int M = (int) indirectAll.size();
        int K = std::max(1, rwEnvI("RW_GPU_K", 8));   // max targets/conn (primary sink + alt sinks)
        std::vector<int> srcNode(M), sinkNode(M);
        std::vector<short> bbox4((size_t) M * 4);
        std::vector<int> tgt((size_t) M * K, -1);
        std::vector<short> tgtX((size_t) M * K, 0), tgtY((size_t) M * K, 0);
        for (int i = 0; i < M; i++) {
            const Connection& c = connections[indirectAll[i]];
            srcNode[i] = c.sourceRnode; sinkNode[i] = c.sinkRnode;
            bbox4[4*i] = c.xMinBB; bbox4[4*i+1] = c.xMaxBB; bbox4[4*i+2] = c.yMinBB; bbox4[4*i+3] = c.yMaxBB;
            size_t b = (size_t) i * K; int j = 0;
            if (c.sinkRnode >= 0) { tgt[b] = c.sinkRnode; tgtX[b] = ns[c.sinkRnode].beginX; tgtY[b] = ns[c.sinkRnode].beginY; j = 1; }
            for (int a : c.altSinks) { if (j >= K) break; if (a < 0) continue;
                tgt[b + j] = a; tgtX[b + j] = ns[a].beginX; tgtY[b + j] = ns[a].beginY; j++; }
        }
        auto isTgtHost = [&](int i, int node) { for (int j = 0; j < K; j++) { int t = tgt[(size_t) i * K + j];
            if (t < 0) return false; if (t == node) return true; } return false; };

        auto t0 = std::chrono::steady_clock::now();
        if (gpuRouteInit(N, E, adjOff.data(), childIds.data(), endX.data(), endY.data(),
                         baseCost.data(), length.data(), blocked.data()) != 0) {
            std::fprintf(stderr, "[gpu-route] gpuRouteInit failed\n"); return;
        }
        double tup = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();

        // --- G0: verify the resident graph against the CPU (children strictly in bbox) ---
        std::vector<int> gpuOut(M, -2);
        auto t1 = std::chrono::steady_clock::now();
        if (gpuRouteVerifyBboxChildren(M, srcNode.data(), bbox4.data(), gpuOut.data()) != 0) {
            std::fprintf(stderr, "[gpu-route] verify kernel failed\n"); gpuRouteShutdown(); return; }
        double tvk = std::chrono::duration<double>(std::chrono::steady_clock::now() - t1).count();
        long mism = 0;
        for (int i = 0; i < M; i++) {
            int src = srcNode[i], cnt = -1;
            if (src >= 0) {
                int xMin = bbox4[4*i], xMax = bbox4[4*i+1], yMin = bbox4[4*i+2], yMax = bbox4[4*i+3];
                int s = ns[src].childStart, e = s + ns[src].childCount; cnt = 0;
                for (int k = s; k < e; k++) { int ch = childIds[k];
                    int ex = ns[ch].endX, ey = ns[ch].endY;
                    if (ex > xMin && ex < xMax && ey > yMin && ey < yMax) cnt++; }
            }
            if (gpuOut[i] != cnt) mism++;
        }
        std::fprintf(stderr, "[gpu-route] G0: nodes=%d edges=%ld conns=%d upload=%.3fs verifyKernel=%.3fs mismatches=%ld%s\n",
                     N, E, M, tup, tvk, mism, mism == 0 ? "  (MATCH)" : "  (!! MISMATCH)");

        // --- G1: bounded forward shortest-path within bbox -> sink-reach coverage gate ---
        int cap = std::max(16, rwEnvI("RW_GPU_CAP", 4096));
        float directedness = rwEnvF("RW_GPU_DIRECT", 2.0f);
        float lenW = rwEnvF("RW_GPU_LENW", 1.0f - cfg.wirelengthWeight);
        float liveFac = rwEnvF("RW_GPU_LIVEFAC", 1.0f);
        int maxPathLen = std::max(8, rwEnvI("RW_GPU_MAXPATH", 1024));
        std::vector<int> reached(M, 0), labels(M, 0), pathLen(M, 0);
        std::vector<int> path((size_t) M * maxPathLen);

        // Apply all reached GPU routes to the EXACT CPU occupancy, count overused (distinct nets), restore.
        auto applyCountRestore = [&]() -> long {
            std::vector<int> applied;
            for (int i = 0; i < M; i++) {
                if (!reached[i] || pathLen[i] <= 0) continue;
                int idx = indirectAll[i]; Connection& c = connections[idx];
                c.rnodes.assign(&path[(size_t) i * maxPathLen], &path[(size_t) i * maxPathLen] + pathLen[i]);
                c.routed = true; updateUsersAndPresentCongestionCost(c); applied.push_back(idx);
            }
            long ov = 0; for (int id = 0; id < N; id++) if (occCnt[id] > CAPACITY) ov++;
            for (int idx : applied) { ripUp(connections[idx]); connections[idx].rnodes.clear(); connections[idx].routed = false; }
            return ov;
        };
        auto runForward = [&](float fac) -> double {
            auto t = std::chrono::steady_clock::now();
            gpuRouteForward(M, srcNode.data(), tgt.data(), tgtX.data(), tgtY.data(), K, bbox4.data(),
                            cap, directedness, lenW, fac, maxPathLen, reached.data(), labels.data(),
                            pathLen.data(), path.data());
            return std::chrono::duration<double>(std::chrono::steady_clock::now() - t).count();
        };

        // ---- FROZEN (presentFac=0): the stale-batch behavior. Validate path correctness + wirelength. ----
        double tFrozen = runForward(0.0f);
        long nReached = 0, nCap = 0, nInvalid = 0, nNoPath = 0, nBadPath = 0; long long totalWL = 0;
        for (int i = 0; i < M; i++) {
            if (labels[i] == -1) { nInvalid++; continue; }
            if (labels[i] == -2 || pathLen[i] == -2) { nCap++; continue; }
            if (!reached[i]) { nNoPath++; continue; }
            nReached++;
            int L = pathLen[i]; const int* p = &path[(size_t) i * maxPathLen];
            bool ok = (L >= 1 && isTgtHost(i, p[0]) && p[L - 1] == srcNode[i]); long wl = 0;
            for (int k = 0; ok && k < L; k++) {
                int node = p[k]; if (node < 0 || node >= N) { ok = false; break; } wl += ns[node].length;
                if (k + 1 < L) { int parent = p[k + 1], child = node; bool edge = false;
                    int s = ns[parent].childStart, e = s + ns[parent].childCount;
                    for (int t = s; t < e; t++) if (childIds[t] == child) { edge = true; break; }
                    if (!edge || blocked[child] == 1) ok = false;
                    if (blocked[child] == 2 && !isTgtHost(i, child)) ok = false; }
            }
            if (ok) totalWL += wl; else nBadPath++;
        }
        long frozenOv = applyCountRestore();
        std::fprintf(stderr, "[gpu-route] G2 FROZEN cap=%d direct=%.2f kernel=%.3fs routed=%ld (%.1f%%) capExceeded=%ld badPath=%ld WL=%lld overusedIfApplied=%ld\n",
                     cap, directedness, tFrozen, nReached, 100.0 * nReached / M, nCap, nBadPath, totalWL, frozenOv);

        // ---- LIVE (presentFac=liveFac): within-batch atomic occupancy spreading ----
        double tLive = runForward(liveFac);
        long lReached = 0; for (int i = 0; i < M; i++) if (reached[i] && pathLen[i] > 0) lReached++;
        long liveOv = applyCountRestore();
        std::fprintf(stderr, "[gpu-route] G2 LIVE  fac=%.2f kernel=%.3fs routed=%ld (%.1f%%) overusedIfApplied=%ld  (vs frozen %ld => %.1f%% fewer overused)\n",
                     liveFac, tLive, lReached, 100.0 * lReached / M, liveOv, frozenOv,
                     frozenOv > 0 ? 100.0 * (frozenOv - liveOv) / frozenOv : 0.0);
        gpuRouteShutdown();
    }
#endif

    void routeIndirectConnectionsIteratively() {
        auto _pr0 = std::chrono::steady_clock::now();
        sortConnections();
        std::fprintf(stderr, "[prolog] sortConnections=%.2fs\n",
                     std::chrono::duration<double>(std::chrono::steady_clock::now() - _pr0).count());
#ifdef WITH_CUDA
        if (rwEnvI("RW_GPU_ROUTE", 0) == 1) { gpuRouteExperiment(); return; }   // G0/G1/G2.1 experiment: verify + coverage, skip routing
#endif
        if (connections.size() > 3000000) {
            // Huge cases (THEIA_50per: 4.95M conns, 39 iterations at mult=2, iters 1-4 = 3624s):
            // ramp present-congestion faster so the heavy middle iterations collapse sooner.
            // Gated by size => jpeg/THEIA/k_800 keep their banked mult=2 behavior bit-identically.
            float m = rwEnvF("RW_PF_MULT", 0.0f);   // MEASURED NEGATIVE at 3.0: 50per 6264->6931s, wl +2.0% (steeper pf makes congested searches dearer); opt-in only
            if (m > 0 && cfg.presentCongestionMultiplier < m) {
                std::fprintf(stderr, "[cfg] huge case: presentCongestionMultiplier %.1f -> %.1f\n",
                             cfg.presentCongestionMultiplier, m);
                cfg.presentCongestionMultiplier = m;
            }
        }
        if (rwEnvI("RW_BBOX", 1)) tightenBoundingBoxesCoarse();   // Track D: coarse-grid bbox tighten (banked ON; RW_BBOX=0 disables; CPU solver -- the GPU corridor variant needs explicit RW_BBOX_GPU=1 and is NOT used)
        // Prepass materialization (lazy JNI + parallel + compact device): build the whole reachable
        // universe up front with spatially-sorted ids and the contiguous CSR (see lazyPrepassMaterialize).
        // Size gate: measured wins for jpeg-class (41M closure, route 51s), k_100-class (25M, route
        // 20.7s), THEIA-class (67M, within-noise favorable) AND k_800-class (2.07M conns, 69M closure:
        // iter-1 71 -> 11.9s, route 94 -> 46.8s). Truly larger cases (untested) stay lazy.
        if (flatGraphBuilt && earlyTotal >= 0) {       // prepass-early already built the CSR during Java init
            auto _pv0 = std::chrono::steady_clock::now();
            if (verifyEarlyCover()) {
                double _pvS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _pv0).count();
                patchLateSeeds(earlyTotal);            // seeds interned by loadLazy after the CSR build
                std::fprintf(stderr, "[prolog] verifyCover=%.2fs patchLateSeeds=%.2fs\n", _pvS,
                             std::chrono::duration<double>(std::chrono::steady_clock::now() - _pv0).count() - _pvS);
            } else {                                   // cover miss (rare): rebuild with the true conn cover
                lazy = true; flatGraphBuilt = false;
                lazyPrepassMaterialize();              // full rebuild covers every interned node -> no patch
            }
        } else if (parPart > 0 && lazy && fetchParSafe && !cfg.enlargeBoundingBox &&
            rwEnvI("RW_PAR_PREPASS", connections.size() < 3000000 ? 1 : 0))
            lazyPrepassMaterialize();
#ifdef WITH_CUDA
        if (rwEnvI("RW_GPU_ROUTE", 0) == 2) { routeGpuLoop(); return; }          // G2.2: GPU negotiated-congestion loop
#endif
        routeCpuLoop();
    }

    // §coarse-h capture test: an admissible priced coarse-h must take MIN node cost per tile. If hotspot
    // tiles have high within-tile price variance (min << typical), that admissible min is loose exactly
    // where steering matters, so a coarse-priced-h cannot capture the h-slack. Snapshot per-tile priced
    // cost = baseCost * hist * present(occ) at a congested iteration and report min-vs-typical spread.
    void dumpPriceVariance() {
        long N = numNodes();
        int maxX = 0, maxY = 0;
        for (long i = 0; i < N; i++) { if (!created[i]) continue;
            int x = getEndTileXCoordinate((int) i), y = getEndTileYCoordinate((int) i);
            if (x > maxX) maxX = x; if (y > maxY) maxY = y; }
        int W = maxX + 1; long T = (long) W * (maxY + 1);
        // full = baseCost*hist*present (total node cost); cong = hist*present (congestion multiplier only,
        // isolates the part a PRICED coarse field must add on top of a type-keyed static lookahead).
        std::vector<float> tmin(T, 1e30f), tmax(T, 0.0f), tsum(T, 0.0f);
        std::vector<float> cmin(T, 1e30f), csum(T, 0.0f); std::vector<int> cmax1(T, 0);  // cmax1: #nodes with cong>1
        std::vector<int> tcnt(T, 0), tover(T, 0);
        for (long i = 0; i < N; i++) { if (!created[i]) continue;
            int occ = getOccupancy((int) i); int occc = occ > 255 ? 255 : occ;
            float cong = dyn[i].hist * presentCongestionCosts[occc];
            float pc = ns[i].baseCost * cong;
            long t = (long) getEndTileYCoordinate((int) i) * W + getEndTileXCoordinate((int) i);
            if (pc < tmin[t]) tmin[t] = pc; if (pc > tmax[t]) tmax[t] = pc; tsum[t] += pc; tcnt[t]++;
            if (cong < cmin[t]) cmin[t] = cong; csum[t] += cong; if (cong > 1.0001f) cmax1[t]++;
            if (occ > CAPACITY) tover[t]++;
        }
        std::vector<double> mmHot, xmHot, cmHot; long nOcc = 0, nHot = 0, sumNodesHot = 0, sumOverHot = 0;
        for (long t = 0; t < T; t++) {
            if (tcnt[t] == 0 || tmin[t] <= 0) continue; nOcc++;
            double mean = tsum[t] / tcnt[t];
            if (tover[t] > 0) { nHot++; mmHot.push_back(mean / tmin[t]); xmHot.push_back(tmax[t] / tmin[t]);
                               cmHot.push_back((cmin[t] > 0) ? (csum[t] / tcnt[t]) / cmin[t] : -1.0);
                               sumNodesHot += tcnt[t]; sumOverHot += tover[t]; }
        }
        auto pct = [](std::vector<double> v, double p) { if (v.empty()) return -1.0;
            std::sort(v.begin(), v.end()); return v[(size_t)(p * (v.size() - 1))]; };
        std::fprintf(stderr, "PRICEVAR iter=%d pf=%.1f occupiedTiles=%ld hotspotTiles=%ld\n",
                     routeIteration, presentCongestionFactor, nOcc, nHot);
        std::fprintf(stderr, "  hotspot FULL(base*hist*pres) mean/min : p50=%.1f p90=%.1f p99=%.1f\n",
                     pct(mmHot, 0.5), pct(mmHot, 0.9), pct(mmHot, 0.99));
        std::fprintf(stderr, "  hotspot CONG(hist*pres)      mean/min : p50=%.1f p90=%.1f p99=%.1f  (priced coarse-h capture ceiling; 1.0=min carries no congestion signal)\n",
                     pct(cmHot, 0.5), pct(cmHot, 0.9), pct(cmHot, 0.99));
        std::fprintf(stderr, "  hotspot max/min(full) : p50=%.1f p90=%.1f p99=%.1f\n",
                     pct(xmHot, 0.5), pct(xmHot, 0.9), pct(xmHot, 0.99));
        std::fprintf(stderr, "  hotspot compose : avg nodes/tile=%.1f  avg overused/tile=%.2f  overused share=%.2f%%\n",
                     (double) sumNodesHot / std::max(1L, nHot), (double) sumOverHot / std::max(1L, nHot),
                     100.0 * sumOverHot / std::max(1L, sumNodesHot));
    }

    void routeCpuLoop() {
        routeIteration = 1;
        tl_dyn = dyn.data(); tl_pq = &pqStorage; tl_seq = 0;   // serial thread-local aliases (parallel iters set their own)
        if (parPart > 0 && lazy && !fetchParSafe) {   // JNI-callback device: one JNIEnv, not worker-callable
            parPart = 0;
            std::fprintf(stderr, "[par] DISABLED: lazy graph served by the JNI callback (need the compact device, RWDEV=1)\n");
        }
        if (parPart > 0 && cfg.enlargeBoundingBox) {  // runtime bbox growth breaks partition disjointness
            parPart = 0;
            std::fprintf(stderr, "[par] DISABLED: enlargeBoundingBox grows bboxes at runtime (partition tree would go stale)\n");
        }
        if (parPart > 0 && connections.size() >= 3500000 && !lazy && flatGraphBuilt) {
            // Huge-case bank (THEIA_50per campaign, 2026-07-11, E-N config): the RPTT cut-straddler
            // giants (1.06M + 632k conns, whole-device bboxes) serialize every iteration -- route them
            // with the deterministic batch-snapshot crew (rollback + bounce + same-net exemption +
            // position bands + paged labels + 4M-pop budget + serial endgame below 128 overused).
            // Verified: 57 iters, overused=0, VERIFY green, wl +5.2%. Explicit env always wins.
            auto bankI = [](const char* env, auto& slot, auto v) { if (!std::getenv(env)) slot = v; };
            bankI("RW_PAR_PART", parPart, 8);
            bankI("RW_BATCH_T", batchT, 24);
            bankI("RW_BATCH_MIN", batchMin, 50000);
            bankI("RW_BATCH_B", batchB, 512);
            bankI("RW_BATCH_ITER_MIN", batchIterMin, 1);
            bankI("RW_BATCH_SPARSE", batchSparse, 1);
            bankI("RW_BATCH_BUDGET", batchBudget, (long long) 4194304);
            setenv("RW_BATCH_NMIN", "4", 0);             // read per leaf call; 0 = no overwrite
            bankI("RW_CORRIDOR", corridorM, 16);         // E-S: giant-subset reroute pops -18%, total pushes
                                                         // 4.19B -> 2.98B compounded, 56-iter converge, legal
            std::fprintf(stderr, "[bank] huge-case batch crew: T=%d MIN=%d B=%d budget=%lld\n",
                         batchT, batchMin, batchB, batchBudget);
        }
        if (parPart > 0) {
            std::fprintf(stderr, "[par] RPTT partition-parallel ON: T=%d overlapEdges=%d midLast=%d\n",
                         parPart, (int) parOverlapEdges, (int) parMidLast);
            if (alphaProbeIter > 0) { alphaProbeIter = -1; std::fprintf(stderr, "[par] RW_ALPHA_PROBE disabled under RW_PAR_PART\n"); }
        }
        historicalCongestionFactor = cfg.historicalCongestionFactor;
        presentCongestionFactor = cfg.initialPresentCongestionFactor;
        wlWeight = cfg.wirelengthWeight;

        // GRoute progress-factor present-congestion schedule (env RW_PROG). Instead of the geometric
        // pf *= mult every iteration (exponent = raw iteration count), set
        //     pf(i) = a * b^( lambda*prog + (1-lambda)*(i-1) ),  prog = 1 + ln(max(1, overuse0/overuse_recent))
        // so the penalty tracks ACTUAL congestion progress, not just the iteration index: gentle while
        // overuse is stuck (don't over-detour / inflate wirelength), firmer once overuse is collapsing
        // (close it out). a/b/lambda tunable; overuse0 = total overuse after the first routing iteration.
        // Defaults are GRoute's studied values (a=0.5=init, b=1.5, lambda=0.75). lambda is the
        // progress-damping weight; setting RW_PROG_BETA=mult and RW_PROG_LAMBDA=0 reproduces RWRoute's
        // exact geometric pf=init*mult^(i-1) (verified identity, used for validation).
        //
        // EMPIRICAL (env RW_PROG, default OFF): this is a CONGESTION-only lever. On THEIA_jpeg (congested)
        // it is time-neutral (161.2s->160.7s) AND cuts wirelength -0.39% -- the gentle schedule avoids the
        // baseline's runaway pf (1e6 by iter 18) that over-detours. But on mid/easy cases (oc_des/mcml/RLE)
        // the gentler ramp just adds iterations (mcml 11->34 at b=1.5) = slower for no wirelength gain.
        // So it is a Pareto win ONLY for heavily congested designs; default OFF, enable per-congested-run.
        bool   prog    = rwEnvI("RW_PROG", 0) != 0;
        // HUS knobs (see the checkHus port at the iteration boundary below)
        bool  husArmed = rwEnvI("RW_HUS", 0) != 0;
        bool  husInitialCongested = false;
        float husAlpha  = rwEnvF("RW_HUS_ALPHA", 1.1f);
        float husBeta   = rwEnvF("RW_HUS_BETA", 2.0f);
        float husInitTh = rwEnvF("RW_HUS_INIT", 0.5f);
        float husActTh  = rwEnvF("RW_HUS_ACT", 0.4f);
        double pAlpha  = rwEnvF("RW_PROG_ALPHA",  cfg.initialPresentCongestionFactor);
        double pBeta   = rwEnvF("RW_PROG_BETA",   1.5f);
        double pLambda = rwEnvF("RW_PROG_LAMBDA", 0.75f);
        long long overuse0 = -1;

#ifdef WITH_CUDA
        // Hybrid GPU-flood dispatch (env RW_GPU_FLOOD; default OFF). Expensive connections (predicted by
        // last-iteration pops >= RW_GPU_FLOOD_MIN) route on the GPU single-connection flood; the cheap
        // majority stays on the CPU A*. Committed sequentially with exact occupancy (zero-staleness).
        floodReady = false;
        long floodEnv = rwEnvI("RW_GPU_FLOOD", 0);
        // Banked verdict (2026-07-08, THEIA_20per): on the 2.2-3.5M-connection class the flood dispatch
        // is net NEGATIVE -- ~21k floods x 10-30ms serialize on the crit chain (adding lanes is neutral:
        // the chain's floods are sequential), and the CPU has idle capacity (util 45%). Flood OFF:
        // native-route 135->113s, e2e -22s, legal. Value 1 = banked default (this size gate applies);
        // 2 = force on everywhere. k_800 (2.07M) and 50per (4.96M) keep their measured-flooded behavior.
        if (floodEnv == 1 && connections.size() >= 2200000 && connections.size() < 3500000) {
            std::fprintf(stderr, "[gpu-flood] auto-off for %zu-connection case (20per-class verdict; RW_GPU_FLOOD=2 forces on)\n",
                         connections.size());
            floodEnv = 0;
        }
        if (floodEnv != 0) {
            // Defaults = the measured best config (live prices + no gate + budget-abort ~8k): RW_GPU_FLOOD=1
            // alone gives THEIA_jpeg -19% / THEIA -25%, legal, WL-neutral. (4k is marginally better on jpeg.)
            floodMin = rwEnvI("RW_GPU_FLOOD_MIN", 16384);
            floodOverGate = rwEnvI("RW_GPU_FLOOD_GATE", 0);
            floodLive = rwEnvI("RW_GPU_FLOOD_LIVE", 1) != 0;
            floodBudget = rwEnvI("RW_GPU_FLOOD_BUDGET", 8000);   // budget-abort dispatch (treats first-search miss)
            floodHedge = rwEnvI("RW_GPU_FLOOD_HEDGE", 0) != 0;   // CPU+flood race (supersedes budget-abort when on)
            floodHedgePoint = rwEnvI("RW_GPU_FLOOD_HEDGEPT", 4000);
            if (parPart > 0 && floodHedge) {                     // hedge spawns its own flood thread: incompatible
                floodHedge = false;                              // with the partition-parallel GPU-mutex discipline
                std::fprintf(stderr, "[par] RW_GPU_FLOOD_HEDGE disabled under RW_PAR_PART\n");
            }
            floodLenW = 1.0f * (1.0f - wlWeight);
            // Multi-lane pool: RW_GPU_FLOOD_LANES (clamp [1,6]); serial mode gains nothing
            // from >1 lane but loses nothing either (pool is uncontended there). VRAM budget on a
            // 24GB card: graph ~2.3GB + cong arrays ~0.8GB + lanes x numNodes*28B (~2.9GB/lane on a
            // 104M-node closure) -> 6 lanes ~20.5GB fits, 7+ does not.
            floodLaneCnt = (int) rwEnvI("RW_GPU_FLOOD_LANES", parPart > 0 ? 4 : 1);   // 4: 50per laneWait ~900s at 3
            if (floodLaneCnt < 1) floodLaneCnt = 1; if (floodLaneCnt > 6) floodLaneCnt = 6;
            laneFreeMask = (1u << floodLaneCnt) - 1u;
            for (int l = 0; l < floodLaneCnt; l++) {
                laneShareNodes[l].assign((size_t) SHARE_CAP_H, 0);
                laneShareCounts[l].assign((size_t) SHARE_CAP_H, 0);
            }
            connLastPops.assign(connections.size(), 0);
            netConns.assign(nets.size(), {});
            for (int i = 0; i < (int) connections.size(); i++) netConns[connections[i].netIdx].push_back(i);
            shareMark.assign((size_t) numNodes(), 0); floodMark = 1;
            if (floodLive) { dirtyStamp.assign((size_t) numNodes(), 0); resetDirtyLocal(); }
            if (lazy) {
                // JNI/lazy: the flat CSR the flood needs does not exist yet; iteration 1 will intern the
                // relevant subgraph, then we materialize + upload after it (setupFloodGpuNow at iter 2).
                floodDeferLazy = true;
                std::fprintf(stderr, "[gpu-flood] lazy graph -> deferring GPU upload until after iter-1\n");
            } else if (numNodes() > 0 && gpuUploadGraph() && gpuFloodInit(floodMaxPath, floodLaneCnt) == 0) {
                floodReady = true;
                std::fprintf(stderr, "[gpu-flood] hybrid loop ON exact-cost (min pops=%lld, gate=%ld, live=%d, lenW=%.3f)\n",
                             floodMin, floodOverGate, (int) floodLive, floodLenW);
                // ALT landmarks for huge cases: must run NOW while d_congCost is still all-1.0
                // (before the first refreshFloodCost). ~30-60s upfront vs the mega-leaf chain.
                if (connections.size() > 3000000 && rwEnvI("RW_LMK", 0)) computeLandmarks();   // MEASURED NEGATIVE: static-graph max cost ~0.37/tile < the banked 0.8*Manhattan term -> ALT never wins the max, pure per-push overhead (50per iter-1 1218->1559s). The banked h is already tighter than ANY admissible static bound; headroom exists only in congestion-aware h.
            } else std::fprintf(stderr, "[gpu-flood] setup failed -> pure CPU\n");
        }
#endif

        while (routeIteration < cfg.maxIterations) {
            auto _it0 = std::chrono::steady_clock::now();
#ifdef WITH_CUDA
            if (floodDeferLazy && !floodReady && routeIteration >= 2) {   // iter-1 interned the graph -> upload now
                setupFloodGpuNow(); floodDeferLazy = false;               // one-shot; on failure stay pure CPU
            }
            floodActive = false; floodedCount = 0; floodFallback = 0;
            // Flood the congested BULK; gate>0 hands the endgame to CPU (needed when prices are FROZEN, else
            // the endgame oscillates). With live prices (floodLive) the flood tracks CPU so the gate can be 0.
            // RW_GPU_FLOOD_ITER1=1: also flood in iteration 1 (no congestion yet, so the usual
            // overused>gate condition is false there). With MIDLAST scheduling the giant straddlers
            // run at the END of iter-1 with most workers idle -- budget-aborting them to the GPU cuts
            // that serial tail. Prices are all-1 at iter-1, so flood paths match fresh CPU searches.
            bool floodIter1 = routeIteration == 1 && parPart > 0 && rwEnvI("RW_GPU_FLOOD_ITER1", 1) != 0;
            if (floodReady && ((floodEverEligible && (long) overUsedList.size() > floodOverGate) || floodIter1)) {
                refreshFloodCost(parPart); floodActive = true;   // iteration boundary: all lanes idle by construction
                if (floodLive) resetDirtyLocal();         // full refresh made GPU current -> drop pending deltas
            }
            trackDirty = floodActive && floodLive;
#endif
            if (prog && overuse0 >= 0) {
                double ratio = (currentTotalOveruse > 0) ? (double) overuse0 / (double) currentTotalOveruse
                                                         : (double) overuse0;
                double progTerm = 1.0 + std::log(std::max(1.0, ratio));
                double expo = pLambda * progTerm + (1.0 - pLambda) * (double)(routeIteration - 1);
                double pf = pAlpha * std::pow(pBeta, expo);
                presentCongestionFactor = (float) std::min(pf, (double) cfg.maxPresentCongestionFactor);
            }
            updatePresentCongestionCosts(presentCongestionFactor);
            iterPops = 0; iterMaxPops = 0; for (int b = 0; b < 28; b++) iterPopHist[b] = 0;
            bigConnsThisIter.clear();
            if (alphaProbeIter > 0 && routeIteration >= alphaProbeIter) {   // presearch a sample at iter-START prices
                alphaSample.clear(); alphaPathStart.clear();
                std::vector<int> routing;                            // connections that will (re)route this iter
                for (int idx : sortedIndirect) { Connection& c = connections[idx]; if (!c.abandoned && shouldRoute(c)) routing.push_back(idx); }
                int stepc = std::max(1, (int) routing.size() / 2000);
                alphaSlot.assign(connections.size(), -1);
                for (int i = 0; i < (int) routing.size(); i += stepc) {
                    int idx = routing[i]; Connection& c = connections[idx];
                    std::vector<int> oldPath = c.rnodes; bool oldRouted = c.routed;
                    routeIndirectConnection(idx);                    // search at P_start (commits, then we restore)
                    alphaSlot[idx] = (int) alphaSample.size();
                    alphaSample.push_back(idx); alphaPathStart.push_back(c.rnodes);
                    ripUp(c); c.rnodes = oldPath; c.routed = oldRouted;
                    if (!c.rnodes.empty()) updateUsersAndPresentCongestionCost(c);   // restore occupancy to P_start
                }
                alphaCommitCF.assign(alphaSample.size(), 0);
                alphaCostAcc.assign(alphaSample.size(), 0);
                alphaSeen.assign(alphaSample.size(), 0);
                alphaPops.assign(alphaSample.size(), 0);
            }
            // ENDGAME pre-rip (RW_ENDGAME=threshold, banked below): the long tail grinds because
            // interlocked pairs release only one layer per iteration (each reroute still sees the
            // other's OLD occupancy). Once the contested set is small, rip ALL of it up front --
            // the in-order (leaf-serial) rerouting then resolves mutual locks in one pass; leftovers
            // fall back to the normal grind. One-shot per run; wl impact is a handful of conns.
            if (endgameAt < 0)
                endgameAt = 0;   // measured NEUTRAL (E28: 38 iters unchanged -- the tail is fresh overuse per round, not interlock cycles); opt-in only
            if (endgameAt > 0 && !endgameDone && routeIteration >= 8 &&
                !overUsedList.empty() && (long) overUsedList.size() < endgameAt) {
                size_t ripped = 0;
                for (int idx : sortedIndirect) {
                    Connection& c = connections[idx];
                    if (c.abandoned || !shouldRoute(c)) continue;
                    ripUp(c); c.rnodes.clear(); c.routed = false; ripped++;
                }
                endgameDone = true;
                std::fprintf(stderr, "[endgame] pre-ripped %zu contested conns at iter=%d overused=%zu\n",
                             ripped, routeIteration, overUsedList.size());
            }
            auto _s0 = std::chrono::steady_clock::now();
            int rerouted = (overlapT > 1)                            // overlap-tolerant LIVE parallel (all iterations)
                         ? routeIndirectConnectionsOverlap(overlapT)
                         : (parPart >= 1)                            // RPTT partition-parallel (all iterations)
                         ? routeIndirectConnectionsPartitioned()
                         : (parIter1 >= 1 && routeIteration == 1)    // §Phase-1 gate: parallelize the big iter-1 (T>=1)
                         ? routeIndirectConnectionsParallel(parIter1)
                         : routeIndirectConnections();
            double _srch = std::chrono::duration<double>(std::chrono::steady_clock::now() - _s0).count();
            // HUS (Hybrid Updating Strategy, CUFR upstream; env RW_HUS=1): one-shot switch to
            // slow-present (alpha) / strong-historical (beta) growth once (a) iteration 1 was congested
            // enough and (b) the reroute fraction has dropped below the activation threshold. Faithful
            // ordering: decide BEFORE this boundary's pf inflation and hist accumulation, so both use
            // the new factors from this boundary on (matches RWRoute.checkHus placement). NOTE: upstream
            // defaults (init>0.5) never fire on our cases (iter-1 overuse ratio 0.10-0.13) -- tune
            // RW_HUS_INIT down to arm it.
            if (husArmed && !prog) {
                if (routeIteration == 1) {
                    long ov = 0;
                    for (int id = 0, N = numNodes(); id < N; id++)
                        if (created[id] && getOccupancy(id) > CAPACITY) ov++;
                    husInitialCongested = (double) ov / (double) sortedIndirect.size() > husInitTh;
                    if (!husInitialCongested) husArmed = false;   // can never activate (upstream semantics)
                } else if ((double) rerouted / (double) sortedIndirect.size() < husActTh) {
                    cfg.presentCongestionMultiplier = husAlpha;
                    historicalCongestionFactor = husBeta;
                    husArmed = false;
                    std::printf("INFO: Hybrid Updating Strategy (HUS) activated at iteration %d (alpha=%.2f beta=%.2f)\n",
                                routeIteration, husAlpha, husBeta);
                }
            }
            auto _uc0 = std::chrono::steady_clock::now();
            if (prog) updateCost();          // prog sets pf itself -> skip the geometric bump in updateCostFactors
            else      updateCostFactors();    // default RWRoute schedule (pf *= mult, capped at max)
            double _ucS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _uc0).count();
            // Tail accelerator (RW_HIST_TAIL=<factor>, default off): once the overuse straggler tail is
            // reached (overused < RW_HIST_TAIL_AT, default 500), raise the HISTORICAL congestion factor
            // so the last few contested nodes price themselves out in fewer iterations (20per: 52 tail
            // iterations clearing 189->0). pf is already at/near its cap there, so this only compounds
            // permanence on the handful of oscillating nodes; the reroute sets are tiny -> WL impact
            // negligible. Convergence-changing => legality-gated (checker + Vivado), off by default.
            {
                // Banked default (2026-07-08): ON at 2.0 for the 20per-class connection band only --
                // measured 64->38 iterations, native-route 106.5->96.7s, wl +0.03%, legal + Vivado
                // clean. 3.0 measured equivalent (40 iters); earlier activation (AT=5000) NEGATIVE
                // (56 iters). Other cases keep hist untouched (bit-identical results preserved).
                const bool tailBand = connections.size() >= 2200000;   // >=3.5M banked too (50per E-A)
                static const float histTail   = rwEnvF("RW_HIST_TAIL", tailBand ? 2.0f : 0.0f);
                static const long  histTailAt = rwEnvI("RW_HIST_TAIL_AT", 500);
                if (histTail > 0.0f && historicalCongestionFactor < histTail &&
                    (long) overUsedList.size() < histTailAt && overUsedList.size() > 0) {
                    historicalCongestionFactor = histTail;
                    std::fprintf(stderr, "[tail] iter=%d overused=%zu -> historicalCongestionFactor=%.1f\n",
                                 routeIteration, overUsedList.size(), histTail);
                }
            }
            if (overuse0 < 0) overuse0 = currentTotalOveruse;   // baseline = total overuse after iteration 1
            if (alphaProbeIter > 0 && routeIteration >= alphaProbeIter) {   // did the presearched paths survive to commit?
                long exact = 0, commitCF = 0, costAcc = 0, n = 0;   // n = samples that actually routed
                long mN = 0, mAcc = 0, kN = 0, kAcc = 0;            // masses (<4k pops) vs monsters (>=4k) cost-alpha
                for (size_t k = 0; k < alphaSample.size(); k++) {
                    if (k >= alphaSeen.size() || !alphaSeen[k]) continue;   // only connections that reached the router
                    Connection& c = connections[alphaSample[k]]; auto& ps = alphaPathStart[k];
                    n++;
                    if (ps == c.rnodes) exact++;                       // presearched path == committed path (strict)
                    if (alphaCommitCF[k]) commitCF++;                  // conflict-free at commit time
                    char acc = alphaCostAcc[k];
                    if (acc) costAcc++;                                // within 5% of fresh cost (TRUE alpha)
                    if (alphaPops[k] < 4000) { mN++; if (acc) mAcc++; } // masses: the batch-presearch target
                    else                     { kN++; if (acc) kAcc++; } // monsters: flood-handled, not presearchable
                }
                std::fprintf(stderr,
                    "ALPHA iter=%d routed=%ld costAlpha=%.1f%% exact=%.1f%% commitCF=%.1f%% | MASSES(<4k) n=%ld a=%.1f%% | MON(>=4k) n=%ld a=%.1f%%\n",
                    routeIteration, n, n ? 100.0 * costAcc / n : 0.0, n ? 100.0 * exact / n : 0.0,
                    n ? 100.0 * commitCF / n : 0.0,
                    mN, mN ? 100.0 * mAcc / mN : 0.0, kN, kN ? 100.0 * kAcc / kN : 0.0);
                std::fflush(stderr);
            }

            auto _un0 = std::chrono::steady_clock::now();
            std::vector<int> unroutable;
            for (int idx : sortedIndirect) {
                Connection& c = connections[idx];
                if (!c.routed && !c.abandoned) unroutable.push_back(idx);
            }
            for (int idx : unroutable) handleUnroutableConnection(idx);
            double _unS = std::chrono::duration<double>(std::chrono::steady_clock::now() - _un0).count();

            double _itw = std::chrono::duration<double>(std::chrono::steady_clock::now() - _it0).count();
            if (parReport)   // boundary decomposition: iter wall minus search = updateCost + unroutable + rest
                std::fprintf(stderr, "[bdry] iter=%d srch=%.3f updc=%.3f unrt=%.3f other=%.3f\n",
                             routeIteration, _srch, _ucS, _unS, _itw - _srch - _ucS - _unS);
            std::printf("%4d       overused=%d  totalOveruse=%lld  unroutable=%d  rerouted=%d  pf=%.3f  wall=%.2fs\n",
                        routeIteration, (int)overUsedList.size(), currentTotalOveruse, (int)unroutable.size(), rerouted,
                        presentCongestionFactor, _itw);
#ifdef WITH_CUDA
            if (floodActive) std::printf("          FLOOD gpu=%lld cpuFallback=%lld\n", floodedCount.load(), floodFallback.load());
#endif
            if (corridorM >= 0 && (corridorHit.load() || corridorFallback.load())) {
                std::printf("          CORRIDOR hit=%lld fullBoxFallback=%lld\n",
                            corridorHit.load(std::memory_order_relaxed), corridorFallback.load(std::memory_order_relaxed));
                corridorHit.store(0, std::memory_order_relaxed); corridorFallback.store(0, std::memory_order_relaxed);
            }
            if (measurePops && rerouted > 0) {
                long long ip = iterPops.load(), im = iterMaxPops.load();
                double popsPerConn = (double) ip / rerouted;
                double nsPerPop = ip > 0 ? _srch * 1e9 / ip : 0.0;
                std::printf("          POPS pops=%lld  pops/conn=%.0f  maxPops=%lld  srch=%.2fs  ns/pop=%.1f  |dist",
                            ip, popsPerConn, im, _srch, nsPerPop);
                for (int b = 0; b < 28; b++) { long long h = iterPopHist[b].load();
                    if (h) std::printf(" %d-%d:%lld", 1 << b, (1 << (b + 1)) - 1, h); }
                std::printf("\n");
            }
            std::fflush(stdout);
            if (routeIteration == priceVarIter) { dumpPriceVariance(); std::fflush(stderr); std::exit(0); }
#ifdef WITH_CUDA
            if (routeIteration == floodProtoIter) { floodProto(); }   // shadow flood proto; exits inside
#endif

            if (overUsedList.empty() && unroutable.empty()) break;
            routeIteration++;
        }
#ifdef WITH_CUDA
        if (floodReady) { gpuFloodFree(); gpuRouteShutdown(); floodReady = false; }
#endif
        totalPushes.fetch_add(tl_pushes, std::memory_order_relaxed); tl_pushes = 0;   // flush the main thread's share
        std::fprintf(stderr, "ROUTE_SUMMARY iters=%d overused=%d direct=%.2f totalPushes=%lld prog=%d\n",
                     routeIteration, (int)overUsedList.size(), directedness, totalPushes.load(), (int)prog);
        // Total wirelength (20% metric): legal routing has <=1 net per node, so per-net-dedup sum of
        // node length == sum of length over all used nodes (matches RWRouteCppCheck's "Total wirelength").
        { long long usedNodes = 0, wl = 0, N = numNodes();
          for (long long id = 0; id < N; id++) if (created[id] && occCnt[id] > 0) { usedNodes++; wl += ns[id].length; }
          std::fprintf(stderr, "WIRELENGTH usedNodes=%lld totalLen=%lld\n", usedNodes, wl); }

        // Diagnostic: report any connections that never routed.
        int reported = 0;
        for (int idx : sortedIndirect) {
            Connection& c = connections[idx];
            if (c.routed) continue;
            if (reported++ >= 8) break;
            int src = c.sourceRnode, snk = c.sinkRnode;
            std::printf("UNROUTABLE conn=%d net=%d bbox=[%d,%d]x[%d,%d] crossSLR=%d "
                        "src(end=%d,%d type=%d) sink(end=%d,%d begin=%d,%d type=%d nAlt=%zu) "
                        "srcChildren=%zu sinkCreated=%d sinkPreserved=%d\n",
                        c.connId, c.netIdx, c.xMinBB, c.xMaxBB, c.yMinBB, c.yMaxBB, (int)c.isCrossSLR(),
                        getEndTileXCoordinate(src), getEndTileYCoordinate(src), (int)type[src],
                        getEndTileXCoordinate(snk), getEndTileYCoordinate(snk),
                        getBeginTileXCoordinate(snk), getBeginTileYCoordinate(snk), (int)type[snk],
                        c.altSinks.size(),
                        getChildren(src).size(), (int)created[snk], (int)ns[snk].preserved);
        }
    }

    // Flag every real sink / alternate sink so the dead-end prune can never drop a routing destination.
    // Must run after all connections are loaded (and, in lazy mode, after sinks have been interned).
    void markSinkNodes() {
        for (auto& c : connections) {
            if (c.sinkRnode >= 0) isSinkNode[c.sinkRnode] = 1;
            for (int a : c.altSinks) if (a >= 0) isSinkNode[a] = 1;
        }
    }

    // ----------------------------------------------------------------- load
    void load(const std::string& path) { rw::BinReader r(path); load(r); }
    void load(rw::BinReader& r) {
        r.expectMagic("RRT1");
        cfg.maxIterations = r.i32();
        cfg.boundingBoxExtensionX = r.i32();
        cfg.boundingBoxExtensionY = r.i32();
        cfg.enlargeBoundingBox = r.i32() != 0;
        cfg.extensionXIncrement = r.i32();
        cfg.extensionYIncrement = r.i32();
        cfg.useBoundingBox = r.i32() != 0;
        cfg.wirelengthWeight = r.f32();
        cfg.shareExponent = r.f32();
        cfg.initialPresentCongestionFactor = r.f32();
        cfg.presentCongestionMultiplier = r.f32();
        cfg.historicalCongestionFactor = r.f32();
        cfg.maxPresentCongestionFactor = r.f32();
        cfg.maxDetourToSnapBackToPrevLagunaColumn = r.i32();
        cfg.superLongLineLengthInTiles = r.i32();
        cfg.useUTurnNodes = r.i32() != 0;
        superLongLineLength = cfg.superLongLineLengthInTiles;

        int numRows = r.i32();
        intYToSLRIndex.resize(numRows);
        for (int y = 0; y < numRows; y++) intYToSLRIndex[y] = r.i32();
        hasLaguna = r.i32() != 0;
        if (hasLaguna) {
            int numCols = r.i32();
            nextLagunaColumn.resize(numCols);
            prevLagunaColumn.resize(numCols);
            for (int x = 0; x < numCols; x++) nextLagunaColumn[x] = r.i32();
            for (int x = 0; x < numCols; x++) prevLagunaColumn[x] = r.i32();
            intYToNorthboundLaguna.resize(numRows);
            for (int y = 0; y < numRows; y++) intYToNorthboundLaguna[y] = r.u8();
        }

        int n = r.i32();
        reserveNodes((size_t) n);   // reserve first: huge pages + (parallel) NUMA interleave before first touch
        ns.resize(n);
        nc.resize(n);
        std::vector<std::vector<int>> tmpChildren(n);
        for (int i = 0; i < n; i++) {
            NodeStatic& a = ns[i];
            NodeCold& cd = nc[i];
            a.tileAddr = r.i32();
            cd.wireIndex = r.i32();
            cd.type = (RouteNodeType)r.u8();
            int flags = r.u8();
            a.beginX = r.i16(); a.beginY = r.i16();
            a.endX = r.i16(); a.endY = r.i16();
            a.length = r.i16();
            a.baseCost = r.f32();
            cd.hashCode = r.i32();
            cd.prevInit = r.i32();
            int cc = r.i32();
            tmpChildren[i].resize(cc);
            for (int k = 0; k < cc; k++) tmpChildren[i][k] = r.i32();
            cd.createdAtInit = flags & 1;
            a.isLaguna = flags & 2;
            a.isPinfeed = flags & 4;
            a.pinfeedLeadsToLaguna = flags & 8;
            a.arcLockedInit = flags & 32;
            a.preserved = flags & 64;
            a.isPinbounce = flags & 128;
        }
        // flatten children
        size_t total = 0;
        for (auto& v : tmpChildren) total += v.size();
        childIds.reserve(total);
        for (int i = 0; i < n; i++) {
            ns[i].childStart = (int)childIds.size();
            ns[i].childCount = (int)tmpChildren[i].size();
            for (int v : tmpChildren[i]) childIds.push_back(v);
        }

        nodeCountA.store(n, std::memory_order_release);   // eager: all nodes exist before routing
        keyToId.reset((size_t) n * 2);
        for (int i = 0; i < n; i++) {
            keyToId.putSerial(((long long) ns[i].tileAddr << 20) | (nc[i].wireIndex & 0xFFFFF), i);
        }

        auto b_state_start = bprof::Clock::now();
        // init mutable state
        type.resize(n);
        { bprof::Scope b_scope(bprof::INIT_LABELS); dyn.assign(n, NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0}); }
        created.assign(n, 0);
        ownerNet.assign(n, -1); ownerCnt.assign(n, 0); userOverflow.assign(n, nullptr);
        occCnt.assign(n, 0); hot.assign(n, HotExpand{}); childrenCache.assign(n, nullptr);
        overUsed.assign(n, 0);
        deadEnd.assign(n, 0); isSinkNode.assign(n, 0);
        for (int i = 0; i < n; i++) {
            type[i] = nc[i].type;
            if (nc[i].createdAtInit) {
                created[i] = 1;
                dyn[i].prev = nc[i].prevInit;
            }
            initHotFromStatic(i);
        }

        bprof::nanos[bprof::INIT_STATE] += bprof::ns(b_state_start); ++bprof::calls[bprof::INIT_STATE];
        int numNets = r.i32();
        nets.resize(numNets);
        for (int ni = 0; ni < numNets; ni++) {
            NetWrapper& nw = nets[ni];
            nw.xCenter = r.f32();
            nw.yCenter = r.f32();
            nw.doubleHpwl = r.i16();
            nw.connectionsSize = r.i32();
            nw.sourceRnode = r.i32();
            int nc = r.i32();
            for (int ci = 0; ci < nc; ci++) {
                Connection c;
                c.netIdx = ni;
                c.connId = r.i32();
                c.sourceRnode = r.i32();
                c.sinkRnode = r.i32();
                int na = r.i32();
                c.altSinks.resize(na);
                for (int k = 0; k < na; k++) c.altSinks[k] = r.i32();
                c.xMinBB = r.i16(); c.xMaxBB = r.i16(); c.yMinBB = r.i16(); c.yMaxBB = r.i16();
                c.hpwl = r.i16();
                c.crossSLRnorth = r.u8() != 0;
                c.crossSLRsouth = r.u8() != 0;
                c.routedAtInit = r.u8() != 0;
                int nr = r.i32();
                // A3: load the initial route straight into the working `rnodes` when routed-at-init;
                // otherwise consume+discard so rnodes stays empty. No permanent per-conn initRnodes.
                if (c.routedAtInit) { c.rnodes.resize(nr); for (int k = 0; k < nr; k++) c.rnodes[k] = r.i32(); }
                else { for (int k = 0; k < nr; k++) (void) r.i32(); }
                connections.push_back(std::move(c));
            }
        }

        markSinkNodes();
        // Replicate the init user counting (createNetWrapperAndConnections + reconstruction).
        for (auto& c : connections) {
            indirectAll.push_back((int)(&c - &connections[0]));
        }
        for (auto& c : connections) {
            if (!c.hasAltSinks()) incrementUser(c.sinkRnode, c.netIdx);  // line 796 pre-increment
            if (c.routedAtInit) {
                c.routed = true;   // rnodes already holds the initial route (loaded in A3)
                int sinkRnode = c.rnodes[0];
                int begin = 0, end = (int)c.rnodes.size();
                if (sinkRnode == c.sinkRnode && !c.hasAltSinks()) { begin = 1; end = (int)c.rnodes.size() - 1; }
                for (int i = begin; i < end; i++) incrementUser(c.rnodes[i], c.netIdx);
            } else {
                c.routed = false;
            }
        }
    }

    // Hint the kernel to back a vector's (large) reserved buffer with transparent huge pages. THP is in
    // [madvise] mode here, so malloc'd buffers default to 4KB pages -> heavy TLB misses on the random-
    // access maze search (the dominant route cost). MADV_HUGEPAGE on the hot per-node arrays cuts that.
    template<class V> static void adviseHuge(V& v) {
#if defined(__linux__)
        size_t bytes = v.capacity() * sizeof(typename V::value_type);
        if (bytes < (4u << 20)) return;                 // not worth it for small buffers
        uintptr_t a = (uintptr_t) v.data();
        uintptr_t aligned = a & ~((uintptr_t) 4095);    // madvise needs a page-aligned start
        madvise((void*) aligned, bytes + (a - aligned), MADV_HUGEPAGE);
#else
        (void) v;
#endif
    }
    // NUMA interleave for the maze-hot arrays (multi-thread only): the loader thread first-touches
    // everything onto its own socket, halving usable memory bandwidth for a two-socket worker fleet.
    // mbind(MPOL_INTERLEAVE) on the reserved VMA makes future first-touches alternate sockets (pages
    // already faulted stay put -- we bind right after reserve, before the bulk touch). Unprivileged.
    template<class V> static void bindInterleave(V& v) {
#if defined(__linux__) && defined(SYS_mbind)
        size_t bytes = v.capacity() * sizeof(typename V::value_type);
        if (bytes < (16u << 20)) return;
        uintptr_t a = (uintptr_t) v.data();
        uintptr_t aligned = a & ~((uintptr_t) 4095);
        unsigned long mask = ~0ul;                       // all nodes the process may run on
        syscall(SYS_mbind, (void*) aligned, bytes + (a - aligned), 3 /*MPOL_INTERLEAVE*/,
                &mask, (unsigned long) (8 * sizeof(mask) + 1), 0ul);
#else
        (void) v;
#endif
    }
    void reserveNodes(size_t n) {
        ns.reserve(n); nc.reserve(n); type.reserve(n); dyn.reserve(n); created.reserve(n);
        ownerNet.reserve(n); ownerCnt.reserve(n); userOverflow.reserve(n);
        occCnt.reserve(n); hot.reserve(n); childrenCache.reserve(n); overUsed.reserve(n);
        deadEnd.reserve(n); isSinkNode.reserve(n);
        rawFetched.reserve(n); rawChildrenStore.reserve(n); kiGrow(n * 2);
        if (n >= (4u << 20)) {  // big case: huge-page the hot arrays the maze search hammers
            adviseHuge(ns); adviseHuge(dyn); adviseHuge(type); adviseHuge(occCnt);
            adviseHuge(ownerNet); adviseHuge(ownerCnt); adviseHuge(hot);
        }
        if (parPart > 0 && parNuma && n >= (4u << 20)) {  // multi-thread: spread the hot arrays across sockets
            bindInterleave(ns); bindInterleave(dyn); bindInterleave(type); bindInterleave(occCnt);
            bindInterleave(ownerNet); bindInterleave(ownerCnt); bindInterleave(hot);
            bindInterleave(created); bindInterleave(overUsed); bindInterleave(childIds);
        }
    }

    // Lazy (JNI) format RRT2: config + device arrays + SEED nodes (initial rnodes, with attrs +
    // existing-route prev) + nets/connections (node refs by KEY). Interior nodes are pulled on
    // demand via fetchChildrenPacked during routing.
    void loadLazy(rw::BinReader& r) {
        lazy = !flatGraphBuilt;                        // prepass-early may have gone eager already
        reserveNodes(1 << 20);
        r.expectMagic("RRT2");
        cfg.maxIterations = r.i32();
        cfg.boundingBoxExtensionX = r.i32();
        cfg.boundingBoxExtensionY = r.i32();
        cfg.enlargeBoundingBox = r.i32() != 0;
        cfg.extensionXIncrement = r.i32();
        cfg.extensionYIncrement = r.i32();
        cfg.useBoundingBox = r.i32() != 0;
        cfg.wirelengthWeight = r.f32();
        cfg.shareExponent = r.f32();
        cfg.initialPresentCongestionFactor = r.f32();
        cfg.presentCongestionMultiplier = r.f32();
        cfg.historicalCongestionFactor = r.f32();
        cfg.maxPresentCongestionFactor = r.f32();
        cfg.maxDetourToSnapBackToPrevLagunaColumn = r.i32();
        cfg.superLongLineLengthInTiles = r.i32();
        cfg.useUTurnNodes = r.i32() != 0;
        superLongLineLength = cfg.superLongLineLengthInTiles;
        int numRows = r.i32();
        intYToSLRIndex.resize(numRows);
        for (int y = 0; y < numRows; y++) intYToSLRIndex[y] = r.i32();
        hasLaguna = r.i32() != 0;
        if (hasLaguna) {
            int numCols = r.i32();
            nextLagunaColumn.resize(numCols);
            prevLagunaColumn.resize(numCols);
            for (int x = 0; x < numCols; x++) nextLagunaColumn[x] = r.i32();
            for (int x = 0; x < numCols; x++) prevLagunaColumn[x] = r.i32();
            intYToNorthboundLaguna.resize(numRows);
            for (int y = 0; y < numRows; y++) intYToNorthboundLaguna[y] = r.u8();
        }
        // B2 (Track B): override the congestion schedule from env so we can sweep convergence knobs
        // WITHOUT recompiling Java. Defaults = the values just read from the stream (Java config).
        cfg.initialPresentCongestionFactor = rwEnvF("RW_PRES_INIT", cfg.initialPresentCongestionFactor);
        cfg.presentCongestionMultiplier    = rwEnvF("RW_PRES_MUL",  cfg.presentCongestionMultiplier);
        cfg.historicalCongestionFactor     = rwEnvF("RW_HIST",      cfg.historicalCongestionFactor);
        cfg.maxPresentCongestionFactor     = rwEnvF("RW_PRES_MAX",  cfg.maxPresentCongestionFactor);
        cfg.maxIterations                  = rwEnvI("RW_MAXIT",     cfg.maxIterations);
        std::fprintf(stderr, "B2cfg presInit=%.4f presMul=%.4f hist=%.4f presMax=%.1f maxIt=%d\n",
                     cfg.initialPresentCongestionFactor, cfg.presentCongestionMultiplier,
                     cfg.historicalCongestionFactor, cfg.maxPresentCongestionFactor, cfg.maxIterations);
        // SEEDS
        int numSeeds = r.i32();
        // Big case: reserve the per-node arrays generously so they don't realloc mid-route (which would
        // drop the huge-page advice) and so the maze search runs on huge pages. Capacity is virtual until
        // touched, so over-reserving costs only address space. numSeeds is a reliable big/small proxy.
        if (numSeeds > 300000)
            // Partition-parallel interning must NEVER hit capacity mid-iteration (FATAL guard), so give
            // it a deeper virtual reserve (untouched pages cost address space only).
            reserveNodes(parPart > 0 ? std::min((size_t) 96000000, (size_t) numSeeds * 24)
                                     : std::min((size_t) 64000000, (size_t) numSeeds * 12));
        std::vector<std::pair<long long, long long>> prevKeys;
        // Seed records are FIXED 39 bytes (tile4 wire4 type1 flags4 i16x5 baseCost4 hash4 prev4+4).
        // When a prepass graph exists (prepass-early/fulldev), almost every seed key already resolves:
        // decode + backfill in PARALLEL (duplicate seeds write identical values -> benign), collect
        // the rare misses and intern them SERIALLY IN ORIGINAL RECORD ORDER -- ids and all attrs come
        // out identical to the sequential loop (20per: 3.5M seeds, ~3s -> ~0.4s).
        auto decodeSeed = [](const uint8_t* p, NodeStatic& a, NodeCold& cd) {
            auto rdI32 = [](const uint8_t* q) { uint32_t v; std::memcpy(&v, q, 4); return (int32_t) v; };
            auto rdI16 = [](const uint8_t* q) { uint16_t v; std::memcpy(&v, q, 2); return (int16_t) v; };
            a = NodeStatic{}; cd = NodeCold{};
            a.tileAddr = rdI32(p); cd.wireIndex = rdI32(p + 4);
            cd.type = (RouteNodeType) p[8];
            int flags = rdI32(p + 9);
            a.isLaguna = flags & 1; a.isPinfeed = flags & 2; a.pinfeedLeadsToLaguna = flags & 4;
            a.isPinbounce = flags & 8; a.preserved = flags & 16; a.arcLockedInit = flags & 32;
            cd.createdAtInit = flags & 64;
            a.beginX = rdI16(p + 13); a.beginY = rdI16(p + 15); a.endX = rdI16(p + 17); a.endY = rdI16(p + 19);
            a.length = rdI16(p + 21); std::memcpy(&a.baseCost, p + 23, 4); cd.hashCode = rdI32(p + 27);
            cd.prevInit = -1; a.childStart = a.childCount = 0;
            return flags;
        };
        if (parPart > 1 && numSeeds > 500000 && earlyTotal >= 0) {
            const size_t seedsStart = r.pos();
            const uint8_t* base = r.data() + seedsStart;
            const int T = parPart;
            prevKeys.resize((size_t) numSeeds);
            std::vector<std::vector<int>> tMiss((size_t) T);
            parForN((size_t) numSeeds, T, [&](int w, size_t lo, size_t hi) {
                NodeStatic a; NodeCold cd;
                for (size_t s = lo; s < hi; s++) {
                    const uint8_t* p = base + s * 39;
                    int flags = decodeSeed(p, a, cd);
                    long long key = ((long long) a.tileAddr << 20) | (cd.wireIndex & 0xFFFFF);
                    auto rdI32 = [](const uint8_t* q) { uint32_t v; std::memcpy(&v, q, 4); return (int32_t) v; };
                    int prevAddr = rdI32(p + 31), prevWire = rdI32(p + 35);
                    prevKeys[s] = {key, prevAddr < 0 ? -1LL : (((long long) prevAddr << 20) | (prevWire & 0xFFFFF))};
                    int sid = keyToId.find(key);
                    if (sid < 0) { tMiss[(size_t) w].push_back((int) s); continue; }
                    if (sid < earlyTotal) {
                        if (flags & 16) ns[(size_t) sid].preserved = true;
                        if (flags & 32) ns[(size_t) sid].arcLockedInit = true;
                        if (flags & 64) created[(size_t) sid] = 1;
                        if (cd.type != type[(size_t) sid]) type[(size_t) sid] = cd.type;
                        initHotFromStatic(sid); syncHotOcc(sid);
                    }
                }
            });
            std::vector<int> misses;
            for (auto& v : tMiss) misses.insert(misses.end(), v.begin(), v.end());
            std::sort(misses.begin(), misses.end());       // original record order -> identical intern ids
            NodeStatic a; NodeCold cd;
            for (int s : misses) {
                decodeSeed(base + (size_t) s * 39, a, cd);
                int sid = internNode(a, cd);
                (void) sid;                                // >= earlyTotal by construction: no backfill
            }
            r.seek(seedsStart + (size_t) numSeeds * 39);
        } else {
        prevKeys.reserve(numSeeds);
        for (int s = 0; s < numSeeds; s++) {
            NodeStatic a{}; NodeCold cd{};
            a.tileAddr = r.i32(); cd.wireIndex = r.i32();
            cd.type = (RouteNodeType) r.u8();
            int flags = r.i32();
            a.isLaguna = flags & 1; a.isPinfeed = flags & 2; a.pinfeedLeadsToLaguna = flags & 4;
            a.isPinbounce = flags & 8; a.preserved = flags & 16; a.arcLockedInit = flags & 32;
            cd.createdAtInit = flags & 64;
            a.beginX = r.i16(); a.beginY = r.i16(); a.endX = r.i16(); a.endY = r.i16();
            a.length = r.i16(); a.baseCost = r.f32(); cd.hashCode = r.i32();
            int prevAddr = r.i32(); int prevWire = r.i32();
            cd.prevInit = -1; a.childStart = a.childCount = 0;
            int sid = internNode(a, cd);
            // prepass-early: the node may pre-exist (closure-discovered via the DESIGN-INDEPENDENT
            // compact device, which cannot know design state) -- re-apply the design-state attrs.
            if (earlyTotal >= 0 && sid < earlyTotal) {
                if (a.preserved) ns[(size_t) sid].preserved = true;
                if (a.arcLockedInit) ns[(size_t) sid].arcLockedInit = true;
                if (cd.createdAtInit) created[(size_t) sid] = 1;
                if (cd.type != type[(size_t) sid]) type[(size_t) sid] = cd.type;   // e.g. EXCLUSIVE_* sink types
                initHotFromStatic(sid); syncHotOcc(sid);           // re-mirror ns/type into the hot bundle
            }
            long long key = ((long long) a.tileAddr << 20) | (cd.wireIndex & 0xFFFFF);
            long long pk = (prevAddr < 0) ? -1 : (((long long) prevAddr << 20) | (prevWire & 0xFFFFF));
            prevKeys.push_back({key, pk});
        }
        }
        for (auto& pr : prevKeys) {
            if (pr.second < 0) continue;
            int a = keyToId.find(pr.first), b = keyToId.find(pr.second);
            if (a >= 0 && b >= 0) dyn[a].prev = b;
        }
        auto idByKey = [&](int addr, int wire) -> int {
            return keyToId.find(((long long) addr << 20) | (wire & 0xFFFFF));
        };
        int numNets = r.i32();
        nets.resize(numNets);
        // NETS chunk table (the parallel serializer emits it): magic is a NaN bit pattern -- a legacy
        // stream holds the first net's xCenter here, never NaN -> unambiguous versioning. With the
        // table, the P writer chunks parse CONCURRENTLY into preallocated nets/connections slots,
        // field-for-field the same decode as the serial loop below => identical state.
        bool parNets = false;
        {
            size_t tablePos = r.pos();
            if (numNets > 0 && r.pos() + 4 <= r.size() && (uint32_t) r.i32() == 0xFFC0DE01u) {
                int P = r.i32();
                std::vector<int> cNets((size_t) P), cConns((size_t) P), cBytes((size_t) P);
                for (int t = 0; t < P; t++) { cNets[(size_t) t] = r.i32(); cConns[(size_t) t] = r.i32(); cBytes[(size_t) t] = r.i32(); }
                std::vector<int> netBase((size_t) P + 1, 0), connBase((size_t) P + 1, 0);
                std::vector<long long> byteBase((size_t) P + 1, 0);
                for (int t = 0; t < P; t++) {
                    netBase[(size_t) t + 1] = netBase[(size_t) t] + cNets[(size_t) t];
                    connBase[(size_t) t + 1] = connBase[(size_t) t] + cConns[(size_t) t];
                    byteBase[(size_t) t + 1] = byteBase[(size_t) t] + cBytes[(size_t) t];
                }
                const size_t dataStart = r.pos();
                connections.resize((size_t) connBase[(size_t) P]);
                const uint8_t* dbase = r.data() + dataStart;
                const int T = std::max(1, std::min(parPart > 0 ? parPart : 1, P));
                parForN((size_t) P, T, [&](int, size_t lo, size_t hi) {
                    struct Cur {
                        const uint8_t* p;
                        int32_t i32() { uint32_t v; std::memcpy(&v, p, 4); p += 4; return (int32_t) v; }
                        int16_t i16() { uint16_t v; std::memcpy(&v, p, 2); p += 2; return (int16_t) v; }
                        uint8_t u8() { return *p++; }
                        float f32() { uint32_t v; std::memcpy(&v, p, 4); p += 4; float f; std::memcpy(&f, &v, 4); return f; }
                    };
                    auto key2id = [&](int a, int wv) { return (a < 0) ? -1 : keyToId.find(((long long) a << 20) | (wv & 0xFFFFF)); };
                    for (size_t t = lo; t < hi; t++) {
                        Cur c2{dbase + byteBase[t]};
                        int ci = connBase[t];
                        for (int k = 0; k < cNets[t]; k++) {
                            int ni = netBase[t] + k;
                            NetWrapper& nw = nets[(size_t) ni];
                            nw.xCenter = c2.f32(); nw.yCenter = c2.f32(); nw.doubleHpwl = c2.i16();
                            nw.connectionsSize = c2.i32();
                            { int a = c2.i32(), wv = c2.i32(); nw.sourceRnode = key2id(a, wv); }
                            int nc2 = c2.i32();
                            for (int cix = 0; cix < nc2; cix++) {
                                Connection& c = connections[(size_t) ci++];
                                c.netIdx = ni;
                                c.connId = c2.i32();
                                { int a = c2.i32(), wv = c2.i32(); c.sourceRnode = key2id(a, wv); }
                                { int a = c2.i32(), wv = c2.i32(); c.sinkRnode = key2id(a, wv); }
                                int na = c2.i32();
                                c.altSinks.resize((size_t) na);
                                for (int k2 = 0; k2 < na; k2++) { int a = c2.i32(), wv = c2.i32(); c.altSinks[(size_t) k2] = key2id(a, wv); }
                                c.xMinBB = c2.i16(); c.xMaxBB = c2.i16(); c.yMinBB = c2.i16(); c.yMaxBB = c2.i16();
                                c.hpwl = c2.i16();
                                c.crossSLRnorth = c2.u8() != 0;
                                c.crossSLRsouth = c2.u8() != 0;
                                c.routedAtInit = c2.u8() != 0;
                                int nr = c2.i32();
                                if (c.routedAtInit) { c.rnodes.resize((size_t) nr); for (int k2 = 0; k2 < nr; k2++) { int a = c2.i32(), wv = c2.i32(); c.rnodes[(size_t) k2] = key2id(a, wv); } }
                                else { for (int k2 = 0; k2 < nr; k2++) { (void) c2.i32(); (void) c2.i32(); } }
                            }
                        }
                    }
                });
                r.seek(dataStart + (size_t) byteBase[(size_t) P]);
                parNets = true;
            } else {
                r.seek(tablePos);
            }
        }
        if (!parNets)
        for (int ni = 0; ni < numNets; ni++) {
            NetWrapper& nw = nets[ni];
            nw.xCenter = r.f32(); nw.yCenter = r.f32(); nw.doubleHpwl = r.i16();
            nw.connectionsSize = r.i32();
            { int a = r.i32(), w = r.i32(); nw.sourceRnode = idByKey(a, w); }
            int nc = r.i32();
            for (int ci = 0; ci < nc; ci++) {
                Connection c;
                c.netIdx = ni;
                c.connId = r.i32();
                { int a = r.i32(), w = r.i32(); c.sourceRnode = idByKey(a, w); }
                { int a = r.i32(), w = r.i32(); c.sinkRnode = idByKey(a, w); }
                int na = r.i32();
                c.altSinks.resize(na);
                for (int k = 0; k < na; k++) { int a = r.i32(), w = r.i32(); c.altSinks[k] = idByKey(a, w); }
                c.xMinBB = r.i16(); c.xMaxBB = r.i16(); c.yMinBB = r.i16(); c.yMaxBB = r.i16();
                c.hpwl = r.i16();
                c.crossSLRnorth = r.u8() != 0; c.crossSLRsouth = r.u8() != 0;
                c.routedAtInit = r.u8() != 0;
                int nr = r.i32();
                // A3: initial route straight into working `rnodes` (kept only when routed-at-init).
                if (c.routedAtInit) { c.rnodes.resize(nr); for (int k = 0; k < nr; k++) { int a = r.i32(), w = r.i32(); c.rnodes[k] = idByKey(a, w); } }
                else { for (int k = 0; k < nr; k++) { (void) r.i32(); (void) r.i32(); } }
                connections.push_back(std::move(c));
            }
        }
        // PRESERVE section: design-specific preserved node keys (for the C++ device-model path)
        { int np = r.i32(); preserveSet.reserve((size_t) np * 2);
          for (int i = 0; i < np; i++) { int a = r.i32(), w = r.i32(); preserveSet.insert(((long long) a << 20) | (w & 0xFFFFF)); } }
        buildBloom();   // ready before any child interning during routing
        if (earlyTotal >= 0) {
            // prepass-early ROOT-CAUSE FIX (ledger 21): the early closure interned its nodes BEFORE
            // this section, so preserveReady was false and EVERY early node lost its preserved bit
            // (searches then ran straight through preserved-net resources: iter-1 overuse 138k vs
            // 66k). Replay the bits over the whole early population, bloom-prefiltered.
            auto _tp = std::chrono::steady_clock::now();
            std::atomic<long long> replayed{0};
            parForN((size_t) earlyTotal, std::max(1, parPart), [&](int, size_t lo, size_t hi) {
                for (size_t id = lo; id < hi; id++) {
                    if (ns[id].preserved) continue;
                    long long k = keyOf((int) id);
                    if (maybePreserved(k) && preserveSet.count(k)) {
                        ns[id].preserved = true;
                        initHotFromStatic((int) id); syncHotOcc((int) id);
                        replayed.fetch_add(1, std::memory_order_relaxed);
                    }
                }
            });
            std::fprintf(stderr, "[par] prepass-early: replayed %lld preserved bits over %d nodes in %.2fs\n",
                         replayed.load(), earlyTotal,
                         std::chrono::duration<double>(std::chrono::steady_clock::now() - _tp).count());
        }
        markSinkNodes();
        for (auto& c : connections) indirectAll.push_back((int)(&c - &connections[0]));
        for (auto& c : connections) {
            if (!c.hasAltSinks()) incrementUser(c.sinkRnode, c.netIdx);
            if (c.routedAtInit) {
                c.routed = true;   // rnodes already holds the initial route (loaded in A3)
                int sinkRnode = c.rnodes[0];
                int begin = 0, end = (int) c.rnodes.size();
                if (sinkRnode == c.sinkRnode && !c.hasAltSinks()) { begin = 1; end = (int) c.rnodes.size() - 1; }
                for (int i = begin; i < end; i++) incrementUser(c.rnodes[i], c.netIdx);
            } else c.routed = false;
        }
    }

    // Replay a golden connection path (from a Java .result, big-endian) arc-by-arc and report
    // the first arc the C++ accessibility filters reject. Pinpoints graph/filter divergences.
    void replayGolden(const std::string& resultPath, int targetConnId) {
        FILE* f = std::fopen(resultPath.c_str(), "rb");
        auto rd = [&]() { int b0=fgetc(f),b1=fgetc(f),b2=fgetc(f),b3=fgetc(f);
                          return (b0<<24)|(b1<<16)|(b2<<8)|b3; };
        rd();  // magic
        int count = rd();
        std::vector<int> goldenIds;  // node ids of golden path (sink->source)
        int connIdx = -1;
        for (int c = 0; c < count; c++) {
            int connId = rd(); int routed = fgetc(f); int nr = rd();
            std::vector<int> path;
            for (int i = 0; i < nr; i++) {
                int addr = rd(); int wire = rd();
                path.push_back(keyToId.find(((long long) addr << 20) | (wire & 0xFFFFF)));
            }
            if (connId == targetConnId) { goldenIds = path; (void)routed;
                // find the matching connection index
                for (size_t k = 0; k < connections.size(); k++) if (connections[k].connId == connId) connIdx = (int)k;
            }
        }
        std::fclose(f);
        if (connIdx < 0) { std::printf("replay: conn %d not found\n", targetConnId); return; }
        Connection& conn = connections[connIdx];
        std::printf("replay conn=%d golden path %zu nodes (sink->source); crossSLR=%d\n",
                    targetConnId, goldenIds.size(), (int)conn.isCrossSLR());
        // golden is sink->source; walk source->sink so parent precedes child
        for (int i = (int)goldenIds.size() - 1; i >= 1; i--) {
            int parent = goldenIds[i], child = goldenIds[i-1];
            if (parent == -1 || child == -1) {
                std::printf("  step %d: MISSING node in .rrt (parent=%d child=%d)\n", i, parent, child);
                continue;
            }
            // is child in parent's raw adjacency?
            bool inAdj = false;
            const NodeStatic& pn = ns[parent];
            for (int k = 0; k < pn.childCount; k++) if (childIds[pn.childStart + k] == child) { inAdj = true; break; }
            bool excluded = isExcluded(parent, child);
            // graph accessibility (must set prev/visited context minimally)
            dyn[child].prev = parent;
            bool accBox = isAccessible(child, conn);
            bool accGraph = graphIsAccessible(child, parent, conn);
            bool accSink = dyn[child].target ? true : (isAnyExclusiveSink(type[child]) ? isAccessibleSink(child, conn) : true);
            std::printf("  step %2d: P=%d(t%d e%d,%d) -> C=%d(t%d e%d,%d) inAdj=%d excl=%d box=%d graph=%d sink=%d  laguna=%d\n",
                        i, parent, (int)type[parent], getEndTileXCoordinate(parent), getEndTileYCoordinate(parent),
                        child, (int)type[child], getEndTileXCoordinate(child), getEndTileYCoordinate(child),
                        inAdj, excluded, accBox, accGraph, accSink, (int)ns[child].isLaguna);
        }
    }

    // ----------------------------------------------------------------- monotonicity stats
    // Route iteration 1 (all connections, real A*) and measure what fraction of the found paths are
    // MONOTONE: every step moves toward the sink (or stays) in each axis, never away. Validates the
    // "most routes are shortest/monotone" premise for a monotone/directed fast-path search.
    void printMonoStats() {
        sortConnections();
        routeIteration = 1;
        historicalCongestionFactor = cfg.historicalCongestionFactor;
        presentCongestionFactor = cfg.initialPresentCongestionFactor;
        wlWeight = cfg.wirelengthWeight;
        updatePresentCongestionCosts(presentCongestionFactor);
        long total = 0, sumLen = 0; long hist[9] = {0};   // hist[k] = #paths with exactly k backward steps (k>=8 bucketed)
        for (int idx : sortedIndirect) {
            Connection& c = connections[idx];
            if (c.abandoned) continue;
            routeIndirectConnection(idx);
            if (!c.routed || c.rnodes.size() < 2) continue;
            total++;
            int sx = getEndTileXCoordinate(c.sourceRnode), sy = getEndTileYCoordinate(c.sourceRnode);
            int kx = getEndTileXCoordinate(c.sinkRnode),   ky = getEndTileYCoordinate(c.sinkRnode);
            int wx = (kx > sx) - (kx < sx), wy = (ky > sy) - (ky < sy);
            long back = 0;                                 // per-step: a move that goes away from sink in X OR Y
            for (int i = (int) c.rnodes.size() - 1; i > 0; i--) {   // walk source -> sink
                int ax = getEndTileXCoordinate(c.rnodes[i]),   ay = getEndTileYCoordinate(c.rnodes[i]);
                int bx = getEndTileXCoordinate(c.rnodes[i-1]),  by = getEndTileYCoordinate(c.rnodes[i-1]);
                int dx = bx - ax, dy = by - ay;
                bool bk = (wx == 0 ? (dx != 0) : (dx * wx < 0)) || (wy == 0 ? (dy != 0) : (dy * wy < 0));
                if (bk) back++;
            }
            hist[back < 8 ? back : 8]++;
            sumLen += (long) c.rnodes.size();
        }
        std::printf("MONO_STATS routed=%ld  avg path len=%.1f\n", total, (double) sumLen / std::max(1L, total));
        long cum = 0;
        for (int k = 0; k <= 4; k++) { cum += hist[k];
            std::printf("  <=%d backward steps: %.1f%%  (exactly %d: %.1f%%)\n",
                        k, 100.0 * cum / std::max(1L, total), k, 100.0 * hist[k] / std::max(1L, total)); }
    }

    // ----------------------------------------------------------------- node / equivalence stats
    void printNodeStats() {
        long n = numNodes();
        long loc = 0, excl = 0, sll = 0, inacc = 0, other = 0, pinfeed = 0, laguna = 0, pinb = 0;
        for (int i = 0; i < n; i++) {
            RouteNodeType t = type[i];
            if (t == RouteNodeType::INACCESSIBLE) inacc++;
            else if (isAnyExclusiveSink(t)) excl++;
            else if (t == RouteNodeType::SUPER_LONG_LINE) sll++;
            else if (isAnyLocal(t)) loc++;
            else other++;
            if (ns[i].isPinfeed) pinfeed++;
            if (ns[i].isLaguna) laguna++;
            if (ns[i].isPinbounce) pinb++;
        }
        std::printf("NODE_STATS total=%ld\n", n);
        std::printf("  by role: nonLocal(general wires)=%ld  local=%ld  exclusiveSink(pins)=%ld  SLL=%ld  inaccessible=%ld\n",
                    other, loc, excl, sll, inacc);
        std::printf("  flags: pinfeed=%ld  pinbounce=%ld  laguna=%ld\n", pinfeed, pinb, laguna);
        // equivalent sink pins (pin swapping): connections whose sink has interchangeable alternatives
        long nc = (long) connections.size(), withAlt = 0, totAlt = 0; int maxAlt = 0;
        for (const auto& c : connections) {
            if (!c.altSinks.empty()) { withAlt++; totAlt += (long) c.altSinks.size();
                if ((int) c.altSinks.size() > maxAlt) maxAlt = (int) c.altSinks.size(); }
        }
        std::printf("  equivalent sinks: %ld/%ld connections have alt sinks (%.1f%%), avg %.2f alts (among those), max %d\n",
                    withAlt, nc, 100.0 * withAlt / std::max(1L, nc),
                    withAlt ? (double) totAlt / withAlt : 0.0, maxAlt);
    }

    // ----------------------------------------------------------------- heatmap dump
    // Emit per-tile grids: capacity (#RRG nodes ending in the tile), demand (sum of distinct-net
    // occupancy after a single iteration-1 route), and overuse (sum of occ-1 where occ>1). Lets us
    // draw node-density + utilization + congestion heatmaps.
    void dumpHeatmap(const std::string& prefix) {
        sortConnections();
        int W = 0, H = 0;
        for (int i = 0; i < numNodes(); i++) { if (ns[i].endX > W) W = ns[i].endX; if (ns[i].endY > H) H = ns[i].endY; }
        W++; H++;
        std::vector<int> cap((size_t) W * H, 0), dem((size_t) W * H, 0), ovr((size_t) W * H, 0);
        for (int i = 0; i < numNodes(); i++) { int x = ns[i].endX, y = ns[i].endY;
            if (x >= 0 && y >= 0 && x < W && y < H) cap[(size_t) y * W + x]++; }
        // iteration-1 route (all indirect connections once; occupancy accumulates, no congestion resolution)
        routeIteration = 1;
        historicalCongestionFactor = cfg.historicalCongestionFactor;
        presentCongestionFactor = cfg.initialPresentCongestionFactor;
        wlWeight = cfg.wirelengthWeight;
        updatePresentCongestionCosts(presentCongestionFactor);
        for (int idx : sortedIndirect) { if (!connections[idx].abandoned) routeIndirectConnection(idx); }
        for (int i = 0; i < numNodes(); i++) { int o = occCnt[i]; if (o <= 0) continue;
            int x = ns[i].endX, y = ns[i].endY; if (x < 0 || y < 0 || x >= W || y >= H) continue;
            dem[(size_t) y * W + x] += o; if (o > 1) ovr[(size_t) y * W + x] += (o - 1); }
        auto writeGrid = [&](const char* suf, std::vector<int>& gd) {
            FILE* f = std::fopen((prefix + suf).c_str(), "w");
            std::fprintf(f, "%d %d\n", W, H);
            for (int y = 0; y < H; y++) { for (int x = 0; x < W; x++) std::fprintf(f, "%s%d", x ? " " : "", gd[(size_t) y * W + x]); std::fprintf(f, "\n"); }
            std::fclose(f);
        };
        writeGrid("_cap.txt", cap); writeGrid("_dem.txt", dem); writeGrid("_ovr.txt", ovr);
        std::fprintf(stderr, "[heatmap] W=%d H=%d wrote %s_{cap,dem,ovr}.txt\n", W, H, prefix.c_str());
    }

    // ----------------------------------------------------------------- bbox stats
    void printBboxStats() {
        if (connections.empty()) { std::printf("no connections\n"); return; }
        int gMinX = INT32_MAX, gMinY = INT32_MAX, gMaxX = INT32_MIN, gMaxY = INT32_MIN;
        int minW = INT32_MAX, maxW = INT32_MIN, minH = INT32_MAX, maxH = INT32_MIN;
        long long minArea = (long long) 1 << 62, maxArea = -1;
        int minAW = 0, minAH = 0, maxAW = 0, maxAH = 0, n = 0;
        for (const auto& c : connections) {
            int w = c.xMaxBB - c.xMinBB, h = c.yMaxBB - c.yMinBB;
            gMinX = std::min(gMinX, (int) c.xMinBB); gMinY = std::min(gMinY, (int) c.yMinBB);
            gMaxX = std::max(gMaxX, (int) c.xMaxBB); gMaxY = std::max(gMaxY, (int) c.yMaxBB);
            minW = std::min(minW, w); maxW = std::max(maxW, w);
            minH = std::min(minH, h); maxH = std::max(maxH, h);
            long long a = (long long) w * h;
            if (a < minArea) { minArea = a; minAW = w; minAH = h; }
            if (a > maxArea) { maxArea = a; maxAW = w; maxAH = h; }
            n++;
        }
        std::printf("CONFIG extX=%d extY=%d enlarge=%d incX=%d incY=%d useBB=%d\n",
                    cfg.boundingBoxExtensionX, cfg.boundingBoxExtensionY, (int) cfg.enlargeBoundingBox,
                    cfg.extensionXIncrement, cfg.extensionYIncrement, (int) cfg.useBoundingBox);
        std::printf("BBOX_STATS connections=%d  (bboxes as loaded, before D0 tightening)\n", n);
        std::printf("  bbox-of-all-bboxes: [%d,%d] -> [%d,%d]   W=%d  H=%d\n",
                    gMinX, gMinY, gMaxX, gMaxY, gMaxX - gMinX, gMaxY - gMinY);
        std::printf("  width  (x-extent): min=%d  max=%d\n", minW, maxW);
        std::printf("  height (y-extent): min=%d  max=%d\n", minH, maxH);
        std::printf("  smallest-area bbox: W=%d x H=%d  (area=%lld)\n", minAW, minAH, minArea);
        std::printf("  largest-area  bbox: W=%d x H=%d  (area=%lld)\n", maxAW, maxAH, maxArea);
    }

    // ----------------------------------------------------------------- viz dump
    // Route a spatial sample of N connections with the real CPU A* (occupancy accumulates), recording
    // for each: source/sink tile, bbox, the ordered A* explored nodes, and the final path -- then emit a
    // JS data file the routing.html animation replays. Shows the real search fan-out + path forming.
    void dumpRouting(const std::string& outPath, int N) {
        sortConnections();
        routeIteration = 1;
        historicalCongestionFactor = cfg.historicalCongestionFactor;
        presentCongestionFactor = cfg.initialPresentCongestionFactor;
        wlWeight = cfg.wirelengthWeight;
        updatePresentCongestionCosts(presentCongestionFactor);

        int W = 0, H = 0;
        for (int i = 0; i < numNodes(); i++) { if (ns[i].endX > W) W = ns[i].endX; if (ns[i].endY > H) H = ns[i].endY; }

        // sample N connections spread across sortedIndirect, skipping tiny ones (nicer to watch)
        int total = (int) sortedIndirect.size();
        int stride = std::max(1, total / std::max(1, N * 3));
        std::vector<int> sample;
        for (int k = 0; k < total && (int) sample.size() < N; k += stride) {
            int idx = sortedIndirect[k];
            if (connections[idx].hpwl >= 6) sample.push_back(idx);
        }

        FILE* f = std::fopen(outPath.c_str(), "w");
        if (!f) { std::fprintf(stderr, "[dump] cannot open %s\n", outPath.c_str()); return; }
        std::fprintf(f, "const ROUTING_DATA={\"w\":%d,\"h\":%d,\"conns\":[\n", W + 1, H + 1);
        dumpMode = true;
        bool first = true;
        for (int idx : sample) {
            Connection& c = connections[idx];
            dumpExplored.clear();
            routeIndirectConnection(idx);      // real A*; push() fills dumpExplored; sets c.rnodes
            if (!c.routed || c.rnodes.empty()) continue;
            int sx = getEndTileXCoordinate(c.sourceRnode), sy = getEndTileYCoordinate(c.sourceRnode);
            int kx = getBeginTileXCoordinate(c.sinkRnode), ky = getBeginTileYCoordinate(c.sinkRnode);
            std::fprintf(f, "%s{\"src\":[%d,%d],\"sink\":[%d,%d],\"bb\":[%d,%d,%d,%d],\"path\":[",
                         first ? "" : ",\n", sx, sy, kx, ky, c.xMinBB, c.yMinBB, c.xMaxBB, c.yMaxBB);
            first = false;
            for (size_t i = 0; i < c.rnodes.size(); i++) {   // path is sink->source; reverse to source->sink
                int n = c.rnodes[c.rnodes.size() - 1 - i];
                std::fprintf(f, "%s[%d,%d]", i ? "," : "", getEndTileXCoordinate(n), getEndTileYCoordinate(n));
            }
            std::fprintf(f, "],\"exp\":[");
            for (size_t i = 0; i < dumpExplored.size(); i++) {
                int n = dumpExplored[i];
                std::fprintf(f, "%s[%d,%d]", i ? "," : "", getEndTileXCoordinate(n), getEndTileYCoordinate(n));
            }
            std::fprintf(f, "]}");
        }
        dumpMode = false;
        std::fprintf(f, "\n]};\n");
        std::fclose(f);
        std::fprintf(stderr, "[dump] wrote %s (device %dx%d, %d connections)\n", outPath.c_str(), W + 1, H + 1, (int) sample.size());
    }

    // ----------------------------------------------------------------- write .result
    #include "real_router_hooks.inc"
    void writeResult(const std::string& path) {
        FILE* f = std::fopen(path.c_str(), "wb");
        auto be32 = [&](int v) {
            unsigned u = (unsigned)v;
            std::fputc((u >> 24) & 0xFF, f); std::fputc((u >> 16) & 0xFF, f);
            std::fputc((u >> 8) & 0xFF, f); std::fputc(u & 0xFF, f);
        };
        be32(0x52575231);                  // 'RWR1'
        be32((int)indirectAll.size());
        for (int idx : indirectAll) {
            Connection& c = connections[idx];
            be32(c.connId);
            std::fputc(c.routed ? 1 : 0, f);
            be32((int)c.rnodes.size());
            for (int rn : c.rnodes) { be32(ns[rn].tileAddr); be32(nc[rn].wireIndex); }
        }
        std::fclose(f);
    }

    // Same big-endian .result format, but to an in-memory buffer (for the JNI path).
    // Post-result bulk release: O(1) munmap-scale frees of the giant per-node arrays once the
    // result bytes are serialized (the JVM needs the memory back for inject/finalize on 100M-node
    // cases). Small-object structures (userOverflow maps, children cache vectors) stay leaked --
    // freeing those is the ~5s cost the leak avoids.
    void releaseBulkArrays() {
        auto drop = [](auto& v) { typename std::remove_reference<decltype(v)>::type().swap(v); };
        drop(childIds); drop(dyn); drop(hot); drop(ns); drop(nc); drop(type);
        drop(occCnt); drop(ownerNet); drop(ownerCnt); drop(created); drop(overUsed);
        drop(deadEnd); drop(isSinkNode); drop(rawFetched); drop(dirtyStamp);
#ifdef WITH_CUDA
        drop(floodCong); drop(floodCongShare); drop(shareMark);
#endif
    }

    std::vector<uint8_t> writeResultToVector() {
        // Parallel (per-connection independent): each thread serializes a contiguous range of
        // indirectAll into its own buffer, concatenated in order. Capped at 32 threads (global rule).
        int n = (int) indirectAll.size();
        int T = std::min(32, std::max(1, (int) std::thread::hardware_concurrency()));
        if (n < 4096) T = 1;
        std::vector<std::vector<uint8_t>> parts(T);
        auto worker = [&](int t) {
            std::vector<uint8_t>& buf = parts[t];
            auto be = [&](int v) { unsigned u = (unsigned) v;
                buf.push_back((u>>24)&0xFF); buf.push_back((u>>16)&0xFF); buf.push_back((u>>8)&0xFF); buf.push_back(u&0xFF); };
            long lo = (long) t * n / T, hi = (long) (t + 1) * n / T;
            for (long i = lo; i < hi; i++) {
                Connection& c = connections[indirectAll[i]];
                be(c.connId); buf.push_back(c.routed ? 1 : 0); be((int) c.rnodes.size());
                for (int rn : c.rnodes) { be(ns[rn].tileAddr); be(nc[rn].wireIndex); }
            }
        };
        std::vector<std::thread> th;
        for (int t = 0; t < T; t++) th.emplace_back(worker, t);
        for (auto& x : th) x.join();
        std::vector<uint8_t> out;
        size_t total = 8; for (auto& p : parts) total += p.size();
        out.reserve(total);
        auto be32 = [&](int v) { unsigned u = (unsigned) v;
            out.push_back((u>>24)&0xFF); out.push_back((u>>16)&0xFF); out.push_back((u>>8)&0xFF); out.push_back(u&0xFF); };
        be32(0x52575231); be32(n);
        for (auto& p : parts) out.insert(out.end(), p.begin(), p.end());
        return out;
    }
};

// Phase-1 parallel prototype: thread-local search scratch (definitions for the static members).
thread_local Router::NodeDyn* Router::tl_dyn = nullptr;
thread_local Router::SparseLabels* Router::tl_sparse = nullptr;
thread_local std::vector<Router::DaryPQ::E>* Router::tl_pq = nullptr;
thread_local long Router::tl_seq = 0;
thread_local bool Router::tl_deferCommit = false;
thread_local int Router::tl_wid = -1;
thread_local long long Router::tl_pushes = 0;
thread_local long long Router::lastPops = 0;
thread_local float Router::lastFoundLb = -1.0f;
thread_local bool Router::lastAborted = false;
thread_local uint32_t Router::tl_dirtyEpoch = 0;
thread_local std::vector<int> Router::tl_dirtyList;
#ifdef WITH_CUDA
thread_local std::vector<float> Router::tl_dscA;
thread_local std::vector<float> Router::tl_dscB;
#endif

int main(int argc, char** argv) {
    // One-time .dmc generation (mmap'able DeviceModel image; small cases map it in ~ms):
    //   rwroute_cpp --gen-dmc [rdv] [atc] [out.dmc]
    if (argc >= 2 && std::string(argv[1]) == "--gen-dmc") {
        const char* rdv = argc > 2 ? argv[2] : "/tmp/xcvu13p.rdv";
        const char* atc = argc > 3 ? argv[3] : "/tmp/xcvu13p.atc";
        const char* out = argc > 4 ? argv[4] : "/tmp/xcvu13p.dmc";
        dev::DeviceModel dm;
        double bt = dm.load(rdv, atc);
        if (bt < 0) { std::fprintf(stderr, "[gen-dmc] build from %s/%s failed\n", rdv, atc); return 1; }
        double wt = dm.dumpTo(out, rdv, atc);
        if (wt < 0) { std::fprintf(stderr, "[gen-dmc] write %s failed\n", out); return 1; }
        std::printf("[gen-dmc] %s: build=%.2fs write=%.2fs nNodes=%ld\n", out, bt, wt, (long) dm.nNodes);
        return 0;
    }
    // Data-integrity check: compare RAM-built model vs mmap'ed .dmc packet-for-packet.
    //   rwroute_cpp --dmc-selftest [rdv] [atc] [dmc]
    if (argc >= 2 && std::string(argv[1]) == "--dmc-selftest") {
        const char* rdv = argc > 2 ? argv[2] : "/tmp/xcvu13p.rdv";
        const char* atc = argc > 3 ? argv[3] : "/tmp/xcvu13p.atc";
        const char* dmc = argc > 4 ? argv[4] : "/tmp/xcvu13p.dmc";
        dev::DeviceModel ram, mm;
        if (ram.load(rdv, atc) < 0) { std::fprintf(stderr, "ram build failed\n"); return 1; }
        if (mm.loadMmap(dmc, rdv, atc) < 0) { std::fprintf(stderr, "mmap failed\n"); return 1; }
        if (ram.nTiles != mm.nTiles || ram.nNodes != mm.nNodes || ram.totW != mm.totW || ram.nSrc != mm.nSrc) {
            std::fprintf(stderr, "META MISMATCH tiles %ld/%ld nodes %ld/%ld totW %ld/%ld nSrc %ld/%ld\n",
                (long)ram.nTiles,(long)mm.nTiles,(long)ram.nNodes,(long)mm.nNodes,
                (long)ram.totW,(long)mm.totW,(long)ram.nSrc,(long)mm.nSrc); return 1; }
        long long bad = 0, checked = 0, abad = 0;
        std::vector<int> a, b;
        for (int64_t i = 0; i < ram.nNodes; i += 97) {   // ~1M sampled nodes, stride-spread
            long key = (long) ram.nrecP[i].baseKey;
            ram.getChildrenPacked(key, a); mm.getChildrenPacked(key, b);
            int cnt = a[0];
            if (b[0] != cnt || memcmp(a.data(), b.data(), sizeof(int)*(1+(size_t)cnt*11)) != 0) bad++;
            int r4[4], m4[4];
            bool rr = ram.getNodeAttr((int)(key >> 20), (int)(key & 0xFFFFF), r4);
            bool mr = mm.getNodeAttr((int)(key >> 20), (int)(key & 0xFFFFF), m4);
            if (!rr || !mr || memcmp(r4, m4, sizeof r4) != 0 ||
                r4[0] != ram.nrecP[i].type || r4[3] != ram.nrecP[i].len) abad++;
            checked++;
        }
        std::printf("[dmc-selftest] checked=%lld childMismatch=%lld attrMismatch=%lld -> %s\n",
                    checked, bad, abad, (bad || abad) ? "FAIL" : "OK");
        return (bad || abad) ? 1 : 0;
    }
    if (argc < 3) {
        std::fprintf(stderr, "USAGE: rwroute_cpp <input.rrt> <output.result>\n");
        std::fprintf(stderr, "       rwroute_cpp --gen-dmc [rdv] [atc] [out.dmc]\n");
        return 1;
    }
    using clk = std::chrono::steady_clock;
    auto ms = [](clk::time_point a, clk::time_point b) {
        return std::chrono::duration_cast<std::chrono::milliseconds>(b - a).count();
    };
    auto t0 = clk::now();
    btrace::init();
    Router router;
    router.load(argv[1]); auto b_frontier_graph = [&](const char* stage) { uint64_t edgeSum=0; int maxDegree=0; for(const auto& a:router.ns) { edgeSum+=(uint64_t)a.childCount; maxDegree=std::max(maxDegree,a.childCount); } std::fprintf(stderr,"FRONTIER_GRAPH stage=%s entry_bytes=%zu heap_arity=%d nodes=%zu edges=%zu edge_sum=%llu max_degree=%d lazy=%d\n",stage,sizeof(Router::DaryPQ::E),router.heapArity,router.ns.size(),router.childIds.size(),(unsigned long long)edgeSum,maxDegree,(int)router.lazy); }; b_frontier_graph("before");
    auto t1 = clk::now();
    std::printf("INFO: [cpp] loaded %d nodes, %zu nets, %zu connections  (load .rrt: %ld ms)\n",
                router.numNodes(), router.nets.size(), router.connections.size(), ms(t0, t1));
    std::fflush(stdout);
    // Debug mode: rwroute_cpp <in.rrt> --replay <golden.result> <connId>
    if (argc >= 5 && std::string(argv[2]) == "--replay") {
        router.replayGolden(argv[3], std::atoi(argv[4]));
        return 0;
    }
    // Visualization dump: rwroute_cpp <in.rrt> --dump <out.js> [N]
    if (argc >= 4 && std::string(argv[2]) == "--dump") {
        router.dumpRouting(argv[3], argc >= 5 ? std::atoi(argv[4]) : 100);
        return 0;
    }
    // Bounding-box stats: rwroute_cpp <in.rrt> --bbstats
    if (argc >= 3 && std::string(argv[2]) == "--bbstats") {
        router.printBboxStats();
        return 0;
    }
    // Per-connection bbox W,H to stdout (CSV) for histograms: rwroute_cpp <in.rrt> --bbdump > f.csv
    if (argc >= 3 && std::string(argv[2]) == "--bbdump") {
        for (const auto& c : router.connections)
            std::printf("%d,%d\n", c.xMaxBB - c.xMinBB, c.yMaxBB - c.yMinBB);
        return 0;
    }
    // Per-tile heatmap grids: rwroute_cpp <in.rrt> --heatmap <prefix>
    if (argc >= 4 && std::string(argv[2]) == "--heatmap") {
        router.dumpHeatmap(argv[3]);
        return 0;
    }
    // Node / equivalence stats: rwroute_cpp <in.rrt> --nodestats
    if (argc >= 3 && std::string(argv[2]) == "--nodestats") {
        router.printNodeStats();
        return 0;
    }
    // Path monotonicity stats (iter-1): rwroute_cpp <in.rrt> --monostats
    if (argc >= 3 && std::string(argv[2]) == "--monostats") {
        router.printMonoStats();
        return 0;
    }
    bprof::startSampling();
    auto b_route_start = clk::now();
    router.routeIndirectConnectionsIteratively();
    auto t2 = clk::now();
    bprof::stopSampling();
    btrace::flush();
    b_frontier_graph("after"); router.writeResult(argv[2]);
    auto t3 = clk::now();
    auto b_ms = [](auto a, auto b) { return std::chrono::duration<double,std::milli>(b-a).count(); };
    bprof::report(b_ms(t0,t1), b_ms(b_route_start,t2), b_ms(t2,t3));
    std::printf("INFO: [cpp] timing: load=%ld ms, route=%ld ms, write .result=%ld ms, total=%ld ms\n",
                ms(t0, t1), ms(t1, t2), ms(t2, t3), ms(t0, t3));
    return 0;
}

#ifdef WITH_JNI
// In-process (single JVM) entry: Java passes the serialized problem (same .rrt bytes, in
// memory) and gets back the .result bytes — no disk, no second device load.
// Java: native byte[] routeNative(byte[] problem);
static dev::DeviceModel* g_dm = nullptr;  // device-static C++ model, built once per JVM
static std::thread g_buildThread;          // background prewarm (device build is design-independent)
static std::atomic<bool> g_buildStarted{false};
static std::atomic<bool> g_built{false};
static std::atomic<bool> g_smallCase{false};   // input DCP <=10MB (set in prewarmDevice)

static void buildDeviceModel() {
    g_dm = new dev::DeviceModel();
    const char* rdv = std::getenv("RWDEV_RDV"); const char* atc = std::getenv("RWDEV_ATC");
    double dt = g_dm->load(rdv ? rdv : "/tmp/xcvu13p.rdv", atc ? atc : "/tmp/xcvu13p.atc");
    fprintf(stderr, "INFO: [cpp-jni] C++ device built from compact %.2fs (nNodes=%ld)\n", dt, (long) g_dm->nNodes);
    g_built.store(true);
}

// prepass-early state: Java hands over projected pin INT-node keys + per-net pin rects right after
// getUnroutedPins; the closure/CSR build then runs on this thread DURING Java initialize
// (~11s window vs ~8-11s prepass -> fully hidden). Compact-device mode only.
static Router* g_earlyRouter = nullptr;
static std::thread g_earlyThread;
static std::atomic<bool> g_earlyStarted{false};

// Kick off the (design-independent) device build in a background thread so its ~12s is HIDDEN behind
// Java's readCheckpoint + target building. Call from main() before readCheckpoint.
extern "C" JNIEXPORT void JNICALL
Java_com_xilinx_rapidwright_rwroute_RWRouteCppJni_prewarmDevice(JNIEnv*, jclass, jlong dcpBytes) {
    const char* useDev = std::getenv("RWDEV");
    if (!(useDev && std::atoi(useDev))) return;
    if (g_buildStarted.exchange(true)) return;
    if (dcpBytes > 0 && dcpBytes <= 10000000LL) {
        g_smallCase.store(true);
        // SMALL case: the 12.5s RAM build can never hide behind a ~2s read, so mmap the .dmc image
        // instead (~ms; lazy paging touches only the design's slice). No .dmc / stale .dmc -> reset
        // state so routeNative falls back to JNI-B exactly as before. RW_DMC=0 disables.
        const char* en = std::getenv("RW_DMC");
        const char* dmc = std::getenv("RWDEV_DMC"); if (!dmc) dmc = "/tmp/xcvu13p.dmc";
        const char* rdv = std::getenv("RWDEV_RDV"); const char* atc = std::getenv("RWDEV_ATC");
        if (!(en && std::atoi(en) == 0)) {
            auto* dm = new dev::DeviceModel();
            double dt = dm->loadMmap(dmc, rdv ? rdv : "/tmp/xcvu13p.rdv", atc ? atc : "/tmp/xcvu13p.atc");
            if (dt >= 0) {
                g_dm = dm; g_built.store(true);
                fprintf(stderr, "INFO: [cpp-jni] C++ device mmap'ed from %s in %.3fs (nNodes=%ld)\n",
                        dmc, dt, (long) g_dm->nNodes);
                return;
            }
            delete dm;
            fprintf(stderr, "INFO: [cpp-jni] no usable .dmc (%s) -> JNI-B device (gen: rwroute_cpp --gen-dmc)\n", dmc);
        }
        g_buildStarted.store(false);   // as if never called: useCompact stays false
        return;
    }
    // BIG cases: prefer the mmap image too (RW_DMC_BIG=0 opts out). Same packets as the RAM build
    // (--dmc-selftest: 1.07M sampled nodes, 0 child/attr mismatches), but ~10GB of anon RSS becomes
    // reclaimable file-backed pages (OOM margin under co-tenant storms -- the T=36 sample died to a
    // global OOM at 70.7GB anon) and the 12.5s 47-thread build disappears. Absent/stale -> RAM build.
    {
        const char* en = std::getenv("RW_DMC_BIG");
        const char* dmc = std::getenv("RWDEV_DMC"); if (!dmc) dmc = "/tmp/xcvu13p.dmc";
        const char* rdv = std::getenv("RWDEV_RDV"); const char* atc = std::getenv("RWDEV_ATC");
        // OPT-IN only (RW_DMC_BIG=1): under co-tenant memory pressure the 9GB mapping THRASHES
        // (file pages evict + re-fault; k_300 went ~90s -> >10min at 21GB avail). Default stays
        // the RAM build; the RAM-gated T=36 watcher opts in (>=90GB guaranteed there).
        if (en && std::atoi(en) == 1) {
            auto* dm = new dev::DeviceModel();
            double dt = dm->loadMmap(dmc, rdv ? rdv : "/tmp/xcvu13p.rdv", atc ? atc : "/tmp/xcvu13p.atc");
            if (dt >= 0) {
                g_dm = dm; g_built.store(true);
                fprintf(stderr, "INFO: [cpp-jni] C++ device mmap'ed from %s in %.3fs (big case; nNodes=%ld)\n",
                        dmc, dt, (long) g_dm->nNodes);
            } else {
                delete dm;
                g_buildThread = std::thread(buildDeviceModel);
            }
        } else {
            g_buildThread = std::thread(buildDeviceModel);
        }
    }
    // prepass-fulldev (RW_PREPASS_FULLDEV=0 disables; RW_PREPASS_EARLY=0 also disables): for the
    // 20per-class (input DCP in [125,250)MB -- a band only THEIA_20per occupies among the 13 cases;
    // k_800=112MB below, 50per=289MB above) the pin cover is ~the whole device, so adopt the device
    // model directly as the routing graph right after it is built -- the whole prepass hides behind
    // readCheckpoint+preprocess+initialize instead of overflowing its old init window by ~12s.
    // Other cases keep the pin-cover prepass-early path bit-identically (Java mirrors this band and
    // skips its seed gather; the g_earlyStarted exchange below also makes prepassEarlyNative a no-op).
    const char* pf = std::getenv("RW_PREPASS_FULLDEV");
    const char* pe = std::getenv("RW_PREPASS_EARLY");
    bool fullDev = (!pf || std::atoi(pf) != 0) && !(pe && std::atoi(pe) == 0)
                   && dcpBytes >= 125000000LL && dcpBytes < 250000000LL;
    if (fullDev && !g_earlyStarted.exchange(true)) {
        g_earlyRouter = new Router();
        if (!std::getenv("RW_PAR_PART"))
            g_earlyRouter->parPart = (int) std::min((unsigned) rwMaxThreads(), std::max(1u, std::thread::hardware_concurrency()));
        g_earlyThread = std::thread([]() {
            while (!g_built.load()) std::this_thread::sleep_for(std::chrono::milliseconds(5));
            if (g_buildThread.joinable()) g_buildThread.join();
            g_earlyRouter->fetchChildrenPacked = [](long key, std::vector<int>& out) { g_dm->getChildrenPacked(key, out); };
            g_earlyRouter->fetchParSafe = true;
            auto t0 = std::chrono::steady_clock::now();
            g_earlyRouter->prepassFullDevice(g_dm);
            fprintf(stderr, "INFO: [cpp-jni] prepass-fulldev done in %.2fs (device adoption, hidden behind read+init)\n",
                    std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
        });
    }
}

// O(1) RouteNodeInfo fields from the mmap'ed .dmc: {typeOrdinal, endX, endY, length}.
// Small-case netCreate uses this to bypass Java's fabric-wire lazy tables entirely.
// Thread-safe (read-only arrays); false when the node isn't modeled (caller falls back).
extern "C" JNIEXPORT jboolean JNICALL
Java_com_xilinx_rapidwright_rwroute_RWRouteCppJni_dmActive(JNIEnv*, jclass) {
    return (g_built.load() && g_dm && g_dm->nodeIdOfP) ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_xilinx_rapidwright_rwroute_RWRouteCppJni_getNodeRec(JNIEnv* env, jclass,
                                                             jint tileAddr, jint wire, jintArray out4) {
    if (!g_built.load() || !g_dm) return JNI_FALSE;
    int v[4];
    if (!g_dm->getNodeAttr((int) tileAddr, (int) wire, v)) return JNI_FALSE;
    env->SetIntArrayRegion(out4, 0, 4, (const jint*) v);
    return JNI_TRUE;
}

extern "C" JNIEXPORT void JNICALL
Java_com_xilinx_rapidwright_rwroute_RWRouteCppJni_prepassEarlyNative(JNIEnv* env, jclass,
                                                                     jlongArray jkeys, jintArray jrects) {
    const char* useDev = std::getenv("RWDEV");
    if (!(useDev && std::atoi(useDev)) || !g_buildStarted.load()) return;
    if (g_earlyStarted.exchange(true)) return;
    auto* keys = new std::vector<long long>((size_t) env->GetArrayLength(jkeys));
    env->GetLongArrayRegion(jkeys, 0, (jsize) keys->size(), reinterpret_cast<jlong*>(keys->data()));
    auto* rects = new std::vector<int>((size_t) env->GetArrayLength(jrects));
    env->GetIntArrayRegion(jrects, 0, (jsize) rects->size(), reinterpret_cast<jint*>(rects->data()));
    g_earlyRouter = new Router();
    if (!std::getenv("RW_PAR_PART"))
        g_earlyRouter->parPart = std::min((unsigned) rwMaxThreads(), std::max(1u, std::thread::hardware_concurrency()));
    g_earlyThread = std::thread([keys, rects]() {
        while (!g_built.load()) std::this_thread::sleep_for(std::chrono::milliseconds(5));
        if (g_buildThread.joinable()) g_buildThread.join();
        g_earlyRouter->fetchChildrenPacked = [](long key, std::vector<int>& out) { g_dm->getChildrenPacked(key, out); };
        g_earlyRouter->fetchParSafe = true;
        auto t0 = std::chrono::steady_clock::now();
        g_earlyRouter->prepassEarly(*keys, *rects);
        fprintf(stderr, "INFO: [cpp-jni] prepass-early done in %.2fs (seeds=%zu rects=%zu, hidden behind init)\n",
                std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count(),
                keys->size(), rects->size() / 4);
        delete keys; delete rects;
    });
}

extern "C" JNIEXPORT jbyteArray JNICALL
Java_com_xilinx_rapidwright_rwroute_RWRouteCppJni_routeNative(JNIEnv* env, jobject self,
                                                             jbyteArray problem) {
    auto _tg = std::chrono::steady_clock::now();
    jsize n = env->GetArrayLength(problem);
    // Heap-allocate and INTENTIONALLY LEAK buf/router/out: the JVM only injects + writeCheckpoints after
    // this returns, then the process exits, so the OS reclaims everything for free. Destroying the Router
    // (per-node vectors/child caches sized to ~12M interned nodes = millions of small frees) otherwise
    // costs ~5s that Java's native-route timer would charge us. Leaking removes it entirely.
    auto* bufp = new std::vector<uint8_t>((size_t) n);
    env->GetByteArrayRegion(problem, 0, n, reinterpret_cast<jbyte*>(bufp->data()));
    if (g_earlyThread.joinable()) {                    // prepass-early in flight: wait (usually already done)
        auto _tw = std::chrono::steady_clock::now();
        g_earlyThread.join();
        fprintf(stderr, "INFO: [cpp-jni] prepass-early residual wait=%.2fs\n",
                std::chrono::duration<double>(std::chrono::steady_clock::now() - _tw).count());
    }
    Router& router = g_earlyRouter ? *g_earlyRouter : *new Router();
    // JNI production default: partition-parallel ON (RW_PAR_PART overrides; 0 disables). The
    // JNI-callback device self-disables in routeCpuLoop (fetchParSafe gate). Must be set BEFORE
    // loadLazy -- the node-array reserve is deeper when parallel interning is possible.
    // SMALL cases (<=10MB input) bank parPart=0: measured on RLE_BlobMerging (2026-07-11), the
    // lazy->eager prepass costs 0.9-1.4s while RPTT's iteration walls equal serial's (34 tiny
    // leaves, critical path = biggest leaf), and the closure materializes 1.54M nodes vs 537k
    // lazily -- serial-compact routes in 2.35s vs 3.4s. Explicit RW_PAR_PART still wins.
    if (!std::getenv("RW_PAR_PART"))
        router.parPart = g_smallCase.load() ? 0
                       : std::min((unsigned) rwMaxThreads(), std::max(1u, std::thread::hardware_concurrency()));
    rw::BinReader r(bufp->data(), bufp->size());
    fprintf(stderr, "INFO: [cpp-jni] getProblemBytes+ctor(%.0fMB)=%.2fs\n", n / 1e6,
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _tg).count());
    auto _tl = std::chrono::steady_clock::now();
    router.loadLazy(r);   // also fills router.preserveSet (PRESERVE section)
    fprintf(stderr, "INFO: [cpp-jni] loadLazy(deserialize)=%.2fs\n",
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _tl).count());

    // Device source for getChildren: env RWDEV=1 -> pure-C++ device model (no per-node JNI);
    // else the JNI getChildrenPacked callback. The C++ model is device-static -> built once.
    // ADAPTIVE: use the compact C++ device IF its background build finished during readCheckpoint+init
    // (big cases hide the ~12s build for free). If not finished within a short grace, the case is too
    // small to hide the build -> fall back to JNI-B (no build, ~par with Java). No per-case build on path.
    auto _tds = std::chrono::steady_clock::now();
    const char* useDev = std::getenv("RWDEV");
    bool useCompact = false;
    if (useDev && std::atoi(useDev) && g_buildStarted.load()) {
        // Prewarm only fires for BIG cases (size-gated in Java). Those ALWAYS benefit from the compact
        // device: the build (~12s, mostly hidden behind read+init) costs FAR less than JNI-B's per-node
        // Java-callback overhead (26s+ of route on k_100). So WAIT for the build (join) instead of giving
        // up to JNI-B on a short grace. Keep a generous safety cap so a pathological hang can't deadlock.
        auto _tj = std::chrono::steady_clock::now(); const double SAFETY = 60.0;
        while (!g_built.load() && std::chrono::duration<double>(std::chrono::steady_clock::now() - _tj).count() < SAFETY)
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        double waited = std::chrono::duration<double>(std::chrono::steady_clock::now() - _tj).count();
        if (g_built.load()) { if (g_buildThread.joinable()) g_buildThread.join(); useCompact = true;
            fprintf(stderr, "INFO: [cpp-jni] device=COMPACT (prewarm; waited %.2fs for build)\n", waited); }
        else { if (g_buildThread.joinable()) g_buildThread.detach();
            fprintf(stderr, "INFO: [cpp-jni] device=JNI-B (build exceeded %.0fs safety cap!)\n", SAFETY); }
    }
    if (useCompact) {
        router.fetchChildrenPacked = [](long key, std::vector<int>& out) { g_dm->getChildrenPacked(key, out); };
        router.fetchParSafe = true;   // DeviceModel::getChildrenPacked is read-only -> worker-thread safe
    } else {
        jclass cls = env->GetObjectClass(self);
        jmethodID mid = env->GetMethodID(cls, "getChildrenPacked", "(J)[I");
        router.fetchChildrenPacked = [env, self, mid](long key, std::vector<int>& out) {
            jintArray arr = (jintArray) env->CallObjectMethod(self, mid, (jlong) key);
            jsize len = env->GetArrayLength(arr);
            out.resize((size_t) len);
            if (len > 0) env->GetIntArrayRegion(arr, 0, len, out.data());
            env->DeleteLocalRef(arr);
        };
    }
    fprintf(stderr, "INFO: [cpp-jni] device-setup(getenv+join+lambda)=%.2fs\n",
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _tds).count());
    auto _rt0 = std::chrono::steady_clock::now();
    router.routeIndirectConnectionsIteratively();
    double _routeSecs = std::chrono::duration<double>(std::chrono::steady_clock::now() - _rt0).count();
    fprintf(stderr, "INFO: [cpp-jni] route=%.2fs  JNI-device=%.2fs (%ld calls, %.1f%% of route)  pure-algo=%.2fs  nodes=%zu/cap=%zu\n",
            _routeSecs, router.jniDeviceSecs, router.jniDeviceCalls,
            100.0 * router.jniDeviceSecs / _routeSecs, _routeSecs - router.jniDeviceSecs,
            router.ns.size(), router.ns.capacity());
    auto _tw = std::chrono::steady_clock::now();
    auto* outp = new std::vector<uint8_t>(router.writeResultToVector());  // leaked (see above)
    std::vector<uint8_t>& out = *outp;
    fprintf(stderr, "INFO: [cpp-jni] writeResult(serialize, parallel)=%.2fs\n",
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _tw).count());
    // The result vector is now self-contained: release the router's BULK arrays (tens of GB on
    // 100M-node cases) so the JVM's inject/finalize phase has headroom. swap-clear = O(1) munmap
    // per vector; the slow-to-destruct small-object structures (userOverflow etc.) stay leaked.
    // THEIA_50per crashed here without this: NewByteArray(700MB+) returned NULL beside a 65GB
    // native heap (G1 humongous alloc failure) and the unchecked region-copy SEGV'd the JVM.
    // GATED to giant cases only: with release unconditionally on, jpeg went probabilistically
    // corrupt downstream (812 null PIPs / 523 UNROUTED with bit-identical result bytes; serial
    // fixRoutes did not help -> release is the only delta vs the clean 02:19 build). Mechanism
    // not yet root-caused; small/medium cases stay on the многократно-validated no-release path.
    if (router.numNodes() > 90000000) router.releaseBulkArrays();

    auto _tm = std::chrono::steady_clock::now();
    if (out.size() > (size_t) 1900000000) {
        // JNI byte[] hard limit is 2^31-1: THEIA_50per's result is 2.58GB (jsize went negative ->
        // NegativeArraySizeException / SEGV). Spill to a temp file and hand Java a tiny sentinel
        // [u32 'RRTF'][u32 pathLen][path...]; injectResult switches to positional-read mode.
        char path[128];
        snprintf(path, sizeof(path), "/tmp/rwroute_result_%d.bin", (int) getpid());
        FILE* f = fopen(path, "wb");
        if (!f || fwrite(out.data(), 1, out.size(), f) != out.size()) {
            fprintf(stderr, "FATAL: [cpp-jni] result spill to %s failed\n", path);
            if (f) fclose(f);
            return nullptr;
        }
        fclose(f);
        uint32_t plen = (uint32_t) strlen(path);
        std::vector<uint8_t> hdr(8 + plen);
        hdr[0] = 'R'; hdr[1] = 'R'; hdr[2] = 'T'; hdr[3] = 'F';
        hdr[4] = (uint8_t) (plen >> 24); hdr[5] = (uint8_t) (plen >> 16);
        hdr[6] = (uint8_t) (plen >> 8); hdr[7] = (uint8_t) plen;
        memcpy(hdr.data() + 8, path, plen);
        jbyteArray sent = env->NewByteArray((jsize) hdr.size());
        env->SetByteArrayRegion(sent, 0, (jsize) hdr.size(), reinterpret_cast<const jbyte*>(hdr.data()));
        fprintf(stderr, "INFO: [cpp-jni] result spilled to %s (%.0fMB, > JNI 2GB array limit)\n",
                path, out.size() / 1e6);
        return sent;
    }
    jbyteArray result = env->NewByteArray((jsize) out.size());
    if (result == nullptr) {
        fprintf(stderr, "FATAL: [cpp-jni] NewByteArray(%zu bytes) failed (JVM heap exhausted)\n", out.size());
        return nullptr;   // pending OutOfMemoryError surfaces in Java instead of a SEGV
    }
    env->SetByteArrayRegion(result, 0, (jsize) out.size(), reinterpret_cast<const jbyte*>(out.data()));
    fprintf(stderr, "INFO: [cpp-jni] marshalResult(%.0fMB)=%.2fs\n", out.size() / 1e6,
            std::chrono::duration<double>(std::chrono::steady_clock::now() - _tm).count());
    return result;
}
#endif
