# 同实例协调复位与提交checkpoint恢复

五类故障（owner B错误、label R错误、owner在途取消/版本输入漂移、owner R错误）分别在32槽/单槽执行，共10例。每例同一DUT/XSim实例经历故障→物理排空及围栏确认→协调rst→真实owner修复→新epoch权威标签重载→完整路径重新提交。生产RTL/已通过排空屏障适配器不改，本轮新增的是TB恢复协调协议。

owner请求握手时记录可能脏node，journal跨DUT reset保留；不以失败ACK数判定物理副作用。恢复阶段先GET：三个已写场景读到refs=1/occupancy=1，执行DEC再GET核验归零；owner读错误虽然有请求journal，却读到0，不做DEC；label读错误无owner请求journal。未知net占用/超额引用会拒绝修复。本例权威checkpoint已确认对应内部节点初态为空，非通用rollback。

| 场景 | journal节点 | 修复DEC | 恢复后完整提交ACK |
| --- | ---: | ---: | ---: |
| owner BRESP2 | 1 | 1 | 6 |
| label RRESP2 | 0 | 0 | 6 |
| owner在途取消 | 1 | 1 | 6 |
| owner在途版本输入漂移 | 1 | 1 | 6 |
| owner RRESP2 | 1 | 0 | 6 |

协调复位前断言AXI观察器、实际memory rp/wp/R/B均排空；复位不关闭/替换文件、不清物理owner/design/cost/标签后备。新OPEN使用query epoch2、price标签4、full version4；物理价格/history字节不变，版本变化用于新的恢复身份，不是改变价格后复用距离标签的证明。先读取150697要求present=0，旧物理字节不得成为新epoch有效记录；再按原CPU q1搜索末态重载328条字面native记录，checkpoint并逐条真实读回。恢复协调器工作期间route/expand/frontier请求保持关闭，核验完成才放行一次重新TRACE_COMMIT。

最终十例owner完整图像SHA均373fd2e819992032677936aaab7ce9add321f8cae702ed94892b7be9c0dc13ba，逐字节等于原CPU q2准备态：恰提交一次q1路径，而非盲目重试造成双倍引用；原设计预占用仍保留。标签328条/120逻辑页/16384物理帧多重集及所有重载CHECK正确，槽数间物理布局可不同，不宣称标签文件SHA均同。所有错误状态、跨reset全部AXI读写字节/WSTRB及最终文件重放通过，无backdoor owner修复/文件替换。

资源/范围：journal、恢复准入门与配置/修复/reload流程是TB协调器，不是综合后的恢复FSM或耐掉电日志。此checkpoint仅覆盖独立回溯提交操作的标签/owner及固定输入，没有恢复完整search的warm children/created、frontier或connection路径表。设计文件维持测试输入，不能称完整search恢复。只测试一次非回绕epoch1→2、version3→4；没有未知工作集、并发写者、实际价格变化或板卡性能。总仿真周期包含两次导入/读回与冷启动初始化，不是速度比较。

首次route_recovery_rtl_v1已通过owner GET/DEC，但恢复OPEN仍带price3/version4，被原身份防护拒绝；修正TB协调器令price=version低4位后route_recovery_rtl_v2通过，原失败保留，没有削弱身份断言。MCP300秒返回running后保持同任务，321.114秒exit0。独立主审计audit_route_recovery_rtl.py，源码冻结route_recovery_sources_20261025，契约hardware/variants/route_recovery_v1/CONTRACT.md。

下一步把恢复准入/日志/修复协议迁移为可综合协调器并扩展完整warm checkpoint，再推进prepare/search外层及unknown-page生命周期。恢复snapshot来自CPU的已知328联合工作集，不能外推为任意数据恢复。

持久化：563文件/18826726B归档逐成员核验；原scratch实际移至.preserved后恢复，十场景主审计重算逐字节一致。凭据route_recovery_restore_20261025.json。run.py check与新增脚本语法检查通过，功能结论以同实例仿真/严格跨reset字节审计为准。
