# 组合候选时序方法学报告

物理实现已终态：Vivado2022.2、MCP147904、374.374秒、exit0。输入为已审计静态codec/epoch6/记录响应直通默认163840帧DCP；同器件xcu280-fsvh2892-2L-e、10ns、Default优化/布局/布线，与原epoch6物理v2配对。最终证据为final_audit.json，启动manifest状态不代表当前运行状态。

| 项目 | 原epoch6 | 组合候选 |
|---|---:|---:|
| 布线后LUT | 12216 | 12396 |
| FF | 11111 | 11111 |
| BRAM | 303 | 303 |
| DSP | 3 | 3 |
| WNS/ns | 1.621 | 1.265 |
| WHS/ns | 0.037 | 0.039 |
| WPWS/ns | 4.458 | 4.458 |
| 建立/保持/脉宽失败端点 | 0/0/0 | 0/0/0 |

布线完全且零routing errors。最差路径为cookie寄存器至目录owners BRAM读使能，数据路径8.369ns；不能将整体物理裕量变化隔离为响应旁路逻辑延迟或外推Fmax。

before/after XDC与原epoch6基线一致，未修改约束或创建豁免。原约束来自record_epoch6_synthesis_20261024/research_clock.xdc第1行：`create_clock -name core_clk -period 10.000 [get_ports clk]`。constraints_diff.html比较规范化before/after约束，两者相同。

方法学仍有SYNTH-10三项、TIMING-18报告1000项；DRC仍为DPIP-2六项、DPOP-3三项、DPOP-4三项、RTSTAT-10一项。1000不是实际未约束端口数；check_timing记录627输入和847输出缺delay，上游物理时钟上下文也不完整。这些缺口保留，本结果不是平台时序闭合或板上验证。

参考Ross vivado-timing-methodology-checks与TIMING-18说明；完整技能要求2026.1+，本机2022.2使用已核实的-file文本报告，未宣称执行全部新版检查。无约束修复，不生成虚构的外部预算。原动态epoch8记录直通全量与组合全量回放独立验收，不能由此物理通过替代。
