# 同一查询内的标识回收：待实现设计

状态：研究设计，尚未实现RTL或协议验证，不能替代现有完整fence语义。顺序软件参考已完成38查询/31次回收的真实值与有限ID预算检查，见 `../results/retained_checkpoint_plan_20261023.md`；这不证明以下排空/ACK性质。用于后续12个超出单区间事务预算的大查询；其中两个也会耗尽槽代次。

现有BEGIN/FINISH会清页域的query_used/generation_used/next_tx，顶层随后RECYCLE清后备目录。CPU参考模型可以snapshot/restore；硬件若照搬，需要显式导出并重新发布大量数据，不能把参考模型的直接恢复当作已实现的DMA操作。

候选方案把当前查询的数据生命周期与一次事务标识区间分开：保留当前query/price、frame地址、published位、原始后备页和索引，只在排空后重置事务与槽代次，再由顶层内部重新建立同一query。它不延长距离标签跨价格版本的有效性，也不改变设计级占用或历史拥塞。

## 允许进入的条件

只允许从一次完整目录回收之后、尚未切换到其他query/price的独占查询区间进入。顶层必须显式跟踪这个条件；仅检查当前active_query不足以证明目录没有其他命名空间。任何第二个成功的外部QUERY都使候选checkpoint不可用，直到下一次完整fence回收。

所有四个驻留槽必须已经写回脏页并RELEASE；仅page_leases==0不够，因为它不代表没有LIVE绑定。可以在顶层根据成功BIND/RELEASE维护bound_mask，并在最终测试中与页域实际状态交叉核对。若不满足条件，命令必须在进入排空前返回明确错误，不能进入等待后再要求被阻塞的主机释放槽。

主机必须为最多四个剩余脏槽的写回预留事务号；不能先耗尽ID再要求checkpoint自动完成写回。新的轨迹生成器需要预先检查即将发生的WB/RF与排空预算，所有原始访问都要被执行。

## 候选内部顺序

1. 顶层接受新的公开checkpoint命令，锁存当前query/price并禁止外部新命令。
2. 复用现有页域BEGIN和FINISH，等待有限fence请求/ACK、所有请求/工作/响应队列以及租约完全排空。不能用单独ACK、固定等待周期或外部布尔值绕过这一步。
3. 新的内部目录操作只重置tx_used/last_tx，要求全部地址租约FREE及可信内部fence退休。保留allocated、owners/published、索引epoch和桶内容。普通RECYCLE仍完整失效这些数据。
4. 顶层内部重新发起同一query/price，页域的新事务号和槽代次从头开始。原query_used在FINISH被清除，因此必须在向主机返回前重新占用当前query tag；不能开放一个可被外部新query插入的窗口。
5. 两域都确认成功后才返回checkpoint成功。任一步失败则保持fail-closed，不提前恢复命令入口。

复用现有页域时无需把新的公开opcode直接送给queued层：queued层12/13已有重发fence/重复ACK含义。顶层应将checkpoint展开为内部既有BEGIN/FINISH/QUERY序列，后备服务链新增的“只回收事务号”操作则必须使用明确的独立编码。

## 必须证明的性质

- checkpoint前后每个已发布owner保持相同frame和原始字节；LOOKUP/RF仍取到同一字段值。
- 重置事务号之前，没有已接受但未完成的AXI burst、页记录、COMPLETE/RETIRE或旧fence ACK。
- host响应被背压时，外部入口仍关闭；内部重新QUERY与host成功之间也没有开放窗口。
- 标签价格未变化；多个query/price曾共存时拒绝这个操作，避免FINISH清query_used后旧目录owner被错误复用。
- 事务号及槽代次多次回绕、query tag不变时，旧响应不能匹配新租约；只在已有封闭同钟队列假设成立时使用排空证明。
- 普通完整fence仍清空目录和索引命名空间；失败租约、无完整排空、仍有LIVE槽、剩余脏页、错误内部响应都不能触发成功。

验证顺序应为小位宽独立协议模型与负例、可综合组合、旧small/19-query回归，再执行全部38查询的值与字节回放。需要记录每次checkpoint的事务/代次高水位、排空成本和恢复后的查找，不把“保留后备页”当作已测得性能收益。

这个方案仍不覆盖不受控制的外部生产者、域外迟到/重复AXI包、跨时钟网络或掉电恢复。实际平台若不能保证端到端排空，需要额外标识区分或其他隔离机制，不能沿用当前封闭队列证明。

目录原语已新增独立变体并完成行为先导，见 `../results/rtl_retained_directory_20261023.md`。这只实现上述第3步的内部操作，fence输入仍可信，其他步骤和完整协议尚未实现。

服务链已增加内部opcode5→目录6并完成64页/4096记录的回收后AXI读回，详见 `../results/rtl_retained_services_20261023.md`。fence仍是可信输入，尚未接入自动排空顶层。

端点自动排空/恢复先导已实现，见 `../results/rtl_retained_endpoint_20261023.md`。21次checkpoint及旧19查询回归通过；全38真实查询、多阶段主动阻塞、综合与平台验证仍待完成。上文保留为原始设计义务。
