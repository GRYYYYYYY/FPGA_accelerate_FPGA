# 优化后完整故障恢复与非冷重试通过

生产RTL与已审计seed bypass候选完全相同。32槽/单槽各验证第三字段native写回复在途取消、末条恢复记录CRC错误，共四例。

取消实际写3字段但无完整记录，原生label status7；CRC例写完780条/3900字段，末条拒绝、status8。两者verified0，coordinator等待服务退休后status6；journal3/CP20保留，失败回复保持及消费后仍封锁业务。旧attempt7原生拒绝，新attempt8/query2/price8非冷恢复。

真实G4 authority两轮复核、6个工作GET、corrected0；全部781标签写入/回读、156path和10query原字节/CRC、三回执及退休联合完成。旧sequence拒绝后q4重试83/82/402/231逐项CPU匹配。最终四路径、floor180330、query CRC626e163b与目标8/2/8符合预期。

全部12AXI、实际部分写及页写回/重载独立重放，最终146MB owner与3MB labels和优化成功例逐字节相同；其他net、满overflow池/allocator保留。两attempt共28个G4 authority读beat，包含allocator及foreign-owner overflow链；全程113beat。没有外部cold reset或工作DDR重装。

四归档实际恢复复审audit一致。新审计器的三个初始假设修正有原版本记录：原生重试需要REARM、cookie只在每attempt内不同、GET需读取allocator和完整overflow链。未改生产RTL或原始仿真结果。

下一步进行匹配参数的query root OOC资源对照，已有两组综合运行中；10ns仅实验约束，综合时序是布局前估计。当前不声称任意故障、任意变价有效性、持久化认证/floor或板卡收益。研究继续。
