# Five-component resident memory candidate

This static plan connects the unchanged search, node occupancy, site occupancy,
resident snapshot, and route tree components. It inventories all 55 pointer
arguments at full declared depths. Shared buffers are counted once: 41 distinct
BOs request 632770560 bytes after 4 KiB alignment (603.46 MiB).

The two candidate configs put all buffers in DDR[0], or split connected groups
across 23 nominal U280 HBM channels. Each pool reserves 16 MiB as a policy;
this is not a measurement of available device memory. The 260 MiB key buffer
requires HBM[5:6], while the graph uses 128 MiB in HBM[0]. The remaining HBM
groups are generated from sharing and AXI bundle constraints.

Shared physical buffers:

| Producer / owner | Consumers |
|---|---|
| Tree roots | Search roots and node update new_nodes |
| Snapshot packet | Search packet |
| Search result/path | Tree accept result/path |
| Tree demands | Snapshot initial state |
| Node meta/counts/history/keys/flags | Snapshot node ledger inputs |
| Site meta/owners/history | Snapshot site ledger inputs |

The plan forbids aliasing two pointers within the same component. Bank sharing
does not imply pointer aliasing. Components execute under one owner; all producer
events finish before consumers access shared mutable buffers. Retained route
traces, old per-net state storage, and future hardware outer scheduling are not
implemented by this plan. Current node.old_nodes and site.request remain
separate input BOs requiring existing host marshalling.

Generation parses all five source signatures and interface depths, checks both
search exported kernel XMLs, and checks new component bundles against their
audited synthesis reports. New component exported XO argument/control layouts
still need checking. The independent audit recomputes unique allocation sizes,
alignment, per-bundle bank consistency, shared-port connectivity, aggregate pool
capacity and exact config lines. Tests reject incompatible/transitive aliasing,
single-channel allocation for oversized keys, channel exhaustion, and corrupted
candidate manifests/configs.

Before device execution: validate installed platform topology, export unchanged
production XOs, link the five kernels, verify each shared BO's compatible XRT
memory-group intersection, then allocate all buffers simultaneously and execute
the sequence. Numerical kernel.group_id values alone do not prove compatibility.
This candidate does not establish platform link, device allocation, timing,
bandwidth, complete hardware routing, or power results.

Commands require fresh output paths:

```sh
python3 scripts/resident_router_memory_plan.py --output <new-plan-directory>
python3 scripts/check_resident_router_memory_plan.py --directory <plan-directory> --output <new-audit.json>
```
