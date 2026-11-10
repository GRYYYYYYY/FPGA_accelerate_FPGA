# 更新：四组完整失败重试已通过

2026-10-27：四组终态、独立审计、归档实际恢复重审均通过，详见CONTRACT.md与results/restore_seed_retry_20261027.json。187文件已冻结；不得就地修改候选或已冻结审计器。后续转向restore_seed_synth_off/on_v1匹配OOC资源与布局前时序检查，当前正在运行。

以下保留此前启动记录。

# 开启优化后的完整失败与非冷重试测试（正在运行）

2026-10-27。生产8文件逐字节沿用restore_seed_bypass_v1；成功路径4例已审计、归档恢复和源冻结，见results/restore_seed_20261027.json。当前只改TB及运行器/审计器，不修改冻结的成功路径证据。

入口scripts/run_restore_seed_retry.py ROOT {full|pressure} {cancel|crc}。四根已存在且有真实运行进程，后续必须实时查询，不得依据旧running状态重启覆盖：

```
/tmp/B_state_residency_offer_20261025/restore_seed_retry_cancel_full_v1
/tmp/B_state_residency_offer_20261025/restore_seed_retry_crc_full_v1
/tmp/B_state_residency_offer_20261025/restore_seed_retry_cancel_pressure_v1
/tmp/B_state_residency_offer_20261025/restore_seed_retry_crc_pressure_v1
```

写入时四组都通过compile/elaborate，仿真仍在前置G2/G3阶段，未到新故障点。以下是断言目标，不是实验结果：

1. 原G4图R错误与三键owner修复沿用成功例。新试验只在随后label恢复出错。cancel在第一条记录第三字段实际native写受理后、回复前abort；预期3个写，written/verified0，原生label status7。crc只篡改最后记录payload bit0，预期780条/3900字段已写、无回读完成，status8。
2. 原生coordinator失败status6、journal3/CP20保持，实际服务退休后才发布，回复保持8周期仍业务封锁。无人为DUT握手/回复伪造。
3. 同attempt7用新cookie请求，被原生status1拒绝且不得重置或访问owner/labels；退休后新attempt8/query2/price8，重新start锁存许可并撤销外部引脚。
4. 新attempt两轮authority复核与6个工作GET，corrected0；从原始G4文件完整恢复781标签/156路径字/10query字。保持源6/0/6、floor180329，目标8/2/8；旧sequence拒绝后真实q4 CPU重试，最终query flags0x62。无外部冷复位/工作DDR重装。
5. 独立重放全部12AXI、原生标签内存与实际写回/重载、全部owner字节；最终物理DDR应与成功优化例一致。失败前缀截至FOURTH_WARM_OWNER须精确匹配成功例。

scripts/audit_restore_seed_retry.py及audit_restore_seed_retry_records.py已编写/语法检查，尚未用终态结果执行，不能当已通过证明。它们对原始日志进行扩展，不制造兼容日志。若失败，先区分TB断言/审计假设/生产RTL问题并保留原例，禁止降低关键正确性要求来凑通过。

通过后再归档、实际恢复重审、冻结源并释放已完成根的干净缓存。当前不声称覆盖任意取消、永久失联AXI、价格变化有效性、overflow生命周期、持久化认证/floor、资源/时序或板卡性能。goal active。
