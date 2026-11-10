# 真实服务恢复接入 v1

本变体将 recovery_coordinator_v1 接到真实分页标签、owner AXI 和 route_commit_controller。正常 route owner 修改先与 j 接口握手，寄存请求，至少下一拍才向实际 owner 服务发送。日志由独立 cold_rst 管理；target_reset 只复位目标服务，不清 journal。后端单挂起 AXI 排空观察器继续使用 drain_v2，不支持通用多 ID 乱序事务。

恢复协调器控制准入、排空/原响应退休、5 拍 target_reset、重新配置回调、两遍 owner 修复/验证、标签回调和持有响应后放行。owner GET/DEC/GET 使用真实服务和 AXI 文件存储；无文件替换、直接清 owner 或 backdoor 修复。恢复前错误返回可能已修改物理数据，不能由 ACK 数反推副作用。

coordinator.inc、observer.inc 和 build_tb.py 是验证连接与回调模型，不是完整可综合生产顶层。CPU checkpoint authority、配置发包、328 条标签重载/读回仍由测试台提供。输入是实际 CPU query1 搜索末态；故障恢复后重试回溯提交，不重新执行搜索。checkpoint17 是提交前状态；成功恢复并重提交后发布 checkpoint18，权威数据取自 CPU query2 准备态。该 checkpoint 只覆盖本次提交相关状态，不是完整 search/frontier/warm 状态快照。

容量32、最多6个本次提交内点，实验不存在容量超订。生产调用方仍须事先预留日志空间、排除其他写者并验证快照身份。cold_rst 会丢失 journal；不提供耐掉电、版本/epoch 回绕、未知页工作集或任意并发恢复保证。此接入未测板卡、完整系统资源或 Fmax，正常双查询共享路径/ripup 尚未用此新增 journal adapter 做回归。

runner：scripts/run_recovery_join_rtl.py；独立审计：scripts/audit_recovery_join_rtl.py。须十例全部通过且 source_bound_audit.json 为 passed 才算本次组合验证通过；不能仅依据编译成功或一例 PASS。
