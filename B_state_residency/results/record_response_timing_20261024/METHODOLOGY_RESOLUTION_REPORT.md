# 时序方法学检查：记录响应直通候选

物理实现已完成，Vivado 2022.2 MCP147904，418.309 s、exit0。输入为已审计默认163840帧动态codec候选DCP，器件xcu280-fsvh2892-2L-e，10ns，Default布局/布线。`final_audit.json`记录终态证据；launch manifest中的running仅为冻结启动状态。

| 项目 | 动态基线 | 记录响应直通 |
|---|---:|---:|
| 布线后 LUT | 14511 | 14759 |
| 布线后 FF | 11159 | 11171 |
| BRAM | 319 | 319 |
| DSP | 3 | 3 |
| WNS/ns | 2.109 | 0.943 |
| WHS/ns | 0.037 | 0.007 |
| WPWS/ns | 4.458 | 4.458 |
| 建立/保持/脉宽失败端点 | 0/0/0 | 0/0/0 |

全部可布线网络已布通，零routing errors。before/after约束与冻结动态基线一致。最差路径为目录owners BRAM至probes寄存器CE，数据路径8.906ns；不能把全局布局变化后的裕量下降直接解释成响应FIFO自身延迟。每个配置只有一次Default实现，不宣称实现波动分布或Fmax。

方法学与DRC规则/数量与动态基线一致：SYNTH-10三项、TIMING-18报告1000项；DRC有DPIP-2六项、DPOP-3三项、DPOP-4三项、RTSTAT-10一项。未添加豁免或修改约束。TIMING-18的1000是报告实例数，时序检查实际缺627输入和847输出延迟；上游物理时钟模型也未补齐。因此结果只证明当前OOC内部模型满足10ns约束，不能证明平台时序闭合或板上性能。

约束来源为record_response_synthesis_20261024/research_clock.xdc第1行：`create_clock -name core_clk -period 10.000 [get_ports clk]`。缺失的外部预算属于尚未接入的平台信息；本研究不编造预算来消除告警。SYNTH-10属于已有目录乘法，RTSTAT-10等既有规则保留，未声明已解决。

参考Ross vivado-timing-methodology-checks与TIMING-18规则说明。完整技能要求2026.1+；本机2022.2的help不含report_methodology -json，采用已支持的-file文本报告，保留before/after XDC、路径TSV、placed/routed DCP和正式报告。没有运行或宣称通过全部新版检查。此轮无约束修复，before/after相同，无约束差异。
