# Search trace v2 writer and independent reader

SearchTraceV2 retains v1's exact binary record format and default128MiB bound.
Only active/count-delimited output is consumed: when result[8]==0 the unknown
bitmap is not read or validated. This is necessary for rejected searches whose
unused buffers can retain prior data. Unknown PIP and path arrays likewise have
no active payload when their result counts are0. The original v1 remains frozen.

read_search_trace.py reads a file containing eight metadata u64 words followed
by exactly committed_words payload words, all explicitly little-endian. The
caller supplies the validated node domain. It independently checks metadata,
record lengths, ABI/count consistency, strictly increasing iteration/query
ordinals, roots/padding, path continuity/direction/domains, sparse unknown sets,
and active65-word demand state according to the documented packed ABI. Unused
state slots are retained in the raw result and ignored when decoding active
state, matching the original word loader.

The reader returns search_fragment_validated and complete_batch=false, even when
all records are valid. It rejects unsupported event types; net/round/history and
successful terminal-event sequencing are not implemented. Query ordinals must
identify individual searches, including distinct ordinals for duplicate sinks.
This is not a whole-batch trace verifier or a hardware trace-export implementation.

Tests compile the actual writer/dumper with C++14 ASAN/UBSAN. The independent
reader checks C++-written bytes, including UINT32_MAX resource words and a
rejected-search frame with stale nonempty unknown buffers but zero active counts.
It rejects23 isolated field/file corruptions. A successful source-level reader
check does not establish RTL, DMA or board behavior.
