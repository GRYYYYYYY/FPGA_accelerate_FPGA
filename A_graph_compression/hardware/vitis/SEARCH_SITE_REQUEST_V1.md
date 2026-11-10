# Packed site demand to ledger requests

`search_site_request_top(state, request, result)` converts the route-tree's
canonical node-zero 65-word state to the existing site-ledger request ABI.
It produces sorted `[kind/id, mask, value]` triples: signals, bit assignments,
then categorical assignments, each sorted by physical resource ID.

The packed limits remain 32 signals, 16 bit fields and 8 categorical fields.
Maximum logical output is 56 records/168 uint64 words. The output pointer retains
the ledger's full declared 196608-word depth, allowing direct buffer sharing
with `search_site_occupancy_top.request`. Only the logical prefix is overwritten.
Zero-mask bit fields remain explicit records. UINT32_MAX resource IDs are valid.

Result[2] is status and record count. Status 0 means success, 1 invalid state,
2 capacity. Production capacity is 65536 records; a smaller helper instantiation
tests the capacity rejection. Errors return zero count and preserve all request
words. Input/state, request and result buffers must be disjoint and exclusively
owned. Unused state slots follow the established load ABI: ignored, not checked
as active fields. Active counts/order/masks, reserved header byte and node-zero
canonicality are validated before writing output.

The top has input_mem(state65) and output_mem(request196608/result2) bundles;
all interface pragmas are in its function body. There is no allocation, STL or
recursion in the component. Native sanitizer testing uses literal input packing
and the original `site_native::entries` map conversion as the expected output.
The HLS C++14 test uses the already established pairwise oracle's entries API.

In an isolated router copy, `Ledger::replace_packed` invokes this actual top and
passes its raw request records to the unchanged bounded site replace helper.
Final host demand unpacking is retained for observable output, rather than as
the source of ledger mutation. Site release, conflict/history operations and
the search/tree/snapshot components keep their predecessor implementations.

This adds another component to the device design: the frozen five-component
memory plan does not include it. A new device plan must connect tree.demands,
snapshot.initial and encoder.state to the same compatible BO, and encoder.request
to the ledger request BO. The record count still needs outer control. CPU
integration does not establish device invocation, atomic multi-kernel scheduling,
platform link, RTL equivalence, bandwidth, power or complete hardware routing.
