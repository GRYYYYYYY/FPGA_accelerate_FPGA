# 首个自然查询RTL闭环搜索通过（2026-10-25，优先历史）

实际Vivado2022.2 XSim在已有B MCP会话 vivado-20261023-140925-d95d4d2b（PID147904）完成32槽/单槽两次主运行，exit0/166.75s。结果 results/natural_query_rtl_v1；机器汇总 natural_query_rtl_20261025.json，终态收据 natural_query_rtl_completion_20261025.json，独立审计 audit_natural_query_rtl.py + audit_natural_axi.py。本轮只加测试台/运行/审计，109份生产RTL/dat与既有通过基线逐SHA一致。

输入仍为真实logicnets首查询：connection_index16506/id37267、net2717、source65185、sink150697、sequence1，实际bbox与64B State、owner/history/价格保持。全图9089009节点/40469536边来自已审计原CSR/RRT32，不改成小图，不设置合成占用或target。host接口实际逐字段导入308条字面标签，再将原prepare已seed的source以实际heap OFFER入队。query/price/version=1/3/3和design_id为TB身份编码，不是从CPU推断的价格版本；实际price table/present-factor保持CPU快照。

新TB hardware/variants/natural_query_v1/tb_natural_query.sv（build_tb.py生成）让actual heap POLL返回node成为下一次expand_parent，每次POLL后通过真实host label读target位来决定停止。CPU P/C/cost文件只作断言评分，不供应下一parent或候选。POLL→实际graph/design首次过滤→metadata/access→geometry/cost→native提交/三ACK→actual OFFER→target EARLY内部CLEAR均通过现有实际链；外层POLL/扩展调度目前是TB顺序逻辑，不是新增可综合的自主search controller。仍未执行backtrace/saveRouting/owner commit/target cleanup。

两配置各73次真实POLL、72次扩展、271次metadata/access/visited判定、171次实际geometry/cost、171组成本提交/513有序ACK与171次成本OFFER；source种子OFFER另计。382条原始边与271条候选的顺序等于原CPU，自然目标出现一次EARLY，实际内部CLEAR使用frontier op5（op3是PEEK），然后目标以40267287出队并停止。关闭前对308条完整native记录逐字检查。整个扩展期间同时排队CLOSE和host label/design/owner请求，围栏保持，内部CLEAR/OFFER继续完成。

完整持久状态独立审计：145424192B design结果与原CSR、CPU逐候选时刻标签/created及过滤重新推导的全部字节一致；72个缓存发布、202个新created。CREATE对24个raw已created sink也设置冗余store.created位，这是幂等getOrCreate的实际结果，不是新建计数24；运行时created始终raw OR store。主owner+allocator145424256B及cost36804480B保持；全部物理标签3145728B的16384个192B帧匹配原CPU308记录分布的111有效逻辑页+16273零页（允许分配帧置换）。两配置物理labels.bin SHA实际相同04fa55e4283c1d4d5c56c3b977b1c97265dd2cddf5bc423d3728e9fd7015629d。

| 配置 | 仿真总周期 | 标签AR事务 | 标签读拍 | 192B页读 | 写B回复 | 标签写拍 | 192B页写 | State读拍 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32槽 | 430263 | 257 | 747 | 249 | 188 | 549 | 183 | 72 |
| 单槽 | 470003 | 802 | 2364 | 788 | 387 | 1143 | 381 | 72 |

页大小192B，跨4KiB边界时三拍页拆为2+1或1+2，故不能将AR事务/B回复乘3当总拍数。32槽读burst长度3/2/1分别241/8/8，写178/5/5；单槽读774/14/14，写375/6/6。新audit_natural_axi逐实际地址/长度验证4KiB分割、后续页片段、完整每拍与WSTRB及最终全文件，不改旧小用例已通过审计。上述周期包括host初始化、POLL标签观察、检查点和最终读回，不是纯搜索计时或板上加速。

两组其他实际总线流量相同：graph4685读拍、design1068读/298写拍、owner422读、cost513读、connection State72读，table0。State72次×64B与72个parent对应，是后续query级驻留的实测仿真流量基线；不能现在就声称省71次后能带来多少速度。32槽面对111页也会驱逐，不是全驻留上界。目录仍FRAMES16384/INDEX14/HASH15，递归DEPTH4/CAPACITY32；本自然输入lookahead0，不增加递归覆盖。

初次辅助审计先后暴露旧假设：CLEAR opcode应为5而非3，design.created位允许对raw创建冗余设置，标签页跨4KiB会拆突发。按既有生产代码和真实事务修正独立模型后所有严检查通过，未改生产RTL或重新运行以躲避失败。两份未通过审计源码及最终审计/辅助/TB生成器已固定在 results/natural_query_rtl_audit_sources_20261025（manifest逐SHA绑定）。唯一编译警告为旧axi_file_memory输出计数初始化VRFC10-8426，无错误/fatal；不是时序/综合结论。

归档 results/offer_archives_20261025/natural_query_rtl_v1.tar.gz：433常规文件/10579578B压缩，逐成员与共享盘copy SHA核验。实际移走scratch到.preserved后解包433文件，重新汇总逐字节一致；恢复凭据 natural_query_rtl_restore_20261025.json。原始图、natural_query_inputs_v1与natural_query_oracle_v1依赖需按既有索引保持。普通run.py check也通过，但仅证明配置/文件可用，功能证据是本次RTL审计。

下一优先任务：在新隔离RTL variant实现每query/connection State驻留，使本自然查询72次重复State读取减少，并保持全部输出/heap/native/design/owner/cost不变；缓存命中必须核验query/price、完整version/design、connection/net/sink/cross、profile revision，不能把新State缓存误作距离标签有效性。切换连接/版本/生命周期应明确失效或拒绝，补负向身份测试。用同自然输入/同TB计数和公平搜索窗口比较，保留本基线。随后将外层search loop移入可综合控制器、实现backtrace与owner提交，扩至多查询/MCML/跨价格有效性及板卡。当前仅一个自然query，goal active。

