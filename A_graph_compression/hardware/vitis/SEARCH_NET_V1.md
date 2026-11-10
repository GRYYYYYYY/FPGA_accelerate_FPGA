# Internal net transaction v1

`search_net_top` composes the actual bounded production cores. Its nested
`sink_loop_worker` is derived from the root_nodes-renamed sink loop with all
subfunction INTERFACE pragmas removed; only the outer top declares interfaces.
`derive_search_net_top.py` reproduces the source without changing frozen cores.

net_control[8] = net, source, present, search_budget, static_words, sink_count,
reserved0, reserved0. Sinks are sorted canonical IDs, duplicates retained.
Global node/site/retention/edge ledgers must be initialized, valid, exclusively
owned and in the same domain as the immutable static snapshot image. The top
resets only the current net's tree and edges, preserving other nets and history.
All buffers disjoint. It uses the original search architecture, not width64.

Internal sequence:
1. Get retained old nodes; remove them from node ownership when nonempty.
2. Release site ownership; reset tree to source; clear this net's edge sequence.
3. Build the complete self-excluded snapshot from actual node/site ledgers.
4. Execute the internal sink loop (roots/patch/search/tree/edges/completeness).
5. Acquire final sorted roots; replace retained nodes; encode final demands and
   replace site ownership, including incomplete routes, matching the reference.

net_result[8] = error, stage, component_status, processed_sinks, found_count,
complete, final_roots, total_retained_edges. Error0 success,1 front preflight,
2 a later component rejected. Stages1 retention get,2 node release,3 site release,
4 tree/edge reset,5 full snapshot build,6 sink loop,7 node acquire,8 node retention,
9 site encode/commit,10 complete. `control_result` retains nested sink diagnostics.
Fields from stages not reached are not completion evidence. No cross-stage
rollback exists; errors after release can leave a partially updated net. Front
preflight checks common controls/state/domains/sinks, but full static validation
occurs in Snapshot after release. Failures must stop or enter explicit recovery.

The original search packet length scalar is removed: packet length comes from
Snapshot. Sink count comes from net_control. Extra ports expose immutable static
image, actual node/site ledgers, retention store, old-node scratch and net_result.
The source is the authoritative argument order/depth specification. Existing
separate-CU memory configurations do not describe this integrated entry.

CPU evidence uses full declared storage, both graph modes and C++14 ASAN/UBSAN.
It checks two reroutes of one net without duplicate ownership, literal ordered
edges and demands, preserved history, source-only commit on unknown semantics,
empty-sink completion without search, and reserved-control rejection without
new committed state changes. Fixture serialization uses existing word packing;
this is not a fully independent end-to-end real graph oracle. Full negotiated
random/real differential, later-stage error cases, actual HLS/RTL, physical
closure and platform/board measurements remain necessary.

Round decisions/history advancement, iteration over all nets and final trace
export still remain outside this top. This is not the complete hardware router.
