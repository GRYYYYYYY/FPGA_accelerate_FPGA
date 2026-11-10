# Four-service search injection

This specialization builds on the sixteen-way static response selector in
`search_static_v2`. It preserves all sixteen HOST/admin services. Only the private
scheduler-to-service interface is restricted to the existing scheduler's four
lanes: control6, label8, expand11 and frontier12. The `issue` call sites in the
unchanged `search_scheduler_v1/search_scheduler.sv` use exactly those lanes.

While search owns the interface, the other twelve service VALIDs and reply READYs
remain zero. Their inactive payloads now pass through host data instead of
selecting the broadcast search payload. No consumer may interpret an inactive
payload as a transaction. Active search payloads (including all zero padding)
remain identical, and all host payloads/requests are unchanged when host is open.
Unsupported private scheduler lanes have READY=0/reply VALID=0 and send no backend
transaction. This is a fail-closed integration contract, not a generic sixteen-
service scheduler interface. Extending the scheduler to another service requires
explicitly extending this lane set and revalidating it.

The source generator derives this exact change; production scheduler, composed
top, all legacy components and real testbench are unchanged. Twenty composed
model cases pass, including cancellation-before-recovery handoff. Side-by-side
simulation checks 4096 reply bits for each of four legal lanes,256 control-gate
combinations per lane, every control output and every VALID payload, plus12
unsupported-lane rejection cases (17420 checks). It deliberately does not compare
invalid payload buses. The gate matrix compares host vectors while search is idle; it is not an
exhaustive enumeration of all host payloads. The host pass-through expressions
are also checked structurally against the reference. The real 32-slot and one-slot executions match v1 per cycle,
seven AXI logs and four complete images; CPU and owner lifecycle evidence remains
bound through the independently audited reference.

The existing limitations remain: external initial import, inter-query prepare and
route commands; CPU-known328-label union; no real search fault/rollback, complete
checkpoint, unknown-page/price-wrap/power-loss proof, placement/routing or board
measurement. Select this variant explicitly in `run_search_sparse_join.py`; do
not overwrite v1 or the response-only control experiment.
