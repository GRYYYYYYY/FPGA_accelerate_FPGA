# AGRAPH01 邻接译码硬件

顶层 `graph_expand` 接收完整 AGRAPH01 二进制镜像、经主机验证的 32 字配置表、规范节点请求数组；输出每请求的 `[start, degree, status]` 和固定宽度边记录 `[source, destination, tile, pip, up_wire, down_wire, attributes, direction]`。字符串、属性、别名与审计表全部保留在输入镜像中，没有把完整邻接预先展开后再交给硬件。

同一核的 mode=0 执行 CSR，mode=1 执行模板、连接例外、属性补丁与显式回退。动态占用仍由公共路由器按规范节点维护，本核只是邻接提供器。当前为功能参考实现，尚未流水化为高吞吐架构。

## 主机契约

- 镜像最多 8 MiB，一批最多 65,536 请求，输出最多 1,048,576 个 uint32。每个邻接行最多 1,024 条边，超过时明确返回容量错误。
- 主机必须先验证镜像目录边界、规范引用、完整属性、GRID/ALIAS 排序、例外索引排序和配置偏移。`prepare_fixtures.py::descriptor` 实现此检查。它生成参数与测试真值，生产输入只需要参数，不传真值或展开邻接。
- status=0 成功，1 未导出邻接，2 邻接度数或输出容量不足，3 规范映射错误，4 节点/配置错误。已知零度 sink 与未知行不同。失败请求不输出部分邻接。
- 请求总数/输出容量违反全局接口界限时，仅返回失败计数，不写 per-request 结果。主机必须拒绝这种提交。
- 输出中的整数属性 ID 指向原镜像完整属性表；两种图表示的属性池不同，跨表示比较须按语义解析，不能直接比较 ID。

## 2022.2 流程

使用 Ross `hls-synthesizable`、`hls-pragma-scope` 和 `hls-run-flow` 的检查顺序。当前安装没有新版 `vitis-run`，也没有 HLS MCP/Unified IDE 工具，使用 Vitis HLS 2022.2 的 classic Tcl。

```bash
python3 hardware/hls/prepare_fixtures.py --output data/derived/hls_fixtures_NEW
env LD_PRELOAD=/lib/x86_64-linux-gnu/libudev.so.1 \
  A_HLS_PROJECT=build/hls_graph_expand_NEW \
  A_HLS_FIXTURES=data/derived/hls_fixtures_NEW A_HLS_STAGE=synth \
  /inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls -f hardware/hls/run.tcl
```

综合成功后将同一命令的 `A_HLS_STAGE` 改为 `cosim`；默认使用 `rtl.txt`。设 `A_HLS_COSIM_MANIFEST=matched.txt` 可在各表示间使用完全相同的规范请求，避免不同工作量的延迟比较。通过联合仿真后，再设 `A_HLS_STAGE=impl`。不要在已有完成的项目上重跑同一阶段并覆盖证据，应新建项目目录。

第一版实验使用审计过的 VU13P 图数据作为通用译码器输入，目标器件为 U280；不是把两种器件图混在一起。全量 C 仿真检验所有采样节点，RTL 用有记录的功能分层子集。当前主机没有 XRT 可见板卡；RTL AXI 存储器模型的周期数不能当成 DDR/HBM 实卡性能。

`build/hls_graph_expand_20261022_v2` 已通过 C 仿真、综合、6 批 RTL 联合仿真，布局布线已完成。综合估计 36,570 LUT、19,830 FF、16 BRAM18K、0 DSP；5 ns 目标，估计关键路径 3.650 ns。多个自动流水线的 II 未达工具尝试值，顶层动态循环延迟未静态界定。上述均不是布局布线后时序或硬件加速结论。

`data/derived/hls_fixtures_20261022_v2` 另加入早期独立留出区的真实并行 PIP，用于 v3 扩展验证；不同数据集的结果分别记录。最终报告须同时列出测试请求、输入哈希、周期数、后布局资源和真实平台限制。

最终阶段报告为 `results/hls_check_20261022_v2.json`：实际 OOC 布线后 12,179 LUT、14,932 FF、33 BRAM18K、0 DSP；目标 5 ns，关键路径周期报告 4.469 ns，WNS 0.531 ns、WHS 0.024 ns，DRC 0，23,689 条网完整布线。612 输入/279 输出无外部延迟约束，不能作为板级时序签核。

相同请求的 RTL 周期：遍历域 CSR 8,280、完整训练模板 303,893、intent 模板 302,438（11 请求，62 边）；并行 PIP 留出域 CSR 9,102、模板 752,873（9 请求，158 边）。模板分别慢 36.70/36.53/82.72 倍，属于当前 AXI 仿真模型下的负结果。结果未包含真实 DDR/HBM、PCIe 或完整路由器。

`results/hls_ii_diagnosis_20261022_v1.json` 保存 Ross II 诊断的原始调度证据：二分规范映射的 AXI readreq 跨 70 个调度阶段，循环 II=74；排序的 7 字记录共享双端口 BRAM，II=11。没有逐函数运行时占比，不能把全部批次时间归因于其中一个模块。后续应比较带完整内存成本的精确片上映射/缓存与基线，并保留本版。

固定模式面积对照正在执行：`data/derived/hls_fixed_modes_20261022_v1` 保留从原核只改变模式分支与模式校验得到的源副本。每种模式分别综合；两者 Csim/csynth/cosim 已通过，impl 由 `scripts/hls_fixed_pipeline.py` 负责。状态在 `results/hls_fixed_csr_20261022_v1.json` 和 `results/hls_fixed_compact_20261022_v1.json`。不要重复启动。完成后用 `scripts/hls_fixed_report.py` 汇总各自的布线后资源与相同请求周期；没有实卡结论。

分离模式最终报告 `results/hls_fixed_check_20261022_v1.json`：CSR 5,763 LUT/8,540 FF，模板 11,307 LUT/14,283 FF，两者33 BRAM18K、DRC=0、200 MHz内部时序通过。相同请求周期比变为46.35/46.13/94.01，仍为负结果。

真实 U280 图的64 MiB声明容量版本由 `scripts/hls_u280_pipeline.py` 等待已有软件报告后生成；当前仍是待执行验证，不能用旧8 MiB输入结果替代。`src/hls_cmodel.py` 提供精确 C++ 核的本机 CPU 调用，用于公共搜索/路由语义集成；绝非 XRT 或 FPGA 时延。
