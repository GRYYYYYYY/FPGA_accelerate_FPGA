# 首次邻接过滤命令控制器

顶层 `children_step`，Vitis HLS 2022.2、xcu280-fsvh2892-2L-e、10ns研究时钟，`ap_ctrl_hs`。每次调用处理一条控制命令并给出完整状态快照；只有一个构建在途。内部helper是已通过93728组原函数对照和完整真实CPU路由的 `children_machine.hpp` 原样副本。没有外部存储访问、动态分配、循环处理全部邻接或并行构建；图/设计状态/缓存/排除边判断仍为外部服务。

接口采用13个32位输入和11个32位输出。`INTERFACE ap_ctrl_hs`位于顶层函数体；静态Controller保存跨调用状态，无DATAFLOW或PIPELINE吞吐声明。顶层包含一次有界step调用；HLS生成的多个独立ap_vld输出必须由集成层完整收集，同时等待ap_done，才能退役本次调用。不能将任意单个ap_vld或ap_ready视为完整结果。

输入顺序：op、parent、count、prune、query、price、generation、position、phase、node、value、aux、service_status。输出顺序：status、result_generation、request、result_position、result_node、result_parent、result_query、result_price、emitted、active、fault。生成Verilog将value命名为`value_r`，active输出命名为`active_r`。

命令：START=0、RESPONSE=1、SNAPSHOT=2。START使用parent(<2^24)、count(uint32)、prune(0/1)、query(0..3)、price(0..15)，其他输入不使用；每次合法START分配单调generation32。空邻接仍需必要死端检查和PUBLISH应答，不能立即退休。count是流式边数，调用者负责检查实际图范围和外部缓存容量；不能据本控制器count宽度声称已提供任意容量缓存。

RESPONSE必须回显generation、parent、query、price、position、phase、node。NEXT/CHECK_DEAD/MARK_DEAD/PUBLISH的node为parent，其他阶段为当前child；DONE的node为0。相同阶段在不同原始边位置出现时，position防止重复或迟到回复被接纳。count/prune在RESPONSE中不使用。SNAPSHOT忽略输入，仅返回当前状态，无外部操作。

| 阶段编号 | 请求 | 成功应答value / aux |
|---|---|---|
| 0 | NEXT | child(<2^24) / structural_dead(0/1) |
| 1 | EXCLUDE | excluded(0/1) / 0 |
| 2 | CREATE | 0 / 0，设计created写入完成 |
| 3 | CLASSIFY | inaccessible(0/1) / known_dead(0/1) |
| 4 | EMIT | 0 / 0，有序缓存追加完成 |
| 5 | CHECK_DEAD | canBeDeadEnd(0/1) / 0 |
| 6 | MARK_DEAD | 0 / 0，设计deadEnd写入完成 |
| 7 | PUBLISH | 0 / 0，完整缓存含空列表已发布 |
| 8 | DONE | 无待应答请求 |

只有身份、阶段和位置匹配后才处理service_status。非零服务状态锁存fault，保持未完成阶段/位置/计数，禁止继续START或RESPONSE。已完成的CREATE等外部副作用不会被本模块撤销；集成恢复必须有明确设计状态恢复边界。错误身份不会以伪服务错误毒化当前构建；相同身份但非法布尔值/ack载荷返回BAD且不推进，可用正确应答重试。emitted仅在EMIT成功应答时增加，PUBLISH成功后active才清零。

状态值：OK0、BUSY1、NO_REQUEST2、STALE3、WRONG_PHASE4、EXHAUSTED5、BAD6、WRONG_POSITION7、SERVICE_ERROR8、STOPPED9。检查顺序固定：故障/空闲，身份，阶段，位置，服务状态，载荷。只有status=0且fault=0才可据快照执行服务；SNAPSHOT在fault下也返回status0但保留fault1。未知opcode返回BAD。

generation永不静默回绕。生产32位未跑满2^32上下文；单独GEN3生成RTL实际完成7个上下文并拒绝第8个。没有在线RESET或ABORT命令。Tcl显式`config_rtl -reset state`；协调冷复位清Controller全部状态并回到generation0/DONE。外层必须排空或整体复位旧消息，不能据编号重启声称跨复位旧回复隔离。

功能测试用原始isExcluded/deadChild/canBeDeadEnd谓词和独立原始边循环生成服务事件，不使用本helper生成期望phase。32位覆盖73728单边参数组合+20000多边/重复边序列；错误回复、BUSY与只读快照穿插部分场景。服务实现是模型，尚未接真实图AXI、设计状态DDR或已验证paged_exclusion_engine。后续整合须保持 `../../CHILDREN_FIRST_TOUCH.md` 的首次创建/缓存语义。

集成时START只用于已经取得排他缓存构建所有权的miss，缓存hit应直接重放已发布列表。一次构建可能发出多个EXCLUDE；外层必须在整个构建期间锁住query/price和会影响过滤的标签修改，不能只依赖paged_exclusion_engine对单条边的保护。设计缓存key不应包含query/price；跨查询命中仍须复用原首次列表。主动checkpoint可以回收标签编号，但不得改变构建上下文或清除设计created/dead/cache。

后续调用收集/构建调度已在 `../../variants/children_engine_v2` 完成并通过实际HLS联调及综合，见 `../../../results/children_engine_20261024.md`。外部图/设计/缓存服务仍为模型，尚未完成设备存储整合。
