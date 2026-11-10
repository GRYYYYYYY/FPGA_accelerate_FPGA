# 连接保存路径的 checkpoint 组件

本变体从已冻结的 `results/recovery_retry_normal_v1/sources/route_commit_controller.sv` 派生，默认两个连接slot、每slot最多32个内部路径节点。它补齐完整checkpoint需要的一类易失状态：后续ripup必须使用的路径、net、source/sink和design身份。原基线和系统顶层尚未改接本组件。

命令需要active、lease、无普通路由操作/待消费回复/错误/意外后端回复，以及调用方提供的cp_safe。cp_safe必须代表整个系统的物理和逻辑排空、无并发写且持有排他checkpoint权限；本组件不能自行证明外层服务的安全。命令与普通路由请求竞争时优先checkpoint；已接受的普通路由请求必须完成后才能接受checkpoint。导出/导入/回复持有期间不接受新路由命令。

每个slot固定7+MAX_PATH个little-endian 32bit字：valid、内部节点数、net、source、sink、design低32位、design高32位、内部路径数组。路径顺序沿sink到source，排除两个端点。无效slot全部输出零，有效slot未使用路径尾部为零。默认完整图像78字/312字节，8节点测试形状30字/120字节。MAX_PATH和格式版本必须记录在外层checkpoint描述符中。

导出先捕获暂存图像、逐字扫描语义，再产生固定index/last流。每个已暴露输出在背压、lease失效或取消后仍保持，直至消费者接收；发生错误时仍退休完整输出流，完成状态报2。只在全部输出已接受后提供最终CRC32/IEEE：初始ffffffff、每字按little-endian字节顺序、poly edb88320、最终按位取反。CRC用于传输完整性，不是来源认证。

导入接收严格递增index及精确最后一字last。全部数据先写入私有暂存bank；校验CRC、valid域、长度、net/node范围、design绑定、端点排除、内部节点唯一、无效slot/未使用尾部归零后，单个时钟沿同时发布两个slot及全部数组。错误返回1，中断或失去quiescence返回2；原已发布slot保持。对输入流已明确失败后调用方必须废弃余下旧流。部分导入期间reset只丢弃暂存；之后必须从匹配owner图像的有效checkpoint完整重放。

语义校验逐字扫描，每周期比较一对历史节点；最坏校验约2×((7+MAX_PATH)+MAX_PATH×(MAX_PATH-1)/2)个扫描周期，避免全部两两比较器并行展开。导出、校验和导入均阻塞普通路由，但不持有label/owner在途事务。没有内部checkpoint流超时；上层可撤销cp_safe或发abort。永久输出背压仍可阻止错误完成，不能撤回已暴露的输出。

本组件只保存路由路径。外层仍须把checkpoint身份、owner引用和allocator、design创建/children cache、history/价格、标签页与目录、配置描述和query序号、journal、frontier/控制器恢复策略绑定为同一一致状态。仅恢复路径不能修复不匹配的owner，也不能替代完整checkpoint或耐掉电协议。cp_design绑定不等于checkpoint版本/防重放验证，外层必须提供可信且一致的checkpoint描述。

验证使用真实q1/q2的CPU路径和label payload，label/owner服务为注册mock。两条同网路径具有两个共享资源；控制器reset时owner模型保留，导入后ripup将共享refs从2降1再降0，且不读取label。8/32容量均保留原25项回归，加保存/恢复相关路由检查共31项、checkpoint27项。包括CRC/order/last、8种语义损坏、原子替换、部分输入取消、导出背压期间失去权限、错误描述、部分bank reset、空图像规范化和普通请求退休；另用合成满长度路径验证最后一节点、重复检测及失败替换保持原路径，此合成路径不证明图拓扑有效。

入口：

- `python3 hardware/variants/route_checkpoint_v1/build.py`
- `python3 hardware/variants/route_checkpoint_v1/build_tb.py`
- `python3 scripts/run_route_checkpoint.py NEW_RESULT`；加`--max-path32`验证默认32节点容量。
- `python3 scripts/audit_route_checkpoint_extended.py RESULT`
- `python3 scripts/prepare_route_checkpoint_synth.py NEW_SYNTH_RESULT`

这是组件级验证。后续须接入adapter、系统围栏和真实AXI owner链，验证与标签/owner同一快照的保存、复位恢复及连续路由。综合是默认32节点组件OOC，没有板卡速度或完整系统资源结论。
