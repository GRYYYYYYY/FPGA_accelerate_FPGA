# 服务接入更新（2026-10-24）

算术核已由[`cost_service_v2`](../../variants/cost_service_v2/cost_service.sv)接入，见[调用契约](../../COST_SERVICE_CONTRACT.md)和[验证报告](../../../results/cost_service_20261024.md)。实际21576向量/720复位时刻、120收集排列/18协议故障与45实际核故障恢复通过；下方关于包装尚待实现的描述为历史状态。整数几何、价格读取、完整搜索和板上仍待接入。

---

# Search cost arithmetic characterization

The scalar inputs come from the verified CPU decomposition and actual captured evaluateCostAndPush calls. This module does not perform graph geometry, price lookup, accessibility, label writes, query ownership or frontier operations.

`native_v1` evaluates the existing float helper directly. Its HLS2022.2 RTL disagrees with the frozen host oracle on158/4776 cases (331 words). The csim matches; cosim prints PASS because the test deliberately completes a characterization. `numerical_audit.json` is the compatibility verdict, which is failed. Ordinary4096 synthetic inputs match but this does not authorize general replacement.

`exact_v1` introduces binary32 integer add/multiply/divide/convert/compare with explicit guard/round/sticky handling. Its C++ result differs in one two-NaN case because the host compiler commuted an addition and preserved the other payload. That failure is retained.

`exact_v2` retains arithmetic association and rounding points, but chooses commutative operand priority to match the frozen SSE oracle. `oracle_disassembly.txt` records the relevant CPU instructions; this is not a claim that arbitrary compilers specify identical NaN payload propagation. Additional576 pairs of quiet/signaling signed NaNs use an independently extended original float-helper producer; its first4776 expected vectors must be byte-identical to the original producer. Real16224 packets preserve observed CPU outputs from all12 route iterations; complete route noninterference is checked independently.

The integer operations use finite bounded loops, no heap, recursion, system calls or floating-point operators. Each result uses round-to-nearest, ties-to-even; subnormal operands and results are preserved, overflow yields signed infinity, zeros keep IEEE signs, invalid arithmetic yields frozen SSE quiet NaN ffc00000. With two NaN primitive inputs the first operand is quieted and propagated. The top controls operand priorities for the frozen cost expression.

The single-call top is `cost_step(const uint32_t input[23],uint32_t output[5])`. Both arrays are ap_memory with explicit depth; the top uses ap_ctrl_hs. Interface pragmas are directly inside the top body. There is no DATAFLOW directive, extra persistent state, pipeline performance target or AXI platform interface. Basic fixed-length normalization loops may be pipelined by HLS automatically; synthesis reports, not source intent, determine latency/area.

| Input word | Meaning |
|---|---|
|0,1|shareWeight binary32, same-net connection count signed32|
|2,3,4|baseCost, design history, selected present congestion price binary32|
|5,6,7|net connection count signed32, distance-to-net-center binary32, doubleHpwl signed32|
|8,9,10|parent upstream binary32, wire-length weight binary32, node length signed32|
|11,12,13,14|estimated wire-length weight binary32, precomputed geometric distance signed32, landmark enable (nonzero), inverse scale binary32|
|15..22|8 pairs: target landmark u16 in low bits, child landmark u16 in high bits|

Outputs are raw binary32 sharing, node cost, partial cost, heuristic and total cost, in that order. The testbench writes every returned word and compares with frozen host-generated vectors; no decimal tolerance or NaN equality shortcut is used at packet level. Returning0 only signifies all scheduled calls completed. Only the independent numerical audit may assert exactness.

The temporary array interface still needs a runtime collector/owner-controlled service. The arithmetic result must not commit query labels or queues by itself. Partial writes/reset semantics, caller input stability, tagged response and cancellation belong to that future service. Existing CPU negative/boundary inputs are checked for numeric semantics; their presence does not permit negative occupancy, zero net fanout or invalid geometry in the router input contract.

Sources for the initial diagnosis: AMD [UG1399 2022.2 floating-point types](https://docs.amd.com/r/2022.2-English/ug1399-vitis-hls/Floats-and-Doubles), [expression optimization](https://docs.amd.com/r/2022.2-English/ug1399-vitis-hls/Optimizing-Logic-Expressions), [PG060 Floating-Point Operator](https://docs.amd.com/v/u/en-US/pg060-floating-point). The actual compatibility conclusions above come from local CPU/RTL comparisons.

Completed gates (2026-10-24): exact HLS21576 calls/107880 output words all bit-identical; cosim latency224/477/687 cycles. Full integer CPU route preserves570286 attempt metadata, paths and captured accesses. Actual Vivado OOC7543LUT4791FF20DSP365CARRY8, zeroRAM/latch/loops;66 inputs86 outputs withoutIOdelay, not routed.

Collector constraint from generated RTL: ap_ready=ap_done only in finalstate23. Both output memory write ports are active earlier (state20/21); do not reuse Frontier's rejection of outputs before ap_ready. Own the operation from launch, retain input snapshot, collect per-address output writes and final done, reject duplicates/out-of-range addresses, and retire coherently. No wrapper/reset proof exists yet.
