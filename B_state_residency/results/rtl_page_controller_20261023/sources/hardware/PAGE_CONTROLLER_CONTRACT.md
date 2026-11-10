# scratch_page_controller 传输端点契约

组合冻结的 `scratch_frame_store_bram.sv`，默认4槽×64节点，136位标签、160位规范记录；hist始终不在标签中。新增控制器不暴露原始CLEAN/LOAD指令。默认事务/槽代次16位，查询2位，价格4位。一次接受一个命令，响应背压期间不接受下一命令；不同槽最多4个未完成传输，可乱序完成。单时钟、冷reset，不包含AXI、DDR/HBM、网络重传或热复位恢复。

## 编码和状态

命令完整绑定为(slot,page,query,price,generation)，传输另带(tx,kind)，kind=0写回、1换入。状态0 OK / 1 STALE / 2 DIRTY / 3 BAD / 4 BUSY / 5 EXHAUSTED / 6 INCOMPLETE / 7 FENCE_WAIT。无效操作无状态副作用。错误payload/present/tx为零；DIRTY错误的dirty=1，其余错误dirty=0。

|op|含义|
|---|---|
|0 QUERY|建立当前query/price。query数值在一次排空周期只能使用一次；不能以新价格重复使用同一query。旧绑定和未完成传输保留，但搜索不可见。|
|1 BIND|为当前查询绑定空槽，清节点有效图。每槽generation必须严格递增（首次可为0），到上限后不回绕。|
|2 READ / 3 WRITE|只对当前查询的LIVE槽操作；同步RAM，非法字段/target值由存储层拒绝。|
|4 RELEASE|仅LIVE且clean槽可解除，旧查询允许释放。generation仍隔离到fence。|
|5 WRITEBACK|冻结LIVE槽，并返回从0开始、不回收复用的tx；允许旧查询脏槽写回。写回期间搜索和释放都拒绝。clean槽也允许导出。|
|6 REFILL|只接受当前查询、刚绑定且尚未写入/换入的pristine槽；分配tx并隐藏整个页。|
|7 BEAT|完整换入描述符匹配，offset未接收过；present=1装入规范记录，present=0必须payload=0且不置节点有效。重复位置拒绝。|
|8 COMPLETE|完整描述符匹配且64个offset全部传完；换入才转LIVE，写回才经内部CLEAN转LIVE。重复完成STALE。|
|9 EXPORT|完整写回描述符匹配，逐位置返回记录和present，未有效位置返回0。64个offset全部导出前不能COMPLETE。每个位置只接受一次。|
|10 BEGIN_FENCE|拒绝仍有未开始写回的LIVE脏页。成功后撤销当前查询并阻止QUERY/BIND/新传输；允许既有传输继续BEAT/EXPORT/COMPLETE以及clean RELEASE。|
|11 FINISH_FENCE|必须已draining、全部槽FREE、peer_quiescent和ingress_empty均为真；才清事务分配计数、已用query与generation隔离。结束后必须重新QUERY。|

脏页不能因开始fence而丢弃；先启动写回或写回完成再开始。传输失败/丢包可永久阻塞本原型，未加入取消、超时或重试。旧查询换入可以在内部结束，但当前query比较持续阻止搜索读取，直到释放；不会重新发布给新查询。

## 外部前提与尚未实现

COMPLETE表示可信传输适配器已经完成操作：写回数据与有效图已在后备存储可见；换入数据全部来源于同一描述符。EXPORT响应被消费只说明交给适配器，不能自行产生持久完成。present位流包含64个位置，因此全空页和真实零值节点可区分。没有外部地址池/地址租约RTL；软件固定后备池的隔离语义仍待接入。

FINISH_FENCE的两个输入是同步、可信的适配器证明，必须覆盖所有请求、执行单元、响应、重复包和控制ACK。当前RTL只验证本地槽/租约为空；**尚未实现远端fence tag/ACK队列状态机，也没有证明真实链路已排空**。陈旧的相同有限token包如果在虚假排空后重新出现，无法仅靠描述符比较识别；不能把本模块当成已经完成整条DMA fence。输入需来自同一时钟域；跨时钟需要另行验证。

reset丢弃绑定和待响应，只适用于整个端点/传输域同时冷启动。设计级占用/历史/价格计算均在模块外；价格字段只做精确匹配，未证明路由价格有效性。

## 验证计划

独立Python字典/传输集合模型产生公开端口刺激；TB在接受后污染所有输入、每13条响应背压4周期并同时尝试下一请求。小位宽实例3位tx/gen验证耗尽拒绝及多次fence后复用、4槽乱序完成、所有描述符字段失配、早完成/重复节点/重复完成、旧查询与排空；默认16位实例使用19个完整真实小查询56588字段事件，经4槽置换产生全页EXPORT/BEAT与完成。每次真实读按原始float32位验证，不能用吞吐估计替代实际加速。

执行通过之前，此文件仅为契约和测试计划，不是测试成功证明。
