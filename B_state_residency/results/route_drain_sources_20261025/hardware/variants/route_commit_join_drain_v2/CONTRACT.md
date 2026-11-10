# native错误与物理AXI排空完成屏障

旧route_commit_host_adapter仅等待native label/owner回复。实际标签RRESP错误实验表明：native错误回复可先返回，而已发3拍AR仍剩2拍未接收；因此native完成不能等同物理排空。旧反例保存在results/route_fault_counterexample_20261025，原成功基线不覆盖该故障保证。

v2添加backend_drained输入，只有该输入为真才允许接受新route请求、向调用方提供完成响应/传递rsp_ready、以及正常释放held。控制器本身/服务mux不改；在native回复到达后仍保持controller响应背压及全部外部围栏，等待物理排空。故障仍锁住held，完成响应退休也不能恢复新命令。

axi_drain_watch是只观察不驱动的可综合计数器，分别观察原label与owner AXI：AR增加待接R拍数、R握手递减；AW记住本次写长度，允许W先到，B后清除AW/W待办。所有计数清零且无AR/R/AW/W/B VALID时才drained。检测读剩余量/RLAST与单AW约束不符时fault锁定，drained不再成立。适用当前固定ID、单挂起burst后端；不支持多ID/重排/多挂起AW或同拍新AR接替旧AR，不能直接当通用互连监视器。wlast形状由已有AXI服务/测试内存检查。watch fault须外层协调停止/重置，非恢复机制。

实际接线必须同时围栏search/config/frontier/旧host入口，admit还要求原engine无fault且无旧请求/回复；本测试连接沿用原正常围栏。backend_drained不能只接native busy或恒1。复位监视器前必须协调处理在途事务；不能靠清零计数宣称事务已排空。

五类真实组合故障，32槽和单槽各一次：owner BRESP2（首个写已落物理字节）、label RRESP2（三拍均接收后完成）、owner事务AW/W开始后的控制器取消、同位置控制器active_version输入漂移、owner RRESP2（首次metadata读，不发生owner写）。标签/owner服务、AXI memory均为原真实RTL路径，错误使用现有inject_r/inject_b端口；不force数据或内部状态。取消只发给route控制器，不取消后端已发事务；版本漂移修改协调器给控制器的版本输入，不等于真实价格/版本更新工作流。

故障测试从CPU q1 search-final原样导入328标签并checkpoint后开始，不重跑search。断言返回前AXI内存rp/wp及R/B VALID清零，控制器无发请求/待native回复；完成背压7周期、退休后32周期仍阻断全部入口，不发热重试、不发布slot。独立重放每个错误R/B的精确状态和字节，验证物理副作用而非仅看rsp_status。正常双查询/共享ripup另行回归。

物理效果：owner B错误确认ACK=0但已写1节点；取消/漂移ACK=1且写1节点；label/owner R错误均不写owner。ACK不是副作用上界。状态需协调修复或从权威checkpoint恢复，本版未实现rollback/recovery/reset-reload流程。无真实AXI超时/RID/RLAST破坏、多net并发、价格/epoch更新、unknown-page或板卡结论。
