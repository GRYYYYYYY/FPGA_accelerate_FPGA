# Frontier 容量与组件验证（2026-10-24）

真实完整CPU路由共570286次搜索、130334832次push，frontier峰值中位114、p90为253、p99为671、最大38638。64K×8B的逻辑payload为512KiB，覆盖当前轨迹；未来设计仍需FULL处理及查询回退。

普查保留原路径结果、全部搜索的原有元数据字段，以及原已采集的标签访问二进制样本。随后将固定容量8叉helper接回完整CPU路由，同样通过核对。两者均有独立source_bound_audit.json。采样访问一致不能替代未采集访问的逐条核对。

C++浮点golden与整数IEEE key比较候选各通过135228条命令及1000169组比较，包括64K实际填满/拒绝溢出/排空、空队列、clear、非法操作、NaN、无穷、正负零和次正规数。相同helper已进入全设计CPU路径，尚未接入设备图扩展、标签页和完整搜索控制。原CPU已保留heap backing且clear为O(1)，此组件不构成初始化收益证据。

首次HLS在open_project阶段因绝对路径工程名失败，保存在frontier_hls_20261024。恢复目录frontier_hls_relative_project_20261024只修正Tcl工程打开方式，核心源码不变，实际HLS2022.2、U280、10ns；按Csim→Csynth→完整容量RTL cosim执行。运行状态以manifest和阶段收据为准，审计入口scripts/audit_frontier_hls.py。综合估计不能解释为布线后或板上结果。

证据目录：frontier_real_20261024、bounded_frontier_real_20261024、frontier_cpp_verified_20261024。架构说明：../hardware/hls/frontier/ARCHITECTURE.md。

综合已完成，RTL协同仿真正在运行。生成的两个AUTO RAM各65536×32bit、16位地址，容量未裁剪。HLS报告的32 BRAM_18K不能直接作为512KiB的物理存储结论；后续需Vivado实际综合确认BRAM/URAM映射。综合时钟估计也不等于布线后时序。

## RTL终态

恢复版Csim、Csynth、完整135228调用的RTL协同仿真均passed，独立源码绑定审计passed；实际64K填满/拒绝/排空保持一致。1000169组比较是TB比较器核对，不能解释成等量独立RTL比较调用。HLS总耗时213.93s，XSIM终点49783975ns不是完整路由或平台性能。生成15个RTL/初始化artifact全部绑定。

下游实际Vivado OOC综合已在既有B会话PID147904启动，输出frontier_hls_vivado_synthesis_20261024，独立核对脚本scripts/audit_frontier_vivado_synthesis.py。该阶段尚未完成，仍不宣称物理存储或时序闭合。

## 实际存储资源终态

Vivado2022.2 OOC综合完成（69.566s、exit0、checksum3c484d91），独立审计passed：3411 LUT、1794 FF、116 RAMB36E2、0 URAM、0 DSP、0 latch。实际物理RAM容量4276224bit覆盖4194304bit逻辑payload，15个原样RTL/初始化文件及门禁/DCP均绑定。HLS32 BRAM_18K估计不能当作实际资源结论。

独立10ns布局布线已启动，结果frontier_hls_timing_20261024。完整资源/时序尚待其终态，外部IO预算与平台时钟上下文仍缺。

## 物理终态

独立布局布线已完成并审计（324.482s、exit0）。3394 LUT、1794 FF、116 BRAM36、0 DSP，WNS1.336ns、WHS0.039ns、WPWS4.458ns，内部setup/hold/pulse失败及route错误均0。98输入与105输出缺少外部delay预算；当前仅10ns研究时钟，不能据此宣布平台时序闭合。结果frontier_hls_timing_20261024/final_audit.json绑定全部方法学、约束diff、路径及DCP证据。
