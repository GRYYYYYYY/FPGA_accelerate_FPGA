# 实际RTL递归汇合联合用例通过（2026-10-25，优先历史）

这次真正执行了后代的graph/metadata/access/native标签、geometry/cost、三项标签ACK与实际OFFER，不再只证明mock调度或无action2前缀。主结果results/recursive_join_20261025（recursive_join_v1）完整32槽/单槽均通过；输入results/recursive_join_inputs_20261025（join_inputs_v1）。CPU/接口生成prepare_recursive_join.py，输入审计audit_recursive_join_inputs.py；运行run_recursive_join.py，主审计audit_recursive_join.py，额外完整物理标签语义审计audit_recursive_join_backing.py。综合收据recursive_join_revision_20261025.json。

图是明确合成：逻辑0->{1,2},1->{2}，五个逻辑节点映射到物理0,8,16,24,32，坐标仍0..4，sink坐标4，33节点CSR含28个无入边padding节点。这样五个显式初始标签处于五个8-node页，单槽确实触发驱逐/重载。所有标签先用实际host native写prev=-1，以匹配原dense CPU初态；不是默认稀疏absent-prev=0的测试。所有类型NON_LOCAL，root Laguna，非crossSLR，landmark inactive，owner占用0、history/price均1、net center0/fanout1/doubleHPWL10。没有修改任何共享或原始基线。

CPU使用前轮完整原Router立即递归类/实际成本/原push/原heap；去掉新增纯cost观测后逐字恢复前轮observed source，构造器与State initializer保持，非cost事件与原5节点金标准逐行相同。原CPU fixture预先提供childrenCache；硬件从同拓扑原始CSR建立缓存，因此本例验证的构建条件是全部已created、无排除的简单条件，不代表复杂过滤/新建状态的递归组合已覆盖。RRT32、CSR、design/owner/cost、64B connection State及最终label镜像经独立逐字段重建；56个cost23输入/输出字还以逐阶段binary32重算。不是自然器件路由轨迹。

实际顺序：root(frame100)处理node8并提交lb/upstream/visited三ACK，action2退休后才启动child(frame101,parent8)；child处理node16并提交三ACK，然后实际OFFER(node16,total=0x4089999a)，成功退休后才恢复root对node16的metadata。此时真实VISITED读返回77，root以SKIP退休，没有重复入队或重新成本计算。主auditor检查E→seal→M→O→子E→子seal→子M→六次有序W/A→OFFER→子O→父M→V(77)→父SKIP及全部payload，明确区别于延后递归。

关键最终标签（物理ID，映射后的原CPU结果）：

| node | prev | upstream bits | total/lb bits | visited |
| --- | --- | --- | --- | --- |
| 8 | 0 | 3fa66666 | 406ccccd | 77 |
| 16 | 8 | 402ccccd | 4089999a | 77 |

node16成本输入里的parent upstream确实为node8刚提交的3fa66666；prev=8证明外层当前parent接线进入了实际postprev/commit。checkpoint后五条完整160bit native记录（25字）与原CPU一致，node0/24/32仍prev=-1且未visited。随后两次验证POLL返回node16/4089999a和EMPTY，再CLOSE；这些POLL是验证fixture，不是已实现的完整搜索循环，也没有到达sink32或完成回溯/占用提交。

两组各2个真实扩展、3次metadata/判定/visited读、2次实际geometry+cost23、2次成本标签提交/6有序ACK、1实际OFFER。实际root/descendant frame context及连接State通过原已验证组合；109份既有RTL/dat全部同SHA，本轮只换输入和TB，不改已验证递归core/top。TB在整次递归期间排队外部CLOSE以及host label/design/owner请求，全部被围栏挡住；内部OFFER仍完成，实际CLOSE只在最终验证后发到heap。因此覆盖了正常递归时queued-CLOSE与内部OFFER共存，不是故障恢复证明。

内存独立审计：graph44读拍/全1344B源镜像，design13读拍/2写拍/576B最终缓存状态，owner4读拍/640B与cost6读拍/1280B源镜像保持不变，connection State1读拍/64B，table0读。完整标签3145728B逐读拍/字节写掩码/B日志重放；另按原codec的bitmap8+8×160bit记录+zero tail，从CPU五条最终记录独立编码，全部16384个192B物理页多重集匹配5个有效页+16379个全零页，并以五个带node的native读回验证关联。额外证明是results/recursive_join_backing_20261025.json，不覆盖已归档的主审计。

32槽标签5个读突发/15读拍、5个写回/15写拍；单槽13读突发/39读拍、9写回/27写拍。不可把AR事务数与burst beat数混用。两组最终labels.bin SHA均为7605ac01a9c4462c48fed6e3a005d14fc1718323f40eb04eb54baa1292d9a374。周期37242/38150仅仿真收据，非加速指标；仍用FRAMES16384/INDEX14/HASH15、递归DEPTH4/CAPACITY32，只走两层，不证明默认大配置资源可行性或深度边界。

B原MCP同进程72.965s/exit0，receipt recursive_join_completion_20261025.json。两个主归档在offer_archives_20261025：join_inputs_v1为35文件693729B，recursive_join_v1为429文件8349727B；压缩成员与共享盘copy SHA验证，真实联合结果已移开scratch到.preserved后恢复429文件核验。restore_offer_result.py恢复原路径；tmp丢失需同时恢复输入和结果。先前所有通过的基线/失败记录保持。

下一步补带target EARLY与预置非空heap的真实递归用例：在原CPU逻辑node2置target并在其queue预置node3，使子树EARLY实际CLEAR先于prev/cost/标签/OFFER，root未处理兄弟应排空而不进入metadata，target位必须跨三ACK/驱逐保留。然后再扩至原真实图的新递归CPU轨迹；旧1216-parent无递归oracle不能直接沿用。非零owner/ref、复杂children过滤/多net生命周期、真实landmark/crossSLR、实际满堆停机、联合故障排空/reset/reload、完整search/backtrace/occupancy提交、综合与板卡性能仍未完成。研究goal active。

