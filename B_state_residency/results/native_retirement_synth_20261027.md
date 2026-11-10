# 原生后端与capture退休合并版本的完整综合复查

native_retirement_synth_v1在已恢复route_block参考上增加backend四源与capture退休一源，累计相对原seed十个唯一生产文件。133 RTL、全部参数、U280器件、10ns时钟一致，未合成TB监视器。默认通用backend协议保留，实际query原生接口互斥特化；退休仍要求零depth与其余所有服务退休。

完整综合及独立重开DCP诊断结束。check_timing组合环0（参考5），LUTLP-1区域LUT计数[]；文本闭合walk 0，覆盖全部报告路径为True。这些是匹配综合网表的报告结果，不是任意配置无环或RTL形式证明。

LUT 139803、FF 88045、BRAM 163、DSP 23、URAM 0，零latch/blackbox。布局前WNS -7.111ns，参考-9.34ns。自动Synth8-326环切断警告出现0次；若非零则不能用相关slack证明有效时序。无IO延迟/物理时钟位置/布局布线，即使未报环也不是物理时序或板卡频率。design_acceptance=unresolved，timing_qualified=false；产物完整性audit passed不等于硬件验收。

归档已实际恢复并重审audit字节一致，源、工具、局部证明与报告冻结。完整CRC行为由独立native_retirement_system_crc报告提供；同源八项矩阵仍需逐例审计，不能从结构检查推导行为正确。其余固定价格/可信初始快照/持久化floor认证/自然overflow/物理实现和板卡缺口保留。
