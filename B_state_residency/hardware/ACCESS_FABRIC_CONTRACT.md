# 访问性共享服务连接（access_fabric_v3）

组合 `access_service`（实际HLS和驻留控制）、`access_dispatch`、`coordinate_service`（实际分页标签、图AXI、SLR/Laguna表AXI）。一个child的visited/target/prev及坐标请求在设备内部完成。WILL_OVERUSE和COUNT_USER通过明确的外部owner接口请求，本版没有实现物理设计占用/引用计数存储；不能称为完整路由器。

## 所有权和仲裁

对外请求/响应沿用 [ACCESS_SERVICE_CONTRACT.md](ACCESS_SERVICE_CONTRACT.md)。Config14字在进入前必须由children构建后的设计状态和静态图生成一致快照；此版未连接该metadata生产过程。

外部host OPEN/CP/CLOSE/标签IO从接受请求到响应退休保持host_pending，阻止新的child判定。反之，v3以access_pending寄存器记录child请求接受至最终响应退休的归属，在此期间独占共享标签/坐标服务，拒绝外部host控制和标签写。即使HLS处于两次服务之间的计算阶段，也不能释放该独占；不能只看coordinate_service.busy，也不能把包含fault的access.busy用于响应归属门控；v2由此产生的组合反馈已在完整综合中被检出。

host ctrl优先于host IO。所有内部标签读取走coordinate_service的host IO端口，由顶层仲裁区分外部host与内部dispatch的响应归属。坐标读取自行独占其图/表和页管理器。分页内部自动CP可继续执行，但不能改变该child的active/query/price，也不能清除查询heap/递归栈。

## 请求分派

| kind | 后端 | 返回 |
|---|---|---|
| 1 VISITED | 实际分页IO field3 | 32位visited |
| 2 TARGET、5 SINK_TARGET | 实际分页IO field4 | 32位target，不合并第二次读取 |
| 9 PARENT_PREV | 实际分页IO field2 | 原始prev，包括0或0xffffffff |
| 3 BBOX_END_Y、11 GRAPH_END_Y | 实际坐标op0 | 动态endY |
| 7 CHILD_SLR、8 SINK_SLR | 实际坐标op1 | 行表SLR |
| 10 PREV_TILE | 实际坐标op3 | 原32字节图属性中的tileAddr |
| 4 WILL_OVERUSE、6 COUNT_USER | 外部owner端口 | 真实占用布尔结果或同net连接引用数，物理服务待实现 |

请求对象由驻留控制器提供：child、sink、parent，或第二次parent.prev返回的aux节点。prev无效且PREV_TILE需要读图时，由实际图/坐标后端检测范围错误，不把无效编号当可访问节点。

原始hot静态属性来自initHotFromStatic，owner/occ由syncHotOcc维护。当前图服务只有静态权威副本；调用者必须保证hot/ns静态副本一致。测试fixture将hot设为同一图数据并用原CPU代码核对；独立变动或不同步的hot属性不在覆盖范围。

## 结果和故障

dispatcher保存kind/phase/node/net/token/query/price并回显。标签空record必须完整payload为零；保留prev0的真实含义。坐标结果检查status及cookie/node/query/price/op；owner结果检查status及所有身份字段。任何后端的无归属响应、错误状态、错误回显、fault、owner漂移、中断或超时都会停止，禁止重发请求。

dispatcher status 1非法kind、2owner不符、3服务错误、4身份不符、5中断/下游fault/无归属/owner漂移/超时。外层access通常以status5报告dispatch的锁存fault。最终响应若已暴露则保持字段，迟到故障只提升fault；外部host及决策消费者必须检查fault0后才能使用响应。

冷复位覆盖整个组合及owner服务，并排空或取消旧总线响应。测试的内存模型在复位时取消旧事务；不表示任意物理AXI设备都支持局部复位。设计级占用/history绝不能跟connection标签一起清零，未来owner服务需要独立生命周期。

## 冷启动预算

v1默认服务上限262144拍。实际默认HASH_BITS18的首次冷标签服务观察到262129拍，虽通过但只有15拍余量；功能测试HASH_BITS15时为32753拍。等待来自冷复位后的目录初始化，与每个connection的标签重置应区别计量。

v2仅改变顶层默认服务预算为 `(1 << HASH_BITS) + 262144`：默认目录为524288拍，功能缩小目录为294912拍。前一项为目录冷初始化规模，后一项保留操作等待预算。预算传给dispatch及coordinate；access整体预算仍为8388608拍。已暴露最终响应的背压不计入超时。该改动不改变正常算法、访存顺序或时钟周期计数。

## 验证边界

合成11664组覆盖18³类型组合×hot/normal，512组真实图节点，以及614组单槽抽样。原CPU条件/坐标调用与候选状态机事件逐项一致，UBSan通过；HLS每次20字输入/六字输出对照，实际native标签READ和graph/table AXI字节独立核对。

19项实际组合故障、19次协调冷复位恢复：图/表/标签R和标签B错误，非法prev，owner超时/身份/状态，四阶段abort及迟到owner fault。另以完整默认163840帧、INDEX/HASH18验证首次冷标签和SLL坐标路径。最终终态及综合资源见 [实验报告](../results/access_fabric_20261024.md)。

owner端口在当前测试中由占用数和同net引用数模型响应，不使用物理存储；元数据输入也来自fixture。真实512组没有SLR请求，不能将合成跨SLR覆盖描述为真实跨SLR路由测量。还缺设计占用/引用服务、metadata生产、完整search、递归执行、回溯提交、平台与板上。

## 后续owner服务的源约束

原始CAPACITY=1，ownerCnt与occCnt均uint16，overflow引用为int；hot.occCnt截断到255。对本接口WILL_OVERUSE，occ>1在截断后仍为真，所以该截断不改变布尔结果；COUNT_USER仍须返回实际同net引用。对后续价格表查找不能直接作同样推断。主owner递增与overflow晋升存在16位边界，真实完整输入的峰值及加载预引用已由[独立观测](../results/owner_profile_20261024.md)核验，下一阶段仍须明确支持域及容量耗尽处理，不能静默更改计数宽度或声称任意溢出输入等价。设计占用状态也不能随标签OPEN/CP/CLOSE初始化。

## v2组合反馈负例与v3修复

v2虽然功能和故障仿真通过，但完整综合发现1条4-LUT组合环：a_busy含fault，又参与标签响应归属门控；无归属响应检查反馈到fault/a_busy。工具exit0不代表该设计通过，negative_audit明确标为failed，原DCP/日志保留。v3只以接受/退休握手维护独立access_pending寄存器，并据此选择标签请求、回应归属和host互斥。正常结果/周期/全部内存轨迹与v2逐字节一致；v3完整默认容量实际综合与独立结构门禁已通过：LUTLP-1/check_timing均为0组合环，19739LUT/16938FF/375BRAM/3DSP。尚未布局布线或接物理owner服务。
