# 完整系统共同发布与正常 q2 连续性

本变体基于已审计 checkpoint_system_v4，在 query root 增加受原生 lease 约束的只读 authority 检查接口；其他生产 RTL 完全沿用。不改公共基线。run_checkpoint_commit.py 每次冻结源和测试、使用 Vivado/XSim 2022.2，分别执行 32 槽与单槽压力场景。

完整系统先完成真实 q1 工作写、owner B 错误、原生 coordinator 修复及 q1 重试，再通过原生 lease 完成已有元数据取消检查与路径/查询导出。此前各工作 AXI 流必须与已独立审计 bundle_capture_v3 的完整流前缀逐字节一致。

候选 authority 在独立只读 AXI 地址窗口映射已提交 bundle 的完整 owner primary+allocator。该图像必须与前缀工作写后的 owner 图像逐字节一致；未使用手写六行 owner 表。旧只读 authority 图像仍保留。此映射由测试环境提供，尚无运行中工作 DDR 快照生产器。

同一真实 lease 内准备 authority、coordinator checkpoint、当前有效配置。保持候选 authority 回复八周期时仍绑定旧身份，且不能发布或释放 lease；coordinator/config 回复同样保持八周期。共同发布必须恰好出现一次 3'b111 握手：G1/CP17/journal6 → G2/CP18/journal0。完成回复保持八周期，消费后才允许释放 lease。上下文 version4/query2/price4 不变，未改变价格，因此本轮不涉及跨价格距离标签复用。

发布后原 G1 查询镜像导入应被原生控制器拒绝；导出的 G2 40B 查询镜像须与 bundle/query.bin 一致，序号下限仍为1，新镜像完整导入后才能释放 lease。随后通过现有 CPU 独立 oracle 继续 q2：43 poll、42 expand、176 candidate、122 cost。原生保存路径参与共享引用及两次拆线，两个共享节点的 ref1→2→1→0，资源占用按不同 net 计数；42 次 owner probe 校验。完整八路 AXI 与最终 DDR 由独立字节重放校验，最终 owner 仅目标路径并集清零，原其他 net 状态保留。

候选配置仅检查布局，不读取 DDR。发布完成消费后、lease 释放前，通过新增 ap_* 公开只读接口对原生 reader 发起一个旧 generation 请求（拒绝，无 DDR 读）及七个新槽 GET（六个目标资源及 node0/net4754）。每个成功 GET 从新窗口实际读取 allocator 和 primary 行，共14 beat，回复保持八周期仍禁止释放 lease。所有新请求和回复经同一原生 reader/AXI；不使用 force 或层次写。正常 q2 仍访问工作 owner。换代后故障恢复尚待做。

ap 请求只在持有 lease、无元数据事务/恢复/配置争用且没有先前 ap 回复拥有权时受理。已受理请求保存回复拥有权，消费前阻止 lease 释放和元数据事务开始；只将回复 VALID/READY 分流，原生 payload/status 保持。错误身份回复报告活动绑定的 generation2，不回显请求中的旧 generation1。

没有执行发布后的 target reset/故障修复；不能声称保存 path/query/label 已在 warm 恢复中重建。manifest_ready 仍为测试输入，不证明持久化原子提交、认证或外部反重放下限。尚无通用多 net/overflow、运行中快照生产、综合/时序闭合或板卡加速结论。
