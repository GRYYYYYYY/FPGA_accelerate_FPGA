# scratch_frame_store 页槽契约

当前验证实现为 `rtl/scratch_frame_store_bram.sv`；`rtl/scratch_frame_store.sv` 保留为行为通过但RAM推断失败的对照。两文件定义相同模块，构建时只选择其中一个。默认4槽、每槽64节点、18位page、2位query、4位price、16位generation；其他参数组合未验证。

每个槽保存绑定及64位节点有效图。RAM每节点136位，依次为lb原始float32位、upstream原始float32位、prev int32位、visited int32位、target字节。接口按160位记录传送，高24位必须为0，与软件20B记录对齐；`hist`不在该存储中。RAM数据不清零，未有效节点读取全0，只有有效图在新绑定时清零。

命令与响应各使用valid/ready握手，一次只接受一个未完成命令。响应背压时所有响应字段保持稳定，期间不接收新命令。READ/WRITE使用同步RAM读及后续处理周期；没有承诺每周期接收一次访问。

|op|操作|条件与效果|
|---|---|---|
|0|BIND|槽必须未绑定；保存完整绑定，清有效图与dirty，不清RAM数据。|
|1|READ|完整绑定相符；返回160位节点记录、present及槽dirty。无效节点返回全0且present=0。|
|2|WRITE|完整绑定相符；只改指定字段，首次写入从全0记录开始；置present和dirty。target写值必须不超过255。|
|3|CLEAN|完整绑定相符；由外部可信控制器在写回已完成后发出，清dirty。模块自身不验证DMA完成。|
|4|UNBIND|完整绑定相符且dirty=0；解除绑定。dirty页被拒绝，不丢数据。|
|5|LOAD|完整绑定相符、dirty=0、padding=0；装入一个有效节点并保持clean。外部控制器负责整页恢复的完整性与可见时机。|

状态：0=OK，1=STALE（未绑定或任一绑定字段不符），2=DIRTY，3=BAD（非法操作/字段/载荷），4=BUSY（覆盖已有绑定）。错误操作不修改页状态。响应数据只在READ/WRITE/LOAD成功时有效；DIRTY拒绝返回dirty=1，其他错误的响应辅助字段为0。

reset是同步冷重置，丢弃绑定、dirty和待响应命令；不支持运行中恢复。外部控制器还必须保证有限ID/槽代次复用前的完整fence、写回/refill描述符租约、重复完成去重和旧命令隔离。同一有限token回绕后旧包与新包无法仅靠比较字段区分，因此本模块的绑定比较不能替代已经验证的软件排空协议。LOAD与搜索之间的整页发布屏障也尚未在RTL实现。

当前自检包含29个定向命令，以及从19个完整真实小查询产生的98322条命令，原始字段访问56588次；8,992次导出READ在CLEAN前逐值比对，15,672次LOAD模拟恢复。外部后备数据来自参考映射，未实现DDR/HBM或DMA。固定插入17,358个响应背压周期。覆盖默认实例的零值、浮点位模式、逐字段保持、非法操作、绑定失配、dirty保护和旧RAM隐藏；不宣称全参数、形式化、CDC或物理时序证明。

执行与证据：`python3 hardware/scripts/verify_scratch_bram.py` 创建新目录，运行XSim和独立综合；随后用 `python3 hardware/scripts/report_scratch_rtl.py <运行目录>` 核验完整阶段、源码/轨迹/产物哈希、终态PASS及BRAM映射。详见 `../results/rtl_scratch_20261023.md`。
