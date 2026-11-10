# Integrated search / tree / ordered-edge connection v1

`search_connection_top` calls the actual production SearchKernel, RouteTree and
RetainedEdges cores in sequence in one entry. It does not call the standalone
interface-bearing tops as subfunctions: interface pragmas appear only in this
top body. Search mode 0/1 is selected at compilation. This first version uses
the original search port-width policy, independently from the width64 experiment.

The original search 15 arguments retain ordering and depth. Six arguments follow:
tree_meta[5], tree_bits[16384], tree_demands[65], edge_meta[6],
edge_rows[37748736] u32, control_result[8] u64. All buffers disjoint/exclusive.
Search's raw path is the actual input to tree accept and edge append: no host
path decoding or intermediate copy is involved. Its declared depth stays
4194304 u32: search path count is bounded to 524288 by the search core before
use, so an edge helper cannot request its standalone 2097152-edge input here.
The persistent edge store retains the standalone 2097152 total-edge capacity.

Inputs include initialized trusted tree/edge state in the same domain as packet.
Packet word count and net/target widths are checked before search. Search input
validation otherwise remains in SearchKernel. Search statuses 5/6 abort the
connection. Statuses 1..4 pass through tree's non-found no-op contract, without
appending. Found results are checked/accepted by tree, then appended verbatim.

control_result = overall, stage, search_status, tree_status, edge_status,
applied, retained_edges, retained_version. Stage 0 preflight,1 search,2 tree,
3 edge,4 complete. Overall0 ok,1 preflight rejected,2 search rejected,
3 tree rejected,4 edge rejected. Only reached-stage result fields are meaningful.
Outputs initialize to zero. Preflight failure does not execute search. Later
failure can leave earlier state mutated: particularly edge failure can leave
an accepted tree. There is no cross-component transaction/rollback guarantee.

CPU evidence: `test_search_connection.py` freezes actual original search sources
and new tree/edge headers, compiles/runs both modes under C++14 ASAN/UBSAN,
checks original literal search outcomes plus full edge store tails, tree state
and non-found preservation. This initial test has two synthetic transactions
per mode; rejection branches and full negotiation/real workloads remain to test.
No HLS synthesis, RTL or device execution is claimed. This entry does not reset
nets, release/acquire ownership, build snapshots, emit roots, loop over sinks,
encode site requests or control rounds; these must be added for the complete
hardware router. Existing separate-CU memory configs do not describe this top.
