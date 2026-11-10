# Internal all-net / round control v1

`search_batch_top` derives from the actual net transaction and invokes all net,
sink and round operations internally. Only the outer top carries INTERFACE
pragmas; nested net_worker/sink_loop_worker have none. This entry uses the
original search width policy, independently of packet64 experiments.

batch_control[16] = present_cap, max_iterations, query_count, sink_pool_words,
static_words, search_budget, reset_state, nine reserved zeros.
Query records are four u64: net, source, first_sink, sink_count. Input query
order is preserved. Maximum 65536 records, 4194304 pooled u32 sinks; each query
has <=1048576 sinks. IDs/domain/offset/count/sorted sinks and reserved control
words are checked before reset. Unique net IDs, protected/reserved-terminal
consistency and full immutable graph/static input provenance must be validated
by the input adapter once. They are trusted input contracts, not implemented by
this top's numeric preflight. It does not sort sink lists or drop duplicates.

reset_state=1 resets global node/site/history/retention/edge state, matching a
fresh negotiation; tree resets per net. reset_state=0 starts iteration0/present1
from trusted existing ledgers, useful for explicit state tests; it is not a
resume-at-arbitrary-iteration API. Search workspace/meta is caller-owned and must
be initially zeroed or valid. Reset ownership state does not reset search epoch.

For each round, each actual net transaction updates ownership/site/retention and
writes its completion flag. Site::analyze plus actual RoundControl consume raw
node counts and flags. With conflicts, both histories advance even on the final
allowed round. With no conflicts, stop immediately, routed iff all nets complete.
Present penalty remains min(2^min(iteration,20),cap). No host decision intervenes.

batch_result[12] = error, stage, core_status, rounds, net_calls, searches, found,
routed, incomplete_nets, node_groups, site_groups, history_advances.
Error0 means the negotiation ran normally (routed may still be0);1 invalid input,
2 initialization/state,3 net failure,4 site analyze,5 round control,6 node advance,
7 site advance,8 unexpected fallthrough. Stages0 preflight,1 init,2 nets,3 analyze,
4 round decision,5 node history,6 site history,7 terminal. Nested net_result and
control_result retain the last reached operation. Failures are not incomplete
negotiation outcomes and offer no global/cross-stage rollback.

Outputs retain final ledgers, completion flags, last tree/search and decisions.
Per-query/per-net/per-round trace export is not implemented in synthesized logic.
CPU observation callbacks and physical trace capture remain separate work.
Existing separate-CU configs and XRT runtime do not implement this top's ABI.

Both-mode C++14 ASAN/UBSAN tests use complete declared storage. They cover a
fresh routed two-query schedule with duplicate sinks, immediate incomplete stop
on unknown semantics, preflight rejection, and two persistent-conflict rounds
with final history advancement. The persistent foreign owner is explicitly
seeded as valid component state, not generated from a real full routing history.
These are synthetic control tests; full native differential, actual HLS/RTL,
physical timing, platform allocation and board performance/power are not proven.
