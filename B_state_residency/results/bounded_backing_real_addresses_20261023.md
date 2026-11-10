# 固定字节后备池完整地址回放

状态：完整回放及终态审计均 passed。进程3736475/工具句柄82952已正常结束，当前无活动队列。

运行证据：`bounded_backing_real_addresses_20261023T022124Z/`，driver `scripts/replay_bounded_backing.py`，终态审计 `scripts/report_bounded_backing_replay.py`。容量依据见 [查询页需求](query_page_demand_20261023.md)。

单owner、4个驻留页、每页64节点，后备预算13 MiB，实际预分配23665个576B页（13631040B），余448B不使用。query之间执行完整fence，地址才回收；中途checkpoint从当前页状态导出，不能从oracle恢复。有限16位事务/槽代次、2位query和2位fence tag保持前版配置。

所有读访问核对独立合成序号oracle；checkpoint和查询末尾额外直接解码原始bytearray并合并驻留值，比对完整逻辑映射。最终要求1132查询/16151535访问完整覆盖，全部数据与控制计数与前版一致，并检查输入/源码/冻结副本哈希。92项既有测试通过，日志位于运行目录tests.log。

这是来自真实路由的访问地址与合成int64写值，不是真实距离标签或实际路由计算。预算只约束raw bytearray，host shadow、所有权表、队列、快照、驻留值和设计全局状态均另存；没有总RSS、DMA、并发、RTL或速度/带宽结论。NodeDyn含历史拥塞，不能据本回放将其全部字段按connection清零。

最终覆盖1113个间隔样本查询（2399968访问）和19个大查询（13751567访问），总1132查询/16151535访问，无截断或跳过。63次中途checkpoint恢复、1195次完整fence、298次2位控制tag回绕、2390次重复ACK；数据/控制计数与前版逐项相同。所有查询最终值与checkpoint值核验通过，包括原始后备字节解码。

终态证据：[completion_audit](bounded_backing_real_addresses_20261023T022124Z/completion_audit.json)，manifest SHA256 `a30f6e26b8f724c18b9a62535ea5d3ac576507b724ded1f01c8d1c829288d49a`。审计核验完整覆盖、计数关系、容量与轨迹绑定、运行前后源/输入及冻结副本哈希；它未独立重跑值oracle，值断言由冻结driver执行。

后续优先将真实字段按生命周期拆分，明确hist/价格状态与connection标签的边界，再接入相应codec及真实值轨迹。当前13 MiB结论仅覆盖已选真实地址轨迹和合成int64布局，不能外推为真实NodeDyn或其他设计的容量需求。
