# 第二轮真实查询 RTL 闭环

Vivado2022.2 XSim、同一B MCP进程147904，完整32槽/单槽均PASS；MCP300秒返回running后保持同一任务，终态308.464秒exit0。109份生产RTL/dat逐SHA保持基线，只有验证TB及图像装载脚本适配。来源followup_rtl_sources_20261025，主审计audit_followup_query_rtl.py。

真实logicnets iteration2/sequence180327、connection170782/net26422/source66893/sink204279。加载1647675个已缓存parent的完整设计图像及53734项owner pool，history/价格使用第二轮准备态。实际heap POLL驱动父节点、实际target标签决定结束，CPU文件仅评分。421组完整23输入/5成本结果（含共享、overflow及history>1）等于独立CPU预期。

两配置均171POLL、170expand、853captured child、849判定、421cost/commit/OFFER、1263标签ACK、EARLY1。最后parent339193的目标204279触发EARLY，后续648770/125130/84955/84114排空而不判定/提交。完整32bit sequence180327实际进入visited标签；不是将其截断为存储epoch。

| 指标 | 32槽 | 单槽 |
| --- | ---: | ---: |
| 仿真总周期 | 1049101 | 1067253 |
| label读事务 | 1007 | 1980 |
| label写回复 | 651 | 1111 |
| State读拍 | 170 | 170 |
| 最终native记录 / 有效页 | 822 / 403 | 822 / 403 |

完整16384物理帧、822条native最终读取、全design图像、owner primary/pool/allocator和cost字节一致；graph/design/label/owner/cost/qstate/table全部AXI事务逐字节重放通过，保留192B页在4KiB边界拆分的检查。design保持真实warm初态，没有新增created；owner/cost不发生搜索外提交。两配置只是容量压力回归，不能把总周期差称算法优化或板卡收益，周期包含TB导入、host读取和调度开销。

边界：这是从CPU准备态恢复一个真实后续query。仍没有同一RTL实例前query backtrace/owner提交→价格更新→后query prepare的连续生命周期；外层仍TB，标签822条工作集仍由CPU预知，未知页默认初始化未解决。实际FPGA板卡/GPU实现与整机性能未完成。

持久化：435文件/20526661B归档已逐成员核验。原scratch移至.preserved后实际恢复，完整主审计重新计算逐字节一致；收据followup_rtl_restore_20261025.json。run.py check与脚本语法检查通过，功能证据来自上述仿真/独立审计。
