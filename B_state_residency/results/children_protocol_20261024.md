# 首次邻接过滤硬件请求控制器（2026-10-24）

`hardware/hls/children` 将已验证的 `children_machine.hpp` 原样接入持久HLS控制器。每次调用处理一条START/RESPONSE/SNAPSHOT，保留八种待服务阶段；回复校验build generation、parent、query/price、原始边position、phase、请求node，拒绝错归属、重复或迟到回复。服务失败锁存fault，未完成构建不发布；空列表也必须等PUBLISH成功应答后退休。协议详见 [ARCHITECTURE](../hardware/hls/children/ARCHITECTURE.md)。

`results/children_hls_20261024` 的C++、Csim、Csynth、Verilog RTL cosim及 `scripts/audit_children_hls.py` 独立审计全部通过：

| 案例 | 正常构建上下文 | 实际调用 | 拒绝回复/命令 | 覆盖 |
|---|---:|---:|---:|---|
| generation32 | 93728 | 918795 | 10657 | 73728单边组合、20000多边/重复边序列、错误归属/阶段/位置/载荷、BUSY、重复回复、故障锁存 |
| generation3 | 7 | 406 | 337 | 实际7次构建完成，第8次START返回EXHAUSTED，不能静默回绕 |

32位正常序列中，NEXT/EXCLUDE各252794次，CREATE/CLASSIFY各66833次，EMIT46896次，CHECK_DEAD32917次，MARK_DEAD644次，PUBLISH93728次；另外一次空构建在PUBLISH注入服务错误并验证停机。测试使用原始isExcluded/deadChild/canBeDeadEnd谓词及独立原始边循环生成服务事件，没有用DUT helper生成期望阶段；服务仍是模型，并未接真实图或缓存存储。

HLS2022.2总墙钟32位263.51s、gen3 42.01s，工具exit0。HLS两组估计均1598 LUT、882 FF、0 BRAM/DSP/URAM，控制函数延迟2周期、调用间隔3周期；这些不是包含图/标签/缓存服务后的构建延迟、物理频率或全路由吞吐。

Tcl显式 `config_rtl -reset state`，独立审计检查生成RTL中13个持久状态字段的ap_rst赋值。随后 `children_reset_20261024` 直接驱动同一gen32 RTL，八个待服务阶段、服务故障锁存、空列表发布及24位最高parent/child均通过，**11次复位、63次调用**；`audit_children_reset.py` passed。复位测试经现有健康MCP B147904执行，14.684s/exit0。协调冷复位清静态Controller；不代表热取消、跨复位旧消息隔离或撤销已经发生的CREATE等外部副作用。

实际Vivado 2022.2综合和 `audit_children_synthesis.py` 结构审计已passed，目录 `children_hls_synthesis_20261024`：**944 CLB LUT、881 FF、36 CARRY8、0 BRAM/URAM/DSP/latch**；84.354s/exit0，checksum `c23d7bc6`。LUTLP-1违规0，check_timing的loops/latch_loops/no_clock/unconstrained_internal_endpoints均0。418输入/248输出未设delay，HD.CLK_SRC未设；未布局布线，无频率或平台闭合结论。其余两类警告为未满足并行综合条件、层次不理想的floorplanning提示，无ERROR或CRITICAL WARNING。

该模块目前是独立控制器，资源不含11个输出的完整调用收集器、图/设计状态/缓存服务或paged_exclusion_engine。一次首次构建包含多次EXCLUDE，外层需要锁住整个构建的查询上下文；现有边引擎只保护单条边，不能直接认为覆盖了完整首次构建。缓存hit应绕过本控制器重放已发布列表，设计缓存不可随query checkpoint丢弃后重滤。

HLS manifest SHA256 `dec9112fc869f66a0de687e830bd6f5ef4565cab0ded7741468da5db592d4aff`；helper SHA256 `2c81dcc34cf7ca50eca31354806a3e943517c3a271857590d4b62a4e19782ed3`；reset manifest `da0bdfdcb0683bcbb5dc3c702e4597e96cc792eac370524237231b8650cfb020`。源码、原函数片段、工具命令、报告、生成RTL和审计均保留。HLS runner1055952及exec47602已终态，不重投。未改原始参考或既有冻结基线。

复核：`python3 scripts/audit_children_hls.py`、`python3 scripts/audit_children_reset.py`、`python3 scripts/audit_children_synthesis.py`。MCP B147904复位和综合均终态，functions cell3793已完成，不再wait或重投。完整FPGA搜索、平台和板上验证仍未完成，不将本轮协议验证或既有全38状态端点回放9.5213%解释为完整路由加速。
