# Occupied candidate input experiment

This experiment uses the unchanged 64 RTL/model modules from the accepted prefetch composition. The testbench differs only in its module name and terminal marker. All existing decision, stability, lease and backing-state assertions remain enabled.

Eight initially empty allowed child nodes from the real graph are selected deterministically. Scripted original CPU incrementUser calls create primary and overflow owners with distinct-net occupancy1,2,3,5,16,32. Same-net references include3,7 and5 (the last in an overflow record); missing same-net cases are included. There are54 live overflow records within the existing capacity64. Original CPU owner counts/occupancy are compared with every encoded modified owner. All other owner bytes remain unchanged.

Each selected node receives a distinct finite history value1.25+i/8. The CPU rebuilds all256 present-price values with factor1.25; the byte image is independently reconstructed. Initial real net parameters remain unchanged. These are scripted inputs imported before configuration; they are not naturally observed route iterations or host SET transactions.

The complete original CPU candidate fixture is rerun after the increments. The original golden decision body and access-machine checks stay intact. In this selected data the3022 A rows happen to remain unchanged; this is established by the new execution, not assumed when constructing the expected result.

Actual candidate outputs trigger owner/history/price/net reads. The audit compares all AXI read data, selection addresses, result identities and final full backing images with the modified input set. SKIP must still suppress prefetch. Same-net references change occupancy selection by exactly one, irrespective of branch count. Core-retirement and center-service fixture checks remain part of the regression.

The original input preparation attempt hit quota. Its CPU driver returned0 without checking its output streams; initial_design was truncated to16MiB and expected_design was empty. Its passed manifest is rejected by output_integrity_failure.json. The strict v2 preparer requires both full145424192B images, all1212 expansions, complete decision count and final control record. No bytes of the failed case are overwritten.

To avoid quota affecting simulation, v2 inputs and runs live in /tmp/B_state_residency_occupied_20261025, with results/ symlinks. Each audited directory is archived under results/occupied_archives_20261025; every regular member is hashed after decompression, then the archive copy is hashed. The index records the exact scratch location and member hashes. Restore with scripts/restore_occupied_result.py <index.json>. Archives are the durable evidence; scratch files alone are not.

This closes the actual-store nonzero selection gap. It does not bind actual post-prev coordinates to center arithmetic, write cost labels, construct all23 cost words or implement Frontier recursion, traceback/owner commit, platform/board execution. No new mapped resource or acceleration claim follows from these simulation results.
