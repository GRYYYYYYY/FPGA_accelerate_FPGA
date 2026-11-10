# 组合反馈诊断与隔离修复计划

当前为诊断阶段，尚无修复候选或通过结论。基线是restore_seed_synth_off_v1/on_v1的实际终态DCP，133 RTL源相同，唯一generic差异为ENABLE_RESTORE_SEED_BYPASS。不能拿旧warm关闭的cold综合作等价对照。

## 已确认

两版check_timing各报告20个组合环。两版独立重开DCP的LUTLP-1#1分别包含103/107个实际LUT，均从get_cells -of_objects提取并核对报告计数。check_timing仅列出9条闭合pin walk，不能把9条当全部20个环；关闭版列出18条。源仿真成功与硬件组合结构无环是不同要求。

源码候选反馈包括：

- recovery_coordinator.attempt_reset由retry_safe决定；label_restore的rst包含attempt_reset，busy又参与retry_safe。
- recovery_coordinator.unexpected依赖authority/owner ready，并传播到fault、权限、发布及服务ready。
- recursive_candidate_controller根请求的e_expand_valid使用上游expand_ready，后者直接依赖child_capture.expand_ready；frames的begin_ready、push、frame_done/pop及结果返回继续参与同一组合区域。

这些是源码依赖证据；不能按合并后的LUT名称直接断言全部根因，也不能认定删除一个门控就修复整个区域。

## 后续隔离实验

1. 从已冻结源复制新候选，保留原始反例根；先针对原生controller/capture/frames形成小型结构复现，同时核对根请求、递归、结果背压、abort和已受理回复退休的行为。
2. 分离offer与accept，或使用明确的寄存请求阶段打断ready返回；具体实现须根据保持/取消契约决定。不要通过降低时钟、增false-path或ALLOW_COMBINATORIAL_LOOPS掩盖环。
3. 独立处理REARM复位和retirement反馈，保留不安全时不得清除旧服务状态、journal和attempt floor的要求；需覆盖新unexpected回复、abort、retry_safe撤销以及J0重试。
4. 小型网表确认每项实际消环，再接完整层级。完整回归包含正常四查询、G4故障恢复、优化on/off、cancel/CRC失败与非冷重试、全部AXI/DDR/CPU数值审计。新增流水周期可变，数值、退休与提交顺序不可变。
5. 最终完整OOC必须检查所有残余环、latch/blackbox、runtime端口、资源与关键路径；无环后再评估路径流水/物理实现。10ns仅实验目标，当前没有顶层接口时序及物理时钟位置，不补造IO delays或HD.CLK_SRC。

## 范围

当前query root之外的baseline provider/snapshot writers不在本次OOC范围。未证明时序闭合或板卡收益。原有价格/history固定、外部初始快照、持久化认证/floor、自然overflow新增/回收等研究缺口继续保留。
