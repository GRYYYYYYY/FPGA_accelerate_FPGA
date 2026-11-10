# 部分路径/query导入取消通过（2026-10-26）

生产RTL与cold_abort_fixed_v1逐字节相同，本轮扩充完整系统覆盖：path在39/78字中断、query在5/10与9/10字中断，32槽/单槽共六例。path第一slot整条已送达仍不发布；query在第9字已送达last_sequence=1时，已发布sequence_seen/last_sequence仍0。真实取消回复status2；保持错误回复8周期期间业务与lease释放均关闭。

query实际S握手与bundle独立核对：部分5/9字前缀后，在同一实例cold reset、不重装外部DDR文件，完整10字重新导入，逐字值/次序/last一致。路径/query状态的被动观察不生成任何恢复回复；不是生产导出API。

每例第二轮328标签重建/核验、路径与query完整导入通过；旧seq1拒绝，seq2独立CPU oracle43poll/42expand/176candidate/122cost，42owner probes及共享refs1→2→1→0通过。全部8AXI逐字节重放与最终可写图像/owner一致。两归档实际恢复重审，audit字节一致，当前源冻结results/cold_stream_sources_20261026。

这是capacity0/同网双路径fixture的部分导入取消与cold-reset重试，不是无复位恢复或AXI在途中断。普通启动回归、新顶层综合/时序、运行中authority轮换、通用多net/overflow快照、持久化下限/认证、未知页/价格/回绕/容量/断电和板卡仍缺。周期包含两轮恢复/查询/探针/撤销，不解释为加速。goal active。
