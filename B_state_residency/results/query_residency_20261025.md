# 查询级State驻留验证：读流量72→1，周期不变（2026-10-25，优先历史）

同一自然logicnets首查询、同一TB和全部既有真实输入，在隔离variant中加入一行64B State缓存后通过32槽/单槽实际XSim。结果 results/natural_query_resident_v2，边界回归 connection_resident_bounds_v1。比较证据 results/query_residency_20261025.json（compare_query_residency.py），两个主审计 audit_natural_query_resident.py、audit_connection_resident.py。原109份生产RTL/dat中只在冻结新实验的params/connection_state_reader.sv替换一份，108份逐SHA保持；基线目录与原connection_state_v1源码未改，不自动提升为默认实现。

| 项目 | 基线32槽 | 驻留32槽 | 基线单槽 | 驻留单槽 |
| --- | --- | --- | --- | --- |
| State 64B读拍 | 72 | 1 | 72 | 1 |
| 仿真总周期 | 430263 | 430263 | 470003 | 470003 |
| 首次到目标POLL周期差 | 311297 | 311297 | 378601 | 378601 |

每配置少71次读/4544B，非State的完整natural_trace.txt（含逐事件周期）逐字节一致，design/labels/owner/cost完整文件和graph/design/label/owner/cost/table所有AXI字节日志均逐SHA一致。qstate日志恰等于原日志第一组AR/R，其他71组消失。73POLL、72expand、271candidate、171cost/commit/OFFER、513ACK、308最终记录和111物理有效标签页保持。没有仿真搜索时延改善；这与State读取被并行扩展准备所覆盖相符，但尚未做受控memory latency扫参或实际板上性能测量，不能宣称加速、能效改善或板卡收益。

实现 hardware/variants/connection_resident_v1/connection_state_reader.sv，由derive.py从未改基线精确生成。缓存完整512bit State，不缓存任何距离/visited标签。key核验query2bit/price4bit、完整version32/design64、connection/net/sink/cross、configured profile revision32。原bad_request/bad_identity检查仍先执行，原row/RID/RRESP/RLAST/timeout/drift/abort及排空保持；仅在所有检查通过的R回复填充一行。命中重新回显本次cookie/身份并提供独立稳定响应。表在configured生命周期不可变，不能绕过所有者在后台修改后备。

query inactive、上下文或revision变化、任何fault/abort均清cache_valid；rst也清。decision_lock正常在父扩展之间下降不失效，但请求和未退休响应仍沿用原锁/身份约束。新connection/net/sink/cross键不匹配会走原实际读与原row检查，未把某次缓存有效当作新请求合法。配置revision只允许冷复位后重新配置，测试revision2复位后首次miss。没有改变标签生命周期或价格版本距离有效性规则。

独立边界TB保留原182个真实row及fault/drain回归，并增加无AR命中、cookie更新、lock-gap复用、query关闭重开miss、版本高16位变化miss、price/query变化miss、warm-cache错误net/sink/cross实际读后拒绝、profile冷重配、64bit design错误无AR拒绝、缓存响应背压期间late drift保留原响应且fault停止。终态CONNECTION_RESIDENT_PASS successes=195 errors=11 AR=199，所有195条完整row独立匹配原180326行表；错误/timeout/abort排空保持。不是并行多context或热profile修改证明。

MCP已有B session/PID147904、Vivado2022.2：自然两组166.122s/exit0，边界10.265s/exit0。最早natural_query_resident_v1因生成器拼接endend编译失败，修正end后空格才运行v2；原失败manifest/log/reader固定在 results/query_residency_compile_failure_20261025，未改已通过基线或通过产物。最终源码/derive/TB/runner/审计依赖固定在 results/query_residency_sources_20261025；终态收据 query_residency_completion_20261025.json。没有新增工具版本要求，无新HLS内核或厂商补丁。

持久化：offer_archives_20261025/natural_query_resident_v2.tar.gz为433常规文件/10585397B；connection_resident_bounds_v1.tar.gz为33文件/98754B。压缩成员与共享盘copy SHA核验，两个scratch目录实际移开到.preserved后解包恢复，完整对照JSON重新生成逐字节一致；凭据 query_residency_restore_20261025.json。依赖原自然输入、oracle、graph和baseline仍按各自索引保持。

下一步优先测真实自然搜索的关键等待：State驻留已经减少流量但没有时延收益，不能继续把重复读取计数当加速依据。先用不改生产行为的观测TB拆出图/首次过滤、metadata/access、几何/成本、标签提交与队列等待，确认State miss完成相对扩展/metadata消费的时间；必要时受控总线延迟扫参。再按关键路径选择设计/查询级驻留，保留动态created/cache/owner语义和同一自然oracle。这个可选缓存尚未综合/布局布线或量化资源开销，若保留需补资源代价；完整可综合search controller、backtrace/owner commit、多查询/MCML/价格版本与板卡性能仍待完成。goal active。

