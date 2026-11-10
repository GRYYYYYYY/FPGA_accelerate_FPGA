# Checkpoint stage-bank write factoring

This candidate branches from the restored route_path_synth_v1 area result.
The CP version remains the timing reference. The new FACTORED_STAGE_WRITES
controller parameter defaults to zero; the candidate adapter enables it along
with the already tested FACTORED_PATH_WRITES option.

Only cp_stage register write implementation changes. Static per-word processes
receive export-capture or accepted import-word events. The original nested
if/else tree is retained, including reset, design/size validation, cancellation,
fault, drift, stream handshake, index and last-word checks. There is no added
state, cycle, stage initialization or changed CRC/publication/reply behavior.

Acceptance requires baseline/default/enabled comparisons using original route,
checkpoint8/32 and same-cycle reply stimuli. Every path and stage bank change
must match in data, index and cycle. An old-control-tree stage reference must
also compare all words after each clock, including failures and partial imports.
These are bounded behavioral checks, not formal equivalence for arbitrary
parameters or X/Z inputs. Full system and matched OOC remain required before
any timing/resource claim; compare both the CP timing and path area baselines.
