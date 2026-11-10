# 结果目录

## 当前入口：冻结模板与受控 CPU 搜索

[region_check_20261022_v2.json](region_check_20261022_v2.json) 是本轮最终报告，所有检查通过。运行 `python3 scripts/run.py region-check` 可离线复现；`python3 -m unittest discover -s tests -v` 共 26 项通过。

- 训练：SLR0 的 384 个规范源节点 → 110 个固定模板。
- 留出：SLR1–3 的 828 个源节点，478 个（57.7%）无需例外，350 个需例外，补齐后全等；覆盖 25 个跨 SLR 节点。
- 四跳搜索域：229 个完整源节点、875 个规范节点、1,076 条有向边；646 个边界节点未展开。186 个源节点未见模板类型，采用显式回退。
- 三种表示的 16 个查询路径/状态/轨迹一致：12 个一至四跳查询找到路径，加零跳共 13 个 found，其余分别为预算耗尽、邻接不足与已确认无路径。

| Python provider | 12 查询批次中位 ms（7 次） | provider 初始化 ms |
|---|---:|---:|
| 显式 CSR | 0.624960 | 1.063237 |
| 原始按需模板 | 20.956275 | 0.579373 |
| 预处理共享模板 | 2.890911 | 10.758953 |

预处理将规则删除索引提前计算，仍共享规则载荷，不预展开规范边；改善了原始实现的 JSON/深拷贝开销，但当前仍慢于 CSR。输入加载、训练拟合、评估例外生成另列在报告的 `preprocessing_ms`，不能忽略。CPU 环境补充见 [region_environment_20261022.json](region_environment_20261022.json)。

报告 `artifacts` 包括冻结库、两组显式/模板图、固定查询列表和完整搜索轨迹，每项均带 SHA256。`profile` 是计时之外的独立 cProfile，累计时间不可相加。`region_check_20261022_v1.json` 保留加入预处理版本之前的结果与代码哈希。

这些是从真实器件构造的单位跳数 BFS 查询，不是网表布线性能。原始数据及采样参数见 `configs/region_query.json`；完整分析见 [EXPERIMENTS.md](../EXPERIMENTS.md)。下一轮优先改善训练覆盖、实现 packed 布局和全成本计量，见 [NEXT_STEPS.md](../NEXT_STEPS.md)。

## 首轮真实语义结果（历史基线）

[real_check_20261022_v1.json](real_check_20261022_v1.json) 为首轮最终报告，`execution_kind=real_device_validation`，所有检查通过。其 `artifacts` 字段给出显式规范图、模板图的路径与 SHA256，`provenance` 保存输入/代码/配置哈希、环境、实际捕获命令和复现命令。

| 覆盖/检查 | 结果 |
|---|---:|
| 完整源节点 / 规范节点 / wire 别名 | 534 / 5,005 / 18,203 |
| 物理 PIP / 有向边 | 4,870 / 4,886 |
| 跨 tile 规范节点 / 平行端点对 | 2,168 / 10 |
| 双向 / pseudo / 可反相 PIP | 18 / 10 / 6 |
| 模板 / 有例外的源节点 | 115 / 169 |
| 省略例外：连接规则不同 / 仅属性不同 | 86 / 83 |
| 故障注入检出 / 回归用例通过 | 11/11 / 11/11 |

通过 `check / plan / smoke / real-check` 和 `python3 -m unittest discover -s tests -v`；已保存模板可用独立 `verify-compact` CLI 校验。明确保留节点与别名表以及审计 oracle；模板规则数和 JSON 文件大小都不能作为硬件压缩率。

复现 Python 检查：

```bash
python3 scripts/run.py real-check
python3 -m unittest discover -s tests -v
python3 scripts/run.py verify-compact \
  --reference data/derived/canonical_20261022T144854.482817Z.json \
  --compact data/derived/templates_20261022T144854.482817Z.json
```

最后两个路径以报告 `artifacts` 为准。重新采样见 [适配器说明](../adapters/README.md)。

## 结果边界与历史文件

- `plan_*.json`：待实施实验表；`smoke_*.json`：手写 CPU 合成样例。
- `real_check_20261022T144125.809589Z.json`：本轮早期的同样本验证记录，保留当时的代码哈希；当前入口使用上面的最终报告。
- `vivado/`：本次 MCP Tcl 会话日志，包括初次 Tcl 兼容问题及成功导出记录。
- 该样本只承诺 534 个源节点的一跳邻接，4,471 个目标节点仍未知邻接；67 个源节点已确认零出度。
- 模板在同一批样本拟合；未验证留出泛化、真实网表保护/占用、excluded PIP、完整搜索、时序或实卡。所有性能字段为 null。

不覆盖旧运行结果。下一步见 [NEXT_STEPS.md](../NEXT_STEPS.md)。

## 第三轮最终报告（2026-10-22）

优先读取 `packed_check_20261022_v2.json`，以及 `../PACKED_FORMAT.md`。对应原始数据及哈希位于 `../data/raw/traversal_20261022_v1/capture.json`；配置 `../configs/traversal_v1.json` 在新评估前登记。C++ 可执行文件、边转储、查询和训练库的实际路径/哈希在报告 artifacts 中。

- 3,831 行 SLR0 训练；2,866 行新 SLR1–3 评估。完整深度 5，边界邻接未知。
- intent / 同预算探索性搜索训练 / 完整搜索训练：回退 2,442 / 854 / 3 行；展开加权 83.73% / 31.36% / 0%。
- CSR / intent / 同预算 / 完整规则例外 / 属性补丁文件：4,907,968 / 4,952,448 / 4,853,312 / 4,865,600 / 4,805,440 字节。
- 24 查询（20 计时、4 语义探针），9 个执行变体。全量边、路径、状态、展开/扫描/获取边数一致；35 项回归通过。
- CSR / 直接模板 / 全展开：驻留批次 1.171501 / 5.653277 / 0.908454 ms；全展开准备 9.588627 ms 和额外 692,920 字节。
- 全进程 VmHWM 约 8.78–9.28 MB；状态数组/队列负载 410,960 字节，每个查询初始化。逻辑记录读取不是物理内存流量。

`packed_check_20261022_v1.json` 保留历史；其 `process_peak_rss_bytes` 受到 fork 继承 Python 父进程峰值影响，应使用 v2 的 `process_vm_hwm_bytes`。两轮计时变动反映系统噪声；没有随机进程顺序或置信区间，不能把小差异作为稳定加速。

真实网表与 FPGA 实验尚在推进，以上不是完整布线或硬件收益。VU13P 综合许可错误保存在 `../data/netlist/routeracc_cost_20261022_v1/failure.json`。

## U280 放置/布线网表基线

`../data/netlist/routeracc_cost_u280_20261022_v1/capture.json` 保存来源、失败恢复过程及所有产物哈希。Vivado 2022.2，1,833 原语；1,277 个可布线逻辑网全部完成，路由错误 0；从固定放置恢复的 route_design 用时 40.920 s。内部 10 ns 时钟下 WNS 6.530 ns、WHS 0.020 ns。168 输入和 175 输出没有外部延迟约束，属于 OOC 工作负载，不是完整 IO 时序签核。

这个真实网表用于下一轮 source/sink、占用保护和路由回写实验。它没有实现压缩硬件；完整目标仍 active。
# 第四轮当前证据

- `hls_check_20261022_v2.json`：HLS 全量 C 仿真、分层 RTL 子集、同工作量周期对比、实际 OOC 布线资源与时序，附文件哈希。模板慢 36.7–82.7 倍；没有实卡收益结论。
- `hls_ii_diagnosis_20261022_v1.json`：原始调度日志与 schedule 行级证据，映射依赖 II=74、排序 BRAM 端口 II=11。
- `netlist_baseline_drc_20261022.rpt`：RouterAcc 路由工作负载基线的一条 HDOOC-4 警告；不要与 HLS 核的 DRC=0 混为一谈。
- `regression_20261022_netlist_v1.log`：44 项全回归；`netlist_router_tests_20261022_v2.log`：新增端点保护后 10 项路由回归。
- `../data/derived/netlist_u280_bank_20261022_v1/manifest.json`：3,761 行 SLR0 独立训练，440 模板。真实网表邻接还在 `vivado/export_netlist_domain_20261022.stdout` 对应的 batch 中导出，不得读半文件当完成。

