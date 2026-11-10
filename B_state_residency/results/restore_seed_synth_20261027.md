# 匹配参数综合完成，组合环导致设计验收失败

两版均为Vivado2022.2、U280 query_residency_system OOC；133份RTL相同，唯一generic差异ENABLE_RESTORE_SEED_BYPASS。4路径、32槽、16384帧、1024恢复记录、baseline/warm开启、测试注入关闭；全部runtime端口保留。资源报告和独立DCP诊断已经审计，两归档实际恢复后审计字节一致。产物审计通过不等于设计验收通过。

| 指标 | 关闭 | 开启 |
| --- | ---: | ---: |
| LUT | 140295 | 139752 |
| FF | 88213 | 88155 |
| BRAM tile | 163 | 163 |
| DSP | 23 | 23 |
| URAM/latch/blackbox | 0 | 0 |
| check_timing组合环 | 20 | 20 |
| LUTLP-1区域内LUT数 | 103 | 107 |
| 10ns布局前WNS/ns | -9.941 | -9.910 |

开启减543 LUT/58 FF，仅为这两个具体综合结果；不能把带组合环的时序估计当作可实现频率。最差开启版路径从directory lease_phase寄存器到search error_code，有84级逻辑，估计19.892ns数据路径。当前首先消除反馈，再处理长路径。实际DCP诊断未添加waiver、ALLOW_COMBINATORIAL_LOOPS或false-path；导出XDC仅含10ns时钟，不能据此否认综合内部自动切环。

每版methodology返回SYNTH-10=23、TIMING-16=1000、TIMING-18=1000、TIMING-23=1个对象；1000是本次返回数量，不能当作完整端点总数。check_timing列明关闭46801、开启46802输入以及各10419输出无IO delay，是本OOC接口边界未定义；无no_clock或内部未约束端点。10ns只是实验目标，尚无板级接口延迟和物理时钟位置约束。

check_timing报告20环，但只列出关闭18条/开启9条完整pin walk；分析器显式保存缺口。LUTLP-1通过对象查询提取全部103/107个cells并与描述核对；它与20环不是相同计数单位。共有反馈涉及recovery、authority、publication、fence、label、route和child_capture。源码可疑依赖和后续原生组件/完整系统回归要求见hardware/variants/timing_loops_v1/PLAN.md；尚未应用生产修复。

新审计器开发中，原先拒绝所有critical warning的门槛遇到实际Synth8-295；现明确记录该已检查的失败证据，并将design_acceptance标为rejected_combinational_loops，未知critical仍拒绝。原审计器和失败说明保留在restore_seed_synth_loop_observation_20261027。无原始数据或生产源码修改。

外部baseline provider和snapshot writers不在query root内。此前仿真正确性与23.6%/30.3%标签阶段周期减少保持其原范围，尚无硬件时序、板卡性能或全局任意输入保证。下一优先隔离原生握手与REARM反馈、完整消环和协议/AXI/数值回归；研究继续。
