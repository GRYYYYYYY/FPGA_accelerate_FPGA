本轮补齐了静态事务围栏接入后的正常双查询、共享路径释放，以及真实成本服务续接退休回归。两套激励各跑 32 槽和单槽，共四次 XSim 2022.2 完整运行均正常退出；CPU、请求账本、全图像和 AXI 字节独立审计通过。生产 RTL 沿用上一轮版本，本轮增加的是验证激励、观测和审计脚本。

机器证据见 [结果 JSON](transaction_fence_normal_20261025.json)、[接入前后比较](transaction_fence_normal_comparison_20261025.json)、[正常双查询审计](transaction_fence_normal_rtl_v1/source_bound_audit.json)、[真实续接审计](transaction_fence_normal_dependent_rtl_v1/source_bound_audit.json)。可重建激励的契约在 [CONTRACT.md](../hardware/variants/transaction_fence_normal_v1/CONTRACT.md)，73 个冻结文件在 transaction_fence_normal_sources_20261025/sha256.json。

每次运行均完成 116 次真实 heap POLL、114 次展开、447 次判定、293 次成本/提交/OFFER 和 879 次标签写确认。下一 parent 来自硬件 POLL，CPU 文件只核对结果；第二查询继承第一查询的真实状态，只做 5 个标签字段准备更新。328 条最终标签及中间准备标签、全部 16,384 个物理帧、完整 design/owner/cost 图像均已核对。仍使用 CPU 预知的联合工作集，外层搜索与准备仍由 TB 驱动。

四个 owner 阶段为 q1 commit、q2 commit、q1 ripup、q2 ripup。两条路径共有内部节点 554512 和 263946，refs 精确经过 1→2→1→0，distinct-net occupancy 经过 1→1→1→0。第二次提交后的全 owner 图像逐节点对照 CPU q3 准备态；两次释放后的 owner 文件恢复为原始 SHA `0155da223647bd763b9d90016f2a032a8f43204c775b675de4368765f0f55fa5`。24 次实际修改均先完成 journal 握手，再转发 owner 服务；去重后保留 10 项日志，没有通过清日志假造 checkpoint 推进。

每种正常配置接受并退休 3,032 个主机/admin 请求，前后端完整 packed payload 一致，无丢失或重复；另有 4 条 route 命令。新增真实续接配置为 3,036 个请求，每条查询首个 root 回复上各叠加一次真实 center HLS 请求和一次 cost AXI 读取。前端先消费父回复，两个子回复随后保持 7 个周期背压；operation_pending 和主机排他屏障在此期间保持，两个子回复消费后才 ACK 后端父回复。四个这样的真实服务场景均通过，无需修改围栏 RTL。center 的零坐标/中心得到状态0、距离0；cost 读取 source65185 的原始 history=1.0，额外两次读取不改变任何内存图像或路由语义。

七类 AXI 记录全部重放，但只有六类在本查询中有实际流量，table 未触发。每次 graph 7,096 个读事务、design 1,364 个读事务及 326 个写回复、owner 830 个读事务及 24 个写回复、qstate 114 个读事务。cost 基线 879 个读事务，续接版 881 个。32 槽 label 为 605 个读事务/260 个写回复，单槽为 1,535/615。不能以 table 的零流量审计声称覆盖了其活跃排空。

与接入围栏前的 route_join_drain_rtl_v1 相比，全部路由语义事件、四种完整内存图像和七份 AXI 文本逐字节保持一致；周期戳有变化。整段测试包含配置、初始导入、搜索、准备、提交、释放和检查：

| 配置 | 接入前周期 | 围栏组合周期 | 增量 | 增幅 |
| --- | ---: | ---: | ---: | ---: |
| 32 槽 | 680,767 | 683,640 | 2,873 | 0.422% |
| 单槽 | 743,652 | 747,471 | 3,819 | 0.514% |

该组合同时增加了 journal adapter 和恢复服务，不能把增量全部归因于 fence。真实续接版恰好取得相同总周期；周期性存储背压会改变等待位置，这不证明额外请求零成本。这里是行为仿真开销，无新综合、布线、Fmax 或板卡加速结论。

验证开发中修复了两个审计程序问题：计数变量遮蔽 native 解码函数；将 negedge 的最后一次持有观测和随后 posedge 的 ACK 误认为必须具有不同 cycle 值。后者依据测试台时钟和 trace 严格顺序修正，并继续要求 7 次连续持有观测、两个子回复先于后端父 ACK。另撤回了“七类 AXI 全部活跃”的错误假设，明确要求六类活跃、table 为零。失败日志和修复前续接审计保留在 transaction_fence_normal_development_20261025；没有降低生产 RTL 的运行断言或更改参考结果。

后续首先抽取完整可综合系统 top，去掉 TB 中的硬件连线与外层搜索流程；继续扩展 checkpoint 到 design-created/cache、frontier、路径和 legacy owner/design/cost 写入。当前初始化 checkpoint17 的 owner authority 只含第一条路径的六行，本轮从未触发恢复，不能据此宣称第二查询或任意写入恢复正确。恢复请求与搜索续接同时发生、恢复期间真实故障、table 活跃排空、unknown-page、价格变化与 epoch 回绕、容量预留、耐掉电和板卡仍未完成，研究目标保持 active。

两份归档均已将原 scratch 移开后实际解压，916 个文件逐 SHA 核对，独立审计重新执行并与原 audit JSON 逐字节相同；原始目录继续保留。见 [恢复收据](transaction_fence_normal_restore_20261025.json)。Python 语法检查与 `python3 scripts/run.py check` 通过。
