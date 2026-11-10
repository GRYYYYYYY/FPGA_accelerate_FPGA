# Remaining outer control requirements

Reference behavior is the frozen retained-nodes router's `site_routes.hpp`.
The seven-component connectivity candidate specifies memory sharing; it does
not implement cross-component start/done control or a hardware scheduler.

For every net and round, preserve this sequence:

1. Retention get; release its sorted old nodes if nonempty; release site demands.
2. Reset tree to the source; build the self-excluded node/site search snapshot.
3. For every sink in ascending canonical-ID order: emit roots, patch target/count/
   budget/initial demands, execute search, accept the raw result/path into tree.
   Keep duplicate sinks. Algorithmic non-found outcomes leave the tree intact;
   component validation failures and invalid search input are errors.
4. Check completion using the original sink list; emit final roots; acquire node
   occupancy, replace retention, encode demands, and replace site ownership.
   Preserve the established per-operation failure contracts. This sequence does
   not currently offer atomic rollback across all components.
5. After all nets, observe node and site conflict counts plus incomplete nets.
   With no conflicts, terminate immediately: routed only if none is incomplete.
   Otherwise advance both histories, even on the final allowed round, matching
   the existing loop. Present penalty is min(2^min(round,20), present_cap).

Node occupancy currently exports conflict count as part of advance, which
mutates history/version. It has no standalone nonmutating conflict-count opcode.
The scheduler must count trusted resident node_counts>1 without advancing, or
use a separately versioned read-only operation. Snapshot's other-owner count
for one querying net cannot substitute for the round's global conflict count.
Site analyze already has a read-only operation and handles compatible owners.

The scheduler must consume actual bounded results: old/new node counts, root
count, packet length, search status/path count, tree completeness, encoded site
request count and conflict counts. It must not infer these from host result
maps or overwrite a capacity error with an incomplete/routed outcome. Native
observational traces may be streamed out, but must not drive live state.

A complete device implementation also needs explicit ownership/completion
signaling between stages. Emitting a command list for the host to execute is
a useful transport test, but does not establish autonomous PL control. A single
integrated top or a verified RTL/control wrapper is a candidate; neither is
implemented by the current seven-CU memory configs. Exported control ABI for
two CUs alone does not prove the entire control path.

Validation must compare all intermediate statuses, paths, costs, unknown
resources, demands, round conflicts and final completion with the native
reference; retain full capacities and real workload settings. Standalone RTL,
static memory capacity and CPU differential results remain separate evidence
from integrated device execution, timing, bandwidth and power.
