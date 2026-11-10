# Search error retirement (isolated variant, 2026-10-25)

`build.py` derives ten production RTL files from the frozen `results/query_lifecycle_join_v2/sources` and the previously verified `query_recovery_v2` top. It does not modify the original reference. The result directory's frozen builder and source hashes identify the revision; directory suffix v6 is the current candidate. Check the final result report before treating a candidate as validated.

## Ownership and completion

- A fault must not retract an exposed request or reply. Capture retains exposed child data/context and completion payload through backpressure. Unexposed children may be discarded after producer retirement. Error frames unwind through ordinary parent result handshakes.
- Expansion preserves graph/design/label SEND and WAIT states on fault. An accepted children HLS service receives an error reply and is allowed to finish. Its controller and call wrapper export actual retired-idle independently of sticky fault.
- Candidate prefetch, post-input, cost, commit and offer stages retain exposed commands. A failed candidate becomes consumable only after every started stage has a reply and no exposed command is waiting for acceptance. Unstarted downstream stages are not prerequisites for a failure reply.
- Coordinate service retires its accepted graph/label/table request before returning an error. The core retirement predicate also includes internal arbiters, capture depth, children HLS and pending native replies. Outer query completion still requires parent retirement, all physical AXI observers drained, and the existing service retirement checks.
- The parallel connection descriptor request may fail before valid metadata is available. Its failed parent completion is permitted only after the accepted descriptor lease retires; requiring successful metadata in this branch would deadlock. Cancellation cannot suppress an unaccepted exposed descriptor request.
- Directory memory leases intentionally pin frames after an error until coordinated recovery. They are not counts of in-flight requests. The checkpoint `draining` indicator includes a persistent fence. Neither is required to become zero before recovery; they are not reset early to manufacture completion.
- The existing route fix permits an already retired adapter with a sticky fault in fence BLOCKED. Other retirement and physical drain requirements remain.

## Evidence and invocation

```
python3 hardware/variants/search_fault_retire_v1/build.py
python3 hardware/variants/search_fault_retire_v1/build_tb.py
python3 scripts/run_query_fault.py NEW_RESULT --search-fix
python3 scripts/audit_query_fault.py NEW_RESULT
python3 scripts/run_query_fault.py NEW_DEEP_RESULT --search-fix --deep
python3 scripts/run_search_retire_join.py NEW_NORMAL_RESULT results/natural_query_inputs_v1
python3 scripts/audit_search_retire_join.py NEW_NORMAL_RESULT
```

The base matrix injects one real AXI SLVERR into source-label read, pressure prepare writeback, graph read, cost read, owner commit write or cleanup writeback. Deep cases use graph response ordinals 24 and 100, and cost ordinal 10, under both capacities. Unit tests cover normal nested replay and nine fault/abort/overflow/identity/held-output scenarios. A runner's `observed` status alone is not a pass: the independent audit requires recovery and complete CPU-matched retry for this variant. Failed development revisions remain evidence.

## Scope

This is behavioral XSim with real graph/connection/cost inputs and generated HLS RTL, plus out-of-context synthesis when recorded. It is not a board measurement or a general formal liveness proof. A permanently nonresponding backend can still prevent completion.

Recovery uses a trusted initial snapshot of 328 known labels and authority for the six q1 interior owner rows. Owner repair is checked before retry; the whole final owner image must equal exactly one CPU commit. Design backing is retained. Changing epoch/price identity does not change actual cost values in these tests. No fault is injected during recovery itself. Arbitrary reroute, unknown-page snapshot coverage, complete warm-cache/frontier/path checkpointing, real price changes, wraparound, capacity exhaustion and durable recovery remain outside the evidence.
