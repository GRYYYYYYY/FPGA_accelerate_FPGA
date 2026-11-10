# 启动完成被abort中断：反例与修复（2026-10-26）

旧版 cold_boot_v1 仅以 rst 取消门控。完整系统在 G2/checkpoint18、八配置回执、328标签核验和原生path/query导入完成后，保持boot成功回复；abort与消费请求同拍时，旧版仍输出成功。cold_abort_unfixed_v1保留预期失败，不算成功恢复。

cold_abort_v1唯一生产差异是gate work_rst(rst||abort)。相同stimulus下成功回复立即屏蔽，恢复资格取消，8周期业务和lease释放保持关闭。lease不强制撤销。之后在同一RTL实例显式cold reset，外部DDR文件不重新装载，重新配置、重建328标签并导入path/query，再验证旧seq1拒绝、seq2 CPU oracle和双ripup。32槽/单槽均通过；全部8AXI字节重放、最终owner图像和42owner probes通过。第二轮查询仍43poll/42expand/176candidate/122cost，共享263946/554512 refs1→2→1→0。

两归档实际恢复并重审audit字节一致。当前源冻结results/cold_abort_sources_20261026。原cold_boot_v1及其历史归档保持，用于反例比较；后续实验应采用cold_abort_v1连接。

中断点已完全退休，本轮不证明AXI/导入流中途取消或无复位恢复。普通启动回归、新顶层综合/时序、运行中authority轮换、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电和板卡仍缺。周期包含两轮恢复、查询、探针和撤销，不作加速比较；goal active。
