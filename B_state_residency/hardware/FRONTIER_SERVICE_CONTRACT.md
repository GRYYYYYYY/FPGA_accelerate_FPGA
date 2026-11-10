# Frontier 查询服务（2026-10-24）

更新：当前使用 `hardware/variants/frontier_service_v3`。新增op5 **CLEAR**，仅active且query/price匹配可执行；等待真实HLS CLEAR完成，size归零但保留active/owner，用于搜索提前命中目标后的队列丢弃。与CLOSE释放owner不同，也与页checkpoint无关。其他协议相同。v3完整回归135157响应与七故障通过，综合3768LUT2297FF116BRAM、组合环0，未布线；下方v2数据保留为历史。[搜索接入契约](SEARCH_COST_AND_SCHEDULE_CONTRACT.md)记录必须先CLEAR再push目标的顺序。

实现：`hardware/variants/frontier_service_v2`。内部使用原样冻结的 `frontier_hls_relative_project_20261024` 生成 RTL，容量65536项，每项raw32位浮点key与32位id，8叉堆。所有端口在clk上升沿同步采样，rst为同步高有效；不能把组合fault的delta-cycle变化当异步事件。

## 冷复位与查询边界

原HLS仅FSM/FIFO控制复位，static size不随ap_rst清零。实际负例先入两项再复位，SIZE仍2，POLL返回旧id deadbeef。因此直接将ap_rst视作空堆不成立。

服务复位后禁止请求，自动调用真实CLEAR，等start被接受、四个输出各自有效、ap_done均收齐，且status=0/size=0/payload=0，才置initialized并开放req_ready。无需清零65536个payload；CLEAR仅隐藏它们。中断中的堆写入不回滚，协调冷复位后的CLEAR重新建立空堆边界。测试复位保持六个时钟周期；该复位必须同时清理整个服务/HLS及上游旧请求，不能独立热复位后接收旧事务。

OPEN/CLOSE也等待真实CLEAR完成。OPEN在成功响应可见时建立owner_query/owner_price，CLOSE在成功响应可见时释放；响应未退休前不接新请求。查询内部标签换页/checkpoint不得触发CLEAR；服务没有页checkpoint输入。外部搜索控制器尚未接入，必须将本服务的OPEN/CLOSE与pager/标签查询生命周期协调。不同price不可复用旧堆，只能关闭再开启。

## 接口

单未完成请求。req_valid/req_ready握手锁存op/key_bits/id/cookie/query/price；等待ready时发送方保持字段。response回显cookie/query/price并提供status/key_bits/id/size。响应在背压下稳定，req_ready此时为0。query2位、price4位；cookie32位仅关联回显，不提供跨复位防重放功能。所有id位保留，不在队列内限定图节点范围。

| op | 操作 | 条件 |
|---|---|---|
| 0 | OPEN | inactive；执行CLEAR后建立owner |
| 1 | OFFER | active且query/price匹配 |
| 2 | POLL | active且query/price匹配 |
| 3 | SIZE | active且query/price匹配；不清堆 |
| 4 | CLOSE | active且query/price匹配；CLEAR完成后释放 |

| status | 含义 |
|---|---|
| 0 | OK |
| 1 | EMPTY，POLL空堆 |
| 2 | FULL，OFFER容量65536已满 |
| 3 | BAD，不支持的op |
| 4 | INACTIVE，非OPEN请求没有查询 |
| 5 | OWNER，query或price不匹配 |
| 6 | BUSY，active时重复OPEN |

先判断BAD，再判断重复OPEN/INACTIVE/OWNER。本地拒绝不调用HLS、不改变堆。除成功POLL外key_bits/id为0；所有响应size为操作完成后的大小。本地镜像heap_size与HLS返回size/status及非POLL零载荷交叉核验。FULL/EMPTY为正常结果。

HLS既有比较语义保持：raw IEEE位整数解码比较，NaN无序、±0等价、负数/无穷/subnormal保留，不增加id作为平局键。新回归的满堆序列为唯一正浮点key；特殊值逐一单元素测试仅证明raw载荷不变，不能当作混合NaN排序证明。混合比较语义仍以已有Frontier helper/RTL cosim审计为证。

## 故障与限制

collector检查无归属输出、重复输出/完成、接受前事件，收齐全部四输出与done后才回复。MAX_CALL_CYCLES默认256，外层MAX_SERVICE_CYCLES默认512也限制等待HLS idle/collector请求；默认参数已测试，任意缩小参数不保证可用。ap_start不依赖ap_ready派生的组合fault，避免组合反馈。

abort、协议错误、超时或返回status/size/非POLL载荷不符会停止服务并保持必要owner；不会伪造成功响应。尚未提交的镜像不更新，但真实堆可能已经修改，不能原查询重试或解除fault继续。需要协调终止查询、复位并重新OPEN。同步采样时使用响应必须同时确认fault=0。fault之前已提供的响应保持稳定，可退休一次，但上层必须丢弃该故障查询结果。

没有热取消、并行查询、跨复位旧请求过滤、ECC纠错或底层heap数据完整性保证。错误SIZE/status的检测不能证明任意POLL payload正确。完整搜索尚未接入；没有完整路由/板上加速结论。

## 验证入口

- `scripts/verify_frontier_reset.py`：原HLS复位负例与显式CLEAR正例。
- `scripts/run_frontier_service.py` / `scripts/audit_frontier_service.py`：实际64K容量、全量排序出队、上下文拒绝、背压、192中断时刻、390成功boot；独立逐请求响应重放。
- `scripts/run_frontier_service_boundaries.py` / `scripts/audit_frontier_service_boundaries.py`：boot idle超时、丢失完成、错误status/size/非POLL载荷、执行中abort六场景，故障后冷复位恢复。
- collector：四输出+done的120全排列、同周期接受/完成、12故障场景。

v1与v2的RTL完全相同。v1 TB异步wait(fault)在delta-cycle暂态提前唤醒，125ns诊断可见实际完成，130ns检查早于135ns服务采样；v2改为下降沿采样。失败/诊断源码、日志均冻结保留，不修改HLS或放宽协议规则。
