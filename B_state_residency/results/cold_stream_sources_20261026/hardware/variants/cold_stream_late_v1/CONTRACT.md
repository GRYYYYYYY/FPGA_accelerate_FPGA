# 查询图像末字之前取消

继承cold_stream_abort_v1，仅把第一轮query导入取消点从5/10移到9/10字，单槽/32槽各一例；生产RTL完全不变。

实际9个S流握手包括有效标志、active上下文及last_sequence=1，但第10字/last尚未送达。中断前后被动观察已发布sequence_seen/last_sequence均0，真实取消回复status2；门控和lease释放保持封锁。消费取消回复后同一实例cold reset，不重装外部DDR，完整重新恢复；旧序号拒绝、CPU q2对照、共享引用及双ripup全部再验证。

独立审计要求QCS精确为bundle的9字前缀（无last）与第二轮完整10字（仅最后一字last）；并重放8AXI和最终owner图像。本用例不是生产序号导出API或AXI在途中断证明。
