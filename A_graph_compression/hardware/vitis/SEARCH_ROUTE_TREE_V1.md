# Current multi-sink route tree

`search_route_tree_top` manages the current net's canonical node membership and
accumulated site demands. It does not replace retained edge traces, negotiated
routing scheduling, or the search core's physical adjacency/site checks.

Production bounds are 1048576 canonical nodes and 524288 edges per accepted
search path. State is external: meta[5] = magic, active node count, source,
unique tree node count, version; bits[16384]; demands[65] in the original packed
32-signal/16-bit-field/8-categorical-state format with node zero.

Config[8] = operation, reset_nodes, reset_source, target, sink_count, 0, 0, 0.
Operations: 0 reset; 1 accept search_result[81] and path[4194304]; 2 emit ascending
canonical roots[1048576]; 3 check sinks[1048576]. Fields unrelated to the selected
operation must be zero. All pointers must be valid, disjoint, exclusively owned;
RTL testbenches must allocate complete declared depths regardless of operation.

Result[6] = status, unique_nodes, version, applied, roots_count, complete.
Status: 0 success, 1 invalid, 2 capacity, 3 version overflow. Errors clear the
other five result words. Every update preflights before touching persistent
state. A well-framed unsuccessful search is a successful no-op (applied=0),
including no change to version. Accepted found results increment version even
for an empty path, whose target must already belong to the tree and whose
demands must be unchanged. Nonempty paths start in the existing tree, end at
target, have continuous canonical endpoints, and preserve all prior demands.
Repeated nodes count once. Active internal state is trusted to originate from
reset/accepted operations; arbitrary corrupted internal buffers are outside
this interface contract. Unused packed-state slots are canonicalized on store.

Reset clears only active bitset words; inactive tails remain unchanged. Roots
overwrites only its logical prefix. Sink lists may contain duplicates; an empty
list is complete. The six AXI bundles are input_mem, meta_mem, tree_mem,
state_mem, path_mem, output_mem. All interface pragmas are in the top body,
following the Ross hls-pragma-scope rules. No throughput claim follows from
these bounded loops or CPU tests.

Verification: `scripts/check_route_tree_cpu.py --build <new-directory>
--output <new-report.json>` compiles strict C++14 with ASAN/UBSAN and runs the
actual production top plus a small-capacity randomized helper test. The oracle
uses a std::set and literal packed ABI, not DUT packing helpers. Tests include
1000 randomized accepted paths, 1000 failed searches, 21 atomic rejections,
actual maximum path length, two paths filling all 1048576 nodes, maximum demand
counts, all roots/sinks, unchanged inputs and guards, partial-reset stale tails.
This evidence does not establish complete-router integration, HLS, RTL, timing,
device throughput, or physical semantic coverage.
