# 数据目录

- `toy.json`：可以立即运行的合成语义样例。
- `datasets.json`：数据登记；已找到的原始基准为 `located_adapter_pending`，待生成的连接轨迹仍为 `pending`，均不伪装成已可运行。
- `input_inventory_20261022.json`：公开/商业基准路径、来源记录、文件大小与本次哈希核查范围。
- `raw/`：原始真实输入或引用说明。
- `derived/`：适配器生成的任务/轨迹，记录源版本与哈希。

不要把大器件库复制七份；共享缓存可以在 `_shared/assets/` 新增独立目录，保持原始快照可核验。

`scripts/run.py trace-smoke` 将合成 RRT1 及其描述写入本次 results 目录。它们运行原始 C++ 搜索代码，但仍不是物理器件数据。真实/公开应用电路已定位，详见 [文献与输入核查](../INPUT_SOURCES.md)；VPR 和 Interchange 接入尚未实现。现有 RRT1 入口要求输入 SHA256、器件、导出器与源版本，见 [适配器说明](../adapters/README.md)。
