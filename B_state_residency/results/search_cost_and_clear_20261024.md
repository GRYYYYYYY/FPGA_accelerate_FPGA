# 搜索代价拆分与查询内CLEAR（2026-10-24）

原CPU搜索在首次push时标记visited；命中可提前终止的目标时，先丢弃现有Frontier再push目标。这要求查询内CLEAR，不能用释放owner的CLOSE替代。已补齐Frontier v3，并拆出可独立验证的浮点代价阶段。

## Frontier v3

`hardware/variants/frontier_service_v3`新增owner匹配的op5 CLEAR，清空堆但保持active/query/price。`frontier_service_v3_20261024`及独立审计passed：135350请求/135157响应、390成功boot、192中断时刻、65536满容量全量入出、collector120排列/12故障。新增错owner CLEAR拒绝、非空/空CLEAR、保持owner与随后新目标入出检查。v2及原复位负例均保留。

`frontier_clear_boundaries_20261024`七故障passed，新例对非空CLEAR返回错误size：故障停止、保留owner与未提交的size镜像；真实堆已可能清空，不能原地继续，协调冷复位后为空。其余timeout/坏返回/abort六例用v3实际RTL重跑。

实际综合`frontier_clear_synthesis_20261024`审计passed：3768LUT2297FF116BRAM140CARRY8，DSP/URAM/latch=0，组合环=0。比v2增加8LUT，FF/BRAM不变。U280/OOC10ns；138输入181输出无IO delay、HD.CLK_SRC未设、未布局布线。MCP77.6s/exit0/checksumfba70535/history67，完整67573字节完成收据和DCP已保存。正常仿真96.574s/exit0/history65，边界12.944s/exit0/history66，全部终态。

## 浮点阶段

新增 `hardware/search/search_cost.hpp`：sharing、node/bias cost、partial、landmark heuristic和total。两种原价格/坐标读取路径保持不变，原CrossSLR整数几何保持不变；adapter保留所有TLD调用顺序与源码行号。该模块目前为CPU标量参考，尚未HLS化。

`search_cost_unit_20261024`及独立审计passed：262144组，golden直接提取原始参考源码的getNodeCost/getNodeCostSearch/evaluateCostAndPush，与candidate逐位比较partial/total（包括NaN payload）、prev、标签访问顺序、push child/lookahead。包含131072跨SLR、131072 landmark、131072前驱相关反向Y、65536 hot无锁路径；产生741 NaN、373 infinity结果。UBSan通过，未启用fast-math/FMA。几何fixture不含原函数可能发生INT_MAX+detour溢出的哨兵路径。

`search_cost_real_20261024`及独立审计passed：完整570286次真实CPU搜索、130334832次push，12轮收敛到overused0。路径result、全部搜索metadata、已采集标签访问二进制与children_real基线完全相同。访问采集有抽样，不能说全量标签访问逐条验证；完整路径和全部metadata确实逐字节一致。单次CPU耗时不用于性能结论。

## 调度证据及下一步

`search_schedule_20261024/audit.json`对全部搜索聚合：130334832 queue offers、48292082 polls、82042750 cleared，570286次搜索全部清掉过非空堆，峰值38638。逐查询offer=poll+cleared。全运行push与queue offer相等，说明这个配置未触发递归lookahead；不能拿它证明递归硬件正确。

后续按 [SEARCH_COST_AND_SCHEDULE_CONTRACT](../hardware/SEARCH_COST_AND_SCHEDULE_CONTRACT.md) 接入：先实际核实HLS浮点的舍入/特殊值，完成访问性与整数几何服务，再构建共享query生命周期的搜索控制器。源prev=-1、先CLEAR再push目标、visited在首次push时设置、prev更新会影响SLL坐标、page checkpoint不清堆、递归不能与未退休的父扩展抢单实例引擎，都需保持。最终还缺回溯/同网引用/occupancy/history提交、完整物理/平台/板上；目前没有完整FPGA路由加速结论。
