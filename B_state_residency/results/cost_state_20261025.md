# 设计级成本状态服务

独立cost_state_store已通过实际AXI功能与故障验证，提供history、256项价格表和只读net参数。查询关闭时BEGIN编辑，在成功B/回复退休后PUBLISH发布完整32位版本；query标签生命周期不清history。

| 测试输入 | 命令 | AXI读 | AXI写/B | 周期 |
|---|---:|---:|---:|---:|
| 合成 | 977 | 642 | 288 | 16157 |
| 真实CPU初始导入 | 1207 | 839 | 321 | 20101 |

每组4次query活动进入/退出；发布至18，旧version2即使低四位tag相同仍被拒绝。全部事务数据/字节strobe、回显与完整后备文件核验通过。真实导入包括9089009个history值、256价格和27960 net记录；RTL对history/net稀疏抽样，并非全表硬件扫描。后续修改为脚本状态，尚未回放完整route历史更新。

另99项实际AXI边界检查覆盖9次错误处理与10次显式后备重载：R/B错、AR/AW/W阻塞abort、超时、query漂移、edit围栏违规、版本耗尽和恢复。失败B前物理字节已改变；早期逻辑错误响应不代表物理排空，busy会保持。复位不能当回滚。

证据在cost_state_20261025/source_bound_audit.json与cost_state_boundaries_20261025/source_bound_audit.json。契约hardware/COST_STATE_CONTRACT.md。当前是独立服务，尚未接入candidate/pager的真实query OPEN与全版本身份、成本packet生产、数值历史更新或Frontier，亦未综合。此前候选链路资源不包含本模块；无板上加速结论。
