# Diagnostic complete-batch entry, version 1

`search_batch_trace_top` is a separate generated diagnostic entry. The original
batch source and experiments are unchanged. It adds three pointers: trace_control8,
trace_meta8, and trace_data16777216 u64 (128 MiB), all on trace_mem. No INTERFACE
pragma appears in internal workers. Existing 42 arguments retain their order.
The extra trace budget is not part of the release-kernel performance baseline.

trace_control = [capacity_words, seven zeros], positive capacity <=16777216.
The metadata is reset per call. All inputs, mutable workspaces and trace buffers
must be disjoint as in the source-only original buffer contract. Invalid trace
control returns batch error9; invalid capacity does not initialize trace metadata.
Begin-frame rejection returns error9 before routing. Later trace failure is sticky
and stops further record commits, while the original routing continues and keeps
its original result. Therefore success requires BOTH routing validation and trace
metadata/terminal acceptance, never batch_result alone.

BEGIN type4: header8=[4,words,1,nets,sink_pool_words,0,0,0], batch_control16,
query_table4*nets, packed complete sink pool (two u32 per u64, zero high padding).
SEARCH type1: frozen v2 ABI, query ordinal=(net_query_index<<32)|sink_index,
including duplicated sinks, captured immediately after each actual SearchKernel.
NET type2: exact committed net snapshot after successful net_worker return.
ROUND type3: exact pre-advance and, when required, successful post-advance records.
TERMINAL type5: header8=[5,20,1,0,0,0,0,0], followed by raw batch_result12.
Errors produce terminal diagnostics when trace capacity allows, but the current
mixed reader intentionally rejects routing-error terminals as unverified runs.

Independent read_batch_trace checks scheduling, roots, exact retained paths and
demands, complete flags, per-net/round ledgers, full histories, decision order and
terminal totals. A reset_state=1 successful trace is accepted as complete_batch
for this synthetic CPU diagnostic protocol. Seeded reset_state=0 has no exported
initial ledger proof, so complete_batch remains false even when observed events
are internally consistent. This is not full experiment completion, algorithm
correctness proof, HLS/RTL equivalence, timing closure or device performance.

Validation uses unchanged original production-capacity CPU batch tests in both
graph modes with ASAN/UBSAN; actual exported binary frames are read independently.
The four cases are fresh routed, explicitly seeded persistent conflict, incomplete
no-conflict stop, and invalid preflight. No top HLS/RTL or device result yet.
