# 恢复期间真实 AXI 二次故障验证（2026-10-25）

10/10 故障处理契约通过：每次先注入真实业务owner B错误，再在恢复owner/标签流程注入一次真实SLVERR。系统返回恢复失败、保留journal、保持业务关闭。**这些结果不表示二次故障后恢复成功或自动重试成功。**

生产RTL和文件内存代理全部继承上轮v6冻结版本，共122个RTL/dat源哈希不变；本轮只新增激励和独立审计，没有重新综合。之前v6 OOC资源不能解释成板卡性能。

## 实验与独立证据

每种故障分别测试32槽与单槽：owner GET R、owner DEC B、标签写入eviction B、标签CHECKPOINT B、标签读回核验R。错误来自实际AXI memory-agent公开注入端口，保留实际地址/数据/背压行为，没有force内部完成。

每例前置真实搜索的73 POLL/72 expand/271候选/171 cost均与CPU精确对应；首次owner B错误已经产生物理写入，确认ACK仍为0。独立审计回放七类AXI所有字节（六类活跃、table闲置），比较完整owner/design/label图像、实际错误次数、所有恢复回调请求/回复一一退休以及snapshot流/逐字段写/核验读的合法前缀。返回written/verified计数也由成功原生回复独立重算。

| 用例 | 错误状态 | 确认修复数 | snapshot写完 / 核验数 | 第二次AXI错误至错误完成周期 |
|---|---:|---:|---:|---:|
| full_1 (owner GET R) | 3 | 0 | 0 / 0 | 4 |
| full_2 (owner修复DEC B) | 3 | 0 | 0 / 0 | 4 |
| full_3 (标签写入 eviction B) | 6 | 1 | 53 / 0 | 6 |
| full_4 (标签CHECKPOINT B) | 6 | 1 | 328 / 0 | 6 |
| full_5 (标签核验 R) | 6 | 1 | 328 / 0 | 22 |
| pressure_1 (owner GET R) | 3 | 0 | 0 / 0 | 4 |
| pressure_2 (owner修复DEC B) | 3 | 0 | 0 / 0 | 4 |
| pressure_3 (标签写入 eviction B) | 6 | 1 | 1 / 0 | 6 |
| pressure_4 (标签CHECKPOINT B) | 6 | 1 | 328 / 0 | 6 |
| pressure_5 (标签核验 R) | 6 | 1 | 328 / 0 | 31 |

这些周期是故障回复延迟（4–31），不是吞吐或加速比。模拟仍使用正常的实际AXI排空/事务退休条件。

## 关键语义

- 恢复GET失败时保留原来那项物理脏owner；恢复DEC B失败时内存已经回到初始owner，确认修复数仍为0。两者都保留journal=1，不依赖成功ACK数决定是否需要外部修复保证。
- 标签阶段故障前owner已确认修复1项，但部分标签或核验失败不允许恢复成功、不清journal。所有运行只有一次target_reset，没有用再次复位伪造成功。
- 错误回复保持9周期时全部业务入口关闭；消费后再提出恢复请求，32周期内仍无恢复接受、业务接受或额外reset。围栏处于RECSEND(8)保持未接受请求，协调器sticky fault使ready为0；不是误把恢复阶段号当完成状态。
- 初版验证代码的声明顺序编译失败保存在 `recovery_fault_development_20261025/`；审计器根据实际冻结RTL核实RECOVERY=9及上述未接受RECSEND语义后修正预期，没有改生产RTL或放宽业务/排空断言。

结果归档实际解压后重跑独立审计，623文件验证通过、audit逐字节一致。源闭包9文件位于 `recovery_fault_sources_20261025/`，原v6基线档案仍是依赖。入口 `scripts/run_recovery_fault.py NEW_RESULT`、`scripts/audit_recovery_fault.py RESULT`；详细契约见 `hardware/variants/recovery_fault_v1/CONTRACT.md`。

## 剩余研究

仍只有q1六owner行authority和328条已知初始标签受信任，design backing保留；不是完整warm/frontier/path/created-cache checkpoint。恢复失败后自动重试尚未实现，cold reset会丢失寄存器journal，必须先有外部权威恢复保证。源码绑定缺口分析见 `recovery_restart_gap_20261025.json`。下一步优先完整checkpoint覆盖及保留journal的恢复重启协议。未知页、任意reroute、真实价格变化、epoch/sequence回绕、容量/耐掉电与板卡仍未完成，研究目标保持active。
