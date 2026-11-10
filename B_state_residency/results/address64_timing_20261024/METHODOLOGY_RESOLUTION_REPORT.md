# 64位基址包装层时序方法学报告

Vivado2022.2物理实现已终态，MCP147904、371.091s、exit0；默认163840帧/hash18/epoch6，同U280器件、10ns、Default策略，与未包装组合版配对。正式DCP、路由/时序报告和final_audit.json完整；启动manifest中的running不代表当前仍在运行。

| 指标 | 未包装组合 | 64位包装 |
|---|---:|---:|
| 布线后LUT | 12396 | 12480 |
| FF | 11111 | 11182 |
| BRAM/DSP | 303/3 | 303/3 |
| WNS/ns | 1.265 | 1.493 |
| WHS/ns | 0.039 | 0.041 |
| WPWS/ns | 4.458 | 4.458 |
| 建立/保持/脉宽失败端点 | 0/0/0 | 0/0/0 |
| 缺输入延迟端口 | 627 | 693 |
| 缺输出延迟端口 | 847 | 938 |

全部可布线网络布通、routing errors0。最差内部路径仍为目录owners BRAM→probes CE，数据路径8.355ns。一次Default实现的内部裕量变化不证明64位包装提高Fmax；外部地址加法路径没有完整输出预算，不能由内部通过推断它满足平台接口周期。

原约束来源address64_synthesis_20261024/research_clock.xdc第1行：`create_clock -name core_clk -period 10.000 [get_ports clk]`。before/after规范化约束与未包装基线一致；新增地址/配置端口没有凭空添加预算。constraints_diff.html给出相同的规范化约束。

方法学报告保留SYNTH-10三项、TIMING-18报告1000项；DRC保留DPIP-2六项、DPOP-3三项、DPOP-4三项、RTSTAT-10一项。报告条目上限不等于缺预算的实际端口数；上表693/938来自check_timing。上游物理时钟上下文仍不完整，平台未闭合。没有添加豁免、虚构外部延迟或宣称解决这些缺口。

参考Ross vivado-timing-methodology-checks/TIMING-18；技能完整流程要求2026.1+，本机2022.2采用核实支持的文本-file报告，不声称执行全部新版检查。后续需真实控制/存储接口的时钟和延迟预算；这不是XRT、板上性能或完整FPGA路由器证明。
