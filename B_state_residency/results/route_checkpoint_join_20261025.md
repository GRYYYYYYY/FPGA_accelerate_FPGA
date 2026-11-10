# 路径 checkpoint 接入系统围栏与真实 AXI（2026-10-25）

路径状态现在由实际硬件导出并重新导入，已接入统一query wrapper、route adapter和实际AXI-backed owner链。q2搜索期间提出的checkpoint lease等待当前查询、回复及物理事务退休后才取得；持有期间阻塞16个host lane及query/route/recovery新请求。

试验首先实际运行q1/q2，RTL从两条已保存路径导出78字/312字节到外部测试台缓冲。诊断端口仅复位路径核心，随后拒绝expected_crc翻转1位的导入，接受原RTL图像并重新导出核验，最后执行实际AXI ripup，两个共享资源refs 2→1→0。CPU路径只作为独立oracle，不用于填充恢复流。

| 容量 | 等待lease周期 | 持有周期 | 全部入口争用周期 | 路径复位周期 | 路径CRC |
|---|---:|---:|---:|---:|---|
| full | 182402 | 1425 | 1424 | 4 | befc5228 |
| pressure | 224046 | 1425 | 1424 | 4 | befc5228 |

持有期间无FS/FD/FB/route/recovery/owner journal接受，未新增物理AXI访问。journal=10、last_sequence=2和2304位配置描述保持。两容量的七AXI日志及四个完整物理图像与旧正常基线逐字节一致（table闲置），四阶段完整owner与CPU一致。完整双query仍为116 POLL/114展开/447判定/293成本。lease和诊断背压是固定fixture，不能把这些等待/持有周期当板卡checkpoint延迟或加速。

正常旁路两容量24份周期轨迹/AXI/图像与旧基线字节一致，周期657222/724963。启用保存、诊断复位、坏CRC、恢复和再导出的整段周期658736/726677，包含四条路径命令及时间对齐变化，不是单次checkpoint开销。

26项独立lease单元检查覆盖健康状态变差后，仍须等待物理/逻辑/route退休、旧回复消费和CPP输入清空才能释放权限。普通错误锁存不再造成lease释放死等。这是受控谓词单元证据；没有在真实AXI checkpoint持有期间注入错误并验证完整接管。

新增接口全部闲置时，32槽/单槽的owner真实B错误回归均恢复并完整重跑q1，修复1项实际副作用。独立CPU/七AXI字节/完整owner/标签审计通过，保留已知328标签、q1六行authority的既有边界。此两例不代替checkpoint持有期故障试验。

完整系统默认32槽/16384帧U280 OOC：99321 LUT、66384 FF、160.5 BRAM、23 DSP，相对原恢复重试版增加10659 LUT/2859 FF。387逻辑端口/57270位，零latch/blackbox/file-agent；五个原组件改写、一个lease guard新增、117继承RTL/dat保持。默认ENABLE_TEST_INJECTION=0关闭诊断路径复位，CPP lease/流接口仍保留。没有place/route、时钟约束/Fmax或板卡测量，暂存资源开销仍需优化。

五归档共1632文件实际恢复复审，audit逐字节一致；32源文件冻结。开发阶段的声明顺序编译失败、lease单元驱动边沿错误、初步成功结果保留于route_checkpoint_join_development_20261025。故障回归原manifest沿用了旧scope描述，已保留原文件，仅修正文案并记录SHA；独立审计证明其余命令、来源与结果内容未改变。

下一步仍是完整checkpoint：

- 用同一版本化描述符绑定路径、owner primary/pool/allocator、design/cache、history/价格、标签页/目录、配置及journal；路径流与owner同一代快照目前由可信调用方保证。
- 实现通用checkpoint owner authority读取，扩展六行q1 fixture；当前q2新增资源的恢复不能由旧authority保证。
- 序列化并恢复query序号、epoch、成功/尝试版本下限。这里last_sequence只是未被路径复位影响，尚未证明全系统reset后恢复。
- 明确frontier/递归状态重启边界，推进未知页/旧prev、真实价格变化、回绕/容量回收和持久化；优化暂存多读口及考虑双bank BRAM。

详见checkpoint_join_coverage_20261025.json和hardware/variants/route_checkpoint_join_v1/CONTRACT.md。完整研究目标保持active。
