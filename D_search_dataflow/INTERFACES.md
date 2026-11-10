# 方案 D 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

输入规范节点/边、冻结边权、source 与 target 集合；输出路径边 ID、代价和逻辑搜索计数。真实接口还需 resource/node 代价、同网共享、上下文、版本及在途终止状态。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。未来添加 `run`/`benchmark` 子命令时需显式选择真实适配器；不要将所有变体映射到同一个 toy reference。

## 与现有系统的边界

沿用 gpuFloodConnection 层次卸载完整连接；先返回完整路径，由 CPU 提交。

优先阅读 f_min_search.v、cen_node_ctrl.v、cost_ctrl.v，并对照 main.cpp 的优先队列和 gpu_route.cu 搜索。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

样例不是现有 CPU A* 的等价实现，不包含时序驱动成本或外层拥塞协商。

- 目标首次入队不能作为一般最短路终止条件。
- 同一节点的在途更新、失效队列项和必要的重新打开需要处理。
- 单算子 II=1 不等于全搜索每拍推进；实测反馈环与多上下文行为。
- 当前 RTL 快照不等于论文最终实现，原型缺陷修复不自动等于研究新贡献。
