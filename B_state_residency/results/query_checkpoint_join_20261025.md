# 查询序号checkpoint接入实际系统（2026-10-25）

原生query_lifecycle组件已接入authority_query_v4完整层级，新增qc_cp_*接口并共用实际checkpoint lease。生产变化仅query_residency_system与query_lifecycle；其余120份生产RTL继承。原生核心与此前14查询/27checkpoint独立验证的组件逐字节一致。普通请求、查询、路由、恢复仍由真实层级和八路AXI驱动，没有以mock后端代替本轮工作。

| 场景 | 32槽周期 | 单槽周期 | 核验 |
|---|---:|---:|---|
| query局部诊断丢失后导入 | 835868 | 893022 | pending104周期；last_sequence1→0→1 |
| 诊断关闭的生产导入 | 835852 | 893006 | pending88周期；last_sequence保持1 |
| checkpoint接口闲置 | 835704 | 892858 | 与旧835704/892858周期保持 |

六例均先实际owner B SLVERR →修复已写但未确认的1项owner变更→真实恢复/读取核验328标签→完整CPU查询重跑：73polls、72expands、271candidates、171cost输出和6项owner提交。之后前四例执行40B流：导出0、坏期望CRC拒绝1、CRC正确但generation高32位错误拒绝1、正确导入0；所有回复持有6周期。成功导入回复尚未消费时pending仍为1，不能释放lease；消费后才清除。诊断reset是注册且有lease/空闲前提，仅query控制器丢失，非force。

导入开始即置生产qc_restore_pending，并非只在诊断下生效。失败后必须重试成功才能解除；导出不能解除。checkpoint guard命令busy包含pending/query_cp_busy；pc_quiet允许checkpoint自身busy而仍保留全部其他退休条件。path/query checkpoint互斥且query优先，ready与实际valid的仲裁一致。诊断默认参数0，生产导入例也按0编译；闲置回归同样关闭诊断。

恢复后将空闲slot1、合法design/version/query/price/source/sink等命令字段明确重建，再重放已经消费的sequence1。回复status1、prepare/cleanup/commit均0；source不是前次握手后故意翻转的无效引脚，因此不把其他参数拒绝当成序号保护。路径slot、完整2304bit配置描述、journal和authority绑定保持，nativeledger按图像恢复。

独立审计重建归档生成器、校验实际S/M全部字、以zlib验证CRC，并核对CPU poll/candidate/cost/path/label/owner、全部八路AXI字节和完整最终内存。每例8AXI+4图像与接入前authority_query_v4字节一致，共72文件比较；新增序号流和拒绝没有增加物理服务流量。不是全部trace周期等价或板卡加速结论。两个早期三命令诊断版本保留为开发证据，不代替选定四命令/生产默认关闭验证。

完整默认32slots/16384frames U280 Vivado2022.2 OOC：105272LUT/70954FF/160.5BRAM/23DSP，零latch/blackbox/file-agent，460逻辑端口/59438位。较旧104144LUT/70377FF增1128LUT/577FF。实际集成资源不等于独立组件增量简单相加，未布局布线/定时闭合/板卡测量。source662.463秒、临时MCP会话已关闭。

五归档2585文件均实际移走原目录、解压并重新独立审计，审计文件逐字节一致。17当前源/审核依赖及原两组件另冻结于results/query_checkpoint_join_sources_20261025。基础check通过，旧基线/其他方案未修改。机器证据见query_checkpoint_join_20261025.json，接口约束见hardware/variants/query_checkpoint_join_v1/CONTRACT.md。

运行：先执行该variant的build.py和build_tb.py；`python3 scripts/run_query_checkpoint_join.py /tmp/B_state_residency_offer_20261025/新目录`；生产无丢失模式加`--no-loss`，闲置回归再加`--bypass`；完成后audit_query_checkpoint_join.py同目录。

尚未完成全系统冷恢复。所有其他状态仍保留；k_cold_rst会清ledger、pending和lease。本轮frame的generation来自当前authority基线，基线owner图像早于当前working owner变更；后者及journal保留才使本次局部恢复一致。不能把该frame与早先初始owner快照单独配对冷恢复，也不能因generation相同就宣称同一时间点完整图像。恢复协调器attempt_version/query下限尚未序列化。

下一步是健康静止边界的新bundle提交身份与实际全状态捕获：提供待提交generation，捕获owner/allocator、query/path流、完整labels/目录、design/history/价格、实际当前配置和journal边界，完成各组件真实恢复receipt后才发布并放开boot业务。当前静态配置描述不一定等于恢复后的active版本，必须显式保存实际上下文。不能用软件常量done或只丢一个模块代替完整冷启动测试。warm非零owner、未知页/旧prev/frontier、实际价格变化/回绕/容量、耐掉电/认证/不可变、lease持有期AXI故障接管和板卡仍缺；goal active。
