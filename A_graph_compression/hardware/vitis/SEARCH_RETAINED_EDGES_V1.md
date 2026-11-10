# Retained ordered physical edge traces v1

Top: `search_retained_edges_top`. This stores the exact eight u32 words of each
search path edge: src, dst, tile, pip, upstream, downstream, attributes, direction.
It preserves duplicate/parallel edges and insertion order within each net. It
never merges by endpoints or tile. Net IDs 0 and UINT32_MAX are ordinary values.

Config8: op, net, reset_nodes, edge_count, four reserved zeros.
Ops 0 reset, 1 replace (zero count deletes), 2 get, 3 append.
Reset requires net/count zero; others require reset_nodes zero; get count zero.
Result5: status, total_edges, nonempty_nets, version, returned_edge_count.
Statuses 0 ok, 1 invalid, 2 capacity, 3 version overflow. Errors zero result tail.
Meta6: magic 0x4152455445444731, domain, edge_count, bank, nonempty_nets, version.

Production domain 1048576; total edges 2097152; nonempty nets 65536.
Two banks of 2097152 rows, each nine u32 (net followed by eight path words).
Declared rows depth 37748736 u32; input/output depths 16777216 u32.
Input arrays must have these declared depths for generated cosimulation.
Get writes only the logical returned prefix. Reset touches only metadata.
State must originate from reset and successful operations; all buffers disjoint
and exclusively owned. Corrupt arbitrary internal rows are outside the contract.

Every update validates active source/destination domain and direction 0/1,
capacity and version before either bank is written. It copies to the inactive
bank and flips only after all writes; rejected operations preserve both banks.
This is validation atomicity under exclusive operation, not crash recovery.
No path continuity, graph-edge existence, site or tree validation is performed:
those belong to validated search/tree stages. Arbitrary attribute words survive.
Append preserves the previous per-net sequence and adds the new sequence.
An accepted zero-length append changes version, matching update semantics.

CPU test uses an independent map of ordered word vectors for 4000 operations,
checks full active bank, input immutability, failure rollback, get tails and
version. Production test fills the actual 2097152-edge capacity, reads every
field, rejects overflow, clears and appends repeated edge sequences. It compiles
and runs the actual top with C++14 ASAN/UBSAN. These are synthetic component tests;
there is no full-router integration, HLS synthesis, RTL, device or performance
claim yet. Copying the whole retained population per update is a correctness
reference strategy and requires performance evaluation before use at scale.
