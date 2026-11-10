# Internal multi-sink loop v1

`search_sink_loop_top` extends the original search arguments plus the six
connection-state arguments with `sinks[1048576]` u32 and scalar sink_count.
Roots and packet are mutable: the top emits roots from the live tree and calls
ProductionResidentSnapshot's query-patch operation before each search. Actual
SearchKernel, RouteTree acceptance and RetainedEdges append execute internally.
The final tree completeness and ascending roots also come from the actual core.

Input is an initialized trusted tree/edge store and a previously built, trusted
snapshot for the same net/domain and fixed round penalty. Sink IDs must already
be in ascending order; duplicate IDs are retained. This version rejects unsorted
input rather than sorting. Net release, initial tree reset, full snapshot build,
node acquisition, retention replacement, site commit and round decisions remain
outside this top. It is not the full hardware router or a complete net transaction.

Every sink, including duplicates and already-reached sinks, executes the original
search path. Found empty paths still invoke tree acceptance and edge append,
preserving their version semantics. Search outcomes 1..4 are algorithmic non-found
and preserve tree/edge state; statuses 5/6 abort. Empty sink lists complete according
to the original all_of semantics and emit roots without executing a search.

control_result[8] = error, stage, successfully_processed_sinks, found_count,
complete, final_root_count, retained_edge_count, retained_version.
Error0 success,1 preflight,2 root emission,3 packet patch,4 search rejection,
5 tree rejection,6 edge rejection,7 final completeness/root emission.
Stages0 preflight,1 roots,2 patch,3 search,4 tree,5 edges,6 final.
Later-stage summary fields are meaningful only when reached. `result[81]` is the
last actually executed search; no-search calls preserve it. Initial buffers must
be disjoint/exclusive. No cross-stage rollback exists: a failed later operation
may leave prior roots, packet, workspaces, tree or edges changed. Failures must
abort or enter an explicitly designed recovery path.

Query patch invokes the unchanged Snapshot::run with constant patch opcode.
Its unused build-only arguments point to local dummy words. These are never
read by patch; HLS must be checked to ensure the dead build path is eliminated.
This does not change full declared depths of active top-level AXI ports.

CPU test covers both modes under C++14 ASAN/UBSAN, sorted sinks [1,2,2], literal
retained edge records, live tree/root/packet query state, empty sinks, preflight
rejection of descending and out-of-domain sinks, and unknown semantics remaining
incomplete. It does not yet compare complete real negotiated routes or RTL traces.
Actual HLS is a separate flow; there is no physical/platform/board proof yet.
Existing separate-CU memory plans do not describe this new integrated top.
