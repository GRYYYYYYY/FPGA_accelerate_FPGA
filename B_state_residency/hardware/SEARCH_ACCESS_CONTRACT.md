# 可访问性与扩展决策状态机

已实现实际HLS的驻留调用控制器，见 [ACCESS_SERVICE_CONTRACT.md](ACCESS_SERVICE_CONTRACT.md)。下文为单步算法ABI；动态物理服务fabric和完整search仍未接齐。

`hardware/hls/search_access/v2/access_machine.hpp`实现**一个已过滤child**的决策，输入来自当前parent、child、sink和connection。顺序从visited开始，随后prune/dead、target、bbox和类型分支。它不实现首次getChildren过滤，不提交标签，不执行递归，也不调用Frontier。

输出action为0跳过、1常规push/入堆、2lookahead立即递归。bits中的EARLY只在最终target决策完成后触发查询内CLEAR，随后仍需prev、代价、标签写及push。AHEAD在图访问性拒绝前可能已置位，**必须以最终action为准**。

## 动态请求

| request | 值 | 返回内容与条件 |
|---|---:|---|
| DONE | 0 | 本child决策完成 |
| VISITED | 1 | child.visited；等于sequence则立即跳过 |
| TARGET | 2 | child.target；目标绕过普通bbox/graph/sink检查 |
| BBOX_END_Y | 3 | 原searchEndY(child)：hot模式用hot属性，normal模式用ns属性 |
| WILL_OVERUSE | 4 | 原searchWillOverUse(child,net)，仍由设计占用/同网引用服务提供 |
| SINK_TARGET | 5 | exclusive sink非target分支按原isAccessibleSink再次读target |
| COUNT_USER | 6 | 同net连接引用数；非零且pinbounce才允许借用该sink |
| CHILD_SLR | 7 | 原getSLRIndex(child)，按ns类型与动态endY查表 |
| SINK_SLR | 8 | 原getSLRIndex(sink) |
| PARENT_PREV | 9 | SLL→NON_LOCAL防返回：先读prev判断−1，再按原代码再次读prev |
| PREV_TILE | 10 | 使用第二次prev返回的aux节点，读取其ns.tileAddr |
| GRAPH_END_Y | 11 | 原getEndTileYCoordinate(child)，用于同X且Y差≤1的末级访问条件 |

NON_LOCAL_LEADING分支先请求sink SLR再child SLR；local-leading及LOCAL→Laguna的graph分支先child再sink。目标exclusive sink不请求WILL_OVERUSE，visited命中不请求target，关闭bbox不请求BBOX_END_Y。parent.prev两次读取没有合并。表/坐标服务已独立实现并验证，尚未连接此状态机；占用服务仍待实现，不能预先伪造布尔判断替代它们。

静态Config含sequence、flags、child/parent/sink type、childX/tile、sink tile/beginX/beginY及四个bbox边界。flags为prune1/dead2/useBBox4/north8/south16/parentLaguna32/childLaguna64/pinbounce128/hot256。类型沿原18项枚举；0..255其他值保留原default分支，≥256拒绝。metadata必须在首次children构建完成后取一致快照，保持到本child决策结束。

## HLS调用接口

`access_step`是显式状态、无隐藏持久状态的单步函数，ap_ctrl_hs和ap_memory：

- input[0]：0 START、1 ADVANCE。
- input[1..4]：phase、bits、aux、action（上次输出状态）；START忽略这些字段。
- input[5]：当前动态请求响应值。
- input[6..19]：Config，依次sequence、flags、childType、parentType、sinkType、childX、childTile、sinkTile、sinkX、sinkY、xmin、xmax、ymin、ymax。
- output[0..5]：status、phase、bits、aux、request、action。status0成功，1非法操作/phase/bits/action/config或对DONE执行ADVANCE，失败体全0。

初始phase1/VISITED；phase0/DONE结束。合法phase为0..18，bits低四位分别AHEAD1、IS_TARGET2、EARLY4、PRUNED8；action0..2。aux按阶段暂存SLR或第二次parent.prev。接收方维护完整状态，只能为实际pending request提交一次响应，不能跨child或查询复用。

该单步ABI本身没有query/price/cookie、服务超时或防重放；外层access_service现已实现拥有者、请求代号、快照及实际HLS协调复位。显式算法状态不意味着中断原HLS调用后可以接受残留写口；完整物理服务fabric仍须独立验证。

## CPU接入与验证边界

`adapters/build_search_access_router.py`替换原exploreAndExpand的每child判定，沿用原getChildren、evaluateCostAndPush和循环停止逻辑。直接TLD访问用原源码行号，坐标/SLR服务仍调用原方法；静态metadata可在visited之前读取，动态读取不提前。完整回归同时核对路径、metadata和已采集标签访问。

单元试验从冻结原CPU原样提取graph/accessible/sink/explore函数，覆盖18³类型组合×8上下文。记录动态label、SLR、endY调用顺序及结果，不把复制状态机的输出当作原函数golden。HLS中间状态向量由已完成此差分的执行轨迹生成。

lookahead测试目前证明决策，不证明递归硬件栈；真实CPU用例lookahead0也不能替代递归测试。SLL初始prev/分页默认0与前后坐标语义仍需设备服务验证。完整控制器必须保留target先CLEAR5、prev写后再计算几何/代价、首次push置visited、标签写成功后offer，以及checkpoint不清heap/栈。
