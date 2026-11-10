# 成本中心距离实际RTL验证

HLS2022.2 Csim、综合、Verilog/XSim cosim和独立数值审计通过：110397调用/220794输出字全部逐位一致，原冻结向量未改。除了Csim与C预/后检查，审计还直接解析了HLS二进制RTL交易文件，逐字匹配全部输出。

| 项目 | 结果 |
|---|---|
| 实际cosim latency min/avg/max | 3/90/113 cycles |
| 实际cosim interval min/avg/max | 4/91/114 cycles |
| HLS估计 latency | 3/40/144 cycles |
| 实际OOC资源 | 1967LUT / 1028FF / 89CARRY8 |
| RAM / DSP / latch / loops | 全0 |

10ns内部max/setup估计裕量3.489ns，但IO延迟与时钟位置未绑定、hold未评估、未布线。上述均非整体路由或板上速度证据。HLS估计5902LUT/1164FF不能替代实际OOC数量。

接口为单输入读口、双输出写口，完成同拍写两字。port0写word1(distance)，port1写word0(status)，收集器必须按地址，而非端口号解释。新collector、复位/归属/实际数据读取与post-prev顺序尚未验证。当前核也未接入成本packet或完整搜索。

数值域限定finite net centers（非finite返回错误），110397向量含12054拒绝；真实静态值/另选SLL Y不等于live路由调用。证据见cost_center_hls_20261025/source_bound_audit.json与cost_center_synthesis_20261025/final_audit.json。下一步接内部packet producer或组合preparation top，再补完整联接门禁。
