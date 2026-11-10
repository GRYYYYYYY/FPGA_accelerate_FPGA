# 方案 A 数据与接口

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

输入显式规范节点/边和模板实例映射、增加/删除例外；输出展开邻接与等价性结果。真实接口另需 PIP/开关身份、方向、资源类型、属性例外和受保护资源。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。未来添加 `run`/`benchmark` 子命令时需显式选择真实适配器；不要将所有变体映射到同一个 toy reference。

## 与现有系统的边界

仅替换邻接/属性读取接口，先保持搜索器与代价函数不变。

优先阅读 DeviceModel.hpp 的模板重建与 getChildrenPacked，再跟踪 main.cpp 的 flatGraphBuilt/CSR 构建路径。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

## 限制

样例不是器件数据库压缩器；不报告 JSON 文件大小为硬件压缩率。

- 不同物理资源即使模板相同，也必须拥有独立的动态占用。
- 跨 tile 的同一物理导线必须映射到同一规范节点；不要只按坐标合并节点。
- 保持并行边、开关方向、属性和特殊资源语义；不能只比较边数。

## 已实现的真实采样接口 v1

原始 `vivado_graph_tsv_v1` 由 [export_vivado.tcl](adapters/export_vivado.tcl) 导出。`meta/tile/node/alias/pip/root/edge/oracle_child/seed_tile/selection/complete` 行使用 tab 分隔，属性按 key/value 成对存储；数据中出现 tab 或换行即拒绝。`complete` 必须位于末尾。

`canonical_graph_v1` JSON 含：

| 字段 | 含义 |
|---|---|
| `metadata`, `provenance` | 器件、工具构建版本、采样范围、原始数据路径/SHA256 |
| `tiles` | tile 名→完整导出属性，包括 COLUMN/ROW/TYPE；坐标只用于定位 tile |
| `nodes` | Vivado 规范节点名→导出节点属性，含 INTENT_CODE_NAME/NUM_WIRES 等 |
| `aliases` | 完整 `tile/wire` 名→规范节点名；每个节点所有别名必须保留 |
| `pips` | 完整物理 PIP 名→`up_wire/down_wire/attributes`；属性值保持源字符串 |
| `roots` | 已完整展开源节点→PIP/子节点查询计数；只有此域的邻接已知 |
| `edges` | `pip, direction, src, dst, src_wire, dst_wire`；方向为 forward/reverse |
| `oracle_children` | Vivado 独立 downhill-node 查询；用于验证目标集合，不替代多重边检查 |
| `seed_tiles`, `selections` | 采样 tile、每个源节点的选择原因 |

物理 PIP 与遍历边分开：同一双向 PIP 可以产生两条有向边；不同 PIP 即使端点相同仍分别保存。绝不按 `(src,dst)` 去重。`src`/`dst` 为规范节点名，节点属性、别名和边的 PIP 属性均参与等价检查。

`adjacency_templates_v1` 保留显式 `context`（除 edges/pips 外的规范图字段）、`templates` 与 `instances`。每条规则包括相对 tile 坐标、PIP 后缀、方向、端点局部 wire 名和 PIP 属性（TILE 在译码时补回）。分组键为 `(源 tile TYPE, 规范 wire 名)`，在样本内选择众数规则列表，实例的 `remove/add` 为多重集合补丁。先删除再解析，不能因为补丁前规则无法解析就丢边。当前 context 保留 oracle 便于审计，它不是计划中的硬件数据布局。

Python 入口：

```python
from import_vivado import read_export
from canonical_graph import compare, validate, NodeState
from template_codec import encode, DirectDecoder

graph = read_export(raw_path)
validate(graph)                       # 包括独立 Vivado oracle
compact = encode(graph)
decoder = DirectDecoder(compact)
result = compare(graph, decoder.materialize())
for edge, pip_record in decoder.neighbors(source_node):
    pass
```

`neighbors` 对未展开节点抛出 KeyError；不会将其解释为无出边。`NodeState` 按规范节点存储可变占用，wire 别名映射到同一槽位，模板不存动态状态。

`real-check` 输出 `execution_kind=real_device_validation`，**不是** `real_benchmark`，也不使用仅限旧 smoke 的共享 schema 冒充性能结果。记录输入/代码/配置/派生数据 SHA256、Python/平台、实际捕获命令、复现命令、覆盖统计、失败消融、11 项故障注入和明确限制。`graph_bytes/bytes_per_relaxation/decode_cycles/routing_ms/speedup` 均为 null。

独立检查候选文件：`python3 scripts/run.py verify-compact --reference <canonical.json> --compact <templates.json>`；等价返回 0，解析/语义错误返回 1。`real-check` 的检查失败返回 1，输入/配置错误返回 2。输出均不覆盖已有文件。

## 冻结模板与四跳域接口

`adapters/export_regions.tcl` 复用原导出器的 node/alias/PIP 写出与检查函数。`export_vivado.tcl` 新增 `graph_export_library_only` 开关，仅供加载函数；默认首轮采样行为不变。第二轮输出仍为 `vivado_graph_tsv_v1`，附加 `meta` 字段记录 purpose、BFS seeds/max_depth/max_sources/budget_hit/discovered 和逐 tile 的 excluded 扫描计数；`selection.reason=bfs_depth:N` 记录已展开节点深度。

`heldout.select_sources` 只筛选完整源行，保留它们的所有出边、端点节点及全部别名，不裁掉跨区域边。`fit_bank` 生成 `frozen_bank_v1`，含训练源 ID、SLR、训练图哈希与模板。`encode_frozen` 必须检查规范源节点不重叠；未见 family 使用 `template=null, fallback_rules=[...]`，不会添加新模板。已知 family 仍使用多重集合 remove/add。

`frozen_adjacency_v1` 可由原 `DirectDecoder` 与 `verify-compact` CLI 读取。载荷带 `bank_sha256`；实验驱动额外检查模板表与冻结库逐项一致、评估前后 bank 内容哈希不变。此哈希并不替代对外部文件的可信来源核验。

`PreparedDecoder` 接受同一输入；在初始化时编译删除索引集合，借用 template/add/fallback 只读载荷，避免每次查询深拷贝和 JSON 转换。其输入在 decoder 生命周期中不得修改。输出邻接仍生成新的 edge 与 PIP attributes 字典；动态占用仍由独立规范节点状态持有。

`search_experiment` 的三个 provider 共享同一 `search` 函数，成本为每次有向 PIP 遍历一跳。返回状态 `found / no_path / budget_exhausted / incomplete_domain`。单位代价 BFS 首次发现目标即可结束，不要求目标本身有已导出的邻接。只有队列实际耗尽且未触及未知邻接才返回 no_path。

轨迹按展开源记录 distance、按序取回的全部 PIP/方向/目标以及实际检查边数。`fetched_edge_records` 与 `examined_edges` 分开：找到目标时，已取回的邻接可能尚未逐项检查。路径保存完整 edge 身份，不能仅按节点序列比对。

`region-check` 输出 `execution_kind=real_device_search_microbenchmark`。其中搜索时间为真实测量的 Python CPU 时间；查询由器件图构造，既不是 synthetic_smoke，也不是完整网表 real_benchmark。trace、图、模板库、查询列表为单独带哈希的 artifacts；初始化/前处理与驻留查询计时分开，硬件/完整 router speedup 为 null。原始/派生 JSON 字节数仍不作为紧凑格式容量。

## 执行二进制与原生入口

新增 AGRAPH01，完整定义见 `PACKED_FORMAT.md`。写入器 `write_packed` 与严格读入器 `PackedGraph` 保留全部静态语义；文件独占创建。未知源行 -1 必须返回 incomplete_domain，不得转换为空邻接。

原生程序参数为 `packed_bench graph.agr queries.bin cache_entries repetitions dump.bin direct|expanded`。查询记录为 `<4I>`：source、target、展开预算、是否计时；输出边转储为 `<8I>`：source 与完整七字段边记录。JSON 输出包含首轮完整路径、状态与计数，以及初始化、搜索、回溯、批次时间、实际文件/分配容量、执行后 VmHWM。查询/节点编号按完整规范名称排序；各文件字符串和属性 ID 可能不同，比较路径须先恢复语义。

CLI `python3 scripts/run.py packed-check` 固定训练库后导入新域，校验文件哈希、全量语义和原生边，再运行全部对照。失败返回非零，已有报告不覆盖。原生 reader 接收 Python 验证通过的本地实验文件，不作为安全边界的通用不可信格式解析器。
# 新增执行接口

`hardware/hls/graph_expand.hpp` 定义 AGRAPH01 邻接核的 AXI 主存与 AXI-Lite 控制接口，详细配置、容量限制与错误状态见 `hardware/hls/README.md`。输入镜像须经主机严格验证；本版上限 8 MiB，不能截断更大的图。每输出边有 8 个 uint32，包含 source 和完整边表引用；动态占用按规范节点由公共路由器管理。

`src/netlist.py` 读取 `routed_netlist_tsv_v1`，按物理网组聚合层次段，仅去除完全相同的端点重复记录。`src/netlist_routing.py` 的 provider 复用 `neighbors(canonical_node)` 接口；未知行抛 `IncompleteDomain`，搜索记录该分支未知并继续其他分支。所有非选中网及其他网的源/目标端点均受保护。

`scripts/prepare_netlist_routes.py` 生成 `canonical_routes_v1` TSV 数据。`adapters/apply_netlist_routes.tcl` 只把已独立验证无冲突的完整树赋给 FIXED_ROUTE，立即核对实际节点/PIP；`scripts/check_netlist_readback.py` 复核全网连接、未选中占用与全部单元 LOC/BEL。这条回写流程尚待真实候选实测。


## 站点感知结果与物理回写

`site_routing_experiment.py` 输出plan.json、routes.json和report.json；routes中site_demands保存信号独占、INIT掩码/值与分类配置需求。未知伪PIP需求不能当空需求。运行中冻结plan依赖，不修改或竞争同一输出。

`python3 scripts/prepare_site_routes.py EXPERIMENT --output NEW.tsv` 校验冻结输入和探针证据，从实际路径独立重算规范树及站点需求，仅发布完成且无冲突的候选。候选meta保留`tested_instances_only_physical_validation_required`范围。原 `prepare_netlist_routes.py` 继续处理旧CSR/模板报告；两者均使用canonical_routes_v1，供 `netlist_apply::apply` 读取。

软件验证不替代物理验证。应用后必须执行check_netlist_readback.py和check_netlist_quality.py，核对全部单元、连接、保护网、精确节点/PIP和质量。g[37]接口探针成功但其site_demands为空；站点模型覆盖不能据此扩大。
