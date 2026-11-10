# 后续重点

777条路径的CRC失败/同attempt拒绝/更高attempt非冷重试已通过；不要继续重做822旧fixture。

1. 对实际777恢复过程做一个明确baseline AR/R在途取消与非冷重arm例，保证取消时reader/guard服务归属不丢失，真正R与native标签回复全部退休后才完成失败。已有SOURCE_CHECK取消不能替代此恢复阶段证明。
2. 然后推进G3 owner快照generation轮转与B错误后rearm，设计草案见[累计差分约束](../owner_cumulative_rearm_v1/PLAN.md)。这份草案尚无RTL/实验，不得写成通过。
3. 不可直接清tracking_fault/dirty_count。区分可恢复B数据错误与不可证明覆盖的错误；G3可先保留同一G1 baseline的累计dirty差分，正确绑定bank/generation/receipt。真正baseline重新建图/清脏仍需另外的已验证clone/reseed协议。
4. G3应接实际owner writer、781标签、两路径、query floor180328和三方发布/AP GET。没有新自然query CPU prepared-state前不得重复已消费seq180328冒充下一query。
5. 之后是实际overflow新增回收、更大路径/全局cache容量、变价有效性、持久化认证/floor与综合时序/板卡。当前FRAMES与路径槽数均有界。
