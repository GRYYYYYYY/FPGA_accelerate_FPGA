# 有界队列封装与有限 fence

`queued_scratch_endpoint.sv` 组合冻结的页控制器与BRAM页槽，通过 `bounded_sync_fifo.sv` 包含全部命令请求、等待执行工作、已完成响应和控制fence请求/ACK。当前是同一时钟域内的闭合端点，不是跨主机/跨时钟的真实DMA链路。

默认命令/工作/响应队列各4条，fence请求与ACK各2条。每条命令265位，每条响应181位，fence包24位；默认tx/gen16位、fence tag2位。控制包保持软件的3字节格式：最低8位opcode（0=fence、1=ACK），其后16位little-endian tag，高于TAG_BITS的tag位为0。测试还使用3位tx/gen与1位tag；未证明所有参数组合。

## 数据路径与握手

公开命令/响应格式沿用 [页控制器契约](PAGE_CONTROLLER_CONTRACT.md)，但去掉外部 `peer_quiescent` / `ingress_empty` 输入。命令握手仅表示入队，不代表执行完成；响应按命令接收顺序交付，一次只执行一个命令，但队列可缓冲多个命令。FIFO满则反压，没有组合直通路径；响应valid且ready为0时整个输出保持稳定。冷reset只清FIFO计数/指针，不清RAM内容。

`dispatch_enable`、`execute_enable`、`fence_service_enable`、`ack_receive_enable`只控制阶段能否前进，可用于下游背压，正常全置1。它们不能宣布排空，也不能绕过占用计数/租约。输出队列计数、lease位图、fence_active/tag/acknowledged/peer_sealed供观测，不承诺跨时钟有效。

op0..11的语义保持页控制器约束；新增op12重新排队当前fence请求，op13复制当前ACK队列首包。无活动fence返回BAD；对应队列满，或ACK不存在，返回BUSY。重复包只来自当前已存在的活动fence，不允许从模块外随意注入旧控制包。原op14/15仍BAD。

## 排空与复用条件

成功WRITEBACK/REFILL响应入响应队列时置相应slot的lease；成功COMPLETE响应入队时解除。尚未入队的响应由busy覆盖，不能产生漏计窗口。旧/重复/错误COMPLETE不解除lease。底层页控制器仍核对完整描述符和64位置传输完整性。

成功BEGIN_FENCE后，控制请求进入FIFO。peer只有在命令请求/工作队列均空、当前执行单元空、所有页传输lease为0，且当前周期没有新命令入队时，才能消费fence请求并排队ACK。此时响应队列可以非空；所以peer_sealed或acknowledged本身不是回收授权。

FINISH_FENCE执行时必须同时满足：活动fence已收到正确tag的ACK、peer已sealed、lease为0、请求队列空、工作队列只含当前FINISH、响应队列空、fence请求/ACK队列全空，且同周期没有新命令握手。此外，底层页控制器检查全部槽已释放，才清有限tx/query/generation隔离。成功响应入队后才推进fence_tag（模2^TAG_BITS）并撤销fence状态。

因此，未消费的旧响应、重复ACK、排在FINISH后面的工作，或FINISH执行边沿的新请求，都会使本次FINISH返回FENCE_WAIT。失败FINISH响应也必须消费后才能再次成功。传输中的页可以在BEGIN后继续EXPORT/BEAT/COMPLETE；底层拒绝创建新传输。仍有尚未开始写回的脏页时BEGIN返回DIRTY，不丢页。

## 尚未实现的边界

此模块产生的排空证明只覆盖其闭合、同钟、无隐藏生产者的队列。命令发送方在成功fence后重新注入已经退休的旧包，或在模块外保留旧ACK/未计入的数据引擎，均不在证明范围。真实系统中的所有DMA执行单元、AXI outstanding请求、返回通道、跨时钟FIFO、地址池租约和远端控制通道必须纳入排空域。当前FIFO承载页控制命令和数据，**不是完整的远端描述符调度/去重DMA引擎**。

COMPLETE仍表示外部适配器确认的数据操作持久完成；本封装不会仅因EXPORT响应被消费就自行生成COMPLETE，也未证明后备地址正确。还没有DDR/HBM地址分配RTL、AXI读写引擎、实际内存写响应绑定、丢包/超时/热复位恢复。不能把本地闭合队列的正确性外推成真实PCIe/AXI链路排空或板级加速。

验证及五项移除保护条件的反例见 [本轮报告](../results/rtl_queued_endpoint_20261023.md)。
