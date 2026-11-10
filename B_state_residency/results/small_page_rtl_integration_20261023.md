# 8节点页RTL接入约束

参考语义已通过38个真实查询，现有RTL仍冻结在64节点/4槽版本。新增独立smallpage模块链，不修改正在回放的源。

|部分|现有约束|新方案要求|
|---|---|---|
|驻留store|已有SLOTS/SLOT_BITS/OFFSET_BITS/PAGE_BITS参数|32/5/3/21，验证BRAM及标签行为|
|controller/queued/top|2位槽、18位页、6位offset、4位租约|全链5/21/3、32位租约；检查队列payload位域|
|cookie|64位，59位有效|72位传输、65位有效、7位保留零|
|owner目录|24位price/query/page|27位完整owner；哈希仅作索引，比较不得截断|
|后备帧|23405帧、15位索引、1344B步长|30MiB/192B=163840帧上限、18位索引；实际需求59843帧，默认池容量与目录资源另评估|
|codec|64位bitmap、64记录、21beat|8位bitmap、8记录、3beat；保留整页检查后commit|
|AXI|固定21beat和4KiB分拆|3beat，仍需跨4KiB边界分拆及错误排空|
|checkpoint|4槽预留6事务|32槽预留34事务，保持排空/ACK/独占query条件|

新cookie低到高：slot[4:0]、page[25:5]、query[27:26]、price[31:28]、generation[47:32]、transaction[63:48]、kind[64]、reserved[71:65]。不能仅把原cookie低64位复用：kind会丢失；check_small_page_cookie.py已构造该碰撞，10002组往返及17个非法边界检出。

192B页面：byte0 bitmap；byte1..160为8个20B记录（每条低17B有效、后3B零）；byte161..191零。此格式记录未按32位对齐，旧word codec不能直接缩短循环，需重新处理跨word拼接。先实现codec及AXI独立测试，再扩展目录与端点，最后同轨迹回放和综合配对。

参考模型与布局契约不等于RTL验证或性能结果。即使数据容量固定，32槽控制与更大目录资源仍需实测。
