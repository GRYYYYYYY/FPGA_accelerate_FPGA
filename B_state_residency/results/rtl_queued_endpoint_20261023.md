# 有界队列与有限 fence 的 RTL 组合验证

2026-10-23，`rtl_queued_endpoint_20261023/manifest.json` 及 `completion_audit.json` 均 **passed**。新增 `bounded_sync_fifo.sv` 与 `queued_scratch_endpoint.sv`，将请求、工作、响应、fence请求和ACK全部保存在有界RTL队列中；外层接口不再接受任意 `peer_quiescent` / `ingress_empty` 布尔值。此前页控制器、BRAM页槽和真实值向量未修改。

这是同一时钟域内的闭合端点证明。实际DMA持久完成、AXI outstanding和地址池租约尚未接入，不能称为真实链路fence或板级加速。完整接口见 [契约](../hardware/QUEUED_ENDPOINT_CONTRACT.md)。

## 验证结果

Vivado/XSim 2022.2，三组正向测试均编译、展开、运行到终态PASS，无非预期ERROR/Fatal。

|测试|命令/值检查|主要证据|
|---|---:|---|
|3位tx/gen、1位fence tag边界|2,267|48次fence、24次tag回绕；队列满、活跃lease、早完成、重复完成、重复ACK、响应残留、FINISH后方排队工作、FINISH同周期入队竞态|
|默认16位tx/gen、2位tag真实回放|472,689|19完整小查询、56,588实际字段事件；19次fence、4次tag回绕，无标签值差异|
|独立顺序值参考下的流水压力|6,144|命令连续入队、不同字段/位置读写；46,060响应背压周期，队列满时仍保持顺序和值|

实际值回放复用上一轮独立Python参考产生的冻结向量：34,610读、21,978写，2,702写回、3,384换入；每次64位置导出/换入均通过公开端口。没有截断所选小查询，也没有将本轮覆盖声称为全部38查询。TB在成功FINISH前允许对FENCE_WAIT重试，本次正常轨迹重试数0；边界测试的预期拒绝另计。

顺序测试先独立预计算6144条串行历史，然后使用周期性且不同步的dispatch/execute/output背压运行FIFO；覆盖多个不同字段的位模式保存和最终128次全页扫描。请求/工作/响应队列处于满状态分别61,627、58,328、34,799个周期。它补足了仅发送相同错误命令无法验证重排问题的不足；这些周期是测试调度结果，不是硬件性能指标。

## 五个负向对照

`verify_queue_guards.py` 只在独立副本中分别删除一个保护条件，原始RTL保持不变。五个副本都成功编译/展开，然后在预期行为检查失败；这证明测试对这些错误敏感，并不表示生产RTL曾出现这些失败。

|删除的条件|观察到的首个失败|
|---|---|
|FINISH要求旧响应队列为空|`retired with old response buffered`|
|FINISH要求重复ACK队列为空|第90条响应错误成功，期望FENCE_WAIT|
|FINISH要求工作队列只剩自身|第94条响应错误成功，期望FENCE_WAIT|
|FINISH拒绝同周期新请求握手|第96条响应错误成功，期望FENCE_WAIT|
|peer seal要求页传输lease为0|`peer sealed with outstanding lease`|

负例完整输入、只改一处的源码、编译/展开/仿真日志和退出码保存在 `negative_guards/`。auditor要求精确负例集合、原始源码哈希、声明替换之外无修改，以及预期Fatal且无TEST_PASS。未忽略或降低断言等级。

## 综合资源

U280器件 `xcu280-fsvh2892-2L-e`，out-of-context综合，探索性10ns约束。默认数据队列各4条、控制队列各2条；单时钟，无布线时序或实卡测量。

|资源|前一轮页控制器+存储|加入有界队列/fence后|整体差值|
|---|---:|---:|---:|
|CLB LUT|2,154|2,708|554|
|寄存器|1,605|1,653|48|
|RAMB36E2|2|2|0|
|锁存器|0|0|0|

最终LUT中432用于memory，已经包含在2,708内，不能再相加。RAM单元仍是页数据的两个RAMB36E2；DCP和清单保留。资源差值是两个顶层独立综合的整体变化，不能等同队列模块的独占布局资源。综合0错误、0严重警告，Synth8-7080并行条件不满足警告1条。没有100MHz闭合或吞吐承诺。

## 排空范围与下一步

peer ACK只有在所有已入队命令/工作与页传输lease排空后生成；收到ACK后还必须排空响应、重复控制请求/ACK、后方工作，并排除同周期新请求，才能让底层回收tx/query/generation。底层仍要求所有槽已释放，BEGIN仍保护未写回的脏页。有限tag只在成功FINISH后递增。

这个范围不包括模块之外的网络旧包、隐藏生产者、跨时钟FIFO、AXI读写未完成项、HBM/DDR持久可见性或后备地址所有权。当前命令FIFO不是完整的远端描述符DMA调度/去重引擎；COMPLETE仍来自可信适配器。下一步应实现固定后备地址与描述符租约，并将实际内存写响应绑定到COMPLETE，随后把内存执行单元计入fence，不能直接将EXPORT消费当成写回完成。设计级hist/占用仍保持独立，不随查询回收。

## 复核与工具记录

按Ross `vivado-simulate-rtl` 技能先查会话，再创建B独立MCP会话 `vivado-20261023-101326-b113e545`（PID2552581）；三组XSim在该会话完成，现为闲置会话、没有活动仿真/综合。没有操作其他方案会话。鉴于前两次 `launch_runs` 在父进程Webtalk/libudev栈崩溃，综合直接使用已验证的本机2022.2非工程batch脚本，本次退出0，无重复启动或工具崩溃。负向副本也使用独立目录的同版本批处理XSim。

完整 `simulation_session.log` 是正向仿真权威记录；项目simulate.log的空/NUL副本保留但不作为终态依据。仿真中未配置外部已编译库路径、无顶层波形对象，以及顺序参考数组超过波形GUI显示位数的警告不影响本次纯SV自检；未声称保存了所有数组波形。上限1001ms，实际三组终止于212,960ns、37,356,090ns、681,650ns。

```bash
python3 hardware/scripts/report_queued_endpoint.py results/rtl_queued_endpoint_20261023
```

审计输入/源码快照/真实轨迹和向量哈希、三次完整仿真、精确终态计数、五个负向行为失败、综合退出与RAM映射。manifest SHA256：`56592fcb80c64c87e304f69a73fe3b51e60f66dd5d97dd598ad52e3687bc7c88`。原始工具句柄96867（负例）与27767（综合）均退出0，无活动计算队列。完整研究目标仍未完成。
