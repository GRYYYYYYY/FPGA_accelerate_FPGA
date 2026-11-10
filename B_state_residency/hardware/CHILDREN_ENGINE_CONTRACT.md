# 首次构建引擎 v2

实现位于 `variants/children_engine_v2`。`children_build_engine` 组合实际 state-reset `children_step` HLS RTL、13输入/11输出的调用收集器和串行构建级调度器。v2与v1的RTL完全相同，仅测试平台将服务valid出现后的采样移至下一下降沿，避免同一delta-cycle读到尚未更新的字段。原失败和诊断证据保留。

构建输入：cookie32、parent32(<2^24)、count32、prune32(0/1)、query2、price4。合法请求锁存全部上下文；无效parent/prune在HLS之前返回BAD_BUILD，且不污染后续构建。busy从构建接收后保持到最终结果被接收，失败后锁定busy直到协调冷复位。外层须将这一信号用于禁止整个构建期间切换查询或修改影响过滤的标签；该模块没有直接控制现有pager的host入口。

结果：status4、detail32、cookie32、generation32、emitted32。仅status=0且fault=0时可以确认构建成功。status：OK0、BAD_BUILD1、HLS_ERROR2、SERVICE_ERROR3、PROTOCOL_ERROR4、ASYNC_FAULT5。最终结果在背压下保持，之后出现外部fault也不改已提供的结果包，调用者同时检查fault。HLS编号耗尽返回HLS_ERROR/detail5并停止；不静默回绕或在线清编号。

服务请求包含generation、parent、position、phase、node、emitted、count、prune（各32位）、query2、price4。八种phase沿用HLS契约；emitted是当前已确认追加的缓存条目数，供EMIT确定写入位置。服务回复必须逐项回显generation/parent/position/phase/node/query/price，并提供status/value/aux各32位。回复最早在请求握手后的下一拍出现，不支持组合零延迟回复。无归属回复或错误回显停止构建，不能把该回复提交HLS。

匹配的非零服务status送入HLS，让HLS本身锁存故障；外层返回SERVICE_ERROR/detail原服务status。匹配但非法成功载荷由HLS拒绝，外层返回HLS_ERROR。service_fault是异步故障指示，当拍阻止新调用/服务回复提交，锁存停机。状态只可由协调全链路冷复位恢复；已发生CREATE/EMIT等外部副作用不会回滚。

调度器独立维护预期phase、position、node、emitted和结构any_alive，核对每个HLS快照的完整上下文、generation单调性、active及fault。只在全部字段符合预期后发出下一个服务请求；PUBLISH应答前不能成功完成。调用收集器等待ap_start/ap_ready接收、ap_done以及全部11路独立ap_vld；HLS调用上限256周期，重复/无归属输出、缺失输出/完成或超时停止。ap_start只受锁存stopped及外部abort控制，禁止ap_ready组合故障反馈形成环。

本模块没有对外部服务设置固定延迟超时；服务可持续背压，系统监督/恢复在外层。没有服务端副作用的重试协议，没有多构建并发、CDC或跨冷复位旧消息保护。缓存hit不应走此首次构建引擎；miss须先由外层取得排他构建所有权。图读取、动态created/dead、持久缓存与paged_exclusion_engine的实际服务分派仍待实现。不能将测试平台的服务应答模型称为设备图/缓存实现。
