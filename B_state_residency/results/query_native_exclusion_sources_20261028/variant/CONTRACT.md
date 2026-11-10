# Query native interface exclusion candidate

Prepared only; no RTL validation or timing improvement claimed.

The default query_lifecycle retains its existing same-cycle request/reply exception. EXCLUSIVE_BACKEND_RESPONSES=1 removes request READY from the unexpected-response predicate only; query_residency_system explicitly enables it for its native service/search/route interfaces. No sequential block, error priority, timeout or retirement predicate changes.

Source-bound two-state analysis is results/query_native_exclusion_20261027.json. Native fence lane responses and admission are exclusive, the selected service lane is identical for both qualifiers, and search/route request/reply states differ. Generic overlap counterexamples remain in results/query_ready_path_hypothesis_20261027.json. This is not X/Z or sequential formal verification.

Required before selection: native legal/default baseline comparisons; deliberate overlap negative behavior; full-system cycle observations of all three actual interface pairs, exact 27-file/cycle regression, and matched OOC diagnostics. Keep existing eight-case native-retirement matrix and OFF synthesis unchanged. Do not submit duplicate or concurrent behavioral jobs. Archive actual results and restore/re-audit before claiming validation. The candidate may not improve the worst path; measure it.
