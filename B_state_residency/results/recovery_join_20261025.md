# 恢复协调器接入真实服务

Vivado 2022.2 XSim，复用 B MCP 会话。可综合 recovery_coordinator_v1 已接入真实分页标签和 owner AXI；32槽与单槽各五类故障，共10例通过独立审计。110份原生产 RTL/dat 保持逐 SHA 一致，采用隔离 journal adapter、原 drain observer 和已通过组件验证的同一 recovery_coordinator 源码。没有修改其他方案基线。

正常 owner 修改先写独立复位域 journal，至少下一拍才送后端。错误响应退休且 AXI 排空后，协调器发出5拍 target_reset，journal 保留；重新配置后实际 GET/DEC 修复，再做第二遍 GET 核对 refs/occupancy。标签使用新 query epoch2、price4、完整 version4：先探测旧物理字节不可见，再重载与逐条读回328份 CPU 搜索末态。恢复响应持有期间禁止新 route/expand/seed；响应退休后回溯提交6个内点，并发布 checkpoint17→18。

故障1为 owner BRESP2（ACK0但物理修改1节点）；故障2为 label RRESP2（无 owner 修改，仍等剩余 R 排空）；故障3/4为在途取消/版本输入漂移（ACK1且修改1节点）；故障5为 owner RRESP2（已记日志但没有物理修改）。1/3/4实际GET发现refs1，DEC至0，第二遍GET验证0；5两次GET均0，不盲目反向修改；2日志为空，无owner修复。每例恢复后恰好6个成功INC，无重复计数，最后可信checkpoint推进清日志。

独立 auditor 从原 CPU initial/search-final/q2-initial 重建路径与权威记录，逐项核验 J→BF 先后、恢复请求/回复及cookie、两遍authority的checkpoint/design绑定、复位/退休/准入断言、328条导入/重载/读回。七类 AXI 包含故障状态的所有读写字节严格重放；完整 owner（含allocator）均等于 CPU q2准备态，SHA256为373fd2e819992032677936aaab7ce9add321f8cae702ed94892b7be9c0dc13ba。完整 design/cost 保持原图像；全部16384物理标签帧按页内容多重集匹配权威值。不是只检查终端 PASS。

保留两次失败：v1是验证代码 trace 前向声明编译错误；v2在1041315ns因测试台撤掉预期故障标志后下一拍才发恢复请求而报旧 sticky fault。v3改为同拍先发恢复请求关闭准入，再撤标志，未削弱断言或更改协调器算法。失败 scratch 与冻结源保留。

配置发包、CPU authority 和标签重载/核验仍为测试台回调，外层搜索未重跑；这只是实际提交 checkpoint 的恢复接入，不是完整自主 warm checkpoint。容量32且本次仅6个内点，生产仍需最坏容量预约、可信不可变快照和排他写者。真实非零authority/多net修复依然只有先前组件模型证据；本组合未新测正常双query共享/ripup、价格更新/回绕、未知页、协调器cold_rst耐掉电、完整系统综合/Fmax或板卡性能。组件OOC资源不代表该组合资源；无实测加速结论。

结果 results/recovery_join_rtl_v3；源冻结 recovery_join_sources_20261025；scripts/run_recovery_join_rtl.py 与 audit_recovery_join_rtl.py。下一优先将配置与标签恢复回调迁移为硬件服务并统一生产围栏，补正常共享/ripup回归，再推进完整checkpoint、prepare/search及未知页生命周期。研究goal保持 active。

567文件归档19101151B；原scratch移入.preserved后实际解压，所有成员hash通过，独立审计重跑逐字节一致，见 recovery_join_restore_20261025.json。run.py check与Python语法检查通过。失败两轮源码和日志另存recovery_join_failures_20261025，共242文件逐SHA冻结。
