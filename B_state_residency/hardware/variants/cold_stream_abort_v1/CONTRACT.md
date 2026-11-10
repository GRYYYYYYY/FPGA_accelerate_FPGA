# 原生恢复流部分导入取消

生产 query root 与 boot gate 逐字节继承已审核 cold_abort_fixed_v1；本轮只扩充完整系统测试，不修改生产RTL。

同一实例执行两次cold boot，DDR文件不重新装载。第一轮在path第39/78字（slot0整条已送达、slot1未送达）或query第5/10字中断。真实native取消回复须status2；path有效位仍0，query已发布sequence_seen/last_sequence仍0。保持错误回复8周期，业务与lease释放不得开放；消费取消回复后，以cold reset开始完整重试。

第二轮重新配置/重建328标签，原生导入path/query，拒绝旧seq1；seq2对照既有CPU oracle为43poll/42expand/176candidate/122cost，随后共享refs1→2及两次ripup2→1→0。32槽/单槽各两中断点，共四例。

实际QCS握手日志与bundle query.bin独立核对，必须是部分前缀后接完整10字，顺序、值、last逐项一致。全部8AXI和最终图像独立重放。标签两轮共656个完成记录。query发布状态为仿真中的被动观察，不是生产导出API；不以私有状态生成恢复回复。

另见cold_stream_late_v1的query第9/10字边界：这时序号下限也已实际送达，仍不能发布。本轮仍不覆盖AXI读/写事务在途取消、无复位恢复、任意快照、运行中authority轮换、板卡与性能；普通启动回归和新顶层综合也待完成。
