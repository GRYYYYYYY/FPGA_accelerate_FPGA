# 后续查询生命周期审计（2026-10-25）

采集logicnets同网sequence2，以及价格切换后的iteration2/sequence180327。两次完整原CPU路由结果保持原始hash；从准备态独立恢复实际Router搜索后，九份快照/事件逐字节相同。逐候选标签时序、原8叉heap、全9089009节点持久状态检查通过。没有新增RTL或板卡结果。

| 准备态字段 | 同网query2 | iteration2首query |
| --- | ---: | ---: |
| 旧visited节点 | 171 | 2467619 |
| 非默认prev节点 | 171 | 2439660 |
| history>1节点 | 0 | 50416 |
| 多net占用节点 | 0 | 50416 |
| overflow引用记录 | 0 | 53734 |
| children缓存parent | 72 | 1647675 |
| children缓存child条目 | 271 | 7582190 |

独立审计每个节点occupancy恰等于主owner是否存在加overflow不同net数，owner空值与引用数一致，缓存记录边界及节点范围正确。overflow只在输出副本排序，不改变原Router容器或搜索行为。全部缓存顺序和标签由真实搜索重放进一步验证。

首query搜索末态到同网query2准备态，全9089009行中只有9行变化，精确等于首路径6个内部节点owner提交、旧target清除、新target置位、source距离/visited初始化。路径为150697→1411724→3919432→2988027→1431200→554512→263946→65185；源/汇不重复提交占用。两个准备态价格表相同；iteration2 present factor由0.5变为1.0。

这验证了跨查询恢复所需的真实旧状态，不证明旧距离仍然有效，也不证明将旧prev清零会在这些查询改变路径。当前RTL首次查询codec仍拒绝warm cache/overflow；CPU oracle预知标签工作集的限制仍在。下一步将持久prev/owner/history/children与query有效距离标签分开定义，扩展warm/overflow codec和按需页初始化，再进行多query硬件闭环。旧prev在isPartOfExistingRoute中参与判断，不能在没有等价性证明时直接以0代替-1或全量清除。

证据：followup_lifecycle_20261025.json，scripts/audit_followup_query.py、analyze_followup_lifecycle.py；独立实际搜索重放沿用run/audit_natural_query_replay.py。完整原路由hash与搜索重放不是硬件成本独立证明或加速结果。

四份采集/重放归档均已将原scratch移至.preserved后实际解压恢复，逐文件hash核验通过；恢复后分析JSON逐字节一致。收据followup_restore_20261025.json，代码冻结followup_sources_20261025。run.py check通过（仅文件/配置/来源可用性）。
