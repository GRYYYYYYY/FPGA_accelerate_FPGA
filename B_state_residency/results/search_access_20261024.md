# 原始可访问性与扩展决策状态机（2026-10-24）

`hardware/hls/search_access/v2/access_machine.hpp`已把每child的visited/prune/target/bbox、图可访问性、pinbounce、Laguna方向、SLL防返回及lookahead/提前清堆决策拆成显式请求状态机。完整接口见[SEARCH_ACCESS_CONTRACT](../hardware/SEARCH_ACCESS_CONTRACT.md)。原getChildren首次过滤、代价计算、push与循环停止逻辑保留。

状态机先发VISITED，按分支请求target、动态endY、SLR、同网引用/占用及parent.prev。目标exclusive sink无需普通bbox或willOverUse；非目标exclusive sink保留第二次target读取；SLL防返回保留两次parent.prev。NON_LOCAL_LEADING先sink再child SLR，graph分支先child再sink。静态属性采用快照，动态读取不提前。

## 原函数差分

`search_access_unit_v3_20261024/source_bound_audit.json` passed。测试从冻结CPU源码原样提取graphIsAccessible/isAccessible/isAccessibleSink/exploreAndExpand，保留原坐标方法和原行号；比较动态label/SLR/endY调用顺序、push/skip/lookahead、earlyTermination、queue.clear和prune计数。

18³种child/parent/sink类型组合×8上下文，共46656组、195175次START/ADVANCE。允许21426、跳过25230、lookahead5329、提前清堆2308、prune1614、visited命中2715；hot23328。覆盖11类服务，包含151次parent.prev读取和61次前驱tile读取。UBSan通过。类型组合完整，不表示动态配置或所有运行状态已穷举。

`search_access_unit_20261024`首次仅因fixture在Candidate作用域未定义TLD宏而编译失败；v2只补测试fixture宏，状态机和kernel逐字节不变。v2通过原决策/标签轨迹后，v3进一步记录SLR和动态endY调用顺序并通过。三份结果均保留。

## 实际HLS与完整CPU

`search_access_hls_20261024/source_bound_audit.json` passed：195175个经原函数差分验证的状态转移，加9个非法op/phase/bits/action/config包，共195184调用，1171104返回字在Csim、cosim前检查、实际RTL后检查均一致。非法包status1、输出体清零。

`access_step`每次显式传入Config/phase/bits/aux/action，不保存隐藏算法状态。实际RTL latency13、interval14，总2732575周期；流程93.280s终态。HLS估计2809LUT757FF6.491ns仅是估计。一次child判断可能需要多次调用和实际服务读取，不能将13拍直接称为每child完整延时。

`search_access_real_20261024/source_bound_audit.json` passed：接回完整CPU路径，570286搜索、130334832 push、12轮overused0。路径、全部搜索metadata及已采集标签访问与`search_geometry_real_v2_20261024`二进制一致。直接标签读取保持原trace行号；坐标和SLR仍调用原方法。CPU route101.728s仅运行记录，不作加速比较。标签访问采集为抽样；真实配置lookahead0，不能据此证明递归硬件。

## 实际综合

`search_access_synthesis_20261024/final_audit.json` passed：xcu280 OOC、10ns研究时钟，764 LUT、756 FF、32 CARRY8，零DSP/BRAM/URAM/latch；LUTLP-1及check_timing组合环0。87.583s/exit0/checksum`98f9839`/MCP history74，27606字节完整收据及DCP冻结。

66输入87输出没有IO delay，HD.CLK_SRC未设，未布局布线。警告包括未使用端口（HOT由坐标服务解释，单步决策核不使用该位）、输出地址常量位、层次布局提示；没有critical warning或error。此结果不证明10ns物理时序或完整系统资源。

## 当前边界

这不是已联接的设备访问性服务：label/SLR/endY/同网引用及occupancy响应仍由CPU或测试环境提供，硬件端还需真实服务适配、pending请求代号、query/price归属、超时及中断复位。显式状态也不消除中断HLS调用的残留写口风险。

下一步优先接实际标签与图属性读取、动态SLL endY、SLR/Laguna表，再实现设计级引用/价格和中心距离浮点计算，将访问性、geometry、cost与Frontier组合为完整搜索。保留target先CLEAR5再prev/代价/标签/offer；首次push置visited；递归需有序子列表与显式栈；checkpoint不清heap/栈。SLL初始prev与paged默认0仍需跨SLR语义核对。

回溯提交、完整平台/物理/板上及端到端性能仍未完成，既有组件验证不扩大为完整FPGA路由或实测加速结论。
