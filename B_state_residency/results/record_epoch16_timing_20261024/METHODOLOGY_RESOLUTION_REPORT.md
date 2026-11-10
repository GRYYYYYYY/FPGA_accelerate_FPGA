# 16位目录epoch物理检查

Vivado2022.2 / MCP147904 / 408.808s / exit0，默认163840帧/hash18，静态codec与记录专用响应旁路。只将目录EPOCH_BITS6→16，TX/GEN16等保持。独立综合和物理终态证据在final_audit.json；启动manifest状态不是实时运行状态。

| 指标 | epoch6 | epoch16 |
|---|---:|---:|
| 综合LUT/FF | 12434/11115 | 12823/11167 |
| 布线后LUT/FF | 12396/11111 | 12750/11161 |
| BRAM/DSP | 303/3 | 375/3 |
| WNS/ns | 1.265 | 1.240 |
| WHS/ns | 0.039 | 0.037 |
| WPWS/ns | 4.458 | 4.458 |

当前10ns内部建立/保持/脉宽失败均0，routing errors0。最差路径state寄存器→目录frame_index BRAM使能，数据路径8.392ns。一次Default实现不证明Fmax或板上吞吐。

before/after规范化约束与epoch6基线一致，只有core_clk 10ns（来源record_epoch16_synthesis_20261024/research_clock.xdc第1行）。无约束修复、虚构IO预算或豁免；constraints_diff.html为空差异。

方法学保留SYNTH-10三项、TIMING-18报告1000项；DRC保留DPIP-2六项、DPOP-3三项、DPOP-4三项、RTSTAT-10一项。实际627输入/847输出缺delay，上游物理时钟上下文不完整，平台未闭合。报告实例数不能代替缺预算端口数。

沿用Ross时序方法学指引及TIMING-18说明；2022.2使用核实可用的文本-file报告，未声称执行要求2026.1+的全部新版检查。本检查支持独立组件的资源/内部时序可行性，不验证全设计570286次尝试的总耗时、XRT或实卡性能。
