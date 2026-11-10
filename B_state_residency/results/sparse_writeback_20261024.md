# 写回稀疏记录控制消融（2026-10-24）

独立变体 `hardware/variants/sparse_writeback` 已实现：同步读取驻留存储的有效位图，跳过无效记录的 EXPORT；仍向 codec 提交全部八条记录，页格式为原 192 字节，AXI 传输字节量不变。REFILL 仍逐条 BEAT。契约见变体目录 `CONTRACT.md`。

## 已完成证据

| 检查 | 结果 |
| --- | --- |
| 全 256 位图，含空页、全有效、有效零值 | 512 WB/RF、256 fence、5377 checks，通过 |
| 过早 COMPLETE、重复 EXPORT、错误事务/generation、租约期间写入 | 22 checks，通过 |
| 九类 AXI/格式错误与故障隔离 | 9 faults、68 成功传输、267 checks，通过 |
| 32 槽背压、保留 CHECKPOINT | 800 阻塞周期、8 CHECKPOINT、288 传输、1778 checks，通过 |
| 真实值配对先导 | 19 查询、75194 原始命令、5183 传输，通过 |
| unsigned64 周期先导 | 所有时间收据、计数、重试与 signed32 候选一致，通过 |
| 默认容量内部物理 | WNS1.726/WHS0.039ns，当前模型内部失败与route错误0，非平台闭合 |
| 默认容量综合 | 12949 LUT、11175 FF、375 BRAM、3 DSP、0 latch，源码绑定通过 |

`audit_sparse_writeback.py` 检查六个 case 的冻结 RTL/TB、生成器、编译集合、顶层、工具退出码及日志，并独立以传输索引连接实际命令和期望页位图。先导共有 2993 次 WB，保留 6357 次有效 EXPORT，省去 17587 次无效 EXPORT；每次 WB 全部八条 codec 输入仍逐值核对。

原版 16 位组合与候选使用同一有界 FINISH 重试检查器。控制组为 20603280ns，保持与原基线相同；候选为 19479270ns，减少 **5.45549%**。候选发生 1 次合法 FENCE_WAIT 重试，已计入实际时间与 75195 次检查；查询收据的非时间字段、内存传输计数及功能结果保持一致。测试台固定响应检查和周期性背压都包含在时间内，不是板上吞吐。独立逐查询分区 `sparse_writeback_pilot_intervals_20261024` 验证区间求和闭合，19/19 区间缩短，幅度 0.9766%–8.8625%；不是纯服务延迟或因果拟合。

首版严格 FINISH 测试在第六查询结束处收到状态 7 而失败，目录 `sparse_writeback_20261024` 保留 failed 状态与 failure_classification.json；只使用其中已通过的位图/故障 case 证据，不将整个首版称通过。独立配对重试检查器对每次 FENCE_WAIT 验证 allocation/epoch/租约与 fence 状态未提前回收，最多重试 20 次，其他错误仍拒绝。

默认容量为 163840 帧、hash18、目录 epoch16，综合相对原生 epoch16 增加 **126 LUT / 8 FF**，BRAM/DSP 不变。MCP147904 综合终态 exit0，279.857s，checksum 61fb09d2；`sparse_writeback_synthesis_20261024/final_audit.json` 验证参数、报告、DCP 与先导源码一致。综合不代表物理时序通过。

## 全量与物理状态

完整 38 查询：唯一 workflow `run_sparse_writeback_full_workflow.py`，目录 `sparse_writeback_full_workflow_20261024`，初始 PID3960194、子 runner3960259、工具66155。使用新 unsigned64 TB、相同冻结向量，终态自动独立审计并复算全量 WB 位图工作量。先导收益不得外推为完整收益，不重复提交。

默认容量内部物理已终态并独立审计：`sparse_writeback_timing_20261024`，MCP147904，407.735s/exit0。布线后12860 LUT、11172 FF、375 BRAM、3 DSP，相对原生16位增加110 LUT/11 FF；WNS1.726ns、WHS0.039ns、WPWS4.458ns，当前内部失败和路由错误为零。保持10ns/Default及相同约束；最差路径在目录BRAM到indexed_frame寄存器，不能将不同布线结果的slack差异视为一般Fmax收益。2022.2文本方法学报告/约束差异/路径均已绑定，627输入/847输出缺delay及上游时钟模型缺口保留，非平台闭合。cell3433旧running交接已正式终态，会话现idle，不重投。

默认 RTL、现有 6 位源包及已经完成的 16 位全量回放不变。下一阶段依据全量回放和资源/物理结果决定是否推进回填空记录控制；目前尚未实现 RF 合并、完整 FPGA 路由器或 XRT/板上验证。

补充全量输入普查：`page_density_by_direction_20261024` 以全部命令/页字节哈希及传输索引绑定，WB 621624 次：有效1724306、空3248686；RF1850442次：有效6030214、空8773322。RF占全部空记录72.9772%，是后续控制合并研究的工作量依据，不是本候选全量执行、预期周期收益或传输压缩证明。
