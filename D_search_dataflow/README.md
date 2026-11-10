# 方案 D：事件驱动搜索数据流

这是可独立继续研究的实验目录。当前状态是“实验设计 + CPU 合成样例参考”，真实 CPU/GPU/FPGA 基准尚未接入。

## 研究问题与方法来源

可变出度搜索的队列、访存和更新依赖如何组织，才能提高有效搜索吞吐而不显著增加无效扩展？

可迁移基础：RouterAcc 的分层存储；FlowGNN/ThunderGP 的图数据流；Sextans 的稀疏任务调度与片上更新。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
```

仅需 Python 3 标准库，不会启动 Vivado、CUDA、下载数据或编译原始工程。`check` 检查配置与本地素材，`plan` 写入待实施实验表，`smoke` 执行本目录的 CPU 合成样例。输出位于本目录 `results/`，文件名包含时间戳；指定 `--output` 时也不会覆盖已有文件。

样例内容：在含并行边、不同出度的有向非负图上运行 Dijkstra，保留边 ID 回溯并验证已知最短代价。

边界：样例不是现有 CPU A* 的等价实现，不包含时序驱动成本或外层拥塞协商。

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

优先阅读 f_min_search.v、cen_node_ctrl.v、cost_ctrl.v，并对照 main.cpp 的优先队列和 gpu_route.cu 搜索。

- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)
- [cpp_router/src/gpu_route.cu](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/gpu_route.cu)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [FlowGNN](https://arxiv.org/abs/2204.13103)
- [ThunderGP](https://www.comp.nus.edu.sg/~wongwf/papers/FPGA2021.pdf)
- [FPGA-Assisted Deterministic Routing](https://graphsearch.epfl.ch/en/publication/271583)

## 当前推荐的第一步

导出真实图查询，建立路径回溯、代价和合法性参考；区分一般 Dijkstra 与现有启发式搜索语义。
