# Query接口互斥候选同源OOC复查

query_native_synth_v1在已恢复native_retirement_synth_v1上仅覆盖query_lifecycle与root两源；133生产RTL与已通过完整CRC压力例逐文件一致，器件/参数/U280/10ns/Tcl保持匹配。没有合成TB监视器或新增IO约束。

check_timing组合环0，LUTLP-1区域LUT计数[]，自动切环警告0。候选布局前WNS -5.717ns，参考-7.111ns。存在环或自动切断时，slack不能证明时序有效性。

候选LUT 138850.0、FF 88263.0、BRAM 163.0、DSP 23.0；候选减参考的差值{'LUT': -953.0, 'FF': 218.0, 'BRAM': 0.0, 'DSP': 0.0, 'URAM': 0.0}。零latch/blackbox检查由独立审计提供。

产物审计、176文件归档实际恢复和audit字节一致通过。design_acceptance=unresolved，timing_qualified=false。未布局net估计、缺少真实IO/时钟位置及物理实现条件，不能换算成板卡频率或收益。新候选完整行为矩阵尚未执行，只有独立CRC压力例/原生12例证据。
