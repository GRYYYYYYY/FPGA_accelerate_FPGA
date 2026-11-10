# Real host edit checkpoint extension

This verification-only suffix follows the existing `FOURTH_PASS` trace event in
the restored CP CRC-pressure fixture. It preserves every original stimulus byte
when its three insertions are removed. The original four real queries, failure
and recovery stimuli, monitors, and summary assertions remain present. No
production RTL changes or direct DUT writes are part of this extension.

The existing fixture never calls `label_write`; its external edit count is zero.
The source-bound finding is in `results/checkpoint_host_edit_coverage_20261030.json`.

The extension exercises these actual interfaces:

1. Save and verify the final clean ten-word checkpoint: sequence 180330, version
   8, generation `0x100000004`, flags `0x62`, and its CRC.
2. Read source node 66893 through host lane 8, write the same sequence-field value
   through the existing `label_write` task, then read back all 160 label bits.
   Require exactly one accepted write and reply, actual CP-safe false, no query
   ownership, and exactly one observed `host_label_edit` cycle.
3. Require the live anti-replay ledger to differ only in its dirty bit. Flush
   through the actual control lane (`control(1)` retains the active context).
4. Acquire the real checkpoint lease and export a dirty checkpoint. Only word7
   bit7 may differ from the saved clean image; independently check the CRC.
5. Import the original clean image with its correct CRC. At the actual CP_CHECK
   edge exclude drift, metadata, CRC, reset/abort/backend failure, rebasing and
   sequence rollback as rejection causes. Require dirty clearing to be the
   remaining cause, status1, retained live ledger, and pending restore still set.
6. Import the valid dirty image, require status0 and pending clear, then release
   the lease. The label remains dirty; no query admission claim is made.

After the write retires, every observed positive edge checks the complete
136-bit live ledger, route-slot bitmap, configuration descriptor, journal count
and saved checkpoint after NBA updates. Counts must be nonzero and balanced;
the extension has a 100000-cycle watchdog.

Expected extension coverage: 3 host requests/replies (read, write, read), 1 write
and write reply, 3 CP commands/replies, 20 imported words, 10 exported words,
1 clean-image rejection check, 1 dirty-image acceptance check. Expected total CP
coverage for this particular fixture is 15 commands/replies, 60 imports,
90 exports and edit=1. Atomic checks and extension cycle count must be measured.

Preparing this source is not compilation, simulation, or acceptance. Run the
same extended fixture separately with the original query-native and CP source
sets (only the existing two CP sources differ). Require exact complete output,
event and cycle comparisons, plus preservation of the old trace prefix through
FOURTH_PASS. Independently audit the actual logs and CRCs, archive, actually
restore and re-audit byte-identically, then freeze and verify SHA bindings.

Existing work retains execution priority: finish/freeze the current CP matrix,
then the already-prepared generic and native descriptor probes. This extension
has no runner or automatic followup yet and must not create a second behavioral
solver. A future runner must use the same single-owner and continuous memory
admission rules, require immutable source bindings, and preserve failures.
