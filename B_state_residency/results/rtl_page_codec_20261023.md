# 页记录编解码 RTL 与后备 AXI 串接验证

2026-10-23：`scratch_page_codec` 的独立XSim、与后备服务串接的XSim、六项故障注入对照、独立综合及最终证据审计均通过。实现160位记录与512位页流转换，并在整页规范校验和成功提交之前隐藏所有解码记录。

本轮不是完整页槽/DMA顶层：成功内存响应→codec提交/中止的控制由测试台task实现；页槽COMPLETE、地址RETIRE和双域fence仍待可综合适配器串接。没有实卡加速结果。

## 证据与数据来源

- [manifest](rtl_page_codec_20261023/manifest.json)、[最终审计](rtl_page_codec_20261023/completion_audit.json)。manifest SHA256：`ff8d055be3acaa280e834a2027034377dafce8a4bdaf0c3c8062e945693de003`。
- [接口契约](../hardware/PAGE_CODEC_CONTRACT.md)、[RTL](../hardware/rtl/scratch_page_codec.sv)。RTL和两组最终TB均已冻结到 `verified_build_v2/sources`。
- 使用上一轮[后备服务](rtl_backing_axi_20261023.md)的固定64页：62页来自真实字段捕获的选定页面，另2页为全空和特殊位模式定向样本。并非完整路由查询在AXI上的回放。
- 每页1344字节，64条160位记录，21个512位数据拍。`records.hex` 的4096条161位条目包含presence位；审计独立逐字节与原始 `pages.bin`、`pages.hex` 比对。
- 包含原始NaN payload `0x7fc12345`、负零 `0x80000000`、present-zero与absent-zero的差异；不转换float数值，不传输hist。

## 实际验证结果

| 流程 | 结果 |
|---|---|
| 独立codec | 5,645项检查；64页编码、65页解码；13,024输出背压周期 |
| 拒绝输入/提交 | 7例：失败提交、absent非零、记录padding非零、页尾非零、错误offset、编码padding非零、编码absent非零 |
| 显式中止 | 5例：编码收集、编码输出受阻、解码未收齐、等待提交、解码输出受阻；随后无需RAM复位即可解码全空页 |
| codec+后备服务 | 910项服务检查；4,096条记录和2,942个原始页流拍逐位核验 |
| 成功存储操作 | 73次写页、64次读页；64种4KB起始偏移全部覆盖；4槽地址租约保留及逆序释放 |
| 总线错误 | 8例；100次AW、89次AR、100次B、1,428次R握手 |

独立仿真结束于1,755,140 ns；串接仿真结束于2,110,770 ns。这是带测试台激励与背压的仿真结束时间，不是实际硬件运行耗时或吞吐。

前7类总线错误沿用后备服务检查：B错误、错误BID、R错误、错误RLAST、错误RID、第二写burst错误、第二读burst错误。新增第8例在地址4032开始写页，第一个仅含1拍的burst返回错误，此时编码页尚未全部输出；测试台中止codec，保留故障租约，不继续发送页尾。读失败时，即使已传输有效前缀，也不输出任何解码记录；已接受读burst仍由原AXI引擎排完。

AXI从设备模型独立于codec，验证地址、长度、4KB分割、W先于AW、延迟B及背压稳定性；原服务TB作为生成器输入保持不变。最终日志位于 `standalone_final/session.log` 和 `integration_final/session.log`，均包含编译、展开、TEST_PASS与正常结束。早期串接仅有声明顺序警告，保留在 `integration_pilot`；最终已移至声明后，计数相同。Vivado波形数组过大/空编译库路径提示不影响行为检查。

## 故障对照与综合

六个独立变体均编译、展开成功，并在预期断言处失败：绕过提交门控、接受失败提交、忽略格式错误、忽略中止、颠倒记录word序、丢弃presence。未降低任何断言等级。

初版验证driver在第5个变体执行前发现待替换片段出现两次，按保护逻辑停止；前4例已完成。`verified_build/build_manifest.json` 保留失败状态。新版driver使用完整右值定位，核验并引用前4例原始证据，只运行剩余2例及综合；`verified_build_v2/build_manifest.json` 正常完成。最终审计独立检查每个变体的唯一替换、运行期失败原因与全部哈希。

Vivado 2022.2、器件 `xcu280-fsvh2892-2L-e`，独立OOC综合结果：

| 资源 | 使用 |
|---|---:|
| LUT | 965 |
| 寄存器 | 1,469 |
| RAMB18E2 | 1 |
| BRAM tile | 0.5 |
| 锁存器 | 0 |

`words_reg RAMB18E2` 保存320×32位记录数据，确认没有被拆成寄存器。其余寄存器包括512位输入/输出拍缓冲和160位记录缓冲等。使用10 ns时钟约束；未进行布局布线或时序收敛，不能据此声称100 MHz。综合采用本机非工程batch，延续此前对 `launch_runs` 两次父进程崩溃的规避；仿真仍复用现有B会话。资源仅属于codec，不包含页槽或后备目录。

## 下一步及约束

1. 实现可综合适配器，绑定页槽EXPORT/BEAT、完整cookie、codec与AXI响应。写操作必须同时满足编码done和成功B响应；读操作必须成功内存响应后commit，消费64条记录后才向页槽COMPLETE。
2. **先校验编码输入再启动AXI写。** 当前串接TB只向编码器提供规范记录；若未来适配器先启动AXI，再因坏offset/padding中止编码，已有AW可能收不到剩余W。本轮没有实现这种写事务恢复。可在codec首拍ready前等待首拍valid（全部记录已校验），再发服务TRANSFER；还须处理PIN拒绝、停机与地址租约。
3. 页槽COMPLETE成功后才能地址RETIRE；失败后的租约不得释放。读格式错误也须保留上游未完成状态，不能因底层读成功而发布损坏页。
4. 为refill增加不分配的owner查询，避免查无页时误消耗后备地址。现有RESERVE会创建未知owner；原模块保持冻结，在新版本增加LOOKUP并回归。
5. 协调页槽fence和后备地址RECYCLE，禁止在两者之间接收新query。当前RETIRE/fence_retired仍依赖可信调用者。
6. 当前逐word串行编解码和线性owner目录均可能限制吞吐；先完成正确组合，再测周期分解和优化。当前容器上一轮XRT查询可见设备0；无平台/板级测量。

重复审计（不重跑实验）：

```sh
python3 hardware/scripts/report_page_codec.py results/rtl_page_codec_20261023
```

构建driver拒绝覆盖已有输出；后续变体应使用新结果目录。MCP会话 `vivado-20261023-101326-b113e545` 已关闭仿真，当前打开本轮codec工程，工作目录仍为旧queued结果目录。最终构建工具句柄1596已退出0；初版95880已退出1，无活动计算任务。
