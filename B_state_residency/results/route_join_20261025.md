# 可综合路径控制器接入真实服务通过

route_commit_controller与新route_commit_host_adapter接入原candidate_recursive_engine的真实host native分页标签和owner AXI服务，替换连续双查询TB中的prev回溯/owner修改循环。原109份生产RTL/dat保持SHA，新增2模块；控制器与已通过25项组件检查的RTL逐SHA一致。新适配器的整体综合/时序成本未测，不能套用原core OOC资源。

TB仅提交4个操作命令：slot0 trace-commit、slot1 trace-commit、slot0 ripup、slot1 ripup。全部16次标签读取（包括两个source prev=-1核验）、24次owner修改地址和顺序由RTL产生，逐项等于原CPU两条实际路径；native payload全部逐位核验。ripup不再读取prev，使用RTL保存的路径。两个共享节点引用1→2→1→0、占用1→1→1→0；owner四阶段全图像核验及原CPU sequence3完整owner对照仍通过。stage0评分GET减为已知slot0的6条，其余阶段各12，共42 GET；四个阶段全部物理字节核验保持。

新适配器在确认search及旧host/config/frontier请求/回复排空后获取lease，控制器响应退休并busy排空后才释放；fault保持阻断。hold期间label/owner服务由RTL独占。测试连接对host ctrl/design、expand/frontier、q/g/d/t/owner/cost配置入口双向围栏；运行及响应背压期间持续施加冲突valid，任何可见ready均失败。完整生产top的围栏/平台接口仍需迁移，不能仅使用两个服务mux而漏掉其他入口。

| 指标 | 32槽 | 单槽 |
| --- | ---: | ---: |
| 两query POLL / expand | 116 / 114 | 116 / 114 |
| 判定 / cost-OFFER | 447 / 293 | 447 / 293 |
| 标签ACK | 879 | 879 |
| 总仿真周期 | 680767 | 743652 |
| label读事务 / 写回复 | 605 / 260 | 1535 / 615 |
| State读拍 | 114 | 114 |

完整328 native记录/120逻辑页、16384物理帧、design/owner/cost与七类AXI日志逐字节通过；两种槽数最终标签与owner SHA一致。周期包含TB导入/评分/prepare/搜索调度，不是加速比较。MCP同PID147904，225.949秒exit0。

仍未完成：外层search/prepare由TB调度，328联合工作集由CPU预知；组合未注入真实pager/AXI错误/超时/在途漂移，不把core mock边界外推为端到端恢复。价格/epoch切换、unknown-page初始化、altSink、长路径溢出恢复、整机资源/时序及板卡未验证。下一步补真实组合故障排空及统一围栏，然后迁移prepare/搜索外层控制并推进未知页/生命周期。

源码冻结route_join_sources_20261025；契约hardware/variants/route_commit_join_v1/CONTRACT.md；主审计audit_route_join_rtl.py。没有覆盖原默认基线目录。

持久化：443文件/10699517B归档逐成员核验；原scratch实际移至.preserved后恢复，完整主审计重算逐字节一致。凭据route_join_restore_20261025.json。run.py check与新增脚本语法检查通过，功能结论来自上述真实仿真/独立审计。
