# Resident snapshot: full-depth RTL verification

`test_resident_snapshot_rtl.cpp` derives its fixture from the frozen native
packet/ledger oracle test. Only the production fixture is instantiated. Every
call has all 13 complete declared pointer depths, with guards; no short dummy
ledger buffers are passed even on patch or rejection operations.

Thirty transactions cover maximum static metadata (1048576 reserved nodes and
protected PIPs, 65536 attributes/fixed rows, 256 full-state semantic rows), actual
65536 site owners and retained history keys, the 3850849-word logical packet,
one-word-short capacity rejection, maximum query patch, malformed controls and
metadata, and recovery. Additional actual node ownership/history changes test
self exclusion and reserved terminal differences for three querying nets.
Full physical buffers include packet/static4194304 words and node2097152 slots.

Each call checks all packet words and unchanged tails against the original
native serializer. All input arrays, metadata, and guards must remain unchanged.
The CPU sanitizer test uses the untouched native site ledger. The HLS C++14
test uses the already frozen pairwise ledger oracle for compiler compatibility.
These share the established packed-state ABI helpers; this is an original
serializer differential, not a fully separate literal packing implementation.
The node/site input states are constructed by their separately verified helpers.

The independent `resident_snapshot_rtl_contract.py` defines literal expected
result fields for all 30 operations. Parser tests reject missing/reordered rows,
changed fields, duplicate completion and invalid cycle sequences. Small parser
fixtures only test the verifier, and are not hardware performance evidence.

The pipeline copies the audited HLS project with all synthesis bytes retained,
changes only the testbench, runs native ASAN/UBSAN, HLS Csim and cosim setup,
then elaborates and simulates the unchanged RTL. The original generated C
postcheck must reproduce all packet/state checks. One owner then runs the final
audit; no competing replay or audit is needed.

`check_resident_snapshot_rtl_setup.py` independently checks the original native
oracle copy, receipts, actual ref.tcl and all binary/text AXI vector frames.
Packed depths are control81x64, static4194304x64, metadata10x64,
counts1048576x32, node-history1048576x64, node-table3145728x64,
site-table131072x256, site-history131072x128, packet524288x512,
result1x512. Only packet/result bundles have output vectors. All thirty frames
must retain those depths with correct binary EOF or text framing and hashes.

The simulation limit is ten seconds of simulated time, not a wall-clock timeout.
These transactions do not establish complete real routing traffic in RTL,
board residency, physical timing, memory bandwidth, or power.
