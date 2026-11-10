# 修复后同源关闭/开启旁路OOC对照

关闭版native_retirement_synth_off_v1与已实际恢复的开启版native_retirement_synth_v1使用完全相同133份生产RTL。唯一参数差异为ENABLE_RESTORE_SEED_BYPASS从1变0，其余参数、U280器件、10ns时钟和Tcl命令保持匹配；除实验路径与这一项generic外脚本逐字节一致。没有沿用旧含组合环版本的资源差值。

关闭版check_timing组合环0，LUTLP-1区域LUT计数[]，开启版组合环0。关闭版自动环切断警告0次；若出现环或自动切断，不把相关slack解释为有效时序。零latch/blackbox。

关闭版LUT 138959、FF 88051、BRAM 163、DSP 23、URAM 0；开启版LUT 139803、FF 88045、BRAM 163、DSP 23。JSON的utilization_delta_off_minus_on为关闭减开启，不混用差值方向。布局前WNS关闭-6.539ns/开启-7.111ns。

两者没有IO延迟/物理时钟位置/布局布线证据，不能把资源与估计slack直接转换成板卡收益或闭合频率。关闭版design_acceptance=unresolved、timing_qualified=false。产物审计与归档实际恢复通过，audit字节一致，相关源和工具冻结；八项行为矩阵另行审计，不由本资源对照代替。
