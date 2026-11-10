# Native epoch6 / static codec / record response bypass candidate

Self-contained RTL-only non-project OOC package. Requires Vivado 2022.2; default target xcu280-fsvh2892-2L-e. Top memory_scratch_endpoint_small_staticcodec, FRAMES163840, INDEX/HASH18, EPOCH_BITS6, TX/GEN16, TAG2, 32 slots, 192-byte pages.

Run `python3 verify.py` to verify hashes. Run `python3 verify.py --test checkpoint --output NEW_DIR --vivado-bin VIVADO_BIN` (or `--test wrap`) for a standalone regression. Rebuild synthesis with `vivado -mode batch -source Scripts/synth.tcl -tclargs NEW_OUTPUT`. Use a new output directory; generated results are not source inputs.

Evidence records retain original experiment provenance paths, but build and simulation require only this package. No XPR, IP, data fixture or prior DCP is needed. This is the native 32-bit relative-address endpoint; the separate address64 wrapper is not included.

Evidence covers 38-query actual-value replay, lifecycle/AXI checks, and internal 10ns OOC implementation. External IO delays and upstream physical-clock context remain incomplete. No complete FPGA router, XRT integration, board timing or board acceleration is claimed.
