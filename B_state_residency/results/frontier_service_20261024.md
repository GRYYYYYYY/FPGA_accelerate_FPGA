# Frontier 复位与查询生命周期结果（2026-10-24）

已实现 `hardware/variants/frontier_service_v2`，把实际64K HLS优先队列接到带启动CLEAR、OPEN/CLOSE、query/price归属、稳定响应和故障停止的串行服务。尚未与完整搜索控制器联接。接口见 [FRONTIER_SERVICE_CONTRACT](../hardware/FRONTIER_SERVICE_CONTRACT.md)。

原始HLS有真实复位缺口：先放入两项再施加ap_rst，SIZE仍返回2，POLL返回旧id deadbeef。`frontier_reset_20261024`保存该负例和显式CLEAR后的EMPTY正例，9调用，MCP14.103s/exit0。其status=passed表示成功复现缺口，不表示原HLS复位安全。

新服务在每次协调冷复位后先完成真实CLEAR再开放请求，查询OPEN/CLOSE同样等CLEAR完成。不重置整块payload RAM，不改原HLS比较语义。设计级占用/历史拥塞与此查询级堆仍是不同生命周期；页checkpoint不能触发堆CLEAR。

## 验证

`frontier_service_v2_20261024`及独立 `scripts/audit_frontier_service.py` passed：

| 项目 | 实测 |
|---|---:|
| 外部请求 / 响应 | 135343 / 135150 |
| 复位中取消、未产生响应的请求 | 193 |
| 完成启动CLEAR | 390 |
| 复位断言（含一次中断boot） | 391 |
| 实际HLS接受次数 | 135727 |
| 实际容量 | 65536 |
| OFFER/POLL中断时刻 | 各96，共192 |
| 正常FULL / EMPTY响应 | 1 / 198 |
| 成功POLL | 65738 |
| 模拟周期 | 6033329 |

全容量使用唯一正浮点key，逆序插入65536项并完整排序弹出；另有±0、正负subnormal、±infinity、正负NaN和±1的单元素raw位保留检查。单元素特殊值测试不等于混合NaN排序证明，混合比较语义仍依据原Frontier helper与RTL cosim。重复OPEN、inactive、错query/price、未知op、非空CLOSE、新查询空堆、背压和晚到abort均验证。

每个OFFER/POLL中断测试先填16项，分别在接受后0..95周期协调复位，重新OPEN必须EMPTY，再入/出新id42不得泄漏旧结果。另测非空空闲堆、未退休CLOSE响应和boot中断。独立Python审计逐请求/响应重放操作、归属、容量、size、key/id、cookie，完整满堆序列用独立heapq核对，不复用HLS 8叉堆实现。

collector单独覆盖四输出+done全部120排列、接受当拍全部返回、背压以及12错误场景。服务层单独 `frontier_service_boundaries_20261024` 通过六组故障注入：等待idle超时、完成丢失、错误status、错误size、错误非POLL载荷、执行中abort。全部停止准入且不错误提交镜像，协调冷复位后恢复；真实堆可能已有部分修改，不允许原地解除fault继续。

主回归MCP95.853s/exit0，边界12.7s/exit0。v1及诊断失败是TB使用异步wait(fault)捕获delta-cycle暂态；v2只改稳定下降沿采样，所有RTL与collector TB保持字节一致。负例与诊断目录、完成收据保留，不能把旧manifest的running字段当后台仍运行。相关工具全部已终态。

## 实际综合

`frontier_service_synthesis_20261024`及 `scripts/audit_frontier_service_synthesis.py` passed。Vivado2022.2、U280、10ns、OOC，实际资源：

| 资源 | 用量 |
|---|---:|
| CLB LUT | 3760 |
| FF | 2297 |
| BRAM Tile | 116 |
| CARRY8 | 140 |
| DSP / URAM / latch | 0 / 0 / 0 |

相较原独立Frontier实际综合3411LUT/1794FF/116BRAM，新服务增加349LUT、503FF，BRAM不变。该差值是整个新顶层的综合差值，不能据此分解精确控制逻辑面积。

LUTLP-1与check_timing组合环均0，no_clock与内部未约束端点0。138输入/181输出没有IO delay，HD.CLK_SRC未设，未布局布线；原裸Frontier的布线时序不适用于新顶层。MCP77.561s/exit0，checksum5f5be8ff，history64。完整67,654字节完成收据、冻结源、报告、DCP均保存。32条warning包括28个未用端口、2个寄存器裁剪、1个不满足并行综合条件及1个OOC时钟源提示，没有Critical Warning/ERROR。

正常manifest SHA：370608d7bdec324e0524421bba4e1ef1dda4ff418c87e81073ef51bd37bb0874。
边界manifest SHA：c1f0e24b3425f2846408ec52ebfeb8f19eed58162905183f87d1c52ed27d9a01。
原复位负例manifest SHA：cbe00187696173004b5c160ed3f4cfdfe12783753539441da9fbb0cca2cc49b2。

下一步接原CPU距离/代价与可访问性/目标判断、查询source标签初始化、Frontier与实际扩展引擎调度，随后回溯/同网引用/设计占用与历史拥塞提交。需要明确pager与Frontier共同OPEN/CLOSE和错误终止，页checkpoint保持堆。当前不是完整FPGA搜索/路由或板上实测加速；旧标签端点的9.5213%不能套用于此结果。
