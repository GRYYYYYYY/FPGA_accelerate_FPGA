# 无组合环之后的最差setup路径

本分析只导航已归档实际恢复的native_retirement_synth_v1布局前报告，不修改RTL或约束。独立DCP check_timing/LUTLP-1零环，10ns下WNS仍-7.111ns。

最差路径从标签目录lease_phase_reg[27][1]到顶层query controller error_code_reg[0]/CE，共71个LUT级、72条数据net。数据延迟17.007ns，其中逻辑2.976ns，未布局net估计14.031ns；不能将该估计转换为实际板卡频率或布线结论。

路径跨目录/pager、label引擎、coordinate/dispatch/access、graph仲裁、expansion/child capture、事务fence/AXI drain watch、label restore/warm join、recovery/route/search及顶层query控制。按逻辑所在层次计，pager与recovery各8级、顶层controller6级、route controller5级；这些是综合网表的导航分组，不能据此直接断言RTL根因。

最高数据扇出为label_restore/SR[0]的653，报告估计延迟0.313ns；其次route controller stopped_reg_1扇出107/0.272ns。单个最高扇出net并不占据全部14.031ns，后续应核对跨层fault/ready/退休链的状态资格及多个串联判断，而不是仅凭扇出排名选择修改。

当前十源候选已通过完整CRC精确回归，剩余七项串行矩阵正在执行；保持这份基线冻结。后续时序候选应独立建变体，从报告实际pin/cell映射回RTL，先验证状态限定的布尔约简。若确需增加寄存级，应明确新增延迟和允许受理/错误退休边界，建立相应独立时序预期并复验数值/AXI/故障恢复，不能改写已有精确回归审计。任何物理时序结论还须有明确实现边界与真实约束及布局布线证据。
