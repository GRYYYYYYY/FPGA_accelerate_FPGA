# 冷恢复启动门控

`boot_required` 必须在 cold reset 时由可信调用方置 1。业务从复位保持关闭；boot descriptor 成功受理后，仅六配置端点、控制/标签 IO、协调器配置、保存配置和 authority bind 可用。query/route/recovery 与其余 host 业务不放行。显式普通启动模式为 required=0，不构成安全启动认证。

描述包含完整 design64/generation64/checkpoint32、active version/query/price、有效配置、标签 count/CRC、路径/query CRC 和保存 slot mask。六端点、协调器与保存配置共八个配置回执来自实际 host 请求和成功回复，且请求逐位匹配描述。owner 与 authority 绑定、全部 provider 状态和 active 上下文须同时一致。

标签经真实 native IO 重建目录；硬件观察随后已消费的读回复，要求 present/status 成功、node 严格递增且界内，CRC32/IEEE 覆盖小端 `(node,5 label words)`，数量和 CRC 都一致。路径和查询资格来自实际 import 命令及已消费的成功回复，而非主机 done 标志。任何配置/控制重写或标签写入都会取消所有已收集标签/path/query 资格和此前在途导入；失效操作优先于同周期回复。恢复中 work reset 重回等待描述，不能开放 RUN。

所有回执齐备、服务完全退休且实际 checkpoint lease 持有后，产生完成回复。回复背压期间所有管理修改和业务都保持关闭，lease 不能释放。完成回复消费后才切到 RUN；随后另行释放 lease。描述和组件恢复必须由单个串行 bootstrap writer 驱动，遵守原 transaction fence 协议。

组件 XSim 检查31项。系统实验从已提交 G2/checkpoint18 bundle 启动全新实例，加载实际 warm owner/design/cost，空 labels DDR 经 IO 重建328条记录；读取 config_effective4，原生导入 path/query。旧 seq1 在空闲 slot1/合法上下文被拒绝且 prepare/commit 为0；seq2 对照既有独立 CPU oracle，43poll/42expand/176candidate，再双路径共享 refs1→2、两次 ripup2→1→0。32槽/单槽均功能通过，并独立重放全部八路 AXI 字节。

该 fixture 为 capacity0/同网两路径，快照最初仅 slot0 有效。预载 DDR 与 fsync 包处理是主机参考流程；不是 FPGA 自主 DMA 恢复或断电测试。尚无该门控的新综合/时序/板卡结果；不宣称实测加速。仍缺运行中 authority 换代、任意多net/overflow快照、持久化 anti-replay/认证和未知页/价格/回绕等通用验证。
