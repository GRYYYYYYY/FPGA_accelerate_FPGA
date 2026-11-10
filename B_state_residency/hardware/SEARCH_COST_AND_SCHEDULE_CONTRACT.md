# 可访问性接入更新（2026-10-24）

[访问性状态机](SEARCH_ACCESS_CONTRACT.md)已完成原分支与动态读取顺序差分、实际单步HLS RTL和完整CPU回归；下方访问性尚待拆分的描述为历史。动态设备服务、pending归属、完整调度与递归/提交仍未完成。

---

# 最新接入状态（2026-10-24）

[代价服务](COST_SERVICE_CONTRACT.md)已完成实际核快照/归属/复位验证；[整数几何](SEARCH_GEOMETRY_CONTRACT.md)已通过原定义域/明确异常策略/实际RTL与完整CPU回归。下方“包装/整数几何尚待实现”为历史记录。原访问性、几何输入表与价格服务、两核实际组合和完整搜索仍未完成；原哨兵溢出不作为受支持语义。

---

# 搜索代价与调度接入契约（2026-10-24）

更新：`hardware/hls/search_cost/exact_v2`已通过实际整数binary32 RTL数值门禁21576组/107880字；原native float有158组差异，不能接入。整数primitive也接回完整CPU路由且路径/metadata/采集访问不变。实际综合7543LUT4791FF20DSP/零RAM/组合环，未布线；顶层仍需ap_memory快照/收集器与查询归属包装，不能直接用于完整搜索。详见[数值报告](../results/search_cost_numerics_20261024.md)。下方“尚无HLS证明”为拆分阶段历史，当前数值门禁已完成；几何/访问性/调度仍待接入。

`hardware/search/search_cost.hpp` 提供与原CPU顺序一致的纯标量浮点阶段。`build_search_cost_router.py`仅替换原函数内这些阶段，保留坐标/价格/同网引用服务、标签读写与原源码行号。`search_cost_unit_20261024`和`search_cost_real_20261024`已通过独立审计；目前没有此浮点算子的HLS/RTL证明，不能把CPU逐位一致等同于FPGA逐位一致。

## 代价输入与顺序

1. 查询级shareWeight及设计级同网连接引用count得到 `sharing = 1 + shareWeight * count`。count是同一net的连接引用次数，occupancy则按不同net计数；不能互换。
2. 原evaluate先写child.prev=parent，再读取parent.upstream，再计算nodeCost。SUPER_LONG_LINE的endY依赖prev与前驱的静态endY，因此代价阶段的childY可能不同于访问性判断时的childY；不可跨prev更新复用未经验证的坐标。
3. present price读取仍由原服务完成。normal模式同网已有引用时读occupancy−1；hot模式使用hot.occCnt且同网时以0下界防减法。历史hist始终从设计全局dyn读取，不能随query/标签epoch清零。hot.occCnt原本最多255的存储特性未在本helper重新定义。
4. `bias = base / connectionsSize * distanceToCenter / doubleHpwl`；`node = base * hist * present / sharing`；返回 `node + std::min(bias,node/2)`。connectionsSize和doubleHpwl在原接口均为int；distanceToCenter由原float中心坐标计算。
5. `partial=parent.upstream; partial+=node; partial+=rnodeWLWeight*length/sharing`。两个累加与内部乘除按原顺序舍入。
6. 原CrossSLR/Laguna整数几何产生distanceToSink，helper计算 `h=estWlWeight*float(distance)`。启用landmark时，8个u16差减1取正最大值，乘invScale；仅在alt>h时更新。最终 `total=partial+h/sharing`。

`std::min`的NaN选择规则不能替换成fminf，`if(alt>h)`也不能任意替换为浮点max。不得未经验证融合FMA、改为近似倒数或重排乘除/加法。raw IEEE特殊值检查包括NaN payload，但并非穷举所有float。HLS下一步须逐位/明确差异范围验证，尤其subnormal、signed zero、NaN、除零与溢出；不能默认工具生成的float IP与CPU完全相同。

几何仍是原CPU代码，尚未硬件化。unit fixture在有定义的整数范围内运行并通过UBSan；原函数可能求值INT_MAX+detour的Laguna哨兵路径未在本fixture执行、也没有修复。后续需明确可用柱/边界校验，不能把有符号溢出当受支持参考语义。

## 搜索控制器必须保留的行为

- 查询开始建立源prev=-1（paged标签默认0）、所有sink/altSink target，然后source的lb/upstream=0、visited=sequence并入队。ripUp在搜索前执行；旧设计级引用/拥塞要正确扣除，不能清成查询标签。
- 从队列POLL后先看target；命中后进入回溯。非目标展开其**首次过滤缓存**，缓存hit不重新过滤。
- 每个child先查visited==sequence，满足即跳过；再按prune查动态dead。该基线是在首次push就标记visited，没有对更好距离做decrease-key/重开节点。自行改成标准距离松弛会改变参考算法。
- target分支不走普通bbox/graph访问性。exclusive sink可提前终止；其他target根据设计级willOverUse决定。提前终止先执行**查询内Frontier CLEAR5**，再写child.prev、计算代价、写lb/upstream/visited并offer目标，最后停止当前子列表遍历。
- 非目标按原节点类型和bbox严格不等式判断，保留pinbounce同网通行、SLR方向、SLL返回方向和Laguna限制。
- push的lookahead=true分支立即递归exploreAndExpand，**不入Frontier**；false才offer。嵌套调用中earlyTermination是共享State字段，返回后各层都必须停止余下孩子。
- 当前扩展引擎是单未完成操作，不能在父扩展流尚未退休时递归启动另一个扩展。需要将父有序子列表完整接收（本图raw max18、接口max32），保存待遍历位置/上下文，再执行子展开，或采用证明等价的调度方案。需明确栈容量及溢出故障，不能静默截断或改为普通入队。
- labels写入成功才提交Frontier OFFER；FULL或服务故障必须使整个查询失败，不能保留visited后跳过该节点继续。目标CLEAR失败也不能继续计算/offer。
- query与price在整个搜索期间固定。pager checkpoint可以回收标签驻留页但必须保留堆与所有搜索栈帧；Frontier OPEN/CLOSE与pager生命周期由外部协调，尚未实现。
- 回溯沿prev直到−1，核验source后提交；同网多连接保留引用关系，设计occupancy/history独立于query标签。

## 本次真实覆盖边界

全部570286搜索：Frontier offer130334832、poll48292082、被CLEAR丢弃82042750，逐查询offer=poll+cleared；每次搜索均清除非空队列，峰值38638。全运行的push计数等于Frontier offer总数，原push分支只有递归或offer两种，因此这次配置lookahead push为0。该证据来自 `results/search_schedule_20261024/audit.json`，不表示所有图或跨SLR设计没有递归。

源码接口helper和Frontier CLEAR已完成；浮点HLS、整数几何/访问性硬件、完整搜索控制器、回溯与设计级提交、整体物理与平台/板上仍未完成。旧状态端点时间收益不能套用到此阶段。
