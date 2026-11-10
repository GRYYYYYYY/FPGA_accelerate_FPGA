# Single-target query lifecycle

The `query_residency_system` structural top composes the unchanged search system
(using `search_sparse_v3/search_host_fence.sv`) with `query_lifecycle` and a whole-
command ingress lease. New public ports use `qc_*`; legacy `q_busy/q_fault` are
connection-service outputs and must not share drivers. The builder rejects port
name collisions. One accepted command supplies the source, single sink/net and
expansion descriptor, sequence, route slot and cookies.

Successful command stages:

1. Validate descriptor, active design/query/price/version, empty saved route slot,
   nonzero sequence and poll bound. Source key must be zero. Sequence increases
   strictly between commands in the same context; context changes or wrap require
   proper target reset/reinitialization, not silent reuse.
2. Read source label and require present/root-prev `0xffffffff`.
3. Set sink target=1; source lower-bound=0, upstream=0, visited=sequence. Other
   labels, predecessor fields, design occupancy and congestion history survive.
4. Launch the real search controller and consume its checked completion. Parents
   and path costs come from actual heap/graph/labels, not CPU scoreboards.
5. Submit the existing route controller automatically. It validates the full
   predecessor chain and applies journaled owner increments to interior nodes.
6. Clear this sink's target, CHECKPOINT the labels, and wait for service/AXI drain.
   Hold completion, counters and the ingress lease until the caller consumes it.

Initial graph/design/owner/configuration and label import remain external. The
first imported target set must be empty or contain only this first command's
sink. Alternate target sets are not supported by the current single-sink search
interface. Each successful command removes its own target before completion, so
consecutive successful commands do not retain an old target. External label
writes after the first accepted command mark the lifecycle's label assumptions
dirty; subsequent autonomous commands return invalid-descriptor status until a
proper reset/reinitialization. Such external requests still retire normally.
Saved-slot reroutes must first use the existing explicit ripup command; this
component does not silently overwrite an occupied saved path.

The outer lease blocks all16 host requests and manual route commands through
prepare, search, commit, cleanup and held response. Only lanes8(label) and6(control)
receive outer-controller payload injection. Inner search uses its four-service
lease. Recovery intent cancels the lifecycle, but recovery is forwarded only when
the lifecycle response has been consumed. Existing recovery callbacks remain
inside the backend and do not depend on the blocked host interface.

| Status | Meaning |
| --- | --- |
| 0 | All stages, target cleanup and physical drain completed |
| 1 | Invalid descriptor/context/sequence/occupied slot or external label edit; no new service operation |
| 2 | Source absent or predecessor not the root sentinel |
| 3 | Prepare/source-check service error |
| 4 | Search result/status/cookie/target error |
| 5 | Route result/status/cookie/ack count error |
| 6 | Target cleanup or final checkpoint error |
| 7 | Cancel, backend fault, context drift or unsolicited reply |
| 8 | Overall cycle bound |

`rsp_detail` retains the latest child status; confirmed label-write and route ACK
counts are reported even on failure. `rsp_committed` means a native route reply
reported status0 with the matching cookie. It is conservative evidence of a
commit, not success on its own: an inconsistent node/ACK count can still make the
outer result fail. Only outer status0 establishes complete lifecycle success.
A failed AXI write may also have an unacknowledged physical side effect, so zero
ACK/commit flags do not prove untouched memory. Existing route journal semantics
and external authoritative recovery still apply.

Cancel/timeout never withdraws an exposed label/search/route request. In particular
an offered-but-unaccepted search descriptor is allowed to be accepted before
propagating cancellation to the inner search. An already offered route can finish
committing before cancellation is reported. Cleanup is skipped on failure, normal
traffic stays locked, and there is no rollback. A permanently unresponsive backend
may prevent completion indefinitely; timeout is containment, not a hard deadline.

Validation:28 model scenarios plus two full real-service executions (32-slot and
single-slot). The real tests send one command per query, mutate command inputs
after acceptance and contend all16 host lanes+manual route during ownership. CPU
files only score search/cost/path/results. Each final328-label readback expects
its sink target cleared, matching CPU post-route cleanup; the original dumps were
captured before cleanup. Independent audit reconstructs both full prepared states,
all1650 host label writes, seven AXI byte streams, complete design/owner/page
images, and four shared-owner commit/ripup states. Real lifecycle faults/recovery
are not injected yet;28 model tests are not a substitute for them.

The known328-label union, external initial import/authority/snapshot and explicit
ripup scheduling remain. Journal covers route-owner writes only; source/target
prepare and search need authoritative label restoration. Complete search
checkpoint, arbitrary pages, alternative sinks, price/sequence wrap, arbitrary
reroutes, power-loss safety, placed/routed timing and board acceleration remain
unproven. Do not equate the checkpoint lane command with a full recoverable snapshot.
