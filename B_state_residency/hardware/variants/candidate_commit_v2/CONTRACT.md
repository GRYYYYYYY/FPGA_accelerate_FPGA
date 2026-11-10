# Guarded cost-label admission

This variant adds the following admission boundary to the v1 ordered-label wrapper, without changing the commit engine or native backend:

- A cost reply with nonzero status raises k_reply_error and the global fault/fence.
- A commit request requires fault=0 and cost status0, in addition to the existing complete/candidate ownership conditions.
- Malformed full cost identity is already rejected by k_identity_error; the new guard prevents exposing a commit request before the registered fence propagates.

The normal three-write and partial-commit/drain semantics remain in ../candidate_commit_v1/CONTRACT.md. derive_top.py reproduces the whole wrapper from frozen cost23 input by applying the v1 transform and the guard. The core and cost_label_commit RTL are unchanged from v1.

Directed joined tests inject bad full-design identity and nonzero cost status into the first actual computed cost reply, before commit acceptance. Both must assert fault, keep the commit block idle, and accept zero cost-label requests. Earlier prev/CLEAR/design preparation may already have occurred. This is not a no-side-effect rollback claim or actual AXI-failure recovery. The same bad-identity admission test fails as expected on the old unguarded wrapper; its normal functional gate remains separately retained.

Normal functional replay, final checkpoint/readback and mocked-native partial-commit tests are separate gates. Immediate recursive lookahead, cost OFFER, coordinated native/AXI drain/reset/reload, full routing, new composition synthesis and board performance remain unfinished.
