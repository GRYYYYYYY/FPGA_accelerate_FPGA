# Six-component shared-buffer candidate

This version adds `search_site_request_top` to the frozen five-component v1 plan.
The encoder reads the same BO as tree.demands/snapshot.initial and writes the
same BO as site.request. Its two-word result is the only new allocation: after
4 KiB alignment, 58 pointer arguments map to 42 unique BOs requesting
632774656 bytes (603.46 MiB). Nominal HBM use remains 23 channels.

Generation reuses the v1 source/XML/synthesis checks and additionally verifies
the audited encoder source and its two AXI bundles. Independent audit recomputes
unique sizes, alias/bundle consistency, disjoint pool capacity and exact config
lines. Ten corruption cases include incompatible encoder state/request banks.
Both configs are static candidates; installed platform topology, exported XO
ABI/control offsets, v++ link and simultaneous device BO allocation remain gates.

The encoder's record count still needs outer control before site replace.
Retained per-net routes, old-node marshalling and the full hardware negotiation
scheduler remain outside this inventory. Shared mutable buffers require one
owner and completed producer events before any consumer access. Numeric XRT
group IDs alone do not prove a common physical memory group.

The full-depth encoder RTL verification establishes 34 synthetic transactions
against its independent literal/map oracle, not device residency or whole-router
RTL traffic. Consult `results/site_request_rtl_audit_20261024_v2.json` for the
corrected postcheck description; the original v1 run/report remains retained.
