# Actual HLS and OOC validation (2026-10-25)

`results/cost_center_hls_20261025/source_bound_audit.json` passes actual HLS2022.2 Csim, synthesis and Verilog/XSim cosim for all110397 frozen vectors/220794 words. Csim, C pre/post observations and the raw binary RTL output transactions match every expected word. The original oracle/vector file remains unchanged. Observed cosim latency min/avg/max3/90/113 cycles; HLS estimates3/40/144, which are different measurements and must not be interchanged.

`results/cost_center_synthesis_20261025/final_audit.json` passes actual OOC mapping:1967LUT/1028FF/89CARRY8, zeroRAM/DSP/latch/loops.10ns max/setup estimate+3.489ns;34input/43output ports lack platform delay, HD.CLK_SRC is unset, hold not assessed and no routing/board proof. This is standalone core area, not a measured joined design.

Frozen generated ABI is one input read port (one-cycle memory response) and two output write ports. Both writes, ap_ready and ap_done coincide on completion. Output port0 addresses word1(distance), port1 addresses word0(status): collect by address, never by port number. See `interface_notes.json` in the HLS result directory. No collector/reset/query ownership service or actual lookup/post-prev/packet join is proven by this numeric gate.

The old CPU-only statement below describes the initial stage; current hardware evidence is above. The read-only HLS testbench is rtl_testbench.cpp and remains separate from the CPU vector generator.

---

# Net-center distance input preparation

The cost service's input word6 is a binary32 distance to the net center. It is distinct from the integer child-to-sink heuristic distance in word12. This helper supplies the scalar computation needed after fetching the net's actual center and the child's effective coordinates.

Input words0/1 are signed32 childX/childY bit patterns; words2/3 are binary32 centerX/centerY. Output word0 is status0 for finite centers and1 for a non-finite center; word1 is distance raw bits, zero on rejection. Integer coordinates convert to binary32, then each subtraction rounds independently, absolute value clears the sign bit, and the two magnitudes add with binary32 rounding. Positive infinity from a finite-input result overflow is preserved. Net centers must be finite, consistent with the validated imported real net records; this is not a universal NaN-payload contract.

Implementation reuses the frozen exact_v2 integer binary32 primitives without changing them. The top cost_center_step has fixed4-word/2-word ap_memory and ap_ctrl_hs; interface pragmas are directly in the top body. No dynamic allocation, syscalls, recursion, native float arithmetic or function pointers occur in the reachable hardware code; loops in the reused helpers are statically bounded. Ross pragma-scope and synthesizable-subset rules were checked; actual HLS acceptance/latency/resource/numerical RTL gates remain pending.

CPU evidence: results/cost_center_cpu_20261025/source_bound_audit.json. The oracle includes the exact original getNodeCost distance expression and compares every result bit under -fno-fast-math -ffp-contract=off and UBSan. An independent binary32-stage reconstruction audits all110397 vectors;12054 non-finite-center cases reject. The set includes32400 edge combinations,50000 deterministic random inputs,27960 real static graph/net value samples and37 SLL alternate beginY samples. Static pairs are not live evaluateCost trace pairs, and choosing SLL beginY does not prove the prev-write/service ordering. The packet producer must request effectiveY after prev has actually been written.

This helper is not joined to the candidate/cost-state wrapper, does not fetch memory, form the23-word packet or invoke cost arithmetic, and has no new HLS/RTL proof yet. The current CPU testbench generates its vector output; a future HLS flow should use a separate read-only frozen-vector testbench and separate observation paths, not point that generator at the frozen oracle file.

Next steps are HLS Csim/synthesis/cosim against frozen vectors, or direct inclusion in a validated packet-preparation top, followed by actual service integration with full identity/lease and post-prev semantics.
