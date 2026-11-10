# 方案 A：资源图压缩与直接执行

这是可独立继续研究的实验目录。当前已具备真实器件邻接检查、独立训练/留出、紧凑二进制图与同一 C++ 搜索基准；共享 CSR/模板 HLS 译码核已完成 C/RTL 检查和 OOC 布局布线。真实网表路由集成正在进行，实卡 DDR/HBM 与端到端加速尚未验证。当前 CPU 和 RTL 对照均保留了模板译码较慢的负结果。最新入口见 `NEXT_STEPS.md`。

旧参考路径条件域已完成1,062网/4,209 sink的CSR、模板与C模型等价，以及Vivado精确读回、保护和内部时序检查，证据 `results/netlist_stage_20261022_v1.json`。这不是独立资源域的完成证据。

独立端点区域已采集220,973个完整源、274,732个规范节点和1,100,754条有向边。CSR/模板原1,062网软件路由等价，但原候选物理回写失败（84个非法站点，证据保留）。新站点模型覆盖14个已测LUT实例，已完成全1,062网/17,682 PIP的CSR路由与物理验证：全部放置/连接/保护保持，未新增DRC，内部时序满足；3个网实际使用站点需求。见 `results/site_full_stage_20261023_v1.json`。这不证明所有资源族模型完整，站点模型下的模板/native全量等价仍待完成。

128MiB区域译码核已完成完整C仿真、采样RTL与OOC实现，独立报告 `results/hls_region_check_20261023_v1.json`。匹配采样中压缩核周期为CSR的224.89倍，LUT约1.96倍；尚无加速收益。旧参考域38.55倍结果保留，不能与新工作负载混用。原生规范节点全网路由已通过两模式/1062网的独立核验，单批压缩表示慢2.23倍，证据 `results/native_region_check_20261023_v1.json`。完整站点合法性、原生站点配置状态、公平统计对照、实卡DDR/HBM及功耗仍未完成。最新状态见 `EXPERIMENT_STATUS.json` 与 `AGENTS.md` 顶部。

## 研究问题与方法来源

压缩资源图能否在保持规范节点、边和资源属性一致的前提下，降低真实搜索的访问成本或扩大可处理规模？

可迁移基础：AccDRC 的延迟展开与局部封装；同学已有的 tile/wire 模板、例外表与节点归一化；压缩数据直接执行。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
python3 scripts/run.py real-check
python3 scripts/run.py region-check
python3 scripts/run.py packed-check
python3 -m unittest discover -s tests -v
```

除 `packed-check` 另需 Linux 与 g++ 外，以上命令仅需 Python 3 标准库，不会启动 Vivado、CUDA、下载数据或编译原始工程。`check` 检查配置与本地素材，`plan` 写入待实施实验表，`smoke` 执行合成样例；`real-check` 验证首批邻接与故障注入；`region-check` 冻结训练模板，运行跨 SLR 留出验证、受控搜索及 CPU 计时。输出位于 `results/`，派生图和搜索轨迹位于 `data/derived/`，均不覆盖已有文件。

样例内容：两个相邻 tile 共享一个规范节点；同一个局部连接模板展开后加一条例外边，与显式图逐项比较。

边界：样例不是器件数据库压缩器；不报告 JSON 文件大小为硬件压缩率。

其他变体目前不可运行：`smoke --variant <真实变体名>` 会明确报错，不会退回参考实现并冒充实测。

## 目录入口

| 路径 | 内容 |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | 假设、基线、消融、指标与阶段验证 |
| [INTERFACES.md](INTERFACES.md) | 数据、状态、结果与真实工具接入约定 |
| [NEXT_STEPS.md](NEXT_STEPS.md) | 下一次会话可以直接开始的任务 |
| [configs/experiment.json](configs/experiment.json) | 实验变体、指标和未设定的真实运行参数 |
| [configs/platform.json](configs/platform.json) | U280 DDR/HBM 平台计划，实际环境待记录 |
| [data/toy.json](data/toy.json) | 明确标为 synthetic_smoke 的小型输入 |
| [data/datasets.json](data/datasets.json) | 真实数据待接入清单 |
| [src/reference.py](src/reference.py) | 可运行 CPU 参考例 |
| [adapters/README.md](adapters/README.md) | 真实工具适配入口 |
| [hardware/README.md](hardware/README.md) | 硬件模块与实现流程起点 |
| results/ | 本目录独立的计划和验证输出 |

## 现有代码与资料

优先阅读 DeviceModel.hpp 的模板重建与 getChildrenPacked，再跟踪 main.cpp 的 flatGraphBuilt/CSR 构建路径。

- [cpp_router/include/DeviceModel.hpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/include/DeviceModel.hpp)
- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)
- [RapidWright/src/com/xilinx/rapidwright/rwroute/RWDeviceTemplateCheck.java](../_shared/assets/gpu_router_original/rewrite/RapidWright/src/com/xilinx/rapidwright/rwroute/RWDeviceTemplateCheck.java)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [Simple FPGA routing graph compression](https://arxiv.org/abs/1811.04749)

## 2026-10-22 实验进展

已完成首批 `xcvu13p-fhgb2104-2-e` 真实规范节点与一跳邻接导出：20 个 seed tile、534 个完整展开源节点、5,005 个规范节点、18,203 个 wire 别名、4,870 个物理 PIP / 4,886 条有向边。覆盖 INT、LAGUNA、BRAM、DSP、时钟资源，以及真实平行边、双向 PIP、pseudo PIP。

115 个源节点邻接模板配合实例例外可精确还原。去掉例外后 169 个源节点不等价，其中 86 个连接规则不同，83 个仅属性不同。11 种真实记录故障注入均被检出。详见 [实验设计与结果](EXPERIMENTS.md) 和 [结果入口](results/README.md)。这些数字是语义覆盖与逻辑记录数，不是加速比或硬件压缩率。

新增入口：

- [Vivado 导出器](adapters/export_vivado.tcl) 与 [适配说明](adapters/README.md)。
- [真实样本配置](configs/real_sample.json)、[严格图检查器](src/canonical_graph.py)、[按需模板译码器](src/template_codec.py)。
- 独立检查已保存的外部/修改后模板：`python3 scripts/run.py verify-compact --reference <canonical.json> --compact <templates.json>`。

## 第二轮：冻结模板与真实资源搜索

已用 SLR0 的 384 个源节点拟合并冻结 110 个模板，随后才加载 SLR1–3 的 828 个留出源节点。478 个（57.7%）无需例外；350 个需要连接/属性例外，补齐后全部等价。此次覆盖 25 个跨 SLR 规范节点。

另导出三个源节点的四跳域：229 个完整源节点、875 个规范节点、1,076 条有向边。16 个查询在显式 CSR、原始按需译码和预处理译码上具有相同路径、状态和展开轨迹，26 项回归通过。查询是从真实器件连通性构造的，并非真实网表工作负载。

7 次驻留运行中，12 个一至四跳查询的批次中位时间依次为 **0.625 / 20.956 / 2.891 ms**。预处理版本将规则匹配移到初始化阶段，但仍慢于 CSR；初始化成本分别为 1.063 / 0.579 / 10.759 ms，另有共同的数据加载、模板拟合与例外生成成本。搜索域 186/229 个源节点属于未见模板类型，需要显式回退，这是下一轮的重点问题。

详见 [第二轮报告](results/region_check_20261022_v2.json)、[结果入口](results/README.md) 和 [NEXT_STEPS.md](NEXT_STEPS.md)。没有据此宣称硬件压缩率或 FPGA 加速收益。

## 第三轮：独立搜索训练、完整二进制与原生执行

新采集的 SLR0 训练域包含 3,831 行；SLR1–3 新留出域包含 2,866 行、10,274 个规范节点和 12,824 条边。所有新评估源与此前样本不重叠。原 intent 训练的未知 family 回退数为 2,442；同为 384 行的探索性搜索训练对照降至 854；完整搜索训练降至 3。按 20 个查询的 2,213 次展开加权，回退比例为 83.73% / 31.36% / 0%。

完整 CSR 文件为 4,907,968 字节；属性补丁模板为 4,805,440 字节，减小 **2.09%**。只看邻接区会高估收益：节点、别名、属性和索引仍占主要空间。紧凑文件的所有语义和 C++ 全量边导出均与原始器件记录等价。

最终 v2 的 20 查询驻留批次中位时间：CSR **1.172 ms**、直接模板 **5.653 ms**、预先全展开模板 **0.908 ms**；全展开额外准备 **9.589 ms**、分配 **692,920 字节**。缓存 16/64/256 行分别为 6.359/6.206/5.355 ms，均慢于 CSR。暂未证明直接译码性能收益。

运行 `python3 scripts/run.py packed-check` 可复现；35 项回归通过。格式及测量边界见 [PACKED_FORMAT.md](PACKED_FORMAT.md)，最终报告为 [packed_check_20261022_v2.json](results/packed_check_20261022_v2.json)。v1 的 getrusage 内存峰值继承父进程，不能使用；v2 改为执行后 VmHWM。

完整目标仍在推进，逐项状态见 [EXPERIMENT_STATUS.json](EXPERIMENT_STATUS.json)。本机 VU13P 综合缺少授权；U280 已通过许可检查，正在接入独立的放置后网表实验。实际 XRT 枚举为 0 张卡，实卡 DDR/HBM 尚未验证。
# 第四轮进展（2026-10-22）

完整实验仍在推进，状态见 `EXPERIMENT_STATUS.json` 和 `NEXT_STEPS.md`。

- U280 真实放置网表已导出 1,062 条可重布网、4,209 个 sink；独立 SLR0 训练已冻结，完整参考路径邻接域仍在导出。
- 同一 AGRAPH01 CSR/模板 HLS 核已通过全采样节点 C 仿真、功能分层 RTL 联合仿真和 OOC 布局布线。报告：`results/hls_check_20261022_v2.json`，接口/复现：`hardware/hls/README.md`。
- 保留负结果：相同请求下模板译码的 RTL 周期为 CSR 的 36.7–82.7 倍；OOC 内部时序通过不等于板级 DDR/HBM 或完整路由加速。
- 新入口：`python3 scripts/run.py netlist-check`（待原始导出完成并生成 capture.json），`python3 scripts/run.py hls-report --output results/NEW.json`（不覆盖已有报告）。

