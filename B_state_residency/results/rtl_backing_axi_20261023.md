# 后备地址租约与 AXI 页服务验证

2026-10-23，`rtl_backing_axi_20261023/manifest.json` 和 `completion_audit.json` 均 **passed**。新增地址目录、原始页AXI引擎及两者的服务组合；外部不能直接注入内存完成。先分配并核验owner，再PIN地址，最后依据实际总线模型响应发布后备页。此前页槽、控制器、闭合队列及CPU基线均未改动。

这仍是独立后备服务模块，尚未与 `queued_scratch_endpoint`、160bit标签记录打包/解包器组成总顶层。它验证了AXI响应驱动的地址发布和租约保持，没有证明完整路由器的CLEAN/COMPLETE链或实际DDR/HBM性能。接口详见 [契约](../hardware/BACKING_AXI_CONTRACT.md)。

## 行为证据

Vivado/XSim **2022.2**，64-frame测试实例，最终905次服务响应检查通过；所有接口响应、AW/AR/W和读流在背压下保持稳定。测试先传完数据再延迟B响应，并允许W先于AW被接收，避免把地址/数据通道错误串行化。全部64种64B对齐的4KB内页起始位置都被覆盖。

|项目|结果|
|---|---:|
|成功写页|73|
|成功读页|64|
|总线错误场景|7|
|AW burst / B response|99 / 99|
|AR burst / 接收R beat|89 / 1,428|
|同时保留的地址租约槽|4，反序退休通过|

固定页大小1,344B，即21个512bit beat。夹具包含2页定向值和62页真实scratch页最终值，真实值来自冻结的字段轨迹；包括有效图、原始float32位模式、零值/不存在区别以及全部padding字节。正向读回逐beat与软件codec生成的字节比对。它是选中页的字节传输验证，**不是19/38个完整查询的AXI路由回放**，不等同此前472,689条控制器命令覆盖。

目录检查覆盖：重复owner不重复分配、错误owner不烧tx、未published不可换入、同一地址不可被第二slot租用、完成后仍保留租约直到消费者RETIRE、错误cookie拒绝、旧tx不能再PIN、满池仍能找到原owner、没有fence或仍有lease时不能回收、回收后原RAM内容不可见。四个不同地址在完成后同时保留lease，并允许按3→0顺序提交退休。

7个错误场景为：写SLVERR、错误BID、读DECERR、错误RLAST、错误RID、跨4KB第二写burst报错、跨4KB第二读burst报错。失败后不发布成功、保持FAILED租约并阻止地址回收；读错误前已收到的正确前缀只能暂存，不能作为完整页发布。当前无热恢复，协调冷启动后才重新工作。

## 实际修复：读错误后的突发排空

初版在第一个R错误后立即停止接收，旧TB在下一错误场景前冷复位，因而可能隐藏尚未排完的读burst。核对官方协议发现这一验证缺口：AXI不允许提前终止burst；读数据可丢弃，但已承诺的传输仍需完成。[Arm IHI0022H，A3.4.1](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)

现已增加READ_DRAIN：发生读错误后接收并丢弃当前burst的剩余beat，最后才返回失败，不启动下一burst。新TB在失败响应后明确要求从设备没有剩余R数据。保留初版源码和先前不足的日志于 `protocol_gap/`，新TB运行原版时观察到 `undrained read burst after error completion`。修正版最终接收1,428个R beat，包含所有错误burst的剩余数据；没有把原先行为PASS当作协议正确证明。

AW/W独立握手、写响应依赖和4KB拆分也按照同一官方规范A3.3.1/A3.4.1实现与检查。本次只验证所用AXI子集，没有完整协议checker、形式化、CDC或非法从设备的活性证明。B响应表示本接口的完成/可见性责任转移，不能解释为掉电持久性保证。

## 五个负向对照

|独立副本中的错误|首次被检出的行为|
|---|---|
|发送最后W后就完成，跳过最终B|`early B completion`|
|忽略BID/BRESP错误|第850条服务响应错误成功，期望IO_ERROR|
|内存完成立即释放消费者租约|`lease released before consumer commit / wrong fault`|
|没有fence也允许回收空租约目录|第843条服务响应错误成功，期望BUSY|
|修复前的读错误停收版本|`undrained read burst after error completion`|

全部先编译/展开成功，然后被具体行为检查拒绝；原生产源码未因负例修改。首版负例runner预期了同一早完成检查的另一段文字，实际首个Fatal为 `early B completion`，导致自动归档停止；原失败 `build_manifest.json`、源码快照和日志保留。独立v2 runner只修正该预期文字，在 `verified_build/` 完成五项对照与综合；没有修改测试断言或把错误当作正向通过。

## 默认容量综合及性能边界

对默认 **23,405 frame**、15位索引的独立 `backing_page_service` 顶层进行了U280 out-of-context综合，支持后备31,456,320B，30MiB字节预算内剩960B；目录/缓冲等片上资源另计。功能仿真只覆盖64-frame实例，未模拟填满默认容量。

|资源|本后备服务独立顶层|
|---|---:|
|CLB LUT|932|
|寄存器|1,416|
|RAMB36E2|18|
|锁存器|0|

18个BRAM均属于owner目录，未退化为寄存器；综合0错误、0严重警告，Synth8-7080并行条件警告1条。10ns只是探索性约束，没有布局布线或100MHz闭合结论。这些资源不包含此前2 BRAM的页槽/队列，也不能把两个独立综合结果直接当成已验证的组合顶层资源。

当前owner查找是顺序扫描，每条目两个读/检查周期。冷启动依次加入23,405个不同owner，需要273,885,310次比较、547,770,620个扫描周期，见 `directory_lookup_bound.json`。这是代码结构的算术计数，不是硬件时间测量，也未计分配、命令响应或AXI；它明确显示当前目录尚不能作为性能方案，后续需采用有界探测哈希或其他可验证的索引结构。

## 环境与下一步

只读 `/opt/xilinx/xrt/bin/xbutil --batch examine --report host --format JSON ...` 返回：XRT **2.14.354 / 2022.2**，当前容器可见设备 **0**，xocl/xclmgmt驱动版本unknown。原始结果 `xrt_host.json` 保留。这说明目前无法在此容器做实卡测量，不能据此断定宿主机物理上没有板卡；未安装驱动、编程设备或修改环境。

下一步为160bit标签记录/512bit页流的codec及总顶层适配：成功内存响应必须匹配原始完整描述符后才送页控制器COMPLETE，页提交成功后再RETIRE地址；fence成功要等待页域、地址域及内存响应一起收尾。在此之前，服务侧RETIRE和fence_retired仍是可信适配器输入，尚未接到现有队列控制器。错误恢复、查询检查点、目录索引优化及完整真实回放也未完成。

## 复核入口

```bash
python3 hardware/scripts/report_backing_axi.py results/rtl_backing_axi_20261023
```

manifest SHA256：`89db1f91e32e60307840b66ebf3f08c6b4cfd8f8243fe7ad6989b8acc6347980`。审计绑定源/快照、真实夹具输入、软件codec字节、最终仿真与精确计数、负例行为、默认容量综合/DCP/RAM清单和环境probe。正向仿真权威日志为冻结的 `simulation_session.log`；完整阶段和PASS已检查，子simulate.log空/NUL不能单独作证。

复用B会话 `vivado-20261023-101326-b113e545`，当前工程切换至本轮 `project/b_backing_axi.xpr`；会话工作目录仍为上一轮results目录，旧工程已关闭且证据未修改。最后已 `close_sim -force`，没有活动仿真。默认综合继续采用本机2022.2非工程batch，规避既往MCP launch_runs父崩溃；最终句柄15246退出0，首个matcher失败句柄12015退出1且保留。没有活动计算队列，完整研究目标仍active。
