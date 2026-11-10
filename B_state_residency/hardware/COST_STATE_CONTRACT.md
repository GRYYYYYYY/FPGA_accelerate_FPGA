# Design-level cost state

`variants/cost_state_v1/cost_state_store.sv` is a standalone AXI512 service for design history, a 256-word present-price table and immutable net parameters. It is not joined to the candidate/pager/cost engine yet. Query activity and the decision lock are explicit external inputs; a future wrapper must gate query OPEN with `ready_for_query` and bind full version and design identity.

History is N raw little-endian u32 values, prices are 256 u32 values, and each net is a 16-byte record `[centerX_f32, centerY_f32, fanout_i32, doubleHPWL_i32]`. Regions must be 64-byte aligned, disjoint and fit in the 64-bit address space including rounded padding. Configuration is immutable after success; `design_id` is retained for outer consistency checks, but request packets do not independently verify a design ID. Backing contents must be imported before configuration.

| Op | Meaning | Requirements |
|---|---|---|
| 0 | GET history[index] | Published state, node in range |
| 1 | SET history[index] raw value | Host, editing, query and decision lock inactive |
| 2 | GET price[index] | Published state, index 0..255 |
| 3 | SET price[index] raw value | Host, editing, query and decision lock inactive |
| 4 | BEGIN edit | Host, no query/decision in progress, not already editing |
| 5 | PUBLISH edit | Host, editing, no query/decision in progress; full version increments |
| 6 | GET net[index] | Published state, net in range; full128-bit response |
| 7 | Invalid | No AXI side effects |

Every request carries cookie/index/op/host/query2/price4/version32 and responses echo them. PUBLISH's data contains the new full version while the echo version remains the accepted request version. Internal reads require an active matching query, a decision lock, an exact full version and price4 equal to its low four bits. Host reads require no active query or decision. The low four-bit price identity can alias; it never substitutes for the full32-bit version check. Version zero is invalid at configuration, and UINT32_MAX cannot publish to zero.

BEGIN fences all cost readers and query admission. Host SET commands are accepted serially; each succeeds after its actual B response, and publication waits until the previous response retires and all bus work is idle. Query-active during editing is a fault. There is no query/epoch-driven history clearing. These are in-place edits while readers are excluded, not rollback-capable transactions or concurrent snapshots. Net data is read-only after import. The service transports raw values; numerical updates of history/prices and net validity remain the producer's responsibility.

AXI requests are aligned64B single beats, IDs0. GET returns the selected u32 or128-bit record. SET uses exactly four byte strobes and never reads/modifies neighboring words. Already-presented AR/AW/W retain VALID/payload through abort or timeout. A logical error response may retire before physical drain; `busy` stays asserted until accepted traffic drains. New requests stop permanently on fault. An unowned bus response is a fault requiring coordinated external recovery.

Status0 success;1 op/index error;2 lifetime/edit policy rejection;3 version/query identity rejection;4 actual AXI error;5 abort/drift/fence/protocol/timeout fault;6 full version exhaustion. Rejected logical requests have no AXI side effects. Already-exposed response fields remain stable under late faults. A failed B or late abort can leave changed backing bytes. Recovery requires draining accepted bus traffic, resetting all linked owners and explicitly reloading design backing before reconfiguration; reset alone is not rollback.

Source-bound functional evidence is `results/cost_state_20261025/source_bound_audit.json`; boundary evidence is `results/cost_state_boundaries_20261025/source_bound_audit.json`. The real initial import comes from the original CPU loader and CPU price initialization (factor0.5), not a completed real routing iteration. Later mutations are scripted. There is no proof yet of integrated price publication/query OPEN coordination, route history arithmetic, complete search, synthesis or board behavior. Price index beyond255 must fail; do not silently clip an occupancy that the original fixed256-entry price array cannot represent.
