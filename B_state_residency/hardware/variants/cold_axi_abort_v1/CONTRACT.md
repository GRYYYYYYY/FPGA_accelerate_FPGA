# AXI在途时取消启动，保留旧回复退休通路

从cold_abort_v1派生。新增16bit host_reply_owned：实际前端request handshake置位，实际前端response handshake清位，rst/cold reset清位，abort不清位。原host_mask仅控制新请求；host_response_mask=host_mask|host_reply_owned用于回复valid/ready。保持原始回复payload/status，不伪造取消回复，不强制撤销已接受事务。

旧连接的完整系统反例：label AR已接受而R尚未发出时abort，物理R随后排空，旧host回复通路随启动管理门控一起关闭。8192周期后f_phase=2、f_all_drained=1、f_normal_retired=0、f_backend_idle=0，前端无法退休。旧失败保留为cold_axi_unfixed_v1。

修复后的32槽/单槽各两例：
- 真实label AR handshake后、RVALID前触发abort；先前请求仍完成，返回成功、present和5个label字段逐字与bundle首个逻辑记录相同。
- 真实最后W beat handshake后、BVALID前触发abort；确认已有AW而B未退休。底层继续完成该已接受flush，所有AW/B计数最终相等，原control成功回复退休。

每例旧回复背压8周期时保持valid/payload，全部新请求ready为0、boot成功回复无效。只有f_all_drained、f_normal_retired、f_backend_idle且authority空闲后才允许测试驱动cold reset；不重装外部DDR，完整重建328标签并恢复path/query，再验证旧seq1拒绝、CPU q2（43poll/42expand/176candidate/122cost）、42owner probes和共享refs1→2→1→0。

独立审计核对AXI日志前缀：读cut有尚未收到的R beat，退休时前缀AR长度总和等于已接收R beat；写cut AW=B+1、退休时AW=B。全程八路AXI与最终可写图像重放，native回复成功且读数据与bundle一致。已有事务完成不等于本次boot成功；boot仍需cold reset重新恢复。

本轮不是AXI协议层撤销/回滚，不允许带在途事务直接reset；不是无复位恢复、任意快照或板卡证明。尚需普通启动完整回归和新顶层综合/时序，以及运行中authority换代、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡研究。
