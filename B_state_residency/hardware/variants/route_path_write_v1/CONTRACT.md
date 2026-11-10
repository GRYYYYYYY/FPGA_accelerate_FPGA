# Same-cycle route path write factoring

The candidate branches from checkpoint_edit_synth_v1, not the rejected label
exclusion mapping. FACTORED_PATH_WRITES defaults to zero in the controller;
the candidate adapter explicitly enables it.

Only path-bank write implementation changes. The enabled branch uses static
per-slot/per-word registers driven by the original checkpoint publication and
ordinary path-write events. It adds no state or cycle. CRC, final verification,
duplicate detection, cancellation, drift, metadata publication and reply logic
remain present. The original default write implementation stays available.

The source-bound Boolean model is not RTL formal or X/Z equivalence. Twelve
controller tests passed, including original route and checkpoint8/32 stimuli,
same-cycle generic replies and exact per-word bank changes/cycles. Actual
archive restoration and re-audit passed. These are bounded modeled-backend
tests, not arbitrary input or parameter proofs.

Full-system acceptance requires the real four-slot/32-word old-tree reference
bank, all prior monitors, 27 exact outputs/finish cycle, independent audit and
actual archive restoration. Matched OOC must measure any timing/resource
benefit; a simpler RTL structure alone does not establish an improvement.
