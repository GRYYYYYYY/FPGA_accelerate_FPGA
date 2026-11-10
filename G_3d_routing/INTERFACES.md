# 方案 G 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

节点包含 layer；垂直边有明确 ID；输入 source/target 和候选端口。真实接口需架构参数、边容量、开关/延迟、net 树分支、价格版本和合法的跨层连接集合。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。未来添加 `run`/`benchmark` 子命令时需显式选择真实适配器；不要将所有变体映射到同一个 toy reference。

## 与现有系统的边界

先比较原算法、简单跨层代价与 CPU 候选选择，再卸载同一个候选算法到普通 FPGA 加速卡。

先检查上级已有 3D_FPGA_routing 目录及 LaZagna/VTR 版本，不自动修改该独立项目。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

原 toy 只演示两层单次跨层候选，不实现 H3D 动态规划、多终端树或三维拥塞协商；新 baseline 运行原始 VPR，不含自定义候选优化。

- 只选择架构已有的垂直连接，不能自由移动或新增 HBT。
- 普通多金属层 ASIC 图、商业多 SLR 器件和堆叠 3D FPGA 模型应区分。
- 跨层次数更少不必然时序更好，需要联合延迟与拥塞评价。
- 模型化 RRG 验证不等于真实三维工艺签核。

## 已实现的原生 CHANZ 接口

`data/raw/ex5p_*.json` 固定架构、BLIF、packed netlist、placement、原始 XML RRG 和归档参考 route 的路径与 SHA256。大型原始输入引用相邻工程；校验失败即停止，不改写原始素材。`configs/vpr.lock.json` 保存 VTR 提交、干净构建归档、基线程序、独立审计脚本快照及本地 TBB 库的哈希。相邻 VTR 工作树有后续算法改动，不是本目录原算法基线的程序来源。

`adapters/vpr_rrg.py` 流式转换原始 XML，输出 `rr_graph.sqlite` 和 `summary.json`。不将此投影回写成 VPR 输入；block types、grid 等仍以原 XML 为准。

| SQLite 表/视图 | 语义 |
|---|---|
| `nodes` | 保留稀疏原始 ID、type、capacity、direction、XY 和 `layer_low/high`、ptc、segment、R/C 及原节点 XML |
| `switches` | 原始 switch ID、类型、名字、Tdel/R/C 和原 XML；Tdel 单位为秒，缺失可选字段保留 NULL |
| `edges` | 零起始 XML 顺序号为 edge ID；保留有向 `(src,dst,switch_id)`，不合并平行边；附带两端 CHANZ ID 或直接跨层标志 |
| `portals` | 每个 `CHANZ` 对应一个 `chanz:<RR node ID>`，容量由该节点定义 |
| `vertical_edges` | CHANZ 的入/出边及无 CHANZ 的直接跨层边，关联实际 switch timing；它们不是独立垂直容量 |

原生 CHANZ 跨越层区间，不可将其压成一个 layer 字段。所有进入/离开同一 CHANZ 的边共享节点容量；同一 net 的树分支共享同一资源时按 net 计占用。入/出度非零也不保证源到目标可达，后续算法仍须在有向图上验证。此版本拒绝非 CHANZ 的跨层区间节点，防止静默误读未知编码。

延迟须保留整条路径的 switch 和节点 RC。某个 switch 的 Tdel 不是整个垂直端口或源汇路径的固定延迟。当前导出保留缺失值，独立审计中的零 RC 路径累加仅适用于固定 VPR 模型的默认零值语义；逻辑内延迟和 CPD 仍由原生 VPR STA 计算。格式依据：[VTR 官方文件格式](https://docs.verilogtorouting.org/en/latest/vpr/file_formats/)以及锁定源码的 `libs/librrgraph/src/io/rr_graph.xsd`。

`baseline` 输出为 `execution_kind=real_benchmark`、`backend=native_vpr_cpu`，并显式标注架构模型与人工布局类型。每次保存 invocation、原生日志、process 记录、完整 route、XML 审计和 result；批次 summary 保留全部成功/失败。计时分为 VPR 的 Routing took（原生日志精度 0.01 秒）和 route-only 进程 wall time；后者含图加载、routing、analysis，不含哈希、导出、独立审计。没有功耗或 FPGA 加速比。

验收同时要求：原生 FULL checker、独立有向边/switch/树结构/容量审计、派生 SQLite 的所有路由节点/边检查，以及归档参考的完整路由记录、CPD、线长一致。独立审计不覆盖 netlist 端点映射、局部 OPIN 预留、非配置边闭包和 bus mux 选择，这些仍依赖 VPR。比较路线时只忽略含路径的文件头，保留分支重启、节点 ID、switch 和 sink pin index。
