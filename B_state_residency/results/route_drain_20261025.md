# 真实错误传播与AXI排空屏障修复

发现并保留旧adapter反例：label RRESP2后，native错误回复在cycle102759到达，旧adapter已经提供完成，但已发三拍AR仅收到第一拍，0xd00/0xd40仍未接收。反例目录route_fault_counterexample_20261025含失败日志、逐字节AXI、源TB、失败manifest与SHA，不把原成功路径结果当故障安全证明。

新增隔离variant route_commit_join_drain_v2，不覆盖旧成功基线。两个只读AXI观察器分别计数label/owner AR-R及AW/W-B，物理计数和VALID清零后才backend_drained。适配器接收新命令、给调用方完成/传递ready、正常释放held均受此条件约束。native错误先到时保持响应背压与围栏，fault仍禁止热重试。原engine fault也纳入admit排他条件。控制器和其余110份RTL/dat保持原接入证据，只有adapter变体替换并新增watcher。

五类真实故障，32槽/单槽各5例，共10例独立仿真：

| 场景 | 完成status | 确认ACK | 物理owner修改节点数 |
| --- | ---: | ---: | ---: |
| owner BRESP2 | 5 | 0 | 1 |
| label RRESP2 | 4 | 0 | 0 |
| owner AW/W在途取消 | 6 | 1 | 1 |
| owner AW/W在途版本输入漂移 | 6 | 1 | 1 |
| owner RRESP2 | 5 | 0 | 0 |

测试从原CPU q1搜索末态328条native记录导入并checkpoint后开始，未重跑search。真实pager/owner AXI后端不改，错误使用已有memory inject端口，不force状态。版本漂移只改协调器给控制器的active_version输入，不等同真实价格/版本更新工作流。

修复版label错误：32槽native回复102759、末拍R接收102780、对外完成102781；单槽74741/74762/74763，均在物理排空之后完成。错误响应保持7周期，退休后持续32周期冲突valid，确认围栏不解除、slot不发布、不继续owner更新。错误R/B状态逐笔严格匹配预期；独立重放全部实际字节和WSTRB，完整owner图像精确验证上述副作用。label完整物理帧保持checkpoint，design/history/cost不清除。owner B失败虽ACK0但已写1节点，明确证明确认计数不能代替副作用判定。

正常回归：修复版32槽/单槽同实例两query、共享提交与ripup全部通过。原447decision/293cost/879ACK/116POLL/114expand、328 native/120页/16384物理帧及四阶段owner/CPU q3仍通过。natural_trace含周期、七类AXI日志与label/design/owner/cost四文件逐SHA等于旧成功基线；周期仍680767/743652，没有本例正常时延变化，不是加速结果。

边界：观察器仅适用当前单ID/单挂起burst后端，非通用AXI重排监视器。没有自动rollback、同实例reset-reload恢复、真实AXI超时/ID/RLAST损坏、多net并发、价格/epoch、unknown-page或板卡验证；监视器/适配器整体资源时序未测。ACK0/失败不意味着可以重发。下一步实现统一生产围栏与协调复位/权威状态恢复，再迁移prepare/search外层与按需页生命周期。

过程证据：v1沿用成功监视器遇预期全局fault提前终止，v2改用专用故障断言后暴露真实早完成缺口；v3新增观察器首次编译因TB实例位于信号声明之前被隐式声明冲突阻止，移动实例后v4通过10例。各失败scratch保留，没有修改失败数据或取消物理排空断言。旧反例单独持久化。

主审计audit_route_fault_rtl.py（错误专用逐字节重放器audit_route_fault_axi.py），正常audit_route_join_drain_rtl.py。代码冻结route_drain_sources_20261025，契约hardware/variants/route_commit_join_drain_v2/CONTRACT.md。

持久化：563文件故障归档与446文件正常回归归档均逐成员核验；原scratch实际移至.preserved后解压恢复，两主审计重算逐字节一致。凭据route_drain_restore_20261025.json。正常逐SHA对照见route_drain_normal_compare_20261025.json。run.py check与新增脚本语法检查通过，功能结论以真实仿真/严格错误字节重放为准。
