# 方案 E 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

输入 sites/cells/nets、位置快照与候选 moves；输出约束违规、加权 HPWL 和最优合法候选。真实接口增加 pin offset、BEL/site 内约束、时钟、宏形状、时序模型和接受策略。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。未来添加 `run`/`benchmark` 子命令时需显式选择真实适配器；不要将所有变体映射到同一个 toy reference。

## 与现有系统的边界

CPU 保留接受决策/复杂合法化；FPGA 先加速一个连续批量计算阶段。

先选择一个现有布局器及数据适配器，定位候选评估热点；不要直接从零实现完整布局器。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

没有完整优化循环、时序引擎、商业 site-pin 检查或 GPU 布局器接入。

- HPWL 不是布线线长或时序；候选代价降低不自动证明布后质量提高。
- 共享位置或网络的多个移动不能未经检查同时提交。
- 样例只覆盖显式建模的约束，不证明商业器件放置合法。
- 解析布局的全局密度求解不能统一当作局部 stencil。
