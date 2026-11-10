# 回填稀疏记录控制增量（2026-10-24）

组合变体 `hardware/variants/sparse_records` 在仅稀疏写回版上增加有效 BEAT 和一次受信任 RF_MASK 收尾；页字节量、公开端口和 AXI 布局不变。`CONTRACT.md` 明确了内部信任边界及原生 ingress 拒绝14，不能将独立控制器的 bitmap seal 误当作内存或完整解码证明。

## 已完成实验

| 项目 | 证据 |
| --- | --- |
| 全256位图，含空页、全有效与有效零值 | 512次WB/RF、256次fence，通过；两方向各1024有效确认/1024空记录省略 |
| 协议边界 | 33项，通过；早COMPLETE、重复seal、错误事务/generation、非规范位图、有效确认缺失/多余及新租约重置 |
| 九类AXI/格式故障 | 9 faults、68成功传输、267 checks，通过；错误时保持隔离 |
| 32槽、背压与保留checkpoint | 800阻塞周期、8CP、288传输、1778checks，通过 |
| 真实16位epoch回绕 | 65536合法回收、1真实回绕、16384 tag回绕、574合法FINISH重试、197223checks，通过；32帧/hash6，仅4个合成数据查询8次传输 |
| 配对真实值先导 | 19查询、75194条原始命令、5183传输，通过 |
| 默认容量内部物理 | 12624LUT/11208FF/375BRAM/3DSP，WNS1.100/WHS.035，当前内部失败和route错误0；非平台闭合 |
| 七组冻结源码/编译/日志与位图普查审计 | `sparse_records_20261024/source_bound_audit.json` passed |

控制组使用与组合候选相同的unsigned64检查器、响应等待超时和有界FINISH重试规则，关闭RF稀疏控制，保留WB稀疏控制。控制组所有时间收据/计数/end19479270ns均复现已审计的WB-only先导（含1次合法FINISH重试）。组合候选end18927670ns、FINISH重试0，增量仿真时间减少 **2.83173%**；相对原生16位20603280ns减少 **8.13273%**。独立查询分区分析 `sparse_records_pilot_intervals_20261024` 验证19区间求和闭合：18区间缩短、1不变，最大缩短4.34505%。这不是纯BEAT延迟：重试及周期性背压相位变化已计入，不从两者差额外推平台收益。

先导WB2993次，6357有效EXPORT、17587空EXPORT省略；RF2190次，5503有效BEAT、12017空BEAT省略，额外2190次位图seal。两个方向仍消费全部八条codec记录。功能、查询非时间收据和AXI计数保持一致，页负载仍为5183×192字节。

默认容量综合163840帧/hash18/epoch16：**12706LUT、11211FF、375BRAM、3DSP、0latch**。相对WB-only减少243LUT、增加36FF，BRAM/DSP不变；源码、DCP、参数和报告审计通过，checksum9cbc31ac。该映射差异不能单独归因为特定表达式删除，综合不能证明物理时序。

## 全量状态

组合内部物理已终态：`sparse_records_timing_20261024`、MCP147904，413.206s/exit0；独立audit_sparse_records_timing.py通过，当前会话idle。布线后12624LUT11208FF375BRAM3DSP，比WB-only少236LUT、多36FF；WNS1.100ns、WHS0.035ns、WPWS4.458ns，内部失败和路由错误0。最差路径仍在目录BRAM到indexed_frame_reg[15]/CE（数据路径8.749ns）；相对WB-only时序余量减少，但同样通过此10ns/Default模型，不据此宣称Fmax或平台收益。627输入/847输出delay与上游clock模型缺口保留。METHODOLOGY_RESOLUTION_REPORT.md及constraints_diff.html已绑定，22个artifact哈希核对通过。cell3472旧running交接已正式终态，不继续wait/source。

原WB-only完整38继续原workflow3960194/工具66155、runner3960259，未重投。新组合全量监督者 `run_sparse_records_full_workflow.py`，目录 `sparse_records_full_workflow_20261024`，PID351225/工具17706，当前waiting_wb_full，commands为空；它只在原WB全38终态审计通过后启动一次组合全38，并自动执行独立audit_sparse_records_full.py，比较WB-only/原生16位及全部WB/RF记录普查。不修改任何旧活动源、失败证据或已导出6位源包；没有Luna选择接口，沿用确定性30秒只读依赖核验，不创建第二个原WB恢复者。

组合全38尚未开始，没有全量收益。完整FPGA路由器、平台/XRT、实卡测量及端到端CPU优于原始路径均未完成，研究继续。

补充相位分析：`sparse_records_phases_20261024` 的6case（0/1/31整体相位×WB-only/组合）已独立审计；三组增量2.83172%–2.83173%，时间差均551600ns。它只检验共同相位平移，不能代表通道相对时序或随机置信度。`sparse_records_relative_phases_20261024` 使用8通道不同偏移权重1/3/5/7/11/13/17/19，也已6case终态审计。两者保持相同RTL、数据、周期及host4cycle检查，不修改活动全量源。


通道相对相位结果（每行均为相同调度下配对，19查询；固定host4cycle检查）：

| 场景 | WB-only / ms | 组合 / ms | 增量减少 |
| --- | ---: | ---: | ---: |
| 0 | 19.47927 | 18.92767 | 2.83173% |
| 1 | 19.46391 | 18.91581 | 2.81598% |
| 31 | 19.46371 | 18.91561 | 2.81601% |

三组均保持同一RTL、数据和确认/传输计数。该结果限于选定确定性相对相位；没有随机抽样、置信区间或真实主机/DDR延迟模型。两个相位实验均终态，工具49543/20691不再等待。原WB全量和组合依赖监督者仍由各自原进程持有；`sparse_queue_observation_20261024T113516Z` 已通过PID身份及8个冻结脚本核验，组合尚未启动且commands为空。
