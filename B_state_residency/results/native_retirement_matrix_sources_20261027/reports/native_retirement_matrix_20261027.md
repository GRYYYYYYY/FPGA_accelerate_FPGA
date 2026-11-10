# 同源八项行为矩阵通过

关闭/开启优化、取消重试、CRC重试各含32槽和单槽；CRC单槽复用已直接核对原参考的anchor，其余七例串行执行。每例27份输出及周期精确比较，共216项；八归档均实际恢复且审计字节一致。

| 实验 | 结束仿真时间 | 比较文件 |
|---|---:|---:|
| native_matrix_off_full_v1 | 45472300 ns | 27 |
| native_matrix_off_pressure_v1 | 47750020 ns | 27 |
| native_matrix_on_full_v1 | 44590330 ns | 27 |
| native_matrix_on_pressure_v1 | 46874800 ns | 27 |
| native_matrix_retry_cancel_full_v1 | 44914260 ns | 27 |
| native_matrix_retry_cancel_pressure_v1 | 47207980 ns | 27 |
| native_matrix_retry_crc_full_v1 | 46615310 ns | 27 |
| native_retirement_system_crc_pressure_v1 | 48288200 ns | 27 |

全部133份生产RTL逐文件匹配已验证开启版OOC。该OOC零组合环，但10ns下布局前WNS仍为-7.111ns，不代表物理时序或板卡验收。关闭版OOC结果另列，不能由本行为矩阵推断。

范围仍为固定价格/history、既有真实四查询与可信初始快照。任意重定价、持久化floor/认证、自然overflow分配回收、物理实现和板卡收益未由本矩阵证明。后续query native exclusion候选不在这八项结果内。
