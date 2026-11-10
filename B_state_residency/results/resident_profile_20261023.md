# 驻留CPU采样诊断

两设计各开/关采样一次，共4项，输出、逐轮收敛、标签计数与构建绑定统一审计通过。LogicNets256页、MCML4096页，固定串行CPU8。标签核心逐字节等同原生ASan/UBSan已通过的resident_zero_v1。

| 设计 | 关闭采样 / s | 开启采样 / s | 本次差异 | 样本数 |
|---|---:|---:|---:|---:|
| logicnets_jscl | 44.487 | 44.533 | +0.10% | 11107 |
| vtr_mcml | 174.635 | 176.831 | +1.26% | 44136 |

单次配对差异包含运行波动和采样开销，不是采样器开销的无偏估计。周期请求1009us，实际样本约每4ms CPU时间一次，不能按请求周期直接换算阶段耗时。无丢样。

| 采样上下文 | LogicNets / % | MCML / % |
|---|---:|---:|
| query_reset | 0.42 | 2.95 |
| zero_page_lookup | 4.65 | 4.00 |
| lru_pin_dirty | 6.16 | 6.67 |
| label_interface_wrapper | 6.84 | 8.13 |
| lease_release_or_wrapper | 1.42 | 2.13 |
| label_prefetch | 3.21 | 6.24 |
| zero_fill_context | 7.36 | 4.44 |
| backing_lookup | 0.43 | 0.40 |
| writeback_context | 0.44 | 0.44 |
| refill_context | 0.01 | 0.01 |
| same_net_owner_lookup | 5.86 | 7.23 |
| adjacency | 6.86 | 7.01 |
| priority_queue | 6.37 | 8.28 |
| other_or_unresolved | 32.42 | 34.60 |

这些是互斥样本代码/栈上下文，不是精确分阶段计时。内联、DWARF行号、库函数地址未知和栈展开会产生偏差；约三分之一样本仍在其他/未解析类。尤其refill_context近零不能证明换入复制无成本：大量实际refill已有计数，库内copy可能无法保留调用上下文。标签表达式类别也不代表独立内存延迟。

重置虽遍历两次数组，但本次仅0.42%/2.95%样本归因，不支持将它视为主要热点。页命中后LRU/pin/dirty维护和标签包装明显可见，预取路径也有开销；预取占比本身不能证明移除预取有净收益。下一步独立消融驻留标签预取，保持标签语义和相同容量，以完整CPU运行确认预取维护成本是否超过收益；再决定LRU更新策略。不会因现有方法成熟而否定组合研究，也不据此宣称创新或硬件加速。

冻结诊断构建及旧正式基线不改。当前仍无FPGA/DMA后端；同输出既有物理证据的MCML RTSTAT-10警告保留。本次没有新增DRC/时序报告。

证据目录：`resident_profile_20261022T235505Z/`；统一审计：`scripts/report_resident_profile.py`；符号和样本归因：`scripts/analyze_resident_samples.py`，sample_analysis.json和各symbols.json保留。
