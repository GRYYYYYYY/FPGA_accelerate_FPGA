# Query候选最差路径对照

新候选最差setup从inner/backend/dut/core/p/endpoint/memory/memory_service/directory/lease_phase_reg[27][1]/C到controller/cp_crc_reg[0]/CE，64级LUT、65条未布局数据net。数据延迟15.613ns，其中逻辑2.737ns、未布局net估计12.876ns；10ns下WNS -5.717ns。

旧最差终点是controller/error_code_reg[0]/CE，新最差终点已转为controller/cp_crc_reg[0]/CE；起点仍为目录lease_phase_reg[27][1]。两份设计各自最差路径的级数由71变64、WNS改善1.394ns，不能把它当作相同端点路径的延迟证明。逻辑延迟差-0.239ns、估计net差-1.155ns；这些均为布局前估计。

当前瓶颈已涉及checkpoint CRC更新使能。后续应映射实际新路径回CP流受理/许可/漂移与退休控制，重新证明任何状态限定约简；不要重复修改已消除的旧unexpected READY分支。若需寄存级，须明确新增接口延迟和取消/错误退休合同，并独立验证，不能改写已冻结的精确周期审计。

候选综合网表已独立检查零组合环且归档实际恢复。尚未满足10ns，无真实IO/时钟位置/布局布线或板卡频率结论；新候选完整行为矩阵仍在运行。
