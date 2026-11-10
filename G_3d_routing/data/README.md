# 数据目录

- `toy.json`：合成语义样例，不承担真实性能比较。
- `datasets.json`：登记两种已接入 ex5p 模型输入及后续 pending 数据。
- `raw/ex5p_natural.json`：原始布局的冻结输入引用与哈希；端点跨层负对照。
- `raw/ex5p_balanced.json`：人工平衡 CLB 层分配的压力布局及完整溯源。
- `derived/ex5p_w100/`：同一完整 RRG 的 SQLite 搜索投影与导出摘要。

原始架构、图、网表和 placement 引用相邻工程，不改写素材。每次 baseline 都校验哈希。模型验证不等于真实器件/工艺验证。
