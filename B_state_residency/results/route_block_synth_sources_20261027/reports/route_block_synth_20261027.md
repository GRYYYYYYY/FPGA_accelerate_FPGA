# 路由门控修改后的完整综合复查

route_block_synth_v1在已审计五源combined参考上新增controller idle_fault和host adapter门控两源变化，累计七个生产文件。133 RTL、所有参数、U280器件、10ns时钟保持一致；只有实验根路径变化。原生完整CRC行为27文件/48288200ns匹配另见route_block_system_crc_20261027。

完整综合与独立重开DCP诊断结束。产物完整性审计passed；设计仍为rejected_combinational_loops，timing_qualified=false。check_timing报告5个组合环，原参考21；LUTLP-1区域LUT计数[29]。文本5条闭合pin walk，是否列出报告全部环为True。环数变化不是已修复独立故障数量。

LUT 139061、FF 88019、BRAM 163、DSP 23、URAM 0；零latch/blackbox。布局前WNS -9.34ns，参考-12.538ns。仍有自动环切断，不能把时序数值当有效频率或板卡收益；无IO时序/物理时钟位置/布局布线。

归档已实际恢复复审，audit逐字节一致；源、工具与报告冻结。当前路径涉及authority请求READY与恢复/发布故障反馈，及core capture/退休/fence反馈。下一候选recovery_backend_loops_v2仅对已证明READY与回复VALID互斥的原生query接线去掉不可能分支，通用参数默认关闭；九项原生组件测试通过但完整CRC仍需单独取得终态审计。该候选不在本次综合内，不能把本结果称下一候选的结构验证。

正常off/on双容量、cancel双容量及CRC full其余七项矩阵仍待最终候选验证。固定价格、可信初始快照、持久化floor/认证、自然overflow分配回收、物理实现和板卡缺口保持。
