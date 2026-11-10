# Warm取消后非冷复位重试通过（2026-10-26）

详见results/warm_retry_20261026.json与hardware/variants/warm_retry_v1/CONTRACT.md。基于warm_cancel_fixed_v2，隔离变体只改receipt join和顶层命令选择；失败回复消费、旧fence释放、新fence重获且实际服务/物理事务退休后才允许重新arm。HALT至新WAIT始终owned，普通业务持续关闭；真实新backend offer选择新recover字段并同沿锁存，避免再次送旧attempt。

35项门控单元检查通过。真实32槽与单槽两例均在G2共享六项修复、query9/10取消后，保留journal6/CP18；相同attempt5返回原生status1，新cookie的attempt6/query0/price6非冷复位重试成功，不重装工作DDR。原生REARM/target_reset后两轮G2读取再次核对全部六键，仅12次工作GET、无DEC、corrected0，journal只在最终成功清零。重新恢复328标签、78路径字、10query字，source4/2/4映射到6/0/6、sequence1；真实回执与最终成功回复消费后才放行。

q2 CPU数值oracle43poll/42expand/176candidate/122cost、最终标签、原生两路径拆线及共享2→1→0通过；独立审计全部8AXI与最终DDR。健康两容量回归共28文件及周期精确匹配shared-last基线。四归档实际恢复后重审audit字节一致，源冻结results/warm_retry_sources_20261026。以上为行为仿真正确性，不是板卡速度或加速比。

价格/history内容不变；仍为一个net两路径、capacity0。下一优先标签或AXI在途取消、已受理回复退休与重试，以及晚成功abort；通用多net/overflow、运行中快照、持久化认证与floor、任意变价有效性、综合时序和板卡仍未完成。研究继续，goal active。
