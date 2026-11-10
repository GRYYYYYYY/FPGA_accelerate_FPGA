# 固定槽索引LRU：真实CPU布局先导

4/4运行及独立完成审计通过。由冻结resident_zero_v1派生，保留prefetch-on、标签语义、精确LRU顺序和pin保护。改用Frame内previous/next索引与head/tail，队尾命中直接返回；LogicNets256槽、MCML4096槽，PBITS6、同序串行CPU8，各单次。

| 设计 | std::list / s | 槽索引双链 / s | 本次耗时下降 |
|---|---:|---:|---:|
| logicnets_jscl | 43.232 | 42.307 | 2.14% |
| vtr_mcml | 172.953 | 164.419 | 4.93% |

所有结果SHA及逐轮收敛匹配冻结串行参考。两布局的全部标签计数完全一致，因此并未以改变缓存替换顺序或减少实际工作换取本次时间差。完成审计复核实际输出、日志、计数、输入、源/二进制、原生证明及CPU/调度参数。原生ASan/UBSan包含独立std::list顺序与pin oracle（2/3/17/256槽各5000步），每步检查完整双向链、victim与全pin拒绝，另保留零页、值保存、RAII、reset拒绝与epoch回绕检查。

本次变体同时改变链接表示和队尾更新快捷路径，不能将收益单独归因到某一项。2.14%/4.93%均为一次原始耗时差，尚未补重复对照，不作稳定/统计显著性主张。减少std::list节点不代表已量得总RSS下降；当前标签报告未计入所有容器/分配器元数据，不能凭载荷计数宣称整体内存收益。

尽管相对resident基线改善，本轮两者仍明显慢于既有同调度原始CPU。所有实际拷贝仍同步，没有DMA/FPGA后端，不能宣称硬件加速；同输出沿用已有物理证据，MCML RTSTAT-10警告保留，未新增完整DRC/时序检查。

下一步对索引布局做三次受控配对，确认小幅收益是否可重复，并记录Frame/链元数据的实际对象容量；不扩大容量搜索。随后将标签查找从逐字段调用收束为安全作用域内的单次租约，或推进有限位宽设备协议，具体由重复证据和语义审计决定。旧基线和本轮源/二进制保持冻结。

证据：`resident_index_lru_pilot_20261023T001754Z/`。复核：`python3 scripts/report_resident_index_lru.py results/resident_index_lru_pilot_20261023T001754Z`。审计字段observed_off_reduction_percent沿用配对报告格式，此处表示index相对list的本次耗时下降，并非prefetch开关。
