# 数据目录

- `toy.json`：可以立即运行的合成语义样例。
- `datasets.json`：数据登记；logicnets_jscl 真实设计已 ready，第二独立设计仍 pending。
- `../configs/state_microbench.json`：合成状态轨迹生成参数，与真实实验分开。
- `raw/`：原始真实输入或引用说明。
- `derived/`：适配器生成的任务/轨迹，记录源版本与哈希。
- `derived/logicnets_jscl.rrt` / `logicnets_jscl_provenance.json`：真实 FPGA24 已布局设计的冻结导出及来源。
- `raw/rapidwright_2025.2.1/`：核验过公开发行校验值的同版本运行时和器件数据。
- `raw/runtime_inventory.json`：原始提交包内加密 rapidwright_runtime.zip.zip 的目录清单；不依赖解密即可运行当前实验。

真实访问轨迹位于 `../results/real_trace_20261022T165136Z/`；接口及采样边界见 INTERFACES.md。清点外部资产时用 `rg --files --hidden --no-ignore`，避免遗漏被忽略的真实数据。

不要把大器件库复制七份；共享缓存可以在 `_shared/assets/` 新增独立目录，保持原始快照可核验。
