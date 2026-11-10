# Direct-ledger search snapshot builder v1

`search_resident_snapshot_top` reads the existing bounded canonical-node and
site ledgers and produces packet v1 for the unchanged complete search kernel.
It builds forbidden-node bits from static protection and terminal reservations,
excludes the current net from both occupancy snapshots, preserves history, and
serializes all static site semantics/fixed constraints. Operation 1 changes the
query target, root count, budget and initial state in an existing packet.

This is a bounded, synthesis-oriented implementation. There is no allocation,
STL, recursion or function pointer in its top call graph. The CPU integration
calls the actual component top and the actual search C top. Outer negotiation,
route retention and encoding immutable metadata still execute on the host.
CPU equivalence does not establish RTL equivalence or board throughput.

## Control and status

Control has 16 uint64 words:
`[op,net,present,target,nroots,budget,static_words,packet_size,0,0,0,0,0,0,0,0]`.

- Operation 0 builds a snapshot; packet_size is available output capacity.
- Operation 1 patches a query; packet_size is the existing logical packet
  length and net/present/static_words must be zero. Existing ownership, static
  metadata and packet length remain unchanged. This operation does not access
  the ledger/static buffers.

Result has 8 uint64 words:
`[status,packet_words,node_occupied,node_history,site_owners,site_history,node_version,site_version]`.
Status 0 means success, 1 invalid input and 2 capacity exceeded. Failure clears
the last seven result words and preserves the entire packet. A successful patch
returns only status/packet_words; the other six result words are zero.

Build validates all static metadata, query state and sizes before writing output.
Ledger arrays are trusted states produced by their reset/update operations,
with exclusive access throughout snapshot construction. Patch accepts a trusted
packet from a prior successful build, checks its header/query fields and does
not recertify its entire unchanged body. Every accessed buffer is disjoint and
caller-sized. The top's declared depths are the production ABI; RTL testbenches
must allocate these depths even when an operation ignores a port. Unused output
tails remain unchanged. Input padding in packed site-state keys is canonicalized
through the existing `LabelKeyWords` loader/store, which ignores unused slots.

## Immutable metadata image

The header is 16 uint64 words:
`[0x41534e4150535431,total,nodes,attributes,nprotected,nsemantics,nfixed,nreserved,8 zeros]`.
Sections immediately follow in this order:

1. Protected canonical nodes: ceil(nodes/64) bitset words; unused bits are zero.
2. Reserved terminals: nreserved words `(node<<32)|net`, sorted by unique node.
   A reserved terminal cannot also be protected.
3. Pseudo and blocked attribute flags: each ceil(attributes/8) words, with eight
   byte lanes of 0 or 1 per word and zero unused lanes.
4. Protected PIP keys and semantic PIP keys: strictly sorted unique uint64 keys
   `(tile<<32)|pip`.
5. Semantic requirements: 65 words per semantic key, with node field zero.
6. Fixed records: `[key,owner,mask,value]`, sorted by unique physical-resource
   key, using the existing signal/masked-bit/categorical contract. Only signals
   may have a nonzero fixed owner.

The CPU adapter creates this image once per complete routing invocation. It
does not rebuild site snapshots, canonical node costs or forbidden sets on each
net. Two small derived ledger adapters add read-only buffer views to the existing
implementations; their allocation and mutation logic is otherwise unchanged.
No root/native/frozen baseline header is edited in place.

## Production allocation

| Pointer | Type | Declared words |
|---|---|---:|
| control | u64 | 16 |
| stat | u64 | 4194304 |
| initial | u64 | 65 |
| node_meta | u64 | 4 |
| node_counts | u32 | 1048576 |
| node_history | u64 | 1048576 |
| node_keys | u64 | 2097152 |
| node_flags | u32 | 2097152 |
| site_meta | u64 | 6 |
| site_owners | u64 | 524288 |
| site_history | u64 | 262144 |
| packet | u64 | 4194304 |
| result | u64 | 8 |

The original ledger buffers and search packet can be shared with the associated
components under explicit sequencing. This interface does not demonstrate that
XRT kernels are linked to compatible banks; existing search-only board memory
plans need a new version before including this component.

Maximum simultaneous metadata counts are 1,048,576 nodes/reservations/protected
PIPs, 65,536 attributes/fixed records, and 256 semantics. The resulting static
image is 2,408,976 words. With 65,536 dynamic site owners/history keys, the packet
is 3,850,849 words, within the unchanged 4,194,304-word search input capacity.
The CPU router keeps that full output allocation and tracks logical length
separately; logical packet counts are not measured AXI or board traffic.

## Verification

The component test compares 1,000 small-domain builds and 1,000 patches with the
original vector serializer and independent native owner/history maps, including
39 invalid/capacity operations and exact packet preservation on failure. It
checks that both ledgers remain unchanged and inactive state-key slots are
canonicalized. An actual production top test simultaneously fills every static
count, uses the full node domain and full site owner/history tables, checks all
3,850,849 packet words, rejects one-word-short output capacity, and patches a
maximum-size query. ASAN/UBSAN covers both paths.

The complete-router differential runs the new production builder top before the
unchanged production search tops, with no native adjacency fallback. Full real
workload evidence and HLS/RTL/physical/board evidence remain separately gated.

Development initially mixed root and frozen offsets-v3 pragma-once headers,
causing duplicate type definitions. All recorded builds use one flat frozen
include tree. A literal maximum-packet assertion was initially miscalculated as
3,950,849 despite successful bytewise oracle comparison; the independently
summed count is 3,850,849. The failed development output is preserved and does
not serve as passing evidence.
