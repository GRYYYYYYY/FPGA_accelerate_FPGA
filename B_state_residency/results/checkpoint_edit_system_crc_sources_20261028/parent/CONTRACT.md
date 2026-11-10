# Native checkpoint edit exclusion candidate

Prepared only; compilation, simulation and timing measurement remain required.

Native query root CP safe implies either warm ownership or ordinary checkpoint
ownership. Both make host_base false, disabling normal and boot admin request
READY masks. Therefore the actual host_label_edit handshake is false whenever
CP safe is true. Source-bound two-state enumeration covers 16384 combinations
with nonzero safe and edit cases. It is not RTL formal or X/Z verification.

CP_SAFE_EXCLUDES_HOST_EDIT defaults to0. Default query_lifecycle preserves the
existing drift check. Only the integrated native root enables it. With that
parameter enabled, the host_label_edit term is omitted only from CP drift;
all other drift terms and all sequential state, ledger, label dirty, error,
cancel, CRC and publication logic remain byte-identical. Generic cp_safe=true
and host_label_edit=true is an explicit counterexample outside the native
contract; never enable this specialization for an arbitrary backend.

Before selection require default compatibility against checkpoint/rebase tests,
native legal CP import/export and held/error/cancel cases, an explicit generic
overlap counterexample, actual CP-safe/edit port monitoring in full-system
replay, exact output/cycle comparison, archive actual restoration, and matched
OOC. Existing checkpoint tests may intentionally violate native exclusion;
preserve their original inputs/checks for default compatibility and create
separate native-qualified cases. Do not mask a failing original test to claim
compatibility. A shorter path is a hypothesis until measured.

Current query-native matrix stays on its frozen eleven-source candidate. This
new variant must not be substituted into that running matrix.
