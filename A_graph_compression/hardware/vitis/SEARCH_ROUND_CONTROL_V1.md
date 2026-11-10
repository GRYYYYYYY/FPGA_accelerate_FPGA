# Read-only round count and termination decision

`search_round_control_top` reads resident node owner counts and per-query tree
completion flags, plus the existing site analyzer's conflict-group count. It
does not advance history or change ownership. This implements one decision
stage; the host still invokes component commands and retains edge traces.

Control[8]: node domain, query count, iteration, max_iterations, present_cap,
site_groups, two zeros. Full pointer depths are control8 uint64, counts1048576
uint32, complete65536 uint32, result8 uint64. Inputs/results must be disjoint
and exclusively owned. The CPU bridge may supply a shorter logical counts
array; RTL testbenches must allocate every full declared port depth.

Result[8]: status, node_conflict_groups, incomplete_queries, action,
next_iteration, next_present, advance_histories, current_present. Status0 is
valid,1 invalid,2 capacity. Errors clear the other seven fields. Completion
flags must be0/1. A node contributes one conflict group if its owner count>1,
regardless of how many owners contend. Site conflicts are a separate count.

Action0 routed: no conflicts and every query complete. Action1 incomplete:
no conflicts with an incomplete query, or conflicts at the final allowed round.
Action2 continue: conflicts remain and another round is allowed. Conflicts
request both history advances, including on the final conflicting round,
matching the native loop. No-conflict termination never requests advancement.
Next fields are zero for terminal actions. Penalty is
min(2^min(iteration,20),present_cap); iteration/max_iterations retain uint32
range. Maximum site_groups65536 matches the existing site component capacity.

The kernel trusts the count array from the existing node ledger and the flags
from completed current-round queries. It does not validate global owner-pair
consistency or enforce stage completion. These are the outer controller's
responsibility; invoking this reader on stale inputs cannot implement a round.

Native integration records flags directly from tree completeness, consumes the
raw site analyze count, and uses this actual top's action/penalty/history flag.
Conflict/incomplete maps remain observations and are checked for consistency,
not used to choose termination. CPU tests use synthetic count/flag inputs for
3000 cases, maximum domains, late invalid flags, uint32 iteration boundaries,
penalty saturation and immutable inputs. A separate400-case complete-routing
differential checks all intermediate and final native routing semantics.

This eighth component is absent from the frozen seven-component memory plan.
Cross-component start/done control, integrated PL scheduling, rollback, platform
link, device execution, full timing and power still require separate work.
