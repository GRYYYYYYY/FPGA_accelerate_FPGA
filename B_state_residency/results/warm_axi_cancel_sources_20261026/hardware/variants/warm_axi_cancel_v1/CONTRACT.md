# 标签写入/校验阶段的AXI在途取消

基于已审计warm_retry_system_v2。生产RTL逐文件SHA保持一致；仅增加独立TB和AXI文件内存agent的response-generation延迟输入。没有force、DUT握手掩码、伪造完成或中途冷复位/工作DDR重装。

## 两个取消点

- R：328个标签写完、第一项读回校验未完成，真实ARVALID/ARREADY受理；agent延迟RVALID生成。保持abort及32周期待返回事务，检查全物理排空为false、label busy、warm owned/fault、恢复完成VALID为false、普通业务关闭。
- B：同样在至少32标签完成后，agent已受理AW和全部W（被动记录AW/W），延迟BVALID生成。取消期间保持相同隔离检查；之后放行真实内存写与B响应。

其余agent输入hold均为0，延迟不影响RNG推进。不能撤销已受理物理事务。取消后等待真实R最后一拍或B握手、原生标签status7消费、服务全部退休，才允许原生coordinator返回status6，journal6/CP18仍保留。

同实例随后拒绝attempt5，以新cookie的6/query0/price6重试。原生REARM/target_reset重新初始化服务；保留journal经G2两轮GET复核，corrected0，无额外DEC；重新写入和验证全部328标签，恢复q1路径与原始查询镜像，再执行完整q2 CPU oracle及两路径拆线。价格和history字节保持不变。

## 审计

run_warm_axi_cancel.py支持--hold-mode=0/1和--full-only/--pressure-only。每个运行冻结源、编译/展开/仿真命令和输入manifest。audit_warm_axi_cancel.py要求全部生产源等于审计基线，重建TB与内存agent，核对32个held周期、真实物理完成先于标签失败/恢复失败、B场景部分标签写入为原镜像前缀、R场景全部写完但verified仍0，真实校验响应被取消丢弃、重试完整镜像、8AXI/DDR重放、CPU数值oracle和共享引用2→1→0。

完整结论以results报告与各source_bound_audit.json为准；仿真PASS不能证明任意取消点、超时/永久不返回、协议违规从设备、CDC、综合时序或板卡性能。晚成功abort、运行中快照生成、持久化floor/认证、多net/overflow和任意价格变化的有效性仍需验证。
