# 方案 C：自适应分区与异构调度

这是可独立继续研究的实验目录。当前已具备实验设计、CPU 合成调度参考，以及原始 C++ 路由器的独立插桩适配器。适配器已在合成 RRT1 图上验证；真实 CPU/GPU/FPGA 基准尚未接入。

真实输入已定位：Beyond-Flatland 的 20 个 BLIF、Koios/Titan 的 VPR 网表/布局/RRG，以及 FPGA'24 的物理网表和 DCP。此前“未找到真实输入”的判断已纠正；待完成的是方案 C 接入。两篇 3D FPGA 论文的输入梳理和本地证据见 [INPUT_SOURCES.md](INPUT_SOURCES.md)。

## 研究问题与方法来源

联合搜索工作量、驻留复用和共享资源依赖安排任务，能否提高利用率并降低完整布线时间？

可迁移基础：DFMAcc 的复杂度驱动分区；AccDRC 的多级任务封装；现有三叉树/DAG 调度和 CPU/GPU 卸载。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
```

仅需 Python 3 标准库，不会启动 Vivado、CUDA、下载数据或编译原始工程。`check` 检查配置与本地素材，`plan` 写入待实施实验表，`smoke` 执行本目录的 CPU 合成样例。输出位于本目录 `results/`，文件名包含时间戳；指定 `--output` 时也不会覆盖已有文件。

样例内容：在两个抽象 worker 上调度带依赖、资源集合和容量约束的任务；输出抽象工作单位的排程。

边界：排程中的 work_units 是输入估计，不能转换为 ms 或作为实测加速比。

其他变体目前不可运行：`smoke --variant <真实变体名>` 会明确报错，不会退回参考实现并冒充实测。

## 已完成的源码实验（2026-10-22）

```bash
python3 scripts/run.py build-router
python3 scripts/run.py trace-smoke
python3 -m unittest discover -s tests -v
```

这组入口需要 `g++`，首次构建会编译本目录生成的两个 CPU 可执行文件，不修改公共快照、不启用 CUDA/Vivado。`trace-smoke` 在原始搜索与分区代码上执行合成图：串行、原分区单 worker、预算 2/8 后 CPU 重试，以及同 net 共享、最终容量冲突和不可达连接。每个设置重复 3 次，共 33 组，每组都有对照进程；预期失败案例必须被正确检出才能整体通过。

已观察到：两个包围盒不交、DAG 无依赖的分区，可读写同一个搜索标签，而最终路径并不共享资源。它是合成反例上的潜在并发风险，不能据此宣称真实器件已有数据竞争。见 [本轮实验记录](results/EXPERIMENT_20261022.md)。

真实 RRT1 输入的入口与溯源要求见 [adapters/README.md](adapters/README.md)。搜索耗时含插桩开销；图页字段只是 dense node ID 的 512 节点分组。两者都不能直接作为硬件加速或 DMA 量。

## 目录入口

预算默认关闭；显式诊断保留，自动启用须有完整成对计时、正确性和匹配范围的证据。运行 `python3 scripts/run.py budget-bench --fixture shared_candidate --budget 2` 可测量同 CPU 重试开销。本轮预算 2/8 均判定关闭。模式、公式及证据格式见 [BUDGET_POLICY.md](BUDGET_POLICY.md)，运行记录见 [预算判据实验](results/BUDGET_POLICY_20261022.md)。

| 路径 | 内容 |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | 假设、基线、消融、指标与阶段验证 |
| [INTERFACES.md](INTERFACES.md) | 数据、状态、结果与真实工具接入约定 |
| [NEXT_STEPS.md](NEXT_STEPS.md) | 下一次会话可以直接开始的任务 |
| [BUDGET_POLICY.md](BUDGET_POLICY.md) | 默认关闭、诊断模式及实测收益准入规则 |
| [INPUT_SOURCES.md](INPUT_SOURCES.md) | LaZagna 等文献的输入、本地基准及接入边界 |
| [data/input_inventory_20261022.json](data/input_inventory_20261022.json) | 输入绝对路径、来源、存在性与哈希复核范围 |
| [configs/experiment.json](configs/experiment.json) | 实验变体、指标和未设定的真实运行参数 |
| [configs/platform.json](configs/platform.json) | U280 DDR/HBM 平台计划，实际环境待记录 |
| [data/toy.json](data/toy.json) | 明确标为 synthetic_smoke 的小型输入 |
| [data/datasets.json](data/datasets.json) | 真实数据待接入清单 |
| [src/reference.py](src/reference.py) | 可运行 CPU 参考例 |
| [scripts/profile.py](scripts/profile.py) | 构建、原始源码合成验证、真实 RRT1 诊断入口 |
| [src/trace_analysis.py](src/trace_analysis.py) | 规范节点 ID 与原分区 DAG 的访问足迹审计 |
| [adapters/README.md](adapters/README.md) | 真实工具适配入口 |
| [hardware/README.md](hardware/README.md) | 硬件模块与实现流程起点 |
| results/ | 本目录独立的计划和验证输出 |

## 现有代码与资料

优先阅读 main.cpp 的分区 DAG、RW_BATCH_*、GPU 卸载预算与回退；对照 DFMAcc 第 4 节。

- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)
- [cpp_router/src/gpu_bbox.cu](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/gpu_bbox.cu)
- [run.sh](../_shared/assets/gpu_router_original/rewrite/run.sh)
- [run2.sh](../_shared/assets/gpu_router_original/rewrite/run2.sh)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [Potter](https://github.com/diriLin/Potter)
- [Sextans](https://arxiv.org/abs/2109.11081)

## 当前推荐的第一步

从已定位的 Koios/Beyond-Flatland 基准中选择有完整来源记录的网表、架构、固定布局和 RRG，接入 VPR 连接级轨迹，再检查分区共享资源、工作量和预算回退。当前 `profile` 仅支持 RRT1，VPR 与 Interchange 接入待实现；不能直接把 BLIF/RRG/DCP 交给该命令。详见 [输入核查](INPUT_SOURCES.md) 与 [下一步](NEXT_STEPS.md)。
