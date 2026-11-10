# 方案 C 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

任务描述包含前驱、规范共享资源 ID、状态字节估计与工作量估计。真实接口增加图页集合、代价版本、CPU/GPU/FPGA 耗时预测、边界端口和回退状态。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。新增的 `profile` 子命令显式使用 RRT1 C++ 适配器，并要求真实输入溯源；不要将所有变体映射到同一个 toy reference。

公开 VPR 基准与商业 `.phys`/DCP 已定位，见 [INPUT_SOURCES.md](INPUT_SOURCES.md)。VPR 接入待实现，应冻结 BLIF/packed `.net`/`.place`、架构、RRG、约束与源版本，以 `(rr_graph_sha256, rr_node_id)` 保留资源身份。不能把 VPR ID 套用下面的 RRT1 tile/wire 编码，也不能仅用最终 `.route` 替代搜索图与运行轨迹。

## C++ 轨迹接口 v1

`scripts/run.py trace-smoke` 输出 `execution_kind=synthetic_router_validation`；真实 RRT1 的 `profile` 输出 `real_cpu_diagnostic`。这是独立诊断协议，不套用只服务 toy 的共享结果校验器，也不标为完整 `real_benchmark`。

每个运行目录有 `manifest.json`、各设置的 `trace.jsonl` / `summary.json`、stdout/stderr、对照与插桩版 `.result`。manifest 保存完整命令、过滤继承变量后的显式 RW/C 配置（在各子运行 summary）、编译命令/版本、输入与源码/二进制 SHA256、CPU 型号/亲和性、重复次数。输出目录必须新建。

| 记录/字段 | 语义 |
|---|---|
| `partition` | 原始 `ptBuildTree` / `ptCollect` 生成的叶任务、连接下标、bbox、后继 |
| `attempt_id` / `parent_attempt_id` | 一次搜索与递归重试的关联；未预算搜索、预算退出、重试不能合并丢失 |
| `connection_id` / `connection_index` / `net_index` / `iteration` | 导出 ID、当前数组下标、net 和拥塞迭代 |
| `budget_pops` / `pops` / `status` | 原始队列 pop 预算、实际次数；退出是 `budget_exhausted`，不是全局无路 |
| `elapsed_ns` | 单次搜索的准备、rip-up、搜索、回溯、提交和收集开销；不含 JSON 序列化及递归重试 |
| `label_access_resources` / `label_write_resources` | `TLD` 标签访问及显式写的规范节点 key 集合；不代表所有共享内存访问 |
| `occupancy_write_resources` | 本次搜索期间增减占用的节点；初始载入和搜索外操作不在此字段内 |
| `examined_edges` | `exploreAndExpand` 实际检查的候选边，含最终被 bbox 拒绝的边；不是全部 raw CSR 加载 |
| `path_resources` | 该次尝试得到的 sink→source 路径；预算失败为空，不能当作完整最终占用快照 |
| `dense_label_pages_512` | 按运行内 dense ID / 512 计算的逻辑分组；不是规范资源页或物理内存页 |
| `truncated` | 任一受限集合达到上限后丢弃了新的元素；不得据此证明访问不相交 |
| `verification` | 最终连接完成数、端点/边/无环校验、按不同 net 计数的容量超额，以及采样总数 |

规范 key 来自源代码 `keyOf(id) = (tileAddr << 20) | wireIndex`，用十进制字符串输出，避免 JSON 消费端浮点精度损失。装载后检查 key 唯一、wireIndex 范围。仅在同一导出器/器件身份下比较；不把独立导出间的 dense ID 当稳定资源 ID。

审计按迭代分组，用 DAG 传递闭包排除已有依赖的任务对。只读交集、标签读写交集、路径交集分别报告；路径交集本身不等于最终非法。默认只记录前 2000 次搜索，每个集合最多 200000 项；总尝试数和预算退出数另外计数，报告丢失范围。

当前适配器只接受 eager `RRT1`、固定输入 bbox，执行串行或原分区单 worker。预算重试保持原始输入约束；“无预算”不等于扩大到完整器件。RRT2/JNI、GPU、批处理回退、动态 bbox、多 worker、真实器件专用合法性与布后时序均未验证。输出路径校验只针对导出图，不能替代 DCP 导入和源工具验证。

## 与现有系统的边界

调度策略先在 CPU 执行；使用同一个搜索后端隔离调度贡献，再增加 FPGA 后端。

优先阅读 main.cpp 的分区 DAG、RW_BATCH_*、GPU 卸载预算与回退；对照 DFMAcc 第 4 节。

## 结果协议

预算策略默认关闭，`profile` 每次结果保存 `budget_policy` 的请求模式/阈值、实际阈值和判定原因；显式 `diagnostic` 保留探测。`budget-bench` 使用同一二进制的无预算/预算两臂，关闭足迹集合收集，输出 `evidence.json` 和 `decision.json`。轻量 `metrics.json` 包含串行搜索/失败搜索/路由阶段纳秒计时及导出图校验，完整进程墙钟由父进程记录。分量含义、证据字段和自动启用条件见 [BUDGET_POLICY.md](BUDGET_POLICY.md)；这些是独立诊断协议，不能改写下面 toy 的性能空值约定。

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

排程中的 work_units 是输入估计，不能转换为 ms 或作为实测加速比。

- 包围盒不交不必然意味着长线物理资源不共享，按规范资源 ID 核验。
- 固定 halo 不能证明覆盖全部可行绕行；允许扩大区域或完整搜索回退。
- 中间资源超额与最终非法需要区分，不预设所有共享都必须拒绝。
- 样例的资源串行化只是保守调度基线，不宣称复刻现有路由器并行语义。
