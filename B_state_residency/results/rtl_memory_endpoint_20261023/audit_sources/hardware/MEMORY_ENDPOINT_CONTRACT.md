# 闭合页槽与AXI后备存储端点

`memory_scratch_endpoint.sv` 组合既有四槽页存储、页控制器、有界请求/响应/fence队列、记录codec、后备owner目录和AXI页引擎。全部内部EXPORT、BEAT、COMPLETE、地址RETIRE及RECYCLE由顶层RTL生成，外部不能注入完成或排空声明。

## 外部命令

单时钟，最多一个外部命令在途；完成响应被消费前不接受下一命令。输入接受后保存全部参数，响应背压时稳定。外部参数为op、slot、page、query、price、generation、offset、field、value，不提供tx/kind/present/payload或fence_retired。有限事务号由页控制器分配并随成功WB/RF响应返回。

| op | 含义 |
|---|---|
| 0 | QUERY，切换到尚未使用的query ID及指定价格版本 |
| 1 | BIND，将空闲槽绑定到当前query/page/generation |
| 2 / 3 | READ / WRITE，读取完整记录或更新指定字段 |
| 4 | RELEASE，仅允许干净LIVE页 |
| 5 | WB，完整导出到固定后备地址，成功后页槽变干净、租约释放 |
| 6 | RF，从已发布后备页恢复到pristine槽，完整发布后租约释放 |
| 10 / 11 | BEGIN_FENCE / FINISH_FENCE |
| 7..9、12..15 | BAD，禁止外部注入内部传输或测试控制命令 |

响应status扩为4位：0..7保留页槽定义（OK、STALE、DIRTY、BAD、BUSY、EXHAUSTED、INCOMPLETE、FENCE_WAIT），8为后备UNREADY，9为后备FULL，10为IO_ERROR或内部协议故障。错误默认payload/present/tx为0；DIRTY保留dirty标志。不能把后备域状态码直接透传为页槽状态码。

参数TX_BITS、GENERATION_BITS取1..16，TAG_BITS取1..16；默认16/16/2。打包后备cookie时，将短事务号和generation零扩展到16位。默认23405后备frame，INDEX_BITS=15；本轮行为实例为4 frame（3位事务/代次）和512 frame（默认事务/代次）。硬件内存地址与页格式沿用后备服务契约。

调度输入dispatch_enable、execute_enable、fence_service_enable、ack_receive_enable只会暂停内部队列阶段，不授予排空权限。常规系统可全部置1；验证使用周期性背压。

## 写回、读取与地址租约

WB：先RESERVE后备地址，再向页槽申请WB事务；按offset 0..63逐条EXPORT并检查每条响应，将记录交给存储适配器。适配器校验完整记录后才启动AXI。等待成功内存响应且核对cookie/frame/published后，发送页槽COMPLETE；收到成功确认后才发地址RETIRE。RETIRE成功后向外返回成功和tx。

RF：先LOOKUP并要求published，不命中时返回UNREADY且不分配地址、不开启页槽事务。然后申请页槽RF，启动存储读取；解码器在整页规范检查和内存成功之后提供记录。每条记录先暂存在顶层寄存器，再发BEAT并等待成功响应，才接受下一条。第64条BEAT的成功响应、成功内存响应及cookie/frame/published检查全部满足后才发COMPLETE，再RETIRE。全部记录到齐之前页槽保持RF，不能被搜索读写。

若RESERVE成功但页槽WB申请失败，后备映射保守保留到fence，可能消耗容量，但没有内存租约或页槽传输事务。这也适用于无效绑定/已排空状态下的WB；因此错误优先级可能先报告后备FULL，再报告页槽错误。RF先LOOKUP，故不存在后备页时可能先返回UNREADY，而不是页槽绑定错误。未实现取消该保留映射的回滚。

外部成功WB/RF响应表示页槽完成和地址租约退休均已确认；不意味着flash持久化或电源故障安全。地址owner分配仍保留到fence，可供后续同owner RF使用。

## 两域回收

BEGIN_FENCE沿用页槽检查；有未写回脏页时返回DIRTY。调用者负责释放全部干净页。FINISH_FENCE先请求页槽端点确认：所有页槽空闲、页槽租约清零、内部请求/工作/响应及fence控制队列均满足排空条件。页槽成功响应后，再向后备服务发RECYCLE。

顶层 `fence_open` 跨越这两个阶段保持draining为1；页槽先退出draining不代表全系统已完成回收。后备RECYCLE返回成功且allocated、memory_leases均为0后，才清fence_open、返回FINISH成功。新QUERY在旧FINISH响应被消费前无法接受，因此有限事务号/代次的页域复用不会先于后备地址隔离结束。

证明范围是封闭、同钟、单发起者、合法握手的内部队列与单在途AXI引擎。未覆盖隐藏外部包、共享地址的另一DMA主机、CDC或非法从设备无限期不返回响应。顶层串行入口限制并发，现有四槽可保存多个工作页，但不会并行运行多个外部命令。

## 故障及恢复边界

底层内存故障或传输阶段异常导致fault；后续所有外部命令返回IO_ERROR，不能通过RELEASE、COMPLETE或FINISH释放故障租约。读AXI错误按已接受burst排空后返回；页槽不会COMPLETE，页槽和地址租约保留。AXI成功而页格式损坏同样不向页槽写入任何BEAT。

未预期的内部EXPORT/BEAT/COMPLETE响应错误、cookie不符或记录offset不符也封锁顶层。它们不自动回滚已接受的工作；本模块没有通用超时、丢包或热复位恢复。特别是内部故障的IO_ERROR不能普遍当作AXI已静止证明。冷复位必须由系统协调全部相关组件和内存接口，不能仅复位某一子模块释放隔离。

数据采用原始位模式，hist/设计占用/历史拥塞不在页记录中，不随connection页面回收。存储搬运正确不证明跨价格版本的距离值仍有效；价格版本和路由算法语义仍由上层负责。
