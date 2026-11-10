# Native-interface specialization and capture retirement

Compose the unchanged four production files of recovery_backend_loops_v2 with
the one-file capture_retirement_loops_v1 change. The reference is the restored
route_block CRC pressure case. There are five changes versus that reference,
ten unique production changes versus the original restore-seed reference.

Both parent contracts apply. Generic backend mode still defaults off. The
capture retirement condition retains zero depth and all other service/arbiter
retirement gates, dropping only the implied absence of a native capture reply.
No sequential logic or runtime stimulus changes.

The full TB adds observation-only checks of both backend READY/reply exclusions,
their completed request counts, capture zero-depth/result exclusion, and exact
equality of the complete original capture retirement predicate at every sampled
cycle. Nonzero capture depth and actual result VALID must be seen. Original 27
artifact bytes, native event cycles, numerical oracle and finish time must equal
the restored reference. Additional coverage markers do not replace those checks.

Do not describe the candidate as behaviorally or structurally accepted before
its own terminal audit. Full-root synthesis must use production sources only;
the monitors are not synthesized. A local identity does not establish X/Z
equivalence, all-state sequential proof, physical timing or board benefit.
