# Route label response exclusion candidate

Prepared only. No compile, simulation, synthesis or timing result yet.

The actual native label chain uses the five-client service_arbiter host lane 2.
Request READY is qualified by IDLE; reply VALID by WAIT_REPLY. Recursive core,
engine and route adapter masks only restrict these signals. The source-bound
two-state analysis checks 4096 chain valuations and 96 route predicates.
This is not an RTL formal or X/Z proof.

LABEL_RESPONSE_EXCLUSIVE defaults to zero in both controller and adapter.
Only residency's existing default-off EXCLUSIVE_BACKEND_RESPONSES flag enables
the label specialization. A generic LS/label-ready/label-reply overlap is an
explicit counterexample: the original permits it; specialization reports an
unexpected response. Never enable this option for an arbitrary backend.

Only the label unexpected-response expression changes. The owner expression,
all sequential logic, CP safety/drift, cancellation and publication stay intact.
The separate owner_pending hypothesis is not proved or applied here.

Before selection require preserved default route/checkpoint regression,
native legal and generic overlap cases, actual label port monitoring through
the complete system, exact output/cycle replay, archive actual restoration and
matched OOC. Earlier CP/query matrices and OOC cannot establish these results.
