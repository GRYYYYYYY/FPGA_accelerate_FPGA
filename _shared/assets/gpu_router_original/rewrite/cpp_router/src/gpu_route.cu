  // GPU detailed-routing engine (CUDA).
//   G0: keep the static RRG resident on the device + verify the upload.
//   G1: per-connection directed A* within the bbox -> sink-reach coverage gate.
//   G2: + blocked-code gating (preserved / exclusive-sink-of-another-net) + length cost term +
//       PATH extraction (backtrack the per-connection prev chain) so the GPU produces usable routes.
// One thread per connection; per-connection scratch is a strided region owned exclusively by the
// thread (no sharing => no atomics). Mirrors gpu_bbox.cu conventions (extern "C", error-checked CUDA,
// cudaDeviceReset on shutdown).
#include <cuda_runtime.h>
#include <algorithm>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>

namespace {
// Resident static graph (uploaded once by gpuRouteInit, freed by gpuRouteShutdown).
int    g_numNodes = 0;
long   g_numEdges = 0;
int*   d_adjOff   = nullptr;   // [numNodes+1] CSR offsets
int*   d_adjList  = nullptr;   // [numEdges]  CSR children
short* d_endX     = nullptr;   // [numNodes]  end-tile X
short* d_endY     = nullptr;   // [numNodes]  end-tile Y
float* d_baseCost = nullptr;   // [numNodes]  base (wirelength) cost
short* d_length   = nullptr;   // [numNodes]  node length (wirelength term)
unsigned char* d_blocked = nullptr;  // [numNodes] 0=usable, 1=hard-blocked, 2=exclusive-sink (usable only as target)
float* d_congCost = nullptr;   // [numNodes]  congestion multiplier = hist*present(occ), refreshed per iteration
int*   d_occ      = nullptr;   // [numNodes]  WITHIN-batch live occupancy delta (reset each forward), atomic
}

__global__ void k_fill_float(float* a, int n, float v) {
    int i = blockIdx.x * blockDim.x + threadIdx.x; if (i < n) a[i] = v;
}

#define CKR(x) do { cudaError_t _e = (x); if (_e != cudaSuccess) { \
    std::fprintf(stderr, "[gpu-route] %s -> %s\n", #x, cudaGetErrorString(_e)); return 1; } } while (0)

extern "C" int gpuRouteAvailable() {
    int n = 0;
    cudaError_t e = cudaGetDeviceCount(&n);
    if (e != cudaSuccess) { cudaGetLastError(); return 0; }
    return n > 0 ? 1 : 0;
}

extern "C" int gpuRouteInit(int numNodes, long numEdges,
                            const int* adjOff, const int* adjList,
                            const short* endX, const short* endY,
                            const float* baseCost, const short* length,
                            const unsigned char* blocked) {
    if (numNodes <= 0 || numEdges < 0) return 1;
    g_numNodes = numNodes;
    g_numEdges = numEdges;
    CKR(cudaMalloc(&d_adjOff,   sizeof(int)   * ((size_t) numNodes + 1)));
    CKR(cudaMalloc(&d_adjList,  sizeof(int)   * (size_t) numEdges));
    CKR(cudaMalloc(&d_endX,     sizeof(short) * (size_t) numNodes));
    CKR(cudaMalloc(&d_endY,     sizeof(short) * (size_t) numNodes));
    CKR(cudaMalloc(&d_baseCost, sizeof(float) * (size_t) numNodes));
    CKR(cudaMalloc(&d_length,   sizeof(short) * (size_t) numNodes));
    CKR(cudaMalloc(&d_blocked,  sizeof(unsigned char) * (size_t) numNodes));
    CKR(cudaMalloc(&d_congCost, sizeof(float) * (size_t) numNodes));
    CKR(cudaMalloc(&d_occ,      sizeof(int)   * (size_t) numNodes));
    { int th = 256, bl = (numNodes + th - 1) / th; k_fill_float<<<bl, th>>>(d_congCost, numNodes, 1.0f); }
    CKR(cudaMemcpy(d_adjOff,   adjOff,   sizeof(int)   * ((size_t) numNodes + 1), cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_adjList,  adjList,  sizeof(int)   * (size_t) numEdges,       cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_endX,     endX,     sizeof(short) * (size_t) numNodes,       cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_endY,     endY,     sizeof(short) * (size_t) numNodes,       cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_baseCost, baseCost, sizeof(float) * (size_t) numNodes,       cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_length,   length,   sizeof(short) * (size_t) numNodes,       cudaMemcpyHostToDevice));
    CKR(cudaMemcpy(d_blocked,  blocked,  sizeof(unsigned char) * (size_t) numNodes, cudaMemcpyHostToDevice));
    return 0;
}

// Refresh the resident per-node congestion multiplier (congCost[n] = hist(n) * present(occ(n))),
// computed on the host each iteration from the exact CPU occupancy. The forward kernel reads it.
extern "C" int gpuRouteUpdateCost(const float* congCost) {
    if (!d_congCost || g_numNodes <= 0) return 1;
    CKR(cudaMemcpy(d_congCost, congCost, sizeof(float) * (size_t) g_numNodes, cudaMemcpyHostToDevice));
    return 0;
}

// ---------------------------------------------------------------------------- G0 verify
__global__ void k_verify_bbox_children(int M, const int* __restrict__ srcNode, const short* __restrict__ bbox4,
                                        const int* __restrict__ adjOff, const int* __restrict__ adjList,
                                        const short* __restrict__ endX, const short* __restrict__ endY,
                                        int numNodes, int* __restrict__ outCount) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= M) return;
    int src = srcNode[i];
    if (src < 0 || src >= numNodes) { outCount[i] = -1; return; }
    int xMin = bbox4[4 * i], xMax = bbox4[4 * i + 1], yMin = bbox4[4 * i + 2], yMax = bbox4[4 * i + 3];
    int cnt = 0, e0 = adjOff[src], e1 = adjOff[src + 1];
    for (int e = e0; e < e1; e++) {
        int c = adjList[e]; int ex = endX[c], ey = endY[c];
        if (ex > xMin && ex < xMax && ey > yMin && ey < yMax) cnt++;
    }
    outCount[i] = cnt;
}

extern "C" int gpuRouteVerifyBboxChildren(int M, const int* srcNode, const short* bbox4, int* outCount) {
    if (M <= 0) return 1;
    if (!d_adjOff) { std::fprintf(stderr, "[gpu-route] verify before init\n"); return 1; }
    int *d_src = nullptr, *d_out = nullptr; short* d_bbox = nullptr; int rc = 1;
#define CKG(x) do { cudaError_t _e = (x); if (_e != cudaSuccess) { \
    std::fprintf(stderr, "[gpu-route] %s -> %s\n", #x, cudaGetErrorString(_e)); goto done; } } while (0)
    CKG(cudaMalloc(&d_src,  sizeof(int)   * (size_t) M));
    CKG(cudaMalloc(&d_bbox, sizeof(short) * (size_t) M * 4));
    CKG(cudaMalloc(&d_out,  sizeof(int)   * (size_t) M));
    CKG(cudaMemcpy(d_src,  srcNode, sizeof(int)   * (size_t) M,     cudaMemcpyHostToDevice));
    CKG(cudaMemcpy(d_bbox, bbox4,   sizeof(short) * (size_t) M * 4, cudaMemcpyHostToDevice));
    {
        int threads = 256, blocks = (M + threads - 1) / threads;
        k_verify_bbox_children<<<blocks, threads>>>(M, d_src, d_bbox, d_adjOff, d_adjList,
                                                    d_endX, d_endY, g_numNodes, d_out);
        CKG(cudaGetLastError());
        CKG(cudaDeviceSynchronize());
    }
    CKG(cudaMemcpy(outCount, d_out, sizeof(int) * (size_t) M, cudaMemcpyDeviceToHost));
    rc = 0;
done:
    if (d_src) cudaFree(d_src); if (d_bbox) cudaFree(d_bbox); if (d_out) cudaFree(d_out);
    return rc;
#undef CKG
}

// ---------------------------------------------------------------------------- G2 directed A* + path
__device__ __forceinline__ int hashSlot(const int* nd, int cap, int node) {
    unsigned h = ((unsigned) node * 2654435761u) % (unsigned) cap;
    for (int t = 0; t < cap; t++) {
        int s = (int) h + t; if (s >= cap) s -= cap;
        int v = nd[s];
        if (v == node || v == -1) return s;
    }
    return -1;
}

// Is `node` one of connection i's targets? tgt[base..) is a fixed-width-K list, -1 padded.
__device__ __forceinline__ bool isTgt(const int* tgt, size_t base, int K, int node) {
    for (int j = 0; j < K; j++) { int t = tgt[base + j]; if (t < 0) return false; if (t == node) return true; }
    return false;
}
// Heuristic: min Manhattan distance from (ex,ey) to any of connection i's target begin-tiles.
__device__ __forceinline__ float hMin(const int* tgt, const short* tgtX, const short* tgtY,
                                       size_t base, int K, int ex, int ey) {
    float best = 1e30f;
    for (int j = 0; j < K; j++) { int t = tgt[base + j]; if (t < 0) break;
        float d = fabsf((float)(ex - tgtX[base + j])) + fabsf((float)(ey - tgtY[base + j]));
        if (d < best) best = d; }
    return best;
}

// Directed A* with MULTI-TARGET sinks: f = g + h, g = sum(baseCost*cong + lenW*length), h =
// directedness*min Manhattan(end -> any target begin). Reaches when ANY target pops (alt sinks let
// lutPinSwapping connections spread instead of all piling on one primary sink). tgt[i*K..] is the
// connection's target node list (-1 padded; index 0 is the primary sink). Backtracks the chosen target.
__global__ void k_forward_astar(int M, const int* __restrict__ srcNode,
                                const int* __restrict__ tgt, const short* __restrict__ tgtX,
                                const short* __restrict__ tgtY, int K,
                                const short* __restrict__ bbox4, int cap, float directedness, float lenW,
                                int maxPathLen,
                                const int* __restrict__ adjOff, const int* __restrict__ adjList,
                                const short* __restrict__ endX, const short* __restrict__ endY,
                                const float* __restrict__ baseCost, const short* __restrict__ length,
                                const float* __restrict__ congCost, int* occ, float presentFac,
                                const unsigned char* __restrict__ blocked, int numNodes,
                                int* slotsNode, float* slotsG, int* slotsPrev, unsigned char* slotsClosed,
                                float* heapF, int* heapN,
                                int* __restrict__ outReached, int* __restrict__ outLabels,
                                int* __restrict__ outPathLen, int* __restrict__ outPath) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= M) return;
    size_t off = (size_t) i * (size_t) cap;
    size_t tbase = (size_t) i * (size_t) K;
    int*  nd = slotsNode + off; float* g = slotsG + off; int* pv = slotsPrev + off;
    unsigned char* cl = slotsClosed + off; float* hf = heapF + off; int* hn = heapN + off;
    for (int j = 0; j < cap; j++) nd[j] = -1;
    outReached[i] = 0; outLabels[i] = 0; outPathLen[i] = 0;

    int src = srcNode[i];
    if (src < 0 || src >= numNodes || tgt[tbase] < 0) { outLabels[i] = -1; return; }
    int xMin = bbox4[4 * i], xMax = bbox4[4 * i + 1], yMin = bbox4[4 * i + 2], yMax = bbox4[4 * i + 3];

    int ss = hashSlot(nd, cap, src);
    nd[ss] = src; g[ss] = 0.0f; pv[ss] = -1; cl[ss] = 0;
    int hs = 0, labels = 1;
    hf[0] = directedness * hMin(tgt, tgtX, tgtY, tbase, K, endX[src], endY[src]);
    hn[0] = src; hs = 1;

    while (hs > 0) {
        int v = hn[0];
        hs--;                                   // pop-min: move last to root, sift down
        if (hs > 0) {
            float lf = hf[hs]; int ln = hn[hs]; int k = 0;
            for (;;) {
                int c0 = 2 * k + 1, c1 = c0 + 1, best = k; float bf = lf;
                if (c0 < hs && hf[c0] < bf) { best = c0; bf = hf[c0]; }
                if (c1 < hs && hf[c1] < bf) { best = c1; bf = hf[c1]; }
                if (best == k) break;
                hf[k] = hf[best]; hn[k] = hn[best]; k = best;
            }
            hf[k] = lf; hn[k] = ln;
        }
        int vs = hashSlot(nd, cap, v);
        if (cl[vs]) continue;                   // stale heap entry
        if (isTgt(tgt, tbase, K, v)) {           // reached ANY target: backtrack the prev chain
            size_t pbase = (size_t) i * maxPathLen;
            int cur = v, len = 0;
            for (;;) {
                if (len >= maxPathLen) { outLabels[i] = -2; outPathLen[i] = -2; return; }
                outPath[pbase + len] = cur; len++;
                if (cur == src) break;
                int cs2 = hashSlot(nd, cap, cur); cur = pv[cs2];
                if (cur < 0) break;
            }
            if (presentFac > 0.0f) for (int k = 1; k + 1 < len; k++) atomicAdd(&occ[outPath[pbase + k]], 1);
            outReached[i] = 1; outLabels[i] = labels; outPathLen[i] = len;
            return;
        }
        cl[vs] = 1;
        float gv = g[vs];
        int e0 = adjOff[v], e1 = adjOff[v + 1];
        for (int e = e0; e < e1; e++) {
            int c = adjList[e];
            unsigned char bc = blocked[c];
            if (bc == 1) continue;                       // preserved / inaccessible
            int ex = endX[c], ey = endY[c];
            bool inbb = (ex > xMin && ex < xMax && ey > yMin && ey < yMax);
            if (bc == 2 || !inbb) {                      // targets are bbox-exempt and override exclusive-sink gating
                bool ct = isTgt(tgt, tbase, K, c);
                if (bc == 2 && !ct) continue;            // another net's exclusive sink
                if (!inbb && !ct) continue;              // out of bbox and not a target
            }
            float cong = congCost[c];
            if (presentFac > 0.0f) cong *= 1.0f + presentFac * (float) occ[c];   // within-batch live occupancy
            float ng = gv + baseCost[c] * cong + lenW * (float) length[c];
            int sc = hashSlot(nd, cap, c);
            if (sc < 0) { outLabels[i] = -2; return; }
            bool improve;
            if (nd[sc] == -1) {
                if (labels + 1 >= cap) { outLabels[i] = -2; return; }
                nd[sc] = c; pv[sc] = v; cl[sc] = 0; labels++; improve = true;
            } else {
                improve = (!cl[sc] && ng < g[sc]);
            }
            if (improve) {
                g[sc] = ng; pv[sc] = v;
                if (hs >= cap) { outLabels[i] = -2; return; }
                float f = ng + directedness * hMin(tgt, tgtX, tgtY, tbase, K, ex, ey);
                int k = hs++; hf[k] = f; hn[k] = c;
                while (k > 0) { int p = (k - 1) >> 1; if (hf[p] <= hf[k]) break;
                    float tf = hf[p]; hf[p] = hf[k]; hf[k] = tf; int tn = hn[p]; hn[p] = hn[k]; hn[k] = tn; k = p; }
            }
        }
    }
    outReached[i] = 0; outLabels[i] = labels;            // drained without reaching any target
}

extern "C" int gpuRouteForward(int M, const int* srcNode,
                               const int* tgt, const short* tgtX, const short* tgtY, int K,
                               const short* bbox4,
                               int cap, float directedness, float lenW, float presentFac, int maxPathLen,
                               int* outReached, int* outLabels, int* outPathLen, int* outPath) {
    if (M <= 0 || cap <= 1 || maxPathLen <= 1) return 1;
    if (!d_adjOff) { std::fprintf(stderr, "[gpu-route] forward before init\n"); return 1; }
    if (!tgt || !tgtX || !tgtY || K < 1) { std::fprintf(stderr, "[gpu-route] forward needs targets\n"); return 1; }
    if (presentFac > 0.0f) { cudaError_t _e = cudaMemset(d_occ, 0, sizeof(int) * (size_t) g_numNodes);
        if (_e != cudaSuccess) { std::fprintf(stderr, "[gpu-route] occ reset -> %s\n", cudaGetErrorString(_e)); return 1; } }
    // Chunk connections so per-connection scratch (cap*21B) + path (maxPathLen*4B) fit a memory budget.
    const size_t perConn = (size_t) cap * (sizeof(int) * 3 + sizeof(unsigned char) + sizeof(float) * 2)
                         + (size_t) maxPathLen * sizeof(int);
    const size_t budget = 9ull * 1024 * 1024 * 1024;
    int chunk = (int) std::max((size_t) 1, budget / std::max((size_t) 1, perConn));
    if (chunk > M) chunk = M;

    int *d_src = nullptr, *d_tgt = nullptr, *d_reached = nullptr, *d_labels = nullptr, *d_plen = nullptr, *d_path = nullptr;
    short *d_bbox = nullptr, *d_tx = nullptr, *d_ty = nullptr;
    int *d_nd = nullptr, *d_pv = nullptr, *d_hn = nullptr; float *d_g = nullptr, *d_hf = nullptr;
    unsigned char* d_cl = nullptr;
    int rc = 1;
#define CKG(x) do { cudaError_t _e = (x); if (_e != cudaSuccess) { \
    std::fprintf(stderr, "[gpu-route] %s -> %s\n", #x, cudaGetErrorString(_e)); goto done; } } while (0)
    CKG(cudaMalloc(&d_src,     sizeof(int)   * (size_t) chunk));
    CKG(cudaMalloc(&d_tgt,     sizeof(int)   * (size_t) chunk * K));
    CKG(cudaMalloc(&d_tx,      sizeof(short) * (size_t) chunk * K));
    CKG(cudaMalloc(&d_ty,      sizeof(short) * (size_t) chunk * K));
    CKG(cudaMalloc(&d_bbox,    sizeof(short) * (size_t) chunk * 4));
    CKG(cudaMalloc(&d_reached, sizeof(int)   * (size_t) chunk));
    CKG(cudaMalloc(&d_labels,  sizeof(int)   * (size_t) chunk));
    CKG(cudaMalloc(&d_plen,    sizeof(int)   * (size_t) chunk));
    CKG(cudaMalloc(&d_path,    sizeof(int)   * (size_t) chunk * maxPathLen));
    CKG(cudaMalloc(&d_nd,      sizeof(int)   * (size_t) chunk * cap));
    CKG(cudaMalloc(&d_g,       sizeof(float) * (size_t) chunk * cap));
    CKG(cudaMalloc(&d_pv,      sizeof(int)   * (size_t) chunk * cap));
    CKG(cudaMalloc(&d_cl,      sizeof(unsigned char) * (size_t) chunk * cap));
    CKG(cudaMalloc(&d_hf,      sizeof(float) * (size_t) chunk * cap));
    CKG(cudaMalloc(&d_hn,      sizeof(int)   * (size_t) chunk * cap));
    for (int base = 0; base < M; base += chunk) {
        int cnt = (base + chunk <= M) ? chunk : (M - base);
        CKG(cudaMemcpy(d_src, srcNode + base, sizeof(int) * (size_t) cnt, cudaMemcpyHostToDevice));
        CKG(cudaMemcpy(d_tgt, tgt  + (size_t) base * K, sizeof(int)   * (size_t) cnt * K, cudaMemcpyHostToDevice));
        CKG(cudaMemcpy(d_tx,  tgtX + (size_t) base * K, sizeof(short) * (size_t) cnt * K, cudaMemcpyHostToDevice));
        CKG(cudaMemcpy(d_ty,  tgtY + (size_t) base * K, sizeof(short) * (size_t) cnt * K, cudaMemcpyHostToDevice));
        CKG(cudaMemcpy(d_bbox, bbox4 + (size_t) base * 4, sizeof(short) * (size_t) cnt * 4, cudaMemcpyHostToDevice));
        int threads = 64, blocks = (cnt + threads - 1) / threads;
        k_forward_astar<<<blocks, threads>>>(cnt, d_src, d_tgt, d_tx, d_ty, K, d_bbox, cap, directedness, lenW,
                                             maxPathLen, d_adjOff, d_adjList, d_endX, d_endY, d_baseCost,
                                             d_length, d_congCost, d_occ, presentFac, d_blocked, g_numNodes,
                                             d_nd, d_g, d_pv, d_cl, d_hf, d_hn, d_reached, d_labels, d_plen, d_path);
        CKG(cudaGetLastError());
        CKG(cudaDeviceSynchronize());
        CKG(cudaMemcpy(outReached + base, d_reached, sizeof(int) * (size_t) cnt, cudaMemcpyDeviceToHost));
        CKG(cudaMemcpy(outLabels  + base, d_labels,  sizeof(int) * (size_t) cnt, cudaMemcpyDeviceToHost));
        CKG(cudaMemcpy(outPathLen + base, d_plen,    sizeof(int) * (size_t) cnt, cudaMemcpyDeviceToHost));
        CKG(cudaMemcpy(outPath + (size_t) base * maxPathLen, d_path,
                       sizeof(int) * (size_t) cnt * maxPathLen, cudaMemcpyDeviceToHost));
    }
    rc = 0;
done:
    if (d_src) cudaFree(d_src); if (d_tgt) cudaFree(d_tgt); if (d_tx) cudaFree(d_tx); if (d_ty) cudaFree(d_ty);
    if (d_bbox) cudaFree(d_bbox); if (d_reached) cudaFree(d_reached); if (d_labels) cudaFree(d_labels);
    if (d_plen) cudaFree(d_plen); if (d_path) cudaFree(d_path);
    if (d_nd) cudaFree(d_nd); if (d_g) cudaFree(d_g); if (d_pv) cudaFree(d_pv);
    if (d_cl) cudaFree(d_cl); if (d_hf) cudaFree(d_hf); if (d_hn) cudaFree(d_hn);
    return rc;
#undef CKG
}

// =====================================================================================================
// GPU-FLOOD PROTOTYPE: single-connection, grid-wide parallel priced flood (label-correcting Bellman-Ford
// with packed (cost,prev) atomicMin, bbox-masked, frontier double-buffer). One CONNECTION uses the WHOLE
// GPU (many threads across the wavefront) -- this is the "flood a monster's bbox" form the strategy docs
// bet on. Measures achievable single-connection speedup vs the CPU A* on the SAME price snapshot.
// Cost matches k_forward_astar's g: edge cost into v = baseCost[v]*congCost[v] + lenW*length[v]
// (sharing/bias omitted -> cost is a close approximation, used for the TIMING (G,S) gate, not commit).
namespace {
// Multi-lane flood: each lane owns a full set of per-flood scratch buffers plus its own CUDA
// stream, so DAG-unordered leaf workers can flood CONCURRENTLY. Only the price arrays
// (d_congCost from gpu graph globals + d_congShare below) stay global: concurrent lanes flood
// disjoint territories, so a lane only ever reads prices its own thread (or a completed,
// host-synced ancestor) wrote -- deterministic per-territory prices are preserved.
struct FloodLane {
    unsigned long long* best = nullptr;    // [N] packBest(dist, prev)
    int*  f0 = nullptr; int* f1 = nullptr; // [N] frontier double-buffer
    int*  fcnt = nullptr;                  // [2] frontier counters
    int*  inNext = nullptr;                // [N] generation stamp (dedup into next frontier)
    int*  ftgt = nullptr;                  // [K] this connection's target node ids
    int*  fpath = nullptr; int* fscalar = nullptr;  // outPath[maxPathLen], [reached,len]
    float* fcost = nullptr;
    int*  shareCount = nullptr;            // [N] per-flood countSourceUses; mostly 0
    int*  shareNodes = nullptr; int* shareCounts = nullptr;  // scatter/reset lists (cap SHARE_CAP)
    int*  scatterN = nullptr; float* scatterA = nullptr; float* scatterB = nullptr;  // live-price scatter
    unsigned genBase = 0;                  // kernel-v2 monotonic stamp base (per lane: own inNext)
    cudaStream_t stream = nullptr;
};
const int FLOOD_MAX_LANES = 6;   // VRAM-bound on a 24GB card at ~104M nodes (28B/lane/node); see main.cpp lane clamp
FloodLane g_flanes[FLOOD_MAX_LANES];
int   g_numFloodLanes = 0;
float* d_congShare = nullptr;              // [N] hist*present(occ-1): the same-net-sharing congestion variant (GLOBAL price)
int   g_floodMaxPath = 0;
const float FLOOD_INF = 3.0e38f;
const int SHARE_CAP = 1 << 20;
}

// packing helpers (own copy; gpu_bbox.cu's are in a separate translation unit)
#define FPREV_NONE 0xFFFFFFFFu
__device__ __forceinline__ unsigned long long packBest(float g, unsigned int prev) {
    return ((unsigned long long) __float_as_uint(g) << 32) | (unsigned long long) prev;
}
__device__ __forceinline__ float bestG(unsigned long long b) { return __uint_as_float((unsigned int)(b >> 32)); }
__device__ __forceinline__ unsigned int bestPrev(unsigned long long b) { return (unsigned int)(b & 0xFFFFFFFFull); }

__global__ void k_fill_best(unsigned long long* a, int n, float sentinel) {
    int i = blockIdx.x * blockDim.x + threadIdx.x; if (i < n) a[i] = packBest(sentinel, FPREV_NONE);
}
__global__ void k_flood_seed(unsigned long long* best, int* f0, int* fcnt, int src) {
    best[src] = packBest(0.0f, FPREV_NONE); f0[0] = src; fcnt[0] = 1; fcnt[1] = 0;
}
__device__ __forceinline__ bool isTgtK(const int* tgt, int K, int v) {
    for (int j = 0; j < K; j++) { int t = tgt[j]; if (t < 0) return false; if (t == v) return true; } return false;
}
__global__ void k_scatter_share(const int* nodes, const int* counts, int m, int* shareCount) {
    int i = blockIdx.x * blockDim.x + threadIdx.x; if (i < m) shareCount[nodes[i]] = counts[i];
}
__global__ void k_reset_share(const int* nodes, int m, int* shareCount) {
    int i = blockIdx.x * blockDim.x + threadIdx.x; if (i < m) shareCount[nodes[i]] = 0;
}
// Live-price: scatter updated congestion for the nodes whose occupancy changed since the last flush.
__global__ void k_scatter_cong(const int* nodes, const float* a, const float* b, int m,
                               float* congCost, float* congShare) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < m) { int nd = nodes[i]; congCost[nd] = a[i]; congShare[nd] = b[i]; }
}

// EXACT-cost edge relaxation, mirroring the CPU getNodeCost + wl term:
//   countSourceUses = shareCount[v] (this net's other connections on v); sf = 1 + countSourceUses
//   cong = countSourceUses ? congShare[v] (present(occ-1)) : congCost[v] (present(occ))
//   nodeCost = baseCost*cong/sf ; bias = baseCost*distToNetCenter/(connSize*doubleHpwl)
//   edge = nodeCost + min(bias, nodeCost/2) + lenW*length/sf
__global__ void k_flood_relax(const int* __restrict__ fCur, int* fcnt, int curIdx, int nxtIdx,
                              int* __restrict__ fNxt, int step, int* __restrict__ inNext,
                              unsigned long long* __restrict__ best,
                              const int* __restrict__ adjOff, const int* __restrict__ adjList,
                              const short* __restrict__ endX, const short* __restrict__ endY,
                              const float* __restrict__ baseCost, const short* __restrict__ length,
                              const float* __restrict__ congCost, const float* __restrict__ congShare,
                              const int* __restrict__ shareCount, const unsigned char* __restrict__ blocked,
                              const int* __restrict__ tgt, int K,
                              int xMin, int xMax, int yMin, int yMax, float lenW,
                              float xCenter, float yCenter, int connSize, int doubleHpwl) {
    int cnt = fcnt[curIdx];
    int stride = gridDim.x * blockDim.x;
    for (int idx = blockIdx.x * blockDim.x + threadIdx.x; idx < cnt; idx += stride) {
        int u = fCur[idx];
        float gu = bestG(best[u]);
        int e0 = adjOff[u], e1 = adjOff[u + 1];
        for (int e = e0; e < e1; e++) {
            int v = adjList[e];
            unsigned char bc = blocked[v];
            if (bc == 1) continue;
            int ex = endX[v], ey = endY[v];
            bool inbb = (ex > xMin && ex < xMax && ey > yMin && ey < yMax);
            bool ct = isTgtK(tgt, K, v);
            if (bc == 2 && !ct) continue;                 // another net's exclusive sink
            if (!inbb && !ct) continue;                   // out of bbox and not a target
            int cu = shareCount[v];
            float sf = 1.0f + (float) cu;
            float cong = cu != 0 ? congShare[v] : congCost[v];
            float nodeCost = baseCost[v] * cong / sf;
            float d2c = fabsf((float) ex - xCenter) + fabsf((float) ey - yCenter);
            float bias = (doubleHpwl > 0 && connSize > 0) ? baseCost[v] * d2c / ((float) connSize * (float) doubleHpwl) : 0.0f;
            float ng = gu + nodeCost + fminf(bias, nodeCost * 0.5f) + lenW * (float) length[v] / sf;
            unsigned long long cand = packBest(ng, (unsigned int) u);
            unsigned long long old = atomicMin(&best[v], cand);
            if (cand < old) {
                if (atomicExch(&inNext[v], step) != step) {
                    int pos = atomicAdd(&fcnt[nxtIdx], 1);
                    fNxt[pos] = v;
                }
            }
        }
    }
}
__global__ void k_flood_backtrack(const unsigned long long* best, const int* tgt, int K, int src,
                                  int maxPathLen, int* outPath, int* outScalar, float* outCost) {
    float bc = FLOOD_INF; int bt = -1;
    for (int j = 0; j < K; j++) { int t = tgt[j]; if (t < 0) break; float c = bestG(best[t]); if (c < bc) { bc = c; bt = t; } }
    if (bt < 0 || bc >= FLOOD_INF) { outScalar[0] = 0; outScalar[1] = 0; *outCost = -1.0f; return; }
    int cur = bt, len = 0;
    while (len < maxPathLen) { outPath[len++] = cur; if (cur == src) break;
        unsigned int p = bestPrev(best[cur]); if (p == FPREV_NONE) break; cur = (int) p; }
    outScalar[0] = (cur == src) ? 1 : 0; outScalar[1] = len; *outCost = bc;
}

extern "C" int gpuFloodInit(int maxPathLen, int lanes) {
    if (!d_adjOff || g_numNodes <= 0) { std::fprintf(stderr, "[gpu-flood] init before graph upload\n"); return 1; }
    if (g_numFloodLanes > 0) return 0;                    // already initialized (prewarm + route paths)
    if (lanes < 1) lanes = 1; if (lanes > FLOOD_MAX_LANES) lanes = FLOOD_MAX_LANES;
    g_floodMaxPath = maxPathLen;
    CKR(cudaMalloc(&d_congShare, sizeof(float) * (size_t) g_numNodes));
    { int th = 256, bl = (g_numNodes + th - 1) / th; k_fill_float<<<bl, th>>>(d_congShare, g_numNodes, 1.0f); }
    for (int l = 0; l < lanes; l++) {
        FloodLane& L = g_flanes[l];
        CKR(cudaStreamCreateWithFlags(&L.stream, cudaStreamNonBlocking));
        CKR(cudaMalloc(&L.best,   sizeof(unsigned long long) * (size_t) g_numNodes));
        CKR(cudaMalloc(&L.f0,     sizeof(int) * (size_t) g_numNodes));
        CKR(cudaMalloc(&L.f1,     sizeof(int) * (size_t) g_numNodes));
        CKR(cudaMalloc(&L.inNext, sizeof(int) * (size_t) g_numNodes));
        CKR(cudaMalloc(&L.fcnt,   sizeof(int) * 2));
        CKR(cudaMalloc(&L.ftgt,   sizeof(int) * 64));
        CKR(cudaMalloc(&L.fpath,  sizeof(int) * (size_t) maxPathLen));
        CKR(cudaMalloc(&L.fscalar,sizeof(int) * 2));
        CKR(cudaMalloc(&L.fcost,  sizeof(float)));
        CKR(cudaMalloc(&L.shareCount, sizeof(int) * (size_t) g_numNodes));
        CKR(cudaMalloc(&L.shareNodes, sizeof(int) * (size_t) SHARE_CAP));
        CKR(cudaMalloc(&L.shareCounts, sizeof(int) * (size_t) SHARE_CAP));
        CKR(cudaMalloc(&L.scatterN, sizeof(int) * (size_t) SHARE_CAP));
        CKR(cudaMalloc(&L.scatterA, sizeof(float) * (size_t) SHARE_CAP));
        CKR(cudaMalloc(&L.scatterB, sizeof(float) * (size_t) SHARE_CAP));
        CKR(cudaMemset(L.inNext, 0, sizeof(int) * (size_t) g_numNodes)); L.genBase = 0;
        CKR(cudaMemset(L.shareCount, 0, sizeof(int) * (size_t) g_numNodes));
        g_numFloodLanes = l + 1;
    }
    std::fprintf(stderr, "[gpu-flood] lanes=%d (per-lane VRAM ~%.0f MB)\n", g_numFloodLanes,
                 (double) g_numNodes * 28.0 / 1e6);
    return 0;
}

// Upload the same-net-sharing congestion variant congShare[n] = hist(n)*present(occ(n)-1). Paired with
// gpuRouteUpdateCost (which uploads the no-share congCost[n] = hist*present(occ)) each flooding iteration.
extern "C" int gpuFloodUpdateCostShare(const float* congShare) {
    if (!d_congShare || g_numNodes <= 0) return 1;
    CKR(cudaMemcpy(d_congShare, congShare, sizeof(float) * (size_t) g_numNodes, cudaMemcpyHostToDevice));
    return 0;
}

// Live-price sparse update: for the m nodes whose occupancy changed, scatter new congCost=a / congShare=b.
// Runs on the LANE's stream: ordered before that lane's subsequent flood kernels; host buffers are
// released after the copies complete (stream sync below), the scatter kernel itself stays async.
extern "C" int gpuFloodScatterCong(int lane, const int* nodes, const float* a, const float* b, int m) {
    if (m <= 0) return 0; if (!d_congCost) return 1; if (m > SHARE_CAP) m = SHARE_CAP;
    if (lane < 0 || lane >= g_numFloodLanes) return 1;
    FloodLane& L = g_flanes[lane];
    CKR(cudaMemcpyAsync(L.scatterN, nodes, sizeof(int)   * (size_t) m, cudaMemcpyHostToDevice, L.stream));
    CKR(cudaMemcpyAsync(L.scatterA, a,     sizeof(float) * (size_t) m, cudaMemcpyHostToDevice, L.stream));
    CKR(cudaMemcpyAsync(L.scatterB, b,     sizeof(float) * (size_t) m, cudaMemcpyHostToDevice, L.stream));
    CKR(cudaStreamSynchronize(L.stream));   // host buffers reusable after this
    int bl = (m + 255) / 256;
    k_scatter_cong<<<bl, 256, 0, L.stream>>>(L.scatterN, L.scatterA, L.scatterB, m, d_congCost, d_congShare);
    return 0;
}

// Make everything queued on a lane's stream globally visible (called before a completed leaf's
// successors are released, so their floods -- on ANY lane -- see the leaf's final prices).
extern "C" int gpuFloodSyncLane(int lane) {
    if (lane < 0 || lane >= g_numFloodLanes) return 1;
    CKR(cudaStreamSynchronize(g_flanes[lane].stream));
    return 0;
}

// Flood one connection. Returns 0 on success; fills outReached/outCost/outPathLen/outPath and outKernelMs
// (GPU-active wall over the whole flood) and outWallMs (host wall incl. per-step sync).
extern "C" int gpuFloodConnection(int lane, int src, const int* targets, int K,
                                  int xMin, int xMax, int yMin, int yMax, float lenW, int maxSteps,
                                  float xCenter, float yCenter, int connSize, int doubleHpwl,
                                  const int* shareNodes, const int* shareCounts, int shareM,
                                  int* outReached, float* outCost, int* outPathLen, int* outPath,
                                  double* outKernelMs) {
    if (g_numFloodLanes == 0) { std::fprintf(stderr, "[gpu-flood] flood before init\n"); return 1; }
    if (lane < 0 || lane >= g_numFloodLanes) return 1;
    if (src < 0 || src >= g_numNodes || K < 1 || K > 64) return 1;
    FloodLane& L = g_flanes[lane];
    cudaStream_t st = L.stream;
    int Ktgt = K;
    CKR(cudaMemcpyAsync(L.ftgt, targets, sizeof(int) * (size_t) K, cudaMemcpyHostToDevice, st));
    int m = shareM; if (m > SHARE_CAP) m = SHARE_CAP;
    if (m > 0) {
        CKR(cudaMemcpyAsync(L.shareNodes,  shareNodes,  sizeof(int) * (size_t) m, cudaMemcpyHostToDevice, st));
        CKR(cudaMemcpyAsync(L.shareCounts, shareCounts, sizeof(int) * (size_t) m, cudaMemcpyHostToDevice, st));
    }
    CKR(cudaStreamSynchronize(st));                      // host-side targets/share buffers reusable after this
    if (m > 0) { int sb = (m + 255) / 256; k_scatter_share<<<sb, 256, 0, st>>>(L.shareNodes, L.shareCounts, m, L.shareCount); }
    const int TH = 128, BL = 4096;                       // grid-stride flood grid (~524k threads)
    int fillTh = 256, fillBl = (g_numNodes + fillTh - 1) / fillTh;
    cudaEvent_t ev0, ev1; cudaEventCreate(&ev0); cudaEventCreate(&ev1);
    cudaEventRecord(ev0, st);
    // kernel-v2-lite (KEPT): skip the per-flood O(N) inNext reset via a PER-LANE monotonic stamp (no atomics).
    // The full-N best fill STAYS: it is coalesced and cheap (~0.5ms). A touched-list reset was MEASURED
    // slower (per-node atomicAdd on one counter contends more than the coalesced fill it replaced).
    if (L.genBase > 2000000000u) { CKR(cudaMemsetAsync(L.inNext, 0, sizeof(int) * (size_t) g_numNodes, st)); L.genBase = 0; }
    unsigned genBase = L.genBase;
    k_fill_best<<<fillBl, fillTh, 0, st>>>(L.best, g_numNodes, FLOOD_INF);
    k_flood_seed<<<1, 1, 0, st>>>(L.best, L.f0, L.fcnt, src);
    int hostCnt = 1;
    int stepsUsed = 0; int lastCnt = 1;
    for (int step = 1; step <= maxSteps && hostCnt > 0; step++) {
        int cur = (step - 1) & 1, nxt = cur ^ 1;
        int* fCur = cur ? L.f1 : L.f0; int* fNxt = nxt ? L.f1 : L.f0;
        int stamp = (int) (genBase + (unsigned) step);   // unique per (flood,step) within this lane
        CKR(cudaMemsetAsync(L.fcnt + nxt, 0, sizeof(int), st));
        k_flood_relax<<<BL, TH, 0, st>>>(fCur, L.fcnt, cur, nxt, fNxt, stamp, L.inNext, L.best,
                                  d_adjOff, d_adjList, d_endX, d_endY, d_baseCost, d_length, d_congCost,
                                  d_congShare, L.shareCount, d_blocked, L.ftgt, Ktgt, xMin, xMax, yMin, yMax,
                                  lenW, xCenter, yCenter, connSize, doubleHpwl);
        if ((step % 16) == 0 || step <= 4) {             // amortized convergence check (avoid per-step D2H)
            CKR(cudaMemcpyAsync(&hostCnt, L.fcnt + nxt, sizeof(int), cudaMemcpyDeviceToHost, st));
            CKR(cudaStreamSynchronize(st));
            lastCnt = hostCnt;
        }
        stepsUsed = step;
    }
    if (stepsUsed >= maxSteps)
        std::fprintf(stderr, "[flood-steps] MAXED steps=%d lastFrontier=%d src=%d bbox=%d..%dx%d..%d\n",
                     stepsUsed, lastCnt, src, xMin, xMax, yMin, yMax);
    L.genBase += (unsigned) (maxSteps + 2);   // advance the stamp base past this flood's range
    k_flood_backtrack<<<1, 1, 0, st>>>(L.best, L.ftgt, Ktgt, src, g_floodMaxPath, L.fpath, L.fscalar, L.fcost);
    cudaEventRecord(ev1, st);
    if (m > 0) { int sb = (m + 255) / 256; k_reset_share<<<sb, 256, 0, st>>>(L.shareNodes, m, L.shareCount); }
    int sc[2];
    CKR(cudaMemcpyAsync(sc, L.fscalar, sizeof(int) * 2, cudaMemcpyDeviceToHost, st));
    CKR(cudaMemcpyAsync(outCost, L.fcost, sizeof(float), cudaMemcpyDeviceToHost, st));
    CKR(cudaStreamSynchronize(st));
    float ms = 0.0f; cudaEventElapsedTime(&ms, ev0, ev1); *outKernelMs = ms;
    cudaEventDestroy(ev0); cudaEventDestroy(ev1);
    *outReached = sc[0]; *outPathLen = sc[1];
    if (sc[1] > 0) {
        CKR(cudaMemcpyAsync(outPath, L.fpath, sizeof(int) * (size_t) std::min(sc[1], g_floodMaxPath), cudaMemcpyDeviceToHost, st));
        CKR(cudaStreamSynchronize(st));
    }
    return 0;
}

// ALT landmark SSSP: whole-device static-cost shortest paths from one source, using lane 0's
// flood scratch with cong=1.0 prices (call BEFORE the first refreshFloodCost). Fills outCost[N]
// (FLOOD_INF where unreached). Cost model = the exact iter-1 static edge cost (bias=0, sf=1).
extern "C" int gpuLandmarkSSSP(int src, int maxSteps, float lenW, float* outCost) {
    if (g_numFloodLanes == 0 || src < 0 || src >= g_numNodes) return 1;
    FloodLane& L = g_flanes[0];
    cudaStream_t st = L.stream;
    int tgtNone = -1;
    CKR(cudaMemcpyAsync(L.ftgt, &tgtNone, sizeof(int), cudaMemcpyHostToDevice, st));
    const int TH = 128, BL = 4096;
    int fillTh = 256, fillBl = (g_numNodes + fillTh - 1) / fillTh;
    if (L.genBase > 2000000000u) { CKR(cudaMemsetAsync(L.inNext, 0, sizeof(int) * (size_t) g_numNodes, st)); L.genBase = 0; }
    unsigned genBase = L.genBase;
    k_fill_best<<<fillBl, fillTh, 0, st>>>(L.best, g_numNodes, FLOOD_INF);
    k_flood_seed<<<1, 1, 0, st>>>(L.best, L.f0, L.fcnt, src);
    int hostCnt = 1;
    for (int step = 1; step <= maxSteps && hostCnt > 0; step++) {
        int cur = (step - 1) & 1, nxt = cur ^ 1;
        int* fCur = cur ? L.f1 : L.f0; int* fNxt = nxt ? L.f1 : L.f0;
        int stamp = (int) (genBase + (unsigned) step);
        CKR(cudaMemsetAsync(L.fcnt + nxt, 0, sizeof(int), st));
        k_flood_relax<<<BL, TH, 0, st>>>(fCur, L.fcnt, cur, nxt, fNxt, stamp, L.inNext, L.best,
                                  d_adjOff, d_adjList, d_endX, d_endY, d_baseCost, d_length, d_congCost,
                                  d_congShare, L.shareCount, d_blocked, L.ftgt, 1,
                                  -1, 1 << 20, -1, 1 << 20, lenW, 0.0f, 0.0f, 0, 0);
        if ((step % 16) == 0 || step <= 4) {
            CKR(cudaMemcpyAsync(&hostCnt, L.fcnt + nxt, sizeof(int), cudaMemcpyDeviceToHost, st));
            CKR(cudaStreamSynchronize(st));
        }
    }
    L.genBase += (unsigned) (maxSteps + 2);
    // extract costs from the packed (cost|prev) array: reuse fpath? sizes differ -- D2H the packed
    // array in chunks through outCost's own memory (caller provides N floats; we need N u64 staging).
    // Simplest: chunked copy via a device-side repack into L.best reinterpreted... do it on host:
    {
        const size_t CH = 8 << 20;                    // 8M nodes per chunk (64MB staging)
        unsigned long long* stage = (unsigned long long*) malloc(CH * sizeof(unsigned long long));
        for (size_t off = 0; off < (size_t) g_numNodes; off += CH) {
            size_t n = std::min(CH, (size_t) g_numNodes - off);
            CKR(cudaMemcpyAsync(stage, L.best + off, n * sizeof(unsigned long long),
                                cudaMemcpyDeviceToHost, st));
            CKR(cudaStreamSynchronize(st));
            for (size_t i = 0; i < n; i++) { unsigned int cb = (unsigned int)(stage[i] >> 32); float cf; memcpy(&cf, &cb, 4); outCost[off + i] = cf; }
        }
        free(stage);
    }
    return 0;
}

extern "C" void gpuFloodFree() {
    for (int l = 0; l < g_numFloodLanes; l++) {
        FloodLane& L = g_flanes[l];
        if (L.best) cudaFree(L.best); if (L.f0) cudaFree(L.f0); if (L.f1) cudaFree(L.f1);
        if (L.inNext) cudaFree(L.inNext); if (L.fcnt) cudaFree(L.fcnt); if (L.ftgt) cudaFree(L.ftgt);
        if (L.fpath) cudaFree(L.fpath); if (L.fscalar) cudaFree(L.fscalar); if (L.fcost) cudaFree(L.fcost);
        if (L.shareCount) cudaFree(L.shareCount);
        if (L.shareNodes) cudaFree(L.shareNodes); if (L.shareCounts) cudaFree(L.shareCounts);
        if (L.scatterN) cudaFree(L.scatterN); if (L.scatterA) cudaFree(L.scatterA); if (L.scatterB) cudaFree(L.scatterB);
        if (L.stream) cudaStreamDestroy(L.stream);
        L = FloodLane();
    }
    g_numFloodLanes = 0;
    if (d_congShare) cudaFree(d_congShare); d_congShare = nullptr;
}

extern "C" void gpuRouteShutdown() {
    if (d_adjOff)   cudaFree(d_adjOff);
    if (d_adjList)  cudaFree(d_adjList);
    if (d_endX)     cudaFree(d_endX);
    if (d_endY)     cudaFree(d_endY);
    if (d_baseCost) cudaFree(d_baseCost);
    if (d_length)   cudaFree(d_length);
    if (d_blocked)  cudaFree(d_blocked);
    if (d_congCost) cudaFree(d_congCost);
    if (d_occ)      cudaFree(d_occ);
    d_adjOff = nullptr; d_adjList = nullptr; d_endX = nullptr; d_endY = nullptr;
    d_baseCost = nullptr; d_length = nullptr; d_blocked = nullptr; d_congCost = nullptr; d_occ = nullptr;
    g_numNodes = 0; g_numEdges = 0;
    cudaDeviceReset();
}
