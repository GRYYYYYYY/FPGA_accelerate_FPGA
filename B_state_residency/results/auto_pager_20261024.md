# 自动驻留页管理器与实际 HLS/AXI 整合（2026-10-24）

`hardware/variants/auto_pager_v1` 已把自动页解析、驻留槽替换与原生命令所有权接入实际 state-reset HLS 排除引擎。五组 XSim 回归和 `scripts/audit_auto_pager.py` 独立审计通过。结果目录 `auto_pager_20261024` 保存全部冻结源码、编译命令、原始函数 oracle、日志与 SHA256；manifest SHA256 为 `df27c1553abff3fbebe572ddb400dd809b9f7c6206847491303970f9a22b758f`。

缺页时依次执行脏页 WB、RELEASE、增加绑定编号的 BIND、RF；只有成功写回后才能淘汰脏页。没有已发布后备页时保留新绑定的零页，真实后备错误则停止。一个解析租约锁住原生入口直至标签桥接器接收响应。生命周期与通用写标签只在边引擎静止时接受，避免边判断中途改变 query/price 或标签。设计级 created、占用和历史拥塞仍在本接口之外。

每次成功 WB/RF 消耗事务编号；预留全部槽写回与当前缺页的最坏预算，在耗尽前自动 checkpoint，保留后备内容并重启事务及绑定编号域。checkpoint 不复位 HLS 边编号。达到绑定编号上限后不静默回绕；CLOSE 完成原生排空与目录回收后才能打开下一查询。详见 [接口契约](../hardware/variants/auto_pager_v1/CONTRACT.md)。

| 回归 | 槽/TX/绑定位宽 | 边判断 | 标签响应 | WB / RF | 自动 checkpoint | 检查数 |
|---|---|---:|---:|---:|---:|---:|
| budget32 | 32 / 6 / 16 | 319 | 410 | 457 / 1063 | 35 | 6566 |
| single | 1 / 6 / 3 | 1660 | 2100 | 2805 / 4377 | 651 | 11930 |
| production32 | 32 / 16 / 16 | 27681 | 34898 | 26984 / 97070 | 1 | 185502 |
| wrap16 | 1 / 16 / 16 | — | — | 0 / 0 | 1 | 65538 |
| fault | 1 / 6 / 16 | 含 RF 错误边 | 禁止错误标签提交 | 三种故障 | — | 14 |

production32 覆盖全部 27680 条原始 CPU 函数 oracle 向量，另外执行一次新查询立即完成边，共 62579 次实际 HLS 调用。预装 96 个稀疏页，包含全部五字段、高位值、显式 prev=-1 和有效全零记录；另加 70000 次访问跨越真实 16 位事务边界，单代最大使用 65503 个事务号。显式 checkpoint 后重新核对标签，CLOSE/新查询后旧后备内容不可见，后一次检查没有发出旧页 AR。

独立 AXI512 字节模型检查 3×512 位页内容、全部写字节使能、4KB 边界拆分、W 先于 AW、通道背压和延迟回复。完整组 AW=B=27724，AR=100000，R=291210=3×97070；跨 4KB 页导致 burst 数可以大于页事务数。每次 WB/RF 的字节与独立标签模型一致，绑定/脏状态观察器仅依据已应答原生命令更新。完整组虚拟仿真终点 252026230ns，XSim 命令墙钟 268.603s；这些是本测试工作负载的时间，不用于推算完整路由加速。

single 用一个槽强迫父、子和重复 prev 请求之间换页；651 次自动 checkpoint 均触及缩小的 GEN3 上限。wrap16 则实际完成 65536 次不同零页访问：第 65535 个绑定之后 checkpoint，第 65536 个绑定重新使用编号 1，没有 AXI 访问和后备分配。这不是以缩位测试替代生产 16 位边界，也不代表覆盖了 HLS 32 位 generation 全域。

故障组分别注入真实 AXI B 错误、在 HLS 标签读取时注入 R 错误，以及两帧目录 FULL。检查失败 WB 不释放原绑定/租约，失败 RF 不暴露原生 READ 或提交 HLS RESPONSE，FULL 不丢弃脏 victim。随后协调冷复位恢复。模块不提供热取消、跨复位旧消息保护或并发请求服务。

独立审计重新核对冻结/live 源码与上游门禁、所有命令退出码与日志哈希，并用 Python 条件逻辑逐条核验 oracle 决策、阶段和读取节点，核对 27648 个 flags/created/Laguna/prev/sequence 组合的完整性及各 stride 子集的计数。

实际 Vivado 2022.2 完整组合 OOC 综合与 `scripts/audit_auto_pager_synthesis.py` 独立审计已通过，结果目录 `auto_pager_synthesis_20261024`。默认32槽、163840后备帧、TX16/binding16/epoch16：**16528 CLB LUT、15156 FF、375 BRAM Tile、3 DSP、196 CARRY8、0 URAM/latch**；命令耗时280.532s、exit0、网表checksum `57828bf5`。资源包含整个原生端点、自动管理器与实际state-reset HLS，不能与此前不含端点的1172 LUT边引擎直接比较为同范围加速或成本增量。

LUTLP-1违规0，`check_timing`的loops/latch_loops/no_clock/unconstrained_internal_endpoints均0。综合日志两条零次复制警告来自冻结原生端点在TX/GEN恰为16位时的零扩展表达式；159条无负载端口警告涉及仅使用prev/visited字段的标签桥接器及生成HLS的未使用端口（标签载荷实际未使用96位，部分警告重复）。没有ERROR或CRITICAL WARNING，没有放宽组合环检查。806输入/920输出未设delay，HD.CLK_SRC未设；未布局布线，没有时序闭合或平台频率结论。完整命令收据、DCP和报告均绑定哈希。

本轮功能仿真最多 256 帧，边界/故障分别 16/2 帧，完整163840帧仅用于实际综合。该模块尚未连接完整图扩展、动态 created/getChildren 首次过滤缓存、Frontier、代价计算、回溯与提交，也没有平台/XRT 或板上结果。既有全 38 查询端点回放的 9.5213% 改善来自单独实验，不能套用到本模块或完整路由。

复核命令：`python3 scripts/audit_auto_pager.py`、`python3 scripts/audit_auto_pager_synthesis.py`。项目 `python3 scripts/run.py check` 通过。若需重跑，使用新结果目录调用 `scripts/run_auto_pager.py`，不要覆盖已冻结结果；结构实验脚本为 `hardware/scripts/synthesize_auto_pager.tcl`。MCP B147904已经终态，仿真385.813s/exit0、综合280.532s/exit0；旧running交接不是待重投任务，functions cell3734已完成。
