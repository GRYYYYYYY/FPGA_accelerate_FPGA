# Sparse WB/RF address64 internal timing methodology report

Vivado 2022.2, non-project xcu280-fsvh2892-2L-e, core_clk 10ns, Default placement/routing. Completion receipt: exit0, 417.822s. The Ross methodology skill targets 2026.1+; this run reuses 2022.2 text reports rather than unsupported JSON options.

No XDC changes or waivers. Constraints before/after and native32 sparse-WB/RF baseline are equal under the independent constraint audit; constraints_diff.html records the unchanged file. The sole research constraint originates from sparse_records_address64_synthesis_20261024/research_clock.xdc:

```tcl
create_clock -name core_clk -period 10.000 [get_ports clk]
```

Internal setup/hold/pulse checks pass in this model: WNS1.134ns, WHS0.028ns, WPWS4.458ns; zero failing endpoints and routing errors. Worst setup path is directory frame_index BRAM clock to indexed_frame_reg[5]/CE, datapath8.715ns. Compared with native32 sparse-WB/RF, endpoints and placement changed; slack difference is not proof of a general Fmax gain.

| Check | Before | After | Disposition |
| --- | ---: | ---: | --- |
| TIMING-18 missing input/output delay | 1000 displayed violations | 1000 displayed violations | Retained; 693 input and 938 output ports lack delay. No platform budget exists to derive valid constraints. |
| SYNTH-10 wide multiplier | 3 | 3 | Retained; same family of frame/address arithmetic and 3 DSP, no new multiplier claim. |
| DPIP-2 input pipelining | synthesis report not applicable | 6 | Retained OOC DSP pipeline advisory. |
| DPOP-3 output pipelining | synthesis report not applicable | 3 | Retained OOC DSP pipeline advisory. |
| DPOP-4 multiplier pipelining | synthesis report not applicable | 3 | Retained OOC DSP pipeline advisory. |
| RTSTAT-10 no routable loads | synthesis report not applicable | 1 | Retained baseline OOC warning; route status separately verifies all routable nets routed. |

TIMING-18 count is the report's displayed instance count, not the number of uncovered ports. External IO and upstream clock-context modeling remain incomplete. No arbitrary set_input_delay/set_output_delay, false paths or warning waivers were added. Integration requires the actual connected interface budgets and source clock assumptions; internal passing checks are not platform closure or board performance.

The independent final_audit.json binds reports, DCP, paths, resources, launch inputs and baseline. Synthesized resources are12812LUT11279FF375BRAM3DSP; routed resources12773LUT11272FF375BRAM3DSP. Compared with native32 routed mapping: +149LUT/+64FF; BRAM/DSP unchanged. Both variants meet this10ns internal model. Address64 output paths lack platform delay budgets and are not closed by this result. Neither result establishes maximum frequency or platform timing. No methodology warning was resolved by this control optimization.
