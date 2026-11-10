Native twelve cases audited and actually restored; 55 files frozen in results/query_native_exclusion_sources_20261028. Full-system integration and timing measurement pending. Do not modify bound candidate/tool sources.

12 cases compiled/elaborated in query_native_preflight_v1; not simulated. See results/query_native_preflight_20261027.json. Independent auditor prepared but not executed.

# Prepared verification, not submitted

build_tb.py adapts the existing lifecycle test with explicit inactive checkpoint/rebase connections. Twelve cases cover baseline/default/exclusive across the unchanged legal regression and three externally injected request-acceptance-cycle replies. No force/deposit. Normal cases monitor all three READY/reply VALID pairs; injected cases require exactly one injection. Baseline/default events must match in all four scenarios, and exclusive legal events must match baseline. Exclusive injected replies must cause status7, retaining route commit semantics when the route completed.

scripts/run_query_native_exclusion.py generates fresh bounded XSim builds and requires PASS/finish/no fatal plus five exact event comparisons. It refuses launch before the existing full-system matrix is observed/complete and enforces 75% memory admission. All twelve TB texts were generated in memory and Python syntax parsed; no RTL compilation, elaboration or simulation yet. Do not count these as passed tests or as a submitted queue. Independent source/event audit and archive/actual restoration remain to implement after actual run evidence.
