# 数据目录

- `toy.json`：手写合成样例，仍由 smoke 单独使用。
- `datasets.json`：真实器件语义样本 `real_A_vivado_semantics_1` 已 ready；原始 RapidWright 图/查询轨迹及 FPGA24 兼容数据仍 pending。
- `raw/xcvu13p_sample_20261022_v2.tsv`：2026-10-22 由 Vivado 2022.2 / SW Build 3671981 的 `xcvu13p-fhgb2104-2-e` 静态数据库直接导出，带 complete 尾标，不改写。名称 v2 源自首次导出因 Tcl `try` 不兼容而重试；无混入首次失败数据。
- `derived/canonical_*.json`：规范节点/别名/多重边/属性与独立 oracle。
- `derived/templates_*.json`：节点与别名保持显式，邻接使用模板与 add/remove 例外。

输入哈希、导出器捕获时哈希、实际捕获/复现命令见 `configs/real_sample.json`；每次 real-check 为新派生文件保存哈希。该数据仅支持 534 个指定源节点的完整一跳邻接，不能直接用于完整布线路由基准。

数据来自本机安装器件库，不复制整器件数据库。默认 real-check 会核对登记原始 SHA256，覆盖输出会报错。

## 第二轮数据

- `raw/regions_20261022_v1/heldout.tsv`：36 tile / 828 完整源行，规范源 SLR 分布 1:272、2:276、3:280。
- `raw/regions_20261022_v1/closure.tsv`：三个源的四跳 BFS 域，229 完整源行，646 未展开边界节点；未耗尽 4,000 源预算。
- `configs/region_query.json`（本目录上一级）：固定训练/评估输入及 SHA256、捕获代码 SHA256、实际命令、预算与重复次数。
- `derived/regions_*/`：冻结模板库、heldout/search 的显式图与模板图、查询、展开轨迹；具体路径/哈希由 `results/region_check_*.json` 引用。

新增两个 ready 数据集仅表示静态资源采样可用；完整网表路由数据仍未接入。历史输入与运行结果保留。
