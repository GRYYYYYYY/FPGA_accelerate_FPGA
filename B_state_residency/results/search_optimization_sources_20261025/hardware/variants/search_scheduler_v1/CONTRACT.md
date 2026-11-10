# Prepared-query autonomous search v1

`search_residency_system.sv` wraps the previously audited `residency_system` with a
search scheduler and a whole-query host lease. `build_join.py` regenerates this
structural wrapper/interface and the real-service testbench. The synthesizable
modules contain no file agents, oracle access or design-specific node constants.

The caller prepares/opens the connection and supplies one accepted descriptor:
source/key/node bound/max polls, cookie bases, design/query/price identity, and the
448-bit lane-11 expansion template (connection, sink, net, sequence, geometry,
flags and version). The scheduler captures all fields. It obtains each parent
from the actual heap, reads that node's actual label, tests target identity and
visited sequence, and issues the next actual expansion. Candidate retirement is
consumed locally. It seeds an empty heap, then executes POLL→LABEL→EXPAND until a
valid target; a nonempty remainder triggers CLEAR before CHECKPOINT and physical
backend drain. Cookies track each request. A zero poll limit is invalid. Failure
to find a target, poll bound or cycle bound is an error, not successful routing.

Admission requires active matching identity, idle/drained services, recovery
permission and no competing host/route/recovery VALID. After admission all 16
host lanes and route submission are blocked, including gaps between requests and
held completion. Search owns candidate consumption. Recovery intent cancels the
search, but recovery acceptance waits until its completion is consumed. A search
fault locks normal traffic until service target reset; the independent cold
journal domain is preserved. Diagnostic injection defaults off.

| Status | Meaning |
| --- | --- |
| 0 | Target validated, checkpoint complete and services drained |
| 1 | Descriptor invalid; no service request issued; reusable |
| 2 | Poll count bound |
| 3 | Empty frontier |
| 4 | Frontier reply/cookie/node/size error |
| 5 | Label absent/status/key mismatch |
| 6 | Target node or visited sequence mismatch |
| 7 | Expand/checkpoint reply error |
| 8 | Cancellation, backend fault or identity drift |
| 9 | Candidate retirement error |
| 10 | Cycle bound |
| 11 | Unexpected reply/state |

For an already offered request, cancellation/timeout never withdraws VALID or
changes its payload. The scheduler waits for acceptance/reply and physical drain,
then holds completion until consumed. Consequently a permanently unresponsive
backend may prevent completion indefinitely; the timeout is containment, not a
hard completion deadline. Dirty-heap detection follows the seed response (size
must be one), so a failure may already have modified the heap. There is no search
rollback, durable journal of all search writes, or autonomous reset/reload here.

Validation: 20 scheduler model scenarios and the same 20 through the host lease;
the latter contends all16+route and checks recovery cancellation/handoff. Real
service tests perform two CPU-captured queries with 32-slot and single-slot label
caches, passive oracle scoring, and four shared-owner commit/ripup commands.
Real search tests do not inject backend faults, and their target POLLs leave the
heap empty; nonempty-target CLEAR is covered only by the model test. All seven
AXI logs/four final images equal the audited host-driven reference. The second
query's 43 label-read payloads differ only in an unused write-value field (old
TB retains 2; scheduler uses 0), explicitly checked by the independent auditor.

Initial 328-record import, inter-query five-field preparation, authority/snapshot
production and route command scheduling remain external. Route-only recovery
journal and known-page limitations persist. There is no full search snapshot,
unknown-page proof, price wrap test, routed timing or board acceleration result.
