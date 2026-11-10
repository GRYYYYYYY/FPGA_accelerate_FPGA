# 不可变图 CSR / 属性 AXI 读取器

实现：`variants/graph_reader_v1/graph_static_reader.sv`。单时钟、单请求、单个 AXI 读拍在途；仅提供原始图服务，不进行过滤或修改设计状态。已验证的数据来自 `results/graph_image_20261024`，包含 9,089,009 节点、40,469,536 原始有序边。

## 配置与布局

冷复位后通过 cfg valid/ready 配置三个 64 位基址、32 位节点数 N 与边数 E。成功后锁定至协调冷复位。cfg response 有背压，未退休前不接受业务。配置失败可重试；状态 0 成功，1 基址非 64B 对齐，2 N 超出 1..2^24 或地址范围溢出，3 非空表窗口重叠。

三表内容均小端：offsets 为 N+1 个 uint32，edges 为 E 个 uint32 节点 ID，attrs 为 N 个 32B 原始记录。各表物理窗口向上补齐 64B；主机必须分配完整补齐空间。E=0 时 edges 空窗口可与其他窗口重叠。65 位范围计算允许末字节恰为 2^64−1，不允许回绕。当前 AXI 文件模型补齐字节为零，读取器只使用合法表项。

attrs 保留全部 256 位（含原 flags bit16 和浮点 raw bits）；初始属性中的 created 标志不能替代运行中设计级 created。offsets/edges 是原始 CSR，不能当成已过滤的 getChildren 缓存。

## 请求与响应

请求字段 op[1:0]、cookie/node/index[31:0]。op0 META 要求 index0，返回当前节点原始属性以及 CSR start/count。op1 CHILD 先读父节点实际 offsets，再验证 index<count，读取原序 child ID 及其属性；响应仍带父节点 start/count。不去重、不排序、不缓存 CSR 度数。

每个响应回显 cookie/parent/index，返回 status[3:0]、node/start/count、attrs[255:0]。所有错误响应的数据载荷为零。必须在 `rsp_valid && rsp_ready && status==0 && !fault` 时使用成功数据。已提供的响应在背压下保持；之后发生 fault 也不会改写已提供内容，故 status0 不能独自代表有效。

| status | 含义 | 后续行为 |
| --- | --- | --- |
| 0 | 成功 | 响应退休后接下一请求 |
| 1 | 未配置 | 不读 AXI，可随后配置 |
| 2 | op/node/META index 非法，或 CHILD index≥实际度数 | 前者无 AXI，后者只读 offsets；可继续 |
| 3 | RRESP 非 OKAY、RID 非0、RLAST 缺失 | 锁存 fault，停止 |
| 4 | offsets/child 数据非法 | 锁存 fault，停止 |
| 5 | 活动请求地址阶段出现无归属 R | 锁存 fault，停止 |

检查 first≤last≤E；node0 要求 first0，node N−1 要求 lastE；child<N。这里是每次请求的局部验证，全图一致性与来源由外部 graph image 审计保证。cookie 由调用方分配并核对，本模块只回显，不管理 generation 或跨复位旧消息。

## AXI 与故障边界

ARADDR64、RDATA512、固定 ARID0/ARLEN0/ARSIZE6/ARBURST1。每次读 64B 对齐单拍，不跨 4KiB；offsets 的父节点索引模16为15时用两拍读取边界对。通常 META 两拍、CHILD 三拍；跨 offset 拍增加一拍。当前无行缓存、预取、多个 outstanding 或突发合并，不能据此推导性能收益。

AR/R 按握手前进；同拍接受 AR 时可以提供 RVALID，读取器下一拍才拉 RREADY，AXI 从端必须保持返回。无请求的 R（含成功结果背压时）锁存 fault；空闲时不制造业务响应。故障后不再发起请求或继续总线活动，无超时、重试、热取消或后台排空；只能在外部协调 AXI/上下游静止后冷复位，不能当成可独立热复位的 AXI 主设备。

## 已验证与后续接入

`results/graph_reader_20261024`：真实文件 AXI 模型，独立 Python 原始字节 oracle；10,163 个抽样父节点、64,806 次请求，含全部 8,875 个 CSR offset 4KiB 边界、每种实际度数、16 种 offset 对齐、两种 attrs 半拍、重复边与首尾。逐笔 AR 和响应日志由 `scripts/audit_graph_reader.py` 再读取原文件核对。另有未配置/坏请求、配置拒绝、64 位末地址配置、背压、19 组总线/图数据/无归属 R 故障和冷恢复。

当前验证不是遍历全部 9M 节点的 RTL 回归，未验证板上内存、上传或完整路由。下一层应由 META 的真实 count 决定构建参数；NEXT/CLASSIFY 等应绑定父节点、位置和构建 generation。还需设计级 created/dead、持久首次过滤缓存、整构建 query/price 保护与实际 paged_exclusion 服务。查询标签回收不能清除这些设计状态。
