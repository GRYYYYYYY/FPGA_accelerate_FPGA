# 坐标服务契约（coordinate_v1）

本服务连接实际 `graph_static_reader`、`geometry_table_reader` 和 `paged_exclusion_engine` 的通用标签端口。当前语义为 resident_zero；不把它等同于 dense 初值策略，也不包含完整搜索、设计级占用/价格或路由提交。

## 请求与返回

每次仅一个在途请求，ready/valid 握手。请求快照包括 op2、node32、cookie32、query2、price4。响应回显所有身份字段，包含 status4、attrs256、y/slr/next/prev_column/label_prev32、north/prev_read/prev_present。响应在背压期间保持；只有 `status==0 && fault==0` 可使用。

| op | 功能 | 动态服务 |
|---|---|---|
| 0 | ENDY | 读节点属性；SLL 再读 prev，必要时读前驱静态属性 |
| 1 | SLR | 先求 ENDY，再读取该 Y 的 `[SLR,north]` |
| 2 | LAGUNA | 按节点静态 endX 读取 `[next,prev]`；不读取标签 |
| 3 | STATIC | 返回原始 32 字节节点属性 |

SLL 是原 RouteNodeType 数值 5。`prev == 0xffffffff` 表示无前驱，返回本节点静态 endY。其他合法 prev 必须读取前驱**静态** endY；与本节点静态 endY 相等时返回本节点 beginY，否则返回本节点静态 endY。前驱即使也是 SLL，也不递归解析。空标签完整 payload 为零，prev=0 是真实节点 0；presence 不用于将它重解释为 −1。非 SLL 不读取 prev。prev 写入后的坐标需要重新请求，不缓存过期动态坐标。

## 生命周期与所有权

host OPEN/CP/CLOSE/标签写和坐标请求互斥。`host_pending` 从接受主机命令保持到其响应退休；坐标 busy 从请求接受保持到响应退休。坐标工作期间拒绝主机控制和标签修改。OPEN 清理本查询标签，CP 保留标签语义，CLOSE 结束所有权。设计级 occupancy/history 不在该清理域内。

active/query/price 在受理后的整个操作和响应退休前保持不变。每次图或表调用使用递增 token；不允许回绕。标签服务无回显 token，依赖包装器对单一端口的独占和正确响应路由。默认 TOKEN_BITS32/MAX_CYCLES262144；超时不累计已给出响应后的背压。

| status | 含义 | 行为 |
|---|---|---|
| 0 | 成功 | 仍须检查 fault |
| 1 | 节点越界，或无列时请求 LAGUNA | 可恢复，未发服务请求 |
| 2 | inactive 或 query/price 不符 | 可恢复，未发服务请求 |
| 3 | 服务错误或空标签 payload 非零 | 停止 |
| 4 | 图/表回显身份不符 | 停止 |
| 5 | abort、服务 fault、无归属响应、owner 改变、超时 | 停止 |
| 6 | token 耗尽 | 停止 |
| 7 | prev 非 −1 且越界 | 停止 |
| 8 | Y/X 负值或超出对应表 | 停止 |

错误响应中的数据可能来自已完成的部分步骤，不保证清零。若响应已经对外有效，随后发生故障只锁存 fault，不能改写已暴露响应；消费者必须同时检查 fault。停止后不能接受新请求，需协调冷复位所有服务并排空/取消旧 AXI 事务；单独清控制器不足以安全恢复。

## 表与地址

行记录为 little-endian `[SLR_i32,north_i32]`，列记录为 `[next_i32,prev_i32]`，每记录 8 字节。保持原 INT_MAX/INT_MIN 柱哨兵。行数 1..65536，列数 0..65536；没有 Laguna 时列文件为空，north 归一为 0。

配置两段 64 字节对齐且不重叠的地址窗口，尾部按 64 字节补零。成功配置后锁定到冷复位。图和表 AXI 地址 64 位、512 位数据，单 beat；分页后备端口沿用当前 32 位地址。测试的图/表地址均超过 4 GiB。

表配置 status 1 对齐错误、2 数量/地址溢出、3 重叠。表请求 status 1 未配置、2 越界，可恢复；3 RID/RRESP/RLAST 错误、4 north 非 0/1、5 无归属 R，锁存 fault。该表读取器自身不含超时，组合控制器提供操作超时。

## 证据范围

`coordinate_service_v2_20261024`：合成 740、真实 23957、单槽压力 740 请求，冻结源码独立审计通过。真实图覆盖全部 11520 SLL；合成图覆盖 Laguna 表及默认值反例。使用实际分页/HLS/native/AXI，功能目录 FRAMES16384/INDEX14/HASH15；默认综合参数为 FRAMES163840/INDEX18/HASH18。

`coordinate_boundaries_20261024`：控制器 40、表读取器 17 项，服务接口注入模型，实际缩位 token 耗尽与 64 拍超时。`coordinate_integration_boundaries_v2_20261024` 实际组合7故障/7恢复通过。默认容量实际OOC综合17873LUT/14570FF/375BRAM/3DSP，零组合环，尚未布线；详情见 `results/coordinate_service_20261024.md`。

原始 loader 对真实 311 行表逐项核对通过。原始 Router/SparseLabels hot0/hot1 反例证明 dense 默认 −1 返回 Y70，paged 空记录 prev0 返回 Y10；将前驱显式写 −1 后恢复 Y70。该差异在本次真实图的初始空标签 SLL 上未触发，不构成其他设计或完整 dense 路由等价证明。
