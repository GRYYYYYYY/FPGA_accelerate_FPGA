# 启动完成被 abort 中断

继承 cold_boot_v1 的完整描述、实际回执与 native 恢复协议，仅将 gate 的 work_rst 从 `rst` 接到 `rst||abort`。cold_boot_v1 保留为已审核历史基线，不能用它声称 abort 安全。

当恢复完成但回复仍被保持时，abort 立即屏蔽回复，下一时钟取消全部 bootstrap 资格并回到等待描述。业务保持封锁。此修复不强制清除 checkpoint lease，也不重置可能仍有事务的后端；本用例从显式 cold reset 重新启动恢复，而不是宣称无需复位的恢复。

完整系统反例使用旧连接，在实际 config8、label328、path/query 成功导入后，abort 与 boot_rsp_ready 同拍，旧版仍输出成功回复。同一 stimulus 在新连接下屏蔽成功，8周期保持业务/lease释放封锁；随后同一实例 cold reset，不重新装载外部DDR文件，重新恢复并完成旧seq拒绝、CPU q2对比和两次ripup。

中断点已完全退休，因此本用例不证明 AXI/导入流中途取消、突然断电、运行中authority轮换、任意多net/overflow快照或板卡性能。新顶层仍需普通启动回归和综合/时序检查。
