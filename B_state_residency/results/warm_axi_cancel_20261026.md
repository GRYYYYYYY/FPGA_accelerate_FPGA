# 标签写入/校验阶段的AXI在途取消与非冷复位重试通过（2026-10-26）

详见results/warm_axi_cancel_20261026.json与hardware/variants/warm_axi_cancel_v1/CONTRACT.md。32槽、单槽各覆盖R与B两种取消点，共四例。R场景328标签已写完但第一项读回校验未完成，真实AR已受理但R未返回；B场景32槽/单槽分别写完53/36项，AW及完整W已受理但B未返回，此时触发abort；延迟agent真实响应32周期，期间物理drained为false、label busy、owned/fault持续、恢复完成VALID为false且业务封锁。没有DUT握手掩码或伪造回复。

放行后实际R最后一拍/B握手、原生标签status7回执消费、服务退休先于coordinator status6；journal6/CP18保留。相同attempt5被原生拒绝，再以新cookie的attempt6/query0/price6非冷复位重试；不重装工作DDR。原生G2两轮核对保留的六键，工作owner仅12次GET、无DEC、corrected0，全部328标签重新写入并验证，q1路径/原始query重建后成功放行。CPU oracle43poll/42expand/176candidate/122cost、最终标签、两路径拆线和共享2→1→0通过，独立重放全部8AXI与最终DDR。

本轮无新增生产RTL修复：全部生产源逐文件SHA等于已审计warm_retry_system_v2。仅改独立TB与AXI内存agent延迟接口，取消前前缀逐行/周期匹配既有基线。四例归档实际恢复后重审audit字节一致；源冻结results/warm_axi_cancel_sources_20261026。结论为行为仿真正确性，不是板卡速度或加速比。

仍是一个net两路径/capacity0、价格/history内容不变、两个确定在途取消点；不能声称覆盖任意取消、永久不返回、协议违规从设备或晚成功abort。下一优先晚成功abort与提交/回复消费边界，然后持久化floor/认证、运行中快照、多net/overflow、任意变价距离有效性、综合时序及板卡。研究继续，goal active。
