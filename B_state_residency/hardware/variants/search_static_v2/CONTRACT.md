# Response-selection control experiment

This isolated variant changes only the search host fence's three dynamic lane
selections (ready, reply valid, 256-bit reply) into an explicit sixteen-way case
with constant slices. All sixteen scheduler lanes and all host lanes remain.
`build.py` reconstructs the exact change from the preserved v1 file; the scheduler,
request mapping, top, and real testbench are unchanged.

The 20 lease-composition scenarios and two real-service/cache configurations pass.
Full cycle trace, seven AXI logs and four complete images equal the independently
CPU-audited v1 result. A side-by-side comparison additionally tests every one of
4096 reply bits on each of 16 known lanes, then all256 selected ownership-gate
combinations per lane: 69632 checks of every output. These are simulations, not a
formal proof over arbitrary X/Z inputs. Unknown lane encodings are not reachable
from the reset/registered existing scheduler.

Complete U280 OOC remains 99477 LUT/61700 FF/160.5 BRAM Tile/23 DSP: no resource
reduction. This negative result rejects the hypothesis that merely rewriting the
reply selector solves the observed LUT increase. Do not claim acceleration or
infer exact physical gate identity from equal resource counts. Next experiment:
restrict request injection to the four services actually used by the scheduler.
