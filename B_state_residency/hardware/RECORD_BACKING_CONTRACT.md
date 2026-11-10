# 记录级后备存储适配器

`record_backing_service.sv` 可综合组合 `scratch_page_codec`、带LOOKUP的后备目录/服务及原AXI引擎。它在RTL内部控制记录校验、内存操作、解码提交与错误中止。原有已验证模块不变，目录/服务的新版本分别为 `backing_frame_directory_lookup.sv`、`backing_page_service_lookup.sv`。

## 命令与身份

单时钟、单命令在途，命令接受后保存全部参数；响应背压期间保持状态、frame、地址、published和cookie。返回响应被消费前不接受下一命令。page owner为24位 `{price4,query2,page18}`；cookie为64位 `{reserved5,kind1,tx16,generation16,owner24,slot2}`。记录流不单独携带cookie，所有记录归属于当前唯一命令。

| cmd_op（3位） | 操作 |
|---|---|
| 0 | RESERVE：查找或分配owner后备frame |
| 1 | TRANSFER：cookie kind0写回、kind1读取 |
| 2 | RETIRE：上游页槽完成提交后释放地址租约 |
| 3 | RECYCLE：上游fence完成后回收目录分配与事务隔离状态 |
| 4 | LOOKUP：仅查找owner，不分配frame |
| 5..7 | BAD，无副作用 |

状态码沿用后备域：0 OK、1 STALE、2 BUSY、3 BAD、4 FULL、5 OLD_TX、6 UNREADY、7 IO_ERROR。它们与页槽状态码含义不同，未来顶层必须映射，不能直接混用。

LOOKUP空目录或查无owner返回UNREADY、frame/address/published为0；找到owner返回OK以及其frame和published位（可能未发布）。不改变分配数、租约、事务历史、RAM或owner值。底层目录LOOKUP opcode为5，服务和适配器opcode为4。仍采用线性两周期/项扫描，没有索引性能改进。

## 写回顺序

1. 启动编码器，逐次接受offset 0..63的64条记录，包括absent记录。
2. 等待编码器首个raw输出valid。这只会发生在全部64条记录校验通过后；此时尚未向目录PIN或AXI发请求。
3. 发后备TRANSFER，保存且核验服务返回cookie。页流直接连接AXI引擎，无测试台提交控制。
4. 等待成功内存响应（全部B成功），再消费codec done并向调用者返回OK。

坏offset/padding或absent非零在第2步之前返回BAD，不发AW/W，不消耗事务号，不取得地址租约，也不置sticky fault。调用者随后可以用相同事务号重试规范页。PIN拒绝则在内存请求阶段返回服务原状态，并在RTL内中止codec。完整记录输入前即使地址/cookie最终无效，也可能需要收齐记录才能获得PIN拒绝响应；调用者不能等待地址接受后才提供记录，否则形成循环等待。

## 读取顺序

启动解码器后发后备TRANSFER。只接受来自AXI页流的记录字节，待成功服务响应且cookie相符，才驱动codec commit。codec独立校验整页规范格式。解码记录逐个受ready背压控制，全部64条被消费并得到codec成功done后，适配器才返回成功响应。

对AXI错误或PIN拒绝，RTL在服务响应后中止codec。AXI引擎负责排完已经接受的读burst；codec中止不替代该责任。对“AXI成功但页格式错误”，返回IO_ERROR并置本地sticky fault；不输出记录，即使目录此时已标记内存操作COMPLETE，也不能RETIRE。

成功内存操作并不自动释放地址租约；主机消费响应也不释放。只有后续RETIRE才能释放，必须由上层在页槽COMPLETE确认后发出。

## 故障与范围

任何后备引擎/目录fault或已读页格式错误使适配器进入故障封锁。所有后续命令均返回IO_ERROR，包括RESERVE、LOOKUP、RETIRE和RECYCLE；不得借释放一个底层COMPLETE租约绕过损坏页故障。恢复需要上层协调冷复位和总线静止。本模块没有超时、丢包恢复、运行中外部cancel或热复位证明。

上游不给完整64条写记录、不给输出ready或不消费响应时，允许一直背压；不能擅自终止已接受AXI事务。页格式只检测规范性，不是CRC/ECC。价格版本有效性与历史拥塞仍由上层维护。

默认容量23405个1344字节frame；原始页载荷池为31,456,320字节，未包括目录和codec内部存储。行为验证使用64-frame实例覆盖全部64种4KB偏移；默认容量通过整体综合，不等于全容量耗尽行为仿真。

本轮尚未组合 `queued_scratch_endpoint`，外部RETIRE和 `fence_retired` 仍是可信控制。下一层必须：WB先RESERVE再申请页槽事务并EXPORT；RF先LOOKUP已发布页再申请页槽事务并BEAT；内存/记录成功后页槽COMPLETE，再地址RETIRE；FINISH_FENCE成功且后备无租约时RECYCLE，在两者完成前阻止新query。该串接未完成前不得宣称完整设备排空、完整路由执行或硬件加速。
