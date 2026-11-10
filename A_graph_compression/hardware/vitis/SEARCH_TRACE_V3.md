# Exact compressed search frame v3

Type6 header12 is `[6,words,iteration,query,target,nroots,nunknown,npips,
node_encoding,node_bytes,pip_encoding,pip_bytes]`. Payload is unchanged raw
result81, packed roots, packed path, then the two independently encoded exact
sets. Each set uses the canonical raw/maximal-run format in
SEARCH_TRACE_SET_CODEC_V1.md; separate word padding is zero. No path, resource
attribute, unknown member or original result word is discarded.

The node encoder walks the original bitmap directly without a million-element
scratch array. Zero active unknown count ignores stale bitmap contents, matching
frozen search v2 semantics. Invalid input and full frame capacity are checked
before output writes. Inputs and trace storage must remain disjoint/exclusive.
PIP encode repeats its preflight after reservation against the same immutable
input. Metadata and sticky failure protocol are unchanged.

`search_batch_trace_top_v2.cpp` differs from the frozen diagnostic top only by
including/calling the new search writer and changing its default top name.
Net/round/begin/terminal records retain their exact original payloads. The same
44-buffer source inventory needs a new kernel-name connectivity configuration;
no old XO/control ABI or HBM layout is automatically certified.

Independent read_compressed_search_trace decodes sets, reconstructs a single
plain frame and applies the frozen search reader. read_batch_trace_v3 handles
mixed type1/type6 and all v2 inheritance/global-ledger checks. The entire expanded
batch is never forced into the original 128MiB byte container.

Actual both-mode synthetic batch CPU outputs decode to identical search/net/
round/history/terminal fields as v1. A full 1,048,576-node unknown bitmap encodes
as four bytes and independently expands to every node. This does not prove full
real-batch fit, algorithm optimality, synthesized RTL correctness or device speed.
