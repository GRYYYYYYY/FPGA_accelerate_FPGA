# G4最后primary owner释放后的warm恢复通过（2026-10-27）

详见同名JSON及hardware/variants/fourth_warm_v1/CONTRACT.md。选定fourth_warm_full_v2/pressure_v2，生产RTL逐文件SHA与正常fourth_system相同；仅TB接入G4源6/0/6、target7/1/7及图R错误。G4发布和首轮q4准备的原始native事件/周期与此前已归档正常例精确相等。

实际q4历史路径6954→990178→558358→265324→66893拆线后，990178 primary全零，另两节点refs3/4；已有三键journal。在搜索第一个图读取实际R握手注入SLVERR，原生search status8、1poll/1次失败展开/0candidate；TB成功展开计数0。query status7/detail8/committed0/route_acked0，未执行任何commit owner写。

原生G4/CP20 authority两轮GET返回990178 ref1/occ1、558358/net26422 ref4/occ2、265324 ref5/occ1。工作owner真实6GET+3INC：先读990178全零再原生创建net26422/ref1/occ1，另外两项3→4、4→5；corrected3，journal3保持至恢复成功。其他net23916/ref1、其他节点及满overflow池/allocator不变，无pool新增或回收。

恢复源是本实例实际G4原始导出：781标签/393页，前三路径加空第四槽156字，10字query。source path CRC f00b72b4/query327d3916，full标签083ee4ad、pressure ae573141，集合相同顺序不同。全部781记录实际写入并回读逐项验证；原始path/query数据与CRC直接交给原生恢复，转换至7/1/7。三种真实回执及服务退休齐全后，最终成功回复保持8周期仍封锁业务，消费后才允许工作。无外部cold reset或工作DDR重装。

序号语义必须区分attempt：原生query_lifecycle在受理时已把失败attempt6的last_sequence设为180330。target reset和授权rebase在新的attempt7根据原始G4镜像建立floor180329；不是手填序号，也不能称旧attempt未消费。恢复后先在空第四槽提交180329，原生status1拒绝、prepare_acked0、没有label/search/owner副作用；再登记q4历史元数据、原生ripup并以180330重试。此结论不证明跨attempt全局永不重放或持久化floor。

重试83poll/82expand/402candidate/231cost逐项CPU匹配，最终四路径保留。全部12AXI审计：copy/g3copy/labelsnap三个完整原始日志与已恢复参考逐字节一致，其余九路按本次事务独立重放，A区在实际退休边界前后分别使用G2/G4图像。37个owner record写逐字节核对，990178两次全零/两次重建均来自原生引擎；最终146284032B owner等于G4，全部781标签/393页/3MB物理标签DDR与CPU一致。

最终path CRC eec36b70、query CRC8a39d874/version7/flags5d/floor180330、slots15/CP20/journal3。结束4547230/4775002周期；故障至业务释放375301/291900周期，其中owner修复579/578，label恢复374180/290780，重试含导出387768/448040。全部是行为仿真，不是板卡时间或加速比。

两成功归档已实际恢复并重新审计，audit字节一致。首版full_v1只在编译时因TB数组声明晚于使用失败，没有运行仿真；移动声明后通过编译，生产RTL不改。编译失败例也已单独审计、归档恢复复审，不能称生产RTL反例。496文件源冻结results/fourth_warm_sources_20261027。

新增阶段统计fourth_warm_phases_20261027.json证明：781次baseline读取、3905次恢复字段写和总7810次native字段写。下一优先按restore_seed_bypass_v1/PLAN.md研究恢复整记录写的受限baseline seed跳过：默认关闭精确回归，开启时仍维持普通未知记录初始化、原始CRC/781回读/失败取消及退休封锁，再报告原生操作数和周期。该优化尚未实现，不能把本轮计数当优化收益。

仍仅一个确定图R错误点；任意故障/取消、任意变价标签有效性、持久化writer/认证/floor、全图baseline reseed、自然overflow新增回收、综合时序与板卡收益未完成。原始G1 clones/full baseline和历史路径元数据外部可信。每轮审计归档恢复后释放自身干净缓存，不删除证据。研究继续，goal active。
