# 真实首次扩展与缓存重放组合

实现 `variants/expansion_v1/node_expansion_engine.sv` 和 `expansion_controller.sv`，组合已冻结的 graph_static_reader、design_state_store、children_build_engine（实际HLS）及paged_exclusion_engine（实际HLS/原生标签后备）。不再使用模型服务替代NEXT/CREATE/CLASSIFY/EMIT/排除/发布。顶层仅实现getChildren等价的邻接扩展与重放，尚不计算新距离或进行完整图搜索。

## 初始化与存储

graph与design分别通过原cfg valid/ready接口配置，不改变组件ABI。节点数必须一致，顶层记录各自实际接受的N；均配置成功但N不同时锁存fault，无业务响应。图三表和设计后备在设计运行中不可由其他写者修改。graph/read-only AXI64、design/read-write AXI64、labels/read-write AXI32为三个独立外部接口；平台尚未聚合或设置labels高地址基址。主机须保证实际后备缓冲区有效且彼此不别名。

真实设计初始化：`results/expansion_inputs_20261024`。原CPU Router loader与独立Python逐字节解析design_suffix同时得到27,960 nets、180,326 connections、180,326个sink节点（主sink和所有非负alternate sink）；hasLaguna=0。initial_design.bin为16B/node的零记录，再设置所有sink的flags bit3，其余字段为零；这是先清零再导入sink的主机初始化映像，没有设备上传器。设计内存不随查询清除。有效created在服务中计算为图初始flags bit0 OR设计记录created增量。

图count以META结果为准，当前mask容量32，真实全图最大度18；超过32返回不可支持且不CLAIM，不截断。请求中的has_laguna必须匹配该设计元数据（目前输入0），调用方负责正确提供；模块只检查0/1并在扩展期间锁存。prune也是0/1，缓存hit不会因后续prune或标签变化而重滤。

## 主机与扩展协议

- `host_ctrl_*`、`host_io_*`转发原pager查询生命周期/标签IO。主机控制优先于IO，主机命令被接受后保持pending直到相应回复退休；pending时不接收扩展。
- `expand_valid/ready`输入cookie/parent/prune/has_laguna各32位。只有两个存储配置成功、pager查询active、无主机命令/回复在途时接收。
- 从接收扩展开始，经过META、CLAIM、构建或hit重放、输出背压，直到最终result退休，**所有host ctrl/io入口保持禁止**。覆盖整个扩展，不能只依赖单边pager锁。
- 所有服务都使用锁存的active query/price。活动期间pager失活或上下文改变视为故障；外层不允许在相邻EXCLUDE之间改标签。

正常流程：META得到父属性和真实start/count，设计CLAIM使用外层owner。hit直接取持久mask；miss才START children HLS，完成全部服务并成功PUBLISH后，再重放该mask。每个输出位置重新读取实际CSR child和全部原始属性，保序/保留重复边；额外检查父start/count未变化。

`out_valid/ready`输出node32、position32（原始CSR位置）、sequence32（从0连续）、attrs256。字段在背压下保持。每个成功输出都在缓存发布之后。全部置位位置退休后，`result_valid/ready`返回status4、detail/cookie/count/raw_count/mask各32位及hit。count是本次已经输出的条目数，与mask popcount一致。所有成功数据须在fault=0时使用；故障后整个搜索运行需停止，不能继续使用已经消费的部分邻接输出。

## 服务行为

| HLS phase | 实际服务 |
| --- | --- |
| NEXT0 | graph CHILD读原序child/属性；design GET读created/dead/sink。结构dead为preserved OR已dead OR INACCESSIBLE OR未被目标使用的exclusive sink |
| EXCLUDE1 | 把原始flags、合并的created、稳定parent/child/hasLaguna交给实际paged_exclusion；其条件标签读取走原生分页存储 |
| CREATE2 | design CREATE幂等写created增量，成功后才继续 |
| CLASSIFY3 | 使用同一串行owner下缓存的child属性与最新CREATE回复；返回INACCESSIBLE和dead位，不改变副作用次序 |
| EMIT4 | design EMIT设置原始位置；独立核对mask递增及emitted计数 |
| CHECK_DEAD5 | 重新GET父状态，结合sink、exclusive sink类型、pinfeed/pinbounce/Laguna属性计算原canBeDeadEnd |
| MARK_DEAD6 | design DEAD幂等设置父dead |
| PUBLISH7 | design重读父记录、写valid/count/mask、等成功B；核对claim已释放及mask完整，再答复HLS |

重复child在下一次NEXT重新读取设计状态，能够观察前一次CREATE；CLASSIFY不会把初始created当作动态增量。空结果也必须PUBLISH，之后hit完全绕过HLS与排除，不重新读取查询标签。

## 所有权与耗尽

外层owner32在接收合法范围扩展时递增，先于CLAIM；HLS generation由START后取得，二者不是同一编号。图/设计/排除命令再使用独立共享token32，每次实际服务请求都递增，回复须精确回显。graph还核对parent/index，服务阶段核对build parent/count/prune/query/price/position/node；children引擎自身继续核对generation和阶段影子。

owner与token都不回绕，最大值后停止。TOKEN_BITS/OWNER_BITS默认32；直接实际RTL缩位验证包括token4到15后在未完成claim中拒绝继续、owner3完成7次扩展后第8次在发图请求前停止。HLS内部generation也有独立耗尽机制。没有热重置编号或旧消息跨冷复位隔离协议。

## 状态与错误

status0成功；1坏parent/prune/hasLaguna或图META输入拒绝；2度数大于32（detail为实际度数）；3编号耗尽（detail0 owner、1 token）；4子系统/上下文/无归属回复故障；5回复/服务结构不符；6无独立fault的HLS错误结果。子模块fault优先聚合为4，未承诺把每个子模块错误码逐一透传。

可恢复输入拒绝不取得设计claim；其他错误锁存fault与busy并禁止新的主机或扩展请求。服务错误不回滚已完成CREATE、DEAD或物理写入；尤其PUBLISH B失败时物理valid可能已经写入，仍保持claim并终止。不要在同一个部分修改的设计状态上重跑过滤。恢复需要协调总线和所有子模块停止，重新初始化整个设计运行；本轮没有中途恢复协议。

已提供的最终result遇晚到故障时不改字段，fault单独标识无效；已提供的out遇故障时保持至退休，之后返回错误最终结果。消费者必须始终检查fault，不能仅按status0消费。空闲时发生配置/后台故障不编造业务结果。没有外部内存超时、热取消、多扩展并发或多主一致性保证。

## 验证范围

`expansion_20261024`：原CPU完整loader/getChildren仅加入观察hook；1212真实扩展/550缓存hit/3229子节点、662首次构建/10753服务，含查询切换、显式checkpoint、标签写入后缓存重访、prune切换。16先导、默认32槽和单槽TX6/GEN3压力均通过。逐事件独立语义重放、所有AXI字节及最终145424192B设计后备核对passed；原生标签READ的完整160位/present也由独立字典核对。压力27checkpoint（其中显式2），设计状态与默认一致。

`expansion_boundaries_20261024`：15组输入/配置、graph/design真实AXI错误、强制pager fault、三类错token、最终/流输出背压故障、真实缩位耗尽。每组从全新初始化后备开始，未复用失败设计。独立审计核对错误B物理写入和保留claim。旧组件的各自故障回归仍保留。

功能仿真FRAMES256，完整默认综合FRAMES163840；图/设计/标签三路均为文件模型，非板上内存。没有完整连接搜索回放、距离/代价/Frontier/回溯提交、占用/历史拥塞服务或平台/XRT验证。不要把本轮功能虚拟周期或先前状态端点9.5213%消融收益解释为此组合的路由加速。
