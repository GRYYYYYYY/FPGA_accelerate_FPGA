# 同实例同网连续查询通过

同一Vivado2022.2 RTL实例，一次配置/复位/初始导入，执行logicnets首query和同网query2。328条初始联合读工作集全部来自q1初态；没有query2前重新加载标签、owner或design。109份生产RTL/dat保持基线；外层TB与装载脚本独立适配。

首query实际heap POLL/target完成后，从实际标签沿prev回溯150697→1411724→3919432→2988027→1431200→554512→263946→65185。7跳均由前一次标签读出的prev决定，没有CPU路径地址表驱动；6内部节点经真实host owner INC、成功响应后退休，源/汇不计入。完整owner primary图像逐字节等于CPU query2准备态；所有owner AXI写仅6次成功回复。

随后5次标签字段写清旧target、置新target、source lb/upstream=0、visited=2。读取328条标签全部等于CPU q2准备态后，实际heap seed和POLL驱动query2（conn16497、net2717、sink128009、sequence2）搜索。保留首query建立的children缓存/created/旧标签和真实占用；query2共享成本由实际owner读取决定。价格、存储epoch不变，搜索sequence独立改变。

| 两查询合计 | 32槽 | 单槽 |
| --- | ---: | ---: |
| POLL / expand | 116 / 114 | 116 / 114 |
| 判定 / cost-OFFER | 447 / 293 | 447 / 293 |
| 标签ACK | 879 | 879 |
| 总仿真周期 | 677359 | 740354 |
| label读事务 / 写回复 | 597 / 260 | 1526 / 615 |
| State读拍 | 114 | 114 |

独立主审计逐项比较两query全部POLL/候选/23字packet/5字成本/879ACK、每query328条末态、中间328条准备态和实际prev/owner轨迹；完整设计缓存图像/owner/cost/16384标签物理帧及七类AXI字节重放通过。两槽数的最终标签和owner SHA相同。具体页数、哈希与事务计数见JSON。

限制：回溯/提交/prepare由TB任务通过真实接口调度，未实现可综合自主backtrace或连续search controller；q2末路径尚未提交，故未覆盖两条同网分支同时提交后的引用增量/ripup。预知联合工作集328条仍由CPU oracle提供；未知页初始化、价格切换/epoch回绕、多net并发及板卡性能未覆盖。周期包含验证导入/读回/调度，不是加速结论。

来源continuous_query_sources_20261025，契约hardware/variants/continuous_query_v1/CONTRACT.md，主审计scripts/audit_continuous_query_rtl.py。MCP同PID147904，221.349秒exit0。下一优先补q2提交/共享引用与ripup，再将TB回溯提交序列移为可综合控制器并推进价格/未知页生命周期。

持久化：oracle与437文件RTL归档已逐成员核验，实际移走原scratch后恢复。主审计重新计算逐字节一致；收据continuous_query_restore_20261025.json。最终120逻辑页/328条native，两配置标签SHA均da1dcababf5d057904dade4a5271bdfe7165a7a1c8016425207362a27e205bad。run.py check及四脚本语法检查通过，功能证据以仿真和独立审计为准。
