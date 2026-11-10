# 保留 journal 的显式恢复重试

这是隔离研究变体，不修改原始/其他方案基线。`build.py` 从已冻结的 `results/recovery_fault_matrix_v2/sources` 派生三个生产组件；`build_tb.py` 从该版本的真实二次故障测试台派生重试试验。旧122个RTL/dat中119个保持，修改 recovery_coordinator、config_restore_controller、residency_system。公共顶层端口不增加。

恢复错误返回后，调用方消费旧回复，再提供新的恢复命令。允许重试必须同时满足：协调器处于空闲、旧回复已消费、所有物理AXI排空、正常上下文退休、围栏回调计数归零、配置和标签服务空闲且无待消费回复、无围栏故障或意外authority/owner回复。永久后端停顿仍可以阻止退休，不可用reset掩盖在途事务。

恢复version必须严格大于最后一次接受的有效尝试，而不只是最后一次成功版本；query必须同时区别于当前成功上下文和上次尝试。checkpoint/design必须匹配已安装authority，price字段必须匹配version低四位。非法命令返回错误，保留journal和fault，不触发暂态清理或目标reset。这不是版本回绕协议，也不意味着不同price编号对应的实际价格数据可以随意复用。

有效重试先经过REARM一周期，产生内部attempt_reset，只清理已经退休的恢复服务暂态和错误锁存。协调器不冷复位，dirty journal和已安装authority身份保留；配置服务保留2304位descriptor、checkpoint/design以及成功配置的version。标签恢复FSM重新开始。之后仍执行原有DRAIN、目标域reset、六服务重配置、owner两遍核对修复、标签写入/刷回/读回核验流程。

每次owner修复重新GET物理引用计数，与authority比较后决定INC/DEC。写入已执行但B回复错误时不能根据确认数盲目反向操作。只有owner与标签全部成功、物理和逻辑退休完成、成功回复被消费，才放行业务。

snapshot来源仍是受信任的外部生产者。旧尝试终止且回复消费后，生产者废弃旧未接受流记录，下一次必须使用新stream cookie，从记录0完整重放；已接受的事务由硬件排空。试验以e0010001/e0020001分隔两次流，以c0010001/c0020001分隔恢复命令。硬件校验当前流cookie，但尚未提供通用全局cookie唯一性或任意旧流重放防护。本变体不是完整持久化checkpoint协议。

验证用例：业务第一次owner INC发生真实B SLVERR；恢复过程中分别在owner GET R、修复DEC B、标签eviction B、标签CHECKPOINT B、标签核验R注入第二次真实SLVERR；随后显式发起query3/version5恢复，再完整重跑q1。32槽和单槽分别验证。authority仍仅q1六个路径内部节点，标签仍328条已知记录，design backing保留。测试台使用真实AXI文件内存，不以force替代故障或修复。审计覆盖七条AXI日志，其中table在本数据路径闲置；不声称验证了table活动访问或未知标签页。

测试入口：

- `python3 hardware/variants/recovery_retry_v1/build.py`
- `python3 hardware/variants/recovery_retry_v1/build_units.py`
- `python3 hardware/variants/recovery_retry_v1/build_tb.py`
- `python3 scripts/run_recovery_retry_unit.py NEW_RESULT`
- `python3 scripts/run_config_retry_unit.py NEW_RESULT`
- `python3 scripts/audit_recovery_retry_unit.py RESULT`
- `python3 scripts/run_recovery_retry.py NEW_RESULT`，可选`--pilot`仅32槽或`--pressure-only`仅单槽。
- `python3 scripts/audit_recovery_retry.py RESULT`
- `python3 scripts/run_recovery_retry_normal.py NEW_RESULT INPUT_RESULT`
- `python3 scripts/audit_recovery_retry_normal.py RESULT`

结果必须以各目录source_bound_audit和总报告为准。单元通过不等于真实AXI通过；综合资源不是布线时序或板卡加速。尚缺完整checkpoint/未知页/任意reroute/真实价格变更/epoch回绕/容量与回收/耐掉电/板卡测量。没有自动重试次数、退避或故障分类策略。
