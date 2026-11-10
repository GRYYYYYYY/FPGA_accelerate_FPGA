# 访问性驻留控制服务（access_service_v1）

本模块接受一个已经完成首次 children 过滤的 child，快照 Config14字、parent/child/sink/net编号、query2/price4/cookie32，然后在设备内反复执行实际 `access_step` HLS 和动态服务请求，直到产生最终跳过/普通push/lookahead决策。算法条件及单步ABI见 [SEARCH_ACCESS_CONTRACT.md](SEARCH_ACCESS_CONTRACT.md)。本模块不写标签、不提交路由、不操作Frontier，也不执行递归。

## 驻留状态和调用

`req_config[32*i+:32]` 对应原HLS input[6+i]，14字依次为 sequence、flags、child/parent/sink type、childX、childTile、sinkTile、sinkX、sinkY、xmin/xmax/ymin/ymax。START时其余六输入字清零。每次ADVANCE把上次phase/bits/aux/action和实际服务值组合成20字，Config保持不变。输入握手后外部可修改请求口，不改变此次快照。

`access_memory_call` 用同步一拍双读口供给实际HLS，收集六个唯一输出地址，允许done之前写出。所有六字收齐且ready/done同时有效才交给控制器。非法地址、重复/冲突写、无归属访问、缺字/握手错误均停止。完成与最后允许周期的超时相遇时，完成优先。

每个实际HLS调用和动态服务请求各分配一个全局单调token。默认32位；到上限后停止，不能回绕。一个child内的Config和算法状态不经主机往返；当前动态服务端口是待接设备后端的硬件请求/响应接口，不是软件调用承诺。

## 动态服务接口

svc请求包括kind4、phase5、node/net32、token32、query2、price4。响应必须逐字段回显身份，并提供status4和值32。只有已接受的请求可在后续周期返回，服务不得在请求尚未握手时返回响应；最多一个在途请求。请求在ready背压期间稳定。实际次序由HLS决定，不得提前推测标签读取。

| kind | 对象 | 后续实际后端映射 |
|---|---|---|
| 1 VISITED | child | 分页标签 field3 |
| 2 TARGET / 5 SINK_TARGET | child | 分页标签 field4；第二次读取不合并 |
| 3 BBOX_END_Y | child | 坐标服务 ENDY；hot/ns快照一致性仍需上层保证 |
| 4 WILL_OVERUSE | child, net | 设计级占用和同网引用服务，尚未接入 |
| 6 COUNT_USER | child, net | 同net连接引用数服务，尚未接入 |
| 7 CHILD_SLR | child | 坐标服务 SLR |
| 8 SINK_SLR | sink | 坐标服务 SLR |
| 9 PARENT_PREV | parent | 分页标签 field2；保留原条件下的两次请求 |
| 10 PREV_TILE | 第二次prev返回的aux节点 | 坐标服务 STATIC 的tileAddr，后端需验证节点范围 |
| 11 GRAPH_END_Y | child | 坐标服务 ENDY |

服务端必须按真实状态返回值，不能用预设布尔数代替物理实现后的占用查询。当前功能试验从已经与原CPU逐条件/顺序对照的冻结轨迹返回动态值；这不证明上述物理后端已接入。

## 完成和故障

响应回显输入身份、status4、bits32、action32、完成的HLS步数和服务数。action0跳过、1普通push、2立即lookahead递归；AHEAD可能先设置后被拒绝，不能代替action。EARLY触发后续target清空Frontier顺序，但本模块自身不执行CLEAR。

| status | 含义 |
|---|---|
| 0 | 完成；还必须检查fault为0 |
| 1 | 请求时inactive，可恢复且不调用HLS |
| 2 | 请求query/price不符，可恢复且不调用HLS |
| 3 | HLS或动态服务返回错误，包括非法Config；停止 |
| 4 | HLS或服务回显身份不匹配；停止 |
| 5 | abort、下游fault、无归属响应、owner变化或整体超时；停止 |
| 6 | token耗尽；停止 |
| 7 | HLS状态/请求编码不一致；停止 |
| 8 | 非终态步数达到MAX_STEPS；停止 |

默认MAX_STEPS32、单次HLS上限64拍、整体上限8388608拍。整体计时包含调用、服务和下游背压，但不包含已暴露最终响应后的消费者背压。有限步数是异常保护，不改变正常状态机顺序；功能轨迹全部正常终止。

active/query/price必须保持到最终响应退休。已给出响应的字段遇迟到故障仍保持，fault会锁存；消费者必须同时检查fault。错误响应里的计数/数据可能仅是部分进展，不可用于提交。复位必须同时覆盖实际HLS、控制器、服务端并清除旧事务；不支持独立局部复位后继续消费旧响应。

上层必须在整个child判定期间独占相关标签/坐标上下文，禁止host标签写、OPEN/CLOSE和版本切换插入。该模块只监测active/query/price；共享物理端口的仲裁和事务排空仍由后续fabric负责。分页CP可由内部服务完成并保持语义，不能清heap/递归栈。

## 验证范围

`access_service_20261024`：46656child、195175实际HLS调用、148519动态请求，全输出/顺序及11类请求独立审计通过。Config和节点口在握手后故意改写，驻留快照仍正确；动态服务与最终响应都施加背压。

`access_boundaries_20261024`：collector720排列、18错误和完成/超时同拍；实际HLS+控制器122检查、96逐周期复位位置、217次复位，含实际token3耗尽、128拍超时、错误回显、迟到故障及超时之外的140拍响应背压。服务响应由测试模型提供。完整搜索、物理服务fabric、递归执行、回溯/占用提交与板上仍缺。
