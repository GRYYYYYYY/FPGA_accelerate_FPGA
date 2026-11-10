# 组合候选完整38查询与可复现源包

静态codec、6位目录epoch和记录专用响应直通组合已完整passed：38查询、28checkpoint、21466914命令、2472066页传输、0错误。自动workflow为composite_replay_audited；全部查询/checkpoint含时间收据、终态计数、结束时间与动态codec/epoch8记录直通全量一致。

相对无直通的小页动态基线，结束时间6246828510→6140213280ns，减少1.70670973%；38/38查询区间缩短，页载荷474636672字节及AXI计数不变。该差异属于端点实际值轨迹回放，不是完整布线或板上加速。

| 指标 | 小页动态基线 | 组合候选 |
|---|---:|---:|
| 布线后LUT | 14511 | 12396 |
| FF | 11159 | 11111 |
| BRAM / DSP | 319 / 3 | 303 / 3 |
| 内部WNS / WHS(ns) | 2.109 / 0.037 | 1.265 / 0.039 |

资源变化是整体配置取舍：静态codec和epoch位宽负责已有资源变化，记录响应旁路带来单独测量的周期收益及额外开销。不能将表中所有变化归给单一方法，不能由一次实现外推Fmax。

原生源包`hardware/candidates/native_epoch6_record/`已导出，含11个RTL文件、独立检查器、约束、相对路径重建脚本、证据和哈希。源包不含address64包装层。哈希验证、独立checkpoint与回绕仿真、全新目录综合均通过；重建为12434LUT/11115FF/303BRAM/3DSP，与原综合一致，Vivado综合校验和同为f2b53ce3。重建不读取原DCP、XPR或轨迹数据，原路径只在历史证据中保留。

复核入口：源包verify.py与validation.json；实验candidate_package_checkpoint/wrap/rebuild_20261024及audit_candidate_package.py。原全量结果source_bound_audit.json、query_comparison.json、cycle_comparison为终态证据。源包门禁通过不等于整体研究目标完成。

重要范围：38查询没有目录epoch回绕，epoch6长期清表频率高于epoch8。默认hash18的清表工作量每次262144周期；应按真实回收频率评估，不能仅为节省16BRAM忽略可能的长期代价。下一步需要更完整生命周期分布和位宽/清表成本比较。

当前仍缺平台外部IO/时钟预算、完整FPGA搜索/路由器和XRT/实卡验证。地址64包装层另有19查询/综合/物理证据，但尚未完整38查询，不能直接合并为“全部已验证平台”。
