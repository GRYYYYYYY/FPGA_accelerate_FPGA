# 方案 F 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

输入局部 RRG、外部固定资源、候选端点、搜索预算；输出带条件的局部结果和路径。真实接口需移动后 pin 映射、受影响 nets、外部路径接口、占用快照、候选差量和反馈接受策略。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。未来添加 `run`/`benchmark` 子命令时需显式选择真实适配器；不要将所有变体映射到同一个 toy reference。

## 与现有系统的边界

候选初筛 → 批量局部布线 → 反馈排序/接受 → 权威状态提交 → 最终完整布线。

以 D 的完整连接接口为起点，增加局部边界、候选上下文和预算；布局入口由 E 或现有布局器提供。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

没有全芯片布线、布局反馈循环、同网多连接协商或全局可布线性证明。

- 局部失败不证明全局不可布；预算耗尽必须返回未知。
- 局部成功也不证明全设计可布，输出不能将 global_routable 置为 true。
- 未接受候选不能修改权威占用；各候选试探状态隔离。
- 样例固定外部硬保留只是一个模型；真实协商中的可超额资源须另行处理。
