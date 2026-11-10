# Parent upstream缓存的物理代价对照（2026-10-25）

已将未改基线postprev_inputs与隔离parent_upstream_v1缓存变体，在同一Vivado2022.2、xcu280-fsvh2892-2L-e、10ns research_clock和Default综合/布局/布线流程下完成模块级OOC对照。两者都包含相同8份实际center服务/算术RTL，只改变post模块一份源码；默认MAX_CYCLES=1048576与实际集成实例相同。机器证据 results/parent_physical_20261025.json，主结果 parent_physical_v2，审计scripts/audit_parent_physical.py。

| 阶段/资源 | 基线 | 缓存 | 增量 |
| --- | --- | --- | --- |
| 综合 LUT | 2620 | 2729 | +109 |
| 布线后 LUT | 2576 | 2683 | +107 |
| FF（综合/布线后相同） | 1951 | 2117 | +166 |
| CARRY8（综合/布线后相同） | 123 | 141 | +18 |
| BRAM / DSP / latch | 0 / 0 / 0 | 0 / 0 / 0 | 0 |

这是post+真实center子模块的代价，不是整套路由引擎面积。综合与实现LUT数分别报告，不把综合109与路后107混用。此前同自然query的仿真POLL窗口改善仍为32槽1.44%、单槽12.07%；本轮未重新测系统吞吐或板卡性能。

| 布线后检查 | 基线 | 缓存 |
| --- | --- | --- |
| WNS（10ns内部约束） | +2.847ns | +2.786ns |
| WHS | +0.041ns | +0.042ns |
| TNS / THS | 0 / 0 | 0 / 0 |
| setup / hold / pulse-width失败端点 | 0 / 0 / 0 | 0 / 0 / 0 |
| routable / fully routed nets | 3583 / 3583 | 3783 / 3783 |
| routing error / DRC violation | 0 / 0 | 0 / 0 |

两者有约束的内部寄存器路径在10ns检查下均满足。最差setup路径均在相同center算术层级中，但端点不同；单次布局的61ps slack差不能当作普遍Fmax变化。没有frequency/placement seed扫参、post-route功能仿真或全加速器实现。

限制必须保持：XDC只有研究时钟，没有外部input/output delay，也没有HD.CLK_SRC假定。两者check_timing均报告939个no_input_delay和771个no_output_delay；methodology文本各列1000项TIMING-18，未waive或禁用。不存在no_clock/unconstrained_internal_endpoints/loops/latch_loops，仍不能将模块内部10ns通过称为平台I/O时序闭合或板卡Fmax。真正集成时需要连接上下游、确定时钟/外部预算后重新布局布线。

流程兼容性：读取Ross vivado-timing-methodology-checks后确认其要求2026.1+；本机help已验证2022.2只支持report_methodology文本-file，不支持示例-json，按本机功能取报告。读取TIMING-18参考并保留未约束I/O的诊断，不编造预算。最早parent_physical_v1在综合前因不存在的redirect命令停止，v2使用报告-file与普通Tcl milestones，失败run/manifest固定parent_physical_failure_20261025。源脚本和审计器固定parent_physical_sources_20261025。v2路径TSV原始分隔符是字面\t，审计显式规范化为tab后解码，原报告不修改；2022.2 Timing Summary与utilization的器件/状态标题格式不同，审计分别按真实格式和完整route状态核验。

已有B MCP会话/PID147904执行source，300s观察返回running后继续同一命令，没有重启；最终exit0/467.116s。完成后无project/design打开并恢复原工作目录。收据parent_physical_completion_20261025.json。根归档57常规文件/12929233B，包含综合/placed/routed DCP和全部报告，逐压缩成员与共享盘copy SHA验证，实际移走scratch后恢复；恢复凭据parent_physical_restore_20261025.json。

并行工作：第二个真实设计MCML的首查询已完成全节点快照与原CPU精确恢复搜索，详见natural_mcml_query_20261025.md/.json。它还没有MCML RTL/parent缓存收益，下一优先为导出MCML原CSR/输入codec、独立geometry/cost/filter oracle，测试自然target EARLY之后剩余一个child的drain；随后再扩大多query与不同生命周期覆盖。仍保留默认基线，完整可综合search loop、backtrace/owner提交和板卡端到端比较未完成，goal active。
