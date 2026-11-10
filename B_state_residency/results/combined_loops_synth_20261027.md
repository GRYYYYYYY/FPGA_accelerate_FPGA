# 五源合并的完整层级结构复查

combined_loops_synth_v1仅合并已审计capture两源与REARM三源；133 RTL列表、全部参数、U280器件、10ns实验clock与restore_seed_synth_on_v1相同。Tcl只改变实验根路径，XDC逐字节一致。运行终态后实际重新打开DCP，提取LUTLP-1、methodology、check_timing及对象/cells/nets/pins；没有waiver或人工false-path。

产物来源及完整性审计passed；设计分类为rejected_combinational_loops，timing_qualified=false。check_timing报告21个环，独立LUTLP-1反馈区域包含的LUT数为[100]。原参考分别为20个环与[107]。两类报告计数单位不同，不能相减解释为修复多少独立故障。当前文本列出5条闭合pin walk，是否覆盖报告全部环为False；未列出的路径不补造。

资源LUT 139647、FF 88310、BRAM 163、DSP 23、URAM 0；latch/blackbox均为0。布局前WNS -12.538ns，原参考-9.91ns。报告包含自动环切断时，slack不能作为有效时序证明；无顶层IO延迟、物理时钟位置或place/route，资源变化不等于板卡收益。

归档实际恢复并重新独立审计，audit逐字节一致，源、工具和报告另行冻结。五源合并的CRC pressure完整行为回归单独见results/combined_loops_system_crc_20261027.json/.md；27文件及48288200ns与参考一致，不能替代本结构检查。其余七项矩阵仍未完成。

下一依据实际闭合pin walk与RTL接线隔离残余反馈，优先核对route host block及authority/发布路径。results/route_block_identity_20261027.json仅证明实际adapter资格下的局部二态恒等式，没有修改生产RTL或宣称全系统消环。完整物理时序、板卡、固定价格之外的有效性、持久化floor/认证与自然overflow分配回收仍未证明。
