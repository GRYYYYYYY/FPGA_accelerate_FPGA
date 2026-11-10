# 可配置路径槽与快照

PATH_SLOTS默认2，PATH_SLOT_BITS为max(1,ceil(log2(PATH_SLOTS)))。参数贯通route controller/host adapter、residency/search/query三个层级、query lifecycle、boot restore gate和export manifest。当前实测容量为2和3；不得据此宣称任意容量综合资源或时序成立。

route slot请求和保存槽位图随容量扩宽，未使用的slot编码在任何label/owner访问前返回status1，不使服务fault。192位路由命令从低位起为op1、slot位、cookie/source/sink/net/sequence各32位及高位零填充。默认两槽仍采用原始位布局；三槽cookie从bit3起。host与硬件须使用一致的容量和布局，不能发送旧布局给三槽实例。

每槽镜像保持valid,size,net,source,sink,design-lo,design-hi与MAX_PATH个内部节点，未用字为零；总字数PATH_SLOTS*(7+MAX_PATH)，本例MAX_PATH32时为78或117字。流的index/last和CRC覆盖完整镜像。当前镜像不含自描述容量头，导入双方须共享参数。第三槽的语义校验、重复节点检查和原子提交与前两槽相同；旧78字镜像在三槽实例被拒绝，不能静默补零。metadata导入不修改owner引用。

四个组件证据见results/path_capacity_20261027.json：原生三槽route controller2494检查/13次checkpoint/8次route，使用真实q3标签和已捕获q1/q2路径，但label/owner服务为注册mock；实际15个owner请求与5个标签读独立重放。覆盖登记历史路径不加引用、slot3拒绝、第三槽错误CRC/长度/design/重复/截断/取消保留旧路径、冷清控制器后恢复、独立拆线与空槽零填充。三槽export observer126检查、默认observer114检查且原事件字节一致；三槽query lifecycle29场景验证实际slot2编码、cookie与字段位置、错误slot拒绝及原失败/取消行为，后端为mock。

默认两槽完整G3系统在32槽和单槽缓存各28文件、全部12AXI、native trace及2331601/2507934结束周期逐字节匹配原已审计基线。六用例均归档实际恢复复审。该默认回归不单独证明完整层级使用slot2；build_third_tb.py/run_path_capacity_third_system.py的独立完整q3实验状态须以其结果JSON为准。

这里的“槽”是保存路径槽，区别于标签驻留缓存SLOTS。运行中持久化bundle、认证/floor、任意变价、全图baseline reseed、综合/时序及板卡收益仍未证明。固定价格与初始G1 clone/全图baseline外部可信条件继续保留。
