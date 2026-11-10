# 自然第三查询的G3 warm故障恢复（2026-10-27）

选定third_warm_full_v2与third_warm_pressure_v2，分别采用32缓存槽和单缓存槽，路径容量均3。全部生产RTL逐文件SHA等于上一轮正常三槽系统；本轮新增故障/恢复激励和观察，不新增生产RTL修复。

真实query180329旧路径先由原生ripup把990179/558358/265324 refs2/4/5降到1/3/4，形成三个journal键。搜索按CPU oracle完成后，第二个commit写558358的B返回SLVERR，第一写990179成功；实际工作owner refs2/4/4，query status7/detail5/committed0/acked1。G3/CP19只读authority两轮分别核对三个键，工作owner实际6次GET与1次INC，只有265324从4补到5，其他owner及另一net23916/ref1保留。

恢复使用实际G3 source5/3/5、floor180328、781标签、117字q1/q2加空第三槽、原始10字query。路径CRC f4394572、query CRC9493257c，标签CRC full742f5a50/pressure2f1c12da。原生label模块写入并回读781条，路径和查询均消费原字节及CRC；三种回执全齐、服务退休且成功回复消费后才放行。成功回复保持8周期期间owned持续、业务关闭、journal只在成功提交清零。恢复到6/0/6，仍保留floor180328，没有外部cold reset或工作DDR重装。

恢复后再次登记q3历史路径元数据并实际拆线，再执行同一query180329。故障前与重试两轮均逐项匹配CPU：114poll/113expand/565candidate/302cost。最终三路径位图7、CP19/journal3、floor180329；实际导出path117字CRC437e9a9a，query10字CRC03650e61。此最终三路径没有共同发布G4。

独立核对完整12路AXI、25个物理owner record写、最终146284032B owner与G3完整图像一致、781标签/393逻辑页及全部3MB物理页。失败前拆线、两次提交写、恢复INC和重试拆线/提交均来自真实引擎与物理日志。

| 行为仿真指标 | 32缓存槽 | 单缓存槽 |
|---|---:|---:|
| 结束周期 | 3760351 | 4010239 |
| owner恢复阶段 | 563 | 511 |
| 标签恢复阶段 | 373309 | 290752 |
| 故障至恢复放行 | 374291 | 291682 |

这些周期不是板卡时间或加速比。两例标签导出顺序不同；原生服务时间核对见third_warm_phases_20261027.json，尚未把剩余控制等待归因到具体模块。781条恢复伴随781次baseline读取、3905次恢复字段写和7810次底层字段写，是未来减少恢复期冗余初始化的候选动机，当前未做该优化。

开发v1的RO/RB/RL/RA/RC观察只保留slot最低位，slot2显示0且落入旧q1观察数组。v2只改TB两行，记录完整slot并限制旧数组范围。两版所有12AXI/最终镜像及事件周期一致，仅五类日志合计46处槽号观察不同；v1不是生产RTL反例，也不充当完整槽号证据。

两个v2归档实际恢复重审字节一致。原v1审计使用未排序目录遍历，解包后JSON键顺序变化导致字节重审失败，但解析内容/数据哈希一致；原归档和失败记录保留。独立排序审计产生两个legacy_stable对照包，明确记录原运行路径及manifest哈希，不冒充新仿真；这两包也实际恢复重审字节一致。全部凭据见同名JSON，源冻结236文件于third_warm_sources_20261027/manifest.json。

下一自然q4已独立CPU采集并验证最后owner释放，见iter2_fourth_20261027.json/.md；尚缺其独立cost/filter oracle、四路径槽/156字镜像验证、连续q4及G4发布/恢复。其他q3故障点、恢复取消、任意变价、持久化writer/认证/floor、全图baseline reseed、实际overflow新增回收、综合时序和板卡收益仍未完成。当前仍依赖外部可信初始G1 clones/full baseline，价格/history内容固定。
