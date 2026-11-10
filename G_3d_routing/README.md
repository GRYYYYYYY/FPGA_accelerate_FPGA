# 方案 G：三维跨层资源选择与分层搜索

这是可独立继续研究的实验目录。已接入固定版本原始 VPR 的 CPU 模型基线、完整 RRG 转换和路由审计；保留原 CPU 合成样例。GPU/FPGA 加速器与候选选择算法的完整路由比较尚未实现。

## 研究问题与方法来源

针对离散固定的跨层资源，候选端口选择和局部搜索能否改善三维布线的求解时间与质量？

可迁移基础：H3D 的异构资源建模与树优化；LaZagna/VTR 三维图；层次分区与批量候选搜索。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
```

上述三个命令仅需 Python 3 标准库，不会启动 Vivado、CUDA、下载数据或编译原始工程。`check` 检查配置与本地素材，`plan` 区分可执行模型基线与计划变体，`smoke` 执行本目录的 CPU 合成样例。输出位于本目录 `results/`，文件名包含时间戳；指定 `--output` 时也不会覆盖已有文件。

样例内容：两层有向图含两个固定垂直端口，逐个限制端口求局部路径，并与不限制端口的参考路径一起输出。

边界：只演示两层单次跨层候选，不实现 H3D 动态规划、多终端树或三维拥塞协商。

其他变体目前不可运行：`smoke --variant <真实变体名>` 会明确报错，不会退回参考实现并冒充实测。

## 原始 VPR 模型基线

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run.py baseline
# 或只复现跨层压力布局
python3 scripts/run.py baseline --cases ex5p_balanced --repetitions 3
```

`baseline` 串行执行 route-only，默认两种布局各 3 次，seed=1，W=100，每次超时 120 秒。使用 [vpr.lock.json](configs/vpr.lock.json) 指定的归档干净基线程序，提交为 `0b912334fdd83bb754b302146ac0d1ec9edc9a0e`；不会使用相邻工程正在修改的路由器。运行前后校验输入、程序和派生图哈希。TBB 依赖解包在本目录 `toolchain/runtime/`，不依赖本机全局安装。

两种布局分别是原始 ex5p 布局和人工平衡 CLB 层分配的压力布局，后者不是自然布局质量证据。数据是 VPR 的 Hecate 三维架构模型，不代表实物工艺签核。结果见 [基线实验记录](results/BASELINE_REPORT.md)。

完整 RRG 已转为 [SQLite 图与导出摘要](data/derived/ex5p_w100/summary.json)。需要重新导出时使用**新的**输出目录：

```bash
python3 scripts/run.py export-rrg \
  --rr-graph ../../3D_FPGA_routing/results/runs/baseline_ex5p_w100_seed1/rr_graph.xml \
  --sha256 6ed35333d25d5c08af7d77706de9cb1764529349649cbe70005fc6c19cf50317 \
  --output data/derived/ex5p_w100_new
```

原始 XML 继续作为 VPR 的权威输入；SQLite 是搜索与候选评估的数据投影。`CHANZ` 是有容量的节点，跨越一个层区间，不能直接套用 toy 的单层节点/垂直边语义。详见 [INTERFACES.md](INTERFACES.md)。

## 目录入口

| 路径 | 内容 |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | 假设、基线、消融、指标与阶段验证 |
| [INTERFACES.md](INTERFACES.md) | 数据、状态、结果与真实工具接入约定 |
| [NEXT_STEPS.md](NEXT_STEPS.md) | 下一次会话可以直接开始的任务 |
| [configs/experiment.json](configs/experiment.json) | 实验变体、指标和未设定的真实运行参数 |
| [configs/platform.json](configs/platform.json) | U280 DDR/HBM 平台计划，实际环境待记录 |
| [data/toy.json](data/toy.json) | 明确标为 synthetic_smoke 的小型输入 |
| [data/datasets.json](data/datasets.json) | 已接入模型数据与后续数据清单 |
| [src/reference.py](src/reference.py) | 可运行 CPU 参考例 |
| [adapters/README.md](adapters/README.md) | 真实工具适配入口 |
| [hardware/README.md](hardware/README.md) | 硬件模块与实现流程起点 |
| results/ | 本目录独立的计划和验证输出 |

## 现有代码与资料

先检查上级已有 3D_FPGA_routing 目录及 LaZagna/VTR 版本，不自动修改该独立项目。

- [cpp_router/include/DeviceModel.hpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/include/DeviceModel.hpp)
- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [H3D](https://www.cse.cuhk.edu.hk/~byu/papers/C297-ICCAD2025-3DRoute.pdf)
- [LaZagna](https://github.com/sharc-lab/LaZagna)
- [Escaping Flatland](https://arxiv.org/abs/2604.01078)

## 当前推荐的下一步

在已固定的模型 RRG 上实现离线候选端口评估：先验证有向可达性、节点共享容量与回退，再接入相同输入/目标函数下的原 VPR、简单垂直惩罚和 CPU 候选选择对照。
