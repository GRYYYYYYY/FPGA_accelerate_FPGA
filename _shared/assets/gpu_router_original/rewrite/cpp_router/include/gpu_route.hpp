#pragma once
// GPU detailed-routing engine (CUDA). Implemented in src/gpu_route.cu, linked into both the
// standalone router and the JNI library when a CUDA toolkit is found (WITH_CUDA). Staged plan:
//   G0  upload the static RRG (CSR + per-node coords/baseCost/blocked) resident on device + verify
//   G1  per-connection bounded forward search within bbox -> sink-reach COVERAGE gate (label study)
//   G2+ congestion cost + bidirectional + directedness + path extraction (the real router)
// The CPU router stays the always-available fallback, so any connection the GPU cannot place
// (capacity-exceeded / not reached) is finished on the CPU.
#ifdef __cplusplus
extern "C" {
#endif

// 1 if at least one CUDA device is present and usable, else 0.
int gpuRouteAvailable();

// G0: upload the static routing-resource graph and keep it resident on the device.
//   adjOff[numNodes+1]  CSR offsets (adjOff[numNodes]==numEdges)
//   adjList[numEdges]   CSR children
//   endX/endY[numNodes] end-tile coords (mirror isInConnectionBoundingBox)
//   baseCost[numNodes]  per-node base cost (wirelength term)
//   length[numNodes]    per-node length (wirelength accumulation)
//   blocked[numNodes]   0=usable, 1=hard-blocked (preserved/INACCESSIBLE),
//                       2=exclusive-sink (usable only when it is this connection's target)
// Returns 0 on success, non-zero on any CUDA error.
int gpuRouteInit(int numNodes, long numEdges,
                 const int* adjOff, const int* adjList,
                 const short* endX, const short* endY,
                 const float* baseCost, const short* length,
                 const unsigned char* blocked);

// Refresh the resident per-node congestion multiplier (congCost[n] = hist(n)*present(occ(n))), computed
// on the host from the exact CPU occupancy each negotiated-congestion iteration. The forward kernel
// multiplies each node's baseCost by it, so congested nodes get expensive and routes negotiate away.
// Returns 0 on success.
int gpuRouteUpdateCost(const float* congCost);

// G0 verification kernel: per connection, count children of srcNode[i] strictly inside its bbox
// (bbox4[4*i+0..3]=xMin,xMax,yMin,yMax). Writes outCount[i] (-1 if srcNode[i] invalid).
int gpuRouteVerifyBboxChildren(int M, const int* srcNode, const short* bbox4, int* outCount);

// G2 forward route: per connection, directed A* (per-thread min-heap on f = g + h, g = sum of
// baseCost + lenW*length, h = directedness * Manhattan(node_end -> sink_begin)) from srcNode[i] toward
// sinkNode[i], restricted to the bbox, gated by blocked-codes, early-exit when the sink pops, then
// backtrack the prev chain into outPath. sinkX/sinkY = sink begin-tile coords. Per connection writes:
//   outReached[i]  = 1 if the sink was reached, else 0
//   outLabels[i]   = #nodes expanded (>0), -2 if cap/path exceeded (=> CPU), -1 if src/sink invalid
//   outPathLen[i]  = #nodes on the route (sink->source), -2 if the path exceeded maxPathLen
//   outPath[i*maxPathLen + k] = the route node ids (sink first, source last) for k < outPathLen[i]
// Returns 0 on success, non-zero on any CUDA error.
// presentFac > 0 enables WITHIN-batch live occupancy: cong(n) = congCost(n)*(1+presentFac*occ(n)) where
// occ is incremented atomically as connections in this batch commit, so they spread instead of piling on
// the same nodes (the stale-batch problem). presentFac = 0 => pure frozen congCost (no atomics).
// Multi-target: tgt[i*K + j] are connection i's target node ids (-1 padded; index 0 = primary sink),
// tgtX/tgtY[i*K + j] the targets' begin-tile coords. The A* reaches when ANY target pops; outPath[0]
// is the chosen target. (Single-sink connections just use K=1.)
int gpuRouteForward(int M, const int* srcNode,
                    const int* tgt, const short* tgtX, const short* tgtY, int K,
                    const short* bbox4,
                    int cap, float directedness, float lenW, float presentFac, int maxPathLen,
                    int* outReached, int* outLabels, int* outPathLen, int* outPath);

// GPU-flood prototype: single-connection grid-wide priced Bellman-Ford flood (bbox-masked, packed
// (cost,prev) atomicMin). gpuFloodInit allocates flood scratch (needs gpuRouteInit first);
// gpuFloodConnection floods one connection against the resident congCost snapshot and returns the path
// + timing; gpuFloodFree releases the scratch. See src/gpu_route.cu.
// Multi-lane: `lanes` independent per-flood scratch sets + CUDA streams so DAG-unordered leaf
// workers flood concurrently (prices stay global; disjoint territories keep them deterministic).
int  gpuFloodInit(int maxPathLen, int lanes);
int  gpuFloodUpdateCostShare(const float* congShare);   // hist*present(occ-1), paired with gpuRouteUpdateCost
int  gpuFloodScatterCong(int lane, const int* nodes, const float* a, const float* b, int m);  // live-price sparse update
int  gpuFloodSyncLane(int lane);                        // stream-sync a lane (leaf-completion price publish)
int  gpuFloodConnection(int lane, int src, const int* targets, int K,
                        int xMin, int xMax, int yMin, int yMax, float lenW, int maxSteps,
                        float xCenter, float yCenter, int connSize, int doubleHpwl,
                        const int* shareNodes, const int* shareCounts, int shareM,
                        int* outReached, float* outCost, int* outPathLen, int* outPath, double* outKernelMs);
int  gpuLandmarkSSSP(int src, int maxSteps, float lenW, float* outCost);  // ALT landmarks (lane 0, cong=1)
void gpuFloodFree();

// Free all resident device buffers and tear down the CUDA context.
void gpuRouteShutdown();

#ifdef __cplusplus
}
#endif
