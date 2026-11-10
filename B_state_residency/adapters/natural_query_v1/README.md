# Natural prepared-query capture v1

`derive.py` inserts observations in the frozen original serial Router. It preserves all original operations; applying `changes.json` backwards recovers the input source byte for byte. The only selected query is sequence 1 with B_NATURAL_QUERY set. Unsupported sparse, lazy, locked or private label contexts fail explicitly.

The capture point is immediately after `prepareRouteConnection`: rip-up and target setup have happened, and the source seed is already in the logical queue. Search-final snapshots are taken immediately after the search loop, before path saving, occupancy commit or target cleanup. They are not final committed connection state.

All `.u32` files use 32-bit little-endian words on the recorded x86 host. Negative IDs use two's complement and floats use binary32 raw bits. No native struct padding or pointer representation is serialized.

`initial_nodes.u32` and `search_final_nodes.u32` have 11 words per node in original global node-ID order: lb, upstream, historical congestion, prev, visited, target, ownerNet, ownerCnt, occupancy (distinct nets), created, mutable RouteNodeType. Owner IDs retain original CPU semantics (-1 empty, otherwise zero-based net), unlike the FPGA codec's net+1 keys. Reference counts are not occupancy. Full snapshots cover every node, not just visited nodes. `initial_overflow.u32` contains (node, net, references) triples; `initial_caches.u32` contains repeated (parent, length, children...) records in original cached order. Prices contains all 256 binary32 congestion table entries. Heap files contain (key bits, node) pairs in logical backing-array order, limited by queue.sz. `state.txt` records actual query weights, factors, bbox, net geometry, flags, targets and landmark sink entries.

`events.txt` records:

- P: node, lb bits, logical size after actual poll.
- E: expanded parent, filtered degree, logical queue size.
- K: parent and each cached/constructed child, in original order.
- C: parent, child, position, pre-decision lb/upstream, prev/visited/target, mutable type and created.
- W: child, prev, committed lb/upstream/visited/target, lookahead, queue size before its actual offer or recursion.
- END: pops, found, aborted, logical queue size.

W observes the original push after prev/lb/upstream/visited have been written. A target EARLY has already cleared the queue before W. Source push occurs before capture, so it is in the initial heap and labels, not a W event. Events do not explicitly distinguish each rejection reason or log cost intermediates. Static graph and original configuration are bound to the source/input hashes in the manifest; the snapshots alone do not embed a standalone graph.

`audit_natural_query.py` reconstructs the label chronology and the original 8-ary heap including target CLEAR, checks all changed full-node records, and verifies historical congestion, owners and occupancy remain unchanged throughout this search. This audit does not independently recompute costs or child filtering.

`make_replay.py` constructs a separate driver: load the original RRT, restore snapshots, caches, costs and prepared State, rebuild HotExpand from restored data, then run the original search-loop text and actual Router expansion/cost/push methods. The prepared snapshot is not passed through prepare a second time. Replay requires no landmarks, no dead-end pruning and the recorded serial eager graph context. Its success gate is byte identity of nine captured files, including every event and full initial/final node snapshots. This proves the selected natural query can be reproduced by the CPU implementation; it is not an RTL or board performance result.

## Hardware image export and independent natural oracle

`derive_cost_inputs.py` adds a read-only 23-input/5-result cost observer to the exact replay. `export_inputs.hpp` writes full design/owner/history/net/state/native-label images before search. It rejects warm caches, overflow owners, landmarks, lazy graphs and pruning rather than silently dropping state. The static graph remains the bound original `graph_image_20261024`. `audit_natural_query_inputs.py` independently decodes every full image and recomputes all 171 binary32 geometry/cost packets. `verify_natural_query_filters.py` independently replays natural eager filtering/access and emits a conservative 308-node/111-page label import/readback footprint. These files are CPU-verified hardware inputs, not a natural RTL search result. Full native160 labels require host import or a separately validated pager encoder; they are not a pager backing image. See results/natural_query_inputs_20261025.md.
