# Checkpoint 元数据联合发布通过（2026-10-26）

详见 hardware/variants/checkpoint_stage_v1/CONTRACT.md 与 results/checkpoint_joint_20261026.json。选定 checkpoint_joint_v7，真实 lease guard 下，双槽 authority、coordinator checkpoint/journal 和有效配置影子状态由共同发布屏障协调。

205 次检查与独立审计通过。四个事务依次为身份错配、显式取消、配置槽 abort 后部分取消、成功发布，状态 1/2/2/0。前三者保留旧 checkpoint17、generation1 与六项 journal；成功事务只有一次共同发布沿，切至 checkpoint18/generation2 并清 journal。准备回复、旧 GET 回复与完成回复保持时的封锁得到验证。发布后同版本恢复请求被原生 coordinator 拒绝，attempt floor 保留。5 个 GET、8 个 AXI 读 beat 与完整两份 owner 图像独立重放一致。

归档已实际移走原目录后恢复、重新独立审计，audit 逐字节一致。当前源码冻结 results/checkpoint_joint_sources_20261026。

范围仅元数据切片：journal 来自已验证 bundle 六项 delta 的接口输入，没有新执行工作 owner 写；无 route engine，route_retired 固定1，manifest_ready 为测试输入。没有执行真实恢复或原生配置 provider 回调，尚无 path/query/label 联合恢复、运行中工作 DDR 快照生产、多 net/overflow、综合/时序/板卡收益证明。

下一优先将屏障和影子元数据接入完整顶层的真实退休/lease/manifest 条件；验证换代后 q2 故障恢复，在 target reset 后恢复保存的 q1 path/query/label 与序号下限，再放行业务。研究继续，goal active。
