# KA system reachability obligations

The failed full v6 run remains failed. The two unit experiments do not discharge
its nonempty KA-stall requirement. No acceptance gate is changed by this plan.

The property of interest is a cover of `k_a_valid && !k_a_ready` using actual
production RTL, followed by successful recovery with the same accepted payload.
A trace that only reaches a permanent fault or an illegal AXI response is not a
successful finite-backpressure scenario.

## Required control cone

- Recovery coordinator, authority rotator, both authority readers and codecs.
- AP ownership, checkpoint lease guard, publication barrier and their actual
  admission equations.
- Authority configuration lease, rearm, retirement and recovery admission.
- AXI outstanding-request bookkeeping; responses must correspond to accepted
  requests and obey AXI payload persistence. Unsolicited response valid cannot
  be used to manufacture a stall.

## Assertions and covers to establish

1. Starting from reset and successful configuration, cover first recovery AS,
   authority transfer, response retirement, next AS, and successful completion.
   This establishes non-vacuity of the setup assumptions.
2. Check lease and AP exclusion across transitions, including simultaneous
   acquisition, release, recovery offer, and authority configuration pins.
3. Check rearm-to-DRAIN retirement and configuration-response consumption.
   `k_rcfg_done` is config-restore completion, not authority ready.
4. At every AS entry, inspect each reader/rotator ready blocker separately:
   configuration, publication, discard, rearm, active bank, configured, fault,
   drained, codec busy, and pending configuration response.
5. Cover finite KA stall followed by acceptance and complete recovery. If absent,
   distinguish a bounded no-cover result from an inductive unreachability proof.
6. Repeat with allowed faults and aborts; classify timeout/failure traces
   separately. Do not constrain away a real bug to obtain an invariant.

## Soundness controls

Use actual source bindings and hashes. Record all environmental assumptions,
black boxes, abstractions, parameters, reset depth, and bounds. A reduced control
cone must overapproximate the real system for a safety proof; a cover in an
overapproximation needs replay against the complete actual RTL before it is
accepted as reachable. Assumptions copied from the desired property are invalid.
Mutating a relevant admission guard must invalidate the associated assertion or
produce a counterexample, establishing that the harness checks the intended cone.

No full-system or physical acceptance follows from tool installation, parsing,
SMT generation, a bounded no-cover result, or the existing unit PASS markers.
