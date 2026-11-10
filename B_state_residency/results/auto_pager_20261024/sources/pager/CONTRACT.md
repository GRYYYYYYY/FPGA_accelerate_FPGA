# 自动驻留页管理器 v1

独占原生命令入口；默认32槽、native TX16、binding16。只允许一个在途操作与一个解析租约；替换采用空槽优先、随后轮转，有限槽顺序查找。SLOTS须为1..32的2次幂，GEN_BITS为1..16（控制本地绑定编号上限，native端口固定16位），TX_BITS与native一致且2^TX_BITS>=SLOTS+2。这是可执行换页控制基线，未声称其查找策略优于CPU LRU或达到最终吞吐目标。

生命周期控制：OPEN=0发送原生QUERY，CHECKPOINT=1逐槽成功WB脏页、RELEASE后调用原生CHECKPOINT12，CLOSE=2同样清理槽后BEGIN10/FINISH11完整回收。FINISH状态7按闭合协议重试。重复OPEN返回BUSY4，无查询的CP/CLOSE返回STALE1，未知控制返回BAD3。只有HLS边引擎静止时接受控制与通用标签访问；边参数隐含当前query/price，防止没有标签读取的立即完成边绕过版本校验。不同边之间可继续同一HLS编号域；checkpoint不复位HLS。

通用标签接口接受node32、write、field0..4、value32；整合顶层固定到当前query/price，管理器内部接口仍显式核对版本。拒绝node>=2^24、field>4和target写入>255。读回完整160位记录与present；空记录保持0，显式prev=-1保持0xffffffff，写入全零仍为有效脏记录。设计级占用/历史/created不在本接口中，不得随标签页回收清除。

缺页：选空槽或可增代的victim；脏victim先WB成功才RELEASE；新BIND使用旧generation+1，再RF。RF成功可用，RF状态8且本管理器从未容忍失败发布时表示无后备页，保留BIND生成的零页。其他错误fail-closed，不将未完成/错误页当作零页。仅成功操作更新镜像标签、dirty和编号。

解析接口回显token/边generation/phase/page/query/price并给出slot/binding。map握手后锁住整个原生入口，只接受符合本租约描述符、phase字段和READ=2的客户端命令。原生响应被桥接器接受后租约退休；这时标签值已被桥接器锁存，允许下一次访问换页。无仲裁外旁路命令。解析响应、通用访问响应和控制响应在背压下保持。

事务预算：每次成功WB/RF消耗一个native事务号，RF miss不消耗。新操作前若used+SLOTS+2>2^TX_BITS，先清理全部槽并原生checkpoint，保留后备页后重置本地事务/绑定编号。预留SLOTS次脏页WB和本次最坏WB+RF，避免耗尽后无号可清理。所有槽绑定编号耗尽且访问未命中时同样自动checkpoint。当前命中即使编号已达上限也可用，但不再增加该编号。失败checkpoint不清本地元数据；编号永不静默回绕。

已返回的成功/失败状态必须与fault同时检查。后备FULL、I/O错误、内部原生状态不一致、无归属响应锁存故障；保留未完成租约和脏victim，不继续绑定或回复成功标签。原生故障可以当拍阻断发命令；已经提供的回复保持不变。恢复需外层排空/协调冷复位；没有在线取消、并发读写、跨时钟域或跨复位旧消息防护。

验证计划：32槽生产TX16完整27680单边oracle及至少70000次额外真实RF压力；32槽TX6预算压力；单槽GEN3在HLS父/子/重复prev阶段间反复换页；真实16位65535绑定后自动checkpoint再绑定；实际AXI字节模型检查稀疏/有效全零/五字段/页边界/背压及B错误、R错误、目录FULL不丢弃脏victim。默认目录163840帧，仿真分别256/16/2帧，未等同全真实路由、平台或板上结果。
