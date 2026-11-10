# 首次构建引擎：实际HLS、调用收集与服务调度（2026-10-24）

`hardware/variants/children_engine_v2` 将已验证state-reset `children_step` RTL、11输出调用收集器和构建级服务调度器组合为 `children_build_engine`。调度器在START到最终结果退休期间保持busy，保存query/price等上下文，逐步核对HLS返回的phase、position、node、emitted、generation和owner；PUBLISH应答完成前不返回成功。契约见 [CHILDREN_ENGINE_CONTRACT](../hardware/CHILDREN_ENGINE_CONTRACT.md)。

四组实际XSim回归和 `scripts/audit_children_engine.py` 独立审计通过：

| 用例 | 主要覆盖 | 结果 |
|---|---|---|
| collector | 12个完成事件（11输出+done）的132组首尾边界顺序和4096组确定性随机顺序；并发到达、缺失每一路、重复/无归属事件、超时、晚到故障 | 4228组顺序、4229次完整调用、19个故障场景通过；不是12!穷举 |
| gen3 | 实际生成GEN3 RTL两轮完整7构建后耗尽，中间协调复位 | 14构建、84服务、100 HLS调用、2次拒绝、16检查 |
| pilot | 1024个原函数服务向量加错误恢复 | 5535正常服务、6673 HLS调用、26故障/协议场景、1051检查 |
| full | 全部93728原函数服务向量加错误恢复 | 813439正常服务、907281 HLS调用、813527 RESPONSE、26故障/协议场景、93755检查 |

正常向量由冻结HLS验证中的原isExcluded/deadChild/canBeDeadEnd谓词与独立原始边循环产生，包含73728单边组合和20000多边/重复边序列；输出46896条缓存记录。正常服务分布：NEXT/EXCLUDE各252794、CREATE/CLASSIFY各66833、EMIT46896、CHECK_DEAD32917、MARK_DEAD644、PUBLISH93728。独立Python审计重新解析全部向量并验证阶段、位置、节点和输出计数，绑定原函数/生成器/HLS源码及实际编译宏。

26个故障/协议场景包括七种错误归属字段（禁止转发HLS RESPONSE）、全部八阶段的匹配服务错误、全部八阶段的非法成功载荷、同拍service_fault阻止回复提交、结果背压期间的晚到故障和无归属回复。另有两个HLS之前拒绝的非法构建，以及协调复位后最高24位child的正常构建。服务status非零会送入HLS使其锁存故障；身份错误则在调度器处停止。已提供的结果在背压下保持，晚到fault由独立fault信号暴露；外层必须同时检查status和fault。

完整组有2440589个请求背压周期；虚拟终点107941490ns，XSim命令墙钟123.746s，整套MCP调用173.388s/exit0。正常构建占907167次HLS调用，错误恢复增加114次调用/88次RESPONSE。这些是服务模型工作负载计数，不是图DDR/完整节点扩展吞吐，也不能与先前独立协议的不同刺激集合直接作速度对比。

首轮 `children_engine_20261024` 在155ns的首个请求检查失败，诊断 `children_engine_diagnose_20261024` 显示同一delta-cycle先读到旧generation0，156ns稳定后为1；下一个请求在255ns重复该采样现象。v2仅把服务valid出现后的检查移到下一下降沿，所有RTL、oracle及HLS保持逐字相同。失败收据、诊断日志和恢复差异由独立审计绑定，未改DUT来迎合测试。

实际Vivado 2022.2 OOC综合 `children_engine_v2_synthesis_20261024` 及 `audit_children_engine_synthesis.py` passed：**1550 CLB LUT、2047 FF、70 CARRY8、0 BRAM/URAM/DSP/latch**；78.002s/exit0，checksum `a8c0c267`。LUTLP-1违规0，check_timing的loops/latch_loops/no_clock/unconstrained_internal_endpoints均0；402输入371输出无delay，HD.CLK_SRC未设，未布线。资源包含HLS、收集器和服务控制器，尚不含实际服务存储或paged_exclusion_engine。

正常服务回复仍由测试平台提供。尚未实现raw图AXI、设计级created/dead、持久过滤缓存或排除边引擎服务适配；busy是外层必须使用的锁定接口，并未自动封锁现有pager的host入口。缓存hit应重放持久结果；miss需先取得排他所有权，count须与原始CSR度数一致，不能让调用者随意省略边。设计缓存不得随query checkpoint清除或在淘汰后重新过滤。下一步优先接这些实际服务，再向Frontier/距离代价/回溯提交推进。

主manifest SHA256 `6b73e7c74cea56b04bb1bf3bb88e00d2a4e32ef5198f747a137cdd41334718fb`；源码、原函数、向量、日志、DCP、门禁及收据冻结。MCP B147904回归和综合均终态，functions cells3806/3810/3817和诊断exec24303均完成，不重投。项目check通过；完整FPGA路由、平台、板上仍未完成。

复核：`python3 scripts/audit_children_engine.py`、`python3 scripts/audit_children_engine_synthesis.py`。复跑须选择新目录，保留所有失败和成功结果。
