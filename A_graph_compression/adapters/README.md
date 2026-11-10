# 真实工具适配入口

已实现 `export_vivado.tcl` → `import_vivado.py` → 规范图 / 模板图 / 等价报告，原始参考代码与公共工具未修改。

## 复用已导出的真实数据

```bash
python3 scripts/run.py real-check
python3 -m unittest discover -s tests -v
```

默认输入、SHA256、器件、导出器捕获时 SHA256 与导出命令记录在 `configs/real_sample.json`。只依赖 Python 标准库，不启动 Vivado。输出 `results/real_check_*.json` 引用两个带 SHA256 的 `data/derived/*.json` 文件。

## 重新导出

实际操作优先 vivado-mcp：先 `vivado_list_sessions`，复用适合的会话；没有则在本目录 `results/vivado` 创建 Tcl 会话。已加载器件必须为 `xcvu13p-fhgb2104-2-e`。

```tcl
set graph_export_path /absolute/path/to/NEW_SAMPLE.tsv
source -notrace /absolute/path/to/adapters/export_vivado.tcl
```

不依赖 MCP 的批处理复现命令（从本目录执行）：

```bash
/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado \
  -mode batch -source adapters/export_vivado.tcl \
  -tclargs data/raw/NEW_SAMPLE.tsv
python3 scripts/run.py real-check --input data/raw/NEW_SAMPLE.tsv
```

需新输出路径，脚本不覆盖已有输入。导出脚本自带空工程创建与 link_design；使用 Tcl 8.5 兼容的 `catch`，没有使用新版本 `try`。当前固定该器件的采样策略，扩大区域需要修改策略并记录新配置/哈希。只有已实测的 MCP 路径完成了本次导出；批处理入口用于复现。

采样策略：8 个固定 INT tile，LAG_LAG、BRAM、DSP、RCLK_INT_L 各按名字排序选首/中/尾，共 20 个 seed tile。每 tile 按 intent 选择至多四个本地规范源节点，并加入真实双向/pseudo/excluded PIP 端点和两个远端别名节点。排序采样不等于随机代表性抽样，也不保证覆盖每个 SLR 边界。

对每个源节点，完整查询 `get_pips -downhill` 与独立的 `get_nodes -downhill`；不裁掉采样 tile 外的邻接。每个 PIP 的起终 wire 通过 `get_wires -uphill/-downhill` 查询，再由 `get_nodes -of_objects` 获得规范身份。双向 PIP 在源匹配反向端点时发出 reverse 边。每个节点的全部 wire 都再次查询规范节点，检测别名错误。所有由 `list_property` 暴露的节点、tile、PIP 属性（除身份字段 NAME/CLASS）原样保存为字符串。

TSV 最后一行 `complete` 记录对象总数；缺行/未完成、重复记录、别名缺失、非法方向或独立邻接不一致都会被拒绝。出现 `No pips/nodes matched` 的已展开源节点记录为明确的零出度，不使用 `-quiet` 掩盖未知命令错误。

## 参考源码适配结论

`DeviceModel.hpp` 用 tile connection pattern 的 union-find 重建规范节点，随后构造 `srcOff/srcKids`；`getChildrenPacked` 返回子节点及属性。`main.cpp` 的 `lazyPrepassMaterialize` 及全器件直采路径把子节点 ID 写入 CSR。该接口未携带每条边的 PIP 身份，本阶段不能据其子节点集合宣称完整边语义等价。

后续可在本目录添加独立适配器与它比较，但要先补 PIP sidecar/属性映射和源器件版本；不得修改原始快照。当前 Vivado 样本也不代表 RapidWright 的所有过滤规则已经复现。

命令语义参考：[AMD UG835 get_nodes](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/get_nodes)、[get_wires](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/get_wires)、[get_pips](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/get_pips)。在线页面可能指向更新版本，实际支持范围以本机 2022.2 `help`、属性查询与本次成功运行记录为准。

## 第二轮：实际 SLR 留出与多跳域

`python3 scripts/run.py region-check` 从 `configs/region_query.json` 的登记输入离线重跑。它先从首轮原始数据挑出 SLR0 源节点拟合模板，再读取第二轮评估文件；显式检查源分组、输入哈希与冻结库未变。

重新导出时，使用新目录避免覆盖：

```tcl
set region_export_dir /absolute/path/to/data/raw/NEW_REGION_RUN
source -notrace /absolute/path/to/adapters/export_regions.tcl
```

批处理等价入口：

```bash
/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado \
  -mode batch -source adapters/export_regions.tcl \
  -tclargs data/raw/NEW_REGION_RUN
```

本轮已实际运行 MCP Tcl 路径。新目录生成 `heldout.tsv` 与 `closure.tsv`；新实验需登记新配置/哈希，再 `region-check --config <new.json>`。采样逻辑固定在 exporter 中，改配置不能自动改变导出范围。

留出：36 个 seed tile 覆盖 SLR1–3，每 SLR 的 LAG_LAG、BRAM、DSP、RCLK_INT_L 选实际物理上下边界行，并加入 INT 内部/边界点。特别纳入经 canonical 查询可能位于另一 SLR 的 NODE_LAGUNA_DATA；按规范源节点的实际 SLR 审计分组。

多跳：三个明确的规范节点做多源 BFS，完整展开距离 0–3，保留距离 4 未展开边界，上限 4,000 个源节点；本次仅展开 229 个，未耗尽预算。`closure_check` 用独立 downhill-node oracle 重建深度，要求预算未耗尽、预边界节点完整、声明的深度与源集一致，才认证该范围。
