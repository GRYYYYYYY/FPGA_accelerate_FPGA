# Zero-depth retirement excludes native capture replies

In the actual query core, capture_depth and e_result_valid are outputs of the
same native expansion_capture. Its result_valid requires frame_done; native
children_frames frame_done requires level!=0 and exports depth=level.
Consequently capture_depth==0 implies !e_result_valid without requiring a
reachable-state argument. The source-bound two-state enumeration has 8192
valuations, including true replies, and retains all other retirement conditions.

The one-file candidate removes only !e_result_valid from the existing
zero-depth retired_idle conjunction. It does not remove physical AXI drain,
arbiter activity, other service replies, core busy, or saved-frame tracking.
Capture/controller sequential behavior is unchanged. This is not permission
to remove reply gates from unrelated services or retirement predicates.

The fifth closed path of route_block_synth_v1 connects capture result gating,
backend retirement and fence request admission. This source identity motivates
the candidate but does not prove structural elimination. Native behavior and
full-system CRC/matrix validation, then full-root synthesis, remain necessary.
Do not claim X/Z equivalence, general formal verification, physical timing or
board gains from the Boolean enumeration.
