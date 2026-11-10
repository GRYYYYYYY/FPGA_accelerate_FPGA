# 下一阶段

优先去除初始822条CPU未来读闭包。先追踪实际record read/write miss，设计只读prepared-baseline provider，保留历史seq/prev/visited/浮点位模式；不能用零或无穷替代未知旧记录。评估记录级与页级填充对标签恢复容量1024及超时的影响，保持原CPU oracle。

其次为owner snapshot writer增加明确baseline/epoch轮转与错误后rearm，并验证实际overflow分配/回收。CRC失败后的同attempt拒绝和更高attempt非冷重试已通过，但不是任意取消、认证或断电恢复证明。
