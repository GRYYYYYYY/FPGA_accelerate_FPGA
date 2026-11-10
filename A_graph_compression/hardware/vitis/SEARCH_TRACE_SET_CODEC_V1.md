# Exact sorted-set trace codec candidate

`TraceSetCodec` preserves every sorted unique uint64 key. Encoding 0 is raw
little-endian uint64 words. Encoding 1 stores maximal consecutive runs as
unsigned LEB128(gap), LEB128(length). The first gap is the absolute first key;
later gaps are measured from the previous last key (at least 2). Lengths are
positive. All varints use minimal representation, fit uint64, and expand to the
exact declared count. Final unused high bytes of the last word are zero.

Choose RLE only when its byte count is strictly less than 8*count; ties use raw.
Empty sets use raw, zero bytes. Invalid input, duplicate/nonascending keys and
insufficient output capacity leave all output words unchanged. Scalar returned
encoding/byte count may change on capacity rejection. Production maximum is
1,100,754 elements. Caller reserves ceil(bytes/8) disjoint words before writing.

The independent Python decoder checks canonical runs, minimal varints, overflow,
count, ordering, selected raw/RLE form and padding. Actual C++14 ASAN/UBSAN
fixtures include 506 cases, the full production count, UINT64_MAX, sparse raw
fallback, empty sets and failed writes. This core is not yet integrated into
search/net/round trace or synthesized. Real-set size measurement does not prove
that a full batch including paths, roots and site records fits the trace buffer.
