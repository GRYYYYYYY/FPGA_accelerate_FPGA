# 方案 F：硬件局部布线评估驱动布局反馈

这是可独立继续研究的实验目录。当前状态是“实验设计 + CPU 合成样例参考”，真实 CPU/GPU/FPGA 基准尚未接入。

## 研究问题与方法来源

降低真实局部布线评估成本，能否让布局器在相同总时间预算内做出更好的决策，减少后期返工？

可迁移基础：DFMAcc 的粗筛—精确验证；局部重布线；多个布局候选的共享图和差量/影子状态。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
```

仅需 Python 3 标准库，不会启动 Vivado、CUDA、下载数据或编译原始工程。`check` 检查配置与本地素材，`plan` 写入待实施实验表，`smoke` 执行本目录的 CPU 合成样例。输出位于本目录 `results/`，文件名包含时间戳；指定 `--output` 时也不会覆盖已有文件。

样例内容：同一局部图上的多个候选查询，共享冻结的外部硬保留节点；区分找到路径、局部无路径和预算耗尽。

边界：没有全芯片布线、布局反馈循环、同网多连接协商或全局可布线性证明。

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

以 D 的完整连接接口为起点，增加局部边界、候选上下文和预算；布局入口由 E 或现有布局器提供。

- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)
- [cpp_router/include/gpu_route.hpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/include/gpu_route.hpp)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [DREAMPlaceFPGA-MP](https://arxiv.org/abs/2311.08582)

## 当前推荐的第一步

实现 CPU 局部评估器和条件化结果，先确认反馈能影响布局结果，再迁移硬件。
