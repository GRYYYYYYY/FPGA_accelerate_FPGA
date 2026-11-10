#pragma once
// Track D / D1: GPU coarse-grid corridor solver (CUDA). Implemented in src/gpu_bbox.cu and linked
// into the JNI library only when a CUDA toolkit is found (WITH_CUDA). main.cpp includes this only
// under WITH_CUDA and falls back to the CPU Dijkstra otherwise.
#ifdef __cplusplus
extern "C" {
#endif

// 1 if at least one CUDA device is present and usable, else 0.
int gpuBboxAvailable();

// Batched congestion-weighted shortest path on the coarse 4-neighbour mesh (one block per pair).
// adjOff/adjList: CSR of the mesh (numCells nodes). nodeCosts[c] = cost of entering cell c.
// xy[2*c],xy[2*c+1] = (gx,gy) of cell c. pairs[2*i],pairs[2*i+1] = (srcCell,sinkCell) of pair i.
// Each block runs Bellman-Ford over the pair's window (cell bbox + marginCells; init and sweep touch
// window cells only), backtracks the path, and writes the corridor cell-range into
// outCorridor[4*i] = {minGx,maxGx,minGy,maxGy}; minGx<0 means no complete path (caller falls back to
// the source/sink rectangle). keepCtx=1 skips the trailing cudaDeviceReset (a GPU-flood init follows
// and would otherwise pay a second context creation).
// Returns 0 on success, non-zero on any CUDA error (caller falls back to the CPU solver).
int gpuSolveCorridors(int gridW, int gridH,
                      const int* adjOff, const int* adjList, const float* nodeCosts, const short* xy,
                      int numCells, const int* pairs, int M, int maxHops, int marginCells,
                      int keepCtx, int* outCorridor);

#ifdef __cplusplus
}
#endif
