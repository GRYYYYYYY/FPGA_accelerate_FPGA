# 可综合路径提交控制器首版

新增独立route_commit_controller.sv，将回溯、保存connection路径、串行owner提交及ripup实现为RTL五状态控制器。两个路径slot；整条prev链验证后才开始owner修改；ripup使用保存路径，不重读被后续搜索改写的prev。完整query/price/version/design上下文、排他lease和slot设计归属校验。未替换现有基线。

实际CPU两query末态8节点native payload由快照逐位导出，注册型mock label/owner服务按RTL请求应答。独立审计真实payload、实际16次初始路径请求及24次正常INC/DEC轨迹，25项成功/身份拒绝/错误链/容量/背压/取消/超时/完整上下文/空路径/响应持有检查通过。mock仅模拟后端，不是实际owner AXI或分页标签实现。

默认MAX_PATH32/two slots，U280 xcu280-fsvh2892-2L-e，Vivado2022.2 OOC综合：2144 LUT、2924 FF、0锁存器/BRAM/DSP。仿真容量8，综合容量32。并行环检测使路径RAM采用寄存器；不代表任意长路径支持或整机资源可行性。未约束时钟/I/O，未place/route或测Fmax。

综合保留103条WARNING行（内部synthesis summary另报192）；分类为未使用payload位、并行综合门槛、固定o_op高位及扁平netlist floorplanning提示，无error/critical warning；完整原始日志保留，没有删除warning。首次unit_v1编译因SV保留字design失败，改变量名ctx_design后unit_v2通过18项；追加边界后unit_v3通过25项。早期目录保留，综合与unit_v3 RTL SHA一致。

故障语义：已发VALID不撤回，等待接受/回复排空后才报告失败，rsp_acked为确认修改数；错误回复或晚取消仍可能已有物理副作用。无自动回滚/热重试，协调停止/重建权威状态仍由外层负责。不能将mock测试称为端到端故障恢复。

下一步优先通过明确的host接口仲裁/全程lease连接真实pager与owner store，替换已有连续查询TB的实际回溯提交循环，重跑两query共享/ripup及故障边界。之后才推进自主search、价格/epoch与unknown-page生命周期；这些仍未完成。

代码/契约固定route_commit_sources_20261025，主审计audit_route_commit.py，综合DCP和netlist保留。

归档恢复：35文件unit与9文件综合归档均实际移走原scratch后恢复。重算审计内容语义一致；综合审计files字典因遍历创建顺序导致JSON键顺序不同，首次逐字节比较未通过。逐项确认对象/文件hash一致后，恢复已接受审计原字节并再次核验所有归档成员hash；凭据route_commit_restore_20261025.json。不把序列化顺序差异记作功能失败或伪称重算逐字节一致。run.py check与脚本语法检查通过。
