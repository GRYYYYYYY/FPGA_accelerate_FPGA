# 后续非冷复位重试接线要求（待实现）

当前query取消后：真实错误回复已退休、coordinator失败回复已消费、journal6保留、G2/CP18未改变；join仍HALT/owned，普通业务继续关闭。不能把本轮的失败返回当作已经允许重试。

1. join记录实际失败完成消费，以及旧recovery fence随后退出拥有权；不能仅按host offer清fault。只有所有服务/回复/物理事务退休，且新fence重新取得拥有权，才允许同一D/G/CP的更高attempt再arm。保持owned连续，不短暂开放业务。
2. 原生coordinator的attempt floor已记住5，即使current context尚未成功提交；重试应使用6/query0/price6。原始快照query仍为4/2/4。严格验证版本/epoch，保留source seq1；重试相同5必须拒绝。
3. 当前root在wm_owned时总选择旧锁存recover_*（5/3/5）。若只放开HALT arm_ready，新命令会再次送成旧5。需要在真实新backend offer/受理窗口选择新字段，同沿锁存并arm；不可通过清wm_owned或伪造pc_owned来换字段。前端recover_ready本身就是backend受理信号。
4. 新attempt由原生REARM/attempt_reset及target_reset清旧服务错误，再配置6并执行G2原生两轮GET。此前owner已被第一次恢复修复，六项journal仍保留，因此重做应是只读验证、corrected0；不能清journal绕过检查。随后重建标签/路径/query，全回执与最终回复消费后才放行。
5. 使用新cookie区分两次恢复，禁止旧完成被当作新完成；全程不冷复位、不重装外部DDR。成功后继续CPU数值oracle的q2与共享引用拆线。价格内容不变是当前fixture前提，不推广到实际价格变化。

还需单独覆盖label/AXI在途abort和晚成功abort：不能假设本地query9/10取消已覆盖这些边界。
