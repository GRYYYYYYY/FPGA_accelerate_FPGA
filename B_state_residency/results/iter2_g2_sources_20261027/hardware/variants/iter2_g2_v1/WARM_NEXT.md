# 下一步：本数据G2后的warm故障恢复

沿用iter2_warm_v1已审计的RESTORE_RECORDS三层参数接线，默认512、此例显式1024，snapshot_count822/末尾821。G2发布后、iter2_next_query命令前，在新query180328的第二次owner物理B写558358注入BRESP2（首写990179成功），工作图像产生两键journal，G2旧目标应为990179/net26422 refs1/occ2、558358/net26422 refs3/occ2；不能按G1空行ref0恢复。其他net占用不变。原生G2 authority两轮GET、真实DEC修正，非冷复位/不重装工作DDR。

恢复source为G2/CP18/storage3/1/3、query ledger floor180327/sequence_seen1（flags0x4d），path为仅slot0的三内部节点，CRC必须来自本轮原生导出。初次开发捕获path CRC1d36e333、query CRC79283e8e；成功选定例应重新核对原始字节/CRC，不能将数值手填替代原生导出。

G2源标签是q180327实际final并清理204279 target，不是q180328 prepared：源点仍visited180327，67922尚未置target。全部822条恢复+回读验证，path/query真实回执联合/服务退休、最终成功回复消费后才允许新attempt4/query2/price4重试sequence180328。保留slot0，slot1由重试真实prev链提交；最后ledger180328/storage4/2/4。价格/history内容保持不变。

预期工作owner记录写13：q1提交3+历史ripup3+q2故障2+修正2+重试3。两次q2搜索各114poll/113expand/564candidate/302cost，独立对原CPU oracle；第二搜索须恢复验证游标但不得重载DUT状态。最终完整owner图像应等于q1提交加q2重新提交，两路径共存，其他net/pool/allocator逐字节保留。此为下一待执行实验，并非当前已通过结论。
