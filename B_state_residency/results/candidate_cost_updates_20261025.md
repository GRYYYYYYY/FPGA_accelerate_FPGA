# 联合发布可见性与边界

当前candidate/pager/cost-state wrapper新增8组实际联合验证，源绑定审计通过，未改RTL。

- 活动query内BEGIN被拒绝；关闭后实际SET history与price、PUBLISH3→4，两次真实pager query均读到新值。排队OPEN等待发布，未阻塞PUBLISH；core结果先退休后lease仍保持。
- full19对full3虽然低4位tag相同，陈旧OPEN和expand均未被接受，且无graph/design/cost AXI副作用。
- 已接收配置的节点数或给定设计ID不一致时停止。
- actual R/B错和AR阻塞abort正确传播/排空；已暴露core final保持稳定。失败B可已修改数据，但没有发布新版本。

每组成本事务与完整cost/owner/design后备独立核验；故障用例各自新进程导入，不证明同会话reset/reload恢复。脚本SET数值测试字节可见性，不代表真实拥塞更新公式。完整记录见candidate_cost_updates_20261025/source_bound_audit.json。

另当前wrapper默认163840帧/18位目录回归通过：1212扩展、3022判定、60EARLY、9067成本读，全部与冻结参考及原始文件一致；仿真1694377周期，不是板上速度。记录candidate_cost_default_20261025/source_bound_audit.json。

candidate_cost_revision_20261025.json绑定三组功能配置和边界的54份同一RTL，可供下一步联合综合。成本读仍由TB发起，内部成本包/算术/标签提交/完整search尚未接通；无板上加速结论。
