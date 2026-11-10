# 原版与宽codec：冻结网表的配对实现

2026-10-23：两份默认容量状态端点网表完成相同的布局布线流程，终态审计通过。在原有10 ns时钟模型下，原版/宽版的建立裕量分别为 **+4.395/+4.280 ns**，保持裕量分别为 **+0.036/+0.016 ns**。宽版裕量略减，但本轮内部模型下均无建立、保持或脉宽违例。

因此，前轮19个真实小查询中 **21.56%的状态端点仿真周期减少**，在本轮内部时序模型下没有因必须降频而被抵消。这个结论不覆盖真实平台时钟、外部接口、完整搜索路由或实卡速度，也不是最高频率测量。

## 可复核证据

- [最终manifest](rtl_codec_timing_20261023/libc_batch/manifest.json)、[终态审计](rtl_codec_timing_20261023/libc_batch/completion_audit.json)、[进程退出记录](rtl_codec_timing_20261023/libc_batch/process_result.json)。独立Vivado进程退出0，两份检查点及完成标记齐全。
- [原版最终时序](rtl_codec_timing_20261023/libc_batch/baseline/timing_routed.rpt)、[宽版最终时序](rtl_codec_timing_20261023/libc_batch/wide/timing_routed.rpt)。每版另有20条内部建立/保持路径的TSV。
- [原版路由检查点](rtl_codec_timing_20261023/libc_batch/baseline/routed.dcp)、[宽版路由检查点](rtl_codec_timing_20261023/libc_batch/wide/routed.dcp)。
- [约束与方法学说明](rtl_codec_timing_20261023/libc_batch/METHODOLOGY_RESOLUTION_REPORT.md)、[环境兼容性诊断](rtl_codec_timing_20261023/probe/README.md)。
- 前轮语义、周期和综合结果：[宽codec实验](rtl_wide_codec_20261023.md)。

## 比较条件

Vivado 2022.2，`xcu280-fsvh2892-2L-e`，默认23405个后备frame，2线程。直接读取前轮冻结综合DCP，不重综合、不修改RTL。两版均执行 `opt_design`、`place_design -directive Default`、`route_design -directive Default`，各保留一次完整的确定性实现结果，没有进行多策略或多种子择优。

输入DCP的SHA256分别为：

- 原版：`cc8c1c53a21e175a5a048c42755716314b78f2a684e1df980c45c36c07addb27`。
- 宽版：`d25642dbe21a9afdf540d590ee44ab10525e33d9089a5a18aea9a58be3c6e870`。

审计核对DCP在前轮manifest中的登记、输入/输出哈希、退出码、完整完成标记、约束前后一致性、内部逐路径与汇总表一致性、可路由网络完成数及资源报告。`audit_status=passed`表示证据及提取一致，`platform_timing_closed=false`明确保留平台未收敛状态。

前轮真实查询仿真使用512-frame实例，峰值390页；本轮实现使用默认23405-frame实例。这里没有新增大查询RTL回放，也没有把两种容量混称为同一次硬件运行。

## 最终报告结果

| 指标 | 原版 | 宽版 |
|---|---:|---:|
| 时钟约束 | 10.000 ns | 10.000 ns |
| 建立裕量 WNS | +4.395 ns | +4.280 ns |
| 保持裕量 WHS | +0.036 ns | +0.016 ns |
| 脉宽裕量 WPWS | +4.458 ns | +4.458 ns |
| 建立/保持/脉宽失败端点 | 0 / 0 / 0 | 0 / 0 / 0 |
| 已完成/可路由网络 | 9608 / 9608 | 9948 / 9948 |
| 路由错误网络 | 0 | 0 |
| 实现后 LUT | 5249 | 5626 |
| 实现后寄存器 | 5105 | 5184 |
| BRAM tile | 20.5 | 22 |
| 锁存器 | 0 | 0 |

实现后宽版增加377 LUT、79个寄存器和1.5 BRAM tile。前轮综合增量383 LUT、80个寄存器属于另一阶段；物理优化及LUT合并后数值变化，不回改原综合结果。

两版最差建立路径均从后备服务的cookie寄存器到目录owner BRAM使能，原版数据路径5.238 ns，宽版5.352 ns；各有11级逻辑。最差路径不是codec的整记录RAM。原版最差保持路径在codec输出到DMA缓存，宽版在事务寄存器到请求队列RAM。宽版保持裕量仅16 ps，不能脱离实际时钟偏斜模型解释为板卡保持时序安全。

布局估计中宽版裕量曾高于原版，但最终布线后略低；结论采用最终 `report_timing_summary`，没有选择更有利的中间值。也没有用 `1000/(10-WNS)` 推算或宣称最高工作频率。

## 仍然缺少的时序条件

唯一显式时序约束来自 `hardware/rtl/scratch_frame_store.xdc` 第2行：

```tcl
create_clock -name core_clk -period 10.000 [get_ports clk]
```

两版均有624个输入端口缺少输入延迟、788个输出端口缺少输出延迟。方法学报告各列出1000条TIMING-18；这与check_timing端口计数分开记录，不能相互替代。`HD.CLK_SRC`未指定，Vivado明确警告无法估计OOC实际时钟延迟/偏斜；路径表中的时钟网络标记为 `unset`。没有实际平台时钟源/时钟树集成、端口负载或接口预算。

两版DRC各保留1条RTSTAT-10，涉及246条无可路由负载网络，包含公开响应及AXI输出。未加waiver、未禁用检查、未填写任意延迟值。可路由网络全部完成不等于整个模块边界已经验证。

## 两次失败与兼容性处理

优先复用B方案MCP会话执行。进程2552581在基线 `route_design` 完成路由后、写出最终报告前异常退出；随后独立原环境批处理进程2389338在同处退出134。两次没有终态检查点，作为失败证据保留，不纳入完整配对结果，也不把它们算作独立性能重复。

共同崩溃栈涉及libudev设备枚举、realloc、许可主机信息与WebTalk调用。查询确认WebTalk在用户及安装范围原本均已关闭，因此没有修改该配置。自建小型诊断程序链接Vivado自带tcmalloc、deep-bind真实libudev，可复现同类崩溃；只为子进程预加载系统libc后枚举成功。这支持内存分配兼容性假设，但没有直接证明Vivado内部加载标志及完整根因。

最终两版在同一个独立进程中，使用仅对子进程生效的 `LD_PRELOAD=/lib/x86_64-linux-gnu/libc.so.6` 完成实现。系统libc哈希、环境覆盖和退出码均记录。没有修改安装文件、全局配置、许可检查、设备身份或其他Vivado会话；正常取得并释放实现许可。基线布局校验值和路由器初报与失败尝试一致。

## 下一步

保留宽codec作为继续研究的候选。在扩大性能结论前，补充明确的上层时钟/接口测试壳并重新检查建立与保持路径；平台未确定时，只能明确标注研究测试壳的假设。随后优化目录的有界索引及剩余记录搬运，并推进19个大查询的有限ID/检查点回放。完整FPGA搜索路由与实卡测量仍待完成。

重做审计（不重新实现）：

```sh
python3 hardware/scripts/report_codec_timing.py results/rtl_codec_timing_20261023/libc_batch
```

实现脚本拒绝覆盖已有证据目录。复现实验应复制脚本并指定新的结果目录，保留相同输入DCP、约束与实现选项。
