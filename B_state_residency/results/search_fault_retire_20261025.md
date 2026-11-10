# 搜索错误事务退休与恢复（2026-10-25）

采用隔离 `hardware/variants/search_fault_retire_v1` 的 v6 冻结版本。原始11例真实AXI故障现在全部恢复并完成CPU一致重跑；新增深层图/cost故障6例也全部通过。这里是RTL行为仿真结果，不是板卡加速数据。

## 修复及反例

十个生产RTL组件由冻结基线确定性生成，另112个生产RTL/dat不变。修复capture错误帧无法完成、候选失败仍等待未启动下游、coordinate错误提前回复遗留graph请求，以及连接元数据取消后父完成仍要求有效元数据的死等。请求/回复已经暴露的VALID与载荷保持到握手；children HLS实际退休、内部仲裁与回复排空纳入core退休条件。继续使用已验证的route故障锁存退休谓词。

目录memory lease在错误后有意保留到协调恢复，不等于在途事务；不能把它归零当作恢复前提。v5过严检查造成标签错误卡住，已保留并纠正。v2早期pressure graph卡住、v2深层coordinate遗留回复、v3声明顺序编译失败均保存在 `search_fault_retire_development_20261025/`。这些是开发失败证据，不计作通过。

## 验证

- 基础故障矩阵11/11：source label R、单槽prepare B、graph R、cost R、owner B和cleanup B，两种容量。错误来自真实AXI memory-agent的SLVERR。
- 深层6/6：graph响应序号24/100、cost序号10，各32槽/单槽。coordinate读错误不再提前完成。
- capture独立单元：正常嵌套回放及9个错误/取消/溢出/身份/背压场景。
- 每个恢复用例独立回放七路AXI、检查修复后的完整owner等于初始值，再核对完整重跑73POLL/72expand/271候选/171cost与CPU相符。owner错误物理写1项但native ACK=0；cleanup错误修复6项；最终owner精确一次提交。
- 正常双查询/两次ripup审计通过，周期 657222 / 724963。两容量共24文件（完整cycle轨迹、七AXI、四内存图像）与旧正常基线逐字节一致；同net共享refs/occupancy语义不变。

| 用例 | 观测 |
|---|---|
| full_1 | recovered_retry cycles=575323 repairs=0 |
| full_3 | recovered_retry cycles=575323 repairs=0 |
| full_4 | recovered_retry cycles=576101 repairs=0 |
| full_5 | recovered_retry cycles=835704 repairs=1 |
| full_6 | recovered_retry cycles=836352 repairs=6 |
| pressure_1 | recovered_retry cycles=571591 repairs=0 |
| pressure_2 | recovered_retry cycles=571591 repairs=0 |
| pressure_3 | recovered_retry cycles=571591 repairs=0 |
| pressure_4 | recovered_retry cycles=573745 repairs=0 |
| pressure_5 | recovered_retry cycles=892858 repairs=1 |
| pressure_6 | recovered_retry cycles=893718 repairs=6 |
| full_3_after24 | recovered_retry cycles=575323 repairs=0 |
| full_3_after100 | recovered_retry cycles=580833 repairs=0 |
| full_4_after10 | recovered_retry cycles=577783 repairs=0 |
| pressure_3_after24 | recovered_retry cycles=572665 repairs=0 |
| pressure_3_after100 | recovered_retry cycles=579742 repairs=0 |
| pressure_4_after10 | recovered_retry cycles=576814 repairs=0 |

## 综合与复现

完整U280 OOC：88652 LUT、63485 FF、160.5 BRAM、23 DSP；零latch/blackbox/file-agent。公开接口位数56927，原逻辑端口358。比正常旧版本增加1772 LUT（约2.04%）与685 FF，BRAM/DSP不变；这是错误恢复支持的资源代价。原生Vivado2022.2 Tcl，观察超时后沿用原进程直到完成。v4综合仅作为开发记录；此处资源来自v6最终源。没有时序约束/place-route/Fmax/板卡结论。

五份通过结果均归档、实际解压、再次独立审计，审计文件逐字节一致，共1841个文件；收据见JSON。源闭包冻结33个文件，原参考源码未改。正常基线归档仍为依赖。

入口与语义见 `hardware/variants/search_fault_retire_v1/CONTRACT.md`。主要入口：`run_query_fault.py NEW_RESULT --search-fix`、加`--deep`运行深层矩阵；`run_search_retire_join.py NEW_RESULT results/natural_query_inputs_v1`运行正常回归。

## 限制及下一步

恢复仍依赖可信初始328标签和q1六个owner行authority，design backing保留；未建立完整warm/frontier/path/created-cache checkpoint。epoch/price身份变化不代表真实价格变化。未知页、任意reroute、恢复阶段再故障、回绕、容量耗尽与耐掉电/板卡仍未覆盖。下一步优先完整checkpoint覆盖与恢复期故障，研究目标保持进行中。
