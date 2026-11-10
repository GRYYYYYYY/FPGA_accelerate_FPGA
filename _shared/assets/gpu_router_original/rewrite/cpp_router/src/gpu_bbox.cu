// Track D / D1: GPU coarse-grid corridor solver. Ported from the previous Java attempt's
// route_bellman_ford kernel (fwbei/RapidWright/cuda/cuda_router.cu): one block per connection,
// congestion-weighted Bellman-Ford on the coarse 4-neighbour mesh bounded by the connection's cell
// bbox, packed (cost,prev) relaxed with atomicMin, then backtrack the path to a corridor cell-range.
#include <cuda_runtime.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>

#define PREV_NONE 0xFFFFFFFFu

__device__ __forceinline__ unsigned long long packBest(float g, unsigned int prev) {
    // Non-negative cost in the high 32 bits => atomicMin on the u64 minimises by cost.
    unsigned int gi = __float_as_uint(g);
    return ((unsigned long long) gi << 32) | (unsigned long long) prev;
}
__device__ __forceinline__ float bestG(unsigned long long b) { return __uint_as_float((unsigned int)(b >> 32)); }
__device__ __forceinline__ unsigned int bestPrev(unsigned long long b) { return (unsigned int)(b & 0xFFFFFFFFull); }

__global__ void bf_corridor(const int* __restrict__ adjOff, const int* __restrict__ adjList,
                            const float* __restrict__ nodeCosts, const short* __restrict__ xy,
                            const int* __restrict__ pairs, int chunkBase, int chunkCnt,
                            int gridW, int gridH, int numCells, int maxHops, int marginCells,
                            unsigned long long* best_global, int* outCorridor) {
    const unsigned long long INF = 0xFFFFFFFFFFFFFFFFull;
    int local = blockIdx.x;
    if (local >= chunkCnt) return;
    int conn = chunkBase + local;
    int src = pairs[2 * conn], dst = pairs[2 * conn + 1];
    unsigned long long* best = best_global + (size_t) local * numCells;
    if (threadIdx.x == 0) {
        outCorridor[4 * conn] = -1; outCorridor[4 * conn + 1] = -1;
        outCorridor[4 * conn + 2] = -1; outCorridor[4 * conn + 3] = -1;
    }
    if (src < 0 || dst < 0 || src >= numCells || dst >= numCells) return;

    // Window = pair bbox + margin, clamped to the grid. Init and sweep touch WINDOW cells only --
    // the old full-grid loops made every Bellman-Ford round cost O(numCells) regardless of how
    // small the corridor was (the reason D1 originally only tied the CPU solver).
    int sX = xy[2 * src], sY = xy[2 * src + 1], dX = xy[2 * dst], dY = xy[2 * dst + 1];
    int bxlo = max(0, min(sX, dX) - marginCells), bxhi = min(gridW - 1, max(sX, dX) + marginCells);
    int bylo = max(0, min(sY, dY) - marginCells), byhi = min(gridH - 1, max(sY, dY) + marginCells);
    const int wW = bxhi - bxlo + 1, wN = wW * (byhi - bylo + 1);

    for (int w = threadIdx.x; w < wN; w += blockDim.x)
        best[(bylo + w / wW) * gridW + (bxlo + w % wW)] = INF;
    __syncthreads();
    if (threadIdx.x == 0) best[src] = packBest(0.f, PREV_NONE);
    __syncthreads();

    __shared__ int changed;
    for (int it = 0; it < maxHops; it++) {
        if (threadIdx.x == 0) changed = 0;
        __syncthreads();
        for (int w = threadIdx.x; w < wN; w += blockDim.x) {
            int v = (bylo + w / wW) * gridW + (bxlo + w % wW);
            unsigned long long bv = best[v];
            if (bv == INF) continue;
            float gv = bestG(bv);
            int e0 = adjOff[v], e1 = adjOff[v + 1];
            for (int e = e0; e < e1; e++) {
                int u = adjList[e];
                int ux = xy[2 * u], uy = xy[2 * u + 1];
                if (ux < bxlo || ux > bxhi || uy < bylo || uy > byhi) continue;
                float cg = gv + nodeCosts[u];
                unsigned long long cand = packBest(cg, (unsigned int) v);
                unsigned long long old = atomicMin(&best[u], cand);
                if (cand < old) changed = 1;
            }
        }
        __syncthreads();
        if (changed == 0) break;
    }

    if (threadIdx.x == 0 && best[dst] != INF) {
        int mnx = 2000000000, mxx = -1, mny = 2000000000, mxy = -1, cur = dst, guard = 0;
        while (cur != -1 && guard++ <= maxHops) {
            int gx = xy[2 * cur], gy = xy[2 * cur + 1];
            if (gx < mnx) mnx = gx; if (gx > mxx) mxx = gx;
            if (gy < mny) mny = gy; if (gy > mxy) mxy = gy;
            if (cur == src) break;
            unsigned int p = bestPrev(best[cur]);
            cur = (p == PREV_NONE) ? -1 : (int) p;
        }
        if (cur == src) {  // only a complete source-anchored path is a valid corridor
            outCorridor[4 * conn] = mnx; outCorridor[4 * conn + 1] = mxx;
            outCorridor[4 * conn + 2] = mny; outCorridor[4 * conn + 3] = mxy;
        }
    }
}

extern "C" int gpuBboxAvailable() {
    int n = 0;
    cudaError_t e = cudaGetDeviceCount(&n);
    if (e != cudaSuccess) { cudaGetLastError(); return 0; }
    return n > 0 ? 1 : 0;
}

extern "C" int gpuSolveCorridors(int gridW, int gridH,
                                 const int* adjOff, const int* adjList, const float* nodeCosts, const short* xy,
                                 int numCells, const int* pairs, int M, int maxHops, int marginCells,
                                 int keepCtx, int* outCorridor) {
    if (M <= 0 || numCells <= 0) return 1;
    const size_t adjLen = (size_t) adjOff[numCells];
    int *d_adjOff = nullptr, *d_adjList = nullptr, *d_pairs = nullptr, *d_corr = nullptr;
    float* d_costs = nullptr; short* d_xy = nullptr; unsigned long long* d_best = nullptr;
    cudaError_t e;
#define CK(x) do { e = (x); if (e != cudaSuccess) { \
        std::fprintf(stderr, "[gpu-bbox] %s -> %s\n", #x, cudaGetErrorString(e)); goto fail; } } while (0)
    CK(cudaMalloc(&d_adjOff,  sizeof(int)   * ((size_t) numCells + 1)));
    CK(cudaMalloc(&d_adjList, sizeof(int)   * adjLen));
    CK(cudaMalloc(&d_costs,   sizeof(float) * (size_t) numCells));
    CK(cudaMalloc(&d_xy,      sizeof(short) * (size_t) numCells * 2));
    CK(cudaMalloc(&d_pairs,   sizeof(int)   * (size_t) M * 2));
    CK(cudaMalloc(&d_corr,    sizeof(int)   * (size_t) M * 4));
    CK(cudaMemcpy(d_adjOff,  adjOff,    sizeof(int)   * ((size_t) numCells + 1), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_adjList, adjList,   sizeof(int)   * adjLen,                  cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_costs,   nodeCosts, sizeof(float) * (size_t) numCells,       cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_xy,      xy,        sizeof(short) * (size_t) numCells * 2,   cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_pairs,   pairs,     sizeof(int)   * (size_t) M * 2,          cudaMemcpyHostToDevice));
    {
        const size_t budget = 6ull * 1024 * 1024 * 1024;   // best_global budget
        const size_t perConn = (size_t) numCells * sizeof(unsigned long long);
        int chunk = (int) std::max((size_t) 1, budget / std::max((size_t) 1, perConn));
        if (chunk > M) chunk = M;
        CK(cudaMalloc(&d_best, perConn * (size_t) chunk));
        const int threads = 128;
        for (int base = 0; base < M; base += chunk) {
            int cnt = (base + chunk <= M) ? chunk : (M - base);
            bf_corridor<<<cnt, threads>>>(d_adjOff, d_adjList, d_costs, d_xy, d_pairs,
                                          base, cnt, gridW, gridH, numCells, maxHops, marginCells,
                                          d_best, d_corr);
            CK(cudaGetLastError());
            CK(cudaDeviceSynchronize());
        }
    }
    CK(cudaMemcpy(outCorridor, d_corr, sizeof(int) * (size_t) M * 4, cudaMemcpyDeviceToHost));
    cudaFree(d_adjOff); cudaFree(d_adjList); cudaFree(d_costs); cudaFree(d_xy);
    cudaFree(d_pairs); cudaFree(d_corr); cudaFree(d_best);
    // When no GPU flood follows, the corridor solve is the ONLY GPU work in the whole run; destroy
    // the context so its driver threads do not compete with the CPU route/finalize (measured: the
    // context, not the solve, was the GPU overhead). With flood enabled (keepCtx=1) the context is
    // reused by the flood init that runs right after -- resetting would just pay it twice.
    if (!keepCtx) cudaDeviceReset();
    return 0;
fail:
    if (d_adjOff) cudaFree(d_adjOff); if (d_adjList) cudaFree(d_adjList);
    if (d_costs) cudaFree(d_costs);   if (d_xy) cudaFree(d_xy);
    if (d_pairs) cudaFree(d_pairs);   if (d_corr) cudaFree(d_corr);
    if (d_best) cudaFree(d_best);
    return 1;
#undef CK
}
