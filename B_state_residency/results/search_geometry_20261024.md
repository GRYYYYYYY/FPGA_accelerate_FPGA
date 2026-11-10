# 整数几何距离拆分与实际RTL（2026-10-24）

已把代价计算中的Manhattan、CrossSLR、相邻SLR绕行和Laguna柱选择拆成`hardware/hls/search_geometry/v1/geometry.hpp`，并接回完整CPU路由。输入/失败策略见[接口契约](../hardware/SEARCH_GEOMETRY_CONTRACT.md)。几何HLS及原代价服务仍是独立模块，尚未组合成完整搜索。

## 原始语义与溢出

原`dToNext < dToPrev && dAndFromNext <= dAndFromPrev + det`分支选next；比较不成立时最终fallback仍选next。prev分支同理；距离相等取总距离较小的一侧。因此detour比较不影响有定义输入上的结果，可以直接选最近可用柱，避免多余的哨兵加法。

原代码在只有next可用、prev哨兵为INT_MIN、det=1时，会计算INT_MAX+1。冻结原函数片段的O0/UBSan探针确实报出`1 + 2147483647 cannot be represented in type 'int'`。O2探针未报错，不代表源程序没有UB；本次以未优化构建的实际诊断确认这条溢出路径。

新实现用int64中间值，输出限制为非负int32；status1为两侧无可用柱，2为距离溢出，4为相邻SLR分支使用负SLL长度，失败时三个数值字均0。不能把这些返回当正常距离继续搜索；CPU适配会终止。此处定义了原UB/不支持输入的明确行为，不宣称与UB等价。

## 验证

`search_geometry_unit_v3_20261024/source_bound_audit.json` passed：9496组。8192组直接对照从冻结原CPU提取、未重写的几何片段，另150边界/1154极值组对照独立Python宽整数oracle。正常8604、缺柱188、范围671、负长度33。原定义域样例包括4095 cross、1820相邻SLR、910多SLR、910在柱上、470等距离、655 next更近、695 prev更近。

`search_geometry_hls_20261024/source_bound_audit.json` passed：同一9496组，Csim、cosim预检查和实际RTL后检查全部37984字一致。实际RTL固定latency9、interval10，总94959周期；HLS流程44.825s终态。HLS估计2081LUT439FF、7.288ns不能当映射后资源或物理时序。

`search_geometry_real_v2_20261024/source_bound_audit.json` passed：完整570286次搜索、130334832 push、12轮overused0，路径文件、全部metadata和已采集标签访问与`search_cost_exact_real_20261024`二进制一致。适配仅改整数计算，保留原坐标、SLR及Laguna读取、TLD顺序和行号；继续使用已验证整数binary32代价。CPU route98.602s只是本次运行记录，不作加速比较。访问采集为抽样，本真实配置不能覆盖CrossSLR与递归的全部语义。

## 实际综合

`search_geometry_synthesis_20261024/final_audit.json` passed：xcu280 OOC、10ns研究时钟，1145 LUT、408 FF、100 CARRY8，零DSP/BRAM/URAM/latch；LUTLP-1及check_timing组合环0。44.348s/exit0/checksum`a01e9cdc`/MCP history73，26688字节完整收据与DCP冻结。

66输入83输出没有IO delay，HD.CLK_SRC未设，未布局布线；存在层次布局提示。结果不证明10ns物理时序、完整系统资源或板上性能。

## 保留的试验问题

初次`search_geometry_unit_20261024`数值9496组通过，但runner要求优化构建必须报UB，该预期未成立。第二次`search_geometry_unit_v2_20261024`已在O0捕获原溢出，却因诊断文本操作数顺序与断言相反而判失败。v3只修runner的探针构建/文本核对，算术header、kernel、testbench始终相同；所有负例保留。

首次`search_geometry_real_20261024`在unit门禁未通过时停止，尚未生成源码或启动路由，目录保留PRECONDITION_FAILURE记录。通过unit审计后在新目录v2执行完整回归，没有覆盖旧结果。

## 尚待完成

原graphIsAccessible、bbox、pinbounce与target分支仍需硬件化；SLL动态endY在访问性与prev写入后代价阶段不同，需要保留阶段顺序，并补足初始prev/分页默认值的跨SLR验证。SLR/Laguna表读取、中心距离浮点运算、价格/引用服务仍未全部接入。

随后组合geometry与cost的请求快照/归属/复位，完整search控制器（首次push置visited、目标先CLEAR、递归栈、checkpoint保留heap/栈）、回溯与设计级提交，最后平台/布线/板上和端到端性能。现有组件通过不等于完整FPGA路由已完成。
