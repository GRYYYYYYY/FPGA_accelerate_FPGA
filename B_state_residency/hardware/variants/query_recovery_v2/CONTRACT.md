# 查询故障后的路由退休判定

本变体只替换 `query_lifecycle_v1/query_residency_system.sv` 的一处排空条件。模块名、端口及全部内部生产组件不变；独立目录保留原版反例。

原路由适配器 `busy = held || c_busy || c_fault`，包含锁存故障。错误提交回复被消费后，即使围栏已退休、后端和 AXI 已排空，`!rc_busy` 仍不成立，外层查询停在 DRAIN，恢复命令被 `qc_busy` 挡住。

新条件为：

```verilog
f_normal_retired && f_backend_idle && f_all_drained && !ss_busy &&
(!rc_busy || (rc_fault && f_phase == 6))
```

`6` 必须对应冻结版本事务围栏的 BLOCKED 状态。围栏在 ROUTE 状态消费原生路由完成后进入 RDRAIN，确认 `clean` 后才能进入 BLOCKED。外层查询也必须先消费原生路由完成才能进入自身 DRAIN。因此该分支允许已退休的锁存路由故障交接，不允许仅凭 AXI 空闲就复位仍拥有请求的服务。

正常无路由故障时，条件与原版完全相同。新条件不清除故障、不清除占用、不伪造成功，也不撤销已暴露请求。原生错误 ACK 计数可能为零，而内存已经执行错误 B 回复之前的写入；必须由 journal/authority 修复实际副作用，然后恢复标签并重跑。

运行：`python3 scripts/run_query_fault.py RESULT --route-fix`；独立审计：`python3 scripts/audit_query_fault.py RESULT`。结果以相应 manifest/audit 为准；诊断审计通过不能解释成所有故障恢复成功。原版完整矩阵由不带 `--route-fix` 的入口运行。

此修复不解决图读取错误后的 capture/递归任务退休、代价预取错误后的候选链退休，也不构成任意设计 checkpoint。恢复 fixture 只提供 q1 六个内部路径节点的 owner authority 和 CPU 已知 328 条初始标签，保留 design backing memory。没有新增布局布线、时序或板卡性能证据。
