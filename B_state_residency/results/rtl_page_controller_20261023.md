# 页槽传输控制器 RTL：行为回放与综合

2026-10-23，`rtl_page_controller_20261023/manifest.json` 与 `completion_audit.json` 均 **passed**。新增 `hardware/rtl/scratch_page_controller.sv` 组合冻结的BRAM页槽，阻止传输中搜索/释放，按完整描述符核验完成，64位置到齐后才发布换入页/清写回dirty。旧页槽、CPU构建和上级原始源码均未改动。

## 实测验证范围

|实例/工作负载|公开接口命令检查|响应背压周期|其他范围|
|---|---:|---:|---|
|3位tx / 3位generation边界|29,774|9,164|40次fence、事务耗尽拒绝、代次禁止回绕、4槽乱序完成、失配/早完成/重复消息、16个确定性随机区组|
|16位tx / 16位generation真实值|472,689|145,444|19完整小查询，56,588字段访问，2,702写回、3,384换入，19次fence|

真实数据来自已冻结的 `real_field_values_20261023T024250Z`，选取count≤100000的全部19查询，不是截断前缀。34,610读、21,978写；通过4槽LRU产生7,184次绑定/释放、172,928个EXPORT位置、216,576个BEAT位置与6,086次完成。每次真实读以原始32位浮点位模式核验；无效节点与有效零节点分别检查。独立字典模型维护标签与传输集合，实际字段轨迹又独立核验搜索读值；全部输出通过公开端口比对，没有DUT内部RAM后门。

TB接受命令后立即污染所有请求字段，验证同步RAM操作只使用锁存值；每13条命令背压4周期，同时尝试提交非法下一请求，要求ready保持低且完整响应稳定。两次终态分别在1,303,510ns和23,175,460ns结束；1001ms是有看门狗的仿真上限，不能用作处理延迟或硬件频率证明。

边界测试观察到所有8个状态：OK14240、STALE3797、DIRTY24、BAD2302、BUSY7782、EXHAUSTED48、INCOMPLETE1520、FENCE_WAIT61。未做形式化、CDC、所有参数组合、默认16位完整耗尽、传输丢包恢复或运行中reset验证。

## 综合结果

Vivado/XSim **2022.2**，器件 `xcu280-fsvh2892-2L-e`，out-of-context，10ns探索性时钟约束；完成综合和DCP读取，未布局布线。

|资源|原单独页槽|控制器+页槽|增加|
|---|---:|---:|---:|
|CLB LUT|1,332|2,154|822|
|寄存器|641|1,605|964|
|锁存器|0|0|0|
|RAMB36E2|2|2|0|

DCP中的RAM单元由 `ram_cells.txt` 保存。没有RAM退化为寄存器；综合0错误、0严重警告，1条Synth8-7080并行综合条件不满足警告。表格是两个独立综合顶层的整体差值，不是控制器模块的独占物理资源归因，也不证明100MHz时序闭合。

## 安全边界与下一步

完整接口见 [控制器契约](../hardware/PAGE_CONTROLLER_CONTRACT.md)。新RTL内有限事务号不复用，页槽代次严格递增，query在一次排空周期只使用一次；耗尽后拒绝，不自动回绕。写回和换入各有槽租约；CLEAN不再是外部可直接调用的操作。开始fence不丢弃脏页，未开始写回的LIVE脏页会拒绝fence；在途传输可完成，全部槽释放后才允许结束fence。

**COMPLETE仍来自可信适配器**：它必须代表写回数据/有效图已持久可见，而不只是EXPORT输出被消费。**FINISH_FENCE仍依赖peer_quiescent和ingress_empty同步证明**，当前只验证本地为空，远端请求/工作/响应/重复包/control ACK队列尚未在RTL实现。谎报排空后，相同有限token旧包仍无法识别。没有地址后备池/地址租约RTL、AXI/DDR/HBM DMA、真实路由计算器或板卡测量；不宣称端到端加速。

下一步将软件 `finite_transport.py` / `fence_control.py` 的有界队列及有限fence tag/ACK规则组合到该端点，产生可核验的排空证明，再接入固定地址后备池和DMA。继续保留“有传输完成消息”与“数据已持久可见”的区别。不得将当前接口前提当作下一层实现完成。

## 工具事件与证据

本轮按Ross `vivado-simulate-rtl` 技能优先使用MCP，创建独立B会话 `vivado-20261023-095030-d4927f96`。两个XSim均在此会话成功结束。项目中的simulate.log为空/含NUL，完整无NUL的Vivado会话日志保留了编译、展开、运行、精确PASS计数及$finish，冻结为 `simulation_session.log` 并作为审计证据；没有从空日志推断成功。

随后 `launch_runs synth_1 -jobs 2` 导致父进程1998871异常退出，code6栈再次包含libudev/realloc、libXil_lmgr11和Webtalk注册。与上一页槽会话同类，保留 `hs_err_pid1998871.log`；这不是根因定位。MCP会话消失，无法执行wait_on_run。实际独立综合子进程2223090仍活跃，未重复启动/中断，随后正常结束，保留 `.vivado.end.rst`、完整runme.log和DCP。本机同版本batch仅open_checkpoint并生成资源/RAM清单，退出0。未改系统库、许可证设置或其他方案会话。

可复核：

```bash
python3 hardware/scripts/report_page_controller.py results/rtl_page_controller_20261023
```

审计冻结源文件、嵌套源码快照、实际轨迹/向量哈希、两个终态与精确计数、综合结束标记、0错误与BRAM映射。manifest SHA256：`379a643438e671efaa9070166410710ef5b5400f23d0db4e1df88275687dbfaf`。生成器 `hardware/scripts/make_controller_vectors.py <新目录>` 不覆盖旧向量；原始XSim工程和生成脚本保留。工具会话已终止，综合和checkpoint报告进程均已结束，无活动计算队列。
