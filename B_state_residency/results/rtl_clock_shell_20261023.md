# 显式时钟壳配对实现：完成，但模型与时序验收未通过

2026-10-23：原版/宽版已在同一Vivado 2022.2会话完成OOC布局布线，source正常退出0，四组原行为回归通过。两版都未满足声明的时序条件；此外，显式BUFG没有消除上游时钟与接口边界位置缺失警告，原模型完整性检查失败。**当前证据只通过完整性核验，不能称为时序或平台闭合。**

证据：[manifest](rtl_clock_shell_20261023/manifest.json)、[审计范围](rtl_clock_shell_20261023/completion_audit.json)、[原模型验收失败收据](rtl_clock_shell_20261023/failed_model_audit.json)。manifest SHA256：`0d8c4aea4a2283d65d16082540e13774033ce233c14480d000bdc188a114cab7`。

## 固定模型与结果

壳只增加一个BUFG，不增加数据寄存器或改变握手。10ns时钟；输入min0.5/max2ns、输出min−0.5/max2ns，参考`b_clock/O`。没有放宽预算、加入false/multicycle path或豁免。四组small/actual XSim的语义计数与结束时间均与父版本相同；这不是SDF仿真。[冻结契约](../hardware/CLOCK_SHELL_CONTRACT.md)。

| 布后结果 | 原版 | 宽codec版 |
|---|---:|---:|
| WNS ns | −1.158 | +1.575 |
| 建立失败端点 | 42 | 0 |
| TNS ns | −38.593 | 0 |
| WHS ns | −2.175 | −1.957 |
| 保持失败端点 | 4470 | 6290 |
| THS ns | −9197.858 | −8796.023 |
| WPWS ns | +4.458 | +4.458 |
| 完整路由net | 9566 | 9903 |
| 路由错误 | 0 | 0 |
| LUT / FF | 5300 / 5105 | 5682 / 5185 |
| BRAM tile | 20.5 | 22 |

两版均有一个位于`BUFGCE_X0Y0`的BUFGCE，输出`core_clk`状态ROUTED。check_timing的输入/输出延迟缺失、部分约束、无时钟和未约束内部端点均为0。原版保留TIMING-15 1000项和TIMING-16 32项，宽版保留TIMING-15 1000项；两版各保留RTSTAT-10一项。方法学条目数不等于失败端点总数。

| 路径组 | 原版setup/hold ns | 宽版setup/hold ns |
|---|---:|---:|
| 内部寄存器之间 | −1.158 / +0.010 | +1.575 / +0.011 |
| 输入到寄存器 | −0.628 / −2.175 | +2.071 / −1.957 |
| 寄存器到输出 | +3.828 / +0.905 | +4.200 / +0.781 |
| 输入直通输出 | +5.856 / +0.007 | +5.837 / +0.007 |

原版最差内部建立路径为busy寄存器到fence ACK队列RAM写使能，数据路径10.870ns；最差输入保持为cmd_value到value寄存器。宽版最差内部建立路径为目录state到owner BRAM使能，数据路径7.997ns；最差输入保持为rst到owner BRAM使能，后续为m_rdata到DMA buffer。两版最差保持问题均出现在输入边界，但原版还存在内部建立问题。

## 模型完整性失败不能被掩盖

完整日志中每版各有一条`Route 35-197`，明确指出clk缺少关联HD.CLK_SRC；两版合计1248条`Route 35-198`，指出接口缺少HD.PARTPIN_LOCS，无法建立对应部分路由。输入输出delay覆盖为0缺失，不意味着物理接口上下文完整。

原审计`report_clock_shell.py`在“Clock source still incomplete”处退出1，脚本和失败收据均保留。新增`report_clock_shell_with_limits.py`仅归档语义、哈希、路径分组、约束和路由证据，明确输出`original_model_gate_passed=false`、`clock_model_complete=false`、`interface_placement_complete=false`和`platform_timing_closed=false`。它没有将失败实验改判为原验收通过。

AMD的[UG905上下文约束说明（2022.1）](https://docs.amd.com/r/2022.1-English/ug905-vivado-hierarchical-design/Context-Constraints)区分外部时钟源位置与接口互连位置；本机2022.2运行警告直接确认这些缺失仍存在。2022.2同名网页本次未能读取，因此不把旧版文档当作本次工具返回的替代证据。

本研究预算参考BUFG输出边沿。真实上层发送端还包含自身时钟分布和数据路径，必须建立对应的物理上下文，不能随意填写位置或调整最小延迟以消除报告。当前负结果不直接证明板卡无法工作；正的内部裕量也不能换算成可靠Fmax或实卡加速。

## 下一步

需要真实平台时钟/接口上下文，或具有实际发送/接收寄存器与协议握手的集成研究壳，再评价内部控制路径和接口时序。保持本轮24个输入文件、DCP、日志和失败条件冻结。旧会话`vivado-20261023-131530-a3bc53bd`已闲置、工程已关闭；不要重复提交本次89分钟的配对脚本。
