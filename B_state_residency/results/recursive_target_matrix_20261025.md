# 实际递归target/占用/共享三条件矩阵通过（2026-10-25，优先历史）

本轮在实际递归graph/metadata/access/native标签/geometry/cost/三ACK/OFFER链中完成3种target初态×32槽/单槽共6个主运行。机器汇总results/recursive_target_matrix_20261025.json，组合审计scripts/audit_recursive_target_matrix.py，实际恢复凭据recursive_target_restore_20261025.json。109份生产RTL/dat跨三条件逐SHA相同，本轮新增输入、TB与审计，不改生产RTL或旧已通过结果。

拓扑沿用明确合成逻辑0->{1,2},1->{2}，物理映射0,8,16,24,32，在33-node CSR中有28个无入边padding节点。目标标记设在逻辑2/物理16，而几何sink仍逻辑4/物理32；这是原算法target-marker条件测试，不代表已到达实际sink或完成连接布线。五条标签以实际host IO初始化prev=-1、node16.target=1，五个8-node页分开；heap另以fixture预置node24/key=3f800000。查询net0，资源CAPACITY=1。

| 条件 | owner主记录(key,refs,occ) | 查询net引用 | occupancy | 价格索引/值 | 共享因子 | EARLY/CLEAR | 祖先剩余兄弟 | node16 total bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| free 空闲目标 | (0,0,0) | 0 | 0 | 0 / 1.0 | 1 | 是 | 静态排空，无metadata | 4089999a |
| foreign 异net占用 | (2,1,1)，net1拥有 | 0 | 1 | 1 / 2.0 | 1 | 否 | 重新读visited77后SKIP | 40a9999a |
| shared 同net共享 | (1,2,1)，net0拥有 | 2 | 1 | 0 / 1.0 | 3 | 是 | 静态排空，无metadata | 40199999 |

owner key=net+1。shared将两个引用与一个占用net分开，不能把refs2当成occupancy2。foreign与shared均配置2个net，并保持cost.bin完全相同（price[1]=2.0），查询始终net0；free只配置1个net且未用的price[1]=1.0。不是单变量性能消融；所有几何、connection State、第一包成本完全相同，第二包23字输入只有count字段word1和实际price字段word4变化，其他21字逐位相同。没有收益、新颖性或路由质量提升结论。

CPU prepare_recursive_early.py / prepare_recursive_occupied_target.py / prepare_recursive_shared_target.py保持原Router递归/成本/标签push/8叉heap，新增成本与CLEAR前heap-size观测。去掉观测后逐字恢复既有observed Router；构造器/原State initializer保持，只在搜索前设定明确owner/target/price/seed初态。独立audit_*_inputs.py逐字段重建CSR/RRT32/设计/owner/成本/64B State/最终label，并逐阶段binary32重算每条件56个cost输入/输出字及CPU事件/POLL。原CPU fixture预置childrenCache，硬件从同拓扑CSR构建，因此仍只覆盖全部created、无复杂排除的构建条件，不是自然图动态过滤轨迹。

free/shared两组都验证：root(frame100,parent0)提交node8三ACK后立即下降；child(frame101,parent8)实际读取target16并判断不overuse，非空heap由seed-size1经CLEAR(status0,size0)清空。CLEAR回复严格早于node16.prev=8的native请求/ACK、parent upstream读取、实际geometry/cost、lb/upstream/visited三ACK与实际OFFER。node16全部三个成本ACK均保留target=1，parent8标签visited77/upstream3fa66666没有被heap CLEAR清掉。子OFFER成功后返回root，D日志显示remaining child16在controller NEXT_CHILD/early=1被直接消费，无第三次metadata/access/输出。只做2次候选判定，但静态expanded/raw计数仍3。

foreign两组相反：真实owner服务读出same-net refs0、occupancy1，目标被判overuse；没有任何CLEAR命令。实际prefetch使用price-index1/value40000000，目标成本total40a9999a；heap保留seed并达到size2。子树返回后root发起第三次metadata，实际VISITED返回77并SKIP。最终验证POLL按原CPU顺序先返回node24/3f800000，再node16/40a9999a及EMPTY。shared实际count2/occupancy1/index0/value3f800000，sharing-result40400000，total40199999（保留原逐步浮点舍入，不能替换成十进制2.4的另一个raw值）。free/shared CLEAR后只返回目标与EMPTY。

所有运行都把外部CLOSE和host label/design/owner请求排队在递归期间；围栏保持，内部CLEAR/OFFER仍可完成。每组2次实际递归扩展、2次成本/geometry、2次成本标签提交/6有序ACK、1次成本OFFER；seed OFFER另计。free/shared visited/metadata/输出各2次，foreign各3次；每组均消费3条静态children。最终checkpoint后五条完整160bit native记录（25字）与原CPU一致，node16.prev=8、visited77、target1，原其他节点状态保持；owner和history/price/net后备不被标签或heap操作清除。

主审计audit_recursive_early.py / audit_recursive_occupied_target.py / audit_recursive_shared_target.py核验完整事件顺序/ACK/成本/队列/全部AXI字节。各条件额外复用audit_recursive_join_backing.py：3145728B标签后备全部16384个192B页匹配原CPU五个已存在页和16379个全零页（允许分配器页位置置换），并有五个带node读回关联；每条件32槽/单槽最终labels.bin实际SHA也相同。证明文件recursive_early_backing_20261025.json、recursive_occupied_target_backing_20261025.json、recursive_shared_target_backing_20261025.json。

| 条件 | 32槽周期 | 单槽周期 | 32槽标签读突发/写回 | 单槽标签读突发/写回 |
| --- | --- | --- | --- | --- |
| free | 37127 | 38282 | 5 / 5 | 14 / 10 |
| foreign | 37288 | 38484 | 5 / 5 | 14 / 10 |
| shared | 37166 | 38285 | 5 / 5 | 14 / 10 |

每个标签突发3拍：32槽15读拍/15写拍，单槽42读拍/30写拍。周期只是仿真收据，不比较不同逻辑工作量的速度。free/shared的graph38读拍、design12读/2写拍；foreign graph44读、design13读/2写；各组owner6读、cost6读、State1读、table0读。owner640B和cost1280B完整保持。仍用FRAMES16384/INDEX14/HASH15与递归DEPTH4/CAPACITY32，只走两层，不是默认大目录综合或板卡可行性证明。

持久化：offer_archives_20261025下6个主包 early_inputs_v1、recursive_early_v2、occupied_target_inputs_v1、recursive_occupied_target_v1、shared_target_inputs_v1、recursive_shared_target_v1，共1395常规文件27171163B，逐成员和copy SHA核验。六个scratch目录全部实际移到.preserved后解包恢复1395文件；恢复后矩阵重新生成与原JSON逐字节相同。results的6个对应链接分别为recursive_early[_inputs]_20261025、recursive_occupied_target[_inputs]_20261025、recursive_shared_target[_inputs]_20261025；tmp丢失对索引运行restore_offer_result.py。最新MCP终态0/72.561s在recursive_target_completion_20261025.json。最初free v1普通检查已通过，v2只加D日志和drain计数断言、RTL不变；v1源/文本/log子集146文件235334B在recursive_early_history_20261025.*，不是主证明或大型binary的完整归档。

边界：owner refs/occupancy是显式初始快照，仅查询，没有更新同网多分支引用、增添其他net或触发overflow池（本例pool capacity0）。未证明真实网表自然搜索轨迹、复杂过滤、实际landmark/crossSLR、价格跨版本距离失效修复、实际满堆停止、联合故障排空/reset/reload、完整search/backtrace/owner提交或板上加速。下一优先任务从原真实CPU搜索采集可重放的递归事件、根前标签/owner/history和实际State快照，生成新递归oracle；不能把旧1216-parent无递归向量直接当新结果金标准。旧真实CPU矩阵及“原串行基线仍最快”等结论保持，研究goal active。

