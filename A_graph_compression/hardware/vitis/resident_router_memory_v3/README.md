# Seven-component shared-buffer candidate

This version adds the bounded per-net canonical-node store to v2. Its input
shares tree.roots/search.roots/node.new_nodes; its output shares node.old_nodes.
Retention metadata and two-bank rows remain independent, as do all pointers
within a component. Config and result are new small BOs. In total, 64 pointer
arguments map to 46 unique BOs, requesting666341376 bytes with4KiB alignment
(635.47MiB). Nominal HBM use is25 channels, including the260MiB key buffer's
two-channel group. A16MiB per-pool reserve remains policy rather than measured
available memory.

Source signatures, interface depths and audited synthesis bundles are checked.
Actual exported XO ABI exists only for the previously exported subset; this
candidate does not establish exported ABI for retention or the other pending
components. Independent accounting/config audit and12 corruption cases cover
the added retention input/output aliases. The old v1/v2 plans remain frozen.

The return counts and all mutable shared buffers require serialized outer
control, with producer completion before consumers. Retained edge traces and
the complete hardware negotiation scheduler remain outside this inventory.
The current host bridge's unused short inputs cannot be used in RTL: its37
transaction RTL testbench separately allocates every complete declared depth.

Platform topology, v++ link, compatible XRT memory-group intersections, all46
BOs allocated together, physical timing and board execution still need actual
verification. This plan does not establish throughput, bandwidth or power.
