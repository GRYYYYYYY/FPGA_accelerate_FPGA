# 记录响应 FIFO 直通消融（2026-10-24）

独立候选放在 `hardware/variants/record_response_fallthrough/`，默认 RTL 与冻结基线未改。只对页记录 EXPORT(9)/BEAT(7) 的响应启用空 FIFO 直通；请求/工作/控制队列不变。背压时响应进入原容量存储，count 表示实际存储占用。该方法是成熟弹性缓冲机制的场景适配，不宣称方法本身新颖。

19 查询真实访问先导通过：75194 命令、5183 传输、全部非时间查询/checkpoint 收据与功能终态计数一致。端点仿真结束时间 20885360 → 20603280 ns，减少 1.350611%。不是主机执行时间、完整路由或板上加速。周期相位改变会改变排程 gap，因此仅放宽 gap_cycles/host_stalls 两项时间相关终态计数；其他字段保留比较，原 TB 的数据/协议检查均启用。

已完成验证：

- FIFO 深度 1/3/4，确定性随机握手顺序计分板、满队列、同时入出队、输出稳定、复位丢弃旧状态。
- 4 页多字段与 32 槽端点；8 次 checkpoint、4 次 tag 回绕；8 种阻塞场景累计 800 周期，逐前置条件阻塞检查保留。
- 门控定向：控制响应必须存储一周期，记录空队列直接交付，阻塞记录必须捕获且只交付一次。
- 九类 AXI/页格式故障：候选与默认各 267 检查、68 次成功传输；故障后页/内存租约保留、封锁后续命令、已接受读事务排空。
- `audit_record_response_variant.py` 独立核对先导编译源集合、所有冻结源哈希、仅两处队列接线变动、实际 TB 不变及语义收据与耗时计算。

失败和范围修正均保留：

1. 初版全响应直通先导减少 4.0714%，但旧小容量 fence 序列在 ACK 尚未消费时 FINISH 返回合法 FENCE_WAIT，测试台却等待进入回收。诊断日志 `response_fallthrough_fence_debug_20261024` 保留，此版不作为后续候选。
2. 记录专用候选完成了该 fence 序列，之后与默认版都在旧故障测试 check320 失败。旧测试仍使用宽页的第3帧触发4KiB后错误，小页对应第21帧。新 `make_response_fault_tb.py` 独立提取故障序列，校正跨界帧并对默认/候选配对验证；没有改旧冻结 TB 或关闭断言。该提取测试不承担 fence 验证，fence 由上述端点/阻塞测试承担。
3. 初始 runner 错把 TB 文件名当作顶层名称，在 elaboration 失败；还发现 plusarg 切片遗漏 flag。`response_fallthrough_20261024` 的失败清单保留，先导恢复在独立 v2 目录，未覆盖失败记录。

完整 38 查询实验 `record_response_full_20261024` 已启动，原工具会话 76142；终态观察器 `record_response_full_watch_20261024` / 会话13400只观察原 runner 并在成功后执行独立全量审计，不会重启。当前无全量收益结论。恢复先检查 manifest/原进程，不重复运行同名实验。后续仍需综合/布局布线验证新增响应多路选择路径的时序和资源代价，再决定是否采用。

默认容量综合已完成并审计：`record_response_synthesis_20261024/final_audit.json`，14909 LUT / 11177 FF / 319 BRAM / 3 DSP / 0 latch。相对动态 codec 默认基线增加258 LUT、13 FF，BRAM/DSP不变。先导逐查询比较19/19区间缩短，见同目录query_intervals.csv；区间包含协议/TB节奏。

物理实现已在原空闲MCP147904启动：`implement_record_response.tcl`，`record_response_timing_20261024`，functions cell3236。与动态codec基线同器件、10ns、Default opt/place/route，额外保存placed.dcp以保留中间证据；不能把中间检查点当最终通过。终态先保存vivado_status为completion_receipt.json，再运行`audit_record_response_timing.py`。源/输入DCP哈希和配对基线审计哈希已冻结。当前未完成，不重复source。

实时全量输入绑定已通过`audit_record_response_inputs.py`：actual/pages哈希匹配冻结向量manifest，simulate参数相同（仅snapshot名称不同）。候选run all，基线run501s；两者使用相同TB的500s失败watchdog和正常finish条件。完整回放当前18查询/5checkpoint、runner3672723与watch3697205均live；这不是最终全量结果。终态后运行`compare_record_response_queries.py`生成38查询区间比较，禁止把checkpoint前flush区间误作单独checkpoint成本。

物理实现终态更新：`record_response_timing_20261024/final_audit.json`证据审计通过，418.309s/exit0，14759LUT/11171FF/319BRAM/3DSP，对动态基线+248LUT/+12FF。WNS0.943/WHS0.007/WPWS4.458ns，建立/保持/脉宽失败端点均0，布线错误0。WNS相对基线2.109下降1.166ns；最差路径仍目录owners BRAM至probes CE，不能归因于FIFO自身或外推Fmax。缺627输入847输出延迟及上游时钟模型，平台未闭合。方法学/DRC规则及数量与动态基线一致；详见物理目录METHODOLOGY_RESOLUTION_REPORT.md。MCP147904已idle，旧cell3236只返回过running交接、现终态以completion_receipt/final_audit为准，不再等待或重复source。

完整回放已独立核对24查询/8checkpoint的全部非时间收据前缀与基线一致，原runner3672723仍live，watch3697205继续。此前先导收益仍不作为全量结论。
