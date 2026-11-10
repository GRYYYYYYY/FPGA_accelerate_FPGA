# Route-tree integration into the complete CPU router

`scripts/prepare_route_tree_router.py` derives an isolated flat source tree from
the resident-snapshot router. All predecessor sources and compiled search objects
remain unchanged and hash-bound. `route_tree_routes_transform.py` uses exact
single-occurrence replacements and produces reviewable diffs.

Per net, the actual tree top resets to the source node. Before each sink search,
the top exports ascending canonical roots; its resident 65-word demands feed the
snapshot top's query patch directly, without host normalization or repacking.
The unchanged search top writes its usual 81-word result and eight-word-per-edge
path. After validating the result framing, the adapter passes these raw buffers
to the tree top before exporting host search traces. Failed searches retain the
existing tree and demands. At net completion, the tree top checks all original
sinks and emits nodes for retained output and occupancy updates. Final demand
unpacking occurs only for retained results and the existing site-ledger bridge.

The host `Tree` owns fixed production-depth bitset and root buffers plus metadata
and demands; it does not maintain a second live node set or demand map. Its dummy
unused arguments are only suitable for CPU execution. A future RTL testbench
must allocate all declared port depths. This integration is not an XRT device
connection or hardware outer scheduler. Per-round scheduling, target sorting,
retained traces, final occupancy marshalling, and static metadata remain host
work. Search/occupancy/snapshot/tree buffers require a new combined device memory
plan; the frozen search-only plan does not establish bank compatibility.

Verification gates retain failures and refuse overwrites:

1. Strict production C++14 top build, native sanitizer component test.
2. Both unchanged production search tops linked into a 400-case randomized
   negotiated-routing differential against the original native router. All
   intermediate paths, statuses, costs, unknown resources, final demands, nodes,
   completion states, and node/site conflicts must match. Native adjacency
   fallback is disabled in the test graph during kernel execution.
3. Independent preparation audit recomputes source transforms and input hashes,
   checks execution receipts and literal coverage counts.
4. Full real workloads use two batches of all 1062 nets for each representation,
   with unchanged cache4096/80 rounds/200000 budget/present cap8. The predecessor
   resident-snapshot full audit must finish first. The new audit compares complete
   raw semantic results and controller/snapshot/kernel counters.
5. Separate local HLS 2022.2 Csim/synthesis uses production capacities, xcu280,
   5 ns clock and 1.35 ns uncertainty. The single audit supervisor observes the
   original process and never restarts synthesis. RTL remains a separate gate.

Timing/resource estimates, CPU durations, and logical ABI counts are not measured
board throughput, physical timing closure, memory bandwidth, or power evidence.
