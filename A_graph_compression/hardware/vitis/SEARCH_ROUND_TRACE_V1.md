# Exact round snapshots, version 1

CPU reference implementation only; no integrated top/AXI or RTL verification.

`RoundTrace::write` uses frozen trace metadata and sticky all-or-nothing capacity
handling. Each record has 16 header words:
`[3,words,iteration,phase,nodes,nets,site_owners,site_history_entries,site_groups,0x7]`.
Here `0x7` means seven zero words, not the integer seven.
Phase 0 is after the round decision and before either history advance. Phase 1
is after both advances succeed, including the last allowed conflicting round.

Payload: control8, decision8, node_meta4, site_meta6, then `(count,history)`
for every node in the active domain, packed two-u32 completion flags per u64
(zero unused high lane), active site owners (four u64 each), active site
history (key,value), and conflict summaries (key,bad_owner_count).

The independent reader recomputes node and site conflicts, completion, penalty,
and decisions. It requires a phase1 for every conflicting phase0, checks exact
history increments and unchanged ownership/decisions, and checks bank/version
transitions. Site conflicts use signal exclusivity, per-owner conflicting
bit masks, and categorical differences, preserving compatible third owners.

This reader consumes round-only fragments. Search/net association, initial
batch state, error exits and terminal records are not yet a complete protocol.
`complete_batch` is always false. Diagnostic snapshot bandwidth and capacity
must be measured separately from release-kernel performance. Capacity failure
is sticky and must invalidate whole-run trace acceptance.

Fixture explicitly seeds node counts/history; it is not a claim of real prior
routing. Site owners and both history advances execute the production cores.
