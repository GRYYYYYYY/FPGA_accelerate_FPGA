# 搜索代价的CPU/RTL数值一致性（2026-10-24）

已把代价算术实现为整数binary32运算，并验证实际生成RTL。原生HLS float版本存在可复现数值差异，不能作为逐位兼容实现。当前通过的版本是 `hardware/hls/search_cost/exact_v2`；接口和操作数字段见 [ARCHITECTURE](../hardware/hls/search_cost/ARCHITECTURE.md)。尚未连接实际搜索控制器。

## 原生浮点负例

`search_cost_native_hls_20261024`完成Csim/Csynth/RTL cosim，独立 `audit_search_cost_native.py` 的**数值准入失败**：

| 组别 | 向量数 | RTL不一致向量 | 不一致输出字 |
|---|---:|---:|---:|
| 普通范围 |4096|0|0|
| 特殊值 |144|33|82|
| 随机位模式 |512|101|201|
| 正常输入产生下溢 |24|24|48|
| 合计 |4776|158|331|

Csim逐位一致；cosim工具显示PASS是因为测试设计为跑完并记录全部结果，并不代表与CPU数值相等。所有observed文件、工具日志、生成RTL和独立差异审计均保存。不得仅按cosim状态把该版本接入搜索。

AMD [PG060](https://docs.amd.com/v/u/en-US/pg060-floating-point)说明了浮点IP对非规格化数等情况的限制；[UG1399 2022.2](https://docs.amd.com/r/2022.2-English/ug1399-vitis-hls/Optimizing-Logic-Expressions)说明浮点表达式优化控制。本地差异结论由实际返回字比较得到，不由文档推断替代测量。

## 整数binary32实现

`softfloat32.hpp`用整数实现add/mul/div/int32转换/比较及min选择；保留guard/round/sticky、最近偶数舍入、subnormal输入输出、signed zero、infinity。invalid结果取冻结SSE参考的ffc00000，NaN安静化并按明确操作数优先级保留payload。每个函数循环有固定上界，没有递归、动态分配、系统调用或原生浮点运算。

`exact_v1`软件门禁保留了一例双NaN不一致：case4390中partial与total保留的payload不同。反汇编确认CPU将第二个partial累加项放在目标寄存器，从而改变两个NaN时的payload优先级；`exact_v2`依冻结指令顺序调整交换律操作的操作数优先级，计算结合顺序和舍入点不变。NaN payload在任意C++编译器间一致不是本研究的保证。增加的576组双NaN组合来自独立扩展的原float oracle，其原4776组输出必须与初始producer逐字节相同。

软件primitive门禁：1000256对输入，5001280项add/mul/div/转换/比较检查，UBSan通过，本次未出现允许分类的双NaN payload例外。`search_cost_exact_cpp_v2_20261024`21000组合输入逐位一致（含16224真实样本）；v1失败源和日志不覆盖。

## 真实样本与全路由对照

`cost_capture_real_20261024`对完整CPU路由作纯观察采集。129764546次evaluate调用中，每8192次取一次，并取每轮前32次，共16224包，覆盖全部12轮。每包含23输入字与5个实际CPU算术结果。加入观察后，完整570286搜索、130334832push的路径、全部metadata、已采集标签访问均与原基线相同。

`search_cost_exact_real_20261024`进一步将同一整数primitive头文件通过薄wrapper接回完整CPU路由。独立审计通过：570286搜索、130334832push、12轮到overused0，路径/全部metadata/已采集标签访问字节相同。访问采集有抽样，且该证据并不是逐条记录所有代价值；不能说全129764546代价调用均已逐字比较。它验证完整路径和调度没有因此改变。该次CPU耗时只用于完成状态，不作为加速基准。

## 实际RTL数值门禁

`search_cost_exact_hls_20261024`及 `audit_search_cost_exact_hls.py` passed：

| 输入来源 | 数量 |
|---|---:|
| 普通范围 |4096|
| 特殊值 |144|
| 随机位模式 |512|
| 下溢 |24|
| 双NaN组合 |576|
| 真实路由采样 |16224|
| 合计 |21576|

host、Csim、实际RTL三路共核对每次5个输出字，RTL的107880字全部逐位一致。没有浮点容差，也没有把不同NaN bit pattern当作相等。HLS流程300.553s，完成收据在manifest，RTL协同仿真实际总10328294周期；调用延迟min224/avg477/max687，interval225/478/688。HLS报告估计LUT21024/FF6946/DSP20/零RAM，估计最坏711周期，**这些估计不能替代实际综合或布局布线**。

该门禁不是IEEE全输入空间的形式化证明，也不是完整设备路由。当前顶层仍为双读口/双写口ap_memory数组接口和ap_ctrl_hs，23输入、5输出；还需稳定输入保持、地址/重复写校验、收齐五字和done、故障/复位及query/price/cookie归属服务。

## 实际Vivado综合

`search_cost_synthesis_20261024` / `audit_search_cost_synthesis.py` passed：**7543 LUT、4791 FF、20 DSP、365 CARRY8、0 BRAM/URAM/latch**。LUTLP-1及check_timing组合环均0，no_clock与内部未约束端点0。U280/OOC10ns，66输入86输出无IO delay、HD.CLK_SRC未设，未布局布线。MCP115.262s/exit0/checksum5a1378c4/history68，完整57511字节收据、冻结生成RTL和DCP保存。8条warning为移除未用除法器结果/寄存器裁剪、常量端口、未满足并行综合条件和OOC时钟源提示，无Critical Warning/ERROR。

生成top的ap_ready与ap_done同在最终state23，输出双写口在state20/21已经写入。因此**不能直接复用Frontier collector的“ap_ready前不得有结果”规则**。未来包装必须从请求启动建立输出归属，允许done前分批写字，同时按地址收齐五字；不能让早写字变成无归属错误。输入双读口需要按实际ap_memory时序提供23字快照。这个观察来自冻结生成RTL，不代表包装已经实现或复位已验证。

下一步接入数值服务包装并完成原访问性/几何与搜索调度；页checkpoint保持Frontier/栈，目标CLEAR5与visited/prev更新顺序按 [搜索契约](../hardware/SEARCH_COST_AND_SCHEDULE_CONTRACT.md)。回溯、同网引用/occupancy/history提交、完整组合物理/平台/板上仍缺。原生float虽小，未满足数值准入；当前整数实现的面积/延迟需要后续基于完整链路测量决定优化，不能宣称端到端收益。
