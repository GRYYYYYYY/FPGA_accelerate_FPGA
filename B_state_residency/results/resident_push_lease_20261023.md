# push作用域租约：真实CPU先导

4/4完整运行及独立完成审计通过。基于冻结indexLRU/prefetch-on构建，只将push中lb/upstream/visited三个连续同节点写入合为一个局部租约；块在push计数、dump、递归扩展和队列操作之前结束。其他读路径未改。LogicNets256槽、MCML4096槽，PBITS6、同序串行CPU8，各单次。

| 设计 | 逐字段租约 / s | 合并写租约 / s | 本次下降 |
|---|---:|---:|---:|
| logicnets_jscl | 42.217 | 40.427 | 4.24% |
| vtr_mcml | 164.739 | 159.125 | 3.41% |

输出SHA和完整逐轮收敛与冻结串行参考一致；配对的全部标签计数相同，包括写回、换入、零页读取、初始化与reset。故本次未以改变路由结果、缓存替换工作量或放松pin安全换取时间差。审计重新读取实际结果、日志、计数，核验源/二进制/驱动快照/原生证明/输入及CPU/调度绑定。

原生ASan/UBSan通过：1000次实际push调用，外层固定另一页，检查三字段与prev保持、queue的id/代价、dump行为和函数返回后pin数；继承独立精确LRU顺序/pin oracle、零页、实际值淘汰保存、reset拒绝与epoch回绕。真实完整路由还验证lookahead递归路径保持输出，原生新测试的直接push调用仅使用lookahead=false，不能冒称专项递归覆盖。

源级每次push由三次acquire/release变为一次，均在相同页且无中间访问，因此减少重复页表/LRU/pin维护；这不是新硬件事务计数。此次时间差为一次先导，相对的是优化后resident index基线；没有统计显著性主张，整体仍慢于原始flat CPU。标签载荷、页表、全局状态、后备及元数据容量未变。

下一步固定两设计和容量做三次完整配对，确认该改动收益能否重复。稳定后再审计安全读取快照/作用域以减少其他重复访问；有限位宽协议、异步DMA及FPGA实现仍未完成，不能以CPU改动替代完整研究。原始及本轮基线保持冻结。

同输出沿用已有物理证据，MCML RTSTAT-10警告保留，本次未新增完整DRC/时序验证。

证据目录：`resident_push_lease_pilot_20261023T005319Z/`。复核：`python3 scripts/report_resident_push_lease.py results/resident_push_lease_pilot_20261023T005319Z`。审计observed_off_reduction_percent字段表示合并版相对逐字段版的本次耗时下降，不涉及预取开关。
