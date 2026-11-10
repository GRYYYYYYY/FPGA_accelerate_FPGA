# 完整系统共同发布及正常 q2 连续性通过（2026-10-26）

详见 results/checkpoint_commit_20261026.json 与 hardware/variants/checkpoint_commit_v1/CONTRACT.md。选定 checkpoint_commit_v6；在已审计 checkpoint_system_v4 的 query root 增加受原生 lease 保护的只读 authority 检查接口，其余生产 RTL 不变。

32 槽与单槽压力两例先完成真实工作写故障/修复/q1重试及取消检查，随后在真实 lease 下准备三个组件。候选 authority 使用已提交 bundle 的完整 owner 图像，与原工作结果逐字节一致。保持准备回复时旧身份不变，每例只有一次 111 共同发布：G1/CP17/journal6 → G2/CP18/journal0；完成消费前 lease 保持。配置仅检查布局、不读 DDR。发布完成后，公开 ap 接口通过原生 reader 拒绝旧 generation 请求，再 GET 六个目标资源及已有 node0/net4754；七次成功 GET 从新窗口读取14个 beat，完整字节重放与回复保持/lease 封锁核验通过。

发布后原 G1 查询镜像导入失败；新 G2 导出40B镜像与 bundle/query.bin 一致，序号下限1保留，成功导入后才释放 lease。真实 q2 正常继续，43 poll/42 expand/176 candidate/122 cost 均对照 CPU oracle；两个共享节点 ref1→2→1→0、42 次 owner probe、两条原生路径拆线通过。全部八路 AXI/最终 DDR 独立重放，原其他 net 状态保留。前缀工作事务与旧已审计完整日志逐字节一致。归档已实际恢复重审，audit 逐字节一致，新增源冻结 results/checkpoint_commit_sources_20261026。

本轮只证明同一上下文 version4/query2/price4 下的正常换代与继续工作。新 authority 节点 GET 已通过公开只读接口验证；普通查询仍访问工作 owner。尚未执行换代后的故障/target reset；保存 path/query/label 与序号下限的 warm 恢复联锁仍待实现和验证。manifest_ready 是外部测试输入，无运行中工作 DDR 快照生产器、通用多 net/overflow、持久化认证/原子提交、综合时序或板卡加速结论。

下一优先完整系统换代后 q2 故障恢复：实际从 G2 authority 修复 owner，target reset 后恢复保存的 q1 路径、查询与标签及下限，再放行业务和重试。研究继续，goal active。
