# 设备侧自主搜索循环通过（2026-10-25）

`search_scheduler` 已接管已准备查询的 SEED→POLL→标签校验→展开→目标检测→CHECKPOINT/排空。`search_residency_system` 将该控制器及全查询主机围栏接到上一轮真实服务顶层；342逻辑端口/56716接口位，117个既有RTL/dat/top文件保持。查询描述握手时锁存，实际堆回复决定parent，CPU文件只评分。

全查询期间，16个host入口与route提交被围栏覆盖，包括请求间隙和完成响应背压。恢复意图先取消搜索，直到完成响应消费后才放行；故障锁存期间禁止普通新请求，service target reset后才可重用。取消/超时不撤回已暴露VALID，必须等请求/回复/物理排空；后端永久停顿时没有有限完成保证。成功后的路径提交仍通过既有route入口另发命令。

## 验证结果

| 验证 | 结果 |
| --- | --- |
| 搜索FSM模型 | 20场景通过：同实例复用、元数据锁存、错误/空堆、标签不一致、cookie、限次、取消、超时、源等于目标、非空目标CLEAR、排空/完成背压 |
| FSM+主机围栏模型 | 同20场景通过；16入口+route竞争，恢复意图引发取消并延迟交接 |
| 真实服务32槽 | 116 POLL / 114展开 / 447判定 / 293 cost-OFFER / 879标签ACK |
| 真实服务单槽压力 | 相同语义，实际分页换入换出 |
| 共享路径 | 两次commit和两次ripup；共享refs 1→2→1→0、不同net占用 1→1→1→0 |
| 独立审计 | CPU轨迹、完整design/owner/label状态、七类AXI严格重放、四阶段owner及CPU q3确认通过 |

每种配置的七AXI日志及四最终图像均与旧驱动版本逐字节相同；语义事件相同，cycle变化。3032普通服务请求逐请求载荷/归属/退休核对；第二query的43次标签read只有无效write-value字段从旧TB残留2改为0，审计显式限定此差异，其余载荷一致。六AXI活跃，table分支未覆盖。

| 整段仿真 | 旧主机驱动 | 自主搜索 | 变化 |
| --- | ---: | ---: | ---: |
| 32槽 | 683640 | 682354 | −1286（−0.1881%） |
| 单槽 | 747471 | 745363 | −2108（−0.2820%） |

这些周期包括导入、外部prepare、回读、提交/释放及评分，是仿真调度变化，不是板卡加速。缓存读/写事务为605/260及1535/615；两个真实query目标处堆均已空，非空CLEAR分支只有模型证据。

## 完整顶层综合

Vivado2022.2 / U280 / 默认32槽、16384帧，诊断注入关闭。原生Tcl 555.981s、exit0；观察工具300秒交回后继续监督同PID，未重启。

| 资源 | 前一服务顶层 | 加自主搜索 | 增量 |
| --- | ---: | ---: | ---: |
| LUT | 79811 | 99477 | +19666 |
| FF | 60324 | 61700 | +1376 |
| BRAM Tile | 160.5 | 160.5 | +0 |
| DSP | 23 | 23 | +0 |

层次报告中search_ctl归入31403 LUT/1379 FF，backend为67950 LUT/60321 FF；跨层次优化会移动逻辑，不能把该归属直接当作孤立FSM成本。宽回复动态选择器是下一步静态切片对照对象，尚未验证根因。

URAM/latch/blackbox/文件agent实例均为0。共2221条警告，分类详见JSON；继承的HLS数组映射寄存器与未使用端口等仍保留。无时钟约束、布局布线、Fmax或板卡测量。

## 可复现证据与后续

入口：`hardware/variants/search_scheduler_v1/CONTRACT.md`、`search_scheduler.sv`、`search_host_fence.sv`、生成的`search_residency_system.sv`与`interface.json`。独立审计脚本：`audit_search_scheduler_unit.py`、`audit_search_scheduler_join.py`、`audit_search_scheduler_synth.py`。四结果目录`search_scheduler_unit_v3`、`search_scheduler_lease_v2`、`search_scheduler_join_v1`、`search_scheduler_synth_v1`均已归档并实际移开原件、解压、逐文件校验、重新审计且audit字节相同；收据`search_scheduler_restore_20261025.json`。源闭包冻结`search_scheduler_sources_20261025`，开发失败保留`search_scheduler_development_20261025`。

下一优先对宽接口选择逻辑做静态切片对照实验，保持逐请求/AXI语义不变并重新测量资源；之后将query间prepare与search→route提交编排迁入硬件，并补真实搜索故障/剩余堆清空验证和完整checkpoint。初始328标签集合及authority/snapshot生产仍依赖外部；现有journal只覆盖route owner修改。任意写恢复、完整warm/frontier/path/created-cache、unknown-page、实际价格/epoch回绕、容量预约、耐掉电与板卡仍未完成。研究goal保持active。
