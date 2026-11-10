# 实际Config14元数据服务（metadata_v1）

`metadata_service`组合实际graph_static_reader、design_state_store和metadata_controller，从三个节点的原始静态属性及child当前设计状态构建448位Config14。它已经独立验证和综合；尚未与node_expansion/共享访问控制器串联，也没有连接真实pager活动信号和实际owner配置输出。本阶段这些上下文是模块输入，不能称为完整设备搜索。

## 请求、来源及输出

请求快照包含cookie/parent/child/sink/net/sequence、flags32、xmin/xmax/ymin/ymax，以及query2/price4。flags只允许PRUNE1、BB4、NORTH8、SOUTH16、HOT256（mask0x11d）；DEAD、Laguna和Pinbounce由设备读取产生，外部注入这些位返回输入错误。坐标和边界均保留原int32位模式，不添加原算法没有的边界顺序限制。

依次对parent、child、sink发graph META，验证cookie/parent/node/index回显，然后对child发design GET。每次服务分配独立token32，整个运行不回绕；默认TOKEN_BITS32，缩位3的实际RTL已经验证在第二请求的设计GET前耗尽。重复node也保留三个META的先后顺序，不用未经验证的cache取代来源。

| Config字 | 来源 |
|---|---|
| 0 sequence | 请求快照 |
| 1 flags | 请求mask0x11d OR design.dead×2 OR parent.Laguna×32 OR child.Laguna×64 OR child.Pinbounce×128 |
| 2/3/4 child/parent/sink type | 对应raw attrs字节8，零扩展 |
| 5 child endX | attrs offset14的int16符号扩展 |
| 6 child tile / 7 sink tile | 对应attrs offset0的原32位 |
| 8/9 sink beginX/beginY | attrs offset10/12的int16符号扩展 |
| 10..13 xmin/xmax/ymin/ymax | 请求快照 |

响应同时回显完整请求身份、Config14及created。created为图初始flags bit0 OR设计增量created；两者都假时拒绝该child并停止。元数据调用者须提供已经经过getChildren创建/筛选的child；本服务只验证范围和created，不验证parent→child是否为一条已过滤CSR边。测试候选child来自原CPU配置fixture，未接实际扩展输出。

当前eager RRT输入的type从loader运行时type数组同源导出，hot静态副本须与该权威图一致。lazy JNI加载sink时会覆盖exclusive type，未来必须支持该覆盖或使用更新后的权威属性，不得把本eager验证扩大到所有lazy输入。

## 设计生命周期和仲裁

设计记录仍为原16B flags/count/mask/reserved；created、dead、过滤cache在设计内持续，metadata只执行GET。host_design接口转发原设计命令；CREATE/DEAD/PUBLISH等待实际成功B后回应。design claim未释放时不接metadata请求，确保getChildren构建发布之后才取快照。

meta_pending寄存器从请求接受保持至最终响应退休。此期间禁止host_design任何操作，包括后端读取间隙和结果背压。主机命令从接受到回复退休保持host_pending，禁止metadata请求；主机请求在空闲同周期优先。响应路由使用这两个握手所有权寄存器，未使用包含fault的busy作为归属来源。

父/child/sink图不可在设计运行中被其他写者修改；设计后备仅允许本design_state_store写入。下一阶段与node_expansion必须共享同一设计存储及claim状态，不能把两个独立store指向相同后备就假定其本地claim自动一致。

dead是设计内单调状态。原随机配置fixture会对相同child给出dead0/1，因此本回归在每个child内先执行dead0再执行dead1，保持原每例Config14和值不变，而不按query清dead。CREATE/DEAD由真实主机设计命令准备，仍属于测试中的上游副作用模拟，不代表已接children HLS。

## 配置和上下文

graph和design使用原配置接口，分别保存其实际握手的nodes。owner_configured/owner_nodes应来自上层实际owner服务的已接受配置。三者均配置后，nodes不相等会fault并拒绝请求，不制造空闲业务回复。原cfg输入在接受后改变不改变held nodes，已经实际验证。

这里检查的是节点数一致，不是设计身份；上层仍须保证全部区域属于同一设计且物理窗口不别名。任何设计切换必须协调全部模块及后备，不能只将owner重新配置为另一个相同N设计。owner上下文在metadata在途时失效会停止。

active/query/price在请求接受时匹配并持有至响应退休；中途变化或claim意外出现均fault。当前默认整体预算262144拍，最终响应背压不计入；已接受的图/设计读取由pending标记继续接收排空，即使元数据错误回复已经暴露。图leaf一次META本身含多个64B读拍，可以在错误后完成该已接受服务，不能仅凭元数据错误回复立即撤掉总线对端。

## 状态和恢复

status0成功、1非法node/外部flags（无AXI，可继续）、2初始活动归属错误、3服务非零状态、4回显错误或child未创建、5fault/abort/漂移/无归属服务回复/超时、6token耗尽。除输入1外锁存fault；raw leaf的fault优先聚合为5，所以物理R错误不承诺逐层透传raw码。

已暴露的响应字段不因late fault改变，必须同时检查fault0。服务cookie和所有请求身份保留至退休；接受后的源输入改变不影响快照。完成与超时同拍时失败优先。设计B错误可能已经改变后备；没有回滚或任意局部热复位保证，恢复需协调总线并重新加载设计。

## 验证范围

`metadata_v2_20261024`：11664合成、512真实图、614抽样，共12790份/179060字逐位等于原CPU Config14。所有graph/design AXI、主机副作用、设计后备全字节独立审计，真实后备145424192B。抽样沿用旧fixture名pressure，但本服务不含pager，不能称单槽分页压力验证。

`metadata_boundaries_v2_20261024`：15错误/15重载恢复、19正常检查；三个节点数不匹配、held配置、非法descriptor、静态created合并、动态created缺失/补齐、错误归属、R/B错、暂停AR abort及读取排空、owner失活、timeout、late fault、token3实际耗尽、int16最小/最大和32位tile/BB边界。B错误的物理字节改变也独立核验。

`metadata_control_v2_20261024`：实际控制器配受控服务，17检查/16错误；四种graph回显错误、graph状态、design cookie/状态、active/query/price/claim漂移、无归属回复、已接受读排空、完成/超时同拍及响应稳定。此项不单独证明AXI，AXI由上述实际服务回归证明。

完整默认metadata服务实际综合2824LUT/2578FF/190CARRY8，零RAM/DSP/latch/组合环。10ns为研究时钟，1942输入/1335输出无平台delay、HD.CLK_SRC未设，尚未布局布线或板上。完整证据见[实验报告](../results/metadata_20261024.md)。
