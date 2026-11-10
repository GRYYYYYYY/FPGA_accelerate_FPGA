# 真实首次扩展整合（2026-10-24）

`hardware/variants/expansion_v1` 已把真实图CSR/属性AXI读取、设计级created/dead/持久缓存、首次过滤HLS以及自动分页排除HLS/原生标签端点接成 `node_expansion_engine`。META取得实际度数，CLAIM区分hit/miss；miss完成所有实际服务并发布，hit直接按持久位置位图重放。全部输出带原序位置、child ID和原始256位属性。

本轮是实际getChildren等价的邻接扩展组合。它还没有距离/代价更新、Frontier、连接搜索、回溯和占用/同网引用提交；不是完整FPGA路由器或板上加速结果。

## 真实设计与CPU基准

`expansion_inputs_20261024`通过原CPU Router loader与独立后缀解析核对：27,960 nets、180,326 connections、180,326个主/备用sink节点，hasLaguna=0。完整initial_design.bin由16B/node零记录加sink位构成。读取器保留初始created标志，排除服务使用初始created OR运行增量，防止把查询label present当作created。

CPU oracle保留原始getChildren，只添加位置/输出/创建观察hook，不替换过滤或发布逻辑。输入含1212次选定真实扩展、两次查询OPEN、一次CLOSE、两次显式checkpoint、110次prev/visited标签写入、prune切换及修改标签后的缓存重访。标签使用原CPU的paged零页语义；不是所有模式的prev初始化都可用零，后续搜索入口仍需显式source prev=-1等操作。

来源审计：`scripts/audit_expansion_inputs.py` passed，manifest SHA `66b108b1e126f42ede074531f88f995c6480c74fec76a95db2882c28b2406347`。完整sink初始化已做主机文件，不等于设备上传。

## 整合回归

`results/expansion_20261024`三组实际RTL回归和 `scripts/audit_expansion.py` passed：

| 指标 | 默认32槽 | 单槽TX6/GEN3压力 |
| --- | ---: | ---: |
| 扩展 | 1,212 | 1,212 |
| 缓存hit（无重新过滤） | 550 | 550 |
| 首次构建 | 662 | 662 |
| 输出child | 3,229 | 3,229 |
| HLS服务请求 | 10,753 | 10,753 |
| 原生标签READ | 240 | 240 |
| checkpoint（含显式2） | 2 | 27 |
| 扩展期间阻止主机请求的周期 | 469,489 | 466,500 |
| graph单拍读取 | 19,280 | 19,280 |
| design读取 / 写入 | 6,109 / 2,500 | 6,109 / 2,500 |
| label后备读突发 / 写突发 | 0 / 18 | 15 / 25 |

16扩展先导也通过。功能FRAMES256；默认完整容量FRAMES163840留给实际综合，不能说功能用例遍历了完整目录容量。压力的单槽/编号边界产生实际回填及自动checkpoint，图输出与设计最终状态保持一致。

服务分布：NEXT/EXCLUDE各2229，CREATE/CLASSIFY各1815，EMIT1812，CHECK_DEAD145，MARK_DEAD46，PUBLISH662。414条原始边被排除；3次CREATE后仍由CLASSIFY丢弃，顺序与原CPU一致。最终created增量1792节点、dead46节点。空结果489次（含缓存重访）。

独立审计从原始属性/CSR、sink集合和输入标签命令重新计算每个服务的phase/node/value/aux，逐行核对全部S/T事件和所有输出属性；重新构建设计记录，并核对完整145424192B后备文件。两配置最终SHA均为 `af7feabcab281d6ed54a6185f38a8bfa23c88a21dce8653da7dfe4a6ece3bebd`，也等于原CPU观察得到的最终映像。所有图AXI字节、设计和标签AXI回放/最终文件均核对；原生READ160位payload及present由独立标签字典检查。

MCP95.062s/exit0；manifest SHA `135f538360df0f474038604aeaf9a90510f020b589f8f13a6ba472d9a0b6a3eb`。用例虚拟周期为476407和475098；不同背压/槽数/编号设置下的测试时间不能当成性能消融，更不能与先前状态端点9.5213%混用。

## 组合边界

`expansion_boundaries_20261024`和独立 `audit_expansion_boundaries.py` passed，15组：输入拒绝/继续执行、两个节点数配置不一致、图META/NEXT读取错误、设计CLAIM读错误、CREATE/PUBLISH写B错误、强制pager故障、图/设计/排除三种错token、最终回复与输出流背压期间故障、实际token4/owner3耗尽。

token到15后，在部分构建claim中停止、保留mask3，没有回绕；owner完成7次扩展后，第8次在新的图读取前停止。PUBLISH错误B的模型已经写入物理valid，但顶层仍锁存fault/busy、保留claim，没有报告成功。每组故障用全新初始化后备文件，未假装从失败设计原地恢复。已提供的流/最终回复保持，调用者同时检查fault；全部扩展期间主机IO/生命周期入口被封锁。

MCP128.163s/exit0，manifest SHA `7de4f3161e0a534998d2289c7fb6efecdf8dc34808a3fdcfe068068e624b5ebe`。边界测试复用相同冻结组合RTL，仅缩位参数不同；源、内存文件和全部收据保存。

## 综合与后续

综合入口 `hardware/scripts/synthesize_expansion.tcl`。首轮预检查遇Vivado附带Python3.8不支持int.bit_count；显式系统Python又受PYTHONHOME影响。两次仅预检查失败保留在 `expansion_synthesis_preflight_20261024`；改用 `/usr/bin/python3 -I` 后在同一健康MCP会话继续，无RTL改动或重复仿真。

实际默认容量组合 `expansion_synthesis_20261024` / `audit_expansion_synthesis.py` passed：Vivado2022.2、xcu280-fsvh2892-2L-e、10ns研究时钟、FRAMES163840，**21726 CLB LUT / 20299 FF / 375 BRAM / 3 DSP / 546 CARRY8**，URAM/latch为0。LUTLP-1和check_timing组合环均0，无内部无时钟/无约束端点。2149输入和1928输出无IO delay，HD.CLK_SRC未设，未布局布线，不能据此给出接口频率或板上时序结论。

MCP终态411.06s/exit0、checksum `d460cd60`。300s交接后继续观察同一会话，没有重投；终态从status确认，再取history id58。历史输出截断于100KiB，完整marker区段从Vivado日志保存为full_synthesis.log；独立审计核对历史中841条完整行和末尾部分行均存在于完整日志（并行综合消息的呈现顺序不同），以及源、两项功能门禁、DCP、资源与结构报告。两版仅收据/有序前缀审计脚本亦保留，最终审计通过；这些是日志获取差异，不是RTL回归或综合失败。

接口和故障契约见 [NODE_EXPANSION_CONTRACT](../hardware/NODE_EXPANSION_CONTRACT.md)。下一步先核实Frontier静态状态冷复位/CLEAR，再接距离/代价更新、查询入口与目标标签、回溯和设计级占用/历史拥塞、同网引用及提交；随后完整真实连接搜索对照、布局布线、平台/XRT和板上。
