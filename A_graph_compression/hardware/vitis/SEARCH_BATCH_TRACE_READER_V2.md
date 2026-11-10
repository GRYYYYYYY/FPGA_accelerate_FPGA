# Mixed trace reader v2

The diagnostic top and binary ABI remain the frozen v1 implementation.
`read_batch_trace_v2.py` first executes all v1 validation, then strengthens it:

- Every successful search retains all accumulated signal requirements.
- Old bit masks cannot shrink and required values cannot change within those masks.
- Categorical fields cannot disappear or change value.
- A zero-edge successful search cannot add any new requirement.
- With reset_state=1, each net snapshot's global occupancy/retention population,
  retained-net count, retained edge population/net count, and site owner count
  must equal the population reconstructed across all latest net snapshots.

The regression deliberately adds signal4 to an early actual search frame, then
leaves later frames unchanged. V1 accepted that internally inconsistent run;
v2 rejects the disappearing requirement. Six separate metadata-total mutations
are also accepted by v1 but rejected by v2. These are verifier counterexamples,
not observed failures in the actual routing kernel. The unmodified actual CPU
and HLS Csim fixtures remain accepted with the same reset/seeded-state limits.

The v1 result files remain immutable historical evidence. Use v2 for subsequent
trace acceptance; a v1 complete_batch flag alone does not prove these stronger
invariants. Neither reader proves search optimality, graph provenance, a seeded
initial state, generated RTL behavior or successful device execution.
