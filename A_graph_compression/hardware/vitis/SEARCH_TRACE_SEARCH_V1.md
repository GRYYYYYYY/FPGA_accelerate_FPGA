# Exact search trace record v1 (writer core only)

`SearchTrace<Words>` is a synthesizable bounded u64 writer; default capacity is
16777216 words (128MiB). It is not yet connected to any batch top or AXI port.
No dynamic allocation, IO, callback or INTERFACE pragmas occur in the core.

Metadata8: magic0x4154524143453031, capacity_words, committed_words,
committed_record_count, sticky_status, transaction_version, zero, zero.
Reset succeeds only for positive capacity <=Words. Successful records commit
used/count/version only after the full payload is written. Rejected records
leave the entire data buffer unchanged; sticky_status records the first error
until successful reset. Status0 ok,1 invalid state/frame,2 capacity,3 version
overflow. There is no truncation-to-success or overwrite/wrap ring behavior.

Search frame8: type1, frame_words, iteration, query_index, target, root_count,
unknown_node_count, unknown_pip_count. Then:

- 81 exact search-result u64 words, including all65 demand-state words.
- ceil(root_count/2) u64, low u32 first; odd final high lane zero.
- Four u64 per raw8-u32 path edge, low u32 first. All tile/PIP/up/down/attribute/
  direction fields survive, including parallel edges and original order.
- Ascending u64 canonical unknown-node IDs (exact bitmap set, not a hash).
- Raw u64 PIP keys, preserving the supplied order and all32 bits per half.

Word count =89+ceil(roots/2)+4*path_count+unknown_nodes+unknown_pips.
The writer validates ABI/version, bounded counts, sorted/domain-valid roots,
path domains/direction, non-found zero-state contract, bitmap tail bits and exact
unknown-node cardinality before reserving/writing. It does not independently
re-run routing or prove that the supplied search result is correct.

Tests use literal path words to check packing and full payload retention,
including UINT32_MAX identities/attributes; unknown IDs cross a64-bit bitmap
boundary. They check first-error stickiness, capacity/version failures, malformed
roots/path/bitmap, no partial-frame writes, guard/tail preservation, two frames,
and an actual default128MiB allocation under C++14 ASAN/UBSAN.

This is record-level CPU evidence only, not hardware trace export. Net/round/
history/terminal records and an independent reader remain to implement. A metadata
status0 with valid frames does not establish batch completion: a complete protocol
also needs an explicit successful terminal event and complete event sequencing.
Diagnostic capacity exhaustion must stop and report failure; never silently drop
records or treat a prefix as full workload evidence. Trace overhead must be
measured separately from release-kernel performance.
