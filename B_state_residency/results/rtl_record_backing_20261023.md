# 可综合记录级后备存储适配器

2026-10-23：`record_backing_service` 已通过XSim、七项故障对照、默认23405-frame整体OOC综合和最终审计。上一轮测试台负责的“成功内存响应→解码提交”和“失败响应→codec中止”已移入可综合RTL；写传输先校验全部记录，refill查询新增不分配地址的LOOKUP。

页槽/队列的EXPORT、BEAT、COMPLETE、地址RETIRE和双域fence尚待接入。这是记录级存储子系统的实现证据，没有完整路由执行或板级加速结论。

## 代码与证据

- [适配器RTL](../hardware/rtl/record_backing_service.sv)、[接口契约](../hardware/RECORD_BACKING_CONTRACT.md)。
- [LOOKUP目录](../hardware/rtl/backing_frame_directory_lookup.sv)、[LOOKUP服务](../hardware/rtl/backing_page_service_lookup.sv)是原模块的新版本，原有已验证源码未修改。LOOKUP在空目录或未找到owner时返回UNREADY，不分配frame；命中时返回原frame和published状态。
- [manifest](rtl_record_backing_20261023/manifest.json)、[最终审计](rtl_record_backing_20261023/completion_audit.json)。manifest SHA256：`95603ad1496c22a604b79ce1dd35cdd5b31b136935a6e31c15e9e432aedb57f0`。
- 最终输入冻结在 `verified_build_v2/sources`。审计在临时目录独立重新生成LOOKUP版本和测试台，确认逐字节相同，并核验上轮codec证据、当前源码和产物哈希。
- 固定64页来源同[上一轮codec](rtl_page_codec_20261023.md)：62个真实捕获页面及2个定向样本；不是完整查询/完整路由的AXI回放。

## 行为结果

| 检查内容 | 实际结果 |
|---|---:|
| 服务响应检查 | 1,144 |
| 解码记录逐位核验 | 4,288 |
| 不改变分配数/租约的LOOKUP检查 | 195 |
| 成功写页 / 读页 | 79 / 67 |
| AXI错误场景 | 8 |
| 坏写输入 / 损坏读取页 | 3 / 3 |
| AW / AR / B / R握手数 | 106 / 95 / 106 / 1,554 |

64-frame行为实例遍历所有64种4KB起始偏移，包含跨4KB分割、W早于AW、延迟B、记录/响应背压、四槽完成租约保留和逆序释放。服务响应保持到消费，输入命令接受后立即被测试台污染为无关值，检查内部参数保存。

三个坏写输入分别是最后offset重复、记录padding非零、absent节点载荷非零。均在启动内存服务前返回BAD；无AW/W、无事务号消耗、无租约或sticky fault。每次拒绝后立即以原事务号写回有效页，再读回核验，证明可以继续工作。

三个损坏页通过独立从设备内存注入：记录padding、页尾、absent节点数据非零。总线返回成功，codec仍拒绝发布任何记录；适配器返回IO_ERROR并封锁全部后续命令。即使底层目录已将该读标为COMPLETE，RETIRE和RECYCLE也被拒绝，租约保留。

八种总线错误包括错误B/R响应、错误ID/RLAST、第二burst出错，以及地址4032处首个仅1拍写burst失败。后一情形证明编码器尚有剩余数据时，适配器能在错误响应后中止codec。读引擎继续排完已接受burst后才返回错误，未将有效前缀当成整页发布。

最终日志 `simulation_session.log` 包含编译、展开、两条TEST_PASS及正常结束（仿真时间2,968,490 ns）；这不是实卡耗时。仿真无RTL编译错误；保留Vivado空编译库路径和大型波形数组显示提示。

## 七项故障对照

| 变体 | 实际检测结果 |
|---|---|
| 写传输绕过编码输入阶段 | 记录输入超时；在较早的PIN拒绝测试处即暴露接口被绕过 |
| 空目录LOOKUP误分配 | 响应OK/UNREADY不符 |
| 非空目录LOOKUP未命中时误分配 | 响应状态与frame不符 |
| 未消费全部解码记录就返回成功 | 提前成功断言 |
| 忽略已读页格式错误 | 返回OK而不是IO_ERROR |
| 故障后仍接受命令 | 返回UNREADY而不是故障封锁的IO_ERROR |
| 省略codec中止 | PIN拒绝后响应超时 |

所有变体均成功编译和展开，随后在预期运行期检查失败，无TEST_PASS。首版driver预计第一个变体触发后面的AXI顺序断言，但它实际在更早的记录输入检查失败，因此首版按分类不符退出；源码、日志和失败manifest保留在 `verified_build`。新版driver核验并继承该单例证据，修正分类后只运行其余六例及综合。未改RTL、测试台或断言以让负例通过。

## 整体综合

Vivado 2022.2，`xcu280-fsvh2892-2L-e`，默认23405-frame，整体顶层 `record_backing_service`：

| 资源 | 使用 |
|---|---:|
| LUT | 2,078 |
| 寄存器 | 3,035 |
| RAMB36E2（目录） | 18 |
| RAMB18E2（codec） | 1 |
| BRAM tile | 18.5 |
| 锁存器 | 0 |

这是实际组合后的综合结果，不是历史模块资源相加。RAM层级审计确认codec的320×32位存储和目录均映射BRAM。原始后备页载荷池31,456,320字节仍位于外部内存，不在这些片上资源中；页槽和队列端点也不包含在本顶层资源内。

综合0错误、0严重警告；一条并行综合条件提示保留。使用10 ns约束，没有布局布线时序或平台实现。为延续此前规避MCP `launch_runs` 父进程崩溃的方式，仿真使用现有MCP会话，综合采用本机非工程batch。

## 后续集成与限制

1. 将 `queued_scratch_endpoint` 与本子系统组合。用户命令禁止直接注入EXPORT、BEAT、COMPLETE；由内部适配流程生成并校验完整描述符。
2. WB先RESERVE后申请页槽WRITEBACK，取得有限tx，逐条EXPORT给本适配器；成功内存响应后发页槽COMPLETE，收到成功确认后才RETIRE地址。
3. RF先LOOKUP且要求published，再申请页槽REFILL；本适配器输出记录后逐条发BEAT。**记录握手不等于页槽BEAT已成功提交**：必须等最后一条BEAT响应并检查全部64条成功，再处理存储响应、COMPLETE和地址RETIRE。
4. 任一中间失败必须保留未完成页槽和地址租约；不能把部分写入页标成LIVE，或通过冷复位某一个子模块孤立释放资源。
5. 页槽FINISH_FENCE确认后再RECYCLE后备目录。两域回收均成功之前不接受新query，避免事务号复用先于旧地址隔离结束。当前本模块的RETIRE和fence_retired仍由可信调用者驱动，尚无完整设备排空证明。
6. 线性owner扫描、逐word codec、串行命令执行仍是明显吞吐约束。默认容量只通过综合；行为实例64 frame，无默认容量耗尽行为覆盖、CDC、超时恢复或板级性能结果。

已有目标仍未完成。下一轮优先推进上述页槽/内存闭环，再运行实际小查询端到端值回放和周期分解。

重复审计（不重跑构建）：

```sh
python3 hardware/scripts/report_record_backing.py results/rtl_record_backing_20261023
```

构建输出禁止覆盖。首版句柄4776已退出1，新版63752已退出0；没有活动计算。MCP会话 `vivado-20261023-101326-b113e545` 已关闭仿真，打开本轮record_backing工程，工作目录仍为旧queued结果目录。不要重启旧任务或操作A方案会话。
