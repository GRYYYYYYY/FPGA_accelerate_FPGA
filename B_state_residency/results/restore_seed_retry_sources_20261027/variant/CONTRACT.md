# 优化恢复写的取消／CRC失败与非冷重试

选定restore_seed_retry_v1。8份生产源与已审计restore_seed_bypass_v1逐字节相同；本轮只扩展TB、运行器和独立审计器。32槽/单槽各cancel、crc，共四个完整系统实验。

## 真实失败边界

此前G4图R错误及三键owner修复沿用成功路径，原始事件/周期截至FOURTH_WARM_OWNER精确一致。

- cancel：第一条恢复记录第三字段实际native写已受理、回复尚未返回时abort。实际3字段写，written0/verified0；回复退休后原生label status7，再coordinator status6。
- crc：只篡改源流最后记录bit0。前780条/3900字段已实际写入，末条在CRC检查拒绝，verified0、label status8、coordinator status6。前缀已产生的物理页写回也纳入独立重放。

两类均保留journal3/CP20，失败完成需真实服务退休，保持回复8周期仍owned/fault且业务关闭。无DUT握手掩码或伪造回复。旧attempt7使用新cookie，被原生status1拒绝；该间隔无target reset、authority/owner/label或查询副作用。

## 新attempt8实际恢复

失败回复与旧服务退休后，原生authority REARM保留G4 generation，随后target reset；没有外部cold reset或工作DDR重装。attempt8/query2/price8再次进行两轮authority检查与6个工作GET，corrected0；此前成功的3次INC保留，最终成功前journal仍3。重新start锁存恢复写许可，外部许可随即撤销，下游WW实际受理全部3905写。

原始G4源781条标签、156字path、10字query重新完整导入；全部781标签实际回读验证。source6/0/6、floor180329、path CRC f00b72b4、query CRC327d3916保持；目标8/2/8，三种实际回执及退休齐全、最终成功回复消费后才放行业务。旧sequence180329被拒绝，再按原历史路径元数据执行q4准备与查询重试，83poll/82expand/402candidate/231cost逐项CPU匹配。最终query flags62/floor180330/CRC626e163b，四路径CRC eec36b70，slots15/CP20/journal3。

## 独立证据

全部12AXI重放，原生记录模型包含7/1/7及8/2/8两个上下文和真实target reset；部分写、页写回/重载逐字节核对。最终146284032B owner、3MB labels及其余DDR与优化成功例完全一致，37个owner record写不变，其他net23916/ref1和满overflow池/allocator保留。

本轮G4两attempt共12次authority GET、28个读beat：每GET读取allocator及primary，558358还读取foreign-owner overflow record。读取地址按实际G4 primary/pool图像独立推导；加此前85beat共113beat。每attempt六个cookie不同，但跨attempt可能因原生XOR构造碰撞；检查每次cookie值和REARM前无未退休回复，不宣称跨attempt全局唯一。

初版新审计器错误继承“不得REARM”、假设12cookie全局唯一和固定2beat/GET；按源代码及原始日志修正为上述更精确约束。三个原版本和解释均保留results/restore_seed_retry_audit_development_sources_20261027与同名开发记录。这是审计假设修正，没有修改生产RTL、测试输入或原始仿真日志。

四例最终周期：cancel32槽4491426、cancel单槽4720798、crc32槽4661531、crc单槽4828820。它们包含故障/拒绝/重试及导出，不能当正常恢复速度或板卡时间。四归档实际恢复重审audit字节一致，源冻结见results/restore_seed_retry_20261027.json。

仍仅两个确定失败点。没有任意AXI中断/永久失联、任意变价有效性、持久化认证/floor、自然overflow新增回收或板卡收益证明。价格/history内容不变，初始G1 clones/full baseline与历史路径元数据仍为外部可信输入。综合资源对照另在restore_seed_synth_off/on_v1运行，不属于本行为验证结论。
