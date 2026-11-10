## 2026-11-07：跨账号恢复从这里开始

- 先读 `HANDOFF_20261107.md` 和 `AGENTS.md` 顶部；最新只读交接观察在 `data/derived/account_handoff_20261107_v1/observation.json`。原 O0/O2 与三个接续监督仍有效，无需重启或重跑已完成准备。
- 保留原容器与 `/tmp/A_graph_compression_recovery_20261025_v1`。新会话先核实环境和权限，再执行 `python3 scripts/experiment_status_v30.py`、`python3 scripts/experiment_status_v29.py`。不要仅因新账号看不到 PID 就判断旧任务失败。
- 09:47 UTC O2 step2042、第一段193863/2097152、0/4，原 O0 最新日志约350ms、0/4，完整 RTL 未验收。继续等待真实事务与完整审核；O2 若先验收，先验证终态和完整绑定再版本化接续原 O0 gate，避免两个执行 owner。U280 未插卡不阻塞此阶段。

## 2026-11-05：O2 观察到第一段扫描结束并进入第二段

- 第 1146 次采样中第二段扫描索引从 16 推进至 2576，时钟计数从 22899974 增至 22919974；两采样间墙钟 189.502 秒。该窗口证明第二段推进，不能外推整个运行速度或估计完成时间。
- O2 完整四态 RTL 的第 1145 次只读采样（2026-11-05T11:23:54.358000+00:00）中，第一段扫描索引为 2097152，第二段扫描索引首次观察到 16，时钟计数 22899974、完成 0/4。进程 PID 576099 身份核验有效；这是阶段变化，不是事务通过，也不是完成时间预测。
- 该时刻无 RTL 退出回执、独立审核报告或终态回执。保留原 O0、O2 运行与接续监督；后续使用 `python3 scripts/experiment_status_v30.py` 检查实际身份、第二段采样和完整验收，O2 通过后接续链仍需版本化处理。

## 2026-11-05：原 O0 日志推进至 250 ms，完整 RTL 继续等待验收

- 00:00:54 UTC只读观察已保存到`results/native_rtl_observation_20261105_v1.json`。原O0 PID3191525及O2 PID576099均重新核验身份有效；O0最新日志250.000158ms、0/4，无退出回执或输出快照。O2最新完整采样step837、时钟16739974、第一段trace扫描索引1310245、0/4，无RTL退出回执、独立审核报告或terminal回执。记录仅是现场观察，不是完整绑定审核或功能验收。
- 原native监督及bus64/full50/full30-read三个接续监督身份均有效，后三项仍等待前置验收；两项RTL均未触发所检查的资源终止条件。没有重启、替换或修改冻结输入、执行器及checker。后续先用`python3 scripts/experiment_status_v30.py`重新核验实际状态，不能将本历史采样当作当前内部状态。
- O2完成后仍须原C后检查与独立完整审核；若O2先通过，使用已准备的`validate_native_o2_acceptance_v1.py`复核，再版本化处理后续链与单执行owner，不能伪造旧native接受报告。完整功能链、物理实现、DDR/HBM及板上测量等原9要求8变体缺口保持。U280未插卡按用户安排，不作为当前RTL等待原因。

## 2026-11-04：完整 O2 已退出初始化并观测到 trace 扫描持续推进

- 新增只读`scripts/validate_native_o2_acceptance_v1.py`，供未来版本化接续复用：要求O2 owner按PID/starttick确认退出、精确terminal/report与独立audit命令/exit/log绑定，再调用原`check_native_o2_full_rtl_v1.audit()`重新完整审核并逐值匹配接受报告，前后重核回执文件。返回前置证据，不转移owner、不写旧接受报告、不改当前gate。9项合成准入及实际/proc身份测试通过，真实当前任务提前拒绝exit1；证据`data/derived/native_o2_acceptance_gate_preparation_20261104_v1/report.json`。当前完整RTL仍未通过，后续接续尚未切换。
- 已核实际O2进程身份。固定日志快照含603组完整采样：step211初始化索引达到2097152且退出两项初始化状态；step325首次观测trace active，step326首次观测扫描索引2110。最后五段采样各增加20000周期、2560槽位，墙钟130.893–134.021秒；末采样step602/60.2ms、扫描索引708645、仍0/4。随后只读现场step603/60.3ms、扫描索引711205，仍无RTL回执、独立审核报告或终态回执。
- 阶段证据`results/native_o2_trace_progress_20261104_v1.json`，SHA256=d83d748e90d7a5917e8ae258f82af8d71aa8ce6be2a2016ea9e4509ff94055b2；固定日志、plan、实际进程限制记录、静态周期下界报告四项SHA已重新核验。证明所采窗口内trace扫描推进，不证明后续无死锁、事务正确或完整验收；扫描比例不能当作实验完成比例，窗口速率不作全程ETA。
- 原O0最新日志已至200ms/0事务；原运行及接续监督保持。O2结束后原C后检查与独立完整输出审核已由runner接通，仍需实际通过回执；若O2先通过，须版本化接续原后续链并保证单执行owner，不能冒充旧native接受报告。当前无需重复启动RTL或修改冻结输入/runner/checker。
- U280未插入是用户当前安排；离线加载代码已准备，板卡缺席不阻塞本阶段RTL验证。下一步关注扫描阶段转换、事务完成及最终独立审核，不再把CPU活动单独作为设计进度。

## 2026-11-03：新完整 O2 执行与独立终审已接通，优先观察此运行

- 已实测新O2从100us至200us初始化索引5575→15575，时钟计数增加20000；首个采样7个共同值匹配历史O2。仍0/4，这提供过程推进证据，不是功能接受；继续依据新采样、最终回执与独立审核推进，避免重复启动或只复述CPU存活。
- `python3 scripts/experiment_status_v30.py`查看O2实际进程/采样，`--json`包括原v29功能链。O2 owner554290/starttick1688359826、最初实际kernel576099，trial `/tmp/A_graph_compression_recovery_20261025_v1/native_o2_full_rtl_20261103_v1`。runner/checker已冻结；禁止重启或改其绑定输入。
- 现有已审核O2快照执行原完整4事务/44指针/30模型，原DUT/模型/输入不变、保留四态及所有guard。每100us只读记录完成数/时钟/初始化/trace循环索引，支持区分真实推进与CPU活动。结束后自动原C后检查及独立全输出审核；尚无完整接受。原O0和三个接续监督继续运行/等待。
- 如果O2真正独立通过，需要新版本typed前置接续bus64/full50/full30/read并消除重复owner风险；当前尚未改旧gate。不能用短窗口、过程采样或Verilator试验取代全部输出/正周期/原C/回执检查。
- 辅助Verilator兼容性失败证据见AGENTS顶部：原十进制解析超时、hex大数组初始化分配失败、static-init继续到Z初值不支持；实验fourstate也不支持。所有私有改写均未进入当前O2/O0运行。六项初始化四态局部对照通过，不是全核通过。
- `scripts/program_u280_xclbin.py --help`是板卡准备入口。默认离线校验镜像/校验和并打印命令，显式--execute才加载；需要后续实际通过RTL/link审核的硬件xclbin，当前没有最终镜像，也没有板上结果。

## 2026-11-03：先完成完整 RTL 验证，U280 暂不插卡

- 用户已明确：板卡未插入，当前先准备部署/烧写代码；优先解决完整 RTL 验收。未插卡不阻塞现阶段软件/RTL工作。旧数据清单的pending项不能作为整个项目缺数据的依据，当前RTL输入齐全。
- 原native继续运行；新 `scripts/probe_native_verilator_v1.py` 对原冻结154份源码做独立兼容性预检，输出 `data/derived/native_verilator_compatibility_20261103_v1`。先检查真实receipt/log及当前子进程；若可编译，再评估完整原输入的辅助运行，保留4事务、44指针、30模型、原输出与C oracle，不缩范围换通过。
- 辅助Verilator后端具有二态语义限制，兼容性预检或后续辅助结果均不自动满足原XSim独立验收门槛。现有原生RTL及后续监督不重启、不改冻结输入。板卡宿主/链接入口已有历史版本，最终部署准备须核对与当前核的ABI/RTL一致，不能把旧15参数search核入口当作当前44指针batch核已适配。

## 2026-11-02：trace提前停止的可信状态边界已实证

- 新增tests/test_trace_live_count_contract.cpp，使用原SearchTraceRecords及NodeOccupancy的小容量实例，g++ -std=c++14 -O2 -Wall -Wextra -Werror编译运行通过。两项live时将meta[2]人为改为0后，valid_meta仍通过，原trace仍按flags记录2项；除序列化的meta[2]外输出逐字一致。该故障注入明确位于NodeOccupancy文档所要求的可信状态之外，不是实际运行中发现的损坏。
- 顶层batch_control[6]=0时接受外部状态，入口只调用valid_meta及节点数等检查，不全表核验flags与meta[2]一致；因此不能把范围检查视为一致性证明。假设在meta[2]=0时直接停止的优化会漏掉此故障注入中的2项，不能主张对所有范围合法的输入保持原行为；若只承诺可信状态，必须明确顶层调用契约及证明状态生产/保存链，或者保留不可信状态的原行为。当前未修改DUT或实现优化，测试不构成RTL/物理/板上验收。
- 测试SHA256=d3acbfc0abf95824e8af30e132a7299a92e88fbc703bdf3bbcd071359c57fdee；原trace/node/top源码SHA256分别为7110a986b5ad9ff683eedfa77f0c1fc4553d3b7fa17e41a9827d3aa6cdde8359、ff03872a0289a3e826036bbeaf792b8dd89c1698be1d796b975a10c106e48176、7485e3d647e86aee4bdf1843289b036b2b928743e3b0baf3870741a011768434。原RTL及后续监督仍在运行或等待，完整实验未完成。

## 2026-11-02：trace可信存活计数提前停止的真实数据可行性筛查

- scripts/analyze_native_trace_live_scan_v1.py重建已审核mode0参考中三个有效事务的8条net操作，验证node_meta[2]、owned_keys顺序及事务末完整2097152 flags/所有非零槽keys均匹配实际44端口快照；AST及实际碰撞/墓碑重用检查通过。报告results/native_trace_live_scan_reconstruction_20261102_v1.json SHA256=6803d77deb32d734f4900467ffe57f46006e2f818f5606787c14d3b9d0177463。
- 可信状态下若在看到全部live项后停止扫描，case0两net各少31.19%槽，带种子case1四net各少3.48%，case2两net各少83.36%。仅扫描迭代数推演，不是测得RTL周期或性能。case1重建依赖参考测试明确77/节点1种子；invalid第四事务未作此分析。
- 该思路依赖meta[2]与真实flags==1数量一致，损坏/不可信状态可能不同于原扫描；不能跳过契约证明或错误路径。hls-optimize要求vitis-run及完整cosim/physical基线，而本机2022.2可用vitis_hls、无vitis-run/对应HLS报告工具，原完整基线仍运行。尚未实现候选或运行其HLS；若后续采用兼容批处理，须隔离源码、严格字节/状态差分及完整原功能/物理门，不修改当前活跃链。完整实验未完成。

## 2026-11-02：O0/O2重复100us对照完成并独立复核

- 实际四次O0/O2/O2/O0均exit0/无abort，20采样×21探针全部一致；O0分别353.105895/353.426002秒，中位353.265948秒，O2分别305.946727/306.091316秒，中位306.019021秒，O2/O0=0.8662567759，窗口耗时低约13.37%。owner3414115已终态退出。
- 独立复核results/native_xsim_optimization_independent_audit_20261102_v1.json SHA256=3ffe578fc49991e45fcca1e4f4ddc2d9f1edc4f3c1a71486d31bf89908dee729；源报告SHA256=232cc8b9b2658bbd4d84650dfd83b34ee8d89358af8002000e55635a30cdb3e3。重读源报告全部文件及311输入/快照绑定，独立重解析采样/完成标记/回执SHA、命令差异及计时计算。
- 仅100us初始化窗口，含启动/查询，共享主机缓存负载未控；不能证明完整事务/全输出等价，也不能外推后续trace扫描或端到端提速。原O0完整RTL已运行约69小时、最近0/4，继续原进程及其接续监督；不据本诊断替换快照、绕过gate或承诺完成时间。仍需完整功能链、physical、板上等原要求。

## 2026-11-02：两次O2短重放完成，最后O0进行中

- replay_2_O2 exit0/无abort/306.091秒，日志SHA/唯一完成标记核对；O0及两次O2完整20采样×21值重新解析一致。三个时间含启动和查询、共享主机，完整重复性能比较仍须第二O0和全部绑定重核，不是功能接受或全程提速证明。
- owner3414115进入replay_3_O0，实际xsimk671111及actual_limits中的starttick已核；原native仍有效0/4，继续等待完整功能链。

## 2026-11-02：首次O2短重放完成，第二次O2进行中

- replay_1_O2 exit0/无abort/305.947秒，实际日志SHA及唯一完成标记核对，20采样×21值与replay_0_O0逐项一致。只覆盖100us早期窗口，时间含启动和查询、共享主机负载不受控，尚无重复性能结论或完整功能接受。
- owner3414115自动进入replay_2_O2，实际xsimk566360/starttick1679213846身份核对通过；后续仍需第二O2和最后O0及全部输入/快照核对。原native仍有效、最近0/4；完整实验及原范围缺口保持。

## 2026-11-02：首次O0短重放完成，首次O2短重放进行中

- replay_0_O0 exit0/无abort/353.106秒，日志SHA与真实完成标记已核，完整20采样×21值与历史O0短重放重新解析一致。仅100us早期诊断，非完整RTL事务接受。
- 诊断owner3414115已进入replay_1_O2，实际xsimk460948/starttick见actual_limits并已核身份；初始21探针值与O0一致，整个窗口仍未完成。之后还有另一O2及另一O0，独立最终比较尚缺；不因单窗口相等推断整个设计等价或提速。原native及后续链保持等待。

## 2026-11-02：独立O2编译成功，重复短重放已开始

- O2 xelab3425427正常退出，独立trial的elaborate_O2.receipt.json为exit0/无abort/3377.077秒，日志SHA256=ac9589e7cb7a4c2451ed9bb5e706c505bd5f51f0010d0f3f7020d8d11deab0d8、Built simulation snapshot，peak RSS156774092KiB、无新增OOM；O2 xsimk SHA256=77b9e2b1dec7e2420fc0391048c1eeab822d838d11bb730f5b478b854f5004e7。仅编译通过，非功能或性能结论。
- benchmark owner3414115自动进入replay_0_O0，xsimk339431/starttick1679146051及AS96GiB/stack256MiB/core0已核。后续O0/O2/O2/O0四次、20采样×21信号匹配历史O0；当前无短重放完成回执及最终性能报告。不改活跃driver，不重启任务；需留意O2优化后探针若缺失将如实失败。
- 原native3191525仍运行、最近0/4，原接续链等待完整独立验收；原9要求8变体、physical及board等缺口保持。

## 2026-11-02：已完成O0短重放的输入及快照未变

- 原已审核compiler trial与已完成native_first_transaction_diagnostic_replay_v1对比：原快照9文件逐SHA一致，重放新增5个运行时文件；原plan的293项输入在重放后逐SHA一致、无缺失（约6.91GB）。这支持当前基准对原有文件的完整性检查用于O0，但不证明O2文件行为或功能等价。未更改活动任务。
- 继续按下条观察正在运行的O2编译和O0/O2重复诊断；原四事务、接续链、physical和board缺口保持。

## 2026-11-02：独立O2编译与重复短窗口性能诊断已启动

- scripts/benchmark_native_xsim_optimization_v1.py owner3414115/starttick1678802546；控制data/derived/native_xsim_optimization_diagnostic_20261102_v1，trial=/tmp/A_graph_compression_recovery_20261025_v1/native_xsim_optimization_diagnostic_v1。原编译gate及plan实际列出的764复制文件/空目录通过，实际xelab3425427/starttick1678806056已进入elaborate_O2，AS192GiB/stack256MiB/core0实核；原完整运行保持。
- 同2022.2、原全4事务44指针30模型/DUT/ROM/guards，唯一编译配置变化--O0→--O2及独立snapshot名；-mt off保持。新OOM/reset停止自有诊断进程，无raw-free门槛，编译7200秒墙钟上限。后续自动O0/O2/O2/O0四次100us诊断，各AS96GiB/1800秒；相同21探针×20采样逐值匹配原诊断，输入和两个快照受哈希保护。缺对象/值不同/异常则失败，不改原验收。
- 后续先实核该owner、actual_limits、log、receipt；编译成功后核四次重复和完整采样比较。预期results/native_xsim_optimization_diagnostic_20261102_v1.json，仅早期初始化窗口及含启动/查询计时，不是4事务接受或可外推全程提速。当前没有性能结果；若O2优化删除探针导致拒绝，不得降低观测要求冒称等价。
- 当前脚本/plan冻结，勿重启；v29仅原功能链，须另观察本诊断。MCP现有两会话属于B目录，未触碰；独立CLI沿用本机2022.2已保存help，--O2为工具支持的默认优化。原9要求8变体及完整功能/物理/板卡缺口保持。

## 2026-11-02：30秒原进程调度观察未见资源等待瓶颈

- 原native PID3191525/starttick1654203702在采样前后均核实一致；只读/proc及cgroup，未附加调试器、停止或修改进程。结果results/native_scheduler_sample_20261102_v1.json，SHA256=5a68f0d7eaf7c801f82f3842094b6caff0b49ccce7068541761d17af524d36f2。
- 30.0317秒窗口中，worker3191528运行约30.0318秒（读取时差导致比例略超1），runqueue等待0.000067615秒；进程用户态30.01秒/内核态0.02秒。cgroup无新增限流/OOM，memory及IO pressure total未增加；进程磁盘read_bytes/write_bytes均未增加，major faults为0，minor faults增加33589。此窗口主要为用户态计算，不支持以CPU排队、限流或磁盘停顿解释当前慢速；不能推广为整个运行期间没有资源瓶颈。
- perf/pidstat/gdb/pstack均未找到，perf_event_paranoid=4；未进行函数级profiling，不能定量归因于FSM、AXI模型或内存分配。继续保留原完整RTL运行及既有串行接续；若后续要比较仿真编译优化，应另作版本化完整输入诊断，不改冻结快照/验收门槛。当前最新仍0/4，无功能接受，全部原9要求8变体缺口保持。

## 2026-11-02：只读状态入口v29区分进程、日志进度和验收

- 新增python3 scripts/experiment_status_v29.py及--json；完整保留v28任务/五项回执观察，另显示原native的PID/starttick/argv匹配、运行及CPU小时/RSS、最后日志事务数及仿真毫秒、日志文件年龄、输出/receipt存在性、新OOM/reset观察。缺证据显示observation_error，不据进程存活或产物存在推导功能接受；不修改任何执行器或gate。
- 周期背景只接受已核报告SHA8409c863f1a56e9da7040264de6d821641a9acb3980c144b04af44f5a7ebb4af，并每次重新读取9项绑定，再显示335.54432ms成功路径条件下界；明确不是实测延迟、现场状态或无死锁证明。实际文本/JSON及缺证据降级检查通过，旧状态脚本保持。
- 资源健康检查results/research_progress_health_review_20261102_v1.json：当时原进程约67.9小时、约1核CPU、RSS15.3GiB、无新增OOM，日志约22.6小时未更新。到100ms日志用了约45.31小时，历史平均约123仿真周期/现实秒、每50ms约22.65小时；这是历史均值，非近期实测区间/ETA/当前仿真时间。实际xelab命令--O0/-mt off已核，运行主要单计算线程；大周期数与高逐周期仿真成本共同限制验证，尚未CPU profiling量化各因素。
- 当前原native与三个接续监督身份有效、最近0/4，无完整输出/回执。两项短诊断已经完成退出，不重启。后续仍须原完整功能验收及全部物理/板卡/原9要求8变体缺口；完整实验未完成。

## 2026-11-02：首事务成功路径静态周期下界335.54432ms，100ms时0/4不足以指示异常

- 新增scripts/analyze_native_trace_cycle_floor_v1.py，读取原native实际RTL并逐SHA匹配原复制plan，解析6681状态的a_write_net_trace_record FSM。两完整2097152项扫描：head3314/update3459与head5328/update5543；每16项边界最快75周期，其余15项各最快3周期，最短路径均保存。验证计数器0起/+1/终值、低4位分组、唯一两个counter写入和循环无旁路出口；将握手/分支放宽为最短可达路径，因此仅是乐观静态下界。
- 每扫描至少15728640周期。参考首事务reset=1、一轮两net，每net调用trace两次全表扫描，四扫描至少62914560周期=314.5728ms（实TB5ns时钟）；此前2097152项reset两状态循环至少4194304周期。两项串行合计67108864周期=335.54432ms，尚不含搜索/其他循环/启动/额外AXI等待。原100000143000ps日志约100ms，低于成功路径这一必要工作量，故该时刻0/4与设计工作量一致；不能由此断言当前现场无死锁。
- 报告results/native_trace_cycle_floor_20261102_v1.json，全部9个文件绑定重新核验，最短路径及计算复核通过。条件是原参考成功路径/复位不重入/两net串行执行；不是形式化全设计证明、实测总延迟或事务接受。两项短重放已结束，无新增重放/RTL/物理执行；原native与三个接续监督仍实际有效、0/4、完整实验未完成。
- 后续应保留此周期量级作为等待解释，并在新的现场/事务日志出现后再判断进展；禁止用早期重放或本静态下界冒充原现场状态。原9要求8变体、全功能链、physical及DDR/HBM/board缺口保持。

## 2026-11-02：首事务两轮独立短窗口诊断完成，早期初始化推进已实测

- 用户追问长期0/4后，检查真实TB确认finish_cnt只在AESL_done时增加、PROGRESS_TIMEOUT=10000000、LATENCY_ESTIMATION=-1。原bounded.tcl的33探针在run 10 sec之后，当前原日志只到100000143000ps；没有WDB/VCD，不能用CPU时间推断硬件进展。
- 新增diagnose_native_first_transaction_v1.py/v2.py；严格重读原编译审核，复制原冻结编译trial全部795文件与空目录，不改原运行/输入/DUT/checker。使用同一快照与完整4事务44指针30模型输入，只更换独立副本的诊断Tcl。运行AS96GiB/stack256MiB/core0、1800秒诊断墙钟上限、无free门槛、新OOM/reset只停止自有子进程。
- 两轮已串行结束：/tmp/A_graph_compression_recovery_20261025_v1/native_first_transaction_diagnostic_replay_v1、v2，实际exit0/357.717750184秒与228.041920338秒，两个实际XSim均已退出。v1采20组0–100us的21信号；v2采1/2/10us，逐位解码top/batch状态及30AXI的300握手信号；共同21信号在相同采样时刻完全一致。均仅诊断，不是任何事务或功能接受。
- v1在50/60/70/80/90/100us的i_135_fu_658分别575/1575/2575/3575/4575/5575，state1510=1、write_block=0，证实早期2097152项清零循环推进。最初从中间日志误述整个窗口未入清零，已按完整原始采样更正并在报告保留说明。v2在1/2us top与batch均state1/idle，10us top state428等待grp_begin_r_fu_1157_ap_done，batch仍idle；TB start_cnt=1不等同DUT已开始有效计算。
- search_trace_records.hpp每net两次完整2097152项flags扫描；原参考首事务两net意味着该路径有8388608项检查，是明确固定开销，但不证明原运行100ms后的实际位置或排除后续死锁。不能把早期重放当原现场观察，也不能删扫描/减容量/缩事务换取通过。
- 证据results/native_first_transaction_diagnostic_replay_20261102_v1.json、v2.json；静态诊断及启动日志data/derived/native_first_transaction_diagnosis_20261102_v1。v28尚无这两项短诊断显示，两项均完成无需再监督。原native3191525/start1654203702与三个接续监督重新核实有效，仍0/4、无receipt，oom0/oom_kill2/max254未增。下一步应围绕后续全表扫描定位/观察，而非只反复报告CPU存活。原9要求8变体/完整功能链/physical/平台DDR-HBM/board缺口保持，完整实验未完成。

## 2026-11-01：原native RTL日志仿真时间推进至100000143000ps，仍未完成首事务

- 原native PID3191525/starttick1654203702已重新实读/proc核对一致；同一rtl.log依次记录0/4 @128000、50000138000、100000143000ps。此次日志变化证明仿真时间继续前进，不能据此计任何事务通过，也不能把此前CPU计时增加等同于仿真时间推进。
- 当前rtl.receipt.json仍不存在，rtl_*.bin快照为0；日志无Fatal/ERROR:/A_REBASE_。cgroup memory.events为oom=0、oom_kill=2、max=254，未增加。保留原运行，不重复启动或改动冻结输入/执行器/checker。
- v28重新核实native监督及实际RTL进程身份；bus64/full50/full30-read三个接续监督身份均有效，仍等待各自完整前置独立验收。五项C/HLS/setup/input报告回执通过观察，不替代完整RTL接受。下一轮重新核实际进程、日志、退出回执和完整输出；功能链、physical、平台/DDR/HBM/board及原9要求8变体缺口保持，完整实验未完成。

## 2026-10-31：新版三项物理实现输入与提前拒绝独立预检通过，尚未执行

- 新增prepare_collision_safe_physical_execution_v1.py、collision_safe_physical_entry_v1.py、check_collision_safe_physical_execution_v1.py、validate_collision_safe_physical_execution_v1.py和八项保护机制测试。新版physical源直接取当前已审核collision_safe bus64 HLS的CSR115/compact118份RTL/ROM，read_control取原staged候选60份；不沿用旧encoded候选DUT或旧物理结果。
- data/derived/collision_safe_physical_execution_20261031_v1含csr、compact、read_control/csr三项。run_flow.tcl和clock.xdc逐字节复用原已验证2022.2流程，U280/5ns/1.35ns/2线程、synth/opt/place/phys_opt/route、3DCP及全部DRC/methodology/timing/route报告保持，无豁免。entry要求新native/两bus64/full50/full30 v6/read v5完整接受、终态链owner退出及实际同模式RTL/ROM绑定后，才能保护专属MCP Tcl会话并执行。
- 准备报告results/collision_safe_physical_execution_preparation_20261031_v1.json共2676绑定，SHA256=818009cc6f0130d4a45663349b112981b3477481b6f357851b6bc19fefc4f3a0。独立预检results/collision_safe_physical_entry_validation_20261031_v1.json共2754绑定，SHA256=d82c9ade099d8b37d9ff336b4954c04b7e6cac0a57ad1d96c7d6265f7536ace3，状态corrected_three_physical_entries_sources_and_early_rejection_verified_not_executed。
- 八项测试（含实际自有fixture OOM停止、无关进程不被停止、复用PID拒绝、完整read与same-mode源码绑定、精确MCP终态历史）通过；六项真实提前arm/audit拒绝通过。原terminal_receipts函数AST一致。完整绑定及复制后每份RTL/ROM均重核，三项state/guard/session均未创建；没有新Vivado会话，没有综合/布局/布线、时序或上板接受。AS192GiB/core0、无raw-free门槛、新OOM/reset停止自有会话契约保持。
- 新输入/入口/checker已绑定冻结。待完整功能链实际接受后再用专属Vivado2022.2 Tcl会话执行，并捕获实际MCP终态/历史交原checker；不触碰B目录会话。旧encoded/FSM缺口仍单列。当前原native3191525实际仍运行、最近0/4、无新增OOM，全部接续监督保持；原9要求8变体及平台/DDR/HBM/board等缺口保持，完整实验未完成。

## 2026-10-31：完整full30/read新版串行接续监督已启动

- 新增snapshot_read_serial_prerequisites_v2.py、run/check_snapshot_dpi_rtl_v6.py、run/check_search_read_control_staging_dpi_rtl_v5.py及supervise_snapshot_read_serial_v2.py。接新full50 v3成功终态及owner退出，先全绑定重读、核实际full50回执/报告SHA，再串行full30执行→独立审核→full2 read执行→独立审核。当前新trial/报告均不存在，尚无实际执行或功能接受。
- 与各旧入口精确差异核对：只改新版typed前置、报告/controller/trial路径及runner的SIGTERM清理；原DUT/ROM/13指针环境、10/7模型、4pages、8个snapshot只读monitor、完整30/2事务、原C与每份完整输出比较、独立storage编辑审核均保留。既有run_full_scope_phase_v1不变，实际phase AS64GiB/stack64MiB/core0，xsc单线程；审核器AS16GiB。无raw-free门槛，新OOM/reset只停止自有子进程。
- 四项scope单测（含容量、事务、周期、RO、原地址及绑定拒绝子例）通过；两runner与两checker实际缺前置/缺trial拒绝，均未创建输出。准备观察脚本曾错误预期snapshot checker先读trial，实际先拒绝缺native接受；此为测试预期顺序错误，原失败log及correction保留，未改设计/checker以绕过。四项确认回执/log已完整保存。
- 原准备712绑定逐项重读通过。新results/snapshot_read_serial_preparation_20261031_v2.json共738绑定，SHA256=ed6f379afb0141c41efcfdd71230dd5af5177d92296ee91ea4f03021a101b013；验证/回执/log位于data/derived/snapshot_read_serial_preparation_20261031_v2。代码及准备已冻结，禁止直接编辑。
- 新监督1486006/starttick1656341714实际/proc argv/starttick核对通过，data/derived/snapshot_read_serial_supervision_20261031_v2/state.json为waiting_corrected_full50_tree_independent_acceptance，绑定full50监督1331363及其plan。v28已显示完整接续；新native→bus64 CSR/compact→full50→full30→read均有等待监督，但等待不是功能接受。
- 原native3191525仍运行、最近0/4，未新增OOM。原9要求8变体、旧encoded/FSM未接受事实及physical/board等缺口保持，完整实验未完成。下方“新版full30/read尚未连接”为历史。

## 2026-10-31：新native/paired RTL之后的full50接续监督已启动

- 发现旧full50→full30→read监督仍绑定已失败的旧native/encoded链。新增route_tree_serial_prerequisites_v2.py、run_route_tree_full50_recovery_v3.py、supervise_route_tree_recovery_v3.py，精确要求新native四事务及新bus64两模式各四事务独立报告、44指针/30模型、完整输出/正周期、全绑定重读和报告前置身份一致；不把新结果算作旧encoded/FSM候选通过。
- full50仍复用未改的route_tree_rtl_pipeline_v2.py、原DUT/综合/TB/完整C oracle/check_route_tree_rtl.py，50事务、nodes1048576/path_edges524288/state_words65保持。wrapper只改变typed前置、新目录/报告和SIGTERM自有子进程清理；编译/RTL/postcheck AS64GiB、原CPU ASan保留、不设原始free门槛，新OOM/reset停止自有子任务。
- 五项前置回归通过（合成fixture只验证准入逻辑，不作实际RTL证明）；实际缺native报告拒绝且未创建OUT/PROJECT/AUDIT/CONTROL；原full50预检605输入绑定通过。准备报告results/route_tree_serial_recovery_preparation_20261031_v3.json共32绑定，SHA256=ad10919906da5b67ff2bf556f206ce410b72a4e192c9f2fb62e4af7c8901057c，日志/回执位于data/derived/route_tree_serial_recovery_preparation_20261031_v3。
- 新监督1331363/starttick1656292920已实读/proc核argv/starttick，data/derived/route_tree_recovery_supervision_20261031_v3/state.json为waiting_corrected_paired_full4_independent_acceptance。绑定当前paired监督4029495及其plan；其成功终态且owner退出后才完整重读新三个接受报告和paired审核回执，再启动full50。当前无full50实际执行、无接受。代码/准备已冻结，不直接修改。
- v28只读入口已显示新full50等待监督。原native3191525仍匹配当前身份、最近0/4；paired RTL继续等native。新版full30/read接续尚未连接，后续需版本化准备且保留全部30/2事务与原独立检查，不能复用旧失败链状态。原9要求8变体、physical/board等缺口保持，完整实验未完成。

## 2026-10-31：只读状态入口补齐实际审核回执，当前使用v28

- 新入口 `python3 scripts/experiment_status_v28.py` 保留v27完整历史JSON和当前实际进程身份观察，文本视图将已结束的pair执行显示为C_and_HLS_execution_complete，避免沿用执行器历史stage中的audit_pending误导当前状态。
- 新增五项审核报告观察：pair独立C/HLS、两模式setup及非零输入；本轮逐核实际report/result SHA、status、exit0/无abort和log SHA，均report_receipt_verified=True。该入口不重新审核底层全部artifact绑定，不新增功能接受或替代原独立checker；JSON保留原执行stage。
- 原native RTL及其监督、paired RTL接续监督仍实际有效；原native最近0/4，无完整输出或退出回执。未修改活跃执行器、DUT、输入或审核器，未重启实验。原9要求8变体、完整RTL/physical/board缺口保持，完整实验未完成。

## 2026-10-30：两模式完整非零输入均独立通过，恢复链全部九步完成

- `results/collision_safe_bus64_nonzero_mode_1_audit_20261030_v2.json`独立通过：collision_safe_bus64_full44_inputs_all30_guards_all44_relocations_independently_verified，3699绑定，SHA256=ee65af37ca5f319c646f681bddd866114d27c05bda3413fc4a0896d8f7b8d4c9。实际checker exit0/93.305796882秒，日志/回执/报告结果SHA核对一致；mode1完整4事务44指针、30模型guard及44重定位，rtl_executed=false。两模式输入审核均通过，尚不是RTL执行验收。
- 恢复监督v3 owner4005048已complete并退出，stage=both_modes_full_nonzero_inputs_independently_audited_RTL_pending，全部九步完成。原checker106875已退出，不重复启动。完整paired RTL监督v3 owner4029495继续等待native目录恢复v2的完整四事务与独立验收，尚未启动新bus64编译/RTL。
- 本轮实读native kernel3191525与原starttick/argv匹配，最新日志仍0/4；功能通过不可从进程存活推断。原9要求8变体、其余功能链及physical/board缺口保持，完整实验未完成。

## 2026-10-30：compact fresh setup独立通过，非零准备已运行

- `results/collision_safe_bus64_cosim_mode_1_audit_20261030_v2.json`已通过：collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending，3115绑定，SHA256=ade2a19a56f658a495a5c6ffa3f88b8aec1f4246217547d66239c31d4fd5f157。实际checker exit0/72.252686298秒，日志/回执/报告结果SHA核对一致，mode1完整4事务44端口30模型，rtl_executed=false。两模式fresh setup均独立通过，尚不能计配对RTL功能通过。
- 恢复监督v3 owner4005048已自动进入mode_1_nonzero_prepare，实际prepare72487/starttick1654539052及--mode1 argv核对通过。后续仍须该准备完成及原独立非零checker，不重复启动。完整RTL监督v3继续等待原native目录恢复v2完整验收及两模式前置；原native仍实际运行、最近0/4。
- 原9要求8变体及physical/board缺口保持，完整实验未完成；只读观察仍v27。

## 2026-10-30：CSR非零完整输入独立通过，compact fresh setup准备已启动

- `results/collision_safe_bus64_nonzero_mode_0_audit_20261030_v2.json`独立通过：collision_safe_bus64_full44_inputs_all30_guards_all44_relocations_independently_verified，3680绑定，SHA256=9829efbaea06a224e2c41b75c86610b85f292b7da180a8d946756dc16d676108。原checker exit0/93.296844786秒，日志/回执/报告结果SHA核对一致；mode0完整4事务44指针、30模型guard与44项地址重定位、其余DUT/ROM/输入不变，rtl_executed=false。此为完整仿真输入验收，不是RTL执行通过。
- 恢复监督v3 owner4005048已自动进入mode_1_fresh_setup，实际prepare4172375/starttick1654511056及--mode1 argv核对通过；旧CSR checker已结束，不重复启动。compact先重读pair gate再执行fresh完整setup，之后仍须setup独立审核、非零准备和独立审核。
- 完整RTL监督v3继续等待native目录恢复v2及两模式非零验收，未启动新RTL。原native仍运行、最近0/4，cgroup oom0/oom_kill2无增加。原9要求8变体和physical/board等缺口保持，完整实验未完成。

## 2026-10-30：CSR fresh setup独立通过，非零输入已准备并进入独立审核

- `results/collision_safe_bus64_cosim_mode_0_audit_20261030_v2.json`已通过：collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending，3099绑定，SHA256=9c379fec1d5bba460a62b3212f63541670d0d84027219f17ec218f87b487a96b。原fresh HLS exit0/147.691186450秒，实际独立checker exit0/71.257620102秒；日志/回执/报告结果SHA核对一致，mode0、4事务/44端口/30模型完整，rtl_executed=false。
- 恢复监督v3 owner4005048自动进入mode0非零准备（原child4110427已结束），prepare完成后现为mode_0_nonzero_audit，实际checker4143505/starttick1654501721、argv --mode0已核。非零准备保留原完整输入与全部guard及地址+4096契约；仅准备完成，尚无非零独立接受报告，不能计为RTL通过。前项prepare实际AS16GiB/stack64MiB/core0已核。
- 当前新非零checker继续完整重读审核，不另起重复检查。之后监督按原顺序进入compact fresh setup和其非零准备/检查；完整paired RTL监督v3继续等待native v2和两模式前置。原native仍运行、最近0/4；原9要求8变体及physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64完整配对C/HLS独立通过，CSR fresh setup准备已启动

- pair execution v2已complete、completed_modes=[0,1]，两个原HLS均退出。compact实际receipt exit0/1226.454385977秒、完整4事务C输出核对通过；LUT447391/FF328692/BRAM69/DSP93/URAM3、估计3.715ns。CSR LUT433034/FF321414，其余相同。3.715ns仍超3.65ns有效预算，不能称时序闭合。
- `results/collision_safe_bus64_pair_hls_audit_20261030_v3.json`现已通过：collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending，2287绑定，SHA256=68706d296e96c0700a7790d1ec403b5650731075d3d4c6c530de8289c4489cd3。实际独立checker v4 exit0、53.243793502秒，日志/回执/结果SHA核对一致；完整两模式各4份946498280字节快照及trace、实际模式/版本/U280/时钟、完整RTL、30接口与配对相等、各9处动态连接全部检查通过。不是RTL/physical/board通过。
- 保留三次拒绝：旧checker v1按update_3匹配拒绝；checker v2在CLI把自己的新v3报告误判为旧恢复输出（未运行设计审核）；checker v3仅修CSR，实际compact bus64也命名update而被拒绝。逐实际compact九调用列表核后，v4仅扩大到两个已知bus64模式、精确sink_loop_worker/update映射，唯一callee/声明信号/类型等检查不变；CLI只禁止覆盖原v1/v2历史路径且保持输出不存在要求。所有失败日志/回执在恢复v1/v2目录保留，无HLS重跑。
- 当前恢复监督**v3 owner4005048/starttick1654457429**，data/derived/bus64_audit_recovery_supervision_20261030_v3，实际处于mode_0_fresh_setup、child4021698；调用prepare_collision_safe_bus64_cosim_v2.py，先全绑定重读后建新目录，不能将已启动准备误计setup完成。setup仍用v2目录/报告和pair v3 gate；后续四步/模式原链保持。
- 完整RTL监督**v3 owner4029495/starttick1654465267**已启动并实际核身份，data/derived/bus64_full_rtl_supervision_20261030_v3，等待native v2和恢复v3的完整非零验收。旧恢复及完整RTL监督v1/v2均failed并退出，不再活跃；其失败仅前置审核链，不能描述成新RTL运行失败。当前活跃脚本依赖已冻结。
- v27观察已加入两个v3监督。原native目录恢复v2 RTL继续运行、最近0/4，无新增OOM。仍需两个fresh setup/非零输入及完整paired RTL和原其余功能链；原9要求8变体及physical/board缺口保持，完整实验未完成。

## 2026-10-30：compact bus64完整C四事务输出独立复核通过

- `results/collision_safe_bus64_compact_csim_20261030_v1.json`已生成，61文件绑定，SHA256=e0e4d731c5abf97ae522599ceca3e8339dacae0e422c77163def455390be4b04。逐重读41份冻结源码及flow、实际csim.log/csim.exe，四份各946498280字节完整44端口快照和四份trace与原compact CPU参考完全一致。实际日志具备mode1 full44四事务、SEARCH_BATCH_PASS、CSim零错误和唯一C完成标记。
- 本结果仅compact C阶段通过，不等于compact综合、pair审核或RTL通过。原CSR C和单模式HLS结果保持；当前pair completed_modes=[0]，compact HLS实际仍运行。native目录恢复v2 RTL仍实际运行、最近0/4；后续两个接续监督正常等前置，无重复启动。
- 完整pair HLS独立审核仍由版本化恢复监督处理CSR helper名称差异；之后fresh setup/非零输入/完整paired RTL均须逐门验收。原9要求8变体和physical/board缺口保持，完整实验未完成。

## 2026-10-30：完整bus64 CSR→compact RTL监督已实际启动

- 新增并后台启动`supervise_bus64_full_rtl_v1.py`，owner3709622/starttick1654364472，位置`data/derived/bus64_full_rtl_supervision_20261030_v1`。已实读/proc及两前置owner核对，11个执行/审核依赖SHA重读一致；当前waiting_native_and_nonzero_independent_acceptance，无新RTL/编译启动。
- 等native目录恢复v2完整独立验收及新bus64恢复链两个模式非零输入独立验收，要求前置监督成功终态且退出、typed报告/退出回执/日志SHA及报告全部绑定重读通过。随后严格CSR完整RTL/原C→独立终审→compact完整RTL/原C→独立终审。输入或native前置失败即保留失败并停，不重启前置、不改旧报告。
- runner/独立checker现已冻结绑定，不直接编辑。外层runner AS192GiB/stack256MiB允许编译子进程192GiB及RTL96GiB既定上限；独立checker AS16GiB/stack64MiB，全部core0。新OOM/reset只停止自有子进程，无raw-free门槛。只执行功能链，不启动physical/board。
- v27只读观察已加入该监督；当前compact HLS及原native RTL实际身份仍匹配，pair completed_modes=[0]、RTL最近0/4，尚无新功能验收。上一条“入口尚未接入监督”已被本条更新。原9要求8变体及其余功能/physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64逐模式完整native RTL运行与独立审核入口已备妥

- 新增`run_collision_safe_bus64_full_rtl_v1.py --mode 0|1`及`check_collision_safe_bus64_full_rtl_v1.py --mode 0|1`，以新pair HLS v3、各模式非零输入独立v2和native目录恢复v2完整验收为前置；compact还必须等待新CSR RTL独立验收。独立输出`collision_safe_bus64_full_rtl_v1/mode_X`，接受报告`collision_safe_bus64_full_rtl_mode_X_audit_20261030_v1.json`。未启动，尚未接入自动监督。
- 复用原native完整流程而不修改DUT/FSM：保留全部目录（包括空rtldatafile）、44指针/30模型/四事务及地址保护，xelab AS192GiB、RTL/原C后检查AS96GiB，stack256MiB/core0。无空闲内存门槛，新OOM/reset停止自有进程；SIGTERM清理自有子进程。四份946498280字节快照须同时匹配各模式fresh C和原CPU参考；独立checker另核完整输入、真实资源/回执、4/4、四条正周期、原C标记及25原始输出。不计physical或board通过。
- AST与两个模式缺前置拒绝通过，未创建trial/接受报告；模式替换检查无遗留compact-only快照/oracle。使用新CSR真实RTL与已核九连接，诊断层级和33个只读get_value探针构造通过；最初测试误写34个，核实际6个顶层+9×3后改为33，运行入口未因此更改。compact尚未生成完整新报告，仍须完成后核其实际层级。
- 当前v27实际进程核对通过：compact HLS处于微架构生成，native v2 RTL最近0/4，新增接续监督等待旧审核终态。未新增OOM。后续仍需新paired完整RTL执行/终审及原其余功能链；原9要求8变体和physical/board缺口保持，完整实验未完成。

## 2026-10-30：新版bus64审核及完整输入接续监督已实际启动

- `supervise_bus64_audit_recovery_v1.py` owner3635444/starttick1654341390已实读/proc核对，位置`data/derived/bus64_audit_recovery_supervision_20261030_v1`。当前waiting_original_audit_terminal，三前置owner均实际匹配。它等待现有两模式完整综合、旧审核及旧setup监督终态退出；仅当旧审核明确因CSR update_3名称匹配失败且无OOM/中止，才保留其日志/回执/状态绑定并进入新版审核。若其他失败则停止，不覆盖旧失败、不重复执行HLS或RTL。
- 新链严格串行：pair checker v2（报告v3）→mode0 fresh setup v2→独立setup检查→非零准备v2→独立非零检查→mode1同四步。四个v2准备/检查入口仅版本化gate、目录及报告路径，原完整44端口/4事务/30模型/guard/oracle检查未变；diff已核。AST及两模式缺前置拒绝测试通过，未生成接受报告。所有新执行脚本现已冻结绑定，不直接修改。
- setup实际HLS仍AS64GiB/stack64MiB/core0，审核和非零准备AS16GiB/stack64MiB/core0；无空闲内存启动门槛，新OOM/reset仅停止自有子进程。此监督只到两模式非零输入独立通过，不启动编译/RTL或physical；后续仍需新完整paired RTL链。
- 当前只读入口`python3 scripts/experiment_status_v27.py`，区分旧等待及新恢复监督。compact HLS、native v2 RTL实际进程继续运行；pair completed_modes=[0]、RTL最近0/4，无新增功能验收。原9要求8变体及physical/board缺口保持，完整实验未完成。

## 2026-10-30：CSR bus64综合完成、九连接单模式复核通过；compact已实际运行

- pair execution v2已completed_modes=[0]并进入mode1。CSR receipt exit0、1181.795318秒，无新增OOM；原四事务完整C证据逐SHA重新读取通过。`results/collision_safe_bus64_CSR_hls_stage_20261030_v1.json`为单模式检查，661绑定，SHA256=14609a9baede07a246777edafa80df18ffa18088ccdb463d74ccd37456ace1c2。全部9处均连接声明信号，30接口宽度通过；LUT433034、FF321414、BRAM69、DSP93、URAM3、估计3.715ns，仍超3.65ns有效预算，不是布局布线时序结论。
- 本次单模式检查首次按旧映射拒绝：CSR sink_loop_worker的旧update_3实际被HLS生成为update。核全部调用列表后，仅对mode0/该parent/该module精确映射，仍保持唯一callee、端口类型、声明信号等严格检查，随后完整检查通过。新增`check_collision_safe_bus64_pair_v2.py`，默认独立报告v3，AST及未完整pair拒绝检查通过；尚未执行最终pair审核。
- **后续必须处理此已知审核入口差异**：现有acceptance监督绑定旧checker v1，预计会因上述CSR名称匹配拒绝，不能改冻结脚本或伪造其成功。需保留旧失败证据，在两模式完成后用v2独立审核并以新版本监督/新gate接续fresh setup链；当前setup监督仍等待旧gate，不能宣称整条链已可自动完成。现有新准备器和checker本身仍有效但其gate/监督需版本化接续。
- 实读compact实际HLS3525089/starttick1654307009与argv匹配，AS64GiB/stack64MiB/core0。原native v2 RTL仍运行，最近0/4；不计功能通过。新非零准备及独立checker尚未实际运行。原9要求8变体、完整RTL与physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64非零输入独立审核器已完成

- 新增 `scripts/check_collision_safe_bus64_nonzero_v1.py --mode 0|1`，要求对应fresh setup独立gate，逐完整重读输入；以对应bus64分配表核44指针四事务原地址及+4096可逆帧、30模型原只读guard/重定位全信号参数结构、原地址guard编译单元、其余DUT/ROM/原C后检查文件不变，并核有限编译/运行配置。额外明确要求空tv/rtldatafile目录保留。
- AST和两个模式缺preparation拒绝检查通过，未生成接受报告。目标报告为 `results/collision_safe_bus64_nonzero_mode_0_audit_20261030_v1.json`及mode_1。此入口和对应准备器尚未运行真实新输入，也未接入自动启动，不计RTL通过。
- 当前v26实际核对原native v2 RTL与mode0 HLS持续运行，尚无新完整事务/综合验收。后续需在两个fresh setup独立通过后串行执行非零准备及本checker，再构造新的完整paired RTL链；不得沿用旧DUT证明。原9要求8变体及physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64非零指针准备入口及布局前检完成

- 新增 `prepare_collision_safe_bus64_nonzero_v1.py --mode 0|1`，必须各模式fresh setup独立审核后才能执行。按真实wrapper/模型重新解析全部44指针30bundle，严格对照对应模式既有bus64完整布局，保留原只读guard原文、已审核地址guard、44×4指针+4096、30模型地址适配和原完整输入，不改DUT/ROM。不执行编译/仿真。
- 确认既有已审核bus64 CSR/compact布局一致，但与native有5组可写区填充/偏移不同；只读范围逐项相同。新准备器不能直接套native布局，仍须新fresh实际分配完全匹配后才复用guard。以两套真实历史wrapper/30模型验证解析器均与原独立allocation报告一致；两个缺fresh gate拒绝检查通过，未创建输出。
- `results/collision_safe_bus64_layout_preflight_20261030_v1.json` SHA256=1d68400e74a761874509d0eda30c4dd0ad169313907e2157c0a103449bcb5f4e，仅历史布局/解析前检，不是新setup或RTL通过。新入口还需对应独立准备审核器，尚未接入自动执行；当前已运行的setup链及其冻结脚本未修改。
- 原native v2 RTL与CSR HLS仍在运行，当前无新增验收；原9要求8变体、完整功能链及physical/board缺口保持，完整实验未完成。

## 2026-10-30：新配对完整setup及独立检查自动监督已实际启动

- 新增并独立后台启动 `supervise_bus64_fresh_setup_v1.py`，owner3270558/starttick1654227849，位置 `data/derived/bus64_fresh_setup_supervision_20261030_v1`，日志owner_loss目录bus64_setup_supervisor.log。实读/proc及前置acceptance监督身份通过，当前waiting_independent_paired_HLS_acceptance。
- 仅等pair HLS分支明确accepted及独立报告/退出回执/完整绑定通过；原native v1失败分支不会被冒充成功。之后严格串行mode0 fresh full44 setup→独立审核→mode1 fresh full44 setup→独立审核，只生成仿真输入，不启动新RTL/physical。准备器内部HLS AS64GiB，审核器AS16GiB，均有限stack/core0；监督新OOM/reset只停止自有子进程。
- 两个setup脚本及依赖现已绑定，不直接编辑。已实读此前实际2022.2 native fresh setup hls.app确认绝对DUT/TB路径及模式宏格式与新checker匹配。当前两个新setup目录/接受报告均尚未生成。
- 原RTL v2与CSR HLS实际进程仍运行，0/4与pair completed_modes=[]保持，未新增OOM。当前只读入口v26；新setup监督可另查上述state/observation及实际/proc。原9要求8变体、全部功能链/physical/board缺口保持，完整实验未完成。

## 2026-10-30：新CSR bus64完整C输出独立比对通过，当前观察入口v26

- `results/collision_safe_bus64_CSR_csim_20261030_v1.json`已生成，61绑定，SHA256=ee6f5c947441f051066676e7b10bd0f94e147be794ea60f8221f9ee084582ad9。逐核mode0冻结41源码和flow、真实csim.log/可执行程序、4份各946498280字节完整44端口快照及4份精确trace与原CPU参考SHA一致。仅CSR C阶段通过，HLS综合仍运行，pair completed_modes=[]，不能计为CSR综合/配对验收。
- 新只读入口 `python3 scripts/experiment_status_v26.py`已显示实际目录恢复v2监督及RTL、pair v2和pair验收监督。当前RTL kernel3191525/starttick1654203702与HLS3140499/starttick1654186350实际argv/starttick核对通过，原RTL最新0/4 @128000，未新增OOM。旧v1 time0目录失败保持；新v2不计完成。
- 下一步继续CSR综合→完整compact C/HLS→原独立pair审核，以及并行新native四事务/C/独立终审。fresh bus64 setup准备与checker已备妥但未运行。原9要求8变体、完整功能链/physical/board缺口保持，完整实验未完成。

## 2026-10-30 最新实质进展：原编译独立通过；目录恢复v2 RTL已实际运行；CSR新HLS已启动

- 原xelab2268851及time2268817已退出，真实日志Built snapshot且Exit status0，elapsed50:07.16、peakRSS158304028KiB。log SHA256=d970879a12193edf1f08c71390f823adcf0a99d9e69a7039bcedbda275dbe72b，xsimk SHA256=7942118bc83202d7c697af7ca1602e1eed430273171eb79e9bbbd7919074d629。observer2684388终态complete，不再活跃。
- `results/collision_safe_native_recovered_compiler_audit_20261030_v1.json`已独立通过，1388绑定，SHA256=25c779be205d5aeb29ba29ed2408d8aaa68bd99f2013058953e6edbb4e4e59b5；原checker实际exit0/27.334秒。此为编译恢复验收，不是RTL功能通过。
- 首次owner_recovery_v1在RTL time0失败：文件复制漏掉原空sim/tv/rtldatafile目录，TB无法创建输出，ERROR正确阻止验收，0事务、后检查未执行。该trial、监督2762383及原acceptance中native分支均failed；不能仍称其活跃。`results/recovered_native_output_directory_failure_20261030_v1.json`保留证据，原输入/快照未改。
- 新 `run_recovered_native_rtl_v2.py`保留完整目录树（已对真实源目录独立复制检查），新trial `/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_owner_recovery_v2`，复用同一已审核快照，不重编译。新增并实际启动 `supervise_native_directory_recovery_v2.py` owner3177550，位置data/derived/native_directory_recovery_supervision_20261030_v2，串行完整RTL/C→`check_recovered_native_rtl_v2.py`。runner3177612、实际kernel3191525/starttick1654203702已实读/proc核argv/AS96GiB/stack256MiB/core0；最新0/4 @128000，输出目录存在且已越过原time0错误。完整事务尚未完成。
- bus64 pair v2 owner2846102已进入mode0 csim_csynth，真实HLS3140499/starttick1654186350已核argv/AS64GiB；completed_modes仍[]，尚无CSR综合通过结论。原acceptance监督2876506继续等待pair分支，native旧分支failed保持。
- v25尚未显示目录恢复v2，也不应把旧native v1 failed当成新v2；下一轮优先核新v2 state/actual_limits与上述HLS真实身份。新v2代码/checker已绑定，禁止直接修改。原9要求8变体、全功能与physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64 fresh setup独立审核器已补齐

- 新增 `scripts/check_collision_safe_bus64_cosim_v1.py --mode 0|1`，独立核新pair审核全部绑定、fresh源码与综合克隆、实际HLS模式/命令/有限资源、原四事务44端口C快照、30个准确bundle模型、仿真DUT/ROM和原合成一致；完整绑定sim所有文件，包括原C后检查程序及生成源码。只证明setup，仍要求allocation/RO guard/非零指针与完整RTL。
- AST及两个模式未产生setup时的拒绝测试通过；对应 `results/collision_safe_bus64_cosim_mode_0_audit_20261030_v1.json`、mode_1报告均不存在。准备器和审核器尚未执行真实setup，没有新RTL或功能接受。
- v25实际核原compiler/time、observer、recovery、pair v2、acceptance监督保持；编译日志已推进到batch相关模块，尚无终态。原9要求8变体和physical/board缺口保持，完整实验未完成。

## 2026-10-30：新bus64配对各模式fresh full44 setup入口已备妥

- 新增 `scripts/prepare_collision_safe_bus64_cosim_v1.py --mode 0|1`，只接受 `results/collision_safe_bus64_pair_hls_audit_20261030_v2.json` 新配对独立报告，克隆对应mode已审核HLS project及全部源码；逐核source/SYN RTL/ROM，保留原综合结果而不重综合。新输出 `/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_bus64_cosim_setup_v1/mode_0|mode_1`。
- 完整原C测试四事务及44端口各946498280字节快照与原CPU参考一致，fresh cosim仅-setup，全部30AXI模型与4事务参数/原RTL-ROM相等；后续仍需allocation/RO guard/非零指针/完整RTL。AS64GiB/stack64MiB/core0、新OOM/reset保护与实际HLS进程观察；SIGTERM清理自有子进程。
- AST及两个mode的缺gate拒绝测试通过，均未创建新输出目录；没有启动新HLS setup。此入口尚未接入自动监督，待新pair独立通过后逐模式执行及独立审核，不从旧DUT结果继承通过。
- 当前v25全部活跃恢复进程身份核对通过，原xelab仍实际运行，恢复RTL未启动，pair v2仍空completed_modes；无新增OOM。原9要求8变体、全功能链及physical/board缺口保持，完整实验未完成。

## 2026-10-30：两项恢复结果的独立终审监督已启动，当前观察入口v25

- 新增 `supervise_recovery_acceptance_v1.py`并独立后台启动，owner2876506/starttick1654095081，位置 `data/derived/recovery_acceptance_supervision_20261030_v1`，日志在owner_loss证据目录acceptance_supervisor.log。实际/proc及两前置owner身份已核对通过。绑定当前recovery监督2762383和pair v2 owner2846102，分别在其成功终态且owner退出后串行调用对应独立checker；只启动审核、无实验重启/physical启动。一项前置或审核失败则保留failed，继续等待另一项，不伪造两项通过。
- 新恢复RTL与pair checker及相关依赖已冻结绑定，后续不要直接编辑。报告分别为 `collision_safe_recovered_native_rtl_audit_20261030_v1.json` 和 `collision_safe_bus64_pair_hls_audit_20261030_v2.json`，目前均不存在。检查器AS16GiB/stack64MiB/core0并监测新OOM/reset；恢复监督和实际实验资源契约保持。
- 新只读入口 `python3 scripts/experiment_status_v25.py` 显示原compiler observer、recovery监督、新RTL trial、pair v2及独立终审监督，HLS实际phase从job cwd读取。当前compiler/time/observer实核存活，recovery/pair/acceptance均等待依赖，新RTL未启动，pair completed_modes=[]。
- 下一步继续原编译完成后的自动独立审核和完整运行；随后对新pair输出创建完整fresh cosim/非零指针等价验证链，不能转移旧DUT证明。原9要求8变体、完整功能/physical/board缺口保持，完整实验未完成。

## 2026-10-30：新版64位配对执行已实际等待编译独立恢复gate

- 已核旧pair的两个project和hls.log均不存在，旧owner已退出，旧state failed/completed_modes=[]保持。新 `run_collision_safe_bus64_pair_v2.py`以独立后台会话启动，owner2846102/starttick1654084131，state目录 `/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_bus64_pair_execution_v2`，阶段waiting_independent_compiler_recovery_gate且/proc身份实核通过。日志 `data/derived/collision_safe_native_owner_loss_20261030_v1/bus64_v2.log`。
- v2沿用原未执行的mode_0/mode_1输入和cwd，只写新的执行计划/state/资源回执；旧失败state不改。等待recovery监督完整写入compiler独立审核成功回执及completed标志后，逐hash复核gate再串行执行CSR→compact。实际HLS执行及完整快照/trace检查循环与v1逐文本核对完全相同，AS64GiB/stack64MiB/core0和新增OOM/reset策略保持。当前尚无新综合启动，禁止再启动pair副本。
- 未绑定的配对checker新增 `--execution-root`、`--output`，新root必须用独立报告，并审核compiler_gate及完整原编译证据。当前v2未完成态拒绝检查通过。最终调用：`python3 scripts/check_collision_safe_bus64_pair_v1.py --execution-root /tmp/A_graph_compression_recovery_20261025_v1/collision_safe_bus64_pair_execution_v2 --output results/collision_safe_bus64_pair_hls_audit_20261030_v2.json`。未执行终态审核、未生成通过报告。
- 原observer2684388和recovery监督2762383仍实际存活等待原compiler；v24还不显示pair v2，需结合新root/state及/proc。新恢复RTL独立终审checker已备妥但尚未自动调用。原9要求8变体、全功能链及physical/board缺口保持，完整实验未完成。

## 2026-10-30：恢复RTL独立终审已补齐，原编译仍实际运行

- 新增 `scripts/check_recovered_native_rtl_v1.py`，最终接受报告 `results/collision_safe_recovered_native_rtl_audit_20261030_v1.json`。要求新恢复trial完整终态、编译恢复独立证明、原完整仿真copy集合与293输入+xsimk、两阶段实际命令/限额/回执和无新增OOM、原4事务正周期、C后检查、四份946498280字节输出与fresh HLS及原CPU一致、完整25 raw输出。逐hash重读所有复制文件及原证据，不把编译通过当RTL通过。
- AST和缺trial拒绝测试通过，未生成接受报告。新recovery trial尚未启动；原observer2684388、recovery监督2762383与compiler2268851实际存活，完整starttick匹配；无新增OOM。当前只读入口v24保持（另查恢复监督状态）。
- 下一步待原编译完成，现有恢复监督自动compiler独立审核→新完整RTL/C。终审checker尚未接入自动监督，待恢复trial完整后运行或增加只审核的监督；不修改已绑定运行中的checker/runner。旧driver143和旧两监督failed保持，不原地重启。后续新版bus64配对与全部9要求8变体、physical/board缺口保持，完整实验未完成。

## 2026-10-30：新完整RTL恢复链已启动等待原编译，不重复编译

- 新增 `run_recovered_native_rtl_v1.py`：必须先有独立surviving-compiler审核，缺gate拒绝且不创建trial（已实测）；完整仿真目录复制到 `/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_owner_recovery_v1`，逐SHA核原293输入及compiled xsimk。原目录与中断证据保持不动；原Tcl/四事务/C后检查/四份946498280字节输出与fresh及原CPU双参考要求保持，运行AS96GiB/stack256MiB/core0及新增OOM/reset停止。终态只到新独立终审待做。当前新trial尚未创建。
- 新增并以独立后台会话启动 `supervise_native_owner_recovery_v1.py`，owner2762383/starttick1654055376，实际/proc核对存活，阶段waiting_surviving_compiler_observer。位置 `data/derived/native_owner_recovery_supervision_20261030_v1`，日志 `data/derived/collision_safe_native_owner_loss_20261030_v1/recovery_supervisor.log`。绑定observer2684388，待原compiler终态→新编译独立checker→新完整RTL/C，只有这一条恢复链；不要另跑checker/runner。新增runner/监督均处理SIGTERM并清理自有子进程。
- 原observer、compiler、time仍由v24核实；旧driver和旧两监督的143/failed事实保持。v24尚未显示新恢复监督，须另读其state/observation和实际/proc。下一步补齐新恢复trial独立终审checker；旧nativechecker不能直接套用缺失旧wait回执的trial。
- 新恢复runner与compiler checker已经绑定，后续不直接编辑。bus64配对旧入口仍failed未启动综合，之后需独立恢复版本。CPU图表证明保持，原9要求8变体与physical/board缺口保持，完整实验未完成。

## 2026-10-30：存活编译独立恢复审核入口已完成，观察入口v24

- 新增 `scripts/check_orphaned_native_compiler_v1.py`，要求原observer终态、compiler/time均已退出、原time真实exit0与唯一Built snapshot标志、实际命令及AS192GiB/stack256MiB/core0、完整原输入/293项实际副本与生成snapshot绑定、无新增OOM/reset、中断证据保持。不伪造旧wait回执，不接受RTL功能；接受报告 `results/collision_safe_native_recovered_compiler_audit_20261030_v1.json` 当前不存在。
- 已用实际timer/compiler argv校验命令匹配，并核对293项copied集合与原准备审核完全一致；AST与当前未终态拒绝检查通过。尚未执行终态完整审核。
- 当前observer2684388、compiler2268851、time2268817均实际存活且starttick/argv匹配，仍observing_existing_compiler，无终态证据。`python3 scripts/experiment_status_v24.py`同时展示旧驱动缺失/旧两监督failed和新observer活跃，避免把旧state running误读为驱动存活。
- 下一步编写新的完整RTL恢复入口：待本checker独立通过后，保留原编译和中断证据，执行原4事务、原C后检查及完整44端口快照；不能把编译恢复当功能验收。随后以新版入口恢复配对HLS链，旧failed入口不原地重启。原9要求8变体与physical/board缺口保持，完整实验未完成。

## 2026-10-30 最新中断：原驱动exit143，但原编译存活，已接管只读终态监测

- 原native工具句柄40140实返exit143；owner2262903已不存在。原trial state仍running/elaborate是遗留，不再代表驱动存活。原因未确定，不能从143推断发送者；oom=0/oom_kill=2未增加。原xelab2268851/starttick1653877328及time2268817/starttick1653877302仍实际存活，原argv/cwd/AS192GiB/stack256MiB/core0核对通过；没有编译终态回执，不重复启动编译。
- 下游native独立终审监督2455436/句柄82035与bus64配对owner2491979/句柄19124均实际exit1，分别因原owner缺失而停止，state已failed。没有启动新bus64 HLS。不能继续引用它们为活跃等待，也不原地重启旧入口。
- 中断证据 `results/collision_safe_native_owner_loss_20261030_v1.json` SHA256=32cc2528ea0e62d560179ccfa144fd262de82f33c814bcf0a34d798b9b69dcf5；复制了原state/plan/actual_limits/resource及两监督状态与日志前缀，原文件未改。
- 新增 `observe_orphaned_native_compiler_v1.py`，独立会话后台observer 2684388/starttick1654026811，位置 `data/derived/collision_safe_native_compiler_observation_20261030_v1`。实际核对observer、compiler、time均存活。只观察原编译并维持原新增OOM/reset停止保护，不启动RTL或重复编译；原日志由time最终提供真实Exit status和Built snapshot证据，另写terminal.json而不伪造旧wait回执。当前仍observing_existing_compiler。
- 下一步：先核observer/原compiler/time身份，等原编译终态后独立审核实际time footer、生成snapshot和所有原输入绑定；以新恢复入口保留原始中断证据，继续完整4事务RTL/C/输出核对。原native终审和bus64runner旧绑定不能伪造成功或改写；后续需新版本恢复链。当前v23会正确显示旧驱动缺失及两项failed，但还不含新observer。
- CPU补充图表验收保持；原9要求8变体及physical/board缺口保持，完整实验未完成。

## 2026-10-30：CPU六排列补充图表已完成并独立复核

- 新增 `scripts/plot_training_order_control_v1.py`，结果 `results/figures/training_order_control_20261030_v1/report.html`，同目录包含完整18行workers.csv、12行paired_ratios.csv、6行execution_order.csv、analysis.json、两张PNG/SVG/PDF、requirements及manifest。与原7组分别报告、不混池；不作为FPGA性能或完整实验完成依据。
- 生成前重读原308项绑定约27.4GB，并用原六组检查器的summarize重新计算，结果与已接受报告完全一致。初次误用七组summarize被完整性检查拒绝且未创建图表目录，改用六组既有检查器后成功，未更改任何原实验数据或审核条件。
- 两张PNG已目视检查；另行逐重读324绑定、重算全部CSV应用值/12个配对比及顺序通过。`results/training_order_control_figures_integrity_20261030_v1.json` SHA256=7ff2ae7029afbe6dc22a684b796d3545d668eb8867d64f2b2cd34580df7a1ec3。manifest SHA256=a90cbab4a6ac9177428807d9fa50eb6fdc3fc69e02ca5779289f5a4ddcae354f。配对耗时中位数direct/CSR=1.433615684125、expanded/CSR=0.902898399248，仅共享主机14站点完整CPU应用观察。
- 当前native原生编译仍elaborate，PID/starttick/argv核对通过；两个监督仍等待现有编译/原生终态。最新oom=0/oom_kill=2未增加；max计数增加不等于OOM，不据此恢复用户取消的空闲内存门槛。只读入口仍v23，句柄40140/82035/19124保持。
- 下一步继续当前编译、完整RTL/C及独立终审，之后新bus64配对与后续全链。原9要求8变体、physical/board等缺口保持，完整实验未完成。

## 2026-10-30：配对审核工具格式补核，当前只读入口v23

- 当前三项实际进程均存活且脚本身份核对通过：native仍elaborate（phase PID/starttick/argv核对通过），native独立审核监督等待原任务终态，bus64配对执行器等待原编译成功退出。没有空闲内存门槛等待，没有新增综合/物理/上板启动。入口 `python3 scripts/experiment_status_v23.py`，新增明确waiting_dependency标签；旧v22及其冻结依赖未修改。
- 已实读旧CSR/compact完整HLS XML确认顶层端口字典完全相同；原native数据宽度有32/64/128/256/512，配对审核要求min(width,64)。旧实测2022.2 HLS进程argv确认实际二进制vitis_hls及-f格式，fresh hls.app两项source/testbench的模式宏检查适用。
- 未绑定执行中的配对独立checker补充了实际HLS程序/flow匹配、两项项目文件集合、唯一模式宏、完整资源字段及原9处碰撞证据重读检查。AST/未完成态拒绝/真实2022.2项目flags检查通过，未产生新功能接受报告。该checker尚无监督自动调用，待两模式完成后执行 `python3 scripts/check_collision_safe_bus64_pair_v1.py`。不要编辑已有native终审或配对runner的冻结输入。
- 完整9要求8变体及功能链/physical/board缺口保持，完整实验未完成。新任务仍使用原句柄40140、82035、19124，不重复启动。

## 2026-10-30：64位配对串行执行器已实际等待当前原生编译

- `run_collision_safe_bus64_pair_v1.py`已启动，工具句柄19124，owner2491979/starttick1653956133，当前阶段waiting_existing_native_compiler。实际/proc身份核对通过；新HLS尚未启动。绑定当前native编译实际身份及回执，待其成功退出后串行CSR→compact完整C仿真+综合；不是等待空闲内存门槛。各HLS AS64GiB/stack64MiB/core0，实际新OOM/reset仅停止自有进程。
- 执行器要求每模式完整4份946498280字节快照、4份精确trace与原CPU参考一致，记录实际HLS二进制身份和限制。终态仍为独立审核待做，不自动计RTL/physical通过。原生任务40140及其独立终审监督82035不重复启动。
- 新增 `check_collision_safe_bus64_pair_v1.py`：完整双模式C输出、同约束、30接口实现min(native_width,64)、两种模式各9处动态连接、无命名冲突和完整生成物绑定。注意64是上限，原有32位接口保留，不能强制全部64。AST与未完成态拒绝测试通过，接受报告未生成；尚未对实际新综合输出验收。完成后运行此checker，若结构差异须查看真实输出再判断，不降低功能条件。
- 下一轮先核上述活跃身份与native阶段，继续新配对审核/全RTL链；原完整9要求8变体和physical/board缺口保持，完整实验未完成。

## 2026-10-30：64位配对输入已独立核对；原生终审监督已实际启动

- `prepare_collision_safe_bus64_pair_v1.py`已完成：`/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_bus64_pair_v1`的CSR/compact各41份源码逐字节等于新命名修复candidate，仅GRAPH_MODE不同；同part/5ns/1.35ns、max_widen64、完整44端口四事务C测试。没有启动任何新HLS工程。
- preparation报告SHA256=1a5b1b26a853dbf68fbdf2a83eed6f4bc3d8a6c27274b9941598a46bff2f3a15。另行核对82源码、两个Tcl及准备报告85绑定通过，`results/collision_safe_bus64_pair_preparation_integrity_20261030_v1.json` SHA256=ad53df0157f72e870ee961d022360b8f4d2604136e6fbce7e1758ec91d1f3e15。此为输入审核，不是综合/RTL通过。下一步编写串行执行器，保留AS64GiB/stack64MiB/core0与新增OOM停止策略，不加空闲内存门槛。
- 新增并实际启动 `supervise_collision_safe_native_audit_v1.py`，句柄82035，owner 2455436/starttick1653943442。只观察既有原生owner，成功终态且owner退出后运行已冻结独立终审；失败即停止，不重启，不发布physical/board结果。位置 `data/derived/collision_safe_native_audit_supervision_20261030_v1`；下次先核实际身份，禁止重复启动审核。
- 原生编译句柄40140仍运行，v22逐/proc身份核对通过，最新编译至search模块。原完整9要求8变体及其余功能/physical/board缺口保持；完整实验未完成。

## 2026-10-30：新原生RTL独立终审程序已补齐，编译仍运行

- 新增 `scripts/check_collision_safe_native_rtl_v1.py`，终审要求新输入/HLS/setup全部绑定、实际三阶段命令与有限资源回执、四事务正周期、原C后检查、四份946498280字节输出与fresh HLS及原CPU参考一致、完整25项raw输出。接受报告为 `results/collision_safe_native_rtl_audit_20261030_v1.json`，当前未生成。
- AST与实际运行态拒绝检查通过：编译未结束时明确拒绝验收且不写报告。尚未执行终态完整审核；不能称功能通过。
- 原native owner及xelab仍由v22核实，阶段elaborate，日志继续编译DUT模块。保留工具句柄40140，不重复启动。原runner自动继续RTL及C后检查；终态complete后再运行新独立终审程序，失败则保留证据诊断。
- 完整实验仍未完成；新bus64配对、完整功能链、physical/board缺口保持。

## 2026-10-30 最新：新HLS九连接独立通过；fresh full44输入通过；新原生RTL编译已实际启动

- 原综合句柄86024现已exit0，owner1720140不再作为活跃综合引用；新HLS独立报告results/collision_safe_compact_hls_audit_20261030_v1.json已生成，342绑定，SHA256=39299dfb2087ad85b9d956bcb36d680583275ad1df6a0e3916650fc3eaa254b8。全部9个原roots_x/query_x/net_x接零端口现恢复为动态信号，原生完整接口/2022.2/U280/5ns/1.35ns保持。roots两处均为root_nodes；query分别or_ln_reg_59929/q_3_reg_2227；net为trunc_ln52_1_reg_59951或net_reg_6479。无命名冲突警告。这是HLS/C/结构通过，仍不是RTL功能通过。
- 新native默认宽度HLS资源估计LUT1939430/FF731277/BRAM18K69/DSP93/URAM3、周期4.509ns；原native为LUT1937259/FF731186、同4.509ns。器件LUT可用1303680，原生默认宽度已有超容量估计，不能称物理可用或时序收敛；它仍承担原生功能验证。后续仍须基于仅改名源码重建64位CSR/compact配对，不得把旧bus64综合/RTL/物理证明自动转移到新DUT。
- 原setup监督1932194/句柄10049已exit0 complete；fresh setup /tmp/A_graph_compression_recovery_20261025_v1/collision_safe_compact_cosim_setup_v1完整结束，4次HLS C与四份946498280字节参考快照相等，syn RTL/ROM克隆保持。setup.json为collision_safe_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending，1012绑定，SHA256=71cfe9b0dd2ec1901f8c5f8db5dd5bf8dcc3a79884e1c20ea287f0e9e8eeb16d。该步骤仅生成仿真模型/输入，不是RTL已经运行。
- 新脚本prepare_collision_safe_native_rtl_v1.py已完成新输入准备；新wrapper全部44区间/30bundle与原完整分配相同，沿用原RO guard文本/原地址guard，44指针每4事务加4096、30模型地址减4096，DUT/ROM及其余全部输入未改。/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_rtl_preparation_v1/preparation.json：600绑定，SHA256=527b5388baa67d597b6f0031ec554985591dd6a0cfd8dc601c78a491544402e3。独立checker另核全部文件、完整集合、30wrapper所有信号/参数、44向量及编译命令；results/collision_safe_native_preparation_audit_20261030_v1.json为collision_safe_native_full44_inputs_all30_guards_all44_relocations_independently_verified，602绑定，SHA256=76e0ebd9f8a39b60b31b31470f5d9af4afb7bc392f1af6ece9d1d2b250b34337。
- 新唯一原生执行owner脚本scripts/run_collision_safe_native_rtl_v1.py已实际运行，工具句柄40140，trial /tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_rtl_v1。当前stage=elaborate，owner2262903/starttick1653875026；time child2268817，实际xelab2268851/starttick1653877328已实读/proc匹配、AS192GiB/stack256MiB/core0。下一轮重新核当前phase与身份，不沿用旧RTL2005478或诊断capture的已停止PID。没有rawfree门槛；OOM=0/oom_kill=2未增加，保留新OOM/reset自有进程停止。当前只是编译，不计任何RTL事务通过。
- 原生driver编译成功后自动顺序运行完整4tx XSim（AS96GiB/stack256MiB/core0），再执行新setup原cosim.pc.exe C后检查，并逐完整四份快照校验；任一步失败停止。bound Tcl在run返回后读取顶层input_mem地址/握手和9处恢复连接及ap_start/ap_done，提供数值诊断；不依赖未启用debug的VCD，不force或削弱guard。结束状态仍为independent_final_rtl_audit_pending，必须再独立验收；新最终RTL独立checker/报告仍待完成，不放行旧下游typed入口。
- 只读入口scripts/experiment_status_v22.py。后续优先监测句柄40140和实际/proc、完善新完整RTL独立验收/新CSR-compact64位配对准备；不能修改活跃driver/绑定输入。原CPU顺序18/18、6/6保持，旧native/paired/tree/snapshot-read失败链未重启。原9要求/8变体、完整RTL链、物理实现、板卡和真实端到端缺口保持，完整实验未完成。

## 2026-10-30 最新：新compact综合继续；9连接独立审核与fresh full44 setup自动接续已实际启动

- 上轮为实质进展：受控复现HLS命名冲突、仅改名副本两模式8份完整C快照通过并启动新HLS；本轮未重新提交该综合。当前实际vitis_hls1728527/starttick1653688436与原owner1720140保持，已从绑定/调度进入RTL生成；尚无综合终态和独立验收，不能提前宣告9连接修复已在完整RTL通过。
- 新本地单owner监督scripts/supervise_collision_safe_compact_setup_v1.py已运行，工具句柄10049，owner1932194/starttick1653755072，data/derived/collision_safe_compact_setup_supervision_20261030_v1/state.json当前waiting_current_collision_safe_hls_terminal。它绑定当前HLS owner的PID/starttick/argv，等待成功终态和owner退出后，依次调用check_collision_safe_batch_hls_v1.py、prepare_collision_safe_compact_cosim_v1.py；任何失败即停止，不重启旧实验。被绑定脚本不可运行中修改。
- 独立HLS checker要求新终态、实际exit0/无OOM回执、原约束与全部原生接口相同、6文件逆改名还原、完整8份CPU证据、所有9个旧冲突端口对应到真实非常量信号、旧roots_x/query_x/net_x连接和命名冲突警告均不存在。输出目标results/collision_safe_compact_hls_audit_20261030_v1.json；当前尚未执行该审核。其解析器已用原9个错误连接和3组实际最小HLS对照验证：results/collision_safe_hls_checker_parser_validation_20261030_v1.json；该报告仅解析器验证，不是新完整综合通过。
- fresh setup入口将克隆已验收HLS项目，保持syn RTL/ROM逐文件SHA一致，使用原完整44端口/4事务testbench执行csim及cosim -setup，并将4份完整946498280字节HLS C快照与仅改名副本参考逐SHA核对。使用AS64GiB/stack64MiB/core0，无rawfree门槛，保留新OOM/reset自有进程停止。目标/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_compact_cosim_setup_v1当前尚未创建。此入口不运行xelab/xsim、不放行physical；完成后仍需新生成wrapper allocation审核、RO guards、44指针非零重定位/30模型映射、新原生RTL及原postcheck完整输出、新CSR/compact配对等全链。
- 只读入口更新为scripts/experiment_status_v21.py。下轮先核原综合句柄86024与监督10049、实际/proc身份和终态文件；不要另启checker或setup。旧native/paired/tree/snapshot-read失败链及capture v1/v2停止事实不变。完整9要求/8变体、RTL/physical/board/真实端到端缺口保持，完整实验未完成。

## 2026-10-30 最新：复现HLS命名冲突错误；独立改名副本8份完整C输出一致，新compact综合运行

- 原失败RTL进一步发现9处冲突端口接零：2个roots_x、2个query_x、5个net_x。原HLS调度报告中的调用仍传root_nodes_read，但生成RTL的roots_x接64'd0；原autopilot.flow.log有对应RTGEN206-101命名冲突警告。清单results/hls_collided_port_inventory_20261030_v1.json，SHA256=677ba87934af14ab8aee445a00df9b3cadb1bdcb177e37be3f96e822f6c617ac。不要仅修roots而漏掉query/net。
- 小型2022.2受控综合实验已实际完成三组：同名roots函数/参数→roots_x接64'd0；只改参数名或只改函数名→动态root_nodes_read_reg_163。三组各68个C参考用例通过，52文件绑定已另行重读；results/hls_root_name_reproducer_20261030_v1.json SHA256=74de43fa9a2b1e8565bb1d88376a6c8b54a1f77970eb2f990cd0c8d3d6df2bd2。两条原roots地址算术cone+原完整AXI adapter+原guard的XSim诊断12正例、2个零地址负例也通过，results/trace_root_address_diagnostic_20261030_v1.json SHA256=5f1ed145ec528d54f7a7b31a132b8b98187c21c9b2c303a30911fdb8a79c65bd。后者没有原FSM可达性证明；原全量失败请求的精确调用者仍未记录，不将诊断当作完整RTL验收。
- 新独立副本/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_batch_hls_v1/source，仅将三个辅助函数及调用点改名：roots→a_collect_tree_roots、query→a_validate_snapshot_query、net→a_write_net_trace_record，共6文件，逐源逆替换还原完全一致；全部pragma、深度、算法、原testbench/oracle保持，冻结硬件源码与旧RTL未修改。两种模式各4次完整44端口C运行通过，8份每份946498280字节快照SHA与原CPU参考完全一致。results/collision_safe_batch_full44_cpu_20261030_v1.json SHA256=05e5d4593d42d63701a5231994dc51f11ecb229d723d4b73088a378d41eb2258；另行重读112绑定，results/collision_safe_batch_cpu_integrity_20261030_v1.json SHA256=bf2f36c207892a9c8f3a87a2ea452c001413b3a4ac2426954e23ec4b4a297916。新报告仅C验收，不能替代原全RTL。
- 当前仅新compact native默认宽度HLS综合运行：scripts/run_collision_safe_batch_hls_v1.py，工具句柄86024；owner1720140/starttick1653685572，shell1728492，实际vitis_hls1728527/starttick1653688436，AS64GiB/stack64MiB/core0已从/proc实读（Python调度父进程自身未施加AS）；没有rawfree门槛，实际新OOM/reset才停止自有进程。U280原part/5ns/1.35ns/禁止自动pipeline_loops保持。下轮先重新核实际身份和state/hls.log；原driver不会启动RTL或physical。若综合完成须独立核原9个连接恢复动态值、所有命名冲突警告、资源/接口/完整manifest，再准备新完整4事务nonzero/native RTL与后续CSR/compact配对的新版本。旧typed前置不得直接改为通过。
- 隔离capture v1/v2都已停止且无新完整RTL结果：v1实际可读31个信号，但检查器误匹配Tcl回显中的MISSING_PROBE而停在preflight；v2已通过46信号preflight，短跑后因另行验证原快照没有-debug、open_vcd会报Simulator45-10而由已核身份的自有owner收SIGINT关闭（1590038/1594570/1596516均已不存在）。v2/diagnostic_stop_reason.json保存原因；原快照get_value可用但VCD不可用。所有旧证据保留，不重启这两个失败入口。受控综合已复现并提供仅改名候选，因此没有启动第三次原快照长复现。
- 当前只读入口scripts/experiment_status_v20.py；旧v19及绑定文件保持。CPU顺序补充18/18、6/6最终独立通过的事实保持；原native/paired/tree/snapshot-read链全为failed，当前没有活跃下游队列、RTL或physical。新综合仍非验收，完整9要求/8变体、全RTL/physical/board/真实端到端等缺口保持，完整实验未完成。

## 2026-10-30 最新：CPU六排列18项最终独立通过；原nonzero RTL地址检查失败，串行链已关闭

- CPU原监督与driver均已结束，state=complete、18/18 worker、6/6原独立组；最终results/training_order_control_audit_20261029_v1.json为all_six_order_permutations_18_complete_training_inclusive_workers_independently_audited，SHA256=56b8e9d510dd3104d3feb7e9f9349bb96daf72debec183c8033d7e6d2bb7ec0e。另行逐文件重读最终与全部6组共308绑定、完整集合/18项summary/两批1062网/3761→440训练/原输入/六排列顺序与非重叠回执、最终统计重算一致：results/training_order_control_integrity_20261030_v1.json，SHA256=e4ad8f6482b02bf26bbc3bdbd652e218ac29589c01800aad661f277f2f766521。补充配对应用耗时中位比compact/direct÷CSR=1.433615684125，compact/expanded÷CSR=0.902898399248；与原7组不混池，共享主机/cache/14实例范围、不含Vivado采集/板卡传输/物理回读限制保持。
- 原native nonzero v2现已终态failed，不再live：rtl.log在31812257500ps触发Fatal: A_REBASE_BELOW_BASE input_mem write=0；最后事务日志0/4。xsim进程exit0但功能失败，elapsed52516.222409748秒、resource_abort=false，无新增OOM，原C postcheck未执行、独立accepted报告不存在。不能按内存问题重跑或把exit0当通过。日志未记录数值地址，只证明已知请求address<BASE；尚未定位产生该请求的DUT过程，不能预断RTL或wrapper谁有错。
- results/native_nonzero_address_failure_20261030_v1.json冻结19份关键源/日志/state/receipt/guard文件并复制后重读核SHA，报告SHA256=9597b67367a07bb67ea43ffa15ddcef2707e0e1899e75a1b015a47d8384dd054。1121343/1128465/kernel2005478及paired1271339/tree1381048/snapshot-read1879400全部/proc不存在，后3监督均按前置失败终态failed；CSR/compact编码、tree/full30/read新trial均未开始。不得再称这些原owner仍运行或下游live waiting；不得重启旧入口。没有新编译、DUT改动、削弱guard或physical执行。
- 下一步先从实际guard、DUT input_mem AXI地址路径、原pointer重定位/嵌套地址来源定位失败；必要时独立新版本诊断instrumentation，保留完整深度/事务/oracle，不能凭CPU结果放行RTL或physical。当前只读状态仍scripts/experiment_status_v19.py，旧绑定文件不改。全部原9要求8变体及完整RTL/physical/board等缺口保持，完整实验未完成。下方17/18和原RTL2005478 live信息均为历史。

## 2026-10-30：最后一项compact/expanded实际native身份补核

- block_005/worker_001/native.submission.json现已创建：native3725742/starttick1650070623、owner3700155。实际/proc argv与submission一致，expanded模式、CPU121/AS16GiB/core0已实读核实；不是仍未启动native，也不沿用旧3280912。当前仍17/18 worker完成、5/6独立组通过，本项与最终审核未验收。下一轮重新核当前身份；原RTL2005478继续运行、最近0/4、无新增OOM。完整实验未完成。

## 2026-10-30：CPU顺序补充17/18完成，最后一项compact/expanded已启动

- block_005/worker_000 csr/direct通过原worker完整两批各1062网输出校验，native与外层worker均exit0。10项artifact及原CSR参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、CSR不训练、实际argv/CPU121/AS16GiB及顺序[2,0,1]非重叠回执核对一致。报告SHA256=a6d2362890bb0006215390511970d7c190184161c5e3c53ac908cd42a8c72759，outer receipt SHA256=636330201c6b6c8394ac5b417a9540afa11bfa4dbf6259ffd7fd73f4e9e58d6a。application=1212.093933927秒，完整输出审核另耗231.886937024秒，native=1160.976529954秒。
- 当前17/18 worker完成、5/6独立组通过。旧worker3261916/native3280912已退出；原监督2624526/句柄27488与driver2660361自动进入block_005 position2 compact/expanded，worker3700155/starttick1650062493已实读/proc核实际argv/CPU121/AS16GiB/core0。该次核对时native.submission.json尚未创建；下一轮从block_005/worker_001/native.submission.json及实际/proc核native身份与资源，不沿用旧3280912。观察入口仍v19。后续仍须本项完整输出、原整组checker及最终typed独立报告，不提前计18/18或形成完整补充性能结论。
- 原RTL2005478仍运行、最近0/4，未新增OOM。全部六排列18项、原9要求8变体及完整功能链/physical/board缺口保持，完整实验未完成。下方16/18及最后一组CSR活跃状态为历史。

## 2026-10-30：CPU顺序补充16/18完成，最后一组CSR已运行

- block_005/worker_002 compact/direct通过原worker完整两批各1062网输出校验，native与外层worker均exit0。11项artifact及原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、训练先于评估、实际argv/CPU121/AS16GiB及顺序[2,0,1]非重叠回执核对一致。报告SHA256=afc652ddef758e35fe1224718cb59c4cdfc0e2a34d88ac67d696cfff69624e13，outer receipt SHA256=6bba9e659ee783ba80134b09ffdef4e3d29d08a028fcb530776fa72f167060cb。application=1607.568046892秒，完整输出审核另耗234.752785407秒，native=1535.826572703秒。
- 当前16/18 worker完成、5/6独立组通过，最后一组尚未整组验收。旧worker2704166/native2729384已退出；原监督2624526/句柄27488与driver2660361自动进入block_005 position1 csr/direct worker3261916/starttick1649917038、native3280912/starttick1649923111，已实读/proc核实际argv/CPU121/AS16GiB/core0。下一轮重新核这些身份，观察入口仍v19。后续仍须CSR、compact/expanded完整输出、原整组checker及最终typed独立报告，不提前形成完整补充性能结论。
- 原RTL2005478仍运行、最近0/4，未新增OOM。全部六排列18项、原9要求8变体及完整功能链/physical/board缺口保持，完整实验未完成。下方15/18及最后一组compact/direct活跃状态为历史。

## 2026-10-30：CPU顺序补充第五组独立通过，最后一组已启动

- 当前15/18 worker完成、5/6独立组通过。block_004/audit.json为all_source_to_route_integration_trials_audited、3/3，全部43文件SHA另行重读通过；完整artifact集合、三项summary/计时、原输入/限制及顺序[1,2,0]非重叠回执核对一致。audit SHA256=7299a297af4bdc37aea96190a718d9fb680d748728bd11b4bcb8b02b51ddb77d，audit.log SHA256=0c068f295317716f81f6badc89ec221736608cf79b5810cc8e7dc3b6504ced9c。原整组checker2484385已退出，未启动重复审核。
- 原监督2624526/句柄27488与driver2660361自动进入最后block_005，冻结顺序[2,0,1]：compact/direct→CSR/direct→compact/expanded。新plan的files/expected_inputs/jobs与前组相同。首项worker2704166/starttick1649731845、native2729384/starttick1649739872已实读/proc核实际argv/CPU121/AS16GiB/core0。下一轮重新核这些身份，观察入口仍v19；待全部18项、6个完整组及最终typed独立报告通过，不提前形成完整补充性能结论。
- 原RTL2005478仍运行、最近0/4，未新增OOM。原9要求8变体、完整功能链和physical/board等缺口保持，完整实验未完成。下方15/18但4/6及第五组审核活跃信息为历史。

## 2026-10-30：CPU顺序补充15/18完成，第五组独立审核已启动

- block_004/worker_000 csr/direct已完成原worker完整两批各1062网输出校验，native及外层worker均exit0。10项artifact与原CSR参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、CSR不训练、实际argv/CPU121/AS16GiB及顺序[1,2,0]非重叠回执一致。报告SHA256=b53e56171209472c6b6da6b36f0f8614503cbdc40fdc83302a1352739aadb1de；outer receipt SHA256=e8b004489dd4bb8a674532ff22829c3d7b0e5256a15c67cc32bff8864ba70829。application=1110.943278009秒，完整输出审核另耗232.631842364秒，native=1059.604134127秒。
- 当前15/18 worker完成、4/6独立组通过。旧worker2064317/native2083780均退出；原监督2624526/句柄27488与driver2660361自动进入original_full_block_audit，实际checker2484385/starttick1649660225已核完整argv、cwd、CPU121/AS16GiB/core0，无partial参数。原checker源SHA仍c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。block_004/audit.json尚不存在，不提前计第五组通过；下一轮重新核该checker身份和报告，禁止重复启动审核。
- 原RTL2005478仍运行、最近0/4，未新增OOM。全部六排列18项、原9要求8变体及完整功能链/physical/board缺口不变，完整实验未完成。下方14/18及CSR运行状态为历史。

## 2026-10-30 最新：14/18完成，第五组最后一项CSR运行中

- block_004/worker_002 compact/direct完整两批各1062网输出通过，native/外层worker均exit0，11项artifact与原参考SHA另行重读通过，完整语义、原输入/训练/实际资源和串行回执一致。报告SHA256=a49fdc4295184d09836e9c5157964e1a0ede659a9f8a39733a186a40c2f3c9f0，outer receipt SHA256=5d110f3413d4282eddb8f403ae22ebbfef59221c7f311ed5b5cfc9e4a6518f4d。当前14/18 worker完成、4/6独立组通过，第五组未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_004 position2 csr/direct worker2064317/starttick1649524887、native2083780/starttick1649530975已实际核argv/CPU121/AS16GiB/core0；下一轮用v19、`block_004/worker_000/native.submission.json`及实际/proc重新核身份。旧worker1491212/native1516682均已退出，不重启或沿用。
- 等待本项完整输出和原独立组checker，再推进最后一组。全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方13/18及compact/direct活跃信息为历史。

## 2026-10-30 最新：13/18完成，第五组第二项compact/direct运行中

- block_004/worker_001 compact/expanded完整两批各1062网输出通过，native/外层worker均exit0，11项artifact及原参考SHA另行重读通过，完整语义、原输入/训练/实际资源与串行回执一致。报告SHA256=b34493e9a4fb89d7a3b70f0aa6348ef48e3fbcd06ad1534ef431fe89e55d86dd，outer receipt SHA256=4bbc35ad666a85fccb0c1476f65d7129dd72113eb4e7fcacf205a1c4cea24750。当前13/18 worker完成、4/6独立组通过，第五组未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_004 position1 compact/direct worker1491212/starttick1649341000、native1516682/starttick1649349064已实际核argv/CPU121/AS16GiB/core0；下一轮用v19、`block_004/worker_002/native.submission.json`与实际/proc重新核身份。旧worker1064901/native1095112均已退出，不重启或沿用。
- 按第五组顺序[1,2,0]等待compact/direct→CSR及原独立组checker，再推进最后一组。全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方12/18及第五组首项计算活跃状态为历史。

## 2026-10-30 最新：第四组独立通过，第五组首项已启动

- 当前12/18 worker完成、4/6独立组通过。block_003/audit.json为all_source_to_route_integration_trials_audited、3/3，全部43文件SHA另行重读通过，完整绑定/计时/串行回执一致。audit SHA256=90ef25f0f1cc2a8277c59b7bfdd1ff7e30b5c10823cd30ea863fc77102b52eb1；原完整checker未改，第四组checker810147已退出。
- 保持监督2624526/句柄27488与driver2660361。当前block_004顺序[1,2,0]，首项compact/expanded worker1064901/starttick1649216673、native1095112/starttick1649224668已实际核argv/CPU121/AS16GiB/core0，新plan的files/expected_inputs/jobs与前组相同。下一轮用v19、`block_004/worker_001/native.submission.json`与实际/proc重新核身份。等待完整输出后按原顺序执行compact/direct、CSR和原独立组checker。
- 全部六排列18项、原9要求8变体、完整功能链和physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方3/6及第四组checker活跃状态为历史，不从四组提前作完整补充性能结论。

## 2026-10-30 最新：12/18完成，第四组原独立审核运行中

- block_003/worker_001 compact/expanded完整两批各1062网输出通过，native/外层worker均exit0，11项artifact及原参考SHA另行重读通过，完整语义、原输入/训练/实际资源与串行回执一致。报告SHA256=c08b90fb4eeac76d5c232dc387bf275a3c20615d9d9b7f32ed56f1172ef3d88b，outer receipt SHA256=f3b8a7847acdf4320136d4271018d9c9aa20a569eb90fb6df114b86766c4eda1。当前12/18 worker完成、3/6独立组通过，第四组audit.json尚不存在。
- 保持监督2624526/句柄27488与driver2660361，当前stage=original_full_block_audit。原checker810147/starttick1649145036已实际核cwd、完整argv且无--partial、CPU121/AS16GiB/core0和原源码SHA；旧worker370602/native399588均已退出，block_004未建立。下一轮先核v19和该checker实际身份，等待原完整组审核成功后核第五组启动，不另起审核。
- 全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方11/18及compact/expanded计算活跃信息为历史，CPU日志round含义纠正仍有效。

## 2026-10-30 最新：11/18完成，第四组最后一项compact/expanded运行中

- block_003/worker_002 compact/direct完整两批各1062网输出通过，native/外层worker均exit0，11项artifact及原参考SHA另行重读通过，完整语义、原输入/训练/实际资源与串行回执一致。报告SHA256=9d8ac675a2b1798122c49638fed824824274d4e30176664cadb083f99e1a456d，outer receipt SHA256=1624612deaec79163409e7a8ea2e6e5fcaf282464bf085ab63ebf0d6d0ad721a。当前11/18 worker完成、3/6独立组通过，第四组未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_003 position2 compact/expanded worker370602/starttick1649018306、native399588/starttick1649026702已实际核argv/CPU121/AS16GiB/core0；下一轮用v19、`block_003/worker_001/native.submission.json`与实际/proc重新核身份。旧worker3945682/native3974169已退出，不重启或沿用。
- 等待本项完整输出与原独立组checker，再推进后两组。全部六排列18项、原9要求8变体、完整功能链与physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方10/18及compact/direct活跃信息为历史。

## 2026-10-30 最新：10/18完成，第四组第二项compact/direct已启动

- block_003/worker_000 csr/direct完整两批各1062网输出通过，native/外层worker均exit0，10项artifact及原参考SHA另行重读通过，完整语义、原输入/实际资源与串行回执一致。报告SHA256=b62f2a6168c424dbd74ead0136a8097f6199bccf041038dc8349d540f27fdba1，outer receipt SHA256=5217ed4061b46bc41820aa64d6bad7eae1f1f474515d0167aa73835a61f6dd32。当前10/18 worker完成、3/6独立组通过，第四组未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_003 position1 compact/direct worker3945682/starttick1648836422、native3974169/starttick1648844698已实际核argv/CPU121/AS16GiB/core0；下一轮用v19、`block_003/worker_002/native.submission.json`和/proc重新核身份。旧worker3498402/native3518408已退出，不重启或沿用。
- 下一轮先核v19和实际进程，按第四组[0,2,1]继续compact/direct→compact/expanded及原完整独立checker。全部六排列18项、原9要求8变体、完整功能链与physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方9/18及CSR活跃信息为历史。

## 2026-10-30 最新：第三组独立通过，第四组首项CSR运行中

- 当前9/18 worker完成、3/6独立组通过。block_002/audit.json为all_source_to_route_integration_trials_audited、3/3，全部43文件SHA另行重读通过，完整绑定/计时/串行回执一致。audit SHA256=4d1e885a429c88fc51be58a3605cfcefc9dfe86fc5f38c451577346279894c10；原完整checker未改，第三组checker3246405已退出。
- 保持监督2624526/句柄27488与driver2660361。当前block_003顺序[0,2,1]，首项csr/direct worker3498402/starttick1648702385、native3518408/starttick1648708377已实际核argv/CPU121/AS16GiB/core0，新plan的files/expected_inputs/jobs与前组相同。下一轮先核v19、原handle及实际/proc，等待CSR完整输出后再按原顺序执行compact/direct、compact/expanded和原独立组checker。
- 全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方2/6及第三组checker活跃信息为历史，不从三组提前作完整补充性能结论。

## 2026-10-30 最新：9/18完成，第三组原独立审核运行中

- block_002/worker_002 compact/direct完整两批各1062网输出通过，native/外层worker均exit0；11项artifact及原参考SHA另行重读通过，完整语义、原输入/训练/实际资源与串行回执一致。报告SHA256=e1603bb318d97ac07e59a751bf7e003754efcd78f50e1db9258ebf7d2541eb53，outer receipt SHA256=77857200f85eb3f6d0c6d88f451c7a2a942d244ba6cb5bc02029bc070ba5619a。当前9/18 worker完成、2/6独立组通过，第三组audit.json尚不存在。
- 保持监督2624526/句柄27488与driver2660361，当前stage=original_full_block_audit。原checker3246405/starttick1648630162已实际核cwd/完整argv且无--partial、CPU121/AS16GiB/core0和原源码SHA。旧worker2617400/native2645430均退出，block_003未建立；下一轮先核v19和该checker实际身份，等待原完整组审核通过后再核第四组启动，不另起审核。
- 全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持。原RTL2005478继续运行、最近0/4、未新增OOM，完整实验未完成。下方8/18及最后一项计算活跃信息为历史，CPU日志round解释纠正继续适用。

## 2026-10-30 最新：8/18完成，第三组最后一项compact/direct已启动

- block_002/worker_000 csr/direct完整两批各1062网输出通过，native/外层worker均exit0；10项artifact及参考SHA另行重读通过，原输入/实际资源/完整语义和串行回执一致。报告SHA256=7248468bce293c72327f46c7a73a48880b5005f199d3bdd89d74c91429b216a8，outer receipt SHA256=a37c7a3f94a9a93af683a0c9dffd8309b9aca2002a4d441b349d9afa99306952。当前8/18 worker完成、2/6独立组通过，第三组未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_002 position2 compact/direct worker2617400/starttick1648445066、native2645430/starttick1648453319已实际核argv/CPU121/AS16GiB/core0；下一轮用v19、`block_002/worker_002/native.submission.json`及/proc重新核身份。旧worker2143113/native2163692已退出，不重启或沿用。
- 下一轮先核v19和实际进程，等待本项完整输出与原组checker，再推进后续三组。全部六排列18项、原9要求8变体、完整功能链及physical/board缺口保持；原RTL2005478继续运行、最近0/4、未新增OOM，完整实验仍未完成。下方7/18及CSR活跃状态为历史。

## 2026-10-30 最新：7/18完成，第三组第二项CSR已启动

- block_002/worker_001 compact/expanded完整两批各1062网输出检查通过，native/外层worker均exit0，11项artifact及参考SHA另行重读通过，原输入/训练/实际资源及串行回执一致。报告SHA256=04e652d0d971f3f6b3e12ca92f41f5a3a310cd95c01872e0ef2de7a698bd2c8f；outer receipt SHA256=cb1994d7ce6cab1d1306dd2df535b8323fd7552185a4226398f98ca1f60c4458。当前7/18 worker完成、2/6独立组通过，第三组尚未整组验收。
- 保持监督2624526/句柄27488与driver2660361。当前block_002 position1 csr/direct worker2143113/starttick1648310928、native2163692/starttick1648317064已实际核argv/CPU121/AS16GiB/core0。下一轮先核v19、`block_002/worker_000/native.submission.json`和实际/proc身份。旧worker1717258/native1742584已退出，不重启或沿用。
- 按原第三组顺序[1,0,2]继续CSR→compact/direct及原完整独立checker，保持全部六排列18项。原RTL2005478继续运行、最近0/4，未新增OOM；原9要求8变体及完整功能链、physical/board缺口保持，完整实验未完成。下方6/18及第三组首项运行信息为历史；日志round含义纠正仍适用。

## 2026-10-30 最新：第二组独立通过，第三组首项运行中

- 当前6/18 worker完成、2/6组独立通过；block_001/audit.json为all_source_to_route_integration_trials_audited、3/3，全部43文件SHA另行重读通过，完整绑定/计时/串行顺序一致。audit SHA256=fc0a95d3b2703f5e09366f15caf281224ca8fb0fa91677c29b064122375821e0，原完整checker未改；第二组checker1485890已退出。
- 保持监督2624526/句柄27488与driver2660361。当前block_002顺序[1,0,2]，首项compact/expanded worker1717258/starttick1648187792、native1742584/starttick1648195676已实际核argv/CPU121/AS16GiB/core0；新plan原files/expected_inputs/jobs与前组一致。下一轮先核v19和实际/proc，再等待本项完整输出及后续CSR、compact/direct，原完整组checker随后自动运行。
- 原RTL2005478继续运行、最近日志0/4，未新增OOM。全部六排列18项、原9要求8变体、完整功能链和physical/board缺口保持；完整实验仍未完成。下方1/6及第二组审核活跃状态为历史，不从两组结果提前推断完整性能结论。

## 2026-10-30 最新：6/18完成，第二组独立审核运行中

- block_001/worker_000 csr/direct完整两批各1062网输出通过，native/外层worker均exit0；10项artifact及原参考SHA另行重读通过，完整语义值比对/原输入/实际资源和顺序回执一致。报告SHA256=a2c5a6840a46a2def6839ac7b1311a1778620eb8936f5c0aa094a3df6199ec7b，outer receipt SHA256=d844f3d06bcd7a08c20ecf5c9b535934922a8d23495cdd7a04b80dcd488038a4。当前6/18 worker完成、1/6独立组通过，第二组audit.json尚不存在。
- 保持监督2624526/句柄27488与driver2660361；当前stage=original_full_block_audit。原checker1485890/starttick1648116303已实际核cwd/完整argv/CPU121/AS16GiB/core0及原源码SHA，没有--partial。旧worker1057672/native1075344均退出，block_002未建立。下一轮先核现有checker和最终组报告，完整独立审核成功后原driver才进入第三组，不另起审核或重提任务。
- 原RTL2005478继续运行，最新日志0/4，未新增OOM；其余完整串行链及9要求8变体、physical/board缺口保持，完整实验未完成。下方5/18及CSR活跃状态为历史，CPU日志round解释纠正仍有效；只读入口v19保持。

## 2026-10-30 最新：5/18完成，第二组最后一项CSR运行中

- block_001/worker_001 compact/expanded完整两批各1062网输出检查通过，native/外层worker均exit0；11项artifact及参考SHA另行重读，原输入/训练/实际资源/顺序回执一致。报告SHA256=28e4984a1c5e4099a4d510138d5c991a00bf0623e2b8e4561bf61891e8dbfa78；outer receipt SHA256=4ea8a8cd73784df39eddcac1cfe36be2a2f3b09455e36e27e8550a55bad2adc2。当前5/18 worker完成、1/6独立组通过，第二组尚未整组验收。
- 保持监督2624526/句柄27488与driver2660361。第二组position2 csr/direct worker1057672/starttick1647983968、native1075344/starttick1647989830已实读/proc argv/CPU121/AS16GiB/core0核对；旧worker659505/native684636已退出。下一轮先用v19、原handle及实际/proc复核，等待该CSR完整输出和本组原checker，不重复提交。
- 原RTL2005478继续运行、最近日志0/4，三个后续监督身份匹配、等实际独立前置，未新增OOM。全部六排列18项、原9要求8变体、完整RTL链及physical/board缺口保持；完整实验未完成。下方4/18及第二项活跃状态为历史，round/batch解释纠正继续有效。

## 2026-10-30 最新：4/18完成，第二组第二项compact/expanded已启动

- block_001/worker_002原两批1062网完整输出通过，11项artifact及参考SHA另行重读，原输入/训练/实际limits/顺序回执一致。报告SHA256=c6d744553da2c633b6fe0e046326763017376a2219468afb776c0076c76d4afd；当前4/18 worker完成、1/6独立组通过，第二组尚未整组验收。
- 保持原监督2624526/句柄27488与driver2660361。新compact/expanded worker659505/starttick1647860142实际身份/CPU121/AS16GiB/core0已核；新native从`data/derived/training_order_control_20261029_v1/block_001/worker_001/native.submission.json`及/proc复查。旧worker77421/native102261已退出，不重启、不重复提交。
- 继续原第二组顺序[2,1,0]和全部六排列18项，完成后独立整组审核。原RTL2005478继续运行、最新日志0/4，完整9要求8变体及physical/board等缺口保留；完整实验尚未完成。下方3/18及旧首项活跃信息为历史，日志round解释纠正继续有效。

## 2026-10-30 最新：第一组独立通过，第二组首项实际运行

- 当前3/18 worker完成、1/6组独立验收；`data/derived/training_order_control_20261029_v1/block_000/audit.json`状态all_source_to_route_integration_trials_audited、3/3，全部43绑定另行重读通过，SHA256=33c1834d8b2d53b00b4256baca9d8608b6bc355b022315a93c10c00cf27357f2。原完整两批输出/训练/计时checker未改，第一组checker4050806已退出。
- 唯一监督2624526/句柄27488及driver2660361自动进入block_001顺序[2,1,0]。首项compact/direct worker77421/starttick1647675255、native102261/starttick1647683319已核实际身份/argv/CPU121/AS16GiB/core0；下次先核v19和原handle、/proc。等待本项完整退出与输出审核，再按原顺序继续，不重复提交或改冻结源。
- 原RTL2005478继续运行、最近日志0/4；原完整功能链/物理v2准备和9要求8变体保持。补充统计仍须全部18项/6组通过后解释，不能从首组或局部日志推断完整验收。下方0/6及旧checker运行信息为历史，round/batch监控纠正继续适用。

## 2026-10-30 最新：3/18 worker完成，第一组独立审核运行中

- compact/direct第三项原完整两批1062网校验通过；11文件及参考SHA另行重读通过，原输入/训练bank/实际资源限制和回执一致。报告`data/derived/training_order_control_20261029_v1/block_000/worker_002/report.json` SHA256=1d76da2335466659cd1fea74e4f7a30d38c11e5bdd6d10a01a641640330da802。当前3/18仅worker完成，0/6独立组验收，不能称第一组通过。
- 唯一监督2624526/句柄27488、driver2660361已自动启动原组checker4050806/starttick1647604240，stage=`original_full_block_audit`，实际argv/cwd/CPU121/AS16GiB/core0已核。旧worker3488238/native3512317已退出；block_000/audit.json与block_001尚不存在。下一轮先重新核v19、handle和实际checker，完成后再复核整组报告；不另起checker/新组或修改冻结入口。
- 原RTL2005478继续运行、最新日志0/4；原完整RTL串行链与物理v2准备保持，完整9要求/8变体和未完成结论不变。下方旧2/18为历史；CPU日志迭代轮次不能当作batch进度的纠正仍有效。

## 2026-10-30 监控纠正：CPU日志编号是迭代轮次

- `NATIVE_SITE_PROGRESS <round> <done>`并未打印batch编号；round在每批内从0开始，done是该轮处理网数。原runtime及site_routes源码已与执行plan逐SHA核对。不能把`1/2 1062`解释成两个batch已完成；前面会话中的该解释已纠正，不修改活跃日志或源码。
- 当前2/18完成仍由实际完整报告/两批原输出校验/exit0及SHA支持；第三项完成与0/6独立组计数只能根据最终回执/原checker更新，不能由部分日志推出。当前运行交接与全部原范围继续按下节执行。

## 2026-10-30 最新：顺序补充2/18 worker完成，第三项已启动

- compact/expanded已完成原两批1062网完整输出校验，11项artifact和参考SHA另行重读通过，原生成输入/训练bank/实际limits/顺序回执一致。报告`data/derived/training_order_control_20261029_v1/block_000/worker_001/report.json` SHA256=22fa10b1e6382d72ad625399ae27602d7bfdc56122695edfa1cd2e7096ecbeed。当前仍0/6独立组验收，等待第三条件完成后由既有原checker审核整组。
- 保持监督2624526/句柄27488、driver2660361；第三项compact/direct worker3488238/starttick1647421250、native3512317/starttick1647429225已实际运行。旧worker3103426/native3127640已退出。下一轮先核v19、原handle和/proc；不重复提交、不改冻结源或缩减18项范围。
- 原native RTL2005478继续运行、最近日志0/4；完整RTL串行链和物理v2准备保持。新单项耗时不提前作性能结论，原9要求/8变体与完整实验未验收结论不变。下方1/18及旧第二项运行信息为历史。

## 2026-10-29 最新：顺序补充1/18 worker完成，0/6独立组验收

- block_000/worker_000 CSR已退出0并通过原worker的完整两批1062网输出比对，10个artifact绑定另行重读。报告`data/derived/training_order_control_20261029_v1/block_000/worker_000/report.json` SHA256=4d041916be08cb1214ab8ab8f65f5166db22a3de68cc1f1086c217be5815d51c。独立组audit还未生成，须等三个条件完成后由原checker再审核；不可把worker内部通过冒充独立组验收。
- 当前监督2624526/句柄27488、driver2660361保持；下一compact/expanded worker3103426、native3127640（starttick1647304264）已真实运行。旧CSR worker2680365/native2698665已退出，不重启。先用v19与/proc核最新状态，再观察已有流程，不另起补充实验。
- 原RTL2005478本次仍0/4；完整功能串行链及物理v2准备状态保持。所有活跃/冻结源不改，原9要求/8变体和18项补充范围不缩减；单项计时不作速度结论。下方0/18及旧CPU native活跃信息为历史。

## 2026-10-29 最新运行交接：v19状态与完整六顺序CPU补充对照

1. 先运行`python3 scripts/experiment_status_v19.py`或`--json`，核真实/proc身份；它只是实时观察，不重新验收SHA。原native RTL2005478（owner1121343/driver1128465）上次0/4；原native→CSR→compact→tree50→snapshot30→read2串行链继续，物理v2尚未执行。
2. 补充CPU六种顺序已经真实运行，不要重提：监督2624526/工具句柄27488，driver2660361，首CSR worker2680365、C++ native2698665。目录为`data/derived/training_order_control_supervision_20261029_v1`与`data/derived/training_order_control_20261029_v1`；开始时0/18、0/6。最终目标`results/training_order_control_audit_20261029_v1.json`，接受status必须`all_six_order_permutations_18_complete_training_inclusive_workers_independently_audited`，外层监督还须complete/`six_permutation_full_workload_independently_audited`。
3. 所有6种排列/18完整worker、原两批1062网/训练/完整输入和输出oracle保持；每组独立通过后继续下一组，失败停止、不自动重试。AS16GiB/core0/CPU121，无rawfree启动/运行门，仅新OOM事件保护。计划和所有运行源均冻结，不在活跃实验中修改；启动证据`training_order_control_launch_20261029_v1.json`（16绑定、SHA6b9d4bd8fa20097ad557467f66818b994d38f0eea2de760ec25b6591309c70bb）。
4. 原7组结果及图表仍保留，新的6组为事后独立顺序对照，不能替换、选择性汇报或混池。实际CPU进程原算法/cache4096/预算/14站点模型不变；顺序均衡不等于冷缓存、独占主机或排除并发RTL干扰。终态后再重新核18项完整语义、阶段计时、实际执行顺序和所有SHA，再做并列解释；目前没有新性能结果。
5. 完整原9项要求/8变体继续保留；当前仍不是只剩上板，勿把CPU控制启动或局部验收算完整实验。下方“顺序补充未启动”的历史内容已由本节取代。

## 2026-10-29 CPU图表交接及已核实顺序限制

- 最新CPU结果入口：`results/figures/training_inclusive_cpu_20261029_v2/report.html`，完整21worker/14配对/7顺序/3汇总CSV和两图PNG/SVG/PDF均已生成并核验；独立337绑定证据为`results/training_cpu_figures_integrity_20261029_v2.json`。这是原已完成实测结果的可复现展示，没有新增路由运行或完成FPGA实验。
- 实际顺序不均衡：compact/direct总在compact/expanded之前（7/7），CSR最先2次、最后5次；报告保留原耗时比1.433840和0.909690及全部配对点，并明确共享缓存/顺序影响未隔离。若需要进一步证明公平性能，后续独立补充应覆盖三条件全部6种排列、每worker原新训练和完整两批1062网/原完整oracle，不能修改或取代原7组、不能选择性重跑较优顺序。当前该补充尚未实施，没有等待队列。
- 当前最优先仍是读取`python3 scripts/experiment_status_v18.py`和原native kernel2005478/driver1128465/owner1121343真实状态；本次0/4、未新增OOM，其余原功能链仅等独立前置。物理v2入口已准备但未执行；后续细节与不变完整范围见下节。

## 2026-10-29 当前交接：native 编译已成功，RTL 0/4；物理入口 v2 准备完成

1. 首先运行 `python3 scripts/experiment_status_v18.py` 并核真实进程/日志。native owner1121343/driver1128465/kernel2005478（starttick1646941760）上次实证live；xelab1138642已exit0，2989.593秒，峰值RSS约151GiB。编译阶段证据在`results/native_v2_compile_transition_audit_20261029_v1.json`（17绑定）。编译成功不是完整RTL验收；最终4tx/44ports/30models/4pages、原C和4个946498280byte全快照仍必须通过。
2. 当前唯一自动功能链：native v2 → CSR nonzero v3 → compact nonzero v3 → route-tree v2 full50 → snapshot v5 full30 → read v4 full2tx。三后续监督1271339/1381048/1879400上次均无child，仅等上游实际独立验收；失败即停止，不自动重试/升cap/并发大型A solver。统一无rawfree门槛策略保留有限AS和新增OOM事件保护，旧冻结source/失败证据不改。
3. 当前可用物理入口是`data/derived/encoded_physical_execution_20261029_v2/plan.json`，对应`encoded_physical_entry_v2.py`和`check_encoded_physical_execution_v2.py`。全输入准备报告861绑定、验证报告1173绑定，8单测+6实际提前拒绝均通过；3个job为csr(115文件)、compact(118)、read_control(60)。没有后台物理监督/新A Vivado会话；不能称物理任务已运行或live waiting。
4. 完整当前功能链通过后，先用`encoded_physical_entry_v2.validate_functional()`重新核所有typed报告/SHA，再通过MCP查询会话，创建本模式专有Vivado2022.2 Tcl会话，cwd必须为plan中的work。保留`work/session.json {session_id,pid}`，只source该work的`entry.tcl`一次；入口会再次核实际同模式DUT SHA/终态依赖并施加AS192GiB/core0，绝不直接source原run_flow绕过入口。每个mode串行；真实运行结束后保存含observed_utc/session_id/status的status JSON和原始history JSON，再调用`python3 scripts/check_encoded_physical_execution_v2.py --bundle <完整bundle绝对路径> --job <csr|compact|read_control> --status <status.json> --history <history.json> --output <新的结果路径>`。成功测量但质量不通过时checker会保存负结果并exit2，不宣称200MHz闭合；流程失败不得伪造测量成功。完成证据收集/审核后退出本模式专有会话，再进入下一模式。B的两个既有会话不操作。
5. 原Tcl/clock.xdc逐byte保持U280/5ns/1.35ns/2threads及全部DRC/methodology/完整报告；这是OOC流程。原9项要求/8变体未降级，真实平台shell、DDR/HBM、功耗/实卡、真实路由流量和完整端到端等仍未完成，完整completion_proven=false。详细SHA和限制见AGENTS最新节；历史状态以下保留。

## 2026-10-29：full30快照与read-control已接入当前串行链，状态入口v18

- 新`audit_snapshot_read_original_addresses_v1.py`核13个snapshot指针×30事务和13个read指针×2事务的严格原始framing/完整值集合。snapshot有10个零基址、read有7个；read全部27个C输入/输出向量重新与原已接受search基线逐SHA比较一致，相关原C++/RTL/报告绑定共83项。结果`snapshot_read_original_address_audit_20261029_v1.json`仅为原环境准备审核；零基址本身既不能证明null控制失败，也不能证明任意地址等价。本轮保留两者原地址环境，不套用batch的+4096 wrapper；完整30/2事务和原oracle仍必须实际通过。
- 新`snapshot_read_serial_prerequisites_v1.py`严格核当前native v2、CSR/compact非零v2实际验收（沿用原严格前置），再核tree新v2 full50实际报告/50正cycles/完整容量/生产综合不变、外层控制完整exit0且无resource_abort、同一组native/配对SHA；read还要求新snapshot v5实际full30/13pointers/10models/4pages/8RO/30正cycles和原search实际2tx/7models/5输出/cycles[2132461,12404]。4项单测拒绝部分、旧策略、缺前置、损坏/冲突绑定；不从准备报告推断通过。
- 新`run/check_snapshot_dpi_rtl_v5.py`、`run/check_search_read_control_staging_dpi_rtl_v4.py`保留全部原输入/DUT/ROM/depth/4pages、8个原snapshot RO monitor、完整C后验和每个输出word/全5输出文件校验。两driver最终完整oracle段AST与原v3/v2完全相同，monitor函数AST完全相同；仅更新typed前置/独立路径、XSC --mt off和资源执行器。`run_full_scope_phase_v1.py`采用无rawfree门槛策略，AS64GiB/stack64MiB/core0、CPU120/125保持，记录xelab/kernel真实limits/cwd/身份；checker重新核实际10/7模型分配的完整width/depth/4pages，及各实际回执。snapshot仍原生成默认优化；read仍原O0，不做FSM重编码。
- 新执行器实际跑本机2022.2 XSC --help exit0（未编译/仿真）；注入OOM事件的独立单测用一次性自有child实测exit-15、失败receipt保存且child消失，没有改真实cgroup计数。实际4次driver/checker提前调用均exit1、无正式trial/报告创建；read用真实格式running假状态包也拒绝。`snapshot_read_serial_preparation_20261029_v1.json`冻结712文件绑定、全部原输入、最终oracle AST及负测回执。
- 唯一新监督`supervise_snapshot_read_serial_v1.py` owner1879400（工具句柄50672）实读/proc命令/starttick匹配、所有线程children为空，在`waiting_full50_tree_independent_acceptance`。严格绑定tree监督1381048身份/plan；tree独立full50通过后才单次执行snapshot v5→独立audit→read v4→独立audit，失败停止且不重试。新目标`results/snapshot_dpi_rtl_audit_20261029_v5.json`与`results/search_read_control_staging_rtl_audit_20261029_v4.json`均不存在，新trial均未建。启动观察`snapshot_read_serial_launch_20261029_v1.json` SHA256=a6fb7df199bb052e3073208272569fd7ead2e74090d7f2e7406a310f22692fd2，6绑定另行重读。该观察不是未来存活保证。
- 当前本地功能链为native v2 → CSR v3 → compact v3 → tree v2 full50 → snapshot v5 full30 → read v4 full2tx，各项均实际独立验收后再推进。当前仍只有native xelab1138642实际编译；两旧监督1271339/1381048及新监督1879400均纯等待，无额外大型solver。native日志已进入net/run/write后续模块，观察到VmPeak159690384KiB；并非编译或RTL完成。下次重新核实实际状态。
- `native_v2_no_rawfree_gate_observation_20261029_v1.json`冻结6个相隔10秒采样：50.149秒内同一compiler身份活跃，rawfree仅1114112–1667072bytes、RSS增加2504122368bytes、file cache下降2506678272bytes，oom=0/oom_kill=2不变。它证明旧16GiB门没有再中止本窗口内的编译，并记录同步缓存变化；不独占归因全部共享cgroup变化、不保证后续内存充分或编译成功。原native v1和旧tree保护中止事实保持。
- 最新只读观察`python3 scripts/experiment_status_v18.py`（或--json）显示新增等待及full30/read未开始；不重新核所有SHA、不从报告存在推断验收。AGENTS/NEXT_STEPS旧v17内容以下为历史，其中“full30/read尚未接入”已由本节取代。原9要求/8变体及completion_proven=false保持，physical/board/真实流量与完整端到端等原缺口仍在；不要把串行入口已准备视作完整实验成功。后续优先核实际进程和终态，另行准备与当前新typed验收一致的物理流程，不并发大型A编译/实现。

## 2026-10-29：按“内存门槛解除继续”恢复唯一串行链，最新状态入口v17

- 当前实际执行native非零地址v2完整编译：监督1121343、driver1128465、xelab1138642均实读/proc身份匹配，actual_limits确认编译AS192GiB/stack256MiB/core0。原编译AS无限，本轮收紧为192GiB；RTL/postcheck仍AS96GiB。完整284输入与失败的非零地址v1逐项SHA相同，4tx/44指针/30模型/4pages/全部深度、25组输出和四个946498280byte完整C快照验收要求保持；原DUT/ROM/C oracle没有改动。当前只是elaborate，不能当作RTL验收。
- 本轮明确覆盖旧“保留16GiB rawfree保护”的解释：新`owned_sim_resource_policy_v1.py`不再以启动或运行rawfree/cache数量为中止条件；继续记录memory.current/stat/events/pressure，并在新OOM/oom_kill事件或事件计数重置时停止自有进程组。有限AS是每进程限制，不是共享cgroup总占用保证；不把缓存统计当作可立即回收的保证。3项策略测试、真实prlimit及自有进程组终止检查通过，见`native_nonzero_resource_policy_validation_20261029_v1.json`。旧冻结入口/失败记录保持，后续使用新入口，不改活跃脚本。
- CSR/compact最新入口为`run/check_binary_nonzero_full44_v3.py`，前置为`binary_nonzero_full44_prerequisites_v2.py`。严格要求native实际`compact_nonzero_native_rtl_audit_20261029_v2.json`；compact再要求CSR实际v2报告。两模式267/270完整输入及10个原始include头文件逐项保持v2 SHA，43/45编码模块、30 DPI模型/完整原C oracle不变；AS64GiB/stack64MiB/core0/CPU122保留，改用相同无rawfree门槛策略。3项typed测试、4次实际driver/checker缺native拒绝及完整include闭包验证通过。准备/验证报告为`paired_binary_nonzero_entries_preparation_20261029_v3.json`与`paired_binary_nonzero_entry_validation_20261029_v3.json`。
- 唯一配对监督1271339（工具句柄52984）实际在`waiting_nonzero_native_independent_acceptance`，owner身份匹配且无child；原native独立通过后才单次CSR执行+审核，再compact执行+审核。两候选trial均未建立，不能说候选已编译。新目标报告分别`compressed_bus64_binary_nonzero_rtl_audit_20261029_v2.json`和`compressed_compact_bus64_binary_nonzero_rtl_audit_20261029_v2.json`，当前均不存在。
- route-tree新完整50事务入口为`run_route_tree_full50_recovery_v2.py`，`route_tree_rtl_pipeline_v2.py`相对原pipeline仅为xelab/RTL/postcheck命令增加AS64GiB前缀，去掉该资源前缀后全文逐byte相同。原CPU ASan及HLS setup保持，全部50事务、nodes1048576/path_edges524288/state_words65、生产综合和完整C/独立输出审核不变；不从旧4/50续接，不把4/50当通过。新preflight重核605绑定和旧guard-abort证据，无128GiB准入/16GiB运行rawfree门；2项前置单测及实际缺native入口拒绝通过，未创建新trial/project。准备证据`route_tree_serial_recovery_preparation_20261029_v2.json`。
- 唯一tree监督1381048（句柄21971）实证在`waiting_paired_nonzero_full44_independent_acceptance`且无child，严格绑定配对监督1271339身份；只有两种当前非零候选均独立验收、文件SHA和前置关联全部一致才启动full50。其目标`results/route_tree_rtl_recovery_audit_20261029_v2.json`当前不存在。旧tree失败/内部running历史状态继续保留。
- 当前链是native v2（句柄57768）→ CSR v3 → compact v3 → tree v2，每项实际验收后才启动下一项；任一失败关闭下游、不自动重试。`serial_nonzero_tree_launch_20261029_v1.json`冻结实际compiler/两个纯等待owner与10绑定，SHA256=f353847936f4a64cc6efe4a94b822467cbe62256970b7fd826b86099ba8d6347；启动观察不是后续存活保证。最新采样oom_kill仍2，未新增。native启动和输入验证另见`compact_nonzero_native_launch_20261029_v2.json`、`compact_nonzero_native_entry_validation_20261029_v2.json`。
- 观察用`python3 scripts/experiment_status_v17.py`或`--json`。默认显示当前组件/CPU/恢复链，两个等待监督明确标为`waiting_dependency_only`，并非等待内存。命令只核进程/日志/报告存在，不重新验收SHA。旧v1-v16保持历史。
- 完整9要求/8变体、completion_proven=false保持。full30 snapshot与read-control尚未接到本链：须先审查其独立指针语义并迁移typed前置、资源策略及XSC单线程入口，不能直接运行旧入口。physical、实卡DDR/HBM/功耗/完整端到端和其他原缺口均未完成；目前还不是只剩上板验证。下一会话先重新核native真实进程及内存事件，继续独立准备后续工作，不并发新的大型A solver。

## 2026-10-29：新native编译与route-tree均被运行保护终止；DPI配对回归通过、完整候选入口v2准备完成

- 当前没有native或route-tree solver继续运行。native监督216559/driver224011/xelab233214及tree监督4027507/control4036512/pipeline4036517/kernel4092413等9个记录PID均已/proc确认不存在。native elaborate exit=-15、resource_abort=true、elapsed1515.146647s，实际触发rawfree=17093734400bytes（低于16GiB），未进入RTL。tree控制state明确resource_abort=true/exit=-15、触发rawfree=17149157376bytes，日志最后4/50；其内部pipeline仍写running只是被外层终止后留下的历史状态，不能当live。oom_kill仍2、未新增。原完整范围、输入和失败源均保存，没有自动重试。
- `results/native_nonzero_and_tree_guard_abort_20261029_v1.json`冻结26个文件绑定及两个实际触发采样，全部另行重读核对；SHA256=87428c6799ad3d6ad1061c1c5d9647fda7b83326b143fe81ab819613ceb193bb。它记录资源保护中止，不是RTL通过，也不能仅凭aggregate阈值归因某一活动。新native验收与tree验收报告均不存在。
- 已实际完成CSR/compact各6个真实native模型对DPI+4096平移wrapper的对照，保留每个模型完整depth/4pages/原C输入，宽度32/64、包括65536/163840容量及小meta模型；所有响应、每个输出word和四个RO写/零WSTRB负例通过。readonly模型完整16word×4pages均读取。`paired_axi_rebase_dpi_regression_20261029_v3.json`为12模型结果；独立`paired_axi_rebase_dpi_independent_audit_20261029_v1.json`重读215绑定/41实际阶段回执，另行复算1835600个输出word（每个实现），全通过。此为模型组合回归，不是完整44指针DUT验收。
- 回归v1的XSC auto126线程在AS8GiB/stack64MiB下报Resource temporarily unavailable，v2首模型仿真已通过但harness不接受实际task路径后缀；旧失败日志保留。v3只修正XSC --mt off、实际dpi.so路径及精确a_storage_write_blk注册路径校验，保留AS8GiB/stack64MiB/core0/90秒，未改生产DUT/CPP helper/冻结模型。`paired_axi_rebase_dpi_harness_history_20261029_v1.json`保存本机2022.2 help与失败历史；不宣称通用工具缺陷。
- 新`binary_nonzero_full44_prerequisites_v1.py`严格要求新native typed实际4tx/44pointers/30models/4pages/4正cycles/4个946498280byte快照及全部SHA；compact还要求新CSR实际accepted报告。保留原43/45模块edit与状态关系、四态1280样本、原配对41相同Cpp、DPI/原失败证据等前置。3项单测覆盖旧结果/部分范围/错误模式/缺实际native等拒绝。不得以新地址准备冒充原native v3或新native通过。
- 最新候选入口使用`paired_binary_nonzero_contract_v2.py`、`run_binary_nonzero_full44_v2.py --mode 0|1`、`check_binary_nonzero_full44_v2.py --mode 0|1`、`supervise_paired_binary_nonzero_full44_v2.py`。v1清单漏记每模式10个原生成include头文件（原copytree会复制、原copied_files未列）；v1从未执行，不使用它启动。v2补齐递归include闭包，10文件逐字等于原HLS工程，其余所有输入SHA与v1相同；分别267/270输入，43/45编码模块、30原DPI模型/44平移向量/4页/原完整C快照均保持。`paired_binary_nonzero_entries_preparation_20261029_v2.json`已生成并验证完整绑定。
- `paired_binary_nonzero_entry_validation_20261029_v2.json`审核include闭包、两模式其余输入不变、driver/checker终态stage相同；实际4次CLI均因缺新native验收报告exit1，未创建trial/验收结果。验证报告SHA256=e6b997ebc8fbc5a5518ca93cd84764b2f959b088225e7f088e850b51f0d1112f。v2保留AS64GiB/stack64MiB/core0/CPU122/16GiB运行保护，XSC单线程；没有恢复128/152/184GiB保守启动门槛。两模式新trial和监督均未启动，不称“队列已在等待”。
- `native_nonzero_resource_review_20261029_v1.json`记录中止后两次内存组成与本机xelab help：末采样rawfree约115.42GiB、anon约19.99GiB、file cache约162.75GiB。memory.current包含文件缓存，rawfree不足不等于已发生不可回收OOM；inactive_file等统计也不保证即时可回收量，不能据此豁免当前保护。原成功native峰值约151GiB仍保留，O2虽本机支持但本设计内存收益未测，--incr重用原编译快照也未证明。没有清缓存、改cgroup或修改运行保护策略。
- 最新只读状态入口为`python3 scripts/experiment_status_v14.py`（或--json）：正确显示native failed、tree resource_aborted、新候选v2 prepared但未启动。下一步先形成有证据的native完整编译恢复方案，再接新typed配对链；route-tree仍须原完整50事务恢复，full30 snapshot/read的各自指针语义也待审查，physical/board等缺口不变。CPU训练计入21项统计已完成；完整9要求/8变体、completion_proven=false保持。不得重启相同失败配置或将本次准备当作完整目标完成。

## 2026-10-29：两种编码候选的同类零地址冲突已识别，配对平移环境准备及结构审核完成

- 实读CSR/compact原四事务标量向量，各30个指针基址为0；已冻结二进制FSM候选的sink_loop_worker中heap/slots/records/keys/unknown_nodes五个64位空指针比较仍存在。因此不得仅改旧前置报告名后启动原零地址候选。
- `prepare_paired_binary_nonzero_axi_v1.py`生成data/derived/paired_binary_nonzero_axi_20261029_v1，每种模式完整44指针×4事务+4096、30原DPI模型外层地址减4096；逐模型宽度/depth/4pages与原配对矩阵完全相同。CSR43/compact45个已编码FSM以及所有其他DUT/ROM均保留原冻结文件，不做第二次编码转换。两种模式各30个零基址的原输入及NULL比较行均记录在准备报告。
- `results/paired_binary_nonzero_axi_preparation_20261029_v1.json`仅准备；独立`check_paired_binary_nonzero_axi_v1.py`重新检查60模型全文/全部连接、88个指针向量各4事务的严格逆变换、两模式完整保留文件集合，并重读2350绑定。`results/paired_binary_nonzero_axi_structure_audit_20261029_v1.json` SHA256=bfd75445c80a0c509e32b1feccb7d4c6af51d943f57d7fc7a7e68b448a5e2cb2。这不证明实际DPI+wrapper行为或完整候选RTL通过。
- 后续先做真实DPI模型与平移wrapper的组合行为回归；再准备新typed full44入口，严格依赖正在运行的新native完整验收（compact_nonzero_native_rtl_audit_20261029_v1.json，目前不存在）。旧候选driver/checker与旧链failed事实保持，不创建候选trial或并发大型编译。full30 snapshot/read控制也须检查各自指针语义后再衔接，不从本配对审核推断它们通过。
- 当前真正活跃的集成步骤仍为native新编译，非“候选队列已运行”。观察继续用experiment_status_v12.py；完整9要求/8变体及completion_proven=false保持。

## 2026-10-29：非零AXI模型回归通过，完整native full44新试验已真实编译

- 零地址/null冲突的修复仅在仿真环境：完整44指针×4事务加4096，30个AXI模型外层AWADDR/ARADDR减4096。`prepare_compact_nonzero_axi_models_v1.py`保留原模型全文（仅内部模块名改变）、全部14参数/所有端口、原depth/4pages/RO guards；独立`check_compact_nonzero_axi_models_v1.py`对30模型审核通过。生产DUT/ROM、C payload和原C校验器均不改，没有FSM重编码。
- 本机Vivado2022.2 XSim实际回归：5种总线宽度32/64/128/256/512，1300合法请求、20非法地址/unknown/burst/4KiB/范围负例全部通过；6个原始模型以真实完整depth/4pages执行，对所有响应、全部输出word及RO写/零WSTRB拒绝核对通过。报告`results/axi_rebase_guard_regression_20261029_v3.json`与`axi_rebase_model_regression_20261029_v3.json`；独立`axi_rebase_regressions_independent_audit_20261029_v1.json`另行重读301个文件绑定、43个实际阶段回执。结构8种破坏和完整输出解析8种破坏拒绝测试通过。
- 初版测试入口失败均保留：v1缺默认timescale，v2负例CASE未正确选择且文本解析器不接受原RTL直接transaction framing；v3显式timescale、单独读取/记录/核对CASE、严格兼容可选runtime外层，未修改冻结guard/模型或降低负例要求。最小plusargs探针保存于data/derived/xsim_plusargs_probe_20261029_v1；未据此宣称通用XSim缺陷。
- 新完整入口`run/check_compact_nonzero_native_rtl_v1.py`及`supervise_compact_nonzero_native_rtl_v1.py`已准备并真实启动。284个输入文件全部逐SHA复制，保留4tx/44pointers/30models/4pages/所有深度、25组原输出和4个946498280byte完整C快照oracle。准备/入口校验报告分别`compact_nonzero_native_entry_preparation_20261029_v1.json`、`compact_nonzero_native_entry_validation_20261029_v1.json`；实际checker缺trial时拒绝，driver/checker completion stage一致。新验收目标`results/compact_nonzero_native_rtl_audit_20261029_v1.json`尚不存在，不能伪造原v3通过。
- 唯一监督216559/starttick1646335749、driver224011/starttick1646338078、xelab233214/starttick1646341401均实读/proc匹配，当前阶段elaborate。执行工具句柄59293。启动报告`results/compact_nonzero_native_launch_20261029_v1.json` SHA256=066e03f6206519434d2391ff9959bf4782c6c0eb5ad42322465e9932b731faba，冻结启动观察，不是当前状态保证。后续须重新核进程与日志，不修改活跃/冻结源。
- 编译沿用原成功native的unlimited AS、-mt off/--O0/--stats，仅为新guard加默认--timescale1ns/1ps；实际编译AS无限、stack256MiB、core0已核。原成功编译峰值约151GiB，不把96GiB运行上限误用于编译，也不保证共享内存必足。仿真/postcheck保留AS96GiB/stack256MiB/core0；所有执行阶段保留16GiB rawfree保护并记录触发采样，只终止自有进程组。用户解除的128/152/184GiB保守启动门槛不恢复，无清cache/自动重试/升cap。
- 新只读入口`python3 scripts/experiment_status_v12.py`（或--json）同时保留原native v3和旧串行链failed，显示新native编译live。route-tree kernel4092413/starttick1627750471再次匹配，仍4/50；CPU训练计入21项统计已complete。旧四个下游不再等待、未启动，未来须对新native实际accepted结果建立新的typed前置，并检查其各自零地址配置，不能简单替换旧报告名后放行。
- 原9项要求/8变体和physical/board等缺口保持，完整completion_proven=false。MCP本轮查询的两个会话均属B，未操作；本次复用本地2022.2批处理，已应用Ross vivado-simulate-rtl的显式验收/失败保存流程。

## 2026-10-29：CPU训练计入21次统计完成；native full44出现功能失败，已定位零地址空指针冲突

- `results/source_to_route_training_statistics_audit_20261027_v2.json` 已正式complete/21 workers/7配对组，原监督2733975与统计driver353656已退出。最终报告SHA256为85b95f23f1f4b59bcdd9a19ce1b135cdfb1597f1184c768c0212186bafc8f345；`results/source_to_route_training_statistics_integrity_20261029_v1.json`另行重读320个文件绑定、复算全部统计并核四阶段exit0/非资源中止。每worker仍完整2×1062路由、原3761训练源/440模板及完整输出审核。application双批中位数CSR/direct=1084.871s、compact/direct=1547.898s、compact/expanded=988.355s；相对CSR的配对比中位数分别1.433840和0.909690。直接解码没有CPU加速；14-site模型、共享主机/cache及不含Vivado采集/board/readback限制保留。native_child_peak_kib是RUSAGE_CHILDREN继承记账，不可当独立native-only post-exec VmHWM。
- 原native v3实际跑完4/4，rtl receipt exit0/62302.761s/resource_abort=false，cycles=[4272278,76969,4265293,8629]；随后的原C postcheck在test_compressed_batch_rtl_full_depth.cpp:165断言失败，exit-6/8.014s/resource_abort=false。不是内存保护中止或完整RTL通过。只生成首个946498280byte快照，44端口全量逐块比较有29端口不同；其余3个C快照未生成，四事务原始RTL输出均保存。`results/compact_native_v3_postcheck_diagnosis_20261029_v1.json`绑定1814文件，SHA256=68aee88a5e3fa4cae3126a784a6f3a4caba6bd65f2294ea70fdb594cdfdc0596。
- 首搜索result=6 invalid_input，control_result前两项[4,3]、net_result前三项[2,6,4]、batch_result前三项[3,2,2]。实际四事务image/config/heap/slots/records/keys/unknown_nodes指针地址均0，而冻结sink_loop_worker RTL含相应null比较、OR归并及state2010错误分支。原生产C内核以保存输入重放，正常主机指针下全部81结果word和完整路径精确匹配原C首搜索，显式nullptr返回6；证据`results/compact_native_first_search_replay_audit_20261029_v1.json`。从真实RTL逐字抽出的24条组合赋值又在本机2022.2 XSim实际跑16例通过，零基址拒绝、所有指针+4096后该拒绝条件解除、各单独零指针/packet长度边界正确；`results/compact_null_pointer_cone_audit_20261029_v1.json`。这只是诊断重放及组合逻辑验证，未捕获完整内部波形，不能代替新的full44 RTL验收。
- 原owner1318691/kernel1328613/audit1323871和集成监督1497979均已退出；集成链state=failed，四个下游仍未开始，不能称live waiting。新`prepare_compact_nonzero_axi_vectors_v1.py`已生成完整44指针×4事务的+4096地址向量，并列出30模型的映射需求，逐项逆变换恢复原文件完全一致、所有绑定另行重读通过。`results/compact_nonzero_axi_vectors_preparation_20261029_v1.json`明确models_modified=false/execution_entry_prepared=false/rtl_executed=false；不能把新向量直接用于原零基址模型。原DUT、模型、失败state及冻结脚本未改，没有自动重试或升cap。
- 失败证据持久化归档及原件/副本独立重读已完成：1804文件、24473451892bytes，原件保留；`results/frozen_compact_native_v3_failure_archive_audit_20261029_v1.json`，SHA256=a657020de337b070c8b3285eef724f1f4db446a9e87312391551b331b9c4ec4f。此为失败证据归档验收，不是RTL通过。
- 原未编码native的elaborate.log实测/usr/bin/time最大RSS=158275628KiB（约150.94GiB），工具peak=159674880KB；原编译成功无该恢复脚本的96GiB AS限制。96GiB是恢复XSim运行上限，不能误用于重新编译并假定足够；后续须明确编译/运行分别的资源依据，不能盲目重复已知不足配置或自动升cap。
- 下一步实现并独立核对AXI物理地址→原模型偏移的4096平移，保留低12位/4KiB边界、全部depth/4pages/44指针/30模型/RO guards/原C oracle；负测边界、unknown、RO写及不合法地址。随后用新版本完整4tx原DUT试验和四份完整快照验收，只有真实通过才能改绑后续CSR/compact编码、full30、read/physical入口。不得伪造原native v3通过或放松独立验收前置。
- 布线树恢复kernel4092413/starttick1627750471本次/proc命令身份仍匹配，日志4/50；后续必须实时复查。只读入口仍`python3 scripts/experiment_status_v11.py`，已正确显示CPU complete、native/postcheck与集成链failed及tree running。完整原9项要求/8变体、physical/board等缺口保持，completion_proven仍false；用户解除的保守启动内存门槛不恢复，既有AS与16GiB运行保护保持。

## 2026-10-28：训练计入 CPU 重复实验第四组独立验收通过，第五组启动

- data/derived/source_to_route_training_statistics_20261027_v2/block_003/audit.json 状态all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3；43个artifact SHA已另行逐文件重读核对。报告SHA256=93da0824a964a55184c2f4a774ee351bc70c0689ac1b475f4851d07eb33c89e1。
- 第四组checker2720935已退出；统计driver353656已实际启动block_004 worker2 compact/direct，worker2974562/starttick1632456980命令已核实，后续须实时复查。当前4/7组独立通过、12/21项完成，最终统计尚未生成。
- 两项RTL恢复kernel1328613与4092413本次仍存活；完整9要求/8变体与physical/board等剩余范围保持，完整实验尚未验收通过。

## 2026-10-28：训练计入 CPU 重复实验第三组独立验收通过，第四组启动

- data/derived/source_to_route_training_statistics_20261027_v2/block_002/audit.json 状态all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3；43个artifact SHA已另行逐文件重读核对。报告SHA256=27831b484c31a3fa1f60b81b999526ad543c351b0a0edca42e9ddc4f38e749ab。
- 第三组checker1018211已退出；统计driver353656已实际启动block_003 worker2 compact/direct，worker1260851/starttick1631948917命令已核实，后续须实时复查。当前3/7组独立通过、9/21项完成，最终统计尚未生成。
- 两项RTL恢复kernel1328613与4092413本次仍存活；完整9要求/8变体与physical/board等剩余范围保持，完整实验尚未验收通过。

## 2026-10-28：训练计入 CPU 重复实验第二组独立验收通过，第三组启动

- data/derived/source_to_route_training_statistics_20261027_v2/block_001/audit.json 状态all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3；43个artifact SHA已另行逐文件重读核对。报告SHA256=13fcf821227d87c57587103fbd7a1d12168c7af58a3329de54a227f533c37964。
- 第二组checker3510850已退出，统计driver353656实际启动block_002 worker2 compact/direct，worker3751792/starttick1631446135命令已核实；后续须实时复查。当前2/7组独立通过、6/21项完成，最终统计尚未生成。
- 两项RTL恢复kernel1328613与4092413本次仍存活；完整9要求/8变体及physical/board等未完成范围保持，完整实验尚未验收通过。

## 2026-10-28：训练计入 CPU 重复实验首组独立验收通过，第二组启动

- data/derived/source_to_route_training_statistics_20261027_v2/block_000/audit.json 状态all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3；43个artifact SHA已另行逐文件重读核对。报告SHA256=38924f5ee49055c1b4df093f1ff32e857decf91ef8c1d6242c90aeaf92b76f40。首组各条件完整两批1062路由，三个工作进程均exit0。
- 首组checker1776877已退出，统计driver353656实际启动block_001 worker2 compact/direct，worker2022054/starttick1630939974命令已核实；后续须实时复查。当前仅1/7组独立通过、3/21项完成，最终统计尚未生成。
- 两项RTL恢复kernel1328613与4092413本次仍存活；完整9要求/8变体及physical/board等未完成范围保持，不能以首组统计验收推断完整实验通过。

## 2026-10-28：训练计入 CPU v2 三条件独立验收通过，7组配对重复已实际启动

- results/source_to_route_training_validation_audit_20261027_v2.json 状态all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3；验收receipt exit0/resource_abort=false，elapsed706.768327195197s。报告43个artifact SHA已逐文件另行重读全部核对，报告SHA256=14c7a91ccf7152b890e8ecdd38c96748322e329c241be6ab7f0ba82ac27084b1。
- 原checker111753已退出。supervisor2733975自动进入seven_paired_blocks，实际统计driver353656、block_000 worker361454已核命令存活；下次须重新核实身份和终态。范围仍7个配对block、21工作项，每项原完整两批1062路由及完整输出审核，不以此次三个单次集成验证替代重复统计。
- 本次只接受训练计入的本地CPU三条件集成验证；原14-site模型、共享主机限制及Vivado采集/板卡传输/物理回读计时缺口保留。RTL恢复仍在运行，physical/board及原9要求/8变体完整完成仍未证明。

## 2026-10-28：训练计入 CPU v2 三条件完整双批自检完成，独立验收已启动

- worker_002 compact/direct 的 native.receipt exit_code=0，完整两批各1062路由自检通过，report.status=regenerated_inputs_and_two_full_batches_verified；全部非计时语义值比较1426871976字节。应用计时1546903.680710122ms，native1476721.8113932759ms；单次计时不作统计性能结论。
- worker3689806/native3716793及验证driver2737508已退出；supervisor2733975已自动进入validation_audit，实际checker111753命令为check_source_to_route_with_training_v2.py，未使用--partial，目标results/source_to_route_training_validation_audit_20261027_v2.json。下次须重新核实进程身份和终态。
- 当前是三个条件自检完成，独立完整验收仍在运行；7个配对重复/21工作项尚未启动。原完整9要求/8变体保持，RTL恢复及physical/board等缺口仍未闭合，不能判定完整实验通过。

## 2026-10-28 compact/expanded完整双批自检通过，compact/direct已启动

- 训练计入CPU v2 worker001/native3252588均已exit0，完整2x1062网的1426871976语义value字节与原compact参考一致；新worker报告status=regenerated_inputs_and_two_full_batches_verified。实际application回执已保存；调用原validate_training再次核完整3761源/440模板、bank/source SHA和object digest、训练冻结先于evaluation读取、三项正训练计时及bank artifact绑定均通过，并核application回执与最终worker报告字段完全一致。此为训练契约检查及worker自检，不冒充第二条件完整独立raw审计；正式三条件checker仍待worker002完成。
- 唯一原监督2733975/driver2737508自动启动compact/direct worker3689806及实际native3716793，命令/starttick、AS16GiB/core0/CPU121重新核实；未开重复作业或更改冻结脚本。当前成功worker回执2/3、正式统计0/21；独立partial报告仍只有首个CSR 1/3，不把自检数当独立验收数。
- 最新观察入口仍scripts/experiment_status_v11.py。原native RTL1328613与tree4092413、集成监督1497979继续运行/等待原前置，未新增完整RTL或物理/实卡验收。完整9要求/8变体保持，completion_proven仍false。

## 2026-10-28 训练计入CPU v2首个CSR完整条件独立核验通过

- v2 worker000的原native2759408已exit0；完整两批各1062网、routes/iterations/status/scope全部1426871976语义value字节与原SHA绑定参考一致，worker自身postcheck及退出码均0。application.receipt.json实际保存，应用区间1085681.686ms；该单次CSR观察不是三条件重复性能结论，也不包含采集/实卡。
- 独立check_source_to_route_with_training_v2.py以4GiB AS/core0、CPU122实际运行，checker3242275已exit0，耗时239.612s。results/source_to_route_training_first_condition_audit_20261027_v2.json明确status=partial_source_to_route_workers_audited、completed_workers=1/planned_workers=3；完整输入/命令/双批原始语义/计时一致性/新application回执均核验，14个artifact绑定另行重读通过。独立命令和退出回执在data/derived/source_to_route_training_recovery_20261027_v2/first_condition_audit.*；此报告不替代三条件验收，不放行21次统计。
- 原监督2733975/driver2737508已自动进入compact/expanded：worker3223018、native3252588；native实际命令/starttick及AS16GiB/CPU121重新确认，本条件的新bank已生成但尚未验收。完整三条件/7配对block/21worker与所有旧范围不变；原CPU v1仍failed。
- 状态入口仍scripts/experiment_status_v11.py。00:03 UTC实查tree4092413仍1/50，但仿真时间已从250098068000推进到300098073000ps；native1328613仍0/4，集成监督1497979仍等待其独立验收。所有相关owner/kernel实证live，oom_kill仍2。完整9要求/8变体及completion_proven=false保持。

## 2026-10-27 原区域采集的计时边界已独立核实

- results/region_capture_timing_boundary_audit_20261027_v1.json核原完整8分片、220973源、分区无重叠且并集完整、原DCP/导出器/输出及合并绑定，47文件SHA再次重读通过。逐分片perf_counter计时实际为8884.391至22440.142秒，最长约6.23小时；该值包含Vivado启动/导出后的Python读入、图验证和源集合检查，且不含随后SHA/状态发布/合并，不能当完整采集总时长或CPU时间，也不能把8项相加作并行延迟。
- 原监督started_utc至capture.json创建时间的记录差为22528.045279秒（约6.26小时）；这只是记录UTC端点之差，不是完整链单调时钟回执。选区、合并、最终hash/发布的独立耗时与placement-to-board总耗时仍未知。不得将这份历史间隔与新CPU计时相加后称实际完整端到端测量；未重启Vivado采集或改动当前CPU/RTL，完整9要求/8变体继续未完成。

## 2026-10-27 CPU完整输出解析触发AS上限，分段核验通过并启动完整v2恢复

- 原训练计入CPU v1监督2061291/driver2061603/worker2065413/native2087151均已退出。native两批执行exit0、1034.544s；Python在读取1426872497byte完整JSON时MemoryError，worker/full_validation exit1，resource_abort=false，oom_kill仍2。results/source_to_route_training_postcheck_memory_failure_20261027_v1.json冻结失败与完整输出，v1仍failed，不当作完整验证通过；应用总计时未保存，不重构或填补。
- 新native_output_segments_v1.py使用只读mmap索引及1MiB分段比较，逐项比较两批所有非原六项measurement字段，保留全部routes/iterations/status/scope；只对已SHA绑定且原独立验收的参考使用该方法。原参考缺少后加peak/logical指标，按原METRICS剔除规则处理，实际新输出仍须完整六指标。该方法要求冻结native序列化逐byte相同，比通用JSON数值等价更严格；虚拟映射随文件大小增长，不声称常量地址空间。
- 5项测试通过，含双批末尾/嵌套metric/历史/缺网/重复键/多或少批/非法计时/截断/跨1MiB尾部损坏拒绝。真实保留输出实际在4GiB AS/core0/CPU121下完成全2x1062核验，elapsed232.540s、peak2126604KiB（约2.03GiB），全部语义字段逐byte等于原参考。results/source_to_route_preserved_full_output_audit_20261027_v1.json绑定完整证据；仅证明保留输出与读取方法，不把v1失效计时纳入统计。
- 新source_to_route_with_training_v2.py/check_source_to_route_with_training_v2.py及统计/监督v2保留同一native binary、原训练3761源/440模板、3条件、2x1062网、7配对block共21worker、CPU121/AS16GiB/core0/16GiB运行保护；路由执行段逐字、计时一致性/配对统计/实际worker执行循环AST与v1相同。变化仅完整分段输出检查、独立v2路径和在postcheck前保存application.receipt.json。新统计入口缺完整验收时实际exit1，未建trial。原失败源、输入及输出不改。
- 唯一v2监督2733975、验证driver2737508、worker2739717已/proc核实命令/cwd/starttick，worker实际AS16GiB及CPU121确认。 随后实际native2759408启动，AS16GiB和CPU121亦通过prlimit/affinity重读；下次须重新核实。先完整三条件及单独checker，再21次完整统计；当前仅首验证worker运行，尚无新完整验证或统计验收。准备/启动报告分别results/source_to_route_training_recovery_preparation_20261027_v2.json、source_to_route_training_recovery_launch_20261027_v2.json（30绑定重读）。失败不自动提高cap或缩范围。
- 最新只读观察入口为python3 scripts/experiment_status_v11.py（或--json），同时保留CPU v1失败并观察v2。原RTL kernel1328613、tree4092413、集成监督1497979再次核实live，分别0/4、1/50、等待native独立验收；未改活跃RTL及串行链。当前完整9项要求/8变体、physical/board和completion_proven=false保持；v9冻结矩阵不是实时进程状态。

## 2026-10-27 含重新训练成本的完整CPU路由实验已启动

- 已核原21次source-to-route统计不含bank训练/Vivado采集。新fresh_training_equivalence_20261027_v1实测完整3761训练源重建440模板，与原冻结bank逐byte/SHA和object digest一致；未读评估图。该单次训练观察不是重复性能结论。
- 新source_to_route_with_training_v1.py在compact worker的同一application计时内先读取原训练TSV、fit、写出并核bank，再打开评估图，构图和实际消费新bank/镜像/fixture完成首批与驻留两批。CSR不训练且相应计时为零。原同一C++ binary/三条件/1062网/两批/cache4096/80轮/budget200000/cap8/全部语义比对保持；实际原始命令、完整golden段、timing一致性函数和七次统计函数AST核对未变，5项训练契约测试通过。数据采集、物理读回、board仍在计时之外，14实例partial-site模型和共享host/cache限制保留。
- 唯一监督supervise_source_to_route_training_v1.py owner2061291、完整验证driver2061603、worker2065413已/proc核实存活；CPU121、每worker AS16GiB/core0通过实际prlimit/affinity重读，16GiB运行保护只终止自有进程组。先3条件完整验证+独立审核，再自动7随机配对block共21新worker+最终审核；失败无重试或缩小范围。当前首验证worker在运行，未有完成/性能结论。results/source_to_route_training_preparation_20261027_v1.json及source_to_route_training_launch_20261027_v1.json冻结准备和启动证据。
- 最新只读观察入口为scripts/experiment_status_v10.py（或--json），增加训练计入CPU链与实际worker命令匹配、成功回执数；回执数不等于语义验收。原RTL kernel1328613、tree4092413和集成监督1497979再次核实存活，未改原活跃脚本/冻结9项要求和8变体，完整completion_proven仍false。

## 2026-10-27 三项物理执行入口与独立报告检查已准备，尚未执行

- 新 `prepare_encoded_physical_execution_v1.py` 已生成 data/derived/encoded_physical_execution_20261027_v1：CSR/compact编码及read控制候选三个完整RTL/ROM集合，run_flow.tcl/clock.xdc逐byte等于各自冻结原2022.2流程，保留xcu280/5ns/1.35ns/2threads。results/encoded_physical_execution_preparation_20261027_v1.json绑定准备证据；execution_entry_prepared=true、physical_executed=false。不把旧onehot HLS资源表当编码后映射结果。
- 新 encoded_physical_entry_v1.py 作为每项entry.tcl之前置：严格核native v3、配对full44、full30、read full2实际accepted报告与SHA，并要求当前集成串行链成功终止，再核独立MCP Vivado PID/cwd/源码。解除184GiB等保守准入等待，仅保留16GiB运行保护。保护进程确认armed之后才source原flow；触发时记录实际rawfree并用pidfd仅终止同一owner，15秒未退出再KILL。逐模式串行，前一物理会话须取证并关闭。
- 新 check_encoded_physical_execution_v1.py 核实际MCP终态/完整source entry历史、保护终态、源码与3个DCP、完整报告/约束/路由状态；保留所有时序/DRC/methodology负结果，质量失败输出报告并exit2，不当作时序闭合。独立平台IO、shell、实卡仍未证明。
- 6项测试通过，包含自建可丢弃Python进程的真实保护终止（不是Vivado设计运行），完整历史/过期/错误owner/PID复用/源码集合变动拒绝。三个真实entry.tcl以tclsh执行均因native v3验收报告缺失而exit1，未创建flow state/guard/reports；三个checker亦拒绝提前验收。results/encoded_physical_entry_validation_20261027_v1.json保存实际入口日志。MCP重新列出的两个现有会话均属B，未操作或新开会话。
- 运行观察仍用experiment_status_v9.py；native kernel1328613、tree4092413和串行监督1497979再次/proc核实live，分别0/4、1/50、等待native独立验收。三项物理流程仅入口准备，不宣称已排队或已开始。完整9要求/8变体及completion_proven=false保持。

## 2026-10-27 完整集成下游串行链已接到 native v3

- 新监督 `supervise_integrated_rtl_recovery_v1.py` owner1497979 已实际启动并核实命令/cwd/starttick、无子进程，等待当前 native v3 owner1318691 / 独立审计1323871 / kernel1328613 的完整验收。然后单次串行执行 CSR编码full4tx/44指针 → compact编码full4tx/44指针 → 原snapshot完整30tx/13指针 → read控制候选完整2tx；每项须独立审核通过才继续。当前四个下游trial均未建，不能说已经在编译或已通过。
- 用户解除保守启动等待后，新版本删除128/152GiB准入等待，仅保留16GiB运行保护（开始时已低于该值则失败）；AS64GiB/core0/stack64MiB、全部depth/pages/guard/C与完整输出oracle保持。运行保护触发后TERM，15秒未结束再KILL，失败不重试或升cap。新trial为CSR/compact v2、snapshot v4、read v3；旧失败入口不改。相同候选的canonical报告路径事前均不存在，继续用于下游typed依赖，不覆盖旧通过结果。
- `binary_fsm_full44_prerequisites_v2.py` 严格改绑本次 `compact_native_stack_recovery_rtl_audit_20261027_v3.json`，不伪造缺失的v2报告。9对源码逐字限制变更核验；四driver/四checker缺前置时实际拒绝且无trial/提前验收；7项监督回归通过，覆盖原v2不能替代v3、PID复用/上游失败、源码变动、非零退出、零退出无报告、部分结果和串行顺序。准备与启动证据分别见 results/integrated_rtl_recovery_chain_preparation_20261027_v1.json、results/integrated_rtl_recovery_chain_launch_20261027_v1.json。
- 最新只读状态入口为 `python3 scripts/experiment_status_v9.py`（或--json），包括native v3、审计监督、新串行链和四个实际执行状态；等待明确为dependency。实测native实际kernel身份匹配、0/4；tree实际kernel4092413仍live、1/50。下次必须重新检查。冻结完整范围矩阵仍 EXPERIMENT_STATUS_20261027_v9.json，早于本次恢复，不当作实时进程证明；完整9要求/8变体及completion_proven=false保持。physical和board仍未完成。

## 2026-10-27 原compact集成full44恢复v3已启动

- 用户解除保守启动门槛；基于实测约202GiB余量启动run_compact_native_stack_recovery_v3.py，复用原compiled snapshot、不执行xelab。owner1318691、独立审计监督1323871、实际kernel1328613已/proc核实；原4tx/44指针/全部深度/RO guard/原C与四份946498280byte快照校验保持。96GiB AS、256MiB stack、core0及16GiB运行保护实读通过。
- 新v3增加v2保护中止证据检查、全线程后代发现和TERM后15秒KILL收尾，原v2未改。独立checker与v2经路径归一逐字相同，实际对running状态拒绝且未产生验收报告。results/compact_native_guard_recovery_launch_20261027_v3.json记录启动证据；仍非RTL通过。
- 布线树完整50事务恢复继续，kernel4092413仍live/1of50且仿真时间推进。只读v8包含tree恢复；native v3当前须直接核新state与/proc，不将v2 failed当作v3状态。旧CSR/compact编码/full30/read监督均failed，尚未恢复或接到v3后面；不能宣称全链运行。

## 2026-10-27 布线树恢复已进入实际RTL

- 用户要求内存门槛解除后继续；实时检查发现原等待监督已自动过门，约212GiB余量，故复用原活跃实验，无交接或重启。supervisor4027507、control4036512、pipeline4036517、XSim4092413均通过/proc核实。CPU/prepare/elaborate退出0，RTL当前1/50及时间推进；尚未通过最终验收。
- 新只读入口为 scripts/experiment_status_v8.py（支持--json），增加3个恢复链状态；旧v7、活跃脚本和v9冻结矩阵保持。results/route_tree_recovery_launch_observation_20261027_v1.json记录本次观察；进程身份下次须重新核实。
- 当前实际运行已不受128GiB启动门等待，16GiB运行保护仍在。用户已授权解除启动等待限制，后续不得只因旧保守准入数值反复等待；按具体资源证据和运行保护决策。原集成链尚未恢复，不能把本次组件恢复说成全链恢复或完整实验完成。

## 2026-10-27 完整范围快照更新 v9

- 最新冻结快照为 EXPERIMENT_STATUS_20261027_v9.json；脚本 snapshot_experiment_completion_v9.py 已实际退出0并逐文件复核历史与新增报告绑定。原9要求/8变体不变，完整completion_proven=false。三项组件RTL验收、布线树7/50中断及原集成链失败均已记录；实时入口仍experiment_status_v7.py。
- check_route_tree_recovery_preflight_v1.py 实际核605绑定通过，因可用内存不足返回2；未执行恢复。128GiB仅保守准入值，不是本组件已测内存需求。

## 2026-10-27 实时更新：两组件验收、布线树中断

- site_occupancy 52/52、retained_nodes 37/37 独立报告已生成，分别238/282文件绑定经额外逐文件SHA重读通过，全部周期为正；仍仅组件RTL功能证据，非完整实验或板级性能。
- route_tree原owner/kernel均不存在，最后7/50且无rtl终态回执；results/route_tree_interruption_20261027_v1.json保存现场绑定，退出原因未知。当前内存余量不足，不直接重启旧入口，不改旧源或降低完整50事务验收范围。
- 原9要求/8变体及完整实验未完成结论保持；旧进程记录均为历史，使用实时状态入口重新核实。

## 实时只读状态入口更新为 v7（2026-10-25）

- 运行 `python3 scripts/experiment_status_v7.py`（或加`--json`）可同时观察原集成链和四个组件RTL；旧v6及所有绑定文件未改。已实际检查四项均被列出：保留边complete/independently_audited、37/37、报告存在；另三项running且owner身份匹配。
- 此命令只观察workflow、日志和报告是否存在，不重新核审计文件SHA，也不从37/37推断验收。保留边219绑定独立重读通过的证据见下节。当前冻结范围矩阵仍v8，早于该组件验收；完整实验completion_proven仍false。

## 新完成：保留边完整深度 37 事务 RTL 独立验收通过（2026-10-25）

- `results/retained_edges_rtl_audit_20261024_v1.json` 已生成；RTL、完整输出postcheck、独立audit退出码均0，owner最终complete/independently_audited。报告219个文件SHA已另行逐文件重读核对，37项周期均为正。报告SHA256：`8d222796913099597f0f8c03f8b29242aa315c378a14beca37b11b0ee767aba0`。
- 保留原生产综合RTL和全部指针深度；容量nodes=1048576、edges=2097152、nets=65536，检查双保留bank、meta、输出尾部与输入/结果guard。饱和版本和65536-net边界包含测试平台播种状态；仅合成事务/HLS AXI模型验证，非真实路由流量、XRT实卡、物理时序、带宽或功耗结果。
- 原owner1977135/kernel2216832及postcheck3558656/audit3591819均已结束。另三个组件最近实时复查仍live：site_occupancy1787486为37/52、route_tree3001920为2/50、retained_nodes459268为2/37；下次须重新核实。v8冻结快照早于本验收，不能当作实时状态。原9要求/8变体、native串行链失败事实和完整实验未完成结论保持不变。

## 当前状态入口：v8 快照及仍在运行的四个组件 RTL

- 最新冻结状态快照为 `EXPERIMENT_STATUS_20261025_v8.json`；原9项要求和8个配置变体保持不变，status=active、completion_proven=false。只读实时状态入口仍为 `scripts/experiment_status_v6.py`。冻结快照不是实时进程证明。
- 本次实际进程复查：site_occupancy PID1787486、route_tree PID3001920、retained_nodes PID459268、retained_edges PID2216832均存活；日志最近分别37/52、1/50、2/37、31/37，仅为部分进度，不是最终验收。下次会话须重新核实实际进程及日志。
- native v2 与其四个下游等待监督已按失败关闭；不要将下方历史记录中的 live waiting 作为当前状态。恢复条件、事件证据与完整范围保持下文所述，尚无完整实验通过结论。

## 最新：native v2 内存保护终止，完整串行链已按前置失败关闭（2026-10-25）

- results/compact_native_v2_guard_abort_20261025_v1.json 冻结21个文件绑定和最终状态：native v2 的 rtl.receipt.json 为 exit -15、resource_abort=true、elapsed 26125.140s，日志最后0/4；不是独立验收通过。运行保护阈值仍16GiB，未保存触发瞬间内存数值，不归因其他作业；oom_kill仍2。
- owner844502/kernel853351/audit850450及CSR1909485/compact2817644/snapshot3163169/read3560722已全部退出，最终state均failed。四个下游trial均未建立，五份目标验收报告均不存在；不能继续称当前链live waiting。没有重试、改cap、清cache或启动新编译。
- 事件冻结时raw free约26.5GiB，远低于新任务128GiB门槛。下一步先分析资源条件和已保留的完整执行证据；任何后续恢复须新版本和明确前置，不直接重启旧入口。四个独立组件RTL仍需实时核实，最近site36/52、edges30/37、nodes2/37、tree1/50，均非最终验收。
- 已新增EXPERIMENT_STATUS_20261025_v7.json（2206独立文件绑定复核，原9要求/8变体不变）；该快照在本事件之前，只读状态入口仍scripts/experiment_status_v6.py。配对编码物理输入准备报告results/paired_binary_fsm_physical_preparation_20261025_v1.json，CSR115/compact118 DUT/ROM，476绑定重读核验，未执行physical且执行入口未准备。实卡入口仍待信息，完整目标尚未完成。

## 最新：候选实际IO预算与当前可用内存核算，保留串行限制（2026-10-25）

- binary_fsm_candidate_memory_budget_observation_20261025_v1.json逐文件stat计数原copy完整319文件6911629381bytes，其中C向量6825406005；25份C输出参考3039403144bytes，完整4个C快照3785993120bytes。参考文本尺寸不是RTL输出/进程总占用的硬上限，编译中间产物未知。
- 本轮首采样cgroup空闲118.8GiB、预算报告末采样100.9GiB，均低于原候选128GiB准入；/sys/fs/cgroup挂载ro且目录不可写，不能在本环境创建独立aggregate memory子组。单进程AS64也不约束全部子进程和file cache总和，因此当前没有证明并发可安全，保留原native独立验收后再候选的顺序，不降低门槛/清缓存/改全局cgroup，不启动新大型任务。
- 原native844502/kernel853351/audit850450及四个后续监督1909485/2817644/3163169/3560722均实时/proc记录身份存活。完整目标active，现状是已核实等待，不是新完成结果；仍需实际完整RTL、physical及board证据。

## 最新：read控制分级完整两事务入口已接到当前full30之后，状态入口v6（2026-10-25）

- 新read_control_pipeline_prerequisites_v1.py严格核当前CSR/compact两full44已接受报告、snapshot_dpi_rtl_audit_20261025_v3完整30tx/13pointers/10models/30正cycles及原search v3已测2tx/7models/5outputs/cycles[2132461,12404]，全部SHA有效。tests/test_read_control_pipeline_prerequisites.py两测试通过（缺snapshot/缩减30项/改原baseline/证据损坏均拒绝）。
- 新run/check_search_read_control_staging_dpi_rtl_v2.py只更新当前typed前置和独立trial位置，保留原HLS staged DUT/ROM、2tx/7models/全depth/4pages/全部输出集合逐byte等价原native基线、原C golden；仅记录新正cycles，不宣称与旧cycles相等。保持原AS64GiB/152GiB准入/core0/stack64MiB/16GiB运行保护，无FSM重编码。driver缺前置exit1且trial未建；checker对真实格式running假包实测拒绝且无提前验收文件，AST completion stage匹配。read_control_v2_entry_preparation_20261025_v1.json冻结准备证据。
- 唯一supervise_read_control_staging_rtl_v2.py owner3560722/exec1404实证live等待full30监督3163169，随后验证全前置+152GiB门才单次执行/独立审核，目标仍search_read_control_staging_rtl_audit_20261025_v1.json（相同candidate语义的canonical报告，原先不存在，不覆盖任何旧通过结果），与既有physical preparation gate一致。
- 当前已配置完整本地功能串行链：原native恢复844502/kernel853351/audit850450 → CSR编码1909485 → compact编码2817644 → full30 snapshot3163169 → read staged3560722。仅原native求解；其余纯等待、candidate trial均未建。scripts/experiment_status_v6.py只读新版本实测识别全部6 live owner及read trial未开始，旧v1-v5不改。physical/board仍未完成，实卡入口仍待用户信息；完整目标active。

## 最新：原full30 snapshot完整入口接在配对图模式之后，状态入口更新v5（2026-10-25）

- 新paired_binary_rtl_prerequisites_v1.py只接受CSR/compact两份typed实际full44 RTL结果，严格44ports/30models/4完整snapshots/4正cycles/编码候选身份及所有SHA；prepared/部分/旧未编码/错误mode报告均不接受。tests/test_paired_binary_rtl_prerequisites.py两测试通过，含缺第二模式、变动证据及错误scope/cycles等拒绝。
- run/check_snapshot_dpi_rtl_v3.py保留原30tx/13pointers/10models/全部原capacity与4pages、8只读monitor、原C golden与每个完整输出word的verify()；原DUT/ROM与默认编译优化不改，未套用FSM重编码。变化仅typed配对前置、独立trial v3、AS144→64GiB/准入168→128GiB（64GiB启动余量）、core0/stack64MiB及16GiB运行门保持。实际driver和checker缺配对结果时均exit1，不建trial/验收文件；AST证明monitor函数与8RO集合和v2完全相同，driver/checker completion stage一致，106原copied绑定全部可正确重定位。snapshot_dpi_v3_entry_preparation_20261025_v1.json冻结证据。
- 唯一supervise_snapshot_dpi_rtl_v3.py owner3163169/exec7849已live等待compact编码监督2817644的独立完成，再核两图完整结果/128GiB门后才启动单次原snapshot与审核，目标results/snapshot_dpi_rtl_audit_20261025_v3.json。不能再把旧v2失败监督当本轮，原source/state历史保留。
- 当前完整已配置串行链：原native恢复844502/kernel853351/audit850450 → CSR编码1909485 → compact编码2817644 → 原full30 snapshot3163169。仅native求解，后三者均纯等待。scripts/experiment_status_v5.py新只读版本实测识别全部5个live owner及snapshot_v3 trial未启动，旧冻结v1-v4不改；后续查看用v5。full30及后续staged-search/physical/board都未验收，完整目标active。

## 最新：配对compact编码候选full44执行/独立审核入口与串行链完成（2026-10-25）

- 新run/check_compressed_compact_bus64_binary_fsm_rtl_v1.py保留原mode1 full4tx/44指针/30模型/全部depth/4pages/RO guard矩阵、原C postcheck与4个946498280byte完整快照；应用已审核45模块FSM编码，所有152文件逐candidate SHA完全一致。独立checker重新核实际DUT每个ledger，compact setup明确绑定原LOCAL setup.json及guarded plan摘要，不误用CSR结果schema。编码改变和不宣称native周期相等均显式记录，独立目标compressed_compact_bus64_binary_fsm_rtl_audit_20261025_v1.json不冒充原onehot通过。
- compact_binary_fsm_full44_prerequisites_v1.py要求typed CSR编码候选full44实际accepted报告与完整4snapshots/44ports/30models，再核配对准备/compact45模块edit与真实state关系证据及全部SHA。三单测通过，覆盖缺CSR/证据更改/旧未编码报告/部分ports/models/snapshots/错误模式顺序/不全45模块拒绝。实际driver和checker在缺CSR报告时均exit1，无trial或提前验收报告。跨driver/checker AST final stage完全一致。
- 唯一supervise_compact_binary_fsm_full44_v1.py owner2817644/exec87319已live等待CSR监督1909485的独立完成，无求解子进程；compact_binary_fsm_full44_entry_preparation_20261025_v1.json冻结全源与真实wait证据。两模式同64GiB AS/128GiB准入/16GiB运行门/core0/stack64MiB、单次执行后独立审计、失败不自动重试或升cap。
- 当前串行链明确：原native恢复owner844502/kernel853351/audit850450 → CSR编码候选监督1909485 → compact编码候选监督2817644。当前仅原native求解，候选两者都在等待；full30 snapshot、staged-search、physical和board仍未补齐，不隐藏剩余项。完整目标active，未新增大型编译。

## 最新：compact global64紧凑FSM配对候选准备与同策略审核通过（2026-10-25）

- scripts/prepare_compact_binary_fsm_inputs_v1.py核原guarded/DPI preflight全部SHA，私有staging保留完整152个RTL/ROM/.sv文件，只应用原已审计30模型DPI存储转换，graph_mode1/full4tx/44指针/depth/pages/guards不变。shape v3对45个FSM/59281状态通过，top初始化格式不符保持拒绝。相同transform_hls_fsm_binary_v1.py生成hls_compact_binary_fsm_candidate_20261025_v1：45模块仅编码变化，107文件逐byte保留。
- 原check_hls_fsm_binary_v1.py独立edit审核通过（results/hls_compact_binary_fsm_candidate_edit_audit_20261025_v1.json）；新增state_relation_v2仅增加显式--expected-modules参数（本轮45，不强迫43），同一算术/转移检查对18599383组state/predicate、62519条命名转移全部通过，结果hls_compact_binary_fsm_state_relation_audit_20261025_v1.json。仍不是完整RTL/通用形式等价验收。
- scripts/check_paired_binary_fsm_candidates_v1.py再次核原41个相同Cpp源的基线配对证明及两候选全部绑定，确认同一转换script SHA、mode0/1来源、每模式full4tx/44指针、全部30bundle的(width,depth,pages)字典完全相同（每model4pages）。paired_binary_fsm_candidates_preparation_audit_20261025_v1.json通过，明确CSR43与compact45模块差异保留、候选两边完整RTL/physical/board均未验证；不把onehot HLS资源表冒充新编码资源。
- 未改原DUT/active scripts，没有大型编译。原恢复owner844502/audit850450/kernel853351及CSR候选等待1909485再次/proc实证存活，OOM未增加；compact候选仅准备，尚未加入新的执行链。完整目标active，实际实卡入口仍待信息。

## 最新：恢复内核IO与日志可观测粒度核实（2026-10-25）

- data/derived/compact_native_runtime_io_observation_20261025_v1.json用精确cwd/cmd/starttick对kernel853351两次相隔20秒采样：75个cdata输入fd位置全部不变，read-character仅+525bytes，CPU+2002ticks。只证明窗口内未见持续大量输入读取；FD预读/缓存处理与HDL时钟推进不能区分，不推断事务完成。
- 原实际autotb.v逐copy-plan SHA核验不变，PROGRESS_TIMEOUT=10000000，进度循环只在约一千万次report_progress事件或完成时打印中间行；0/4不变本身不是时间停滞证据。results/compact_native_progress_observability_audit_20261025_v1.json冻结观测与原TB源码，明确CPU活跃也不是已推进的充分证明。无信号/debugger/仿真命令/源变更，不重启。完整目标active，原恢复与后续候选监督保持。

## 最新：真实43模块全部合法控制状态映射穷举核验（2026-10-25）

- 新scripts/check_hls_fsm_state_relation_v1.py在已冻结edit审核前提下，独立解析原/候选codebook与位译码，对真实43模块57780个合法状态逐项检查18500482个state/predicate组合，均满足onehot bit j == (binary_state == j)。独立核60926条命名next-state赋值目标合法、全部合法case标签完整、转移case文本逐byte完全相同、初始state1→0和命名复位/寄存器转移映射不变；results/hls_binary_fsm_state_relation_audit_20261025_v1.json保存完整统计及SHA。
- tests/test_hls_fsm_state_relation.py两项测试通过，含七种损坏codebook/predicate/target/condition/X-default/reset/initial拒绝。该结果只是在已核初始化合法状态不变量下的算术穷举和转移文本检查，不是全设计SMT形式等价或任意非法/部分未知state注入证明；7状态四态回归与完整IP事务验收仍各自独立。
- 没有修改已冻结执行入口/监督链，也未新开大型编译；原native owner844502/audit850450/kernel853351及候选等待监督1909485再次/proc实证存活。候选完整4tx/full44仍须等原native通过后实际执行，不用本次穷举冒充完整RTL结果。完整目标active。

## 最新：紧凑FSM完整full44执行/独立验收入口已准备并排在原恢复之后（2026-10-25）

- 新run_compressed_bus64_binary_fsm_rtl_v1.py/check_compressed_bus64_binary_fsm_rtl_v1.py保留原CSR0全部4tx/44指针/30模型/所有depth/4pages/9guard证据、原C literal oracle及4个946498280byte全快照。原copy与DPI模型转换先逐SHA核原样，再仅覆盖43个已核FSM候选模块；实际完整149文件须逐candidate SHA匹配，checker重新逐ledger核实际DUT映射，其余ROM/模型/fixtures不变。候选DUT显式changed、独立status/结果compressed_bus64_binary_fsm_rtl_audit_20261025_v1.json，不伪称原未改编码基线通过，不宣称native周期相等。
- 首次实际入口负测exit1：缺少compact_native_stack_recovery_rtl_audit_20261025_v2.json，在创建trial之前拒绝。binary_fsm_full44_prerequisites_v1.py严格核原native完整4快照/rtl_verified、候选edit报告、7状态1280样本机制回归、原编译失败报告及全部SHA。新tests/test_binary_fsm_full44_prerequisites.py三项通过，覆盖缺失/未通过/部分/空绑定/原证据变动/不全机制矩阵拒绝。
- 唯一supervise_binary_fsm_full44_v1.py owner1909485/exec75264已真实live等待原native独立audit owner850450的终态成功；无solver子进程、local compressed_batch_bus64_binary_fsm_rtl_v1不存在。原native先验收，随后独立128GiB rawfree准入才执行单次候选与独立审计；候选AS64GiB/core0/stack64MiB、16GiB运行保护，64GiB启动余量覆盖setup/cache，失败不自动重试/升cap。results/binary_fsm_full44_entry_preparation_20261025_v1.json冻结该准备/真实wait证据与所有新脚本SHA。
- 当前原恢复844502/850450/kernel853351再次/proc实证存活，0/4、未新增OOM；未启动新大型编译。完整目标active，实卡入口问题仍待用户信息。

## 最新：隔离二进制FSM候选与独立修改审核、7状态四态机制回归通过（2026-10-25）

- scripts/transform_hls_fsm_binary_v1.py已生成data/derived/hls_binary_fsm_candidate_20261025_v1：保持完整149个.v/.sv/.dat文件，43个可识别模块只改state常量/CS与NS位宽/无条件初始state/状态位译码，106文件（含未通过shape审核的top、所有AXI模型/ROM等）逐byte保留。所有原命名状态/转移及非编码文本保持，原DUT/活跃sim均未改。每模块ledger记录原span/old/new/编码映射与SHA。
- check_hls_fsm_binary_v1.py独立逐edit验证onehot i→binary i-1、初始state1→0、每decode用逻辑==而非===、所有原状态codebook与decode计数完整，重放后全文必须完全一致且完整文件集合不变；results/hls_binary_fsm_candidate_edit_audit_20261025_v1.json记录通过。这是已审核初始化合法状态不变量下的结构映射，不是通用形式等价证明，不覆盖注入非法内部状态。tests/test_hls_fsm_binary.py三测试通过，包含自洽hash但错误语义的常量/宽度/initial/decode ledger、遗漏与未列逻辑改动的拒绝。
- scripts/run_fsm_binary_four_state_regression_v1.py实际用安装2022.2 xvlog/xelab/xsim跑独立7状态机制样例，严格8GiB AS/core0/stack64MiB及90秒每阶段界限；原/候选仅wrapper模块名不同。reset/go/hold各0/1/X/Z全64组合×20cycle=1280样本，全部7状态覆盖、状态译码与四态datum逐采样===一致。results/fsm_binary_four_state_regression_20261025_v1.json通过，但明确非真实43模块/完整44指针内核验收，没有候选完整编译/综合/实卡或内存收益结论。
- 新两份报告绑定的149个原本机小文件共74829864bytes已归档到frozen_binary_fsm_candidate_evidence_20261025_v1，restore独立重读归档/原件、并再次核所有persistent/report绑定，results/frozen_binary_fsm_candidate_archive_audit_20261025_v1.json通过，原件保留。当前原恢复owner844502/audit850450/kernel853351再次/proc实证存活，未启动任何新大型编译；完整目标active。

## 最新：FSM原始读写/复位/转移结构严格审核，43模块可识别、1模块保留拒绝（2026-10-25）

- scripts/audit_hls_fsm_shape_v3.py对全部原始44个FSM逐源码SHA扫描：严格1-hot常量/编号连续、CS/NS宽度、唯一初始化/复位/时钟转移、所有位译码编号、所有whole-state访问，递归仅接受begin/if-else/命名next-state赋值的控制转移，并要求每合法状态分支覆盖且所有路径赋合法下一状态、default仍为X。43模块共57780状态符合识别形状；顶层1模块因初始化不是块首条语句拒绝，未绕过，任何未来候选须保留该原始模块或另证。
- results/hls_control_fsm_shape_audit_20261025_v3.json为最新严格形状审核，不是RTL编码等价证明。历史v1对初始化上下文不足、v2要求单独initial块过严均原样保留；v3仅接受initial块首条为无条件CS初始化，禁止条件初始化。tests/test_hls_fsm_shape.py两项测试含九种故障注入均通过（坏codebook/条件init/错误decode/缺case/越界目标/未全赋值/改变X默认/额外读/不同clock），results/hls_control_fsm_shape_tests_20261025_v1.json冻结原始测试输出与SHA。
- 没有生成或改写任何DUT RTL，没有新HLS综合/RTL编译；下一步仍须独立候选及编码映射、四态/reset/输出转移等价检查和fullscope原oracle。原native恢复kernel853351、owner844502/audit850450本轮仍实证存活、0/4，OOM计数不变；完整目标active。

## 最新：大型独热FSM清点与本机2022.2支持面核实（2026-10-25）

- results/hls_control_fsm_inventory_20261025_v1.json逐源SHA记录原失败global64 RTL的FSM参数，验证所有state编号连续且常量严格1<<(id-1)。sink_loop_worker有11398个状态、11398位独热编码、123736行RTL；这只是编译膨胀候选贡献因素，未隔离证明因果。
- data/derived/hls_fsm_encoding_support_probe_20261025_v1实际受限执行本机Vitis HLS2022.2的help config_rtl后exit，未open design/综合/仿真；peak约267MB，帮助没有-encoding/-fsm_encoding。官方2022.2 config_rtl页亦未列编码选项，不能照搬2026.1新选项。
- 后续若做紧凑编码，须独立candidate、完整合法状态映射、所有state读写fail-closed审核及reset/四态/转移输出等价证明，再跑原fullscope全部事务输出/C oracle；不能直接改原DUT并声称unchanged。当前没有RTL变更或新大型编译，native恢复853351仍活跃，完整目标active。

## 最新：完整范围验收快照v6记录失败与新恢复，而非旧等待态（2026-10-25）

- EXPERIMENT_STATUS_20261025_v6.json通过snapshot_experiment_completion_v6.py生成，重新验证所有继承绑定，并保持原9项要求的id/requirement文字逐项相同、8变体不变。新增8组已闭合失败/准备/启动证据，全部顶层SHA再验证；completion_proven与所有完整要求complete仍false。旧快照保留。
- 硬件状态明确full44 LLVM144GiB失败、原native guard-abort、恢复v2 active但未验收、full30及后续未执行、physical准备而已；保留WNS-0.316与DRC/method负结果。新本机XRT0devices进入DDR/HBM证据，clock公开接口/官方文档边界进入semantics，未降低或删除缺口。current status使用v4实证识别恢复owner844502/audit850450，原失败链不冒充等待。完整目标active，无新增大型编译。

## 最新：两个组件出现实际事务进展，恢复仿真继续（2026-10-25）

- data/derived/component_rtl_progress_observation_20261025_v2.json保存当前/proc身份与实际日志行：site_occupancy35/52（前次34）、retained_nodes2/37（前次1），route_tree1/50、retained_edges1/37。这些kernel均实证存活，但不是最终oracle审核通过；打印仿真时间按ps记录，不冒充cycles/板级速度。
- compact恢复v2 kernel853351/owner844502/audit850450仍运行，0/4；cgroup约156.6GiB，OOM计数仍2。未收到实卡入口，异步问题保留；没有启动新大型编译，完整目标active。

## 最新：实卡入口重新核实仍缺失，当前状态入口更新v4（2026-10-25）

- results/xrt_board_recheck_20261025_v3.json记录新的真实/opt/xilinx/xrt/bin/xbutil examine --format JSON --output执行：exit0、XRT2.14.354/2022.2、0 visible devices，/dev/dri缺失，当前/sys/bus/pci/devices也未见vendor10ee函数。仅证明本执行环境不可见，不能证明其他机器没有板卡；未安装驱动/改PCI绑定/启动远程或编程。初次命令遗漏JSON output参数被CLI拒绝后已按本机语法纠正。
- 已通过异步文本问题请求U280所在主机名/SSH配置名或作业入口，以推进实卡DDR/HBM、功耗、端到端测量。等待的是接入信息，不是重复申请授权；本地RTL不依赖该回答，继续运行。
- 新scripts/experiment_status_v4.py保持旧已冻结v1/v2/v3不改，实测正确显示compact恢复v2 owner844502/audit850450为live、batch19186/snapshot23681/post279139终态failed。该入口只读观察，不是通过证明。实际kernel853351继续0/4，完整目标active，禁止并发大型编译。

## 最新：恢复v2完成状态契约与提前验收拒绝已实测（2026-10-25）

- results/compact_native_recovery_v2_completion_contract_20261025_v1.json保存AST跨驱动/检查器核验：唯一complete stage与checker要求均independent_final_audit_pending。对当前真实running状态实际调用独立checker，明确拒绝Actual RTL/postcheck execution not complete且无验收报告创建；不会以进程存活代替通过。三份脚本SHA冻结，活跃脚本未改。
- 原owner844502/audit850450/kernel853351在/proc实时存活，当前0/4，kernel RSS约13.4GiB、cgroup约155GiB，OOM计数仍2。保留完整4tx/44指针和禁止并发大型编译的策略，完整目标active。

## 最新：已核实保护中止的原compact完整快照恢复v2已运行，禁止并发大型编译（2026-10-25）

- 在记录144GiB LLVM失败与原native guard abort后，明确决策复用原已编译快照恢复，不自动提高编译cap。新scripts/run_compact_native_stack_recovery_v2.py启动前强制核全incident文件SHA、原0/4 resource_abort=true及所有旧owner缺失；完整原snapshot/4tx/44指针/RO guards/所有depth/原C与完整快照oracle保留，AS96GiB/stack256MiB/core0/原128GiB准入及16GiB运行保护完全不变，无重新xelab。
- 恢复owner844502/exec59761已完成完整snapshot逐SHA复制并进入RTL，真实kernel853351；audit监督850450/exec38045在等待。results/compact_native_guard_recovery_launch_20261025_v2.json绑定所有新源/plan/独立实读kernel limits，实际AS96GiB/stack256MiB/core0已核；当前0/4，不是通过。不得在此完整solver活跃时再启动大型编译。
- 发现并在新v2修正旧v1驱动final stage independent_audit_pending与独立checker期待independent_final_audit_pending的契约不一致；旧source保留不改。v2增加自动runtime limit观察但主线程children遍历未及时发现由工具线程派生kernel，本轮用唯一精确cwd+cmd匹配独立捕获actual_runtime_limits.json并实读prlimit；不修改活跃脚本，后续需要时新版本再改善全线程发现。
- 现场定位原batch静态elaboration实际656732KB，巨大分配发生在后续codegeneration，最后可见sink_loop_worker模块、其RTL25797364bytes；未取得精确失败分配栈，不能宣称已证明哪个HDL过程单独致因。不可把相同完整AXI存储转换再次操作当既有编译问题已解决。完整目标active。

## 最新重大失败终态：full44 DPI 144GiB编译分配失败，原compact保护中止，后续链已停（2026-10-25）

- 新CSR batch v3 xelab30531已退出，不再活跃。完整elaborate.log实际LLVM ERROR: out of memory，receipt exit134、elapsed1541.72s、resource_admission_abort=false，time峰值149429976KiB约142.5GiB，实际AS144GiB；符合进程地址空间不足，但未定位精确失败分配。cgroup oom_kill仍2、未增加，不能称kernel OOM kill。未完成xelab、未执行full44 RTL事务。
- 同时原compact栈恢复83892/owner72430也已终止，不再活跃：rtl.receipt elapsed10900.30s/exit-15/resource_abort=true，原16GiB rawfree保护触发，仍0/4。该保护只证明阈值被穿越，不能单独归因哪个进程；原大compiled snapshot/所有输入仍保留。final audit180564失败，非栈再次SIGSEGV证据。
- batch监督19186失败；snapshot23681因Full44 prerequisite did not pass失败；post-snapshot279139因Original full30 chain did not pass失败。所有这些owner和solver均/proc不存在，后两项未启动实际solver，不能再说本链仍等待或运行。未重启/提高上限/自动重试。
- data/derived/full_rtl_stricter_cap_incident_20261025_v1已复制19份最终log/state/plan/receipt逐SHA验证，observation记录cgroup事件，results/full_rtl_stricter_cap_incident_20261025_v1.json冻结20绑定。实际失败证明144GiB不足；AS+24GiB启动余量没有覆盖后续setup/cache及其他活动变化，后续恢复须完整串行并重新核总内存预算，不盲目提升。原160GiB也尚无充分性证明。
- AMD官方2022.2 UG900 xelab页面已查；说明elaborate包含生成/链接可执行snapshot，未取得该LLVM分配错误的已核实修复，不虚构AR或新版命令。其余A组件XSim1787486/3001920/459268/2216832本轮/proc实证仍存活，未修改B会话。完整目标active，下一步先分析资源占用与可保留完整范围的恢复策略；不得把失败标为通过。

## 最新：full30之后的compact配对与read分级RTL已接入唯一串行监督链（2026-10-25）

- scripts/supervise_post_snapshot_rtl_v1.py已真实启动owner279139/exec53370，当前waiting_existing_full30_snapshot_independent_acceptance，实读/proc命令与无child核实；绑定原snapshot监督23681身份和plan，等其终态/独立accepted报告及原search/full44/full30全部SHA通过后才推进。data/derived/post_snapshot_rtl_supervision_20261025_v1保存唯一owner与完整冻结jobs；results/post_snapshot_rtl_serial_setup_audit_20261025_v1.json审核当前无下游solver/trial/结果文件，非仅计划队列。
- 首项compact full44使用新run/check_compressed_compact_bus64_dpi_rtl_v2.py，逐源码验证仅AS160→144GiB、准入184→168GiB、独立trial v1→v2改变，其余功能代码完全相同；原4tx/44指针/30模型/所有depth/4pages/guard/C与完整快照oracle保持。目标results/compressed_compact_bus64_dpi_rtl_audit_20261025_v1.json与已准备physical gate一致。
- compact独立通过后第二项再启动已冻结read控制候选full2tx入口/检查器，原AS64GiB/152GiB准入，目标search_read_control_staging_rtl_audit_20261025_v1.json。各项单次执行+独立审核，任何失败终止该链、保存证据，无自动重试/并发solver/物理实现。原CSR编译30531和compact83892仍活跃，OOM事件未新增。完整目标active。

## 最新：compact global64配对物理输入完整冻结（2026-10-25）

- scripts/prepare_compact_bus64_physical_v1.py已实际生成data/derived/compressed_batch_compact_bus64_physical_20261025_v1/compact，完整118个RTL/ROM逐HLS独立审核绑定SHA匹配并复制后再读核验，RTL/ROM集合完全相同；run_flow.tcl与clock.xdc逐byte等于原集成CSR物理流程，part/5ns/1.35ns/2threads不变。results/compressed_compact_bus64_physical_preparation_20261025_v1.json保存冻结元数据。
- 明确仅inputs prepared，execution_entry_prepared=false/physical_executed=false；未来执行入口必须先核原search/full44 CSR/full30 snapshot及本compact完整DPI四accepted报告及所有SHA，保留独立184GiB物理准入，不能把仿真144GiB策略套用到物理流程。未创建Vivado会话。
- 现新CSR batch xelab30531已实际进入Starting static elaboration/Pass Through NonSizing Optimizer，活跃RSS约463124KiB，原compact83892继续；尚无新RTL验收。完整目标active。

## 最新：严格资源版本功能范围独立源码审核通过（2026-10-25）

- scripts/audit_stricter_rtl_driver_scope_v1.py逐字比较batch driver/checker v2→v3及snapshot driver/checker v1→v2四对源码，仅允许AS160→144GiB、准入184→168GiB和独立trial路径替换；其余功能代码完全相同，24GiB启动余量及16GiB运行门保持。results/stricter_rtl_driver_scope_audit_20261025_v1.json冻结两版全部SHA，未改活跃脚本。此审核不证明新上限充分或RTL通过。
- 快照完整输出oracle两项回归实际通过（test_snapshot_dpi_output_oracle.py），覆盖binary全部word/可选EOF和文本framing/value/unknown拒绝。真实xelab30531及wrapper30429在新batch owner19254之下活跃，/proc实读全部AS144GiB；snapshot23681等待batch独立验收，compact83892继续。完整目标active。

## 最新重大推进：完整44指针批处理已真实启动，严格144GiB资源交接（2026-10-25）

- 原184GiB门长期未满足，缓存两类提示均无效。本轮新版本把每进程AS从160收紧到144GiB，同时准入184→168GiB，保留相同24GiB启动余量、16GiB运行rawfree保护、core0/stack64MiB，全部原4tx/44指针/30模型/原depth/4pages/只读guards及完整C/快照oracle不变。160上限并无已测充分性保证，144也未保证成功；若不足保留失败、不自动升限重试。
- 严格核旧snapshot3465022与batch2747433均纯等待/无child、各冻结plan全部SHA未变、所有原/新trial与最终报告不存在后，用pidfd仅终止这两个等待监督进程；原compact XSim83892仍继续。旧source/state/plan保留不改，terminal sidecar位于data/derived/full_rtl_wait_only_resource_handoff_20261025_v1，旧running状态仅历史。
- 新supervise_compressed_bus64_dpi_rtl_v6.py owner19186/exec18260已过真实168GiB门，driver run_compressed_bus64_dpi_rtl_v3.py owner19254，local compressed_batch_bus64_dpi_rtl_v3已创建、xsc完成并真实elaborate。new_chain_observation.json从4个live子进程RLIMIT实读核AS144GiB/stack64MiB/core0，非仅计划值。
- 新snapshot监督v2 owner23681/exec97674等待同一batch独立通过，未来driver/checker v2同144GiB+24余量、原30tx不变，目标两份结果路径和accepted状态保持兼容，但仍未通过。scripts/experiment_status_v3.py新版本实测正确识别这三owner；旧v1/v2状态源码不改。replacement.json冻结7份新脚本SHA和owners。完整目标active，不把elaboration当RTL成功。

## 最新：官方UG572公开时钟能力核对（2026-10-25）

- results/clock_official_documentation_review_20261025_v1.json记录已实际读取的AMD官方UG572两页面、revision1.11/2025-05-29及本机接口审核SHA。官方描述leaf门控和SYNC/ASYNC，并明确leaf资源仅信息性文档、不可由用户在Vivado直接实例化/放置。故不能用直接primitive放置代替隐式pseudo路由配置取证。
- 该文档版本晚于本机2022.2，不推断新命令可用；本轮未取得实际LCLK_TEST_DELAY编码、常量反相或共享所有权，完整clock模型依旧未完成。不把检索未找到当硬件不存在，不扩充已验证14实例模型。原运行链维持，完整目标active。

## 最新：时钟公开仿真模型接口范围审核（2026-10-25）

- scripts/audit_clock_model_surface_v1.py实际读取安装2022.2 BUFCE_ROW/LEAF模块header，核参数仅LOC/CE_TYPE/IS_CE_INVERTED/IS_I_INVERTED，端口仅O/CE/I；重新核验原物理属性、扩展捕获及原语行为三报告的全部文件绑定，确认真实捕获存在LCLK_TEST_DELAY/CONFIG.DELAY。results/clock_public_model_surface_audit_20261025_v1.json保存逐SHA证据。
- 明确这两种公开接口无delay/test控制入口，重复扩大原有参数测试不能证明物理leaf delay/test语义；不是硬件不存在该功能的证明。下一步必须取得器件配置层语义、实际常量/反相及共享固定所有权证据；不扩充14实例路由模型、不标完整时钟语义通过。无新Vivado/仿真进程，原83892/2747433/3465022已实时确认存活。完整目标active。

## 最新：本机闭合原文件缓存试验未解决准入（2026-10-25）

- full44_batch_closed_original_cache_hint_20261025_v1.json记录162个来自较早三份冻结归档、逐SHA核验且每步排除/proc打开路径的本机原文件提示，current134922891264→134893785088，仅-29106176bytes；不是可用的准入改善。文件与184GiB门槛均保留。原件与归档副本两种提示均已测，不再重复此策略。
- full44_batch_post_cache_observation_20261025_v1.json记录原83892/2747433/3465022当前/proc命令/启动tick/状态及cgroup事件、实际batch等待态；这是verified wait，非完成证明。后续需实际资源释放或有实测依据的资源策略，完整目标active。

## 最新：完整范围验收快照v5及原项目入口检查通过（2026-10-25）

- EXPERIMENT_STATUS_20261025_v5.json保留原9项要求/8变体，验证全部继承绑定后加入10项独立范围证据：原search完整DPI及归档、read分级CPU/HLS/full setup/full44 CPU/physical准备/DPI准备、compact全局64 DPI模型及入口准备。旧v4不改；全部顶层绑定再次核验，completion_proven仍false，未把prepared标为RTL通过。
- scripts/run.py check与smoke实际通过，plan实际生成results/plan_20261025T111156.515064Z.json；smoke为results/smoke_20261025T111156.493226Z.json。其范围仍仅项目配置和CPU合成例，不支持板级性能声明。完整目标active，原live链继续。

## 最新：compact global64完整DPI模型审核和执行入口准备（2026-10-25）

- scripts/preflight_compressed_compact_bus64_dpi_models_v1.py针对自身guarded setup转换全部30模型，独立check_compressed_bus64_dpi_storage_edits_v1.py逐edit ledger重放通过，results/compressed_compact_bus64_dpi_storage_preflight_audit_20261025_v1.json记录120 storage declarations/840 writes/100 low16/240 packed-bit/640 word-read edits。所有原depth和4pages不变，声明总payload3785988768bytes；这不是RTL通过。初次复用CSR路径时setup摘要类型不匹配、在创建out之前拒绝；核compact实际绑定setup.json后修正，未改原CSR入口。
- 新run_compressed_compact_bus64_dpi_rtl_v1.py/check_compressed_compact_bus64_dpi_rtl_v1.py保留mode1完整4tx/44指针/30模型/7只读guard及原C oracle、4个946498280byte快照核验，160GiB AS/core0/184GiB准入/16GiB运行门。执行前严格要求原search/full44 CSR/full30 snapshot三审核全SHA通过，未新增等待进程。语法检查及实际missing CSR prerequisite负测exit1通过，trial目录未创建；results/compressed_compact_bus64_dpi_entry_preparation_20261025_v1.json绑定准备证据。
- 原compact XSim83892、batch监督2747433、snapshot监督3465022已实时核实存活；内存仍未准入。完整目标active。

## 最新：归档缓存提示未改善full44准入（2026-10-25）

- data/derived/full44_batch_closed_archive_cache_hint_20261025_v2.json记录189个已闭合归档大文件逐SHA复核后文件级DONTNEED提示，排除当时/proc可读打开路径，不删除文件、不改变184GiB门槛。cgroup current实际131234443264→133606957056 bytes（+2372513792），包含并发变化，不能声称已释放内存或准入；不继续重复相同缓存操作。
- 实时原监督2747433/3465022和compact XSim83892仍存活，compact日志仍0/4；后续应等待实际释放或依据实测峰值重新论证资源策略，不能把CPU活跃当事务完成，不能重复启动原batch。

## 最新：search DPI 最终闭合证据持久归档（2026-10-25）

- frozen_search_dpi_final_evidence_20261025_v1 保存最终 v3 审核绑定的155个本机文件，共2473152519 bytes；归档与原件独立全量SHA复核通过，全部报告及持久绑定再次核验。results/frozen_search_dpi_final_archive_audit_20261025_v1.json记录证据，原件保留。这是证据持久化，不是新增RTL试验。原batch监督2747433与snapshot监督3465022、compact XSim83892已实时核实仍存活；完整目标仍未完成。

## 最新重大闭合：search DPI v7完整周期/所有输出/原C oracle及独立审核通过（2026-10-25）

- 原DPI XSim78596/owner4073029及supervisor2747344现已正常结束，不再活跃。results/search_axi_dpi_replay_audit_20261025_v3.json已存在，status full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified，655bindings，7models/各4pages/原全depth/2tx/5完整输出文件，实际cycles[2132461,12404]逐项等于原native baseline、所有输出bytes一致、原PC oracle通过；full-dut replay验证不是仅小单元。实际RTL日志完整2/2，elapsed2:10:09，CPU7810030ms。
- 首次观察已写两行perf但仍导出大输出；采样准备时实际kernel恰已退出，/proc缺失导致只留下data/derived/search_axi_dpi_output_export_observation_20261025_v1/performance_observed.xml，未发布partial report；随后核原正常终态和最终独立audit，不能再说两原XSim均活跃。只剩compact栈恢复83892继续full4tx。
- 原batch supervisor2747433/exec66927已自动进入waiting_cgroup_admission_for_full44_batch，snapshot3465022仍等full44 batch接受。原184GiB rawfree门尚未达到，未启动local compressed_batch_bus64_dpi_rtl_v2。两个新file-scoped cachehint记录为data/derived/full44_batch_admission_cache_hint_20261025_v1.json（130 closed files/observed delta-16956268544）及additional...json（34files/observed+345956352），原件/active FD/全局设置/门槛均不改；不能把hint成功当实际准入。
- 当前memory.stat anon约36.5GB/file92.5GB/shmem81920，inactive_file约30.1GB、dirty很小；实际rawfree约192GB，仍差原184GiB(197.568GB)门约5GB。不得重复search replay或重复提交batch；完整目标active。

## 最新：read分级候选六份闭合证据已持久归档并独立核验（2026-10-25）

- data/derived/frozen_read_control_staging_evidence_20261025_v1归档隔离CPU、完整HLS、full2tx setup、full44双模式CPU逐bytes等价、物理输入准备、DPI入口准备六报告的574个精确local绑定文件，共17066160421bytes。原件保留，未复制活跃无绑定日志/缓存。
- archive driver成功后独立restore(relink=False)重读归档及原件全SHA，复核全部六报告local覆盖与persistent绑定，results/frozen_read_control_staging_archive_audit_20261025_v1.json记录通过。该报告仅持久性，不是新RTL/physical结果。原XSim78596/83892复查活跃，完整目标active。

## 最新：分级候选完整DPI执行/独立审核入口已准备，原链验收缺失时无副作用拒绝（2026-10-25）

- scripts/run_search_read_control_staging_dpi_rtl_v1.py与check_search_read_control_staging_dpi_rtl_v1.py已准备。严格先复用validate_prerequisites核原search完整DPI周期/全输出等价、原full44 batch和full30 snapshot三项accepted报告与全部SHA，保持原链优先；当前第一项缺失，真实负测exit1且local search_read_control_staging_dpi_rtl_v1未创建，未新增wait/编译/仿真进程。
- 将从candidate full2tx setup完整复制/7模型按原transform_v2存储ledger替换，DUT/ROM/TV不变，相同AS64GiB/core0/stack64MiB/152GiB准入/16GiB运行门，CPU125。候选不同于旧DUT，独立审核仍核精确storage ledger、完整RTL/ROM集、原C literal oracle和每份完整输出与原已通过baseline逐bytes一致，但新2项positivecycles仅核实际完整，不要求旧2132461/12404周期相等。
- results/search_read_control_staging_dpi_entry_preparation_20261025_v1.json是入口/负测准备证据，不是RTL通过。完成候选后输出目标仍results/search_read_control_staging_rtl_audit_20261025_v1.json以衔接物理gate；当前未运行。原XSim78596/83892继续，完整目标active。

## 最新：分级候选物理输入已冻结，严格等待候选RTL审核（2026-10-25）

- scripts/prepare_search_read_control_staging_physical_v2.py已准备data/derived/search_read_control_staging_physical_20261025_v2/csr，60个完整RTL/ROM逐HLS审核绑定SHA一致，run_flow.tcl/clock.xdc与原packet64物理流程逐byte相同；5ns/1.35ns/part/2threads保持，plan明确execution_gate=results/search_read_control_staging_rtl_audit_20261025_v1.json且当前缺失、未启动物理实现。results/search_read_control_staging_physical_preparation_20261025_v1.json保存独立复核。
- v1准备误以helper文件无top前缀，复制后在模块存在检查被拒绝；核真实search_kernel_top_valid_decoded_record.v后新v2目录成功，旧v1partial保留，非DUT失败，无综合/实现执行。原两XSim78596/83892仍运行，完整目标active。

## 最新：read分级候选完整44端口两模式CPU与原基线8快照逐bytes完全一致（2026-10-25）

- scripts/test_read_control_staging_full44_cpu_v1.py owner2836571/exec65959实际完成CSR0与compact1两组ASan+UBSan编译/执行；只替换一header，完整原TB/44ports/各4tx/所有声明depth不变。local read_control_staging_full44_cpu_v1保存8快照与trace。
- 先复用check_compressed_batch_rtl_tb_cpu.py审核完整snapshot结构/各port哈希/只读fixtures/trace/result与错误拒绝，再check_read_control_staging_full44_equivalence_v1.py独立流式比较每一byte：8x946498280=7571986240bytes全部等于原frozen CPU reference，trace8份亦完全一致；results/read_control_staging_full44_cpu_equivalence_20261025_v1.json记录通过。完整容量但原逻辑4-node合成用例，不声称生产真实流量或硬件通过。
- 未并发新增大型native elaboration（原baseline无可用compile峰值统计，避免无据96GiB尝试）；候选full2tx setup已准备、HLS真实2cycle/II1已测，仍需候选RTL与postroute。原XSim78596/83892继续活跃，完整目标active。

## 最新：read分级完整cosim setup及独立全C向量审核通过，未执行RTL（2026-10-25）

- scripts/prepare_search_read_control_staging_cosim_v1.py owner2695998/exec25757正常complete，local search_read_control_staging_cosim_setup_v1/project search_read_control_staging_cosim_project_v1，HLS45.37s复用原candidate综合并csim/cosim -setup，未重新综合/未跑xelab。两处原C oracle均完整2tx/fullworkspace，实际DUT RTL和综合副本逐SHA保持。
- check_search_read_control_staging_setup_v1.py独立核execution_plan输入全SHA、唯一setup命令成功及两组literal oracle；全部27个C TV文件与原已通过CSR packet64 baseline逐字节SHA相等，7模型width/depth/各4pages精确相同，results/search_read_control_staging_full_depth_setup_audit_20261025_v1.json记录通过。内部周期可能不同，未声称RTL/新周期等价。
- 原XSim78596/83892复查活跃、尚无事务完成记录；完整目标active。

## 最新：read控制分级完整搜索核HLS与独立审核完成，实际helper2cycle/II1（2026-10-25）

- owner2475719/exec99060与supervisor2562999/exec49349正常complete，实际HLS316.73s/peakallocated2.220GB，results/search_read_control_staging_hls_audit_20261025_v1.json含140bindings。原2tx fullworkspace C oracle/源集仅一header差异/接口宽度/5ns与1.35ns约束保持。
- valid_decoded_record_csynth.xml实际best/avg/worst latency均2cycle、II1、PipelineDepth3，helper staging achieved；完整核LUT224149/FF138106/DSP77/BRAM69/URAM3，相比packet64 CSR baseline多14525LUT/7437FF，estimatedclock仍3.65ns（delta0）。分级实现不等于整体收益或postroute closure，新增代价如实保留。
- 该candidate仍需完整RTL及物理实现实测，不能沿用旧DUT周期；原canonical/活跃DUT未改，原XSim78596/83892继续运行。完整目标active。

## 最新：完整read分级候选独立HLS审核入口与自动监督已接好（2026-10-25）

- scripts/check_search_read_control_staging_hls_v1.py核完整source集仅一header变更、原2tx literal C oracle/fullworkspace marker、实际flow/版本/part/时钟、7memory widths与packet64原基线一致，读取valid_decoded_record实际module XML latency/II。未达到min2/II1时报告staging_not_confirmed，不把pragma当成功；新内部周期不可复用旧RTL周期。对当前未完成实际负测拒绝，无success文件。
- supervisor（scripts/supervise_search_read_control_staging_hls_v1.py，exec49349，state在local search_read_control_staging_hls_v1/audit_supervisor）冻结当前owner2475719身份和checker SHA，只等该次完整HLS成功后审核一次，目标results/search_read_control_staging_hls_audit_20261025_v1.json；未重复HLS。原两XSim78596/83892继续活跃。完整目标active。

## 最新：read控制分级候选完整搜索核HLS已启动（2026-10-25）

- scripts/search_read_control_staging_hls_v1.py owner2475719/exec99060，local search_read_control_staging_hls_v1及project search_read_control_staging_hls_project_v1；从原CSR packet64 full-workspace source克隆，文件集差异严格只有search_label_records.hpp，其余top/TB/pragma64/flow/5ns/1.35ns/2tx保持，先验隔离CPU10万read+10万path proof精确SHA复验。
- 实际完整Csim命令已运行，综合正在原2022.2流程继续；AS64GiB/core0/stack64MiB/file8GiB、128GiBfree准入/16GiB运行门。此候选改变内部流水线，后续周期不能冒充原基线周期等价；必须新的完整Csim/合成分级实现/RTL/physical证据，不宣称收益。
- 尚未最终独立audit；原DPI XSim78596与compact栈恢复83892继续活跃。完整目标active。

## 最新候选：read_r有效性判断函数分级，隔离CPU差分与sanitizer通过（2026-10-25）

- hardware/vitis/search_control_staging_v1/search_label_records.hpp保留原读取/宽度检查/ABI，把解码后root/cost/parent条件提取到独立标量valid_decoded_record，function-scope INLINE off/PIPELINE II=1/LATENCY min=2；不在内存读取循环上pipeline、不改原canonical头或活跃DUT。实际HLS寄存器/latency未测，不保证解决CE路径。
- test_read_control.cpp用原namespace对照，20000随机/故障case，100000 reads+100000 validate_path结果/out/edges完全一致，任意父顺序、invalid count/index/field/root/cost/self-parent覆盖，输入保持；g++ ASan+UBSan通过。results/search_read_control_staging_cpu_20261025_v1.json绑定源码/可执行/log，测试capacity64，仅隔离CPU语义，仍须完整workspace/kernel CPU/HLS/RTL/physical验证。
- 原XSim78596/83892复查继续活跃，完整目标active。

## 最新诊断：physopt后最差路径仍为read_r控制链，未实施源码改动（2026-10-25）

- results/search_packet64_physopt_path_diagnosis_20261025_v1.json绑定最终-0.316ns报告、原生成RTL（原baseline绑定SHA复验）及LabelRecords源码。Source cursor_2_reg_482_reg[17]/C→n_fu_76_reg[4]/CE；3.863ns=logic1.060+route2.803ns（72.559%），12levels/5CARRY8，实际控制net扇出231。与之前cursor CE路径相比终点有变，不能照搬旧终点。
- 后续候选是分离read_r有效性/返回状态到计数CE的控制链；当前只诊断、尚未实现，所有invalid/parent-chain/完整容量条件需保持，必须新的CPU/HLS/RTL/physical实证，不推断收益。首次新脚本误指向旧目标被refuse-overwrite拒绝后更正新结果名，旧结果未动。原两XSim78596/83892继续活跃。完整目标active。

## 最新资源准备：仅已归档闭合local大文件的缓存提示降低实际占用（2026-10-25）

- 冷归档副本提示此前无即时效果；随后针对同一已独立核验manifest的local原件，仅>=32MiB且不在当前XSim78596/83892的open FD集合内的41文件（18453598736bytes），逐个SHA重新匹配再POSIX_FADV_DONTNEED。data/derived/frozen_compact_global64_evidence_20261025_v1/closed_source_cache_hint.json记录实际CG delta-18488438784bytes（含其他活进程变化，不作性能归因）。
- 未删除/改写文件、不改global cache/cgroup/184GiB原准入门，当前仿真input/output保持，两个原XSim继续活跃。该动作仅改善后续完整batch准入余量，不代替search语义审核。完整目标active。

## 最新验收快照：EXPERIMENT_STATUS_20261025_v4.json（2026-10-25）

- scripts/snapshot_experiment_completion_v4.py先复验v3全部绑定SHA，再保留原9requirements/8variants，纳入8项新闭合证据：compact global64 HLS/Csim/setup/guardedcopy、成对比较、packet64后布线优化负结果、持久归档与新结果图。全部complete仍false；元数据快照不替代各独立artifact审核。
- 当前scripts/experiment_status_v2.py已被v4绑定，后续扩展须新版本，不再原地改写。原两XSim78596/83892复查活跃。完整目标active。

## 最新：已完成CSR/compact成对HLS和physopt后时序结果图（2026-10-25）

- scripts/plot_csr_compact_and_physopt_v1.py输出results/figures/csr_compact_and_physopt_20261025_v1，两图各PNG/SVG/PDF、2CSV、caption、依赖和source/artifact SHA manifest；全部哈希、4HLS+3postroute行核验，两个PNG已实际view_image检查。
- 集成full44 HLS图分别列default/global64的CSR与compact资源/估计时钟，仍miss3.65ns；独立search-only CSR后布线图列-1.389/-0.382/-0.316ns，全部miss时序/DRC/method门。未跨集成范围比资源，未声称board加速。原两XSim78596/83892继续。完整目标active。

## 最新：已完成packet64物理会话释放，31冻结文件不变（2026-10-25）

- 经MCP再确认idle/code0/queue0，PID1156863的startticks/command/cwd与runtime_admission精确一致后，仅pidfd SIGTERM该已完成自有会话；实际退出，关闭前后原31项audit文件SHA全部一致。results/idle_packet64_physopt_release_audit_20261025_v1.json及data/derived/idle_packet64_physopt_release_20261025_v1保存证据，DCP/报告/日志全保留；session vivado-20261025-092245-a862e421现不可复用，新查询需新session读保存DCP。B和原XSim未触。
- 另只对已独立验证的1594个compact global64归档文件发POSIX_FADV_DONTNEED提示，cold_archive_cache_hint.json保存observed CG delta+389120bytes（无即时下降，不宣称已释放归档缓存）。不删文件、不改global cache/cgroup。当前memory.stat约anon42GB/file93GB，多数余量涉及文件缓存；后续184GiB原门仍保持，不能把hint当准入。
- 原XSim78596/83892继续活跃；完整目标active。

## 最新：packet64物理优化完成并独立审核，WNS改善66ps但质量门仍未通过（2026-10-25）

- session vivado-20261025-092245-a862e421/PID1156863原唯一source正常terminal code0/1336.549s/queue0，flow complete/physopt_complete_pending_independent_audit；memoryguard1181611/exec10012正常flow_terminal，未resource_abort。完整真实terminal_observation.json/mcp_history.json及两raw wrapper存原bundle；历史原文完整，首个保存因单参数过长被系统拒绝后分块写入，未裁剪/改写。
- results/search_packet64_physopt_audit_20261025_v1.json独立完成（31bindings），checker退出1是实际quality_gates_not_met而不是审核崩溃。原active XDC精确一致、DCP ZIP完整、来源/唯一命令历史核实；182762/182762全route、errors0，资源LUT81235/FF108764/DSP77/RAMB36218/RAMB1815全部不变。最终WNS -0.382→-0.316ns(+0.066ns)，TNS -199.829→-186.266，失败端点2151→2098；仍未时序闭合。DRC87、method1001(TIMING-18 1000/TIMING-44 1)不清零，未waive。
- MCP todos3/3完成表示试验和审核完成，不是设计通过。专用session当前idle，原log已被最终report绑定；不要再向该session发新Tcl改写冻结log。原search XSim78596及compact恢复83892继续，完整目标active。

## 最新物理调用交接：cell5874已收running handoff，后续只poll同session（2026-10-25）

- functions.wait(cell5874)已正常返回MCP 300s running handoff，原响应存data/derived/search_packet64_physopt_20261025_v1/mcp_source_handoff.json；cell不再活跃，不继续wait该旧cell。实际source仍在session vivado-20261025-092245-a862e421/PID1156863执行，最近MCPstatus is_command_running=true/queue0，aggressive_fanout/关键路径处理，多条net尚无WNS改善。只能间隔后vivado_status，不重复source或向该session发Tcl。
- 原两个XSim78596/83892复查活跃、CPU增长、无事务完成记录；OOMkill仍2。完整目标active。

## 最新：compact global64闭合证据已全量持久归档并独立复核（2026-10-25）

- data/derived/frozen_compact_global64_evidence_20261025_v1归档HLS审核/full44 cosim setup/CSR-compact受控比较三份报告的1594个精确local绑定文件，共19136542076bytes；原件保留，未复制活跃无绑定日志/缓存。archive driver成功后另用restore_frozen_local_evidence.restore(relink=False)重读归档及原件全部SHA，核三报告local完整覆盖及persistent绑定，results/frozen_compact_global64_archive_audit_20261025_v1.json记录通过。
- 原search XSim78596、compact恢复83892继续活跃，packet64物理session PID1156863仍aggressive_fanout，原source cell5874未收终态，不重复提交。完整目标active。

## 最新：packet64后布线优化已在新MCP会话实际运行（2026-10-25）

- session vivado-20261025-092245-a862e421/PID1156863，新Tcl无GUI，cwd data/derived/search_packet64_physopt_20261025_v1；MCP先list确认只有两个B会话仍在，未触B。原冻结plan/DCP/Tcl全部SHA复验；参考原packet64physical日志peak68167.148MB，在当前rawfree>=184GiB后启动。runtime_admission.json保存真实AS96GiB/core0/stack64MiB的/proc limits，mcp_start.json保存原工具返回。
- 唯一source调用仍为functions.exec cell5874（尚待functions.wait取原返回，不能重复source）。实际state running/aggressive_fanout，已重开baseline WNS复验并签出Implementation/xcu280许可证；仅运行原prepared两命令AggressiveFanoutOpt与Explore/tns_cleanup，未改原DUT/XDC/5ns/1.35ns约束。
- scripts/guard_packet64_physopt_memory_v1.py owner1181611/exec10012验证startticks+command，仅16GiB rawfree不足才pidfd终止该自有物理PID并保存resource_abort，绝不触其他任务。最终使用既有check_packet64_physopt_v1.py和真实MCP terminal/history独立审核，尚未完成，不宣称改善/时序通过。
- 原search XSim78596及compact栈恢复83892继续活跃。完整目标active。

## 最新：状态入口版本化，恢复旧验收快照的精确源码绑定（2026-10-25）

- 当前完整本地状态用python3 scripts/experiment_status_v2.py（含新compact global64 cosim setup和audit）；原scripts/experiment_status.py两条后加cosim展示导致EXPERIMENT_STATUS_20261025_v3.json绑定SHA偏差，现已重建并验证SHA精确匹配后原子恢复，所有新增展示完整保留在v2。results/status_source_binding_recovery_20261025_v1.json记录前向版本和旧SHA；未改实验/输入/原结果，4项status回归通过。
- 两原XSim78596/83892复查活跃；compact global64 HLS/Csim/setup及独立审核complete，新global64guarded副本ready但未执行。完整目标active。

## 最新：compact global64 setup独立审核完成，7RO guard执行副本就绪但未编译（2026-10-25）

- results/compressed_batch_compact_bus64_full_depth_cosim_setup_20261025_v1.json已完成（984bindings、30models/44pointers/4tx、55完整memory vectors），supervisor947807/exec77060正常完成。
- prepare_compressed_batch_compact_bus64_guarded_rtl.py新copy local compressed_batch_compact_bus64_rtl_guarded_v1已ready_for_elaboration；未启动xelab。results/compressed_batch_compact_bus64_guarded_setup_audit_20261025_v1.json独立核7个RO bundle完整alloc覆盖，30models与全部RTL/ROM文件集一致，只有7处纯追加guard、移除guard后原文精确一致，其余bytes保持。不是DUT执行通过。
- 原search DPI78596及compact stack恢复83892继续运行；不重复启动它们，完整目标active。

## 最新：compact global64完整cosim setup已生成，独立三项审核进行中（2026-10-25）

- scripts/prepare_compressed_batch_compact_bus64_cosim.py owner863872/exec6920已complete；local compressed_batch_compact_bus64_cosim_setup与project compressed_batch_compact_bus64_cosim_project。复用原综合逐SHA克隆、full44 TB/mode1/full4tx/全部depth不变，实际csim+cosim -setup exit0/141.41s，4份完整快照逐bytes相等；未重新综合、未跑新xelab或新RTL。
- supervisor947807/exec77060（supervise_compact_bus64_cosim_setup_v1.py）固定该次setup与三个checker，正在独立核30模型容量、44pointer disjoint allocation、每份memory TV完整4tx，最后核全部绑定再输出results/compressed_batch_compact_bus64_full_depth_cosim_setup_20261025_v1.json。仅setup验收，不是功能RTL通过。原search XSim78596与compact stack恢复83892继续，完整目标active。

## 最新：compact global64 HLS与独立审核完成，CSR/compact同配置比较已闭合（2026-10-25）

- owner256536/exec95399 HLS正常complete，supervisor268850/exec45985独立full44 Csim与综合audit complete。results/compressed_batch_compact_bus64_synthesis_review_20261025_v1.json含1129bindings、30AXI/44pointers；LUT447391/FF328607/DSP93/BRAM69/URAM3，estimated3.715ns，仍超3.65ns有效预算0.065ns。此前mode1四完整快照/trace通过保持，未执行该新global64 DUT的RTL/板卡。
- results/compressed_batch_csr_compact_global64_comparison_20261025_v1.json核两模式全部source file集/SHA完全相同、Tcl仅两SEARCH_GRAPH_MODE flag不同；compact相对CSR（433034LUT/321329FF）多14357LUT/7278FF，时钟相同。较原compact1937259LUT显著下降仍仅HLS估计，不作实际加速/平台fit结论。
- 原search DPI XSim78596与compact stack恢复83892继续RTL；完整目标active，后续full44batch和full30snapshot等原独立search接受。

## 最新：compact global64完整Csim独立早期审核通过（2026-10-25）

- results/compressed_batch_compact_bus64_early_full44_csim_20261025_v1.json由现有check_compressed_batch_compact_bus64_csim.audit()直接审核已关闭Csim输出后原子保存：4份各946498280bytes/总3785993120bytes完整44端口快照与mode1 CPU逐SHA相等，4条trace完全一致，reset-state和错误trace拒绝检查保持；绑定闭合csim.log，不冻结仍增长综合log。
- 这是实际Csim独立通过，仍不是RTL/平台通过。canonical final Csim报告留给原supervisor268850在HLS成功后生成并综合独立审核，早期报告不覆盖其目标；原综合owner256536与两个RTL XSim78596/83892继续。

## 最新：compact global64 HLS已启动，完整Csim命令完成、综合继续（2026-10-25）

- 当前入口scripts/compressed_batch_compact_bus64_hls_v3.py，owner256536/exec95399，local compressed_batch_compact_bus64_hls。取消v2人为串行DPI先决要求：HLS只需已完成full44 CPU证据，DPI语义证明仍是RTL链的门。此前CSR同配置日志峰值allocated5.219GB，当前CG约77GiB/300GiB，采用128GiBfree准入、AS64GiB/core0/单文件8GiB/运行16GiBfree保护，独立CPU123，不启动新xelab。
- canonical源码/full44 TB/4tx/全部depth保持，Tcl严格仅SEARCH_GRAPH_MODE与CSR global64不同。csim_design已exit0并唯一CSIM_COMPLETE，csynth_design进行中；独立full44快照和最终综合审核尚未出具，不能把命令完成当审核通过。
- supervisor268850/exec45985（scripts/supervise_compact_bus64_hls_v1.py）冻结当前owner和两checker，成功后先运行full44 Csim audit再综合audit，目标results/compressed_batch_compact_bus64_synthesis_review_20261025_v1.json，不重复运行HLS。原search XSim78596/compact栈恢复83892仍活跃，完整目标active。

## 最新：compact stack恢复已接唯一自动最终审核（2026-10-25）

- supervisor180564/exec6445运行scripts/supervise_compact_native_stack_recovery_audit_v1.py，local compact_native_stack_final_audit_v1固定当前owner72430及startticks/command和checker SHA，只等待该次完整执行终态，成功后运行一次check_compact_native_stack_recovery_v1.py，输出results/compact_native_stack_recovery_rtl_audit_20261025_v1.json。未重复仿真。
- 实际对当前running状态进行负测，checker正确拒绝且无success文件。原search XSim78596及compact恢复83892均复查活跃；日志仍首事务未完成，尚无完整RTL成功结论。

## 最新：search DPI v7编译成功并进入RTL，compact原快照stack256受控恢复正在RTL（2026-10-25）

- search DPI v7 owner4073029已完成elaboration exit0、MaxRSS54306256KiB，在原full2tx/全depth/全pages/64GiB AS/core0下进入RTL，尚未完整等价验收；原batch/snapshot仍等完整独立audit。
- scripts/run_compact_native_stack_recovery_v1.py新trial owner72430/exec11365位于local compact_native_stack_recovery_v1；复制原sim快照/全部输入逐SHA相等，原failed trial不动、不重新compile。保持4tx/full44、原DUT/models/guards/PC oracle；只调运行栈256MiB并加AS96GiB/core0和128GiB准入/16GiB运行余量保护。实际xsimk83892的/proc limits已保存，日志已越过原崩溃点显示0/4，仍不能宣称完成或根因解决。
- check_compact_native_stack_recovery_v1.py已准备，严格原snapshot来源/命令/实际limits/full4tx/cycles/原C与四完整快照/guard证据；最终审核尚未执行。status入口加入该trial，完整目标active。

## 最新诊断：compact core定位到生成execute函数的大栈帧（2026-10-25）

- results/compact_xsim_core_location_20261025_v1.json绑定原core与实际xsimk及addr2line/objdump/readelf输出。线程4068609的RIP归一化0x1685f8c4，符号execute_11057；入口sub rsp,0x1f65048（32919624bytes），core保存RSP所在PT_LOAD flags0，而入口RSP落另一个RW段。支持线程栈边界/大栈帧方向的进一步诊断，但未映射到具体RTL/模型源码，未作已证明根因结论。未改现有DUT/深度/页/事务，未重跑失败trial。
- search DPI v7同一编译继续，64GiB AS/core0保持；完整目标active。

## 最新终态：compact native elaboration成功，但XSim SIGSEGV；search DPI v7已启动（2026-10-25）

- 原xelab1509104及owner1504642正常结束，receipt exit0、14641.523s，实际Built simulation snapshot；不再是运行中的compile。原监督1537035随后执行RTL，XSim wrapper虽exit0但日志明确Simulator command interrupted/engine not responding，实际kernel core.4068607的ELF NT_SIGINFO为signal11/errno0/code128。postcheck exit1/Error on TV file，execution和final audit均failed，不能记为4tx RTL通过；未证明OOM/工具根因，未重启该trial。
- 13份日志/状态/receipt/core已经逐字节SHA一致复制到data/derived/compact_native_xsim_crash_20261025_v1，results/compact_native_xsim_crash_incident_20261025_v1.json记录真实终态；原仿真snapshot和源码保持。OOMkill仍2。
- 原search supervisor2747344已按既有依赖自动启动attempt search_axi_dpi_replay_v7（owner4073029），当前elaborate；后续batch2747433/snapshot3465022继续原串行链。不得重复提交。完整目标仍active。

## 最新：DPI失败与来源闭合证据已持久化（2026-10-25）

- data/derived/frozen_dpi_incident_provenance_evidence_20261025_v1归档5份报告的29个精确local绑定文件，共651251bytes：search capped v4/v5/v6实际失败证据及helper/protocol实际来源证明。不复制活跃缓存、不删除原件。独立重新读取归档和原件所有bytes/SHA、核完整报告覆盖后，results/frozen_dpi_incident_provenance_archive_audit_20261025_v1.json记录通过；这是可复现性证据，不是完整DPI/RTL通过。原compact1509104复查仍R，oom_kill维持2，既有串行链不变。

## 最新：compact global64入口v2严格重验先决证据（2026-10-25）

- 当前应使用scripts/compressed_batch_compact_bus64_hls_v2.py。旧v1及其准备报告保持原字节；v2调用compact_bus64_prerequisites_v1.py要求三份DPI审核精确成功status、非空files及全部绑定SHA重新一致，合并进新实验plan，避免仅凭文件存在就启动。
- tests/test_compact_bus64_prerequisites.py三项覆盖有效证据、failed status、证据改写；均通过。实际缺先决审核路径也正确拒绝，local实验目录仍不存在。results/compressed_batch_compact_bus64_preparation_20261025_v2.json是准备/拒绝路径证据，不是HLS或RTL成功。原运行链无变更，完整目标active。

## 最新：compact 全总线64位 HLS对照入口已准备，尚未启动（2026-10-25）

- scripts/compressed_batch_compact_bus64_hls.py 复用 canonical top/full44 testbench，4事务/全部声明容量/5ns与1.35ns约束保持；与原CSR global64 Tcl仅两处SEARCH_GRAPH_MODE由0改1。配套check_compressed_batch_compact_bus64_csim.py逐字节对照mode1完整946498280-byte快照及trace，check_compressed_batch_compact_bus64_hls.py审核综合接口/资源与原compact基线。
- 明确要求原search/batch/snapshot DPI三份审核文件存在及CG余量184GiB才允许启动，未新增等待进程/未提交实验；三脚本语法、单变量Tcl对照、缺先决条件时无实验目录的拒绝路径已验证。results/compressed_batch_compact_bus64_preparation_20261025_v1.json只证明准备完成，不是Csim/HLS/RTL通过。已有串行链不变，完整目标未完成。

## 最新完整交付准备：30事务snapshot DPI执行/逐字输出oracle/独立审核/唯一监督已齐备，未运行（2026-10-25）

- 新run_snapshot_dpi_rtl_v1.py按原native setup完整复制、保持13pointers/10模型/40pages/30tx与全部DUT/ROM/TV，仅已审核storage替换+8全RO模型纯AW写入监视，原cosim.pc.exe不变，literal30rows/C state checks不变。每process AS160GiB/core0、184GiB准入/16GiB运行保护，编译保留原generated默认优化，不使用原失败recovery额外O0，未声称该选择会改善内存或速度。
- snapshot_dpi_output_oracle_v1.py完整对照packet30x524288x512bits二进制records、全部result512bit words，核深度/顺序/数据/完整EOF/文件集合。已读实际autotb确认binary EOF和text runtime markers，修正实际C %d transaction marker有多个空白的格式；完整snapshot要求EOF存在，通用binary单元函数另支持纯AXI模型无footer。text未知X/超宽/重复或错序、binary中部数据篡改/截断均拒绝。
- check_snapshot_dpi_rtl_v1.py核全scope/原冻结输入、10模型精确storage+纯monitor、全部RTL/ROM矩阵、4phase精确命令/receipts/日志、原C literal30rows+fullchecks、30positivecycles及每完整输出word；不与不存在的native snapshot RTL cycle baseline比较。实际缺prerequisite gate和原failed compile都被负测拒绝，未创建snapshot执行目录或发布success。
- 唯一supervisor3465022/exec24950等待原batch owner2747433完整独立acceptance，再串行执行snapshot并最终audit，目标results/snapshot_dpi_rtl_audit_20261025_v1.json。当前state waiting_existing_full44_batch_independent_acceptance，local snapshot_dpi_rtl_v1尚不存在。output parser2tests、status3tests及原实际C result30records parsing通过；results/snapshot_dpi_execution_preparation_20261025_v1.json只是prepare+negative evidence，不是功能通过。完整目标active。

## 最新：完整30tx snapshot的10模型DPI预检+独立ledger审核通过，未执行RTL（2026-10-25）

- scripts/preflight_snapshot_dpi_models_v1.py实际成功，data/derived/snapshot_dpi_models_preflight_20261025_v1/plan.json。核原local recovery copied模型hash、原setup30事务且12bundle-level input/output vectors每份均30记录；13个m_axi pointer接口另外按原top C++指纹与pragma数验证，不能把13pointers误作13模型/13TVfiles。实际10 AXI models、每个4pages（不是30pages），原全部depth保留。
- scripts/check_snapshot_dpi_storage_edits_v1.py实际独立phase replay/原输入hash/matrix完整检查通过，results/snapshot_dpi_storage_preflight_audit_20261025_v1.json；40声明、280写、8low16读、80bit读、112word读，非storage文本逐字保持。原DUT/ROM/TV未改/未复制、未编译仿真。computed四态backing889198784bytes仅存储容量，不是编译器峰值界（此前native峰值已远大于backing）。
- 初次preflight把memory_vectors当13指针数量而在建输出目录前拒绝；核真实schema后改为12个bundle vectors+另验13pointer，未改任何实际输入/旧证据。30原事务与完整C postcheck仍待实际DUT执行，不能用2tx search-core parity替代。
- 另核原已通过search packet64实际execution_plan：原xelab未带--O0，采用工具默认优化；snapshot旧original_elaborate_command亦无--O0，而local memory recovery和当前DPI尝试追加--O0。此事实尚不能证明优化level是内存根因，但若串行64GiB/O0仍失败，下一步可受控比较原默认/O2配置并坚持全部输出/周期/C oracle门；不无据把backing当唯一成本。当前不改已冻结/排队driver。
- 原compact1509104已经恢复并继续其full44/4tx nativecompile；DPI v7及后续batch严格等待，完整目标active。

## 最新重大资源终态：原snapshot native编译已保护中止，compact恢复原PID继续（2026-10-25）

- snapshot RSS持续由约216.8GiB涨至264.3GiB；CG anon+kernel/page-table超过285GiB保护界，memory.max300GiB/swap0且全部完成A会话均已释放仍不能止增长。冻结原state/plan/log、记录真实压力后，仅将该自有compiler core限0并pidfd SIGTERM，未改DUT/TV/30tx/声明depth。原2508987自然写failed/elaborate/phase receipt，exec92733收exit1；无RTL/PC通过结果。results/snapshot_compile_resource_abort_20261025_v1.json与data/derived/snapshot_compile_resource_abort_20261025_v1保存完整终态。OOMkill仍2，不将本次主动保护写为内核OOM；原完整30tx/13pointer snapshot验收仍需后续完整实现（不能用2tx search parity替代）。
- 原compact controller1665449观察snapshot真实退出+free>=184GiB，已SIGCONT同1509104（startticks不变），exec50427收exit0。该原nativecompact full44/4tx compile继续，execution1537035/最终1553441保持原监督链。DPI v7 owner2747344/exec8267继续严格等owner1504642结束后再152GiB准入，batch2747433/exec66927等真正DPI audit。
- 最后idle site session2607458经MCP status idle/queue0/lastcode0、24项site-full/clock evidence SHA前后全保持才释放；results/idle_site_vivado_release_audit_20261025_v1.json与data/derived/idle_site_vivado_release_20261025_v1保留原MCP/identity/核验。首次四idle session另426项均保持，所有DCP/报告/源完整，不触B。释放site仍挡不住snapshot自身继续增长，故采用真实资源保护中止，非因观察超时重启。完整目标active，下一步优先完成可验证的存储后端等价，再恢复完整30tx snapshot DUT执行。

## 最新调度结论：64GiB DPI因并发CG保护中止，改严格等待原native workflow后串行验证（2026-10-25）

- 实际v6编译到top时原snapshot RSS涨至207577764KiB（约198GiB），父driver触发CG rawfree<16GiB保护，receipt exit-15/resource_admission_abort=true，没有RTL/postcheck/独立audit。不是已证明64GiB自身不足，未缩scope，OOMkill仍2。results/search_axi_dpi_capped_attempt_incident_20261025_v6.json保存完整原state/plan/log/receipt/limits。exec81980/41590已收exit1，旧owner不再运行。
- 新search唯一owner2747344/exec8267，scripts/supervise_search_axi_dpi_serial_capped_replay_v7.py冻结原2508987/1504642身份到original_native_blockers.json，严格等两原workflow退出，再CGrawfree>=152GiB启动新attemptv7（AS64GiB/core0/原16GiB保护/全部full2tx和exactcycle+output+原PC）。复用checker v6，canonical audit语义路径保持。首次startup因替换脚本名误指checker v7缺失而拒绝，空目录无任何实验/计划，修正明确复用v6后唯一owner启动；未重跑原实验。
- 新batch唯一owner2747433/exec66927（supervise_compressed_bus64_dpi_rtl_v5.py）只衔接新v7独立audit，原full44/4tx/160GiB/core0/184GiB+最终audit不变。当前v7和batch仅waiting，未再并发试探大编译。status入口选择新链并3tests通过，原snapshot/compact/controller不动，完整目标active。

## 最新执行与资源释放：DPI48GiB失败保留，关闭四已完成会话后64GiB受限回归已启动（2026-10-25）

- attemptv5在top编译LLVM ERROR out of memory，exit134、MaxRSS48620136KiB、resource_admission_abort=false，无core；未进入RTL/PC，results/search_axi_dpi_capped_attempt_incident_20261025_v5.json绑定原失败。exec11212/26871均收exit1。原2fulltx/DUT/TV/全部门不变，未把编译失败作功能反例。
- 找到四已完成A physical Vivado仍占内存，经MCP list与status确认全部is_command_running=false/queue0/lastcode0；逐一核原4份独立audit的426个原bindings，保存原log后只pidfd关闭4146646/4159154/633621/497587。关闭前后426项SHA全部不变，actual资源从约250.2GB降225.97GB，释放约22.6GiB。results/idle_completed_vivado_release_audit_20261025_v1.json与data/derived/idle_completed_vivado_release_20261025_v1保存raw MCP/原身份/前后核验。首次cwd检查因compact已在export-recovery目录拒绝且未signal，核实确切cwd后继续；没有改变冻结log/Tcl、DCP、报告、源，不动B和oldsite2607458。
- 新actual v6：supervisor2519968/exec81980→driver2520077，local search_axi_dpi_replay_v6已xelab，AS64GiB/core0，88GiB admission（64+16+8GiB）、16GiB运行门。资源来自已完成空闲会话释放，不超CG配额、不改full scope；checker v6保留originalexactcycle和所有输出/PC oracle。新batch等待2537792/exec41590只接新v6，仍原184GiB/full44/4tx/160GiB/core0+独立audit。当前尚无功能通过。
- 原snapshot2516537 R、compact1509104 T/controller1665449继续，goal active。下次实际Vivado操作不要复用上述已关闭session，应新会话打开已保存DCP，先检查现有MCP列表。

## 最新实质进度：core全字节归档完成，48GiB/core0完整搜索回归已实际编译（2026-10-25）

- data/derived/capped_xelab_core_archive_20261025_v1/state complete；exec18780已收exit0。原core32492687360bytes（SHA483809984e2c233de1d133d9433c47ad4cb38fe6f0a3b35608eb0cfcfeaa8e8b）经独立完整解压SHA/size核验后，持久压缩为5884336984bytes（SHAa13340e00868fbed789d256b23c91d3908d4a43a6d0fa06fd839638dc42add77），source_removed=true。未丢调试字节，原大core仅在验证/fsync后释放。闭合归档文件执行POSIX_FADV_DONTNEED仅提示其自身cleanpages，cold_archive_cache_hint.json记录即时CG无变化，不把提示当保证，不清全局cache。
- 原search v5 supervisor2024814/exec11212自动从等待转full_capped_replay，driver2191734，actualxelab wrapper2199664/leaf2199697；已从/proc验证AS51539607552/core0并冻结enforced_elaborator_limits.json。当前local search_axi_dpi_replay_v5编译到search_kernel_top，leaf RSS约18.2GiB，CG约266.9GB，OOMkill仍2。只是实际编译阶段，未进入RTL/原PC/独立audit，不能称等价通过。
- batch2051098/exec26871继续等新真实audit，原snapshot2516537 R（RSS约153.1GiB）、compact1509104 T/恢复controller1665449不动。完整目标active，后续优先收v5实际终态并诊断，不重复提交。

## 最新资源修订已排队：完整DPI48GiB/core0，但先等31GiB core无损归档完毕（2026-10-25）

- 新driver/checker scripts/replay_search_axi_dpi_v5.py、check_search_axi_dpi_replay_v5.py：按实际32GiB LLVM内存失败修订AS48GiB、--core=0:0、准入72GiB（48+16GiB运行中保护+8GiB余量），保留全部7模型/full depths/4pages/2tx、原cycle[2132461,12404]与完整outputs/PCpostcheck。新canonical audit仍v3语义路径，不覆盖任何旧trial。
- 新唯一combined supervisor2024814/exec11212等待data/derived/capped_xelab_core_archive_20261025_v1 complete+manifest source_removed/全解压验证状态，再CGrawfree>=72GiB才实际启动v5。当前原core archive1970412/exec18780仍compressing，已读约27.38GB/32.49GB，compressed临时文件约4.7GiB；尚未全验证、未unlink原。不要把48GiB当已足够或新回归已运行。
- 新唯一batch supervisor2051098/exec26871等待新search完成；后续batch driver/checker v2额外AS160GiB/core0并保持原184GiB admission/16GiB运行门、4tx/44ports/全快照与C oracle。local attempt v2尚未创建。所有新脚本py_compile通过，status CLI优先新链并3tests通过；旧failed等待者不复用。
- 原snapshot/compact实验与controller不动，完整目标active。下一步先完成core lossless归档并核实际CG；若压缩目标clean cache影响rawfree，可只针对该已fsync归档文件做POSIX_FADV_DONTNEED提示并记录（不得清全局cache或改CG配额）；不降低既定gate来强启。

## 最新实际失败：full-search DPI32GiB受限xelab失败，core无损归档中（2026-10-25）

- 实际v4静态展开complete（peak368780KB）后编译到search_kernel_top，/proc实际VSS接近32GiB时日志LLVM ERROR out of memory；最终父receipt elapsed204.2318s、exit-15、resource_admission_abort=true。另产生31GiB ELF core.1797616，file cache由约18GB增至51GB、cgroup低余量门触发；不能只归因一个事件，也不是DUT功能不一致。OOMkill仍2，原snapshot未动/继续R。results/search_axi_dpi_capped_attempt_incident_20261025_v4.json保存完整state/plan/log/receipt/实际limits等SHA。
- combined owner1789765/exec59512 failed，batch v2等待1802141/exec66903跟随failed，两句柄均已收exit1；尚无RTL/postcheck/独立audit，canonical search audit文件未生成。原2tx/fulldepth/4pages/DUT/TV/golden门保持，失败保存不覆盖。
- 新scripts/archive_capped_xelab_core_v1.py owner1970412/exec18780运行data/derived/capped_xelab_core_archive_20261025_v1，无损gziplevel1流式SHA+独立全解压验证，目标persistent core.gz，验证/fsync/manifest完成后才unlink原unbound closed core。当前不要重复归档/先删原core。新尝试需编译器开销预算和--core=0；32GiB硬限不足的证据明确，不能再只按4.19GB backing推断峰值。可在归档释放缓存后评估更大但受保护budget，完整目标active。

## 最新实质执行：完整2tx搜索核DPI受限回归已进入xelab，旧wait-only链已交接（2026-10-25）

- 重新按真实7模型width/depth/4pages核算四态backing=4190310144bytes，当前CG rawfree约77.7GiB；旧DPI等待184GiB+原native流程全结束并非必要存储界。新driver scripts/replay_search_axi_dpi_v4.py保持全部full depth/2tx/page数/DUT/TV/originalexactcycles/完整outputs/原PCpostcheck，新增每process RLIMIT_AS32GiB（整个exec链继承）+原64GiB admission/16GiB CG资源中止门；不把存储总量当xelab峰值保证，用实际硬上限保护原大编译。
- 只交接三个尚无child/仍waiting的监督196239/247521/731182，全部PID身份/旧state冻结到data/derived/search_dpi_supervision_handoff_20261025_v4/before.json，pidfd终止后验证均不活跃；exec82074/42992/46217收143，旧目录handoff侧车显式superseded。原snapshot/compact及controller未signal，原未完成DPI v3与batch执行目录均不存在，没有重启任何原实验。
- 新combined supervisor1789765/exec59512→driver1789768，data/derived/search_axi_dpi_capped_supervision_20261025_v4，local search_axi_dpi_replay_v4已实际xsc通过并elaborate。新checker scripts/check_search_axi_dpi_replay_v4.py核实际32GiB命令及全部原验收，若真实通过写canonical audit v3路径（语义不变，报告内绑定attemptv4）。实际原xelab /proc limits继承32GiB已捕获enforced_elaborator_limits.json；日志static elaboration complete，peak368780KB，当前simulation dataflow analysis，尚非完整RTL通过。
- 新batch supervisor1802141/exec66903（scripts/supervise_compressed_bus64_dpi_rtl_v2.py）等待新combinedsearch独立audit后按原184GiB/full44/4tx执行及审核，不跟旧已终止owner。status CLI更新识别handoff/新链，3tests通过。完整目标active，不把小静态内存或xelab阶段完成当完整等价。

## 最新：新增只读统一状态入口，PID复用/历史running/挂起子编译器回归通过（2026-10-25）

- 可直接运行python3 scripts/experiment_status.py（或--json），只读/proc与已有状态，不启动/恢复/修改任何任务，也不把本地依赖称为集群调度队列。当前输出snapshot running、compact process_suspended、三DPI后续及compact controller waiting_dependency_or_memory、原integrated physical resource_aborted、两个physical候选prepared_not_started。
- owner只在进程存活且命令匹配原脚本时verified；缺失/不同PID命令返回owner_missing_or_mismatched_no_terminal_receipt，不据此假定成功/重跑。compact额外比controller保存的actual xelab startticks+完整command，避免Python owner等待时误报子compiler在跑；物理原试验以实际resource-abort terminal侧车覆盖历史running。
- tests/test_experiment_status.py三项实际unittest通过：foreign PID不能证明原owner活跃、resource-abort覆盖历史状态、stopped compiler在Python owner存活时仍标T。入口不替代完整功能/物理audit，completion_proven仍false。未改已冻结scripts/run.py/框架/原config；完整目标active。

## 最新：原xelab长编译诊断与2022.2官方选项核实，未找到可证明root cause（2026-10-25）

- results/xelab_long_compile_review_20261025_v1.json记录/proc原2516537身份/实际命令/CPU/RSS/io/wchan，data/derived/xelab_long_compile_review_20261025_v1/xelab_2022_2_help.txt持久保留本机实际--help与SHA。已读Ross simulation-performance参考并查2022.2官方UG900 xelab和command-options原页，文档链接在report。
- 原命令已--O0且-mt off，官方确认O0关闭优化，maxarraysize只管VHDL数组，不把该参数当SV巨型存储的已验证修复。不存在可用于新启动的doc-search MCP工具，因此使用AMD官方网页并核本机help，不用2026版功能推断2022.2支持。
- 本机PATH未发现perf/gdb/pstack，未获取用户态stack/hotspot；wchan0+CPU增长只表明采样时用户态活动，不足以证实有用编译前进/死循环。日志/IO本轮无新变化，未找到可信tool defect或超时界，不因等待时间重启原任务。完整目标active，继续原编译与完整监督链。

## 最新：完整实验九要求/八变体状态v2已生成，最新XRT仍零设备（2026-10-25）

- scripts/snapshot_experiment_completion_v2.py实际成功，EXPERIMENT_STATUS_20261025_v2.json保持原9 requirement IDs/原8 configured variant IDs，不修改configs或旧status；已实际对照id顺序/数量与completion_proven=false、global LUT433034及search WNS-0.382字段。更新全bus64 HLS/三组ablation、search routed、资源中止、DPI四页与30模型预检、durable archive和图表证据，原9项全部不作超scope完成判定。
- 新data/derived/xrt_environment_recheck_20261025_v2实际xbutil examine host exit0，仍0devices/noDRI/no standard platformdir；host.json/examine.log/receipt SHA保留。DDR/HBM同卡带宽/功耗/吞吐未测，不能以CPU/HLS/小DPI样例替代。
- v2硬件状态明确：集成bus64 HLS estimate3.715ns仍差effective3.65ns65ps，search-only实际WNS-0.382ns未过，原集成physical资源中止无DCP；原snapshot及compact/DPI等待链另按/proc记录。状态快照是现有审核元数据汇总，不重新执行全部语义auditors，不据它声明完整目标完成。完整目标active。

## 最新：globalbus64独立物理恢复v4输入已冻结，实际Tcl负测拒绝提前启动（2026-10-25）

- scripts/prepare_compressed_bus64_physical_recovery_v4.py实际成功，data/derived/compressed_batch_bus64_physical_recovery_20261025_v4/plan.json，未启动Vivado。逐hash核原4inputs/117generated和资源中止权威，精确复制原113个.v+2个.dat及clock.xdc，flow保持原版本后接相同物理流程，仅前置更严格准入Tcl。只复制original generated绑定115files，不复制运行生成.Xil cache。旧plan的source_rtl_files=115实际含2ROM，不能误说115个Verilog。
- admission冻结五原workflow owners（2508987/1504642/196239/247521/731182）的startticks，任何原进程仍活跃均拒绝；还要求真实full44独立batch DPI audit accepted状态与CG rawfree>=184GiB。实际/usr/bin/tclsh执行该前置检查，正确报Original workflow still live:2508987，未创建state.json，admission_negative_test.json保存原stderr/exit；未执行任何Vivado design命令。
- 首次prepare v2把115误作全部.v数量而拒绝；v3修计数后遇原source/.Xil目录拒绝，两个未完成prepared目录/源码保留；v4改精确generated复制后完整成功，无覆盖原试验，也未恢复旧消失session。后续需专用新MCP session/真正terminal及新的独立物理audit，不沿用旧v1结果。
- 原snapshot已出现内存回落但仍运行，完整目标active；更严格串行恢复未source。

## 最新资源终态：globalbus64未完成物理试验主动中止，释放约47GiB保住原snapshot（2026-10-25）

- anon已升至303620956160bytes>280GiB，CG300GiB且swap.max0，file cache降到约16.9GB；暂停Vivado仍占约47GiB。保留现场/log/controllerstate到data/derived/bus64_physical_resource_abort_20261025_v1/before.json和文件快照后，通过pidfd先终止自有controller1037647，再SIGTERM+SIGCONT同Vivado1924562，避免在T状态滞留pending signal。仅此未完成/无synthesized.dcp的可再生成尝试中止，未动原snapshot/compact/DPI任务。
- 实际/proc确认两PID不存在，exec48654收143；Vivado具体exitcode未取得不推断。snapshot2516537仍R/RSS约182.0GiB，CGcurrent回落约273.1GB，oom_kill仍2未增加。terminal.json侧车权威标owned incomplete physical trial resource aborted；旧state.json因外部signal保持历史running，不伪造source完成/失败catch记录。results/compressed_bus64_physical_resource_abort_20261025_v1.json绑定完整incident。没有synthesis/physical通过结果。
- 后续新独立physical trial只能在大编译串行释放后恢复，不能沿用旧消失session或因旧state running声称活跃；原64GiB并发准入已被实际内存增长证明不足，需要更严格串行条件。原数据/源/日志/失败都保留，完整目标active。

## 紧急调度更新：globalbus64同一Vivado PID已暂挂，等待snapshot释放内存（2026-10-25）

- 新scripts/serialize_bus64_physical_memory_v1.py owner1037647/exec48654已实际/proc确认；data/derived/bus64_physical_memory_serialization_20261025_v1/plan.json,state.json与first_suspension_observed.json。target仍1924562/startticks1605862311，真实/proc cwd因run_flow中cd已是csr/source（MCP逻辑working_dir仍csr）。首次启动在cwd检查拒绝，尚未建目录/无signal；修正为实际source路径后唯一controller启动。
- CG anon+kernel_stack+pagetables+slab_unreclaimable+shmem+dirty/writeback保守压力代理达到270GiB（非精确不可回收测量）时，pidfd对1924562执行SIGSTOP；本轮ps确认T，RSS约47.5GiB。snapshot2516537仍R，RSS约165.2GiB；非目标完成/失败/重启，goal仍active，原源码/DCP/约束/44ports/全部事务不动。OOMkill仍2。
- controller每5秒检查原身份/压力，原active xelab blockers为snapshot2516537和compact1509104（已经T的不算活跃分配者），仅当没有活跃大compiler且CG rawfree>=64GiB才SIGCONT同target。原compact恢复controller1665449职责不变。目标无子进程才允许stop，pidfd避免PID复用误signal。若controller失败且suspended=true，须优先核身份与恢复条件处理该原PID；不要忘记挂起任务、不要新建替代会话或重复source。
- 在1924562仍T时不要调用该session执行新命令或因MCP响应超时重建会话；先读controller状态和/proc。会话vivado-20261025-044405-144bb05a原source保持。wall source elapsed含资源等待，不能作实验加速数据。所有DPI后续监督仍仅等待；完整目标active。

## 最新：总线宽度消融与实际post-route图表已导出并目视核验（2026-10-25）

- scripts/plot_bus_width_ablation_v2.py实际成功，results/figures/bus_width_ablation_20261025_v2含两套PNG/SVG/PDF、两份CSV、CAPTION.md、固定requirements.txt及source/artifact SHA manifest。已用view_image目视查看两幅PNG，标签/单位/负WNS与不同integration scope清晰；另重读manifest全部hash并复核CSV literal values。
- integrated_hls图仅同一full44 HLS三组1922947/1632814/433034 LUT与4.509/4.509/3.715ns，标whole-device LUT reference1303680（非platform fit）及effective budget3.65ns，全部仍不满足时钟预算。search_core_postroute图是单独小search-only CSR设计，105963→81235 LUT、WNS-1.389→-0.382ns，明确DRC/methodology仍非全通过，不与集成资源跨scope混比、无板卡/带宽/功耗/加速比推断。
- 系统Python没有pip/matplotlib，原pip尝试失败日志保留；通过PyPI官方pip24.3.1 wheel metadata SHA验证在/tmp独立bootstrap，matplotlib3.9.4及依赖装在plot_dependencies_v1，未改系统Python/全局配置，安装日志和bootstrap receipt保留。初版plot v1误用HLS资源键读取physical report而失败，保留未完成v1目录/CSV；v2使用actual Total LUTs/FFs键，不改数据源。
- 这是已审核结果的展示和交付物，不是新综合/RTL结果；原完整实验与监督继续active。

## 最新：完整batch DPI执行+独立审核已接入唯一串行监督链，当前只等待（2026-10-25）

- 新scripts/supervise_compressed_bus64_dpi_rtl_v1.py owner731182/exec46217已实际/proc确认，data/derived/compressed_bus64_dpi_supervision_20261025_v1/plan.json,state.json。只等待既有full-search独立audit owner247521原身份结束；只有其complete+真实report SHA一致才等CG rawfree>=184GiB，再校验冻结driver/checker/preflight/setup/allocation hashes并运行一次完整batch，随后执行一次独立checker。无retry，不signal/重排现有snapshot/compact/global任务，不缩4tx/44ports/depth。
- 当前stage waiting_existing_full_search_parity_audit，local compressed_batch_bus64_dpi_rtl_v1仍不存在（未启动xsc/xelab）。最终目标results/compressed_bus64_dpi_rtl_audit_20261025_v1.json仅在完整功能链实际通过后发布；任何失败保留原试验，回主模型诊断。该监督拥有批次启动权，后续勿手工重复运行driver。
- 完整串行链：snapshot/compact原owners2508987/1504642→search DPI owner196239（exec82074）→search独立audit247521（exec42992）→batch owner731182（exec46217）。原compact恢复controller1665449仍独立负责同PID恢复。完整目标active，链条接通不代表实际实验完成。

## 最新：globalbus64四事务DPI独立最终审核器已准备，未有批次执行结果（2026-10-25）

- scripts/check_compressed_bus64_dpi_rtl_v1.py已导入/CLI通过；实际把原ready_for_elaboration准备目录作为输入，正确拒绝Actual full44 DPI RTL execution incomplete且不发布success。results/compressed_bus64_dpi_final_auditor_preparation_20261025_v1.json仅记录准备/负测，正向路径须实际完整执行后才能验证。
- checker核完整4tx/44ports scope、search full-depth独立parity、30 model preflight与exact转换来源、所有RTL/ROM集合和内容、原完整copied fixtures/C executable；allocation→RO guard覆盖、guard之外模型字节保持、9case执行log hash；精确重建4phase命令、receipt/plan/log hashes/abort与error门；4/4结束、原C fullsnapshot marker、4positive cycles；四份946498280bytes快照与已接受setup reference整个文件SHA，绑定全部RTL output/DPI.so。仍无real workload/platform/board/timing/speedup推论。
- 原完整DPI batch driver尚未执行，独立最终audit亦尚无实测结果；完整目标active。后续必须原search gate真实通过与内存门达到后启动新batch副本，再跑此checker。

## 最新：globalbus64完整四事务DPI执行入口已准备并验证前置门拒绝，未运行（2026-10-25）

- scripts/run_compressed_bus64_dpi_rtl_v1.py已py_compile通过。完整2tx search-core独立audit文件缺失时实际拒绝启动，二次受控检查确认异常消息准确且local compressed_batch_bus64_dpi_rtl_v1目录始终不存在；results/compressed_bus64_dpi_execution_entry_preparation_20261025_v1.json只记录准备与gate负测，不是RTL结果。没有启动新的大编译。
- driver要求原search full-depth等价独立report和全部绑定hash；原30模型preflight audit/9case guards、guarded setup copied hashes核验后，按CG rawfree>=184GiB clone完整setup（新rtldatafile空）、仅替换30个经审核DPI模型，完整RTL/ROM set/hash不变。保留4tx/44ports/所有depth/pages与原RO guards，xsc→xelab→10sec bounded XSim→原cosim.pc.exe，16GiB rawfree abort门；要求4/4实际结束、四条positivecycle记录、原mode0 C标记、4份每946498280bytes snapshot与原HLS/CPU门下reference完全相同，之后状态仍pending independent audit。
- 该driver尚未通过实际full-batch编译/执行验证，也尚未连接自动batch提交监督；须原search gate真实通过且内存合格后才能运行。完整实验active，不拿入口准备替代功能验收。

## 最新：globalbus64完整批次30 AXI模型DPI存储转换预检+独立ledger审核通过，未执行RTL（2026-10-25）

- 新scripts/preflight_compressed_bus64_dpi_models_v1.py实际exit0，data/derived/compressed_bus64_dpi_models_preflight_20261025_v1/plan.json。先验证原full-depth setup report SHA及准备好的30模型：7guarded models按原guarded hash，另23按setup原模型hash。只复制30模型输入和转换后输出+ledger，未复制/修改DUT/ROM/TV，未运行xsc/xelab/xsim。仍4事务、每模型4pages、原32/64bit和所有declared depths，总模型payload allpages=3785988768bytes，四态C++ backing实际容量还需2倍aval/bval，不将此数字当原BO或实测内存峰值。
- 新scripts/check_compressed_bus64_dpi_storage_edits_v1.py实际独立逐字节phase replay+所有原绑定hash/matrix检查通过，results/compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json。30模型/120 storage declarations、840 writes、100 low16 reads、240 bit reads、640 word reads；所有非storage文本完全保持（含原RO/trace guards），helper不写协议状态/不增delay。
- 当前仅conversion-preflight gate，不是集成batch RTL通过。后续必须先完成原search-core full-depth DPI回归及独立audit，再按内存门运行新的完整batch副本，保留4 full transactions/44ports/全部深度/原PC postcheck/全snapshot和trace oracle。原guarded setup与原失败证据未改，完整目标active。

## 最新：原入口三命令复核通过；时钟内部语义证据仍不足（2026-10-25）

- 原授权入口实际执行python3 scripts/run.py check/plan/smoke（各--output指定新scaffold_*_recheck_20261025_v1.json），全部exit0；check报告3 real_data_ready，smoke保持synthetic_smoke/python_cpu且性能字段None，plan仅计划清单。未改原configs/experiment.json八variants或原框架，不把脚手架命令成功当真实实验完成。
- 读取现有clock semantics/connectivity capture与requirements builder后确认：两个目标clock实例仍缺内部constant/inversion/delay/test/ownership证据；外部signal owner和node非GND/VCC不足以推定内部常量。没有新增特例豁免或用假设“闭合”语义，也没有改动旧证据。
- 最新MCP status确认globalbus64 session vivado-20261025-044405-144bb05a/PID1924562原source仍is_command_running=true、queue_length0（已90m49s），无终态，不重复source。/proc确认snapshot2516537 R、compact1509104 T、controller1665449、DPI owner196239及末级audit247521活跃；CGcurrent约285.8GB/322.1GB。完整目标active。

## 最新：四项原RTL仿真时间单位与延迟证据核实，未中止原进程（2026-10-25）

- 新scripts/observe_component_rtl_progress_v1.py实际执行，results/component_rtl_progress_observation_20261025_v1.json。核/proc真实xsimk身份/startticks并保存原rtl.log不可变snapshot至data/derived/component_rtl_progress_observation_20261025_v1，绑定autotb.v和实际top csynth.xml。XSim日志Time resolution is 1 ps、TB timescale1ns/1ps且%0t打印$time；例如1200005043000是1.200005043仿真秒，5ns时钟下约2.4亿cycles，不能误当1.2e12ns。
- 四项最新完成数/总数：site occupancy34/52@0.273232773s，route tree1/50@0.350098078s，retained nodes1/37@0.550004978s，retained edges1/37@1.200005043s。四top综合Worst-caseLatency均undef，未形成可靠事务超时界。仿真clock推进仅证明时钟在跑，不证明DUT内部前进/无死锁；原complete+PC postcheck仍未达，未重复/中止/缩交易。
- 原snapshot/compact串行与DPI监督链保持，完整目标active。下一步以原终态或新握手/内部状态证据诊断，不把单纯墙钟耗时/大timestamp当失败证据。

## 最新：整核DPI完整验收checker+唯一末级audit监督已接通，仍等待原任务（2026-10-25）

- scripts/check_search_axi_dpi_replay_v3.py已准备且CLI导入通过。实际拿原aborted v2测试fail-closed：拒绝Actual full replay incomplete且不发布success文件。接受门包括原2tx完整state、frozen baseline/files、7真实model矩阵+独立storage ledger重放、完整DUT/ROM文件集合和值保持、原生成命令精确重建/4phase receipts+logs、C golden两行/ALL_PASS、exactcycle [2132461,12404]、完整output文件集合/所有字节SHA、DPI.so绑定。小helper/protocol proof不替代该门；尚无完整v3结果。
- scripts/supervise_search_axi_dpi_final_audit_v3.py owner247521/exec42992已实际/proc确认，data/derived/search_axi_dpi_final_audit_supervision_20261025_v3/plan.json/state.json。仅等待原串行owner196239同startticks/cmd/cwd进程结束，只有其complete状态才校验冻结checker/deps/上游plan并执行一次独立audit，目标results/search_axi_dpi_replay_audit_20261025_v3.json。失败保留，不重跑/不替代上游owner。原exec82074与新42992均为活跃长任务句柄，勿重复提交。
- 本轮snapshot2516537实际R，RSS由约161GiB回落至约131.8GiB，CGcurrent回落285.5GB，memory.events oom_kill仍2；不是失败/重启。compact1509104仍T、原controller1665449活跃，global1924562活跃。完整目标active。

## 最新：完整两事务DPI回归的单一串行监督已启动等待，未启动xelab（2026-10-25）

- 新scripts/replay_search_axi_dpi_v3.py保持原v2完整scope/全部7models/full-depth/page数/2tx、exact cycles [2132461,12404]、全部输出文件集合+完整字节SHA、原PC postcheck及16GiB运行中resource-abort门；额外在开始前校验helper、protocol、four-page独立oracle及其files，原v1/v2失败不改。
- 新scripts/supervise_search_axi_dpi_v3.py唯一owner196239/exec82074已实际通过/proc确认，data/derived/search_axi_dpi_serialized_supervision_20261025_v3/plan.json,state.json。监督核原snapshot owner2508987与compact owner1504642的startticks/cmd/cwd，每30s轻量读取；两原任务均退出且CG rawfree>=184GiB才校验冻结driver/transform/backend/proof hashes并启动一次完整v3。当前stage waiting_original_jobs_and_raw_cgroup_headroom，两个blockers均活跃，local search_axi_dpi_replay_v3尚不存在（未编译）。无自动重试，不signal/重排既有任务。后续原compact恢复controller1665449继续原职责。
- 新driver/supervisor已py_compile通过；监督只等待，不将pending计划当完整RTL验收。最终完整replay若成功仍需独立审核，失败保留并由主模型诊断。监督技能无可用luna切换接口，使用确定性监督，不声称切换。完整目标active。

## 最新：DPI完成证据35文件持久归档并独立全字节复核；原RTL仍活跃（2026-10-25）

- scripts/archive_report_local_evidence.py实际完成data/derived/frozen_dpi_validation_evidence_20261025_v1（35files/669801bytes），覆盖两份memory units、helper provenance、protocol provenance、四页独立oracle五份report的精确顶层files绑定；原local不删。results/frozen_dpi_validation_archive_audit_20261025_v1.json又独立重读全部archive字节SHA和尺寸，并核5report SHA/全部local覆盖/persistent hashes。兼容原restore helper。嵌套historical incidents非顶层files的不宣称完整归档。
- 实际四独立RTL xsim进程仍存活：site occupancy1787486最新34/52；route tree3001920最新1/50；retained nodes459268和edges2216832均1/37，仿真时间继续增长。未拿耗时或进度打印当失败，不重复启动，不宣称完成。完整功能结果/PC postcheck仍待原任务结束。
- data/derived/dpi_validation_resource_observation_20261025_v1.json记录/proc实际state/startticks/RSS与CG memory.stat/events。snapshot2516537继续R，RSS约159.9GiB，compact1509104 T/controller1665449活跃，global1924562活跃。CGcurrent已约315.3GB/322.1GB，含约76GB file cache，rawfree不足不能直接证明不可回收分配失败；本轮未启动新大编译/physopt，未调cache/cgroup或既有准入门。下一轮优先检查snapshot和memory.events，完整目标active。

## 最新：四页真实AXI模型生命周期+完整导出独立Python字节oracle通过（2026-10-25）

- 新scripts/test_axi_dpi_protocol_pages_v1.py（基于已通过v5），local axi_dpi_protocol_pages_v1实际xsc/xvlog/xelab/xsim全exit0（exec77402已收），results/axi_dpi_protocol_pages_20261025_v1.json。两模型仅module名/各自TV_OUT宏文件名分离；相同小depth64/原4pages/原latency。每页独特pattern，ready/done按生成模型语义推进事务，先读零再全写+读+部分byte写+读，共20个INCR bursts/80beats，所有输出周期采样一致、SV独立byte scoreboard与stall检查通过。done触发完整64word页导出，native.dat/dpi.dat均8224bytes且完全相同。
- 新scripts/check_axi_dpi_protocol_pages_v1.py实际通过，results/axi_dpi_protocol_pages_oracle_20261025_v1.json。独立Python由字面pattern/byte mask/pageoffset重建所有4x64words和4个64bit depth headers（big-endian），两个完整导出逐字节等于预期，四页payload彼此不同；执行proof全部hash复核。此为小模型事务页与输出路径证据，不替代完整深度整核/其他AXI模型或真实workload验收。
- 最新/proc：snapshot2516537仍R、RSS约147.0GiB（继续增长），compact1509104 T、controller1665449活跃、global1924562活跃。CGcurrent300654424064bytes/322122547200bytes（约280.0/300GiB，仅20GiB rawfree），未启动新的大编译或physopt，下一轮优先核内存/原进程状态。完整目标active。

## 最新：实际HLS AXI模型native/DPI小深度协议对照与独立数据oracle通过（2026-10-25）

- scripts/test_axi_dpi_protocol_v5.py实际xsc/xvlog/xelab/xsim全exit0，exec58753已收，results/axi_dpi_protocol_unit_20261025_v5.json。同一实际AESL_axi_master_output_mem原生和转换后副本仅改module名，双实例相同depth64参数override，原4pages/64cycle请求latency/协议逻辑保持；sentinel文件避免额外初始化，ready起始marker使读写均page0。四个INCR burst（两写两读）16beats，完整写后部分byte mask写，读RREADY和BRESP各stall3周期；逐周期negedge+1ns比较全部输出，读值/RESP/LAST另对独立byte scoreboard，PASS于3201ns。只限一个256bit模型/page0小单测，不是full-depth整核回归。
- results/axi_dpi_protocol_provenance_20261025_v1.json复核unit全部files SHA，断言两份执行模型与各自frozen输入仅module重命名差别，绑定DPI.so；保留v1-v4设置/测试台失败与日志。v1误端口数；v2未发ready造成读transaction=-1/page3与write/page0；v3在原模型negedge/NBA更新区采样竞态；v4delay编辑语法错误。v5仅修测试台，在+1ns稳定区采样并保持所有data/handshake门，未改DPI转换或原模型。勿将这些测试台错误归因DUT，勿将小测替代完整原2tx/full44/30snapshot验收。
- 本轮snapshot2516537仍R，RSS约131.8GiB，compact1509104 T/controller1665449活跃，global1924562活跃；CGcurrent约284.3GB/322.1GB，未启动新大编译/物理优化。完整目标active。

## 最新：实际转换存储helper五宽度word/bit/low16/NBA对照已通过（2026-10-25）

- hardware/sim/test_axi_dpi_helper_v1.sv与scripts/test_axi_dpi_helper_v1.py执行xsc/xvlog/xelab/xsim全exit0（exec38097已收），results/axi_dpi_helper_unit_20261025_v1.json。实际output_mem edits ledger helper仅参数名改为W/D/P，保留4pages assertion，五宽度32/64/128/256/512，各depth23、128更新；每次比较整字、所有bit、low16以及越界/unknown bit返回X，同时原生SV对照X/Z与blocking/NBA可见性、同地址双NBA顺序。未更改DUT/既有模型/CPP backend。
- results/axi_dpi_helper_provenance_20261025_v1.json另绑定实际ledger、执行test SV、unit proof、全部4phase日志及DPI.so；原unit所有源hash和每phase exit/hash复核，断言规范化真实helper逐字包含于执行SV。仅小型helper存储语义证明，不是原生完整AXI握手/整核full-depth事务通过，不能替代原full replay。
- 本轮snapshot2516537 R、compact1509104 T/controller1665449活跃、global1924562活跃；CGcurrent265.6GB，物理优化64GiB内存门仍未达到。完整目标active。

## 最新：packet64 physopt独立审核器已就绪，尚无优化执行结果（2026-10-25）

- 新scripts/check_packet64_physopt_v1.py，CLI导入/--help已通过。对原prepared trial后续完整state、MCP raw terminal/exact history/独有log completion、冻结input hashes、原WNS复现（setup/hold/pulse）、DCP ZIP CRC、report版本/设计/part、route/setup/hold/DRC/methodology做独立审核；允许history明确截断时取完整已绑定Vivado log唯一marker，不伪造原history。
- 加强前后约束一致性：before/routed active XDC均需与原packet64 routed XDC逐行去注释排序后完全一致，原XDC hash须匹配原audit；另保留严格no-exception/1.35ns uncertainty检查。实际原XDC控制检查通过：注释不影响；新增set_input_delay被差异检查识别；set_false_path被约束门拒绝。最终report仅完整执行后生成，未把checker准备当实际优化通过。
- /proc本轮确认snapshot2516537 R、compact1509104 T、controller1665449活跃、global1924562活跃；CGcurrent约265.6GB/322.1GB，rawfree仍不足64GiB，不source新physical或大xelab。global原日志仍推进batch net模块综合。完整目标active。

## 最新：packet64独立post-route优化输入已冻结，未启动（2026-10-25）

- 新scripts/diagnose_packet64_routed_path_v1.py已实际生成results/search_packet64_routed_path_diagnosis_20261025_v1.json，绑定原routed timing/generated validate_path/read_r RTL及独立physical audit；实际最坏setup -0.382ns、route占70.626%。只定位实测路径，不将生成模块名称直接宣称为精确C++操作映射。
- 新scripts/prepare_packet64_physopt_v1.py已完成（exec82990收exit0），data/derived/search_packet64_physopt_20261025_v1/plan.json状态prepared_not_started。完整原routed.dcp先核对原audit SHA及ZIP CRC，再复制冻结并重读核hash；沿用原2022.2本地help证明支持的AggressiveFanoutOpt及Explore -tns_cleanup流程，仅替换baseline输入、基线WNS断言和marker。原session/DCP/源码/XDC不动，2线程，同part/5ns/约束。
- 本轮CG rawfree约52.9GiB，小于64GiB admission，不创建新Vivado session、不source新流程。不能把prepared当实际优化，更不能声称修复。后续先检查原输入hash/内存门，专用新MCP Tcl session source一次，保持baseline重现WNS断言，完成后独立核约束、DCP、route、setup/hold、DRC与methodology。
- /proc确认snapshot2516537实际R、compact1509104 T、controller1665449活跃；OOMkill仍2。global1924562在上一轮MCP确认仍source运行，本轮进程存活。完整目标active，未新增大xelab。

## 最新：CSR packet64完整OOC独立审核完成仍时序失败；DPI五宽度测试/7模型storage范围通过，整核回归受内存门中止（2026-10-25）

- search-only packet64物理PID497587/session vivado-20261025-035512-03ffde3f source已complete/exit0，5719.24s。terminal_status.json/raw full_source_history.json已真实保存。原check_packet_width64_physical.py首次审核因history输出102451chars截断不含末尾marker而拒绝；未改写history/status。新scripts/check_packet_width64_physical_v2.py仅在明确truncation sentinel时改用已绑定完整Vivado.log唯一completion marker，额外核对history/status elapsed与timestamp/last-command prefix；其余源/约束/DCP/报告/gates同原。实际results/search_packet_width64_physical_audit_20261025_v2.json独立审核完成，96bindings。
- 最终post-route LUT81235/FF108764/RAMB36=218/RAMB18=15/DSP77，全182762 routable nets fully routed、errors0；setup WNS-0.382ns/TNS-199.829ns/2151failing（原-1.389ns，改善1.007ns），hold0.017ns/pulse1.958ns通过。DRC87/methodology1001，timing/noDRC/noMethodology gates false；非200MHz/platform/board通过。MCPtodos3/3代表工作审核完成。该会话与本次DCP/报告冻结，后续优化用新副本/session。
- 已查看实际最坏path：grp_validate_path_fu_20149/cursor_2_reg_482_reg[17]/C→cursor_fu_88_reg[20]/CE，data3.929ns（logic1.154/route2.775=70.626%），14levels含6CARRY8；后续基于此瓶颈分析，不继续仅凭旧packet mux假设调参。
- DPI新五宽度unit：hardware/sim/test_axi_dpi_memory_v2.sv/scripts/test_axi_dpi_memory_v2.py，results/axi_dpi_memory_unit_20261025_v2.json实际32/64/128/256/512五组×128更新通过（exec48431收exit0），沿用未改的CPP v1，四态/NBA语义小测而非完整AXI/DUT证明。
- scripts/transform_axi_memory_dpi_v1.py只改原AXI storage声明和访问、生成完整逐字节edit ledger及可逆hash。首轮完整搜索核replay_search_axi_dpi_v1.py（local search_axi_dpi_replay_v1，exec1209收exit1）在解析阶段因函数返回后[15:0]切片不被2022.2接受，原失败保留。新transform_axi_memory_dpi_v2.py独立low16 helper，协议/延迟/深度/page数/DUT/TVDATA不变。
- scripts/replay_search_axi_dpi_v2.py owner3219676/exec24053已failed（收exit1），7模型解析通过、编译至search_kernel_top，但父进程观察CG rawfree<16GiB主动SIGTERM own process-group（receipt resource_admission_abort=true，172.2s），未进入RTL仿真且OOM计数未加。保留原2full-capacity交易/全部输出+cycle[2132461,12404]+原PC postcheck门，未缩scope。results/axi_dpi_search_replay_incidents_20261025_v1.json绑定两次失败，不作功能不一致结论，也不能称DPI完整等价已通过。
- 新scripts/check_axi_dpi_storage_edits_v1.py→results/axi_dpi_search_model_storage_edits_20261025_v1.json独立检查7模型ledger，所有非storage协议文本完全保留；counts声明28、写196、low16读20、bit读56、word读136。此静态范围audit不替代完整cycle/output回归。后续可做低内存协议单元对照，整核原回归等待真实CG余量，勿无变化重复提交。
- CG上限300GiB，rawcurrent含大量干净file cache，保护门偏保守；不要把资源中止解释DUT bug。snapshot2516537仍R、compact1509104仍T/controller1665449活跃，global integrated物理1924562继续synthesis；完整目标active。

## 最新：globalbus64执行输入已冻结但未xelab；19.13GB第三批归档完成；DPI仿真存储原型首轮小测试通过（2026-10-25）

- 新scripts/prepare_compressed_batch_bus64_guarded_rtl.py owner2396444/exec69333已complete/收exit0，local compressed_batch_bus64_rtl_guarded_v1/state status ready_for_elaboration, stage guarded_full44_setup_frozen_cgroup_memory_admission_pending。clone全部setup并检查copied TV/RTL/ROM等、全部RO模型guard，trace guard原文同已执行9例CSRguard；plan记录原generated xelab命令和copied hashes。没有启动xelab！不要把ready_for_elaboration当CSR旧driver的prepared/elaborated；后续需单独内存门和runner验证所有模型/库/ROM再执行。
- 新归档owner2337954/exec44537 complete/收exit0，data/derived/frozen_report_local_evidence_20261025_v3，1607local文件/19130952623bytes，覆盖global bus64 syn+setup+三组ablation+CSR failed-elab内存incident。源流hash/目标独立重读/fsync/source稳定检查通过；results/frozen_report_local_evidence_archive_audit_20261025_v3.json复核4report全部local依赖覆盖及路径/尺寸。兼容原restore helper，不删原local；活跃编译缓存不归档。
- 研究内存瓶颈的可行替代：本机2022.2 xsc --help与SDK svdpi.h已确认支持C++14 DPI。新hardware/sim/axi_dpi_memory_v1.cpp四态svLogicVecVal存储，全部page/depth保留、零初始化、越界读X/写忽略；区分blocking写与排队NBA写，SV NBA toggle后commit以保留可见性顺序，未改FPGA DUT。
- hardware/sim/test_axi_dpi_memory_v1.sv与scripts/test_axi_dpi_memory_v1.py实际xsc→xvlog→xelab→xsim全部exit0（exec63218已收），results/axi_dpi_memory_unit_20261025_v1.json：32/64/512bit三组、每组128更新，覆盖初值/多page/越界unknown read/X/Z/部分byte/active+inactive区域旧值/NBA提交/同地址两NBA最后写顺序。报告绑定源/日志/DPI.so/SDKheader。仅小型存储语义对照！未转换实际HLS AXI模型，未做完整协议/原RTL事务回归，不能替代完整full44/30snapshot验证或称DPI已解决大编译。
- 下一步可在新副本实现精确storage hook，保持原AXI握手、burst/latency、全部声明depth/page/transaction、DUT与数据文件不变，保留NBA语义，再用已通过的原搜索核两事务对照完整输出和cycle及PCpostcheck。通过后才能用于完整case。不要简单将SV非阻塞内存赋值改成C立即写，或减page/depth/交易来绕过内存门。
- 原snapshot2516537继续R并已增长到约126.7GiB；compact1509104仍T由controller1665449等待；两物理497587/1924562继续。CG内存约267GB/322GB，oom_kill2未再增加，绝不能启动大xelab并发。完整目标active。

## 新进展：search-only CSR packet64实际Vivado综合改善；集成bus64物理最终审核器已准备（2026-10-25）

- 原search-only物理PID497587/session vivado-20261025-035512-03ffde3f已越过综合+报告，当前placement。同阶段对照实际Vivado synthesis LUT108168→83984（-22.3578%）、FF142046→108318，setup WNS-1.623→-0.094ns（仍负）；RAMB36=218/RAMB18=15/DSP77。results/search_packet_width64_physical_synthesis_observation_20261025_v1.json绑定实际closed synthesis util/timing/check/XDC与原基线审核，明确不是post-route/board，也不是全batch globalbus64结果。不与不同阶段/不同integration混比。
- 新scripts/check_compressed_bus64_physical.py为global integrated最终物理审核器：成功idle MCP终态/精确source history、frozen inputs/generated/hash、原flow只top名不同/同clockXDC、3个DCP zip完整性、真实设计名/2022.2/part/clock/coverage/DRC/methodology、完整routed quality gates均核对；记录HLS估计另列，不拿旧search-only物理作为whole-batch controlled baseline。CLI已检查，未运行最终审核，不称通过。
- global integrated物理session vivado-20261025-044405-144bb05a/PID1924562原source工具cell5416本轮已返回300s running handoff且cell结束，不再wait5416；actual command仍synthesis（有Synthesis/xcu280 license checkout）。下次按MCP status退避观察，不重复source。
- 内存controller1665449仍等待snapshot2516537/CG free>=184GiB；compact1509104保持T，同一进程保留。snapshot实际R约80.8GiB；没有新大xelab启动。完整目标active。

## 新进展：三组集成CSR接口宽度消融的源码/ABI/约束可比性已独立核对（2026-10-25）

- scripts/compare_integrated_bus_width_ablation.py→results/compressed_batch_bus_width_ablation_20261025_v1.json：default、packet64、all64的所有非测试辅助C++/header逐hash相同；packet top仅1条max_widen pragma差异、all64 top与canonical exact；v2 parser去可选width metadata后45args/44ptr身份、顺序、深度、payload容量相同；DUT cflags严格stdc++14/mode0，5ns/1.35ns/part/top一致；flow排除TB行与预先指定的global64配置后逐行相同。TB full44化仅影响Csim验证，不是综合源码变化。
- 对照HLS估计default LUT1922947/4.509ns，packet64 LUT1632814/4.509ns，all64 LUT433034/3.715ns；global仍比有效3.65ns差0.065ns，低于整片LUT参考不是mapped/platform fit。所有因果结论只限接口配置对HLS估计，不把CPU或HLS数值称实际HBM带宽/route加速。
- 新globalbus64物理1924562/session vivado-20261025-044405-144bb05a原source继续，functions exec cell5416仍待工具返回，不重复source；内存调度controller1665449保持compact1509104挂起，等snapshot2516537及CG门。完整目标active。

## 最新：集成globalbus64同约束OOC物理已启动；full44 cosim setup和实际TV静态审核完成（2026-10-25）

- scripts/prepare_compressed_bus64_physical.py先按cgroup当前余量>=64GiB准入（不是hostMemAvailable），重新核对global syn全部1123files绑定，source RTL/ROM逐hash复制到data/derived/compressed_batch_bus64_physical_20261025_v1/csr/source。原物理flow只替换top search_kernel_top→search_batch_trace_top_v2，其余物理流程/clock.xdc逐字节不改，U280/5ns/1.35ns/2threads无waiver。此是独立资源/时序表征，不宣称功能RTL已通过，未绕过RTL最终门。
- MCP先list当前会话后新建专用Tcl session vivado-20261025-044405-144bb05a PID1924562，start_raw/session/plan保存；已唯一source run_flow.tcl，实际state running/synthesis且ps活跃。functions exec cell5416仍待该工具返回（后续可能300s handoff），不重复source；MCPtodos freeze done/run active/audit pending。与大xelab分开，current RSS约1GiB；本轮CGcurrent205GB/300GiB。
- 原bus64 setup1789023/exec9054已complete/收exit0，results/compressed_batch_bus64_full_depth_cosim_setup_20261025_v1.json原子持久复制，953bindings，SHA7063eb456429ee0ed1db6f034c19ebf570dc38df4718bd9d0dc72c91ff00974b，4完整HLS/Csim snapshots与CPUmode0同、生成4tx RTL setup，不是实际RTL执行。
- 新audit_compressed_bus64_cosim_{model_capacity,allocations,binary_transactions}.py→对应results/compressed_batch_bus64_cosim_*_20261025_v1.json，44port/30model容量、完整disjoint wrapper区域、55份实际text/binary TV各4 full-depth事务全通过，exec1418收exit0。真正bus64 xelab仍须等cgroup内存门，不启动。
- controller1665449/exec50427仍alive，compact actual1509104为T，snapshot2516537仍R约80.8GiB；保留同进程不重跑。CSR原failed137及其全部failed监督保留；完整目标active。

## 最新终态：global bus64集成候选独立综合通过，LUT433034但65ps估计预算缺口；先准备cosim不启动大xelab（2026-10-25）

- 原global HLS1039762/exec16359、监督1096966/exec65528均complete/independently_audited，本轮均收exit0。local compressed_batch_bus64_hls_review.json已按原字节原子持久复制results/compressed_batch_bus64_synthesis_review_20261025_v1.json，SHA186015cb970da24c19c5f370ae1fcab030775000ad399e87b743f17564c24771，1123bindings。actual30RDATA均等于min(original,64)，canonical top不改，仅global HLS配置，full44 Csim gate通过。
- 实际HLS估计LUT433034/FF321329/DSP93/BRAM69/URAM3，较原LUT1922947减1489913=77.4807106%，FF减402591；estimatedclock3.715ns较4.509改善0.794，但仍>有效3.65ns（差0.065）。仅估计低于整片1303680 LUT参考，不是mapped/platform fit或时序/带宽/功耗通过。窄总线有带宽/周期代价，仍须测量，不宣称加速。
- 新scripts/prepare_compressed_batch_bus64_cosim.py唯一owner1789023/child1797460/exec9054，local compressed_batch_bus64_cosim_setup/project compressed_batch_bus64_cosim_project，root data/derived/compressed_batch_bus64_cosim_setup_20261025_v1/location.json。复用syn逐hash，保持canonical/full44 TB/4calls/全depth，Csim→cosim -setup及全部payload对CPUmode0，8GiB文件上限。此为低内存准备，未启动新xelab；终态未收，后续需实际TV/RO/宽度核对。
- cgroup300GiB硬限制继续生效，本轮current约206GB、oom_kill2未增加。controller1665449/exec50427活跃，compact实际1509104仍T，等snapshot2516537结束+CGfree>=184GiB才恢复同一进程。原CSR整批failed137仍保留；新大编译必须等cgroup门，不能用主机1.2TiB判断。
- 其他原物理/小HLS检查可在资源余量内推进，完整实验active；不将正面的HLS资源估计替代RTL/物理/实板验证。

## 紧急资源实态：CSR整批xelab已SIGKILL；compact同一PID暂挂起等待内存（2026-10-25）

- CSR guarded owner334627/child342081已failed/elaborate，exit137/SIGKILL、2202.9465s、MaxRSS157933656KiB≈150.6GiB；依赖执行397193与最终审核779628也failed。exec4723/51340/47375本轮全部收exit1，不能再按旧条目称它们运行或RTL通过。全部原scope/源码/44depth/4tx及失败日志保留，不盲重跑。results/compressed_batch_csr_elaboration_memory_incident_20261025_v1.json记录。
- 当前cgroup memory.max=322122547200bytes=300GiB，memory.events oom_kill2（早前1），本机/proc/MemAvailable约1.2TiB不能代表会话配额！dmesg被拒，OOM计数无精确PID时间，所以只称与内存压力一致，不断言OOM已归因此PID。memory.events max/oom仍0，可能上级/其他OOM事件，勿夸大根因。未来大编译须按cgroup当前余量与已观测峰值留裕量，不能只看主机空闲。
- 自主调度修正：仅owned compact实际xelab PID1509104（owner1504642/exec13729、cwd compact_rtl_guarded_v1/sim/verilog）已SIGSTOP，ps状态T，约6.6GiB，保留同一进程/完整输入/源码/容量；未杀掉/重启，goal仍active。新scripts/serialize_compact_rtl_memory.py controller1665449/exec50427，state=data/derived/compact_rtl_memory_serialization_20261025_v1/state.json，核对startticks+cmd+cwd，等待原snapshot compiler2516537结束且cgroup free>=184GiB才SIGCONT恢复同一1509104。若controller意外退出，必须先检查state/身份/配额再处理该挂起PID，不能忘记或重复启动。
- snapshot恢复2508987/实际xelab2516537仍running（约80.8GiB），继续原任务；compact执行/审核监督1537035/1553441仍等待原编译。没有大规模新xelab通过内存门前启动；不以缩声明深度/删除交易代替完整验证。CSR失败后另新revision的串行恢复仍待可用内存。

## 最新：5份新审核证据30.64GB已持久归档；compact整批guarded RTL编译与后续监督已启动（2026-10-25）

- 新scripts/archive_report_local_evidence.py按5份已审核report精确files集合归档，不递归活跃目录。owner1458071/exec58822已complete/exit0，data/derived/frozen_report_local_evidence_20261025_v2/manifest.json，2041独立local文件/30638277088bytes。源流hash、目标独立重读hash、size/mtime稳定、fsync、原local不删；persistent已有文件单独校hash。覆盖compact syn、integrated packetwidth syn v2、compact full44 cosim setup、search-only compactwidth syn、globalbus64 full44 Csim。results/frozen_report_local_evidence_archive_audit_20261025_v2.json确认5report全部local依赖hash被覆盖及目标路径/尺寸，schema兼容原restore_frozen_local_evidence.py（仅补缺，不覆盖不同原件）。活跃未绑定cache/log不归档。
- 新持久metadata results/search_packet_width64_compact_synthesis_review_20261025_v1.json（142bindings，SHA3874054af017a2274b4d235959f9c8c0d81be4eaceabca870eb23bb2b938f74b），search-onlycompact64 LUT223947/FF137947/DSP77/BRAM69/URAM3，estimated3.65ns，较原compact LUT-145511/FF-36638/clock-0.106。只是Csim+syn，未RTL/物理/板卡；旧failedcompact路由不因此修复。原HLS1180234/exec88004及监督1237085/exec96429均complete，本轮收exit0。
- 新持久metadata results/compressed_batch_compact_full_depth_cosim_setup_20261025_v1.json（1003bindings，SHAb309046cd884139e5686bed079296079635a31fa8c4b44180da88ae4fcc0e17e）；owner1307637/exec33730 complete/收exit0。4份full44 HLS/CPUmode1快照逐字节相同，cosim -setup四交易，syn无改；不是RTL执行通过。
- 新compact静态审计3份results/compressed_batch_compact_cosim_{model_capacity,allocations,binary_transactions}_20261025_v1.json：44端口/30AXImodel尺寸覆盖、同bundle完整互斥地址、55实际text/binary TV各4完整declared-depth事务；exec34679已exit0。
- scripts/run_compressed_batch_compact_rtl_guarded.py唯一owner1504642/child1508947/exec13729，local compressed_batch_compact_rtl_guarded_v1 stage elaborate，先全部setup hash验证/独立copy，same readonly AW guard，trace guard原文与已执行9case CSRguard完全相同；MemAvailable先验>192GiB（实际约1.2TiB），未缩深度/交易/源码。
- scripts/supervise_compressed_batch_compact_rtl_guarded.py唯一owner1537035/exec63490等原compact编译→有界RTL→原PCpostcheck/4fullsnapshots；新scripts/check_compressed_batch_compact_guarded_rtl.py最终额外核对ROM.dat与RTL、全部保护及性能/快照；scripts/supervise_compressed_batch_compact_guarded_audit.py owner1553441/exec3866等执行后唯一最终审计，预期results/compressed_batch_compact_guarded_rtl_audit_20261025_v1.json。不重复任务，当前无compact整体RTL pass。
- 原CSR guarded334627/342047、snapshot恢复2508987/2516537、globalbus64 HLS1039762及CSRwidth64物理497587继续。完整目标active，实际平台/板卡等缺口保留。

## 最新终态：集成packet-width64综合完成，修复审核解析器后独立通过，LUT估计降15.1%但仍超预算（2026-10-25）

- 原owner673564/exec80434已complete/exit0；监督721786/exec72996因旧parse_source只接受port/offset/bundle/depth、不接受max_widen_bitwidth64而failed，原state/log/receipt/checker保留，绝非综合失败。不重综合。
- 新scripts/search_kernel_memory_plan_v2.py只增加明确验证的max_widen_bitwidth64可选字段，保留字段metadata/顺序/容量/物理身份，严格拒绝重复/未知/非法文本；旧parser未改。tests/test_search_memory_plan_v2.py实际3tests/7非法subcases通过（canonical45arg44ptr完全相同，width字段不改变ABI身份/容量）。新checker scripts/check_compressed_batch_width64_hls_v2.py导入新parser，其余原完整审核保持。
- results/compressed_batch_width64_synthesis_review_20261025_v2.json实际独立审核exit0，1131绑定，actual input_mem RDATA64、其他接口宽度不变、4 full44 snapshots/trace gate仍通过。LUT1632814（原1922947，-290133≈15.1%），FF654085（-69835），DSP93/BRAM69/URAM3不变；estimatedclock仍4.509ns（delta0）>effective3.65且LUT>整片参考1303680，非fit/时序/RTL/板卡通过。parser incident报告同时绑定原失败证据及v2 reconciliation，不覆盖旧失败。
- compact full44 cosim setup1307637/1316436仍运行wrapper C TB测试，exec33730待原终态；不重复。globalbus64、search-only compactwidth64及CSR物理/RTL等原任务继续。完整目标active。

## 最新终态：集成compact压缩batch综合独立审核通过，估计仍超预算；compact cosim准备启动（2026-10-25）

- 原compact HLS owner581295/exec66947已complete，监督637230/exec73005已independently_audited，两exec本轮均exit0收取；没有重跑原综合。local compressed_batch_compact_hls_review.json status compressed_batch_trace_compact_integrated_control_csim_synthesis_verified_rtl_pending，全部1134files绑定本轮再次逐hash核验后原子持久复制results/compressed_batch_compact_synthesis_review_20261025_v1.json，SHA731ce828cc1bbf6619d1065fc7bb898859e547d4707cc2ccb76714c8b4b25720。
- 真实HLS2022.2/U280/5ns/1.35ns，45args44ptr30AXI，full44 Csim4快照+trace independently pass；LUT1937259/FF731186/DSP93/BRAM18K69/URAM3，estimated4.509ns仍>effective3.65ns，超过整片LUT参考1303680（尚未扣shell）。这是HLS估计，不是实际mapping/部署通过；all loop constraints satisfied不表示时钟/平台质量通过。
- 新scripts/prepare_compressed_batch_compact_cosim.py唯一owner1307637/child1316436/exec33730，local compressed_batch_compact_cosim_setup/project compressed_batch_compact_cosim_project，root data/derived/compressed_batch_compact_cosim_setup_20261025_v1/location.json。基于原prepare_compressed_batch_cosim.py改为compact review/mode1、原TB已full44，复用syn且逐hash一致、不重综合；fresh Csim和cosim -setup生成44port四交易goldens并对CPUmode1全payload比较。8GiB单文件限制，尚未setup pass，更没有RTL pass。后续先收原owner终态再查TV/RO allocation、独立执行副本xelab/xsim/PCpostcheck。
- packet-width64 integrated673564接近RTL generation但仍需终态；globalbus641039762、search-onlycompact1180234及各监督继续；CSR guarded334627/342047与snapshot恢复2508987继续，width64物理497587继续。完整目标active。

## 补充：compact search-only width64后综合审核及监督已启动（2026-10-25）

- scripts/check_search_packet_width_compact_hls.py已准备，要求same owner完成receipt/log/frozenfiles、2022.2/U280/5ns/1.35ns、HLSapp两源均mode1、literal2tx[(0,status0,cost35,path2),(1,status3,cost0,path0)]及full_workspace marker；actual input_mem512→64且其他读接口不变、top仅packetpragma差异；原compact xml必须命中frozen boundary_setup artifacts，生成resource/clock delta并绑定所有syn报告/RTL。实际审核未执行，不称综合通过。
- scripts/supervise_search_packet_width_compact_hls.py唯一owner1237085/exec96429等待原1180234，local search_packet_width64_compact_hls/audit_supervisor，freezechecker/plan身份后唯一审核到local search_packet_width64_compact_hls_review.json。原exec88004继续，不重复。
- MCP只读status确认CSR width64物理session vivado-20261025-035512-03ffde3f/PID497587仍source运行1516s、queue0、healthy，未重发source；guarded RTL334627/342047 ps仍活跃31min。其他原集成HLS保持。完整目标active。

## 新进展：compact search-only packet-width64 HLS已启动（2026-10-25）

- scripts/search_packet_width_compact_hls.py唯一owner1180234/child1180444/exec88004，local search_packet_width64_compact_hls/project search_packet_width64_compact_hls_project，root data/derived/search_packet_width64_compact_hls_20261025_v1/location.json。先独立核对原results/search_packet_width64_comparison_20261024_v1.json全部files及旧plan generated，复用其相同width64源码和原compact ASAN/UBSAN preflight_1（二tx status0/cost35/path2和status3）。仅HLSflow两个SEARCH_GRAPH_MODE flags由0→1；不是把CSR结果套给compact，也没有重复跑相同CPU检查。
- 本次实际2022.2 Csim→csynth，U280/5ns/1.35ns/pipeline_loops0、CPU125、RLIMIT_FSIZE8GiB，当前actual log进入csim。相对原compact变量仍为packet max_widen64。新candidate还需独立actual input_mem位宽/资源/clock与原compact HLS比较、2txRTL/原postcheck，再同约束物理对照，不可称负结果已修复。
- 未来compact HLS基线xml路径build/search_kernel_hls_20261024_v3/compact/solution/syn/report/search_kernel_top_csynth.xml，已确认被results/search_kernel_boundary_setup_20261024_v1.json artifacts绑定；可复用其frozen proof做资源对照。当前新compact候选尚无后综合审核器/监督，下一步补齐。
- 原compact物理与新恢复会话已冻结（审核负结果），原CSR width64物理497587、三个集成HLS与guarded/snapshot RTL继续，不重复提交。完整目标active。

## 最新终态：compact原内存设计恢复导出及独立审核已完成，质量明确失败（2026-10-25）

- 新export_existing source在原session vivado-20261024-200724-c151e46f/PID4159154成功结束342.99s，原failed flow仍failed。真实MCP terminal_status.json与export_history.json保存于data/derived/search_kernel_compact_route_export_recovery_20261025_v1，未替造字段。工具cell5328此前已结束running handoff，不再wait。该会话现在idle，原内存设计及恢复结果冻结，后续对照/修复用新副本或新session，避免改变证据。
- scripts/check_compact_route_export_recovery.py实际运行exit0，results/search_kernel_compact_route_export_audit_20261025_v1.json status existing_compact_route_export_recovered_with_quality_failures，SHA749d35f75c358ec1ab58d9dc12e99e0bba85b3c63eacb5f72e34f7aabc9b1d25，26绑定，DCP zip完整性通过、原失败6文件/hash、同PID成功export历史/终态、仅导出无reroute、真实timing/resource/DRC/methodology全部核验。MCPtodos3/3完成指审核流程完成，不是质量通过。
- 实际route errors20204/fully230329/routable250528，setup WNS-6.416/TNS-75991.031/63278fail，LUT110863/FF148176；DRC91（RTSTAT-5/6各1、DPIP-2=16、DPOP-3=21、DPOP-4=51、RTSTAT-10=1），methodology2001（TIMING16=1000、18=1000、44=1）。all_nets_routed/internal_timing/no_DRC/no_methodology均false，internal constraint checks clear仅局部检查。外部IO未platform约束，不能据此推Fmax/200MHz/实卡部署。
- 三集成HLS compact581295、packet-width64 673564、globalbus64 1039762及各监督继续；guarded RTL334627/342047及snapshot local恢复2508987/2516537仍实际compile。原search-only width64物理497587继续。完整目标active。

## 新进展：全bus64候选full44 Csim独立通过、综合后监督启动（2026-10-25）

- scripts/check_compressed_batch_bus64_csim.py→results/compressed_batch_bus64_full44_csim_20261025_v1.json通过：4份946498280bytes full44 snapshots与原CPUmode0逐hash相同，四trace字节相同且v4验收；candidate top与canonical exact，配置文件/flow只出现一次全局64cap，源文件绑定，未改DUT逻辑。
- scripts/check_compressed_batch_bus64_hls.py基于width64审核器调整为graphmode0/globalcap，后续要求实际30读接口位宽等于min(original_width,64)，full44 Csim gate、原资源/clock estimate delta、所有版本/器件/约束/ABI不变等。CLI通过，尚未跑实际最终审核。不能仅配置log称实际bus宽度已生效或资源改善。
- scripts/supervise_compressed_batch_bus64_hls.py唯一owner1096966/exec65528等待原1039762完成后唯一checker到local compressed_batch_bus64_hls_review.json，freeze checker与plan。原exec16359仍运行HLS，source未改、没有重启。
- compact恢复原source工具cell5328已返回300s running handoff（cell已结束！不要再wait5328），实际PID4159154继续export/report_drc；methodology已完成，DRC/summary待齐。后续按MCP session vivado-20261024-200724-c151e46f退避status，不重复source。其他长任务保持，完整目标active。

## 新进展：全m_axi统一64位扩展上限消融已启动（2026-10-25）

- 本机2022.2 vitis_hls help config_interface实证支持-m_axi_max_widen_bitwidth，完整help/receipt local hls_interface_options_20261025_v1（exec85299已exit0），不使用2026-only选项。原compressed CSR实际30接口中多个512位，不止packet；因此新增一个单配置因素候选，不能预设面积或速度收益。
- scripts/compressed_batch_bus64_hls.py唯一owner1039762/child1039914/exec16359，local compressed_batch_bus64_hls/project compressed_batch_bus64_hls_project，root data/derived/compressed_batch_bus64_hls_20261025_v1/location.json。源码仍canonical exact（无packet pragma改动），仅flow增加config_interface -m_axi_max_widen_bitwidth64；移除该行后flow与width64 CSR fullTB流程逐字节相同，single_variable_configuration.json绑定证据。CSRmode0、full44 TB、U280/5ns/1.35ns/pipeline_loops0、CPU122、RLIMIT_FSIZE8GiB。实际log已执行配置并开始Csim，非抽象计划。需要独立full44 Csim/syn审核与实际宽度资源对照，再RTL/物理，当前尚无候选通过结论。
- compact原恢复export PID4159154仍reports（timing/util/check/methodology已出现，DRC/summary未齐）；exec cell5328继续待原source返回，不重复。原负结果WNS-6.416/20204conflicts保持。其他HLS/RTLowners不重启。完整目标active。

## 补充：compact恢复已导出DCP，实际setup WNS=-6.416ns，报告仍在生成（2026-10-25）

- 原session4159154的新export恢复已越过write_checkpoint，routed.dcp约100MB已闭合，state running/reports；未重布线。新routed timing/utilization/route_status已输出：5ns/1.35ns，setup WNS-6.416ns/TNS-75991.031ns，63278/360459 setup失败；hold0.019ns与pulse1.958ns仅各自通过。LUT110863/FF148176/RAMB36=225/RAMB18=16/DSP77。route errors/resource conflicts20204、fully230329/routable250528仍然负结果，不能声称route合法/200MHz/Fmax。
- results/search_kernel_compact_route_export_observation_20261025_v1.json绑定三个已完成partial报告及限制；最终DRC/methodology等仍在生成。scripts/check_compact_route_export_recovery.py已准备，需complete state+成功MCP终态/status/history、DCP zip integrity、全部timing/resource/DRC/methodology及negative quality gates、冻结原失败证据/仅导出script等独立审核。CLI已检查，最终审核未运行。
- functions exec cell5328仍等同一source工具返回，不重复source。原width64物理497587与HLS/RTL owners保持，完整目标active。

## 重要新终态：原compact物理已失败，已启动原内存设计导出恢复（2026-10-25）

- MCP status原session vivado-20261024-200724-c151e46f实际idle,last_completed_code1,elapsed24972.611s，不再运行原source。原state failed/routing，log明确route_design completed successfully但随后write_checkpoint routed.dcp写临时search_kernel_top.edf报Designutils20-2054；写失败与当时quota事件相关性可疑但根因未证明。不要再按旧条目当作在布线。
- 先将原完整log/state/error/flow/XDC/plan六文件逐hash复制冻结到data/derived/search_kernel_compact_route_export_recovery_20261025_v1/failed_original_*，incident.json保存。未修改原failed state或原DCP。
- 随后同一idle会话只读report_route_status真实显示routable250528、fully routed230329、routing errors20204/resource conflicts20204、antennas5！负结果，不是合法路由；route_design command成功不等于无冲突。
- 新export_existing.tcl与export_plan.json仅导出同一内存设计和报告，不重综合/place/route；source已唯一提交原session，PID4159154，functions exec cell5328待返回（工具可能300s handoff，命令仍继续，不重复source）。新output同上目录，原a_reports逻辑复制为独立前缀，cd新目录后write_checkpoint/reports；保留所有timing/DRC/methodology负结果。MCPtodos preserve done/export active/audit pending。
- 新width64 search-only物理session497587与集成HLS/RTL原owners继续，完整目标active，不能因恢复导出成功就称compact物理质量通过。

## 补充：原9需求/8变体完整范围状态快照已生成（2026-10-25）

- scripts/snapshot_experiment_completion.py生成根EXPERIMENT_STATUS_20261025_v1.json，保留原EXPERIMENT_STATUS.json及全部9项原需求文字、configs/experiment.json全部8变体，不改冻结旧文稿/配置。绑定来源SHA，明确metadata review不是重执行语义审核/完成声明；complete=false、goal active。
- 回查已有统计审核终态：native_site63workers、source_to_route21、template_scope35、conversion14均已有完整报告，而旧总状态仍有running字样。新状态引用完整报告范围与限制，不把CPU captured-TSV→两批统计当采集/训练/板端全链，也不把负结果抹去。source-to-route compact/direct对CSR配对中位比1.42397376，compact/expanded0.89520303（应用wall两批口径；shared host/cache限制）。
- 状态快照同时记录新CSR/compact/width64证据及6个local owner实际/proc命令；核心剩余明确：14实例以外特殊资源、整体RTL/时序资源fit、真实platform/DDR-HBM/功耗/板端全链。XRT新探测仍0devices。快照是当时观测，不是新进程终态。
- 当前长任务继续，执行侧不得因状态快照出现就缩小或完成完整实验目标。

## 补充：整批CSR guarded RTL最终独立审核已准备并启动监督（2026-10-25）

- scripts/check_compressed_batch_guarded_rtl.py要求原execution complete/parent prepared、frozen setup全部hash、driver hashes、allocation证据与全部RO bundle保护范围一致、模型仅追加guard且其余DUT逐字节相同、原cosim.pc.exe相同、9例guard测试log绑定、elab/RTL/postcheck receipt/log无错误、实际4/4 progress及4笔正cycle性能记录、4份946498280bytes完整snapshot与HLS CPU相同、全部RTL output TV绑定，最终output results/compressed_batch_guarded_rtl_audit_20261025_v1.json。CLI已检查，实际尚未最终审核！保留合成4node/full44capacity而非真实流量、CSRonly、无物理或板卡结论的限制。
- 新scripts/supervise_compressed_batch_guarded_audit.py唯一owner779628/exec47375，local compressed_batch_guarded_final_audit_v1，等待原执行监督397193（后者仍等elab334627/342047），identity/startticks守卫，freeze checker hash后只审核一次，不重启仿真。原有exec4723/51340继续，尚无RTL pass。
- compact HLS581295与width64 HLS673564及其监督637230/721786均保留原任务；search-only width64物理497587上轮MCP约451s running，后续按退避status，不重发source；完整目标active。

## 补充：集成width64后综合审核与监督已启动（2026-10-25）

- scripts/check_compressed_batch_width64_hls.py基于已用CSR/compact审核器，绑定full44 Csim证据，确认-DSEARCH_GRAPH_MODE=0、实际input_mem RDATA=64、其他29接口位宽与原compressed CSR均一致、45args44ptr、版本/器件/5ns/1.35ns等约束；资源/clock estimate直接对原results/compressed_batch_synthesis_review_20261025_v1.json生成delta。独立HLS成功不代表RTL/物理/平台fit。CLI已检查，实际审核待原综合结束。
- scripts/supervise_compressed_batch_width64_hls.py唯一owner721786/exec72996已启动，bundle compressed_batch_width64_hls/audit_supervisor，等待同一原owner673564，冻结checker/plan/hash后唯一审核到local compressed_batch_width64_hls_review.json，不重复提交。
- MCP只读status实态确认width64物理session vivado-20261025-035512-03ffde3f source仍运行约451s，process497587、queue0、healthy，未重发source。其编译仍需等待；原compact物理需>=600s退避另读，未动其他baseline会话。
- compressed guarded334627/342047、compact HLS581295/582574及各监督继续原任务；完整实验active。

## 新进展：集成batch packet-width64单变量候选已启动，full44 Csim独立通过（2026-10-25）

- scripts/compressed_batch_width64_hls.py唯一owner673564/child673660/exec80434，local compressed_batch_width64_hls/project compressed_batch_width64_hls_project，data/derived/compressed_batch_width64_hls_20261025_v1/location.json。原canonical compressed top仅packet m_axi pragma追加max_widen_bitwidth=64，single_variable_change.json记录原/新hash和唯一pragma差异、原search-only候选RTL前驱SHA。未改算法/控制/容量/约束或canonical基线。CSRmode0、full44 TB、U280/5ns/1.35ns/pipeline_loops0、CPU124、RLIMIT_FSIZE8GiB。
- 新scripts/check_compressed_batch_width64_csim.py与results/compressed_batch_width64_full44_csim_20261025_v1.json独立通过：4份946498280bytes完整端口快照与原full44 CPUmode0逐hash相同，4trace字节一致+v4语义验收，candidate去除新pragma后与canonical逐字符相同且hash一致；绑定source/单变量记录。Csim不能证明AXI RTL调整等价或资源改善。实际HLS已进入综合，尚无后综合审核器/监督；下一步仿原compact审核，必须确认actual input_mem RDATA64、其他接口未改、资源/时序与原compressed CSR对照，之后RTL补证。
- 原width64 search-only物理source exec cell5278已返回300s running handoff并结束该工具cell，实际Vivado command继续；不要再wait cell5278/不要再source。下次按session vivado-20261025-035512-03ffde3f只读status检查，当前物理仍需等待。原start_raw/session/plan均保留。
- compact压缩HLS581295/582574及监督637230继续；compressed guarded334627/342047、snapshot2508987/2516421继续actual elaborate，均不重复提交。完整目标active，资源/整体RTL/平台/板卡等不足未被Csim取代。

## 新进展：compact full44 Csim独立通过，综合后审核监督已启动（2026-10-25）

- results/compressed_batch_compact_full44_csim_20261025_v1.json由scripts/check_compressed_batch_compact_csim.py生成：4份946498280bytes全44端口HLS Csim快照与已审核CPU mode1完整快照hash相同，四trace字节一致且v4正常/seed/error语义验收。首次checker误选旧trace_v2_cpu（capacity metadata不同）导致拒绝，改用被full44 CPUreport绑定的compressed_batch_rtl_tb_cpu_v2对应trace后通过，未改DUT/输入/验收内容。
- scripts/check_compressed_batch_compact_hls.py为单独compact后综合审核器，基于原CSR审核，graphmode=1、45args44ptr30AXI、2022.2/U280/5ns/1.35ns、完整full44 Csim gate、全部frozen证据复核；尚未实际运行，不称综合通过。
- scripts/supervise_compressed_batch_compact_hls.py唯一owner637230/exec73005，bundle原compact_hls/audit_supervisor，等待原581295后运行新checker到local compressed_batch_compact_hls_review.json，冻结checker/plan hash。原compact owner581295/582574持续实际综合，不重复提交；exec66947待收。
- width64物理497587仍synthesis，exec cell5278原source待返回；compressed guarded334627仍elaborate，原supervisor397193保留。所有整体RTL/平台/板卡缺口仍在，完整目标active。

## 新进展：compact压缩batch full44 Csim→综合已启动，板卡重新探测仍0（2026-10-25）

- scripts/compressed_batch_compact_hls.py新唯一owner581295/child582574/exec66947，本机bundle compressed_batch_compact_hls/project compressed_batch_compact_hls_project，data/derived/compressed_batch_compact_hls_20261025_v1/location.json指向，实际2022.2 log和/proc确认在执行csim_and_synthesis，不重复启动。先原400trace gate逐hash，使用原canonical compressed top/source，仅-DSEARCH_GRAPH_MODE=1，TB改用已审核full44完整深度test_compressed_batch_rtl_full_depth.cpp（与CPUreport绑定一致），A_BATCH_RTL_SNAPSHOT_PREFIX=out/csim，4笔约946MB全端口快照。U280/5ns/1.35ns/pipeline_loops0，CPU126，prlimit stack64MiB；新增继承RLIMIT_FSIZE=8GiB单文件上限防verbose失控，触发则失败保留，不能弱化约束。此任务不是RTL cosim；成功后需独立检查syn/ABI/资源、4份快照与CPU mode1相同及trace解码，再准备mode1 RTL。
- data/derived/xrt_environment_recheck_20261025_v1/保存本次xbutil examine host JSON/日志/receipt及hash，XRT2.14.354，0devices、无/dev/dri、无/opt/xilinx/platforms。本机仍不可实板测量；不推断远端无卡，也不把此局部依赖当整个目标blocked。继续其他实验。
- width64物理PID497587仍running/synthesis，exec cell5278待原source返回；compressed guarded334627/342047仍elaborate，supervisor397193继续，不重复提交。完整目标active。

## 补充：width64物理独立审核器已准备，仍无终态（2026-10-25）

- scripts/check_packet_width64_physical.py为新候选单模式审核器，复用原check_search_kernel_physical_mode的解析器/quality gates；要求complete state、成功idle MCP terminal observation与exact source history、同PID/work、全部frozen hash、原baseline flow/XDC相同、实际器件license、3DCP、完整synth/routed资源/时序/DRC/methodology及约束覆盖。对原results/search_kernel_physical_csr_audit_20261024_v1.json生成实际资源和WNS delta，所有quality gates原样保留；CLI --help已检查，实际审核待run结束后执行。
- data/derived/search_packet_width64_physical_20261025_v1/start_raw.json保留完整原MCP start响应。最终需先保存原始MCP status为{observed_utc,status:raw}及完整history JSON再调用审核器，不能补造terminal证据。当前exec cell5278仍待同一source返回，PID497587此前ps确认active/synthesis，不重发source。
- compressed guarded334627/342047、监督397193及snapshot2508987依旧ps活跃；本轮没有新RTL终态结论。

## 新进展：width64候选同约束CSR物理流程已实际启动（2026-10-25）

- scripts/prepare_packet_width64_physical.py先核验results/search_packet_width64_rtl_audit_20261025_v1.json全部489files绑定，再复制其已验证原syn RTL/ROM到data/derived/search_packet_width64_physical_20261025_v1/csr/source，plan.json冻结来源/generated。clock.xdc和run_flow.tcl与原CSR物理基线逐字节一致，U280/5ns/1.35ns/2threads/OOC全器件，无shell、不补外部AXI延迟、不加waiver。
- MCP先list现有session后新建专用Tcl session vivado-20261025-035512-03ffde3f PID497587，LD_PRELOAD libudev；已唯一source run_flow.tcl，真实state.json running/synthesis且ps活跃。functions exec cell5278仍在等待该原source工具返回，不重复source；wait cell5278接收工具handoff即可，后续按MCP status退避读取，不能把观察超时当失败。session.json持久记录。MCPtodos inputs done / physical active / audit pending。
- 尚无物理时序/资源结果，保持原CSR baseline、physopt v2及原compact会话冻结/不干扰。该候选原HLS估计LUT209624/FF130669/clock3.65ns，真实RTL2txcycles2132461/12404；不要把这些称实际路由结果或带宽。整体batch尚未采用此变量，full-real/边界RTL也未补齐。
- compressed guarded334627/342047与supervisor397193仍ps活跃elaboration/waiting；完整目标active。

## 新进展：原搜索边界RTL两模式已完整通过并重新验绑定（2026-10-25）

- 原boundary owner1530495与监督3099710已退出，data/derived/search_kernel_boundary_rtl_20261024_v1/state.json为complete/csr+compact。results/search_kernel_boundary_rtl_audit_20261024_v1.json已存在，本轮全部952 artifact hash重新核验，原literal postcheck及实际8笔performance transaction再次检查通过；补充results/search_kernel_boundary_rtl_revalidation_20261025_v1.json。CSRcycles[2178178,37537,37684,37705,86887,37684,37705,80839]，compact[2181454,40792,40939,40981,90163,40939,40981,84094]。合成边界状态capacity[32,16,8]、full declared workspaces，非全真实流量/peakheap/板卡/整体batch RTL。
- 其余site52、tree50、retained nodes37、edges37 owner与实际xsim leaf均ps确认仍运行且CPU约100%。当前日志分别33/52、1/50、1/37、1/37；模拟时间前进。不能仅据进程活着称功能正常，也不能只因交易计数慢就判死锁；retained_nodes第二笔实际校验并写1,048,576节点，需完成大量非流水AXI访问。保留原进程不重复提交，后续按原有界运行和最终交易/后检查验收。
- 主compressed guarded owner334627/child342047仍elaborate，后续supervisor397193保持同一等待；snapshot local owner2508987/child2516421仍elaborate。完整实验active。

## 新进展：RO检查器9例实际XSim通过，后续监督已启动（2026-10-25）

- scripts/test_compressed_axi_ro_guard_v2.py抽取当前实际trace_mem guard原文运行Vivado2022.2 XSim，9例通过：合法meta/data、长INCR、未握手、FIXED合法；RO首/末byte和跨边界写、未知地址、不支持WRAP分别fatal且无PASS。results/compressed_axi_ro_guard_tests_20261025_v1.json。初v1单独bundle因xvlog默认work库而xelab错误引用xil_defaultlib失败，保留；v2修正work.tb，未改guard/DUT。此为trace guard隔离验证，非整体RTL结果。
- scripts/supervise_compressed_batch_rtl_guarded.py唯一owner397193/exec51340已ps确认，等待原elaboration owner334627，bundle compressed_batch_rtl_guarded_execution_v1。原owner完成prepared后，验证9例gate/guard hash和receipt，执行10sec模拟时间有界xsim，再原cosim.pc.exe，A_BATCH_RTL_SNAPSHOT_PREFIX单独out/rtl避免覆盖golden，4份全44端口snapshot逐字节hash对照原HLS CPU；成功也仅review_pending，仍须独立transaction XML与最终审核。不重复提交。
- 主elaboration owner334627/child342047仍ps活跃，stage elaborate；旧snapshot2508987亦活跃。完整目标active，不将这些编译/隔离检查当整体RTL或板卡通过。

## 新进展：压缩批处理独立 guarded RTL 已启动（2026-10-25）

- scripts/run_compressed_batch_rtl_guarded.py 唯一owner334627/child342047/exec4723已由ps确认活跃，local compressed_batch_rtl_guarded_v1，stage=elaborate。先验证原setup全部hash，再复制sim；原DUT RTL逐文件相等，仅AESL AXI模型加入保守RO AW burst重叠fatal检查（零WSTRB也拒绝，未知地址/不支持burst也拒绝）。复用生成的2022.2 xelab命令，-mt off/--O0/--stats，未动冻结setup。当前owner只执行elaboration，成功状态prepared/elaborated_rtl_execution_pending，不会自动跑xsim/postcheck；后续须验证guard本身并追加独立有界RTL运行+原C postcheck。不要重复启动！
- results/compressed_batch_cosim_model_capacity_20261025_v1.json静态审核44port/30model容量覆盖；results/compressed_batch_cosim_allocations_20261025_v1.json核对wrapper全部44区域完整、同bundle不重叠；results/compressed_batch_cosim_binary_transactions_20261025_v1.json已审核55份实际text/binary memory TV文件各4完整declared-depth事务。指针地址scalar文件不是内存payload；tiny模型用text，large用binary，两种均独立检查。以上均不代表RTL功能通过。
- snapshot local原owner2508987/child2516421仍ps活跃，不重复运行。完整实验继续，所有原资源/时序/平台/板卡/特殊资源缺口仍待解决。

## 最新归档与容量修复已完成（2026-10-25）

- 已完成33,866,385,651bytes/8168文件的字节校验持久备份，data/derived/frozen_local_evidence_20261025_v1/manifest.json。9个关键审核报告涉及的2024个local依赖已核对全部由备份覆盖且hash匹配，results/frozen_local_evidence_archive_audit_20261025_v1.json通过。保留原local副本；需恢复时使用scripts/restore_frozen_local_evidence.py MANIFEST --relink-missing（只补缺失路径、不覆盖不同文件，支持备份目录整体迁移）。明确排除仍活跃snapshot local recovery/project，后续其终态另归档。此前async归档目录问题已由项目内空间恢复解决，无需等待答复。
- 根因定位并处置：旧heap综合2468371未完成pop.verbose.sched.rpt达2.52TB，保留完整源码/plan/log+2MiB头尾，停止仅此旧试验及其残留tee，确认未被任何已发布heap审核绑定后仅删除此可再生verbose缓存。共享卷从满额恢复约2.3TiB。旧owner2468333最终failed，wrapper exit0但最终completion markers缺失，不能判成功。results/search_heap_verbose_storage_incident_20261025_v1.json及terminal报告保留证据；没有删路由数据/源代码/冻结已审核结果，不重跑该失控候选。未来长综合应限制单个verbose报告增长，不能再让辅助日志耗尽主实验配额。
- quota曾使results/compressed_batch_full_depth_cosim_setup_20261025_v1.json创建0byte；现已原子复制修复为已审核完整setup metadata，SHA13eb98c22d81677e50fcca271e9de00f4f127abab8896930caf70bc0ad466853。根AGENTS/NEXT均已原子更新。实际新top仍未RTL执行，下一步44port TV/RO AXI写地址完整性→新execution copy xelab/xsim/postcheck。
- 新发现原packet-width64 RTL已在02:04独立通过，results/search_packet_width64_rtl_audit_20261025_v1.json status=packet_width64_csr_two_transaction_rtl_and_original_postcheck_verified，实际cycles[2132461,12404]对原[2132461,12383]，第二笔+21cycles（0.1696%），不是加速/设备带宽证据。2297545/2339367已退出，不再等待；后续可做同约束CSR OOC物理对照评估实际时序，尚未执行该物理试验。原compact物理source仍需按MCP只读实态、>=600s退避，不发送重复source。
- 当前四真实压缩CPU批次完整审核均通过（每95.958847MiB）、压缩HLS审核完成但1922947LUT/4.509ns估计不达预算，full44端口CPU/HLS快照与cosim setup通过但非RTL pass。唯一活跃snapshot local恢复2508987/exec92733仍需实际状态接收。完整实验目标active，整体RTL、资源/时序优化与平台/板卡、特殊资源缺口未完。

## 最新：四真实压缩诊断完整通过；full44端口CPU/HLS快照与cosim setup通过，RTL未执行；已解决超大临时报告导致的配额问题（2026-10-25）

- compressed_batch_real owner1803274/exec28167已complete/independently_audited，CSR/compact各两1062网batch。results/compressed_batch_real_audit_20261025_v1.json 全32绑定再次核验，SHA635f03e951a657d7aff53bc9f8bddf180643fdf4d2056a655ea3eb01e66c7d1b；原raw中间/末态/CC/SC/KC、每search cost/expanded/blocked/unknown全成员及最终roots/8字段边/demands均一致。每批12577518u64=100620144bytes=95.958847MiB，16836searches/4248nets/7round snapshots，128MiB内。真实CPU诊断，不是实板。旧plain布局完整等价593241928bytes，省83.0389%，精确布局重序列化计量不是另跑plain实现，更非速度/带宽/功耗。
- 新full TB生成器prepare_compressed_batch_rtl_tb.py→test_compressed_batch_rtl_full_depth.cpp/inventory，每44port实际extent>=declared，trace实际16777217u64/capacity16777216，每call保存完整44BO payload，946498280bytes/份。首inline编译缺packet helper失败保留；test_compressed_batch_rtl_full_depth_cpu.py用独立source copy解决路径，两模式ASAN/UBSAN/4case全部通过。results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json验证每port depth/width/id/全字节长度/主trace与snapshot committed区逐字节相同。仅逻辑4nodes但全声明指针深度，不能称max生产traffic。
- prepare_compressed_batch_cosim.py owner2648921/exec76368已complete，local compressed_batch_cosim_setup/project compressed_batch_cosim_project。复用原compressed syn、不重综合；4份CSR HLS Csim/wrapper C快照与ASAN full CPU payload逐字节相同，AUTOTB_TRANSACTION_NUM4，sim RTL等于原syn。setup.json980绑定再次全核验，SHA13eb98c22d81677e50fcca271e9de00f4f127abab8896930caf70bc0ad466853。metadata持久复制results/compressed_batch_full_depth_cosim_setup_20261025_v1.json（首次配额写失败0-byte现已原子修复，不是有效旧证据覆盖）。尚未xelab/xsim/postcheck！下一步查实际44port TV深度、RO AXI写地址监测，另execution copy启动RTL；host RO snapshots不证明RTL const地址完整性。HLS/新RTL目前CSR，compact仍缺。
- compressed HLS1860773/监督1872988均complete。1110绑定再次全核验，results/compressed_batch_synthesis_review_20261025_v1.json：LUT1922947/FF723920/DSP93/BRAM69/URAM3，4.509ns>有效3.65ns；对plain诊断+63928LUT/+19059FF。整片参考LUT1303680，仍非mapped fit/时序/板卡通过。资源限制单独review，不用metadata通过冒充可部署。
- snapshot旧恢复848340/859354明确Disk quota exceeded exit1，2744.762s/RSS42101108KiB，OOMkill前后1未变，不证明原SIGKILL原因。已保留新quota incident。新local恢复owner2508987/child2516421/exec92733仍实际阶段elaborate，local snapshot_rtl_local_recovery/project snapshot_rtl_local_project，同30交易/full深度/原RTL/mt off/O0不变，自动RTL/postcheck/audit预期local snapshot_rtl_local_review.json，不重复提交。
- 配额主因定位旧heap HLS2468371（owner2468333，exec16547）：未完成pop.verbose.sched.rpt达2522672529408bytes（2.52TB），耗时约11h写展开条件。确认是本项目未绑定、可再生编译诊断缓存，完整source/plan/log及2MiB head+tail已保留，终止该旧实验及自己的残留tee后，仅清理此verbose缓存；所有路由/源数据不删。旧flow最终failed，wrapper receipt0但缺completion markers，不能作综合成功。results/search_heap_verbose_storage_incident_20261025_v1.json/terminal报告记录全过程。共享卷恢复约2.3TiB，可继续项目内持久归档；无需等待先前async目录问题。另terminal snapshot .autopilot cache722文件逐hash搬local、原路径symlink保留，未碰active项目。
- 新promote_frozen_local_evidence.py owner3940909/exec21589已complete，备份8168文件/33866385651bytes到data/derived/frozen_local_evidence_20261025_v1/payload，复制逐字节流hash+目标重读验证。manifest.json仅全部成功后生成；restore_frozen_local_evidence.py用于校验/仅重链缺失/tmp路径。明确排除active snapshot_rtl_local_recovery/project和动态handoff/progress，未删原local资料。manifest完成后需核对全部关键report的local绑定覆盖，不能提前声称已全归档。
- MCP只读确认原compact物理4159154/session vivado-20261024-200724-c151e46f仍同一source约400min/queue0；未新Tcl，按600s退避。完整目标active，RTL执行、资源/时序优化与映射、平台/板卡和特殊资源语义仍未齐。ROOT文稿后续必须temp+fsync+replace原子更新，不能在quota时truncate已有AGENTS/NEXT。

## 最新：压缩诊断四真实批次已启动，首CSR批实际trace95.96MiB；压缩HLS已启动，无压缩诊断基线综合审核通过但估计超资源（2026-10-25）

- 新compressed_batch_real_pipeline.py唯一owner1803274 / exec28167，workers CSR1804329、compact1804332，已/proc确认运行；bundle=/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_real，root data/derived/compressed_batch_real_20261025_v1/location.json持久pointer。gate为400case+400exact traces v4独立通过、O2 v2 build完整hash/receipt/仅已知warning。按原CSR/compact各两1062网batch/cache4096/80round/budget200000/cap8，env A_BATCH_TRACE_OUTPUT_PREFIX导出四份128MiB预算trace，raw stdout及CC/SC/KC保留。owner等待两workers全部终态后唯一check_compressed_batch_real.py对原batch全真实raw完整中间/末态、所有search unknown成员、最终route/path/demands及v4全trace核对，预期results/compressed_batch_real_audit_20261025_v1.json。不重复执行/竞争审核。
- 首CSR trace_0_0.bin已关闭，实际committed100620144bytes=95.958847MiB，capacity134217728bytes，21093 records，sticky0且终态raw result=[0,7,0,4,4248,16836,16836,1,0,0,0,3]。results/compressed_batch_real_first_trace_observation_20261025_v1.json保存hash/metadata/terminal；仅容量及终态观察，完整语义审核尚未结束，其他批次仍运行。
- 新compressed_batch_hls.py唯一owner1860773 / child1861147 / exec61552，source为经两模式CPU/400trace验收的canonical search_batch_trace_top_v2，实际2022.2/xcu280/5ns/1.35ns Csim→csynth，本机bundle compressed_batch_hls/project compressed_batch_hls_project。Csim已过并进入实际综合，尚无综合通过结果。新唯一supervise_compressed_batch_hls.py owner1872988 / exec72097，等待该原owner后check_compressed_batch_hls.py审核实际约束/45args44ptr30AXI/生成RTL资源warning及Csim二进制与CPU新格式一致，再v4解码；预期/tmp/.../compressed_batch_hls_review.json。root data/derived/compressed_batch_hls_20261025_v1/location.json给出路径，别与原无压缩基线混淆。
- 新compressed_batch_trace_memory_plan.py/checker生成hardware/vitis/compressed_batch_trace_memory_v1，新top名cfg，不复用旧kernel名；44独立BO946561024bytes/31名义HBM通道。results/compressed_batch_trace_memory_audit_20261025_v1.json及memory_tests报告通过16损坏拒绝；仍是源ABI候选，实际XO/control offsets/group映射/platform/44BO设备分配未证。新test_compressed_trace_capacity.py/checker两模式16cuts+exactfit+3非法控制均通过，results/compressed_trace_capacity_cpu_20261025_v1.json，type6 epoch按25word位置核对。
- 原无压缩trace本机恢复owner1310895/监督1314947已complete并独立审核。331文件hash本轮全核对，通过report从/tmp/.../trace_hls_synthesis_review.json复制到results/search_batch_trace_local_recovery_synthesis_review_20261025_v1.json（SHA5f393787e0deff80b6162e838bc7af116fb1cd5354c3752e6829187749738991）。LUT1859019/FF704861/DSP93/BRAM69/URAM3，4.509ns>effective3.65；HLS估计LUT已超过整片参考1303680且未扣平台，不可称可部署/时序通过。资源补充review保存限制；bulk源/RTL仍在临时local，只有报告metadata已持久复制。原exec27921/80022终态待收取。
- snapshot恢复848340/859354仍需按实际/proc接收原任务；不重启。共享空间仍紧，已用async询问可用持久归档目录/扩容安排，尚未获答；不等待此答案而停止local独立工作，不能把/tmp当持久交付。完整实验active，无新RTL/200MHz/实板通过结论。

## 最新：全部400份压缩trace经修正reader独立验收；O2 v2真实router已构建成功（2026-10-25）

- export_compressed_batch_cases.py原1594056/1603285已结束：400份实际binary全部导出成功、export receipt0且stdout与原400case差分完全一致，但原pipeline在independent_decode400阶段因Wrong round decision失败。原state/log不改。首帧case_0_0：24nodes/3nets全incomplete，无冲突，内核r=[0,0,3,1,0,0,0,1]正确。旧read_round_trace.py用int(conflict or incomplete)把数量3误作action3，校验器错误非内核错误。
- 新read_round_trace_v2.py修正为positive-count predicate；read_batch_trace_v4.py接此round reader，其余原全部校验保持。tests/test_read_round_trace_v2.py两测试覆盖2/3/65536 incomplete与错误action拒绝。对原400导出无需重跑内核，新独立复核全部通过，总4938searches/3750net snapshots/1250rounds，results/compressed_batch_trace_cases_20261025_v2.json status=compressed_batch_all400_native_differential_and_exact_trace_v4_independently_verified_real_workload_pending。后续使用v4，不用旧v3误拒绝多incomplete情况。
- compile_compressed_batch_router_v2.py owner1687584 / exec22477已正常exit0，compile_csr_regular_v2/compact/router_v2全PASS，regular_build_complete_v2.json存在且binary hash一致。两top日志各仅1条已知unused trace_control warning，本轮已精确核对，无其他warning。driver仍-Werror。旧v1构建失败保留。可执行=/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router/router_v2。
- 下一步以已通过400trace/regularbuild的该binary运行CSR/compact各两真实1062网batch（原cache4096/80round/budget200000/cap8不变），A_BATCH_TRACE_OUTPUT_PREFIX指向本机local目录，独立对照原batch_router_full raw/CC/SC/KC，并用v4完整验收四份实际compressed trace/实际占用容量。当前尚未启动新real诊断，不宣称fit。
- 原本机无压缩trace HLS1310895/监督exec80022、snapshot恢复848340/859354仍需按/proc接收，不重复提交。root共享空间紧张，本轮仅终止旧snapshot cache168文件搬/tmp后保路径，active项目未迁移。完整目标active，无新HLS/RTL/设备通过结论。

## 最新补充：compressed O2构建v1因内部unused参数告警失败，已保留并启动v2（2026-10-25）

- owner1620758 / exec92567已终态失败，compile_csr_regular.log实际-Werror=unused-parameter：batch_worker的trace_control未使用（外层wrapper实际检查它），不能继续称在构建。源码已被CPU/400差分绑定，未修改源码。
- 新compile_compressed_batch_router_v2.py / owner1687584 / exec22477，计划regular_build_plan_v2.json，输出sink_{csr,compact}_regular_v2.o/router_v2/regular_build_complete_v2.json。仅top编译添加-Wno-error=unused-parameter使该warning保留可见，其他-Werror不变，driver仍全部-Werror；后续需审核实际warning只为已知参数，不能省略warning。旧失败plan/log/receipt保留。
- 400独立trace导出原1594056/1603285（exec90320）继续，同一已验证ASAN binary未改。其完整独立验收目标仍results/compressed_batch_trace_cases_20261025_v1.json。不要在此gate通过前宣称real trace已验证。

## 最新：无损集合编码已接search/batch新入口，两模式CPU逐字段等价；400case差分通过并正在逐批导出独立验收（2026-10-25）

- 新search_trace_v3.hpp type6 header12=[6,words,iteration,query,target,nroots,nunknown,npips,node_encoding,node_bytes,pip_encoding,pip_bytes]，后接raw81/packed roots/path及两exact sets；bitmap直接迭代，无百万node scratch，预检全frame容量后写，count0仍忽略旧bitmap。原v1/v2 writer/证据不动。derive_search_batch_trace_top_v2.py→search_batch_trace_top_v2.cpp仅换默认name/include/search call，其他net/round/history/begin/terminal原payload保持。
- 新read_compressed_search_trace.py独立解set→单frameplain→旧search reader；read_batch_trace_v3.py支持mixed type1/6并沿用v2继承与全局计数。test_search_batch_trace_v2.py在/tmp/.../trace_v2_cpu两模式原4case ASAN/UBSAN通过，tests/test_read_batch_trace_v3.py 3测试通过，6份正常trace解码search/net/round/history/terminal全部字段与旧实际trace完全等价（seed仍complete=false），errorcase仍拒绝。dump_search_trace_v3.cpp实际1048576node全bitmap压成4bytes并独立恢复全部成员，另检查满buffer/sticky不改prefix。results/search_trace_v3_cpu_20261025_v1.json及reader_dependencies报告绑定；尚无本新入口HLS/RTL/真实容量结论。
- 新prepare_compressed_batch_router.py owner1478928 / exec31050已complete；bundle=/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router，root data/derived/compressed_batch_router_20261025_v1/location.json指向它。将新compressed top加仅CPU observer守卫，synthesis预处理token相等，Context新分配128MiB诊断BO；初态fresh ledgers显式reset1，保持原完整400case source/driver。check_compressed_batch_component.py已独立通过，results/compressed_batch_component_20261025_v1.json：400cases/4938searches/3750net snapshots/1250rounds中间及末态全等，本轮426绑定hash一致。不是RTL等价。
- 新export_compressed_batch_cases.py owner1594056 / child1603285 / exec90320，已/proc+state核实stage=export400：在已通过gate后相同ASAN binary启用A_BATCH_TRACE_OUTPUT_PREFIX，保存全部400二进制trace，之后独立v3 reader逐批/总覆盖核对，目标results/compressed_batch_trace_cases_20261025_v1.json。不能提前称全部独立解码通过，不重复提交。新compile_compressed_batch_router.py owner1620758 / exec92567正在同bundle单独O2 regular对象+真实router构建，不覆盖已绑定ASAN proof。后续gate完成后用新binary执行两模式各两真实1062网batch并实测trace容量，仍需独立raw和trace对照。
- 共享空间再次接近满，确认原snapshot v1 owner终止后仅搬其failed xsim.dir编译cache807MiB到/tmp/.../failed_snapshot_xsim_cache，168文件逐hash一致+原路径symlink，manifest snapshot_cache_relocation.json；active snapshot恢复项目未移动。释放后约688MiB，仍紧张。大artifact继续本机，需后续持久归档。
- 原无压缩trace HLS本机恢复1310895及监督仍原进程；snapshot恢复848340/859354仍elaborate；原687570 HLS已failed IO，勿按旧AGENTS说在跑。完整实验active，无新HLS/RTL/200MHz或板卡结论。

## 最新：无损unknown集合codec CPU通过，真实集合载荷降至约44.3MB；诊断HLS遇共享卷满后本机隔离恢复（2026-10-25）

- 新search_trace_set_codec.hpp提供sorted-u64 maximal run(gap,length)最短ULEB128编码，若不比raw8bytes/key更小则原样raw回退，保留全部成员及UINT64_MAX。预检非法/重复/乱序/count/cap后才写，tail零padding。独立read_trace_set_codec.py拒绝非最短/overflow/run/count/padding/非canonical raw。tests/test_trace_set_codec.cpp严格C++14-Werror ASAN/UBSAN实际506cases（含1100754元素满量、64bit末端、raw回退/容量拒绝）+Python3测试通过，results/trace_set_codec_cpu_20261025_v1.json绑定。尚未接top/综合。
- measure_trace_set_codec_real.py唯一owner1235466 / exec98032已complete，CSR/compact各两批实际unknown集合统计一致：node21862971bytes、PIP22384342bytes，逐set word padding后5542898u64；含拟议每set2word descriptor的完整trace下界91969168bytes≈87.7MiB。results/trace_set_codec_real_20261025_v1.json status=real_unknown_set_lossless_run_encoding_size_measured_full_trace_fit_unproven。低于128MiB不证明完整fit（路径/额外roots/net/site仍下界），下一步接新search frame/bitmap直接迭代器和独立mixed reader，实际整批导出计量。
- 原trace HLS687570/687572及监督727144已failed，flow末尾LLVM ERROR: IO failure on output stream，receipt exit1；当时共享gpfs卷df10T/10T/0available，inode仍够。不是综合通过，也不能据此判内核错误。
- 已确认原owners退出，逐文件校验857项后将仅已终止HLS .autopilot cache复制至/tmp/A_graph_compression_recovery_20261025_v1/failed_trace_hls_autopilot，原路径软链接保留，释放约1.1GiB共享空间；源码/日志/报告均原位。manifest=/tmp/.../relocation.json。新search_batch_trace_hls_local_recovery.py唯一owner1310895 / child1311075 / exec27921，bundle=/tmp/A_graph_compression_recovery_20261025_v1/trace_hls_recovery，project同父trace_hls_project；同源码/2022.2/U280/5ns/1.35ns在本机3.2TiB可用卷重新Csim→综合，不在原失败project覆盖。新唯一监督owner1314947 / exec80022，预期local trace_hls_synthesis_review.json。root data/derived/search_batch_trace_hls_local_recovery_20261025_v1/location.json记录路径；/tmp不是持久交付，后续有空间需归档，当前不得称恢复成功。
- results/search_batch_trace_hls_io_incident_20261025_v1.json绑定失败/迁移和恢复指针，原snapshot恢复848340/859354继续，完整实验active。共享空间仍紧张，新大artifact优先本机隔离位置并保存持久pointer，不擅删冻结证据/其他方案。

## 最新：真实全批次诊断trace容量已证不足，至少557.5MiB/批（2026-10-25）

- 新batch_trace_capacity_lower_bound.py对已独立审核的CSR/compact各两批raw逐search统计unknown_sources/PIP keys，真实每批16836 searches、23941567 unknown-node记录、43246398 unknown-PIP记录。仅search header/result/最小roots与unknown即68703205u64；加BEGIN、最小逐net快照、7个最小全domain round快照和TERMINAL，下界73073869u64=584590952bytes≈557.5MiB。完整路径/额外roots及site状态仍省略，不能当精确容量。四批一致，均严格超过现有16777216u64/128MiB，不能用原trace top全真实完成验收。
- results/batch_trace_real_capacity_lower_bound_20261025_v1.json绑定实际raw与source/proof；独立review校验两个immutable fixtures原execution hash、各自nodes274732/nets1062/sinks4209和下界公式，results/batch_trace_real_capacity_review_20261025_v1.json status=real_batch_exact_trace_current_capacity_proven_insufficient。tests/test_batch_trace_capacity_lower_bound.py三测试通过，覆盖>1MiB record跨块/EOF/截断。开发稿EOF与保留已解析prefix性能问题已修正并记录development.json；仅停止自己只读估算进程，原HLS/RTL未重启。
- 这是实际容量负结论，不是设备性能。下一步必须设计无损编码或producer/consumer continuation分段导出以保留完整payload/末态，不能删unknown、截断成功或用hash摘要替代。现有诊断44BO源计划只能容纳128MiB旧协议；直接扩容还需改模板/实际HBM bank容量计划，不能假定现有31通道足够。
- 原诊断HLS687570/监督727144及snapshot恢复848340/859354仍按原owner推进，未产生新通过结论。完整目标active；不能以synthetic trace通过或CPU全真实通过标记完成。

## 最新：诊断batch容量失败与exact-fit实际入口双模式验证通过（2026-10-25）

- 新test_batch_trace_capacity.py v1首次在run0失败：其逐字节对照误把正常递增的Search workspace epoch(result13)当成不变字段。失败bundle/state/log保留，未改内核或原trace源。新test_batch_trace_capacity_v2.py→batch_trace_capacity_cpu_20261025_v2，两模式ASAN/UBSAN实际入口均成功；每模式16个实际record边界cut（含边界前1word）、exactfit和3种非法trace controls。
- C++核验每次失败只保留完整prefix、全未提交payload/tail sentinel不变；begin不足返回batch9，begin后trace不足仍保留原routing结果/ledger元数据/counts/history；非法trace控制不推进node版本。epoch按明确实际Search meta累计增量单独检查，其余payload全部exact。
- 新check_batch_trace_capacity.py独立重读所有二进制/receipt/hash，确认32份overflow都sticky2且不能被v2 mixed reader接受、prefix逐frame等于exact-fit（仅核对一致epoch偏移）、首缺失frame确实超容量，两份exact-fit可完整验收。results/batch_trace_capacity_cpu_20261025_v2.json绑定实际输入/二进制/日志/reader，status=diagnostic_batch_both_modes_atomic_capacity_prefix_and_exact_fit_cpu_verified。无RTL/设备结论。
- 原snapshot恢复848340/859354仍elaborate，已完成static elaboration进入simulation data flow analysis；原诊断batch HLS687570/监督727144继续，不重启。完整目标active，接收终态/整体RTL/实际XO平台时序设备/特殊资源仍待推进。

## 最新：完整批次全真实独立审核通过；snapshot失败后隔离恢复已实际elaborate（2026-10-25）

- 原batch_router_full_20261025_v1 owner131608正常complete/independently_audited，新results/batch_router_audit_20261025_v1.json status=batch_two_full_router_conditions_independently_verified。CSR/compact各两完整1062网batch，每批16836 searches，完整中间语义/CC/SC/KC与单net前驱一致。本轮重核报告全部16绑定文件hash一致，report SHA=3a66a62ea523dbd72377253647847b47d59874c7528631228aa4e92c3ae69d30。是实际whole-batch top的CPU执行，CPU-only回调非硬件trace，不代表RTL/设备/200MHz。
- snapshot原elaboration receipt exit137，rdiArgs日志Killed；当前cgroup memory.events oom_kill=1但无timestamp/PID归属，不足证明本次OOM。读取Ross vivado-simulate-rtl及known-issue/performance references；两类官方查询未定位直接匹配AR，不宣称工具bug/根因。MCP list现有会话后未更动任何旧session；xelab是独立CLI，采用已有批处理setup。官方2022.2 UG900及本机xelab -help确认--mt off/--O0/--stats。
- 新resident_snapshot_rtl_recovery.py+check_resident_snapshot_rtl_recovery.py，唯一bundle/project resident_snapshot_rtl_recovery_20261025_v1，owner848340 / child859354 / exec16438，已/proc确认live且stage=elaborate。严格核验原失败已终态、原CPU/setup/synthesis全部hash，复制原5.3GiB sim（去掉编译缓存/log），保持原全depth和30交易/原generated C postcheck/10sec simbound，仅xelab添加-mt off --O0 --stats及/usr/bin/time -v记录资源。原目录不改，不减规模，不重综合。owner自动elaborate→RTL→原postcheck→独立audit，目标results/resident_snapshot_rtl_recovery_audit_20261025_v1.json。当前尚无恢复成功结论。
- results/resident_snapshot_elaboration_incident_20261025_v1.json保存原failure/commands/资源观察和研究适用限制；已启动尝试不等于已验证workaround。trace HLS/监督原687570/727144继续，v2 reader补充验收仍需合并解释。完整实验active，物理/实板/特殊资源缺口未完成。

## 最新：mixed reader v2补齐需求继承与逐net全局计数，发现并拒绝旧验收反例（2026-10-25）

- 审查发现冻结read_batch_trace.py v1未逐次验证成功search继承已有site demands，也未将逐net metadata全局总量对照全部latest net snapshots。旧证据保留不改；新read_batch_trace_v2.py先执行旧全部检查，再验证signal不消失、bitmask不收缩且旧mask内值不变、category不改变、zero-edge不增加需求，以及reset1时node/retention/edge/site全局人口和net数量。
- tests/test_read_batch_trace_v2.py四测试通过：在实际首search追加signal4而后续静默丢失的counterexample，旧reader仍complete_batch=true，新reader拒绝；另6种逐net全局metadata count篡改旧reader接受新reader拒绝。这些是校验器反例，不是实际内核失败。所有原CPU两模式3cases和实际HLS Csim3cases共9份跟踪在v2仍按reset/seed规则通过。results/search_batch_trace_reader_20261025_v2.json完整绑定source/tests/log/raw/decoded，文档SEARCH_BATCH_TRACE_READER_V2.md明确v2加强后续验收。
- 原HLS/监督仍owner687570/727144，实际进程live；HLS进入run_2 scheduling，未终态。现有冻结综合checker仍v1 reader，收到原综合审核后必须同时引用v2补充验收，不能仅旧complete_batch支持需求继承结论。
- 原batch全真实owner131608两模式运行均结束、进入independent_full_audit，最终report尚未生成，不重复启动/竞争审核。完整目标active，无新RTL/时序/设备通过结论。

## 最新：诊断batch源接口44BO内存候选及独立综合监督就绪（2026-10-25）

- 新batch_trace_memory_plan.py→hardware/vitis/search_batch_trace_memory_v1，严格45args/44ptr/30AXI inventory，44独立BO（含128MiB trace_data、trace_control/meta各4KiB对齐），946561024bytes，31名义HBM通道，HBM/DDR cfg保存。check_batch_trace_memory_plan.py独立核对源ABI/CPU gate/BO不别名、layout/银行/完整summary/channel计数。results/search_batch_trace_memory_audit_20261025_v1.json通过；tests/test_batch_trace_memory_plan.py实际16损坏拒绝通过，结果绑定results/search_batch_trace_memory_tests_20261025_v1.json。仍非actual XO/group mapping/platform link/设备44BO分配，固定容量不能保证真实trace容纳。
- 原trace HLS owner687570/child687572实际/proc live，Csim已零错误；4份Csim实际binary trace与CPU mode0逐字节完全一致。综合仍执行原flow，不能称已通过。
- 新check_batch_trace_hls.py要求完整receipt/tool/part/clock/全部接口+实际生成RTL，且核对4份Csim trace与CPU完全一致再运行独立mixed reader；保留全部warnings/resource/timing限制。新supervise_batch_trace_hls.py owner727144 / exec15005已/proc确认live，绑定原owner identity只等待一次终态并审核，目标results/search_batch_trace_synthesis_review_20261025_v1.json；不启动/重启HLS。原HLS exec60770保留。
- 完整实验仍active，下一步综合终态审核与整体RTL、实际XO/平台/时序设备工作及真实特殊资源缺口；本轮没有新RTL/物理/实板达标结论。

## 最新：诊断完整批次top已实际导出混合trace，两模式CPU及独立reader通过，HLS已启动（2026-10-25）

- 新derive_search_batch_trace_top.py→search_batch_trace_top.cpp，从冻结原batch生成独立入口，原基线不改；仅external top有INTERFACE，45args/44ptr/30AXI bundles，新trace_control8/meta8/data16777216u64共128MiB诊断域。实际search之后立即写frame，成功net后写快照，round前后写full histories，wrapper保留路由error terminal。trace不足sticky且不再commit，后续routing仍原结果；整批验收必须独立metadata+terminal，不能只看batch_result。
- 新search_batch_trace_frames.hpp BEGIN保存raw control/完整immutable query与sink pool，TERMINAL保存raw result12。新test_search_batch_trace.py运行原production-depth CPU测试，两模式ASAN/UBSAN成功，实际8份二进制涵盖fresh routed/seed持续冲突/incomplete/前置拒绝。新read_batch_trace.py按schedule交叉核对search roots/path/demands、net占用与保留边、round ledgers/full history及terminal全部计数；tests/test_read_batch_trace.py两测试通过，删除/乱序/篡改事件拒绝。
- reset1成功trace可判定本CPU诊断协议complete_batch=true；reset0因无导出初态证明仍false；routing-error terminal当前仅诊断，不被success reader验收。results/search_batch_trace_cpu_20261025_v1.json绑定实际source/binary/log/trace/reader，完整实验仍未完成，无HLS/RTL/设备通过宣称。
- 新search_batch_trace_hls.py唯一owner 687570 / child 687572 / exec60770，已/proc核实实际运行；bundle/project search_batch_trace_hls_20261025_v1，2022.2 xcu280/5ns/1.35ns CSR Csim→csynth。无Unified HLS工具，使用既有2022.2 Tcl CLI替代；后续独立综合报告/RTL及实际内存计划必须新审核，不能沿用原batch 41BO计划。不要重复提交。

## 最新：轮次前后精确快照及history增量独立校验通过（2026-10-25）

- 新search_round_trace.hpp / dump_round_trace.cpp导出完整domain counts/history、complete flags、active site owners/history和conflict summaries，phase0判断后/推进前、phase1两history推进后；严格C++14-Werror ASAN/UBSAN实际fixture成功，容量拒绝保持payload/尾guard。节点counts/history为明确有效seed，site ledger和两history增量调用实际生产core。
- 新read_round_trace.py独立重算node/site冲突、penalty、终止与incomplete，要求每个conflict pre-state有post-state，完整比较history增量/owner不变与bank/version。tests/test_read_round_trace.py两测试通过，含最后冲突轮仍advance的字面结果及损坏/缺post拒绝。results/round_trace_cpu_20261025_v1.json绑定全部实际文件。开发时修正template参数/fixture计数/测试字面offset后最终通过；无硬件通过宣称。
- 尚缺search/net/round混合关联、batch初态/错误/terminal和实际top/AXI接入；完整目标仍active。
- round_control RTL v2审核status=production_round_control_full_depth_37_transactions_rtl_verified，本轮重核211绑定文件全部hash一致。snapshot原owner已终止，state=failed/stage=elaborate，elaborate.log显示rdiArgs子进程Killed；目前不能确定原因，不重启/不称通过。保留原现场，后续诊断恢复需新版本。

## 最新：精确net快照写入与独立reader CPU验证（2026-10-25）

- 新search_trace_records.hpp扩展冻结search writer，记录原始net result/demands/组件metadata，以及实际tree roots、retained节点、hash表owned keys、counts/history、完整8字段边和site所有权；140word实际fixture通过严格C++14 ASAN/UBSAN，容量拒绝保持payload、尾guard。
- 新read_net_trace.py独立解码，交叉核对三份节点集合、需求/site所有权、树版本与found数量、保留边端点/方向及metadata域。tests/test_read_net_trace.py两测试通过，41个隔离word损坏及截断/额外字节均拒绝。开发初稿部分mutation offset落在合法bank/version/属性变动，已修正字面期望后重新通过，不将合法变动冒充损坏。results/net_trace_cpu_20261025_v1.json绑定实际文件。
- 仅合成CPU net快照，不是完整batch协议；尚缺search/net混合顺序、round/history/terminal以及实际top/AXI接入和RTL。reader明确complete_batch=false，不能以快照通过认定完整实验完成。
- 本轮/proc确认batch真实原owner131608与retention/site/edges/tree/width64 RTL原owners仍live，未重启。snapshot及round v2旧PID已缺失，后续读取原终态与独立审核报告，不仅按旧state称仍运行。

## 最新：trace v2修正零数量旧buffer语义，独立reader已通过实际C++字节fixture（2026-10-25）

- 原v1 search trace证据冻结不改。新search_trace_v2.hpp只修正unknown count0时不读/校验旧bitmap；原写入器在SearchStatus5/6前置拒绝后可能把旧unknown数据当活跃输出拒绝记录。v2保留同一frame/metadata ABI、首错误sticky和全预检提交规则。
- test_search_trace_v2.cpp实际默认128MiB和small512 word模板ASAN/UBSAN均通过，新增status6/unknowncount0但bitmap非零的case。独立dump_search_trace.cpp写出实际little-endian metadata+committed payload文件；首次未冻结dumper draft缩进warning已修正。reader不依赖C++ helper，按已读packed LabelKeyWords ABI解析active state/完整raw81word/roots/path/unknown集合，验证path连续性/序号/全部边字段。
- tests/test_read_search_trace.py三组测试通过，读取实际fixture且拒绝23种隔离损坏（含长度/数量/version/status、路径/roots/unknown/demand、乱序/重复、truncation/extra/endian）。results/search_trace_cpu_20261025_v2.json绑定source/tests/binary/log/fixture/decoded结果，status=exact_search_trace_writer_and_independent_reader_verified_batch_protocol_pending。
- reader只返回search_fragment_validated、complete_batch=false、requires_terminal_record=true；net/round/history/terminal完整协议与top/AXI接入尚未实现，不能把有效片段当整批完成。文档SEARCH_TRACE_SEARCH_V2.md明确范围。
- 本轮实际确认原round_control RTL v1已complete/independently_audited，v2仍原xsim；net全真实已complete，batch真实监督已进入full_real并启动owner131608（下一轮核实其新workers/进展）。不改变/重启原长任务。完整目标active，继续完整trace/整体RTL、资源时序/平台实板。

## 最新：完整批次实际综合审核完成但估计资源/时钟紧张；精确search trace写入器CPU通过（2026-10-25）

- 原batch HLS3559903及supervisor3801933均正常complete，exec98359已收取。results/search_batch_synthesis_review_20261025_v1.json status=batch_integrated_control_csim_synthesis_verified_rtl_pending；实际42参数/41指针/29AXI接口核对通过，LUT1290250/FF514060/DSP93/BRAM18K69/URAM3。估计4.509ns>effective3.65ns，estimated_clock_meets_effective_budget=false。LUT估计接近整片1303680，未包含平台reserve，不能称fit/200MHz达标；须实映射/时序对照。范围/函数复制等warnings全部保留。
- 新search_trace.hpp为有界精确search record writer，默认16777216u64/128MiB。记录完整81word结果、packed sorted roots、4u64/edge全部8原始u32字段、exact unknown node IDs和PIP keys，非hash摘要；全预检后写入，frame拒绝仅sticky error变化，data/committed prefix不动，容量不足不截断成功。
- tests/test_search_trace.cpp严格C++14-Werror ASAN/UBSAN已通过，实际默认128MiB分配也验证完整tail/guards；literal endian/fields、跨64bit unknown ID、两frame、6类错误/sticky/version/capacity覆盖。首次编译的test缺algorithm include与误缩进已在未冻结开发阶段修正；最终log/binary/source绑定results/search_trace_cpu_20261025_v1.json。exec38142已正常收取。
- 这只是writer core，尚未接batch top/AXI，net/round/history/terminal records与独立reader仍缺。文档SEARCH_TRACE_SEARCH_V1.md明确status0 frames不等于完整batch成功，必须终态事件/顺序/全部payload验收；诊断开销不混同release性能。
- 原net全真实已两workers结束进入independent_full_audit；原batch全真实监督仍按原前驱门等待/续跑。完整目标active；下一步完整硬件trace协议/整体RTL与实际映射，平台/实板与特殊资源语义仍未完成。

## 最新：完整批次单CU源接口内存候选已独立审核（2026-10-25）

- 新batch_memory_plan.py生成hardware/vitis/search_batch_memory_v1，直接解析冻结canonical batch top的42参数/41指针，不沿用旧9CU计划。单CU所有41BO互不alias，按实际bundle同bank、4096对齐、nominal HBM/DDR及16MiB reserve策略分配。结果812335104bytes（约774.7MiB），30名义HBM通道，HBM/DDR candidate cfg均保存。
- 新check_batch_memory_plan.py对照源参数完全相等，并复核完整batch CPU proof所有文件、全部BO/银行/cfg。results/search_batch_memory_audit_20261025_v1.json SHA=fbc41085bf70b7d093aacd1adb4b77a4175285e5f4d8e2ceabc66d9e6347587d，status=integrated_batch_source_buffers_independently_checked_actual_abi_platform_pending。tests/test_batch_memory_plan.py 12种真实manifest隔离破坏拒绝通过，包含depth/width/name、重复/遗漏BO、容量/对齐/总量、bundle、布局、cfg/hash。
- 这是源接口容量候选，不是kernel.xml/XO控制ABI：导出后的参数名/offset/qualifier/真实group映射仍需核验。未实际平台link、41BO同时设备分配、200MHz通过或设备带宽功耗。此接口只保存final ledgers/completion/last diagnostics，完整query/net/round硬件trace导出仍未实现，不能用末态替代全部诊断验收。
- 原batch综合与全真实前驱/续跑均保持原owners，完整目标active。后续实际综合→整体RTL→真实XO/平台/设备接口和物理闭合，继续特殊资源语义验收。

## 最新：完整批次真实router已优化编译，后继全真实验证自动续跑已就绪（2026-10-25）

- 新compile_batch_router.py验证已通过完整400case批次差分所有绑定，真实两个batch observed tops以O2编译、严格-Werror site_runtime链接成功。exec90621已正常收取3条PASS，batch_router_20261025_v1/regular_build_complete.json保存actual binary/objects/plan hash，原source不变。此编译的CPU callbacks保留完整诊断，不是硬件trace。
- 新prepare_batch_real.py + batch_router_pipeline.py/check_batch_router.py，设置仍为CSR/compact各两批1062网/cache4096/max80/budget200000/presentcap8，对已审核单net前驱逐raw中间/最终语义与CC/SC/KC比较。新supervise_batch_real.py owner3903511 / exec44156已/proc确认live，已通过build门，当前await_original_predecessor；绑定原单net真实owner3639401精确identity，待其完整成功审核后自动prepare→唯一完整工作负载→独立终态审核，不绕过前驱/不重复提交。
- 预期新bundle batch_router_full_20261025_v1、最终results/batch_router_audit_20261025_v1.json，status=batch_two_full_router_conditions_independently_verified。当前未启动批次全真实，不能称运行/完成。单net原两模式真实workers仍运行，completed=[]。批次HLS原3559903仍binding，监督3801933保持，无新硬件成功结论。
- 完整目标active。后续实际完整批次RTL/接口/平台连接/200MHz时序/设备性能功耗和特殊资源语义仍需完成，不能将CPU全部控制差分当作完整实验结束。

## 最新：完整批次CPU入口全部400case中间差分独立审核通过（2026-10-25）

- 原batch_router owner3710916/child3735585正常complete/all_net_round_intermediate_differential_verified。新check_batch_router_component.py要求全部源/object/binary/command/receipts及精确输出，确认site_routes每batch一次actual top且无host route_net/advance/round decision调用。`results/batch_component_20261025_v1.json` SHA=b096f670c35134666b672994d238636125661e92f343a86e54c177e5b842a1e8，status=batch_full_negotiation_intermediate_differential_verified_real_workload_pending；400cases/4938searches/3750snapshots/1250rounds中间/最终全等（node-history2412/site-history2106/site-paths2896，routed210/incomplete190）。Canonical/observed再次独立预处理token相同，CPU回调仅观察，不当作RTL等价或设备trace。
- 新check_batch_control_hls.py + supervise_batch_hls.py owner3801933 / exec98359已/proc确认live等原3559903。实际source parser确认42参数/41指针/29AXI bundles，审核器要求真实XML+top、CSR Csim全部批次case、原目标/receipt/hash，记录effective3.65ns预算是否满足与完整warnings，不提前判定成功。预期results/search_batch_synthesis_review_20261025_v1.json。
- 原HLS当前binding，未有终态。原sink_loop全真实已正常完整审核结束，net单net全真实owner3639401已实际启动；监督3354654现full_real。原compact物理会话4159154 MCP确认仍running精确原source、queue0，未重启/执行新Tcl；没有新物理达标结果。
- 下一步批次版本完整真实工作负载、综合终态/整体RTL与实际XRT接口，再物理时序/平台实板性能功耗。真实特殊资源语义缺口仍未齐，完整实验目标active。

## 最新：全net/round入口已接入完整协商差分，实际400case运行中（2026-10-25）

- 新search_batch_observed_top.cpp只在CPU诊断宏且非__SYNTHESIS__下逐search和net/round边界回调。新batch_router_transform.py / prepare_batch_router.py从已验证net完整源复制，单次actual batch top替换host net/round循环；queries唯一ID与protected/reserved原静态验证保留。top实际决定complete、conflict、终止与history，观察只重建SiteBatch/maps/trace，不驱动live控制。
- 回调kind0清当前search帧，kind1导出真实net状态+完整query帧，kind2在实际history推进前导出round冲突/完整性，并与raw RoundControl计数核对。site冲突观察仅重算disposable scratch，不改owner/history。全部旧400case中间路径/需求/unknown、轮次和最终结果检查保留，不改成只比末态。
- batch_router_20261025_v1 owner3710916 / exec52494，已实际完成两模式top对象和严格-Werror ASAN driver编译，state=differential，child3735585 CPU125已/proc确认live。尚无终态，不能宣称pass。原HLS owner3559903仍执行CSR Csim/csynth，root canonical源不改。
- results/search_batch_observation_guard_20261025_v1.json及bundle两预处理源码，确认canonical/observed在__SYNTHESIS__+observer宏下g++ C++tokens完全一致；这是host预处理证据，不是RTL等价或400case通过。
- 下一步接收完整差分、独立绑定审核后运行全真实，并准备实际整体RTL/物理/设备ABI。旧各RTL与真实任务按原owners继续，完整目标active。

## 最新：全net/round内部控制入口已实现，两模式synthetic CPU测试通过，HLS已启动（2026-10-25）

- 新derive_search_batch_top.py→search_batch_top.cpp，保留实际net_worker/sink_loop_worker逻辑且移除子函数INTERFACE。入口内部遍历immutable query table，执行全net交易，Site.analyze→RoundControl→按真实decision推进两history。无host轮判断介入；保持排序sink/重复、present=min(2^min(iter,20),cap)、最后冲突轮仍advance、无冲突立即按完整性终止。
- 新test_search_batch.py / search_batch_cpu_20261025_v1两模式C++14 ASAN/UBSAN正常终态，exec43864已收取。完整声明buffers；验证fresh两query routed、重复sink、显式seed外部owner77的两轮持续冲突和history[1]==2、最后轮advance、unknown无冲突首轮incomplete、前置invalid不重置状态及completion tail。seed是有效组件状态，不是实测真实历史。
- 新search_batch_hls.py唯一bundle/project search_batch_hls_20261025_v1，owner3559903 / exec36287，CPU127（affinity确认），实际2022.2/xcu280/5ns/1.35ns CSR Csim/csynth。尚无HLS/RTL通过结果，不套用原单net综合。
- 原单net HLS owner3071132及supervisor3221960正常complete；results/search_net_synthesis_review_20261025_v1.json status=net_integrated_control_csim_synthesis_verified_rtl_pending，LUT937410/FF395569/DSP93/BRAM18K69/URAM3，保留函数复制/范围/时钟告警，不代表物理fit或200MHz通过。
- 批次ABI及trusted-input契约见SEARCH_BATCH_V1.md：query唯一net和protected/reserved一致性仍需静态适配器预验证；范围/顺序检查在reset之前。无全局rollback，综合逻辑尚无完整query/net/round trace导出，未有全400case/真实/RTL/平台实板验证。原各长任务继续，完整目标active。

## 最新：单net完整真实router已优化编译，待原前驱审核后自动运行（2026-10-25）

- 新compile_net_router.py复核单net400case已审核输入，实际两模式observed net tops以O2编译，严格-Werror完整site_runtime链接成功。exec51452已收取3条PASS并正常exit0，net_router_20261025_v1/regular_build_complete.json保存plan/binary/object hashes。source保持原完整差分版本，无主机释放/build/commit回退。
- 新prepare_net_real.py + net_router_pipeline.py/check_net_router.py，保持原两模式各两批1062网/cache4096/max80/budget200000/presentcap8，与sink_loop全真实前驱逐raw中间/最终语义及CC/SC/KC核对；CPU观测不当作设备执行。新supervise_net_real.py owner3354654 / exec77841，/proc确认live，已经完成build等待，当前await_original_predecessor；冻结前驱owner2915404精确identity，成功审核后自动prepare→唯一完整工作负载→独立终态审核。缺失/失败不绕过或重启。
- 预期新bundle net_router_full_20261025_v1，最终results/net_router_audit_20261025_v1.json，status=net_two_full_router_conditions_independently_verified。当前尚未启动该工作负载，不宣称运行/完成。前驱sink_loop_router_full当前completed=[0]，原compactworker及后续审核继续原owner。
- 原search_net HLS仍运行且独立supervisor3221960保持；原RTL/物理不变。完整目标active，继续全net/round内部控制、RTL/时序/平台实板。

## 最新：单net内部控制400case全部差分审核通过，六种部分提交失败测试也通过（2026-10-25）

- 原net_router owner3161362已complete。新check_net_router_component.py复核全部源/objects/binary/receipts/log及精确400case输出，并检查两路site_routes没有旧host释放/build/acquire/retention调用，只有每net一次actual top。`results/net_component_20261025_v1.json` SHA=14369912a8853183f52ba01508294e1693e32528be33fb95fdeed033d79dea2f，status=net_full_negotiation_intermediate_differential_verified_real_workload_pending；400cases/4938searches/3750snapshots/1250rounds、全部路径/状态/需求/unknown/协商最终语义相同。
- Canonical net top与CPU observed top在__SYNTHESIS__+observer宏下g++预处理tokens完全相同；预处理源码与hash纳入审核。这不是RTL等价证明，不把CPU观察结果当设备trace。Net/round外层尚在host。
- 新test_search_net_failures.py / search_net_failures_20261025_v1两模式ASAN/UBSAN正常终态（exec26704已收取）：site versionMAX失败stage3、edge versionMAX stage4、非法static stage5、非法search metadata stage6、retention versionMAX stage8、site先release到MAX后commit失败stage9。逐case核对node/source ownership、tree/edge/retention/site状态和search epoch，证实接口如实保留此前stage改变，无跨stage rollback。原source不变。
- 新check_net_control_hls.py及supervise_net_hls.py owner3221960 / exec15461已冻结，/proc确认仍等待原HLS3071132；检查实际26个AXI bundles/原markers/target/sourcehash/warnings，成功后一次results/search_net_synthesis_review_20261025_v1.json。勿竞争审核或改输入。原综合仍未终态；原sink-loop全真实继续。完整目标active，下一步全真实net、全net/round内部控制及RTL/物理/实板。

## 最新：sink循环root_nodes修复版实际综合审核通过；完整单net控制已接入400case差分（2026-10-25）

- 原HLS v2 owner2864351及supervisor2875093均正常complete。`results/search_sink_loop_synthesis_review_20261025_v2.json` SHA=e41aa8b6c9f093e201b4cb75de068e03010c43f106dcf5e30d3f04cec4774394，status=sink_loop_integrated_control_csim_synthesis_verified_rtl_pending。root_nodes单变量重命名后实际RTL生成成功（原v1命名失败保留）。LUT600988/FF269673/DSP77/BRAM18K69/URAM3；warnings214-366=3、SYNCHK200-23=1、ANALYSIS214-31=6、SYN201-103=12、HLS200-871/1016各1、RTGEN206-101=1。未解决时序/范围告警，非RTL/物理/实板通过。
- 新search_net_observed_top.cpp仅在CPU诊断宏且非__SYNTHESIS__下逐search记录frame，不驱动live net状态。新net_router_transform.py在隔离source增加node/site/retention backing buffer桥接、static snapshot只读访问；删除旧host释放/构建/提交调用，把每net改为一次actual net top；外部只做完整结果解码、状态只读导出与round/history操作。旧root adapters与其他方案不动。
- 新prepare_net_router.py / net_router_20261025_v1，复核前驱全差分绑定后复制source，明确所有原bounded core相同。node/site snapshot统计从实际构建packet的冻结body观察恢复，非host生成新live state。两模式实际net top与严格-Werror ASAN全driver均已编译PASS，exec83030已收取3条输出，仍live。owner3161362 / differential child3185131 CPU125已/proc确认，正在原400cases/4938searches/3750snapshots/1250rounds全部中间最终差分，尚未终态。
- 原search_net HLS owner3071132仍运行，原sink全真实两workers继续。完整目标active；下一步接收单net全差分和综合结果，继续全net/round内部控制、RTL/物理与实板验收。

## 最新：完整单net内部控制入口已实现并两模式CPU通过，HLS已启动（2026-10-25）

- 新derive_search_net_top.py→search_net_top.cpp可重现组合：RetainedNodes.get→Node.update旧释放→Site.replace空请求释放→Tree.reset/Edges.clear→完整Snapshot.build→内部sink loop→Node.acquire→RetainedNodes.replace→SiteRequest.encode/Site.replace提交。所有决策来自实际bounded cores，helper接口pragma已剥离，只在新top声明。未改原核心/其他方案。graph模式与原搜索容量不变。
- 新test_search_net.py / search_net_cpu_20261025_v1两模式C++14 ASAN/UBSAN正常终态，exec48350已收取：同net两次重布不重复计owner，literal原始边及需求，history不变，unknown只提交source且incomplete，空sink完成不执行search，reserved前置拒绝不增加提交状态。full declared buffers，但只有合成fixture，未有400case/全真实差分或RTL结果。
- 新search_net_hls.py已冻结CPU source/receipts，唯一bundle/project search_net_hls_20261025_v1，owner3071132 / exec19692，CPU126（affinity确认可用），实际2022.2/xcu280/5ns/1.35ns CSR Csim/csynth。不能套用先前三核心/sink-loop或packet64综合结果。后续需要核实全stage硬件与资源、命名及动态访问问题。
- ABI/错误阶段与限制见SEARCH_NET_V1.md：原packet length与sink_count标量改为内部Snapshot/输入net_control生成；不存在跨stage rollback，完整static校验仍在释放之后。net_result错误必须中止/显式恢复，不能当成功。全net遍历、round/history和最终trace导出仍外部，旧9CU cfg不对应新top。完整目标active。
- 原轮判断RTL实际推进7/37；site30/52、retention1/37仍原真实xsim活跃，packet64也已进入RTL，未因慢而重启。原sink_loop全真实与root_nodes HLS v2继续。

## 最新：内部sink循环全真实两模式工作负载已实际启动（2026-10-25）

- 新compile_sink_loop_router.py复核已通过400case完整差分证据，保持原source不变，实际两个observed integrated top以O2编译并与原全部外层helper/production objects链接。exec44199正常exit0，compile_csr_regular/compile_compact_regular/compile_router全部PASS，regular_build_complete.json保存binary/objects/plan hash。
- 新prepare_sink_loop_real.py + sink_loop_router_pipeline.py/check_sink_loop_router.py，保持原CSR/compact各两批1062网/cache4096/max80/budget200000/presentcap8，逐raw中间/最终语义与已审核retained_edges前驱比较，CPU callback只观察。新supervise_sink_loop_real.py owner2915063 / exec45007已完成prepare进入full_real；唯一真实owner2915404，bundle sink_loop_router_full_20261025_v1，workers2916227/2916231实际/proc live，completed=[]。勿重复提交/竞争审核。
- 原owner自动终态独立审核，预期results/sink_loop_router_audit_20261025_v1.json，status=sink_loop_two_full_router_conditions_independently_verified。原root端口名称版本用于CPU真实语义验证，不混同新HLS root_nodes命名修复版ABI；所有限制保留。未宣称设备性能或PL完整router。
- HLS root_nodes v2原owner2864351与其supervisor继续；原各RTL/物理按原owner继续。下一步接收实际全真实与RTL/综合终态，推进net释放/build/commit和round内部控制，物理时序/平台实板。完整目标active。

## 最新：内部sink循环400case全部差分通过；HLS v1命名失败保留，重命名v2已验证并重综合（2026-10-25）

- 原sink_loop_router owner2722853/child2747045正常complete，全部400cases/4938searches/3750snapshots/1250rounds中间及最终语义一致。`results/sink_loop_component_20261025_v1.json` status=sink_loop_full_negotiation_intermediate_differential_verified_real_workload_pending，独立复核全部源/对象/binary/receipts/log绑定及精确输出；内部top执行sink loop，callback只供诊断，外部net/round尚未硬件化。
- 原sink HLS v1在RTL生成阶段实际失败：RTGEN206-402 type-inconsistent element roots，HLS200-103 Naming conflict of RTL elements。原state/receipt/log/project保持failed；随后supervisor v1按设计failed而非自动重启，/proc PID2831040已退出，不要等待其旧state。上一条尚未写入NEXT_STEPS的“supervisor live”草稿因实际缺失进程失败，未发布成功声明。
- 仅新search_sink_loop_top_v2.cpp重命名顶层roots变量/port为root_nodes，保留Tree::roots函数名；反向identifier替换与原整个源码严格相等，参数顺序/type/深度/算法不变，但未来XML端口名称变化须用新ABI。新test_search_sink_loop_v2.py / search_sink_loop_cpu_20261025_v2两模式ASAN/UBSAN通过，exec20167正常收取。
- 新search_sink_loop_hls_v2.py独立bundle/project search_sink_loop_hls_20261025_v2，owner2864351 / exec65185，CPU124，/proc确认live，目标不变。新supervise_sink_loop_hls_v2.py只等此新owner→独立--kind sink_loop审核，预期results/search_sink_loop_synthesis_review_20261025_v2.json。不能在新RTL成功前称命名问题已解决，也不能把v1失败覆盖。
- 三核心connection综合审阅已通过但预算4.509ns>3.65ns且有range warnings；仍需RTL/时序。完整目标active，下一步原完整差分后全真实、统一入口RTL及net/round控制与实板验收。

## 最新：统一sink循环已接入完整协商差分，实际400case测试运行中（2026-10-25）

- 新prepare_sink_loop_router.py，隔离sink_loop_router_20261025_v1，验证前驱edge完整差分所有绑定后复制flat source。仅隔离tree/edge adapters增加resident backing pointers给实际top独占使用；原根目录/其他方案不改。新增sink_loop_observer.hpp复制每次原始81word结果、path、unknown bitset/PIPs、target/root_count，观察不驱动内部tree/edge决策。
- 原Context每sink search方法替换search_all，原site_routes/snapshot_test_routes主机sink循环替换为每net一次actual observed top；该top自行roots→patch→search→accept→append。收到frame后沿用原解码/计数/unknown集合检查，原host末尾readonly complete/roots仍用于输出和轮判断，尚未换成summary字段，也没有声称外层net/round已硬件化。
- 实际两模式top以-DSEARCH_SINK_LOOP_OBSERVE和独立SEARCH_TOP_NAME编译，完整search/ledger容量不变。compile_csr/compile_compact/严格-Werror ASAN完整driver编译均正常exit0；原exec19195已收取这3条输出，仍live（不要再次提交）。owner2722853 / differential child2747045 CPU125（/proc确认live），state=differential。期望原400cases/4938searches/3750snapshots/1250rounds与全部中间/最终结果精确一致；本轮尚无终态，不宣称pass。
- 原三核心connection HLS与sink-loop HLS仍各自运行，sink-loop已进入binding。packet64/edge/其他旧RTL继续各原owners。完整目标active；下一步接收此实际差分、独立审核后运行全真实，并继续整体控制/物理与实板验收。

## 最新：边存储全真实审核通过，多sink完整差分的中间观察接口已验证（2026-10-25）

- 原edge真实owner1915928已正常complete/independently_audited；`results/retained_edges_router_audit_20261024_v1.json` SHA=5da6f73db8cf3c788e7318d67ac3d9ea023442ee0911ef57d3c4de4e658ec628，status=retained_edges_two_full_router_conditions_independently_verified。两模式各两批1062网、每批16836searches，全部raw中间/最终语义与round-control前驱相等；硬件执行仍false。原supervisor无需重复提交。
- 当前sink-loop top只保留最后search输出，不能据此声称全部中间真实路径已比较。新 `search_sink_loop_observed_top.cpp` 在SEARCH_SINK_LOOP_OBSERVE且非__SYNTHESIS__时调用const raw observer；综合中不存在此接口。不改原v1冻结top/在跑HLS。新 `test_search_sink_loop_observed.py` / search_sink_loop_observed_cpu_20261025_v1两模式ASAN/UBSAN通过（exec35602正常收取），逐callback核对roots1/2/3、原始单边路径、重复目标empty path及unknown PIP集合；空输入与前置拒绝无callback。
- `results/search_sink_loop_observation_guard_20261025_v1.json` 记录两版g++在__SYNTHESIS__+observer宏预处理后的C++ token完全一致；原/observed预处理源码与hash保存bundle。不是实际HLS/RTL等价证明，观察接口只能用于诊断，不能驱动tree/edges或搜索决策。
- 下一步把observer raw帧转为完整router现有SearchResult观察，给tree/edge CPU buffers只读/受控桥接，在隔离source中把原host sink循环替换一次top调用，运行原400case全部中间差分；未完成这一步，不宣称sink-loop已接入完整路由器。实际net/round控制及物理/实板目标仍active。

## 最新：多sink内部控制入口已实现并通过两模式CPU测试，HLS已启动（2026-10-25）

- 新search_sink_loop_top.cpp在内部逐sink执行实际Tree.roots→Snapshot query patch→SearchKernel→Tree.accept→Edges.update，最终实际complete/roots；不以host命令表替代。保留原search/ledger全部容量，只用有界count；sink要求预排序但保留重复，未实现硬件sort。空列表无search且complete=true；nonfound不追加树边；search5/6或后续验证失败返回stage，仍无跨stage rollback。
- 新test_search_sink_loop.py / search_sink_loop_cpu_20261025_v1，两模式C++14 ASAN/UBSAN正常终态，原exec64123已收取。验证[1,2,2]三次实际search、树/edges版本和literal原始边，空列表不变、descending/越界输入拒绝、unknown语义incomplete。源码/命令/日志/receipt/hash冻结；非完整真实差分/RTL结果。
- 新search_sink_loop_hls.py已唯一启动，bundle/project search_sink_loop_hls_20261025_v1，owner2589695 / exec40903，CPU124（本机affinity确认可用），2022.2/xcu280/5ns/1.35ns，实际CSR Csim/csynth。原三核心connection HLS owner2494269继续，不改原source或挪用其结果。后续需检查Snapshot常量patch调用消除build分支及实际生成控制循环。
- ABI/行为/缺口见SEARCH_SINK_LOOP_V1.md；输入仍需外层net释放、tree reset和完整snapshot build，输出仍需occupancy/retention/site commit与round控制。现有9CU cfg不对应此新top，未宣称全PL路由。完整目标active。

## 最新：统一连接入口两模式8拒绝验证通过，实际HLS已启动（2026-10-25）

- 新test_search_connection_v2首版因同一auto声明中混用vector<uint32_t>/vector<uint64_t>编译失败，原bundle/log/receipt/state完整保留，未篡改为成功。修正只在新 `test_search_connection_v3.py` / search_connection_cpu_20261025_v3，exec45443正常结束；原top无变化。
- v3两模式均C++14 ASAN/UBSAN通过：原2事务字面结果+8拒绝（preflight invalid meta/短packet/net宽度3；search invalid magic/cap预算2；tree饱和version1；edge饱和version/真实2097152满边容量2）。核对失败阶段，preflight不改search输出/meta/path，tree失败不改tree/edge，edge失败不改两bank/meta但保留已accepted tree。填满edge状态为明确有效seed，不把它称为完整运行生成历史。
- 新 `search_connection_hls.py` 已冻结v3 source/CPU receipts并唯一启动，bundle/project search_connection_hls_20261025_v1，owner2494269 / exec33999，CPU123，/proc确认live。实际CSR 2022.2/xcu280/5ns/1.35ns，原search width策略，csim包含2+8事务，随后csynth。尚未HLS完成/RTL/设备，不对应原9CU cfg；先根据实际结果检查单CU资源与控制路径。
- edge真实原state已completed=[0,1]进入independent_full_audit，原owner1915928负责完整raw审核；勿竞争。packet64 RTL原owner仍执行。完整目标active，仍需整个net/round控制、真实特殊资源、物理时序与实板验收。

## 最新：三核心统一连接入口已实现，两模式CPU sanitizer通过（2026-10-25）

- 新 `hardware/vitis/search_connection_top.cpp` 直接组合原SearchKernel→ProductionRouteTree.accept→RetainedEdges.update，raw path/result驱动后续状态；只在新top body放INTERFACE，无非法子函数接口pragma。保留原search 15参数/容量/width策略，新六state/result参数。整个入口一次调用执行实际顺序，而非host命令表；这还不是完整net/round scheduler。
- 新 `test_search_connection.py` 隔离bundle search_connection_cpu_20261025_v1，原v3搜索源hash验证、实际tree/edge header复制冻结。两模式各两原完整workspace事务C++14 ASAN/UBSAN已正常终态：字面search结果/边8字段、tree节点/version、全edge store tails、nonfound不追加且树边保留均通过。原exec62672已收取正常exit0。source/command/log/receipt/state完整保存，未执行HLS/RTL/设备。
- ABI/错误阶段及限制见SEARCH_CONNECTION_V1.md。前置校验拒绝不启动search；搜索5/6、树错误、edge错误分别返回阶段。后续失败可保留先前已变状态，尤其edge失败前tree可能已accept，无跨组件rollback。还需拒绝分支/满负载测试、HLS/RTL、接入net释放/快照/roots/sinks/site/round控制。现有九CU配置不对应新top，不能误称整体PL路由已完成。
- packet64原RTL仍在elaborate；edge全真实原owner继续，所有原证据与进程不变。完整目标active。

## 最新：packet64 RTL已进入elaborate，终态独立周期对照已挂接（2026-10-25）

- 原packet64 RTL owner2297545正常完成setup，原两事务Csim与generated cosim oracle通过；当前elaborate/child2330461，继续唯一exec94558，不重启。目标stack64MiB/full capacities不变。
- 新 `check_search_packet_width_rtl.py` 独立要求state正常终态、全部plan/execution files/源RTL哈希、精确命令/cwd/receipts、2/2 actual progress与generated-C postcheck原字面输出、实际performance2事务与state一致。基线从原replay审核取CSR cycles并核对实际原performance文件哈希，不手写比值。报告真实cycles/ratio但明确不是HBM/实板吞吐或物理时序证明。
- 新parser负例通过，覆盖缺事务/重复/逆序/0周期/错误ID；不是RTL执行证据。唯一 `supervise_search_packet_width_rtl.py` owner2339367 / exec84938已/proc确认live，在原bundle/audit_supervisor冻结依赖，只等原owner成功后一次审核；预期results/search_packet_width64_rtl_audit_20261025_v1.json。勿竞争审核或改其输入。
- edge真实state completed=[0]，CSR模式两批完成，compact仍原worker；原owner将两模式全部完成后自动完整raw审核。本轮未重复运行。完整目标active，仍需候选RTL/结构物理对照、整体自主控制与平台实板验收。

## 最新：packet缩宽实际生效，资源估计显著降低，隔离RTL对照已启动（2026-10-25）

- 原owner2096766与独立supervisor2149800均正常终态；exec71023已收取。`results/search_packet_width64_comparison_20261024_v1.json` SHA=38f5e951ff126887f68a9f4130045c09ca36f7da111121008fb4c13176e724c8，status=packet_width_single_variable_csim_synthesis_compared_physical_unverified。XML+实际RTL一致确认input_mem512→64。LUT估计355208→209624（-145584），FF167307→130669（-36638），BRAM/DSP/URAM不变；两模式sanitizer两事务与CSR实际Csim通过。原时钟/uncertainty/算法/容量不变。不是物理时序修复证据，可能降低突发带宽或增加cycles。
- 新 `search_packet_width_rtl.py` 复用该冻结候选综合，不动基线，bundle/project search_packet_width64_rtl_20261025_v1。唯一owner2297545 / exec94558，CPU122，/proc核实live。完整声明depth、原两事务TB、64MiB stack；原owner顺序csim/cosim-setup→xelab→10sec bounded xsim→原generated-C postcheck，记录2事务cycles与全部输入/synthesis hash。未做物理实现；终态后仍需独立审核并与原CSR cycles2132461/12383比较。
- 原边真实与各RTL仍按原owners运行。完整目标active，继续候选RTL/全真实验证和物理对照，整体自主控制及平台/板卡性能功耗仍未完成。

## 最新：边RTL完整输入审核通过；九组件综合估计资源已统一核算（2026-10-25）

- 原独立setup审核PID2190154 / exec49575正常exit0，已收取，不再wait此session。`results/retained_edges_rtl_setup_20261024_v1.json` SHA=0499393b33f288a481f066fb77ce4f5610fb9cf29451b7221cebfec5ed6ab4be，status=production_retained_edges_full_capacity_37_transaction_setup_independently_verified_rtl_pending，7实际vectors/37帧完整depth与hash均通过。原owner1977135进入RTL/child2215998，继续原仿真→generated-C postcheck→最终审核，不竞争。
- 新 `audit_resident_resource_budget.py` 对已审核8 helper XML与两search基线XML，核对同2022.2/xcu280/5ns/1.35ns、resource report值及whole-device available一致；search RTL须与原物理负结果绑定一致。`results/resident_resource_estimates_20261025_v1.json` SHA=436fc72e89e62f74d3fbbea1c83c3f7fc6bf5e25149918c2f28a54bf0710a2da，status=nine_component_hls_resource_estimates_accounted_platform_budget_unverified。
- 同层级HLS估计合计CSR LUT1098034/FF549716、compact LUT1112284/FF556994，各DSP101/BRAM18K69/URAM3；LUT占整片84.23%/85.32%。不是mapped/placed/routed整体利用率，未计平台保留/互联/自主controller；search自身HLS估计与已布线LUT差异大，不混合估计层级去宣称fit。此数要求后续实际集成资源/拥塞核验，不能把内存容量通过等同整个系统可装入。
- packet64单变量仍运行在硬件生成，原自动独立比较保持；edge真实原两workers仍执行。完整目标active，继续结构结果/原RTL终态及自主控制、200MHz物理与实板验收。

## 最新：实际search/edge tops共享最大深度路径CPU交接通过（2026-10-25）

- 新 `test_shared_search_edge_path.py` 冻结原v3来源，原实际search top+实际edge top，shared path为16777216u32（64MiB），search声明4194304u32不变。两模式各2完整search调用ASAN/UBSAN通过：found原始路径两次append保留全部8字段/顺序/重复，nonfound不追加且旧4边保持，edge get尾部不变，edge输入全buffer不变，搜索声明范围之外48MiB尾部不变。
- `results/shared_search_edge_path_cpu_20261025_v1.json` SHA=0bc01a550db15c55512d5c65a1f3ddca778a2ef36352ab2ebdeaec6023a05bea，status=actual_search_and_edge_tops_shared_max_depth_path_cpu_sanitizers_verified。运行source/binary/log/receipt全部hash与精确输出重核。这补齐v6静态共享的数据交接CPU证据，不证明真实流量、RTL交接、device start/done/coherency/topology或BO分配。
- 原edge RTL生成已完成，owner1977135进入elaborate/child2184525，未重启。实际ref确认config_r/meta/rows/path/output_r/result，packed input2097154x256/meta1x512/store37748736x32/output1048577x512，37帧与预设一致。
- 唯一全深度setup独立审核 `check_retained_edges_rtl_setup.py` 已启动，PID2190154 / exec49575，正在逐vector/hash扫描；不要重复运行。预期results/retained_edges_rtl_setup_20261024_v1.json，目前尚无报告。需要用write_stdin session49575接收终态（不是functions.wait）。原RTL pipeline将继续自动后续仿真及最终审核。
- width64实验仍HLS微架构生成；真实edge原两workers继续，完整目标active，RTL/物理/自主PL控制与实板尚未完成。

## 最新：packet扩宽单变量独立审核器与终态自动审核已就绪（2026-10-24）

- 新 `check_search_packet_width.py` 要求原实验正常终态、全部源hash/逐文件单变量推导、两模式真实sanitizer日志、Csim/synthesis markers/receipts、实际2022.2/xcu280/5ns/1.35ns与7总线。baseline top RTL须匹配原物理负结果绑定；两边XML宽度均交叉检查实际RTL参数。报告输入512是否缩减/是否64、资源差值、静态latency与原warning计数，明确不证明关键路径消除或时序改善。
- `tests/test_search_packet_width.py` 正反例通过（含缺失/错误/重复RTL参数拒绝），并读实际原XML+RTL确认均512。不是新综合或RTL结果。
- 唯一 `supervise_search_packet_width.py` owner2149800 / exec71023，目录search_packet_width64_20261024_v1/audit_supervisor，/proc核实live；只等原owner2096766正常终态，自动一次独立比较到results/search_packet_width64_comparison_20261024_v1.json。已冻结checker/监督器/plan依赖，勿改或竞争审核。若无缩宽也保留负结果，不因工具成功宣称优化。
- 原实验仍实际HLS调度中，原edge输入生成与真实负载保持其原owners；本轮无新终态达标结果。完整目标active，下一步以真实结构结果决定RTL/物理对照，同时继续整体控制与实板缺口。

## 最新：搜索packet自动扩宽单变量结构对照已启动（2026-10-24）

- 原CSR最差路径证据含packet地址低6位→控制选择，实际baseline input_mem_RDATA=512。已查AMD 2022.2官方pragma-HLS-interface确认max_widen_bitwidth可用；文档URL绑定在新plan。仅在隔离top的packet pragma增加max_widen_bitwidth=64，不改算法/参数顺序/指针depth/容量/时钟，原全部source冻结不动。是否改变共享bundle宽度必须读实际综合结果，不能由pragma推断。
- 新 `search_packet_width_experiment.py`，bundle/project search_packet_width64_20261024_v1，唯一owner2096766 / exec92264，CPU122。验证原v3所有source hash，复制flat source，冻结单变量及负结果基线/路径报告。按两模式完整声明workspace二事务ASAN/UBSAN预检→CSR实际2022.2 Csim/csynth，5ns/1.35ns、pipeline_loops0不变。两模式均完成compile/preflight（status/cost/path分别0/35/2及3/0/0），当前已进入实际HLS且/proc核实live。没有RTL/时序收益或达标结论。
- Ross hls-optimize技能经检查依赖vitis-run/Unified组件与专用报告函数，本机2022.2流程不适用；未运行其init-git、未改全局技能或基线，继续既有本机Tcl/哈希冻结实验法与已应用pragma-scope规则。下一步对实际端口宽度/调度/RTL地址选择逻辑与资源作独立比较，只有结构证据后再决定更昂贵验证，不能以3.65ns估计替代物理达标。
- 原edge RTL仍在prepare生成37帧（ref.tcl尚未填完），真实与旧RTL各原owners继续，不因生成慢重启。完整目标active。

## 最新：原compact物理仍在拥塞修复；边RTL输入深度审核器已准备（2026-10-24）

- 本轮先MCP list sessions，仅读compact原会话status，不执行Tcl、不动B/冻结CSR/恢复会话。MCP确认session vivado-20261024-200724-c151e46f / PID4159154 running精确原source、queue0；中间WNS=-2.107、TNS=-22446.562，原log在Phase4.2 Global Iteration1拥塞修复。非终态，不作达标结论，不能重启。只读snapshot保存compact_observation_20261024_2354.json（以其observed_utc字段为准）。
- 原snapshot RTL owner3082954仍实际live在elaborate，不凭长时间静默判失败；原edge RTL owner1977135/prepare child1992361仍live，实际cosim.tv.exe2007610在生成全深度37帧。原真实CSR/compact workers仍按原owner执行。
- 新 `check_retained_edges_rtl_setup.py` +两组parser负例测试通过。待原setup.json/execution_plan.json生成后，命令 `python3 scripts/check_retained_edges_rtl_setup.py --bundle data/derived/retained_edges_rtl_20261024_v1 --output results/retained_edges_rtl_setup_20261024_v1.json`；审核7实际vectors的37帧、指针/packed depth、全部hash与Csim/CPU/golden。预设input2097154x256/meta1x512/store37748736x32/output1048577x512，必须与实际ref.tcl精确一致；若不一致先核实实际wrapc layout，不能绕过深度门。
- 本轮尚无新RTL或物理终态通过证据。完整目标active，继续原运行与整体控制、时序修复及实板验收。

## 最新：路径不同声明深度可按最大容量共享，新增v6候选修正过严限制（2026-10-24）

- 更正v5交接说明：HLS声明depth不同本身不禁止同类型端口共享更大BO。无需为了depth差异必然加入copy kernel；必须给BO提供所有端口需要的最大容量，并保持count界限和访问顺序。v5独立BO方案及其负例保留，不篡改原证据。
- 新 `resident_router_memory_allocate_v6.py` 仅允许已知u32 search/tree/retained-edge path组存在不同深度，按max(payload)对齐分配，其他异深alias仍拒绝，保持component内不alias与bundle bank union。新generator/checker v6和 `hardware/vitis/resident_router_memory_v6`：74指针/54BO/935059456bytes/30名义HBM通道。路径BO64MiB，search/tree访问声明前16MiB，edge允许完整64MiB；search实际count上限524288边，edge append只消费实际count。
- 独立 `results/resident_router_memory_audit_20261024_v6.json` SHA=3e5ad80d0de926b1fb9a3522b9a9001b2d511082241fa5d319831e8fffd108dd，status=nine_component_shared_buffer_capacity_independently_checked_platform_pending。20种隔离损坏拒绝通过，新增共享BO错误缩小到16MiB、元素宽度不兼容。相较v5减少1BO/16MiB/1名义通道；无实际带宽收益结论。
- 这仅落实静态容量与连接，不证明内存拓扑/group intersection、BO同时分配、跨CU启动/完成与生命周期安全、实板吞吐；完整RTL TB仍需按各port原声明depth，不缩减。原edge RTL owner1977135/child1992361本轮/proc确认live在prepare，真实两workers也继续原owner；完整目标active。

## 最新：有序边存储37事务完整深度RTL流程已启动（2026-10-24）

- 新 `test_retained_edges_rtl.cpp` 独立map-vector+literal状态oracle，不include DUT header/helper。六指针完整声明深度+guards，每次比较两完整bank/meta/完整output及tail/输入不变；实际2097152边、逐8字段/重复顺序、满容量append与跨net拒绝、后位非法src/dst/dir、版本饱和、reserved/宽度/invalid状态与恢复、显式seed65536非空net边界。
- 初始CPU严格C++14 ASAN/UBSAN执行37事务通过，独立 `retained_edges_rtl_contract.py` 字面37行一致；两组parser负例测试通过。`results/retained_edges_rtl_tb_cpu_20261024_v1.json` 绑定TB/core/contract/test/log/binary，不代表RTL结果。
- 新 `retained_edges_rtl_pipeline.py` / `check_retained_edges_rtl.py` 基于已用retained-nodes流程，复用冻结边HLS实际RTL，不改原综合。唯一owner1977135 / exec20900，bundle/project retained_edges_rtl_20261024_v1，/proc需按state child继续核对。原owner自动CPU/Csim/setup/xelab→10sec bounded RTL37→原generated-C完整postcheck→独立审核。预期results/retained_edges_rtl_audit_20261024_v1.json，production_retained_edges_full_depth_37_transactions_rtl_verified。勿重复提交/审核。
- 新edge综合实际read widths input256/meta512/store32/output512；后续setup独立审核必须以生成ref.tcl和wrapc offsets为准，不能套用node retention的64位总线depth。
- 原全真实owner1915928及worker1916017/1916019已/proc核实live，约2分钟、completed=[]，仍由原supervisor续跑。完整目标active，物理时序/整体控制/平台实板未完成。

## 最新：边存储完整随机差分通过，全真实已运行；九组件连接容量审核通过（2026-10-24）

- 原随机runner1829661/1829662已正常结束，唯一real_supervisor1907852完成独立审核与准备，进入full_real。`results/retained_edges_component_20261024_v1.json` SHA=b96630a41fdd927b27cfbff51f9019b2b23ba04bde359626f6487fe50d5983dd，status=retained_edges_full_random_router_differential_verified_real_workload_pending，400cases/4938searches/3750snapshots/1250rounds及全部路径/需求/状态一致。只解码存储get结果作为最终route.edges；raw路径实际驱动append。
- 原supervisor自动启动唯一真实owner1915928，bundle retained_edges_router_20261024_v1，worker1916017/1916019均/proc确认live，completed=[]。CSR/compact原两批1062网设置保持；原owner负责raw终态审核，勿竞争或重复提交。预期results/retained_edges_router_audit_20261024_v1.json。
- 新v5 generator/checker与hardware/vitis/resident_router_memory_v5：九组件74指针/55唯一BO/951836672bytes/31名义HBM通道；`results/resident_router_memory_audit_20261024_v5.json` SHA=1676ea2003929cd37f7cda62ebb26c3950f258091c3836c05a2f3127a1d011d6，status=nine_component_shared_buffer_capacity_independently_checked_platform_pending。18种隔离损坏拒绝通过，新增edge错误alias/同bundle错bank/深度篡改。
- 搜索path4194304u32与edge path16777216u32声明不同，不能直接声明同BO ABI等价。v5保留独立输入BO，显式标注需有界copy/control stage；此cfg未实现该阶段。容量通过不代表设备buffer分配、31通道带宽或实际link通过，现有XO/平台/RTL前提仍未齐备。下一步补edge完整深度RTL与整体控制/路径交接，接收原长任务终态；完整目标active。

## 最新：边存储随机差分→全真实工作负载自动续跑已挂接（2026-10-24）

- 新 `prepare_retained_edges_real.py` / `retained_edges_router_pipeline.py` / `check_retained_edges_router.py`：要求随机差分独立报告与实际完整router编译证据，复核全部输入；CSR/compact各两批1062网，cache4096/max80/budget200000/presentcap8原设置不变；对完整raw语义和CC/SC/KC与已审核round-control前驱比较。静态方案不替代运行，真实测量仍为CPU。
- 唯一 `supervise_retained_edges_integration.py` owner1907852 / exec64563已运行并/proc确认，目录`retained_edges_integration_20261024_v1/real_supervisor`。冻结七续跑依赖，等待原runner1829661精确/proc identity；成功后一次独立随机审核→准备新真实bundle→唯一两模式流水线及终态审核。缺失/失败均保留并停止，不自动重启，不竞争审核。
- 随机原child1829662在本轮核实live（已运行约2分半），没有终态输出；supervisor当前await_original_randomized_run，不能提前宣称完成。预期component report `results/retained_edges_component_20261024_v1.json`，真实bundle `data/derived/retained_edges_router_20261024_v1`，最终 `results/retained_edges_router_audit_20261024_v1.json`。不要手工再次审核/提交与owner竞争。
- 完整目标仍active；继续接收此流水线与原RTL结果，推进边存储完整RTL/第九组件连接、自主PL控制、特殊资源、200MHz物理时序与平台实板性能/功耗验收。

## 最新：边存储Csim/综合独立审核通过，完整router已编译（2026-10-24）

- HLS owner1849854和supervisor1852352均正常终态；`results/retained_edges_synthesis_review_20261024_v1.json` status=retained_edges_csim_and_synthesis_verified_rtl_pending。实际2022.2/xcu280/5ns/1.35ns、全2097152边Csim与综合通过，全部source/report/RTL绑定重核。LUT85494/FF34908/DSP0/BRAM0/URAM0，3.65ns估计；HLS200-880=52/878=10/885=1、RTGEN206-101=13。不代表RTL、物理或板卡通过。
- 新 `compile_retained_edges_router.py` 使用原regular objects和实际新edge top编译完整真实router，exec7459；`regular_build_complete.json` 已生成compiled、二进制hash和输入计划。独立CPU120构建，不干扰随机差分CPU119。
- 新 `check_retained_edges_integration.py` 已准备：要求原随机runner正常complete、全部95输入/binary/log绑定、实际driver+sanitized edge object命令、逐源文件复现routes/search变换、精确400cases/4938searches/3750snapshots/1250rounds及完整结果。终态后执行 `python3 scripts/check_retained_edges_integration.py --bundle data/derived/retained_edges_integration_20261024_v1 --output results/retained_edges_component_20261024_v1.json`。当前原child1829662仍live，无终态；勿提前宣称pass或重复启动。
- 下一步接收随机差分、启动完整真实CSR/compact各两批，然后全深度RTL/第九组件memory方案及自主控制、时序与实板。完整目标active。

## 最新：物理边存储实际2022.2 Csim/综合已启动（2026-10-24）

- 新 `retained_edges_hls_pipeline.py` + `run_retained_edges_synthesis.tcl` 使用既有CPU sanitizer证据作门，冻结最小flat source/test。已唯一运行bundle/project `retained_edges_hls_20261024_v1`，owner1849854 / child1849856 / exec9434，/proc核实live。目标xcu280、5ns/1.35ns不变，csim实际全2097152边容量，随后csynth，不缩减生产深度。
- 独立supervisor owner1852352 / exec2652已启动并核实live。只等待原owner、终态一次审核，不重启流；新checker核对两个CPU标记/实际2022.2 XML/四AXI端口/资源/原始warnings及全部hash。预期 `results/retained_edges_synthesis_review_20261024_v1.json` status=retained_edges_csim_and_synthesis_verified_rtl_pending，不代表RTL/物理/板卡通过。
- 原边接入完整随机差分owner1829661/child1829662仍实际live CPU119，保持原exec15918。当前无终态输出；继续原进程，不重复提交。完整目标仍active。

## 最新：round-control全真实审核完成；边存储已接入并启动完整随机差分（2026-10-24）

- round-control原owner与审核子进程均已退出，state=complete/independently_audited。`results/round_control_router_audit_20261024_v1.json` SHA=4fdebf1ea71663691fb14b69f09471622f0ddde9a63608146f7e0b7a41e27e8d，status=round_control_two_full_router_conditions_independently_verified。CSR/compact各两批1062网，每批16836 searches，所有原始路径与中间语义一致；hardware_executed=false，不解释为设备性能。
- 新 `retained_edges_adapter.hpp` + `retained_edges_routes_transform.py`：每net清空旧edges；search/tree accept后直接将原始w.path/result[7]送实际edge top append，connection.path只用于观察；最终route.edges从edge top get的完整字段恢复。依旧无跨组件rollback，edge失败必须中止，不能把已accept tree伪装回滚。
- 隔离 `data/derived/retained_edges_integration_20261024_v1`，冻结95输入/对象与command。严格-Werror/C++14 edge top ASAN对象及完整C++17 ASAN差分编译已成功（原compile exec85733正常exit0）。实际 `run_retained_edges_integration.py` 已唯一启动，exec15918；以run_state的owner/child PID及/proc核实运行，勿重复。保留原driver输出标签ROUND_CONTROL_ROUTE_*，不是测试旧版本；driver实际include已变更snapshot_test_routes和raw search adapter。
- runner精确要求400cases/4938searches/3750snapshots/1250rounds、完整结果与原native一致，运行前后复核全部95绑定，保留sanitizer错误，不自动重启。尚未得到差分终态，不宣称验证通过。后续完整真实工作负载、HLS/RTL/内存方案/实板均仍需推进。完整目标active。

## 最新：有界有序物理边存储核心CPU验证通过，待路由接入（2026-10-24）

- 新 `search_retained_edges.hpp` / `search_retained_edges_top.cpp`，reset/replace/get/append，完整8u32边字段，按net分组且组内严格保留插入顺序与重复边。双bank预检后写入/翻转，状态容量2097152 edges/65536 nonempty nets/1048576 nodes；错误不改两bank/meta，get不改tail。外部trusted/exclusive/disjoint状态，非图邻接/路径连续性检查器。
- 实际top C++14 ASAN/UBSAN通过独立map-vector 4000操作（1287接受/2713拒绝），实际填满2097152边并逐word读回，overflow/清空/重复append/属性及方向保留测试。`results/retained_edges_cpu_20261024_v1.json` 绑定源码、二进制、日志与说明。pragma均在top函数体，核心无动态分配/递归/STL，符合已读Ross作用域与可综合子集规则；这不替代实际HLS结果。
- 当前每次update复制保留总体到inactive bank，只是正确性参考策略，无性能收益结论。尚未接入完整router、HLS/RTL、memory v4或设备。下一步从实际raw search path append、每net重布前清空、最终get替换主机route.edges，再完整随机/真实差分及HLS。完整实验目标active。
- round-control真实两workers已结束，原owner1139799仍有独立审核子进程1675744；保持唯一原审核，不重复提交。

## 最新：八组件共享内存连接候选已独立审核（2026-10-24）

- 新 `resident_router_memory_plan_v4.py` / `check_resident_router_memory_plan_v4.py`，保留v3冻结方案，新增round-control四指针并将counts与node occupancy实际counts BO共享。生成 `hardware/vitis/resident_router_memory_v4` 的HBM/DDR候选：68指针、49唯一BO、666611712申请字节、27名义HBM通道。
- 独立 `results/resident_router_memory_audit_20261024_v4.json` SHA=1cbd3ea0f77b91cc9e2987d118837401522ce9bb5c4c351fe553d70c03968694，status=eight_component_shared_buffer_capacity_independently_checked_platform_pending。检查全部BO容量、对齐、共享端口、bundle银行一致性及配置；15种隔离实际manifest损坏拒绝测试通过，包含round counts错银行、删除共享关系、complete/control同bundle错银行。
- 这是静态候选，不代表八XO全部导出、真实平台link/MEM_TOPOLOGY/group交集、49BO同时设备分配、跨CU控制或板卡性能。completion flags仍由外层写入，edge retention及自主scheduler仍未完成。原RTL流水线保持运行，完整实验目标active。

## 最新：轮判断RTL两版实际运行，新版单owner输入已独立审核（2026-10-24）

- 实际ps确认v1 owner1439224 / xsim1468887、v2 owner1563966 / xsim1590073均存活；各原pipeline继续自动终态审核，不重复提交。retention/site/tree/search-boundary原xsim也仍存在；这不是Inspire调度队列。
- 新 `scripts/check_round_control_rtl_setup_v2.py` 保留v1全部37事务/完整AXI深度/输入绑定审核，并读取实际二进制count_mem首帧，要求1048576个32位word全部等于1。该合成输入预期conflict groups=0，覆盖单owner阈值；不能当成RTL已通过。
- 新threshold parser测试通过，覆盖截断、首位0、末位2、深度错误拒绝。独立 `results/round_control_rtl_setup_20261024_v2.json` SHA=74a368dc58e23a358e63770ee21da243d098c0407201358f61d0bea3ed8242dd，status=production_round_control_full_capacity_37_transaction_setup_independently_verified_rtl_pending。v1源码、报告和两版原流水线均保持。
- 下一步接收原RTL终态与37事务generated-C postcheck，继续整体控制/保留边、特殊资源、结构性时序修复及平台实板验收；完整目标尚未完成。

## 最新：只读轮判断组件已接入并综合；CSR恢复终态审核仍未过时序（2026-10-24）

- 新 `hardware/vitis/search_round_control.hpp` / `search_round_control_top.cpp` 只读resident node counts、当前轮query complete flags和原site analyze group count。4指针/3AXI，control8/counts1048576u32/complete65536u32/result8。结果包括node groups/incomplete/action/next iteration/next present/advance flag/current present；保持原min(2^min(iter,20),cap)，不直接改任何history。无冲突时按完整性终止；有冲突最后允许轮也要求advance两history再结束。支持uint32 iteration/max迭代边界，activeflag必须0/1，错误清零结果其余字段，inputs不变。ABI见 `hardware/vitis/SEARCH_ROUND_CONTROL_V1.md`；这不是完整PL自主scheduler。
- `tests/test_search_round_control.cpp` 独立3000组合、最大声明domain/net input、末位非法flag、13拒绝、penalty饱和/uint32末端、final-conflict advance及完整inputs/guards不变，实际top严格C++14 ASAN/UBSAN通过。输入为合成counts/flags，不宣称其均由完整ledger运行生成。新 `round_control_adapter.hpp` 直接收tree complete；`site_occupancy_round_adapter.hpp::analyze_groups`返回raw helper count。`round_control_routes_transform.py` 将action/penalty/history是否推进交实际top决定；原map仅观察/一致性检查，host仍执行各component、保留edge traces/执行loop，无跨组件rollback或PL跨CU启动证明。
- 隔离准备 `data/derived/round_control_router_20261024_v1` **owner1037384 / exec83333** 已正常终态，实际全部旧components+新top完成400完整随机协商/4938 searches/3750 snapshots/1250 rounds，路径/成本/需求/unknown/各轮冲突与完整结果均等；node-history2412/site-history2106/site-paths2896，routed210/incomplete190，无native邻接回退，完整router已编译。独立 `results/round_control_component_20261024_v1.json` SHA=91c759d41fcf16e8cae5200a5bde1698f27fb98dbd34c08a7115be02d5d3cd05，status=`round_decision_and_full_search_differential_independently_verified`。绑定source/test/adapters/scripts冻结，修改须新版本。
- 新全真实唯一 `round_control_router_pipeline.py` **owner1139799 / exec14102**，CSR **1139802 CPU116** / compact **1139803 CPU117** 已核实live，completed=[]，原两模式各两批1062网/80轮/budget200000/presentcap8不变，原owner自动全raw/CC/SC/KC审核；预期 `results/round_control_router_audit_20261024_v1.json` status=`round_control_two_full_router_conditions_independently_verified`。不重复提交或竞争审核。
- 新HLS owner1139804/exec2696及唯一supervisor1142338/exec9846均正常终态；bundle/project=`round_control_hls_20261024_v1`。实际2022.2/xcu280/5ns/1.35ns Csim+综合审核通过，`results/round_control_synthesis_review_20261024_v1.json` SHA=2b8bbfdb27c9b42fb71812da6d4c79666d63afee6a31b277b6b036b04c9fafb8，status=`round_control_csim_and_synthesis_verified_rtl_pending`；LUT17171/FF9495/DSP0/BRAM0/URAM0，3.65ns估计，warnings200-878=7/RTGEN206-101=13。read widths input64/count32/output512。未跑本组件RTL/设备；旧七组件memory plan不含此第八组件。
- **retained-nodes前驱全真实终态审核通过**：`results/retained_nodes_router_audit_20261024_v1.json` SHA=897ccd480265b01fff19d5735f7b0cd4c92b051f40f8c434c1885511bdfd11f1，status=`retained_nodes_two_full_router_conditions_independently_verified`。旧owner235812已退出，不重跑。
- **CSR恢复v2 source正常终态code0**：633621/session vivado-20261024-230509-704f773a在UTC23:24:55完成。已先保存 `terminal_mcp_status.json`（queue0/idle/code0）与完整 `terminal_mcp_history.json`（唯一精确source/elapsed1126.105/marker）。此会话/日志现冻结，勿再执行Tcl。新todo3/3完成，表示实验与审核完成，不代表时序修复。v1 abort现场仍保持，未把它改成成功。
- 独立 `results/search_kernel_csr_physopt_recovery_audit_20261024_v1.json` SHA=aaabf30df0df02753e1afc3b6fc2962b729a6dc7e1910e4ad0f2c153aa8fae64，status=`csr_postroute_recovery_completed_quality_gates_not_met`；退出1为真实quality失败、报告已生成。5ns/1.35ns不变，全部网络布通/internal constraint checks clear，但**WNS=-1.307ns/TNS=-18122.939ns、36399/346271 setup端点失败**；比原baseline改善0.082ns，LUT+6、FF/BRAM/DSP等不变。DRC/methodology仍未清，不豁免。没有平台时序或实板通过结论。下一步需结构性HLS/RTL对照，不能靠工具exit0或82ps改善宣称200MHz达标。
- 原retention/tree/site/boundary RTL、snapshot elaborate、compact物理仍各自原owner运行，本轮未改变。项目check通过。本轮progress，完整目标active；继续round-control完整深度RTL、整体控制/edge retention、特殊资源、时序修复与平台/实板验收。

## 最新：CSR physopt v1实际abort，已保留现场并从检查点启动隔离恢复（2026-10-24）

- **不要继续等待v1 PID3952737/session vivado-20261024-223355-9aeb1811**：/proc进程缺失，MCP返回session not found，现有sessions列表也无此会话。v1 state.json仍running/explore_reroute是崩溃前旧状态，不代表live。发现 `hs_err_pid3952737.log` unexpected error(6)，stack含abort/realloc、libudev设备枚举、Xil许可证host info与WebTalk代码。根因未证明，不把它解释为缺许可证或算法失败，也未猜测OOM。
- v1日志router末尾给WNS=-1.307/TNS=-18122.939/WHS0.015，但无最终optimized_routed.dcp/after报告/成功terminal history。仅已保存 `optimized.dcp`（post-phys-opt、pre-reroute），zip全部23members CRC通过。独立事故记录 `results/search_kernel_csr_physopt_incident_20261024_v1.json` SHA=bf342a48a15aa03e3514cd2421fabfad1b598d3762e288551b00efa99e507f85；保留原stale state/log/crash/plan/script/checkpoint，不发布v1质量通过报告。
- 现有3个稳定Vivado会话4146646/4159154/2607458均可确认LD_PRELOAD=/lib/x86_64-linux-gnu/libudev.so.1；新恢复会话显式使用同一值并在/proc验证。v1运行时environ未留存，不能断言其实际值或已证明崩溃根因。未改任何全局WebTalk/许可配置。
- 新隔离目录 **`data/derived/search_kernel_csr_physopt_20261024_v2`**，新Tcl无GUI MCP **`vivado-20261024-230509-704f773a` / PID633621**。plan/hash绑定完整v1 incident及优化检查点、原negative CSR audit、原before reports。source只重开优化检查点→实际resume_input timing/XDC→Explore/-tns_cleanup reroute→新DCP/全报告；**不再运行phys_opt_design**，保持5ns/1.35ns/原part，无exception/waiver。原CSR基线会话/日志仍不动且摘要重核未改变。
- 新source已唯一提交，**不要再次source**。调用曾在functions cell4735等待，现已收取MCP300s running handoff、cell4735已结束不用再wait。startup/submission_mcp_response.json和observation_0001.json保存。最新actual state explore_reroute，MCP确认PID633621 live/current_command精确匹配/queue0。实际DCP重开成功，resume_input STA WNS=-1.307/TNS=-18190.85、36423/346271 setup端点失败；XDC仍1.35ns。该输入检查不是新终态，也不构成修复。
- 提交/恢复检查证据 `results/search_kernel_csr_physopt_recovery_submission_20261024_v1.json` SHA=784b34fba2cd452898ee64e80eb6ffc6ef8c517bfdb96ee53128e73024725e00，status=`csr_physopt_aborted_attempt_preserved_saved_checkpoint_reopened_recovery_routing_running`，记录/proc start_ticks与preload验证。`check_search_csr_physopt_recovery.py`/对应两组protocol tests已准备并通过；比较原baseline、实际resume_input与after，保持完整质量门。source/checker/tests及提交证据已绑定冻结。
- **新恢复终态仍必须先保存raw MCP status+完整history，再任何Tcl**。stage为physopt_complete_pending_independent_audit，markerCSR_PHYSOPT_FLOW_COMPLETE。命令：`python3 scripts/check_search_csr_physopt_recovery.py --bundle data/derived/search_kernel_csr_physopt_20261024_v2 --session-status <snapshot.json> --history <history.json> --output results/search_kernel_csr_physopt_recovery_audit_20261024_v1.json`；snapshot={session_id,observed_utc,status}。质量失败退出1但保留报告；不能拿旧router日志数字代替完整报告。新todo step2仍active、step3pending。
- 为后续真实控制实现补 `hardware/vitis/OUTER_CONTROL_REQUIREMENTS_V1.md`：严格保持net/sink排序/重复sink、release-before-snapshot、搜索结果/树接入、提交/轮终止/最后冲突轮仍advance的语义。node现有advance带history mutation，不能提前用它判定停机；需readonly计数或直接scan resident counts。单纯把主机命令列表有界化并不证明PL控制跨CU，七CU memory cfg也未提供该启动/完成控制路径。
- retention全真实235812仍live，completed=[0]；retention RTL395251/454996仍live，snapshot/tree等原长任务继续，不因等待重跑。项目check通过。本轮progress，完整目标active；恢复完成后仍需修复时序并完成控制、特殊资源、平台/实板实验。

## 最新：retained-nodes37事务完整深度RTL已实际运行，七组件静态内存计划通过（2026-10-24）

- 新 `hardware/vitis/test_retained_nodes_rtl.cpp` 不含DUT helper/header，独立ordered-map/字面pair序列oracle。6指针每次保持config8/meta6/rows4194304u64/nodes与output各1048576u32/result5全深度+guard；每事务逐字核对两完整bank、meta、output及stale tails/所有输入/guards。实际2次满域replace达到2097152pairs；满输出get/max-net/missing-net、移除/替换/空操作、无序重复/域外/保留字段/u32宽度、容量/overflow拒绝、恢复/reset共37事务。65536-net边界与version饱和明确为合法状态注入，不冒充自然生成。
- 严格C++14 ASAN/UBSAN、实际2022.2 Csim及cosim -setup均通过。`retained_nodes_rtl_contract.py` 独立字面37行结果；`tests/test_retained_nodes_rtl_contract.py` 缺行/改字段/性能序列负例通过，`test_retained_nodes_rtl_setup.py` binary/text帧正反测试通过。小fixture仅验parser，不是硬件性能证据。
- 唯一 `retained_nodes_rtl_pipeline.py` **owner395251 / exec94847**，bundle/project=`retained_nodes_rtl_20261024_v1`。复制原独立综合并保留全部syn字节，只换TB。xelab通过，实际RTL wrapper**454996**→真实xsimk **459268** 已从/proc所有线程children确认live，最新1/37（第一满域replace事务）。CPU119、64MiB栈，run10sec为仿真时间，不是墙钟超时。勿重启或重复postcheck/审核。
- 独立准备 `results/retained_nodes_rtl_setup_20261024_v1.json` SHA=e6586c02a258202d1bcdc41ac1fbc4add60d63d2cde3b44919d6e26b446b91bd，status=`production_retained_nodes_full_capacity_37_transaction_setup_independently_verified_rtl_pending`；270绑定、7个实际in/out向量逐37帧深度/字宽/总长/EOF/摘要核验通过。实际ref: input524296×64/meta1×512/store4194304×64/output65537×512，pointer config_r/meta/rows/nodes/output_r/result，input只读。独立启动证据 `results/retained_nodes_rtl_submission_20261024_v1.json` SHA=fde4c19b7c598288681b8bd629e149581b166a095b058a814299f564855458b4，status=`production_retained_nodes_full_capacity_37_transaction_rtl_started_not_yet_verified`。
- 原owner自动后继RTL→37行真实performance→原生成C全字postcheck→`check_retained_nodes_rtl.py`，预期 `results/retained_nodes_rtl_audit_20261024_v1.json` status=`production_retained_nodes_full_depth_37_transactions_rtl_verified`。绑定source/TB/pipeline/contracts/checkers冻结，修改用新版本。
- 新 `resident_router_memory_plan_v3.py` / `check_resident_router_memory_plan_v3.py`、目录 `hardware/vitis/resident_router_memory_v3` 加入retention输入共享tree.roots、输出共享node.old_nodes（不同BO但AXI bank兼容），额外config/meta/rows/result4BO。64参数→46BO，666341376bytes（635.47MiB，4KiB对齐），nominal HBM25通道；旧v1/v2不改。独立 `results/resident_router_memory_audit_20261024_v3.json` SHA=0d918721d0c89c28b61092b10ba8209605cc9689fe384821abc01b71f59c30d9，status=`seven_component_shared_buffer_capacity_independently_checked_platform_pending`，12类候选临时篡改拒绝，含retention两个alias。仍未actual XO ABI覆盖全部、v++ link、XRT group交集/46BO同时设备分配；count外控/retained edges/完整硬件调度仍缺。
- 原retention全真实owner235812仍live，completed=[]，继续原自动完整raw审核。CSR隔离physopt3952737已进入 **explore_reroute**（UTC22:49:13），仍原source，不重复运行；没有时序修复结论。snapshot/tree/site/boundary等长RTL继续原owners。项目check通过。
- 本轮progress，完整目标active。下一步接收37事务RTL/全真实原owner终态，补retention XO/控制ABI及实际七组件链接，并继续外层协商/edge retention、特殊资源、CSR/compact时序与实板实验；不把激励准备/静态635MiB容量当作设备/完整实验完成。

## 最新：每网规范节点有界保留已接入，CPU/Csim/综合通过，全真实运行（2026-10-24）

- 新 `hardware/vitis/search_retained_nodes.hpp` / `search_retained_nodes_top.cpp`：双bank sorted (net<<32)|canonical_node pairs，生产node domain1048576/pairs2097152/nets65536。meta6=[magic,domain,pairs,bank,nets,version]；config8 reset/replace/get，rows4194304u64/input/output各1048576u32/result5，6指针/4AXI bundles。get按net做有界binary bounds并导出sorted节点；replace全预检后复制inactive bank/flip，拒绝保持两bank/meta/output；reset仅metadata。net0/UINT32_MAX都合法，无sentinel合并。复制总保留人口是参考策略，不声称高吞吐。ABI/边界见 `hardware/vitis/SEARCH_RETAINED_NODES_V1.md`。
- `tests/test_search_retained_nodes.cpp` 独立map/set oracle6000操作（3106接受/2894拒绝），sorted/duplicate/domain、容量/版本overflow、两bank失败不变、missing/max-net、全buffer/guards/tails；实际2个满域route操作填满2097152pairs。65536-net边界由合法状态显式注入，非自然65536次更新。严格C++14 ASAN/UBSAN通过；复现 `check_retained_nodes_cpu.py` 要新build/report路径。报告 `results/retained_nodes_cpu_20261024_v1.json` SHA=3e5f98c960684a4628e14b527f303c38666b010ca5d29b06e65d3e03114411a9。
- 新 `src/native/retained_nodes_adapter.hpp`、`node_occupancy_retained_adapter.hpp`、`retained_nodes_routes_transform.py` 在隔离副本从retained.get取旧节点并一次bulk release，从tree roots一次bulk acquire及retained.replace；不再从主机result.routes查旧节点。node version改按bulk事务而非每节点计数；搜索费用/history/packet语义不变。route.nodes与边trace仍为观察输出保存，外层协商/跨组件失败回滚未硬件化，不能称整个router全硬件。旧六组件memory plan不含此第七组件及32MiB rows BO，未来需新版本。
- 准备 `data/derived/retained_nodes_router_20261024_v1` **owner164242 / exec11114** 已正常终态。新top/原production search/既有node-site-snapshot-tree-request组件400完整随机协商/4938 searches/3750 snapshots/1250 rounds与原native全部中间/最终结果相同；node-history2412/site-history2106/site-paths2896、routed210/incomplete190，无native邻接回退，完整router已编译。独立 `results/retained_nodes_component_20261024_v1.json` SHA=eed11b6c2a902db66f26ed5c55fd08b6fca35ccfec5be583ba2d853a5678724d，status=`retained_nodes_bulk_occupancy_and_full_search_differential_independently_verified`。绑定源码/test/adapter/transform/preparer/checker冻结，变更须新版本。
- 新全真实唯一 `retained_nodes_router_pipeline.py` **owner235812 / exec1303**；CSR **236218 CPU116** / compact **236220 CPU117** 已核实live，completed=[]，原两模式各两批1062网/cache4096/80轮/budget200000/presentcap8不变。原owner自动完整raw及CC/SC/KC核验，预期 `results/retained_nodes_router_audit_20261024_v1.json` status=`retained_nodes_two_full_router_conditions_independently_verified`。不重复提交/审核。
- 新HLS owner236412/exec97617已终态0，bundle/project=`retained_nodes_hls_20261024_v1`；本机2022.2/xcu280/5ns/1.35ns，实际Csim及csynth完成。唯一supervisor **238699 / exec65085** 已终态完成审阅。独立 `results/retained_nodes_synthesis_review_20261024_v1.json` SHA=0bff12393d169df022a1ef4678c925afa5cbe52ffe52898c13162bb3e6ddfca0，status=`retained_nodes_csim_and_synthesis_verified_rtl_pending`，36文件绑定已重核；LUT71639/FF30966/DSP0/BRAM0/URAM0、估计3.65ns，HLS200-878=9/200-880=42/RTGEN206-101=26。无明确positive循环summary时字段unknown，不因无negative推断全部满足。未执行本组件RTL/物理/XO/设备。
- **site-request前驱全真实已终态审核通过**：`results/site_request_router_audit_20261024_v1.json` SHA=e265965070f8fc00b088766307df81f462376253e254ba26cf56d800f96f1a74，status=`site_request_two_full_router_conditions_independently_verified`。旧owner3551068结束，勿重跑。
- 原snapshot/tree/site/boundary RTL及compact物理/CSR新physopt仍按原owners运行，本轮未更动。CSR新physopt state仍aggressive_fanout，继续原source，不重启。项目check通过。本轮progress，完整目标active；下一步给retention准备全深度RTL/第七组件实际连接，接收原长任务终态，继续外层控制/edge retention及全部特殊资源、时序修复和实板实验。

## 最新：CSR隔离post-route优化对照已实际运行，基线复现（2026-10-24）

- 按原真实WNS=-1.389失败启动新隔离实验，原CSR会话/日志/DCP与所有基线保持封存。先查询现有MCP sessions，再新建Tcl无GUI会话 **`vivado-20261024-223355-9aeb1811` / PID3952737**，目录 `data/derived/search_kernel_csr_physopt_20261024_v1`。本机实际 `help phys_opt_design` / `help route_design` 确认2022.2支持post-route AggressiveFanoutOpt及Explore/-tns_cleanup；完整help history保存 `local_help_mcp_history.json`。沿用Ross timing skill的2022.2文本替代流程。
- 冻结plan与 `run_flow.tcl`：只open原只读CSR routed.dcp，不改source/ABI/clock/uncertainty；重算before_timing并要求WNS与-1.389一致；随后 `phys_opt_design -directive AggressiveFanoutOpt` →新optimized.dcp→`route_design -directive Explore -tns_cleanup`→新optimized_routed.dcp及完整timing/check_timing/utilization/route/DRC/methodology/XDC/summary。5ns/1.35ns不变，无新增false path/multicycle/waiver。
- 唯一source已经执行，**不要再次source**。提交调用先yield为functions cell4686，随后收到MCP300s running handoff，原响应保存 `submission_mcp_response.json`，**cell4686已正常收取完成，不需再wait此cell**。新会话仍在执行原source。最新MCP observation_0001.json确认current_command精确相同、PID3952737真实live、queue0；state当前aggressive_fanout。工具提示negative slack幅度过大，post-route通常WNS>-0.5才更有效；当前已处理一些路径未改善，这不是终态或重启理由。
- 实际before报告已复现WNS=-1.389并核对原1.35ns约束。提交/基线复现证据 `results/search_kernel_csr_physopt_submission_20261024_v1.json` SHA=682b28908661aaac205acd32921d00440b5e00313dec4b3e8590c519ef6fe2b3，status=`isolated_csr_postroute_baseline_reproduced_optimization_running`；绑定原checkpoint/negative audit/flow/local help/真实MCP提交与live observation/before报告及新checker/tests，记录/proc start_ticks身份。不代表优化已修复。
- 预备独立 `scripts/check_search_csr_physopt.py`，终态后要求raw MCP成功idle+完整history相同source/exit/duration/完成marker，复核原基线所有绑定，before setup/hold/pulse endpoint/slack，原clock/uncertainty与无exception，after全部质量门/资源变化/实际improvement。`tests/test_search_csr_physopt.py` 两组nanosecond/protocol正反fixture通过（不是物理结果）。后续用fresh状态与history运行，输出新report，质量失败仍返回1并保留负结果。
- **终态先保存新会话raw status和完整history，再任何Tcl；之后不要改该log。** 预期完成stage=`physopt_complete_pending_independent_audit`，marker=`CSR_PHYSOPT_FLOW_COMPLETE`。审计命令：`python3 scripts/check_search_csr_physopt.py --bundle data/derived/search_kernel_csr_physopt_20261024_v1 --session-status <raw_snapshot.json> --history <full_history.json> --output results/search_kernel_csr_physopt_audit_20261024_v1.json`。snapshot格式{session_id,observed_utc,status}，不是mode字典。当前尚未终态，勿提前审核或重复运行。
- 新会话todo3步：1本机支持/冻结baseline已done；2原优化流程active；3终态/独立审核pending。只在真实完成后更新，不把质量失败隐藏。已绑定source/plan/checker/tests冻结，变更派生新版本。
- 原site-request全真实3551068已两workers结束，进入independent_full_audit（原owner live）；snapshot RTL3082954/3152131仍live在elaborate，tree RTL2929797/3001030仍live在RTL。继续各原owners；本轮未操作B或原CSR会话。项目check通过。
- 本轮progress，完整目标active；单次physical优化不保证达标，也不构成新功能等价证明。若终态仍失败，后续针对已定位动态地址/控制路径开展新HLS架构/分段实验，保持数据/资源语义及200MHz验收，不以降低目标替代修复；其他组件/XRT/外层控制/特殊资源/实板实验仍需继续。

## 最新：完整search CSR物理流程终态；已记录setup失败，compact仍运行（2026-10-24）

- MCP原CSR会话 `vivado-20261024-200659-4536a838` / PID4146646已返回原source成功（code0、queue0），state complete/ooc_complete_pending_independent_audit，完成UTC22:25:01；未重启/重source。已在任何新Tcl前保存原始终态 `data/derived/search_kernel_physical_20261024_v1/session_observation_20261024_csr_terminal.json`，完整MCP history另存 `csr_terminal_mcp_history.json`（1.66MB），source精确命令/exit0/elapsed7747.38/实际完成marker均一致。**CSR Vivado会话及其log现已被审核绑定，后续勿在该会话执行Tcl导致log改变；新实验使用隔离会话。**
- MCP status的last_completed_output仅展示截断片段，不含尾部marker，原双模式checker的该假设不足。新 `scripts/check_search_kernel_physical_mode.py` 使用未改动raw status与单独完整MCP history交叉核对，不伪造/替换status字段；可只审核已完成一模式，明确full_two_mode_physical_audit_complete=False。首次Python3.10不接受history纳秒timestamp，规范化至微秒后重审；无失败报告被发布。`tests/test_search_kernel_physical_mode.py` 实际纳秒history正例及11个running/stale/错误owner/命令/代码/marker/耗时负例通过。
- 独立 `results/search_kernel_physical_csr_audit_20261024_v1.json` SHA=f555cffe72ff6f93219a3a9c4bf674d5f76a7c8688167595d280ed91c6b9b38d，status=`selected_search_mode_ooc_completed_with_quality_failures_or_review_required`。**这是真实负结果，脚本返回1表示质量门未过，不是报告生成失败。** 原RTL/ROM、约束/计划、综合/放置/布线DCP、全部report、日志/提交/终态/历史均核验绑定；仅CSR，不能当成两表示整体物理完成。
- CSR239662/239662 routable nets全部布通、routing errors0；内部clock/constraint checks clear。保持原5ns/200MHz、setup uncertainty1.35ns：**WNS=-1.389ns、TNS=-18207.627ns、36424/346271 setup端点失败**。hold slack0.015ns/失败0、pulse width1.958ns/失败0。DRC报告83 warning（DPIP-2=10,DPOP-3=21,DPOP-4=51,RTSTAT-10=1），methodology报告2001（TIMING-16=1000,TIMING-18=1000,TIMING-44=1），质量门保留为false，不豁免/降低约束。
- 实际post-route资源LUT105963/FF141943/RAMB36=224/RAMB18=16/URAM0/DSP77，非HLS估计。裸器件OOC仍缺外部IO延迟（input1856/output2204），不证明U280 shell/平台时序。沿用已读Ross timing methodology skill；其2026.1+ JSON流程不适用本机2022.2，因此分析原2022.2文本报告，无新工具命令/约束修改。
- 路径证据 `results/search_kernel_physical_csr_path_analysis_20261024_v1.json` SHA=a5b9113520ed3dabadb58880b21e290b9ee7ecbbeee48e18fb60d4487c7af79f。报告10条最差setup路径均从trunc_ln42_1_reg_38274低位出发；最差到ap_CS_fsm_reg[6699]/D，22级逻辑、5.018ns数据延迟（logic1.730/route3.288，布线65.527%）。实际原RTL证明packet_read_reg_36101<=packet，再取[5:0]进该寄存器；这定位相关packet地址低位路径，不证明全部36424端点根因。候选新实验为地址/控制逻辑分段、层级/扇出调整；若使用对齐特化，必须新ABI强制校验，不能静默假设低位0。
- 原compact会话 `vivado-20261024-200724-c151e46f` /4159154最新仍原source运行、queue0，日志拥塞level6。不得重复source；终态同样先保存raw status+完整history，再用新版本完成两模式审核。原v1双模式checker不修改，未来修正须派生版本。
- 其他长任务原owners仍在运行；本轮未改六组件源或XO。项目check通过。本轮progress，完整目标active。下一步在隔离版本量化修复CSR时序并等待compact，继续长RTL/全真实原owner验收，以及实际平台/BO/外层控制/特殊资源/实板实验；不能把工具exit0或全部布通当成5ns质量门通过。

## 最新：已RTL通过的node/site-request组件XO已导出并审核（2026-10-24）

- 新 `scripts/export_resident_component_xo.py` 仅接受当前已独立RTL通过的node_occupancy/site_request。先核验原RTL报告全部文件，再复制原HLS project（排除csim/sim），保存全部原及复制syn摘要；本机2022.2运行 `export_design -format xo -rtl verilog`，前后重核syn与输入不变。没有改原HLS/RTL/物理工程，也不重复csynth。
- site-request导出 **owner3669130 / exec60046** 已终态0，bundle=`data/derived/site_request_xo_20261024_v1`，XO=`search_site_request_top.xo`。node导出 **owner3674595 / exec8454** 已终态0，bundle=`data/derived/node_occupancy_xo_20261024_v1`，XO=`search_node_occupancy_top.xo`。勿重复导出覆盖。
- 新 `check_resident_component_xo.py` 检查archive全部RTL/.dat成员字节、kernel identity/ap_ctrl_chain、pointer名字/顺序/类型/宽度、控制寄存器不重叠与范围。站点初审保留v1。加强版 `check_resident_component_xo_v2.py` 额外对照原csynth XML的RDATA位宽、拒绝重复RTL basename；两真实XO均通过。`tests/test_resident_component_xo.py` 在临时archive复制品分别修改RTL字节和XML AXI宽度，正确拒绝且不发布报告，未改真实产物。
- **node XO审核** `results/node_occupancy_xo_audit_20261024_v1.json` SHA=eee5250278bd3de6aff54d27ecf618c4970c0a8b5f06be5ac99411a1017f842f，status=`rtl_verified_component_xo_archive_and_control_abi_independently_verified`，10指针。实际offset：config16/meta28/counts40/history52/keys64/flags76/old_nodes88/new_nodes100/output112/result124；bundle数据宽度由实际XML及syn共同核对（table512/meta256/output256等）。
- **site-request加强XO审核** `results/site_request_xo_audit_20261024_v2.json` SHA=5c3d3eb3939596d6657565449cb3a3aff5a9b9a6eb59b29164a6c530fdd7bad6，同status，3指针；state offset16/input64，request28/result40/output128。所有控制ABI均来自实际导出kernel.xml，不再只有source推断。源码/runner/checkers/已导出XO冻结，修改须新版本。
- 仍未平台link、MEM_TOPOLOGY/group兼容交集、42BO设备分配或设备执行。六组件memory候选只对这两个新组件取得actual XO ABI，site/snapshot/tree及完整search export/链接门仍待各自RTL证明；不能用这两个XO缩小完整实验要求。
- 原site-request全真实owner3551068仍live运行，completed=[]；原snapshot RTL owner3082954/child3152131仍live在elaborate；原tree RTL2929797/3001030仍live在RTL。保留唯一owner，不重启静默长任务。项目check通过。
- 本轮progress，完整目标active。下一步收取原长任务终态，为其余组件按同样隔离方式导出/审核XO，并推进实际XRT连接、外层协商/retained route有界实现及全部特殊资源/实板带宽功耗。

## 最新：site-request完整34事务RTL已通过；六组件内存连接候选已审核（2026-10-24）

- 新 `hardware/vitis/test_site_request_rtl.cpp` 不含DUT helper/header，独立字面65word packing+ordered-map oracle；34事务所有3指针保持state65/request196608/result2完整深度+guards，逐字比较所有request及stale tails/input/result。覆盖20组不同计数、满56记录、空输入、零mask/最高ID、未用slots忽略、9无效状态拒绝不变和恢复。`site_request_rtl_contract.py` 独立字面34结果；`test_site_request_rtl_contract.py` 与 `test_site_request_rtl_setup.py` 正反parser测试通过。
- 唯一 `site_request_rtl_pipeline.py` **owner3533566 / exec8521** 已终态退出0；bundle/project=`site_request_rtl_20261024_v1`。原综合syn全部字节保留，仅换TB。实际严格C++14 ASAN/UBSAN、HLS Csim/cosim-setup、xelab、XSim34事务、原生成C逐字postcheck、原自动audit全通过，不重跑。
- 独立准备 `results/site_request_rtl_setup_20261024_v1.json` SHA=632d08573af5a453077e57ba5e2e4c971b8efd5f17ccd3439b3af9eaebda629b，status=`production_site_request_full_capacity_34_transaction_setup_independently_verified_rtl_pending`；实际ref为input_mem65×64/output_mem98305×128，3个in/out vector每个34帧深度/字宽/长度/EOF和摘要通过。
- **采用修正文案的最终RTL审核** `results/site_request_rtl_audit_20261024_v2.json` SHA=12f443bb578e6acd320ffac9b5be1158a449763b2ddf8e7dd2046dc8f7adf079，status=`production_site_request_full_depth_34_transactions_rtl_verified`。原v1 SHA=7368486fc0a24bf99bf738871260f9047a82fc38cc5a8eb2b376002b738c3b71的305绑定已实际逐项重核，但其postcheck描述误沿用tree的metadata/bitset/roots。保留v1不改，`check_site_request_rtl_v2.py` 重审同一真实run/receipts/cycles并改为实际request全字/tails/input/result guards，不重跑仿真。34周期列表保留，满56记录两事务均1702cycles；不是实卡或完整router吞吐证据。
- 新组件综合估计3.65ns、LUT18521/FF8311/DSP0/BRAM0/URAM0，HLS200-885=8、200-878=4、RTGEN206-101=1，部分自动pipeline II3。原 `site_request_synthesis_review_20261024_v1.json` SHA=852e68a6535bb61e0ae94267dede14c7a27b6d921b1fa9d7aa8dfa433dd6af90 的“无negative汇总即全部满足”布尔推断过强；新 `check_site_request_synthesis_v2.py` 要求明确positive，否则unknown。新版 `results/site_request_synthesis_review_20261024_v2.json` SHA=eb32ac1be3e0453b8b9f1a2ea84f40f0b7088b54b299417fb28204a12cf9f898，loop_constraints_summary=not_reported/满足状态null，原综合与警告未改变。后续不据v1的true宣称性能达标。
- 新 `resident_router_memory_plan_v2.py` / `check_resident_router_memory_plan_v2.py` 派生六组件候选 `hardware/vitis/resident_router_memory_v2`，增加encoder.state共享tree.demands/snapshot.initial，encoder.request共享site.request，仅新增result BO。58参数→42BO，632774656bytes（4KiB alignment），23 nominal HBM channels。独立 `results/resident_router_memory_audit_20261024_v2.json` SHA=31c727ea8f44c2bea427015d3697adcc1fe0d4c19675f515910c59fb18edcd52，status=`six_component_shared_buffer_capacity_independently_checked_platform_pending`；10种实际候选临时篡改拒绝，包括encoder两共享接口。仍是静态容量/连接，未XO ABI/v++ link/实际group交集或设备分配；count控制/外层scheduler/旧node与trace保存未实现。v1五组件计划保持冻结。
- 原tree全真实已终态成功，`results/route_tree_router_audit_20261024_v1.json` SHA=b5620d7465b7c7222308dbdb76d7c5eb483478a9297e8e6f6273017fea1f173b，status=`route_tree_two_full_router_conditions_independently_verified`，勿重跑。site-request唯一supervisor3480833已自动启动全真实pipeline **owner3551068**，CSR **3551514 CPU116** / compact **3551516 CPU117** 均核实live，completed=[]；自动最终raw+CC/SC/KC仍归原owner。
- 原snapshot RTL owner3082954/child3152131仍live在elaborate；原tree RTL2929797/3001030仍live在RTL。继续原owners，不以安静/耗时重启。新绑定TB/pipeline/contracts/checkers/plan/config冻结，修改用新版本。项目check通过。
- 本轮progress，完整目标active。下一步核验原长任务终态；导出已RTL通过组件XO并核对控制ABI，准备实际多组件连接及有界外层调度/retained route；补全部特殊资源和实板带宽功耗。不可把34合成事务或静态603MiB计划当作完整硬件实验完成。

## 最新：packed site需求直接生成ledger请求已接入，CPU差分通过（2026-10-24）

- 新 `hardware/vitis/search_site_request.hpp` / `search_site_request_top.cpp`：直接将node-zero 65word状态转为既有sorted [kind/id,mask,value] triples。逻辑上限56记录/168words（32/16/8不变）；request端口仍完整196608words供原site组件消费，尾部保留。零mask仍输出独立请求，UINT32_MAX资源ID合法；active状态/节点/保留字段全部预检后才写，失败count0且全request不变。top3指针/2AXI bundles，pragma在top函数体，无动态分配/STL。ABI见 `hardware/vitis/SEARCH_SITE_REQUEST_V1.md`。
- 新 `src/native/site_occupancy_request_adapter.hpp::replace_packed` 调实际新top后将raw request/count传原site helper replace；`site_request_routes_transform.py`只在新隔离副本替换最终site提交。65word tree demands不再先通过Normalized/entries来驱动ledger mutation；最终host unpack仍为观察输出保留，外层调度/旧node marshal/trace仍host。新增第六组件，**旧五组件memory plan未覆盖它**，未来须新版本连接encoder.state到tree demands、encoder.request到site request及处理count控制。
- `tests/test_search_site_request.cpp` 字面输入packing、原native site_native::entries oracle：2000随机状态/完整56记录/零mask/最高ID/未用state slots忽略/空状态、9非法及1小容量拒绝，完整196608request+guards和tails，ASAN/UBSAN通过；实际top严格C++14，native测试C++17。正式准备 `data/derived/site_request_router_20261024_v1` owner3425456/exec45843已正常结束：两种原production搜索核共400完整协商问题/4938搜索/3750快照/1250轮与native所有中间/最终语义相同，node-history2412/site-history2106/site-paths2896，routed210/incomplete190，无native邻接回退，完整router已编译。
- 独立 `results/site_request_component_20261024_v1.json` SHA=179c93d358f074b471d9645c7b58476e5a10933355b30984ea008cff454e7c49，status=`site_request_packed_commit_and_full_search_differential_independently_verified`；复核源变换、packed adapter、原oracle、所有输入/实际编译与运行receipts。绑定source/test/preparer/transform/checker冻结，修改须派生新版本。
- 新HLS唯一 `site_request_hls_pipeline.py` **owner3477534 / exec67701**，wrapper3477535已核实live，bundle/project=`site_request_hls_20261024_v1`。本机2022.2、xcu280/5ns/1.35ns。HLS test flat source的site_ledger仅用原冻结C++14 pairwise oracle替换，native sanitizer证据另存。当前csim_and_synthesis运行，未宣称Csim/综合完成，更无本组件RTL。原唯一只观察后继 `supervise_site_request_hls.py` **owner3480184 / exec21969**，终态自动 `check_site_request_synthesis.py`，预期 `results/site_request_synthesis_review_20261024_v1.json` status=`site_request_csim_and_synthesis_verified_rtl_pending`；不另起审核或重启。
- 全真实唯一后继 `supervise_site_request_real.py` **owner3480833 / exec93984**，state在新router bundle/real_supervisor/state.json，当前await_predecessor_full_audit；观察原tree owner2899588（已两workers完成、当前independent_full_audit且live），不重复前驱审核。前驱成功后自动新 `site_request_router_pipeline.py`，原两模式各两批1062网/cache4096/80轮/budget200000/presentcap8，最终 `check_site_request_router.py` 完整raw+CC/SC/KC比较，预期 `results/site_request_router_audit_20261024_v1.json` status=`site_request_two_full_router_conditions_independently_verified`。排队不等于全量已运行。
- 原snapshot owner3082954/child3152131仍live在elaborate；原tree RTL owner2929797/wrapper3001030仍live在RTL，继续原50事务及自动postcheck。未改原site/boundary/physical flows。项目check通过。
- 本轮progress，完整目标active。下一步确认新encoder HLS/原tree全真实终态；准备encoder完整深度RTL并将新组件加入实际设备连接；继续有界外层控制/route retention、全部特殊资源/物理时序与实板带宽功耗。不能把CPU转换/完整随机差分当成设备驻留或完整加速实验。

## 最新：五组件共享缓冲区静态连接/容量审核通过（2026-10-24）

- 新 `scripts/resident_router_memory_plan.py` 解析production search/node/site/snapshot/tree的实际top签名/pragma深度，复核CSR/compact原kernel XML ABI及四新组件原综合报告/source/bundle。新 `hardware/vitis/resident_router_memory_v1/` 给出DDR[0]与HBM候选config。55指针参数通过明确共享关系合并为41个物理BO，完整声明容量/4KiB对齐共632770560 bytes（603.46MiB），HBM候选占23通道；key260MiB跨HBM[5:6]，graph128MiB在HBM[0]。每pool16MiB reserve仅policy，不是实测free memory。
- 共享：tree roots→search roots/node new_nodes；snapshot packet→search；search result/path→tree accept；tree demands→snapshot initial；node五状态buffers/site三状态buffers→snapshot。自动传递合并每个AXI bundle的bank约束；同组件指针仍必须独立BO。node.old_nodes/site.request仍单独输入，外层协商/保留route/未来硬件scheduler不在本内存清单，不能称完整硬件路由实现。
- 独立 `scripts/check_resident_router_memory_plan.py` 重算唯一BO容量/对齐、共享一致性、bundle连接、pool不重叠/聚合容量以及config逐行内容。`results/resident_router_memory_audit_20261024_v1.json` SHA=2d9a7f85da2aee7590fe070d2ab0fe4dc77a4ecc6d1b24a5c2f4affd0faca947，status=`five_component_shared_buffer_capacity_independently_checked_platform_pending`。`tests/test_resident_router_memory_plan.py` 3组共享传递/过大key/非法别名/通道耗尽测试；`test_resident_router_memory_audit.py` 8类真实候选临时副本篡改拒绝，失败不发布报告。源码/plan/config/checker已绑定冻结，变更须新版本。
- 仍未export四组件XO控制/参数ABI、v++ link、实际平台MEM_TOPOLOGY/XRT group交集或41BO同时分配；新config是候选。真实BO共享需验证各producer/consumer的兼容memory group，不能比较数值group_id便宣称兼容。所有共享状态要求单owner且producer完成后才consumer访问。README列明这些设备验收步骤；不将603.46MiB计划容量解读为实测占用/带宽/功耗。
- 原snapshot RTL owner3082954/child3152131仍live，当前elaborate；日志正在编译load模块。原tree RTL owner2929797→wrapper3001030→leaf3001920仍live，1/50大路径事务。新全真实tree owner2899588 completed=[0]，另一worker仍运行，继续其原自动raw审核，不重复提交/审核。
- 原物理MCP最新仍source执行，CSR4146646中间WNS=-1.460、compact4159154报告拥塞，queue0，不能宣称最终时序通过。继续原owners；终态先保存MCPstatus再其他Tcl。未操作B会话。
- 本轮progress，完整目标active；项目check通过。下一步接收snapshot/tree RTL与全真实终态；准备新组件export/XRT共享BO的实际验证及外层调度/保留结果硬件化，同时补完整特殊资源和实板实验。静态连接不是平台链接/设备执行证据。

## 最新：驻留快照30事务完整深度RTL准备通过，路由树已实际RTL（2026-10-24）

- 新 `hardware/vitis/test_resident_snapshot_rtl.cpp` 从冻结的native packet/ledger测试派生，仅实例化生产Fixture。13指针每次保持全部声明深度+guard，包括patch/拒绝事务；逐字检查packet全逻辑区及stale tails、全部ledger/metadata/input/guard不变。最大static metadata（1m reserved/protected PIPs、65536 attrs/fixed、256满需求semantics）、实际65536 site owners/history、3850849word包、少一字容量拒绝、最大query patch、非法控制/metadata及恢复共30事务。后3事务通过实际node update/advance创建3个owner pairs和node history，比较不同net自网排除/保留终端；没有声称填满2m node hash pairs。
- CPU严格C++17 ASAN/UBSAN使用原native site_ledger/serializer；HLS C++14使用已冻结pairwise oracle，两份flat源分别保存为cpu_source/source，均与原frozen来源核对。共享既有packed-state ABI helper，不能称完全独立字面packing。新 `resident_snapshot_rtl_contract.py` 为独立字面30行结果；`test_resident_snapshot_rtl_contract.py` 行缺失/字段篡改/性能序列负例通过。`test_resident_snapshot_rtl_setup.py` BE binary及text帧正反测试通过。开发时parser派生误改binary EOF被负例拒绝，已恢复本机生成器标记5a5aa5a50f0ff0f0；实际wrapper确认pointer名control/initial_r后才审核正式激励。
- 唯一 `scripts/resident_snapshot_rtl_pipeline.py` **owner3082954 / exec25322**，bundle/project=`resident_snapshot_rtl_20261024_v1`。保留原snapshot全部syn字节，仅换TB；CPU、HLS Csim和cosim -setup均通过。当前 **elaborate，child3152131已核实live**，未声称本组件RTL完成。CPU120、64MiB栈，run10sec是仿真时间上限。原owner后继RTL→30行performance→原HLS C postcheck→`check_resident_snapshot_rtl.py`，预期 `results/resident_snapshot_rtl_audit_20261024_v1.json` status=`production_resident_snapshot_full_depth_30_transactions_rtl_verified`。不重复提交或竞争postcheck/audit。
- 独立准备 `results/resident_snapshot_rtl_setup_20261024_v1.json` SHA=07c3a2563c4cb4ae63e12dc2ad15eca5531ebafdc4db7413738cf43192f222a2，status=`production_resident_snapshot_full_capacity_30_transaction_setup_independently_verified_rtl_pending`，676绑定及12个实际AXI向量逐事务全深度/字宽/长度/EOF/摘要检查通过。packed深度：control81×64、static4194304×64、meta10×64、count1048576×32、node-history1048576×64、node-table3145728×64、site-table131072×256、site-history131072×128、packet524288×512、result1×512；仅packet/result有out向量。见 `hardware/vitis/RESIDENT_SNAPSHOT_RTL_V1.md`。绑定source/TB/pipeline/contract/checkers冻结，变更须新版本。
- **路由树已进入实际RTL**：原owner2929797/exec82141，wrapper3001030→实际xsimk **3001920**，已从/proc所有线程children核实live身份，最新1/50，正在最大路径事务。启动证据 `results/route_tree_rtl_submission_20261024_v1.json` SHA=2b2e8e88979199232b857e86423fdd2a9061ce23f75176689dde1ee7a9adf2e0，status=`production_route_tree_full_capacity_50_transaction_rtl_started_not_yet_verified`。不把长路径耗时视为失败或重启理由。
- 新tree全真实owner2899588、CSR2900910/compact2900915仍live（CPU活跃），completed=[]。继续原自动完整raw审核。site RTL、boundary RTL及物理流程仍由原owners负责，未更动。项目check通过。
- 本轮progress，完整目标active。下一步确认snapshot实际RTL进入并收取两新组件/全真实原owner终态，继续有界外层调度/保留结果及多组件memory/XRT连接、特殊资源与真实实板实验。CPU/Csim/AXI模型不构成完整真实路由RTL吞吐/DDR/HBM/功耗证据。

## 最新：路由树50事务完整深度RTL已准备，原综合及前驱全真实均通过（2026-10-24）

- 新 `hardware/vitis/test_route_tree_rtl.cpp` 不含DUT helper/header，独立规范节点set与字面65-word ABI oracle。9指针每次保持生产声明深度+guard：meta5、bits16384、demands65、search81、path4194304、sinks/roots1048576、config8、result6。50事务逐字检查整个meta/bitset/demands/roots（含inactive tails）、全部const输入及guards。实际524288边首路径+524287边次路径填满1048576节点，32/16/8满需求、完整roots/sinks；覆盖6种失败搜索不变、非法/断裂/非树起点/目标/方向路径、需求删除/冲突、空路径、超容量、保留字段/u32宽度、version饱和拒绝与恢复/reset。饱和version由TB显式注入，非自然运行到上限。
- 严格C++14 ASAN/UBSAN、实际HLS2022.2 Csim和cosim -setup通过。开发首次编译发现同声明auto类型不同及misleading-indentation，修正TB后重新编译/运行通过；未改DUT或降低警告要求。`scripts/route_tree_rtl_contract.py` 独立字面50行序列、`tests/test_route_tree_rtl_contract.py` 450行缺失/字段篡改及性能序列负例通过；`tests/test_route_tree_rtl_setup.py` 文本/BE二进制深度格式正反检查通过。合成parser fixture不是RTL证据。
- 唯一 `scripts/route_tree_rtl_pipeline.py` **owner2929797 / exec82141**；bundle=`data/derived/route_tree_rtl_20261024_v1`，project=`build/route_tree_rtl_20261024_v1`。复制已审阅原tree综合工程，原syn所有字节相同；仅换TB并重生Csim/激励。当前 **elaborate，child2954318已核实live**，尚未声称进入或通过RTL。请求CPU118、64MiB栈、run10sec为仿真时间而非墙钟超时。不得因日志安静重启。
- 独立准备报告 `results/route_tree_rtl_setup_20261024_v1.json` SHA=f6ad6b92e4948c808303043a834efbfd6e7e5c468b65934460a3f2444c52f573，status=`production_route_tree_full_capacity_50_transaction_setup_independently_verified_rtl_pending`，589项绑定，10个实际AXI in/out vector逐事务完整深度检查通过。packed depths: input_mem524377×64、meta_mem1×512、tree_mem16384×64、state_mem65×64、path_mem524288×256、output_mem65537×512；input/path只读，无out向量。checker `check_route_tree_rtl_setup.py` 检查实际ref.tcl、字长、50个深度帧、总长度/EOF及摘要。所有绑定源码/TB/runner/contract/checker冻结；变更须新版本。
- 原owner自动后继：xelab→实际RTL50事务→原HLS生成C postcheck逐字回检→`check_route_tree_rtl.py`。预期 `results/route_tree_rtl_audit_20261024_v1.json` status=`production_route_tree_full_depth_50_transactions_rtl_verified`，最终绑定不可变audit_owner_state快照。不要另起postcheck/最终审核。
- **tree综合已完成并由原supervisor审核**：`results/route_tree_synthesis_review_20261024_v1.json` SHA=73ae18b126b38f5c13e3159c13afac24fb57153dc03e3ff114cf16d6d44241a6，status=`route_tree_csim_and_synthesis_verified_rtl_pending`。LUT111485/FF58943/DSP0/BRAM0/URAM0、估计3.65ns、循环约束NOT satisfied。不能当作物理时序/吞吐达标。
- **resident snapshot原全真实已独立通过**：`results/resident_snapshot_router_audit_20261024_v1.json` SHA=191b4c98e21e990e3127d51090f0dbe5dd9283e23e1dbf223f3c95008b0b7efd，status=`resident_snapshot_two_full_router_conditions_independently_verified`。原owner2259234终态，不重跑。新tree supervisor2834989已自动启动全真实pipeline **owner2899588**，workers **2900910 CSR CPU116 / 2900915 compact CPU117** 均已核实live；state completed=[]，原两模式各两批1062网，自动全raw/CC/SC/KC审核仍归原owner，勿重复。
- 本轮progress；完整目标active。下一步确认原tree RTL进入/终态，接收新全真实审核；准备resident snapshot生产深度RTL、推进外层协商与结果保留硬件化、多组件共享bank/XRT连接及剩余特殊资源/实板带宽功耗。完整硬件实验尚未实现，不能用本50合成事务替代完整真实路由RTL流量。

## 最新：有界路由树已接入完整搜索，差分通过，HLS运行/全真实待前驱审核（2026-10-24）

- 新 `src/native/route_tree_adapter.hpp`、`scripts/route_tree_routes_transform.py`、`prepare_route_tree_router.py`，隔离副本 `data/derived/route_tree_router_20261024_v1`。当前网reset/roots/需求累积/sink完成均调用实际tree top；原search raw result81/path直接传入accept，65-word demands直接传入snapshot query patch，不经host normalize/repack。每网结束才导出nodes与demands供保留结果和占用桥接。外层协商、target排序、trace保存、最终占用marshal仍host；非全硬件。详见 `hardware/vitis/ROUTE_TREE_INTEGRATION_V1.md`。
- 准备owner2767434/exec20969已正常终态。实际新top严格C++14、组件ASAN/UBSAN通过；完整两种production搜索核共400协商问题/4938搜索/3750快照/1250轮，与原native完整路径/成本/需求/unknown/最终状态/各轮node-site冲突相同；node-history2412/site-history2106/site-paths2896，routed210/incomplete190，无native邻接回退。正式完整router已编译。
- 独立 `results/route_tree_component_20261024_v1.json` SHA=26156d4e8f6aa7877ad5bb7c4d66fc5c5fb26bcc26080e24b9be180891bb9d0b，status=`route_tree_raw_state_and_full_search_differential_independently_verified`。绑定原输入/实际源/变换/原oracle/编译与运行receipts，重算集成副本变换。所有绑定source/test/scripts冻结，变更须新版本。
- HLS唯一 `route_tree_hls_pipeline.py` **owner2823693 / exec20945**，wrapper2823901，bundle/project=`route_tree_hls_20261024_v1`；沿用Ross scope/run-flow与本机2022.2 Tcl，xcu280/5ns/1.35ns。实际Csim通过同一C++14组件oracle，当前综合运行。没有本组件RTL证据。唯一后继 `supervise_route_tree_hls.py` **owner2826269 / exec46754**，检查原owner身份，终态自动 `check_route_tree_synthesis.py`，预期 `results/route_tree_synthesis_review_20261024_v1.json` status=`route_tree_csim_and_synthesis_verified_rtl_pending`。不要竞争审核或重启。
- 原resident snapshot full CPU两worker已结束，原owner2259234进入 `independent_full_audit`，仍live。新真实实验唯一后继 `supervise_route_tree_real.py` **owner2834989 / exec52613**，state在新router bundle/real_supervisor/state.json，当前 `await_predecessor_full_audit`。仅观察原owner身份，不重复前驱审核。前驱完整审核成功后自动调用 `route_tree_router_pipeline.py`，保持两模式各两批1062网/cache4096/80轮/budget200000/presentcap8，自动完整raw+CC/SC/KC比较。预期 `results/route_tree_router_audit_20261024_v1.json` status=`route_tree_two_full_router_conditions_independently_verified`。此刻排队不等于全量实验已运行。
- 阶段 `results/route_tree_integration_stage_20261024_v1.json` SHA=9bb087572c4d300a3613cce35f97b634a08106fa6156a696d68b3e196b80e84b，重核187项绑定、Csim标记和三原owner真实/proc身份；状态为CPU集成通过/Csim通过/综合运行/全真实排队，不声称硬件完成。
- 原node RTL审计239文件摘要重核通过，报告SHA=ce2bd29d40d81de2b75c8a6d66ff29f4db35cbba2c96bcdbacc7e80a48b98de0；原resident snapshot综合审阅95文件摘要重核通过，SHA=e4cc3a44bd8d665641d34d759fb4c453ab8b6bddd1f15a0fc76fa4de0799b55d，LUT203202/FF138345/DSP8/BRAM0/URAM0、3.65ns估计，循环约束NOT satisfied，不是物理时序通过。
- 原site RTL leaf1787486、boundary两leaf1820784/1830120、heap HLS2468371仍live。物理MCP两会话原source仍运行、queue0；CSR中间WNS=-0.983，compact报告拥塞，不是最终验收。继续原owners；终态先保存MCPstatus再其他Tcl，不操作B会话。
- 本轮progress，完整目标active。下一步核验上述唯一owners终态，给tree及resident snapshot准备生产完整深度RTL测试；继续外层调度/保留结果硬件化、多组件bank/XRT及全特殊资源/实板吞吐功耗。不要用CPU差分或Csim缩小完整实验要求。

## 最新：路由树组件生产容量 CPU 验证通过（2026-10-24）

- 新 `hardware/vitis/search_route_tree.hpp` / `search_route_tree_top.cpp` 管理当前网的规范节点 bitset、65-word站点需求与版本；支持reset、接受搜索结果、升序roots和sink完成检查。生产容量1048576节点/524288边，不改变原搜索核。全预检后提交；失败搜索不改变状态；不连续路径/不保留旧需求/非法字段被拒绝。物理边合法性及完整站点语义仍由搜索核负责，保留路径和外层协商尚在host。
- `tests/test_search_route_tree.cpp` 独立std::set/字面ABI oracle：1000随机接入、1000失败搜索不变、21原子拒绝，实际生产top用两条路径填满1048576节点，首条524288边，32/16/8满需求，完整roots/sinks/输入与guard及reset尾部检查。严格C++14与ASAN/UBSAN通过。复现入口 `scripts/check_route_tree_cpu.py`（要求新build/report路径）。ABI见 `hardware/vitis/SEARCH_ROUTE_TREE_V1.md`。
- CPU组件报告 `results/route_tree_cpu_20261024_v1.json` SHA=bae3806b59249c4441871e8e11d99eb47347a70cd4022a1302718553f35978c0，status=`route_tree_production_top_cpu_oracle_and_sanitizers_passed`，绑定传递headers/source/test/runner及编译/运行log。不是独立RTL审计；当前**未接入完整路由副本，未执行本组件HLS/RTL**。本报告绑定文件冻结，需改动时派生新版本。
- 原node占用RTL owner已终态：`results/node_occupancy_rtl_audit_20261024_v3.json` status=`production_node_occupancy_full_depth_28_transactions_rtl_verified`。原resident snapshot HLS及其唯一supervisor已终态：`results/resident_snapshot_synthesis_review_20261024_v1.json` status=`resident_snapshot_csim_and_synthesis_verified_rtl_pending`。不重复启动。
- 下一步：新派生完整路由副本，用本top替代当前网host集合/累积需求，直接消费原search result/path，并把roots与65-word需求传入snapshot query patch；保留trace输出，比较全部中间结果和原完整CPU工作负载。然后本组件HLS/完整深度RTL、多组件共享bank/XRT连接；全部特殊资源和实板仍未完成。既有site/boundary RTL、真实CPU、物理流程继续由原owners负责。本轮progress，完整目标active。

## 最新：驻留node/site状态直接构造搜索packet已接入，CPU/Csim通过（2026-10-24）

- 新 `hardware/vitis/search_resident_snapshot.hpp` / `search_resident_snapshot_top.cpp`：读取原node/site有界ledger，直接构造原搜索packet v1及每次query patch，生产容量不变（nodes1048576、node slots2097152、site owner/history65536、packet4194304 words）。固定metadata一次编码为16字头+protected bitset/reserved node-net/packed flags/protected PIPs/semantic keys+65word requirements/fixed records；build在全部预检后写packet，失败保持整个packet和全部ledger不变；patch只改target/nroots/budget/initial，packet其余体为之前build生成的可信状态。top13指针/10AXI bundles，均为有界C++14，无STL/动态分配/外部成员指针。沿用Ross scope/synthesizable/run-flow及本机2022.2 Tcl。
- 新 `src/native/resident_snapshot_adapter.hpp` 通过实际新top构造packet/patch；`node_occupancy_snapshot_adapter.hpp`、`site_occupancy_snapshot_adapter.hpp`仅为原host ledger添加const buffer view，原mutation逻辑不变。`resident_snapshot_routes_transform.py`派生独立完整路由副本，移除逐网host forbidden集合/快照向量/原vector serializer构造；完整搜索top未改。新CPU保持4194304物理packet words，另记逻辑长度。外层协商、route保存及一次性static metadata编码仍host，不能说已全硬件。
- 测试 `tests/test_search_resident_snapshot.cpp`：1000小容量helper随机构包+1000patch，与原序列化器和独立native owner/history逐字一致；39拒绝事务及全packet/ledger保持、未用state slots规范化通过。实际生产top同时填满全部metadata计数、1048576 node/reserved/protected PIPs、65536 owner/history/fixed、256 semantics、65536 attrs，输出**3850849** words，静态image2408976 words；检查全字/tails，少一字容量拒绝及最大query patch。ASAN/UBSAN与严格C++14 top编译通过。
- 开发失败保留：直接混用root与offsets-v3的pragma-once headers曾重复定义类型，正式编译统一使用单一flat冻结include tree；初始最大packet字面数误写3950849，虽然逐字oracle已相等，最后literal断言正确拒绝。独立重算为3850849后修正测试，旧开发失败log保留在 `build/resident_snapshot_development_20261024_v1/cpu.log`；不算通过证据。
- 准备 `data/derived/resident_snapshot_router_20261024_v1` owner2189504/exec37985已退出0。实际新builder top与原两种production search C top完成400完整随机协商问题、4938 searches、3750 snapshots、1250 rounds；全部中间路径/成本/需求/unknown/轮冲突相等，node-history2412/site-history2106/site-paths2896，routed210/incomplete190，无native邻接回退。独立 `results/resident_snapshot_component_20261024_v1.json` SHA=b48b6747443fc133012ae7e2120f4787a13bf04ad7a2afcc8bbe3f8f1a19cd65，status=`resident_snapshot_native_packet_and_full_search_differential_independently_verified`。
- 新全真实唯一 `resident_snapshot_router_pipeline.py` **owner2259234 / exec55706**，CSR worker**2259241** CPU116、compact **2259242** CPU117已核实live；两个模式各两批1062网，原cache4096/80轮/budget200000/present_cap8不变。原owner自动完整raw字段及CC/SC/KC核验，预期 `results/resident_snapshot_router_audit_20261024_v1.json` status=`resident_snapshot_two_full_router_conditions_independently_verified`。不要重跑或竞争启动审计。
- 新HLS `resident_snapshot_hls_pipeline.py` **owner2259361 / exec49709**，wrapper2259609→loader2259645→实际backend**2259728**已核实live。bundle/project=`resident_snapshot_hls_20261024_v1`。实际Csim已通过上述1000/1000/39与最大容量检查；HLS TB仅将flat source的site_ledger.hpp替换为已绑定C++14 pairwise test oracle，原native测试证据另保留。当前csynth在RTL generation的load模块运行，不能称综合完成或失败，勿重启。
- 为长HLS增加唯一只观察后继 `scripts/supervise_resident_snapshot_hls.py` **owner2400530 / exec64159**。状态在HLS bundle/audit_supervisor/state.json；核对原owner的PID/start_ticks/argv，等原终态后自动调用冻结的 `check_resident_snapshot_synthesis.py`，预期 `results/resident_snapshot_synthesis_review_20261024_v1.json`、status=`resident_snapshot_csim_and_synthesis_verified_rtl_pending`。此后继不启动/重启HLS；失败保留。不要手动重复审阅。
- 阶段 `results/resident_snapshot_stage_20261024_v1.json` SHA=b4d6273926837af9af6baa618b6d5c290f6cffafc40181f7073a8935afba30bc，status=`resident_snapshot_cpu_verified_csim_passed_synthesis_and_full_real_workloads_running`，重核238输入/产物、稳定Csim报告和实际进程身份。ABI/边界见 `hardware/vitis/SEARCH_RESIDENT_SNAPSHOT_V1.md`。已绑定新source/test/scripts冻结，修改派生新版本。旧search-only XRT memory plan尚不含新component，未来连接须新版本验证共享bank。
- **上一版site全真实CPU已终态通过，勿重跑**：`results/site_occupancy_router_audit_20261024_v1.json` SHA=38a6b114b0ebf9d56697ed430427ab772d4b0a607f4053775854e99399e724ca，status=`bounded_site_occupancy_two_full_router_conditions_independently_verified`，原owner1531489结束。原site RTL leaf1787486仍live（30/52，正在满65536 owner/request阶段）；node RTL leaf1137004仍live（已24/28）；完整search boundary两leaf1820784/1830120仍live。原物理MCP4146646/4159154仍source运行，stage placement，compact日志已到phys_opt_design；继续原唯一owners，不重复source。终态先保存MCPstatus再其他Tcl，未宣称物理通过。
- 本轮progress，完整目标active。下一步核验原owners终态；新组件完成独立综合后准备完整深度RTL验证；继续外层协商/route retention硬件化和多组件/XRT连接，补全部特殊资源及真实板卡实验。不能用CPU/Csim或AXI模型替代全硬件路由、物理时序、DDR/HBM/功耗结论。

## 最新：站点占用完整容量52事务RTL已实际运行（2026-10-24）

- 新 `hardware/vitis/test_site_occupancy_rtl.cpp` 不包含DUT helper，使用独立有序map及pairwise冲突oracle。10个top指针每次保持完整声明深度+guard，逐事务比较两bank全部owner/history、meta、scratch、snapshot及所有stale tails；const请求/config和result guard也核对。52事务覆盖signal/64位mask/categorical、兼容第三owner排除、替换/释放/自网排除、无效kind/mask/value/顺序/重复/count/net/reserved/opcode、迟发history overflow/version saturation、恢复/reset。实际65536请求填满65536 owner；两个32768冲突资源轮实际累积65536 history，并测试真实容量拒绝及全部输出深度。饱和历史/version仍明确由TB注入。
- ASAN/UBSAN CPU、实际2022.2 HLS Csim和cosim -setup均通过。独立字面52行contract `scripts/site_occupancy_rtl_contract.py` 核对op/status/owner/history/version/groups/snapshot，4组parser测试通过（15种golden损坏、5种performance损坏、8种文本深度损坏、6种binary深度损坏）；performance小fixture仅测解析，不是RTL证据。
- 唯一owner **`scripts/site_occupancy_rtl_pipeline.py` PID1722158 / exec6858**；bundle=`data/derived/site_occupancy_rtl_20261024_v1`，project=`build/site_occupancy_rtl_20261024_v1`。复制已独立审阅的site HLS工程，保留全部原综合RTL字节，仅替换TB并重新生成Csim/激励；xelab已通过，实际RTL wrapper1786428→xsim1786462→**leaf1787486**已核实live/CPU活跃。请求CPU119，XSim leaf实际affinity[23,55,87,119]；64MiB栈，`run 10 sec`是仿真时间上限，不是墙钟超时。最新30/52，接下来是实际满65536 owner/request事务，长时间运行不能据此判失败或重启。
- 独立准备报告 `results/site_occupancy_rtl_setup_20261024_v1.json` SHA=fe7d879d90d3fdc898cc03b601c0e8722a7aab5f6b1c994784afa0e03f1edb9f，status=`production_site_occupancy_full_capacity_52_transaction_setup_independently_verified_rtl_pending`。绑定225输入/原及复制syn/真实激励和receipts；逐事务验证11个完整AXI in/out vector文件的深度、总长度、EOF及摘要（9个binary、2个text）。packed depths: input196616×64、meta1×512、owner131072×256、history131072×128、scratch81920×128、output49153×512；全部52次不缩小。
- 初版 `check_site_occupancy_rtl_setup.py` 错将所有大数组激励当文本，正确拒绝并未发布报告；失败记录 `setup_audit_attempt_001.json` 保留。依据本机生成wrapc Output::begin/from及AESL binary reader，新增 `check_site_occupancy_rtl_setup_v2.py` 支持BE uint64 depth+固定宽字+EOF 5a5aa5a50f0ff0f0。未修改激励/RTL；新版经正反测试及全部实际vector核验后才发布准备报告。
- 启动证据 `results/site_occupancy_rtl_submission_20261024_v1.json` SHA=909c89e667f497e7f57bdc15a8da77a052341fa78690161adf9bacfc37432598，status=`production_site_occupancy_full_capacity_52_transaction_rtl_started_not_yet_verified`；重核225项并通过所有线程children发现真实xsimk，记录完整父子链和affinity。**没有site RTL通过结论**。源/TB/contract/runner/checker/测试fixture已绑定冻结，修改须派生新版本。
- 后继完全由原owner执行：RTL返回→performance52行→原生成C postcheck→`check_site_occupancy_rtl.py`；预期 `results/site_occupancy_rtl_audit_20261024_v1.json`，status=`production_site_occupancy_full_depth_52_transactions_rtl_verified`。最终checker绑定不可变audit_owner_state.json，禁止另起postcheck/auditor或重跑。
- 新site完整真实CPU owner1531489/exec82322及workers1532010/1532012仍live，completed=[]，最终raw全语义/计数比较仍归原pipeline。原node占用RTL leaf1137004仍live。原完整搜索boundary owner1530495已经完成xelab并实际进入两路XSim：leaf1820784/1830120 live，最终独立验收归原supervisor3099710；不要另提。旧heap HLS owner2468333/leaf2468371仍live。
- 原完整搜索物理MCP最新仍source运行；两个state均已进入placement（CSR4146646、compact4159154），不可当作布线或时序通过。终态时先获取并保存MCPstatus再执行任何Tcl，按原物理checker验收。B方向会话不操作。
- 本轮为progress，完整目标active。下一步核验现有唯一owners终态；继续连接有界node/site ledger与完整硬件调度/packet构造，处理完整特殊资源语义和实板缺口。HLS AXI事务不是实卡驻留、实际全网路由RTL吞吐/DDR/HBM/功耗证据。

## 最新：站点占用/历史组件 CPU 集成与 HLS 综合完成，真实全量实验运行（2026-10-24）

- 新 `hardware/vitis/search_site_occupancy.hpp` / `search_site_occupancy_top.cpp`、`src/native/site_occupancy_adapter.hpp`：生产 owner/history/request 各65536；按(kind, physical_id, net)排序的外部双bank数组，保留信号、64位mask配置、分类值语义；兼容或不相交bit owner不计冲突参与者。replace和history merge全预检后提交，容量/溢出失败保持两bank及meta不变；scratch可变。snapshot排除自身网并直接生成原搜索packet rows。bridge不再维护另一份活跃owner/history map。接口/内存/失败语义见 `hardware/vitis/SEARCH_SITE_OCCUPANCY_V1.md`。原搜索top和旧副本未改。
- `tests/test_search_site_occupancy.cpp` 用原native pairwise oracle完成12000随机操作：6173成功replace、4117容量拒绝、1710历史轮；独立逐字段检查全部owner/history/conflict sets/snapshot/tails，兼容第三owner、零mask、最高ID、迟发history overflow、version饱和、释放后history保留，生产65536 owner/request/history上限均通过ASAN/UBSAN。400完整随机协商问题/4938搜索/3750 snapshots/1250 rounds与原完整路由oracle一致；node-history2412、site-history2106、site-paths2896，routed210/incomplete190，禁止native邻接回退。生产top严格C++14，原native测试C++17。
- 准备bundle `data/derived/site_occupancy_router_20261024_v1`，`prepare_site_occupancy_router.py` owner1466345/exec73582已退出0。独立 `results/site_occupancy_component_20261024_v1.json` SHA=c9c7bebbd4d113b5747689c4f4695fa001ef2845710a1264e1bc7c5c3e3d22e9，status=`bounded_site_occupancy_native_component_and_full_search_differential_independently_verified`。代码/输入/原oracle/实际receipts均绑定；已绑定的新代码、测试和脚本冻结，修改用新版本。
- 新全真实唯一owner `site_occupancy_router_pipeline.py` **1531489 / exec82322**，CSR **1532010** CPU116、compact **1532012** CPU117已核实live，两个模式各两批1062网，cache4096/80轮/budget200000/present_cap8原参数不变。尚未完成。原owner结束后自动 `check_site_occupancy_router.py` 比较全部raw语义字段及CC/SC/KC计数，预期 `results/site_occupancy_router_audit_20261024_v1.json` status=`bounded_site_occupancy_two_full_router_conditions_independently_verified`。不要竞争启动审计或重跑。
- 新HLS owner1532082/exec11528已退出0，bundle=`site_occupancy_hls_20261024_v1`，project=`build/site_occupancy_hls_20261024_v1`；实际2022.2、xcu280、5ns/1.35ns，Csim+csynth完成。沿用Ross pragma-scope/synthesizable/run-flow，采用本机Tcl。HLS TB仅把原测试的native oracle include换成独立C++14 pairwise oracle，规避旧编译器C++17；两套oracle测试均通过。**未执行本组件RTL**。
- 独立综合报告 `results/site_occupancy_synthesis_review_20261024_v1.json` SHA=a796e82da0cb583feebc54194dde95be1152b10e09bf3b3f67d0532233992a30，status=`bounded_site_occupancy_csim_and_synthesis_verified_rtl_pending`：估计3.650ns，LUT163270/FF67405/DSP0/BRAM0/URAM0。II73/215/147等，replace merge无法pipeline；All loop constraints were NOT satisfied，整体latency为undef。SYNCHK200-23=1、HLS200-960=2、200-878=19、200-880=16、200-885=1、RTGEN206-101=25。这不是性能或物理时序结论。
- 阶段 `results/site_occupancy_stage_20261024_v1.json` SHA=ba269653278ab3706e2f2b643d27a670d13cda1f97971aa08bc186df9d40175f，status=`bounded_site_occupancy_cpu_and_synthesis_verified_full_real_workloads_running`，重核204输入/产物并记录真实worker状态。外层调度、结果保存和packet构建仍host；完整特殊资源语义/实际板卡仍缺。
- **旧节点占用真实实验已终态成功，勿重跑**：`results/node_occupancy_router_audit_20261024_v1.json` SHA=b7792b5f7b08312f4d1c5df3502cece2a4e087faa7e738dea01179a4ef20c9a7，status=`bounded_node_occupancy_two_full_router_conditions_independently_verified`。旧node RTL owner1065904、leaf1137004仍live，继续由其原v3自动postcheck/audit。
- **原完整搜索RTL重放两模式已完成并独立通过**：`results/search_kernel_xsim_replay_audit_20261024_v1.json` SHA=19a1f4f267bd358acc9fc870237535c03e08d26542dccadd42974934d9ce65a3，status=`unchanged_search_kernel_rtl_replay_and_original_postcheck_verified`；CSR周期[2132461,12383]，compact[2135716,14021]，各仅2个合成事务，原失败v3仍保留failed。原supervisor3099710自动进入boundary_rtl，子owner1530495，`search_kernel_boundary_rtl_20261024_v1/state.json`，最新xelab仍执行，勿另启动。原物理MCP两会话4146646/4159154最新均live/source运行，未终态，仍须终态时先保存MCPstatus再任何Tcl操作。
- 下一步：核验上述原owner终态；给site组件准备独立完整深度RTL TB/冻结验证副本，覆盖两bank跨事务状态和失败不变，不缩小综合容量；连接两个有界ledger到完整硬件外层控制，继续原搜索物理与实板实验。本轮为progress，完整目标active。

## 最新：占用组件完整深度28事务RTL已实际启动（2026-10-24）

- 新 `hardware/vitis/test_node_occupancy_rtl.cpp` 对10个top指针始终按生产深度分配（另有guard），不再用会resize/为空的CPU测试向量直接做cosim。独立std::set规范节点/网oracle逐事务比较所有counts/history/meta、所有活跃hash entries、整个snapshot输出及尾部；拒绝事务比较全部持久buffer（包括闲置槽/输出）不变。第一阶段1048576活动节点，检查最高node/net ID；后续64活动节点但综合容量1048576节点/2097152槽和接口深度不变。硬编码独立发现的哈希碰撞net820与3227、node3、slot625610，覆盖tombstone后查找、自网排除、幂等插入、缺失owner、重复ID/超容量/保留字段拒绝、恢复/reset。合法饱和history/version由TB注入；不声称通过海量历史轮自然生成。
- 28事务ASAN/UBSAN、实际HLS Csim和C激励生成均通过。`node_occupancy_rtl_contract.py`以字面status/node_count/pair_count/version矩阵核对全部28行，parser测试2组通过（10种golden篡改、4种性能序列缺失/错误拒绝）；合成性能输入只测解析，不是硬件证据。
- 保留两次失败：v1 bundle/project `node_occupancy_rtl_20261024_v1` owner998710/exec69295在CPU预检失败，原因LD_PRELOAD libudev抢先加载导致ASAN拒绝；没有进入HLS/RTL。v2 owner1041314/exec16122 CPU预检通过，但本机2022.2 `open_project`拒绝绝对路径，在打开工程前退出。未修改原综合RTL。v3用CPU独立环境、AMD阶段才preload libudev，并采用本机已用过的cd-parent/open-project-basename；没有绕过ASAN检查。
- 当前唯一 `scripts/node_occupancy_rtl_pipeline_v3.py` owner**1065904** / exec**7286**，bundle=`data/derived/node_occupancy_rtl_20261024_v3`，project=`build/node_occupancy_rtl_20261024_v3`。已实际完成Csim/cosim -setup、校验原syn字节一致、xelab，并进入RTL；wrapper1134640→loader1134669→xsim1134739→实际xsimk leaf**1137004**已核实live/CPU活跃。命令请求CPU118、64MiB栈；XSim自身把leaf affinity扩为[22,54,86,118]，已在提交证据记录。Tcl界限run2sec（2e9ns），不是墙钟超时；未完成不能重启。
- 独立准备报告 `results/node_occupancy_rtl_setup_20261024_v3.json` SHA=`1cac020ba73355332a51f045050f2078f4492cc27ed3b86f348e9d3243355c9c`，status=`production_node_occupancy_full_depth_28_transaction_setup_independently_verified_rtl_pending`，核对230项输入/原及复制syn/实际RTL/激励/编译与CPU/HLS准备receipts，包含前两次失败证据。全部源码/脚本/测试/输入已绑定，后续修改用新版本。
- 实际RTL启动证据 `results/node_occupancy_rtl_submission_20261024_v3.json` SHA=`66917fbbd29a69edd930392089327d93bda65b052a27c9ff992ab6c549507cca`，status=`production_node_occupancy_full_depth_28_transaction_rtl_started_not_yet_verified`。初次只查wrapper主线程children未发现xsimk，未写出启动报告；随后遍历所有task children确认真实leaf及完整父子链才发布。最新进度0/28@128000ps，不能据此判死或重启。
- **后继完全由原v3 owner负责**：RTL返回→核对实际performance28行→原HLS C postcheck完整状态检查→`check_node_occupancy_rtl_v2.py`独立审计，输出 `results/node_occupancy_rtl_audit_20261024_v3.json`，期望status=`production_node_occupancy_full_depth_28_transactions_rtl_verified`。不要另行竞争启动postcheck/auditor。v2 checker绑定不可变`audit_owner_state.json`快照，避免parent最后更新state.json使审计摘要失效；这点在v3中已落实。
- 仍仅准备/CPU验证及RTL启动，**没有占用组件RTL成功结论**。HLS AXI模型的事务序列不是XRT真实驻留设备执行，不证明完整真实路由RTL流量/满表性能/物理时序/DDR/HBM/功耗。
- 新占用CPU全真实实验owner694011/exec6336仍live，state.completed=[0]：CSR worker694611已正常结束两批，compact worker694612仍live（已完成首批并执行第二批），最终完整raw审计仍由其原pipeline等待两边结束后运行；此刻不能称两模式全量验证已通过。原完整搜索核XSim2764812/2764813及物理Vivado4146646/4159154仍live，MCP最新仍source运行，勿重提。项目check通过。
- 上一轮progress，本轮完整深度TB、环境/本机命令修复、Csim/setup独立证据及真实RTL启动为progress。完整目标active。下一步优先核验上述两个唯一owner终态；然后推进占用结果与搜索核连接及剩余站点ledger/外层控制，继续完整搜索核物理验收和实板实验。

## 最新：规范节点占用/历史更新已接入完整搜索副本并完成综合（2026-10-24）

- 新 `hardware/vitis/search_node_occupancy.hpp` 和 `search_node_occupancy_top.cpp`：有界、外部字寻址的(node,net) hash set，1048576规范节点、2097152所有者对槽；flags区分empty/live/tombstone，不以key0或UINT32_MAX当哨兵。节点计数按不同net计，独立history按每轮owner_count-1累计。update先完整检查再释放/占用；缺失owner、非法/重复/乱序节点、容量及overflow失败保持持久状态。snapshot直接生成旧搜索包的[other_owner_count,history]。缓冲区必须互不重叠、由唯一调用者管理；内部table是reset/操作生成的可信状态，未声称校验任意损坏内存。
- 新组件严格C++14+ASAN/UBSAN通过：12000随机操作（6503成功更新、3782容量拒绝、1715历史轮）与独立std::set/map逐步对照；满表/碰撞/tombstone/自网排除/幂等占用/后段overflow原子性拒绝通过。生产top实际1048576节点、峰值1048578 owner pairs、2097152槽，完整节点采集/释放/快照与边界通过；满表探测最坏可扫描全表，不能据此称高吞吐。
- `src/native/node_occupancy_adapter.hpp`只为同一helper分配backing buffers和导出冲突结果，不另存活跃owner set/history map。新 `scripts/node_occupancy_routes_transform.py`在独立已冻结完整搜索副本替换节点占用、history和node snapshot；站点ledger/站点history、外层调度、包构造仍host。原生产搜索C top、原CPU/XRT副本、正在运行的旧RTL/物理流程均未改。
- 准备bundle `data/derived/node_occupancy_router_20261024_v1`，`prepare_node_occupancy_router.py` owner629995/exec73082已退出0。report.json status=`bounded_node_occupancy_full_search_cpu_differential_verified_full_workload_pending`，绑定新代码/编译/原始产物。CSR/compact共400完整随机协商批、4938 searches、3750 snapshots、1250 rounds、node-history2412、site-history2106、site-paths2896，所有中间路径/状态/成本/unknown/轮冲突完全相等；routed210/incomplete190。禁止native邻接回退，生产搜索容量不变。完整新router已严格编译。**所有绑定源码/测试/脚本已冻结，修改必须派生新版本**。
- 真实完整两表示×两批1062网已启动：唯一 `node_occupancy_router_pipeline.py` owner**694011**/exec**6336**；CSR worker**694611** CPU116、compact worker**694612** CPU117，最后已核实live/CPU活跃。状态在bundle/state.json。新execution_plan绑定原真实图/fixture/site/config摘要，原搜索参数cache4096/80轮/budget200000/present_cap8不变。结束后唯一owner自动运行 `check_node_occupancy_router.py`，逐字段比较两种表示各两批完整raw与原完整搜索核raw，并核对controller/snapshot/kernel计数完全一致；预期报告`results/node_occupancy_router_audit_20261024_v1.json`、status=`bounded_node_occupancy_two_full_router_conditions_independently_verified`。尚未终态；不要另启动审计或重跑。
- 新组件HLS bundle `data/derived/node_occupancy_hls_20261024_v1`，project `build/node_occupancy_hls_20261024_v1`。`node_occupancy_hls_pipeline.py` owner699302/exec29086已退出0，Csim和csynth均完成；**不要重启**。使用已读Ross hls-pragma-scope/hls-synthesizable/hls-run-flow，实际本机2022.2 Tcl替代新版Unified命令；新top所有INTERFACE均位于top函数体，helper无动态分配/STL/递归/成员外部指针。默认5ns、setup margin1.35ns。
- 独立综合审阅 `results/node_occupancy_synthesis_review_20261024_v1.json` SHA=`ae651dfc362d5ce28ff512b37d5c5a095fd0bb44497363dbffc0de9b84e3bc9f`，status=`bounded_node_occupancy_csim_and_synthesis_verified_rtl_pending`。估计3.650ns，LUT72044、FF34036、DSP16、BRAM/URAM0；六AXI bundle。原log保留HLS200-960=1、HLS200-878=45、RTGEN206-101=14；若干自动pipeline II145，**All loop constraints were NOT satisfied**。静态极端循环latency不是实测性能。初次审阅checker使用错误Csim标记文本而拒绝、未发布报告，按实际2022.2 `CSim done with 0 errors.`修正后才审阅通过；原HLS结果未改。
- 阶段证据 `results/node_occupancy_stage_20261024_v1.json` SHA=`b16c9a7c34d9e081cc0068dbf6c206b2bbd701b57e166bf8d88289cbb7ee264d`，status=`bounded_node_occupancy_cpu_and_synthesis_verified_full_real_workloads_running`。重新核对129输入/产物、准备和HLS receipts、真实worker身份；项目check通过。阶段报告首次生成时HLS恰好已退出，live-owner检查正确拒绝，没有写出旧状态；改为核验真实终态+receipt后发布本报告。
- **下一步**：先读取原真实工作负载owner及其自动审计终态；为占用组件创建独立完整深度TB/RTL验证副本（旧CPU test里的old/new vector会resize且可为空，不能直接把该TB当cosim指针深度合法）。保持完整1048576/2097152容量和原syn RTL，覆盖跨调用reset/update/snapshot/history/失败不变/恢复，先Csim再cosim；no-argument main无需argv。当前**未执行新占用组件RTL**，也没有其物理/板卡结果。可后续分析II145和meta/input memory exit依赖，先记录证据再用新版本优化，不能改正在跑的完整CPU副本。
- 原完整搜索核物理CSR/compact会话及PID4146646/4159154最新仍live/source运行、均完成RTL Optimization Phase1但stage仍synthesis；XSim原leaf2764812/2764813仍live。原HLS唯一后继3099710继续负责重放和full-state边界。继续此前物理终态MCP快照/独立验收步骤，不重复source。上一轮progress，本轮实现/CPU集成验证/真实提交/实际综合为progress；完整目标active，全部特殊资源、完整硬件外层控制和真实DDR/HBM/功耗仍缺。

## 最新：完整搜索核独立物理验收入口已测试，实际物理任务仍运行（2026-10-24）

- 新增 `scripts/check_search_kernel_physical.py`，只读验收冻结的完整搜索核OOC，不启动/重启Vivado。先核对两模式终态及原MCP会话/owner/log/完成命令，再检查plan/input/RTL/ROM完整绑定、三个DCP摘要、综合与布线阶段报告、实际5ns/200MHz及1.35ns setup uncertainty、setup/hold/pulse-width非空端点与裕量、独立check_timing一致性、全网布线、资源、DRC和方法学违例。保留负结果；不自动waive TIMING-18，不将外部IO未知约束当完整closure。
- `tests/test_search_kernel_physical.py`五组测试通过，使用已有2022.2真实旧译码核报告验证格式，另覆盖负裕量/空端点/不完整布线/不一致或非有限数值/错误时钟/被放宽约束/错误或运行中会话。旧报告949条TIMING-18仍使方法学清洁门控为false。**这些测试不是新完整搜索核物理结果**；新报告实际产生后仍须确认格式与证据。
- 准备证据 `results/search_kernel_physical_audit_preparation_20261024_v1.json` SHA=`3a12f73bb5b353fd4e0e69d31d773244e2bd41b9ab5ed79735ff6d4cc0761504`，status=`full_search_ooc_auditor_tested_actual_physical_results_pending`。绑定新checker/test、依赖、真实旧报告、实际MCP当前快照及三份执行receipt。项目check通过；使用当前live会话的验收尝试按预期拒绝，未创建任何物理通过报告。**新checker/test现已冻结，后续修复用新版本**。
- MCP最新仍确认CSR会话`vivado-20261024-200659-4536a838`/PID4146646、compact会话`vivado-20261024-200724-c151e46f`/PID4159154实际执行原source，queue_length=0，stage=synthesis；不要重复source。当前记录为`data/derived/search_kernel_physical_20261024_v1/audit_preparation_live_sessions.json`，不能将其当终态receipt。无新增自动物理审计owner。
- **下一步**：两会话source完成后，先以`vivado_status(action=session)`保存新的JSON，再发送其他Tcl（否则last_completed会被替换）。JSON格式：`{"csr":{"session_id":"...","observed_utc":"UTC ISO时间","status":原始MCP状态对象},"compact":{...}}`。要求is_command_running=false、last_completed_code=0、queue为空、最后命令是本模式原source且output含SEARCH_PHYSICAL_FLOW_COMPLETE。然后运行：`python3 scripts/check_search_kernel_physical.py --bundle data/derived/search_kernel_physical_20261024_v1 --session-status <新的终态快照.json> --output results/search_kernel_physical_audit_20261024_v1.json`。所有质量门控通过退出0；完整报告包含负门控退出1；缺证据/运行中拒绝且不发布报告。不要伪造终态，也不要改冻结flow来适配检查器。若真实格式不兼容，保存证据后新建checker版本。
- 正式物理结果还需结合DCP实时查询/必要的独立重开检查；此checker仅绑定DCP摘要、不声称已重新打开。裸器件OOC不含U280 shell保留区，不能推断平台时序。RTL功能原重放与full-state边界流程仍由原唯一owner3099710处理；最后实际确认XSim leaf2764812/2764813和旧heap leaf2468371 live。完整目标active，实卡DDR/HBM/功耗、全部特殊资源与硬件外层协商/占用仍未完成。
- 上一状态回复轮核对实际live进程，为verified wait；本轮完成验收实现、真实报告/拒绝测试与准备证据，为progress。

## 最新：完整搜索核两模式独立物理综合已实际启动（2026-10-24，以本段为准）

- 新bundle `data/derived/search_kernel_physical_20261024_v1`，plan SHA=`738b9eaee10071eea323b7f2191d1e4f8d337a0541d667517e96b7d10b3a2aa0`。`scripts/prepare_search_kernel_physical.py`核对完整CPU审计与boundary_setup的生产RTL绑定，逐字复制CSR58.v+1.dat、compact61.v+1.dat；原HLS/重放/边界工程未改。`hardware/vitis/search_kernel_physical_flow.tcl`也已冻结，不直接覆盖。
- MCP先查询已有会话，原A `vivado-20261023-072116-f6c0019b`实际只读返回2022.2/checkpoint_routed/project_routed_19；保持其当前设计。B会话未操作。新建两个A Tcl无GUI会话：CSR=`vivado-20261024-200659-4536a838`，Vivado PID4146646，CPU122/124；compact=`vivado-20261024-200724-c151e46f`，PID4159154，CPU125/126。两边general.maxThreads=2，**均已实际进入synthesis，且日志确认Got license for Synthesis and/or xcu280**。不能据此推断xcvu13p也已授权。
- 唯一提交调用为 **functions.exec cell4367**，两个 `source .../{mode}/run_flow.tcl` 请求。compact先启动，300秒后MCP返回status=running（继续执行，并非超时失败）；CSR随后实际开始，尚有待返回的MCP调用。后续可wait cell4367获取尚未回传的结果，但**不要重新source或用execute往这两会话排写命令**；先用各会话 `vivado_status(action=session)` 查看is_command_running/last_completed_code。本机mode/state.json也记录实际Vivado PID与阶段，始终核实进程，不因日志静默或观察超时重启。
- 各脚本顺序：非工程OOC synth_design→synthesized.dcp/综合报告→opt_design→place_design→phys_opt_design→placed.dcp→route_design→routed.dcp/布线报告。器件xcu280-fsvh2892-2L-e，create_clock5ns，setup uncertainty1.35ns，保持HLS目标；外部AXI输入/输出delay等待实际平台，**没有添加false path或waiver隐藏未知约束**。整个U280裸器件OOC不含平台shell/保留区，不能当平台timing closure。
- Ross `vivado-timing-methodology-checks`已读，要求2026.1；本机2022.2 help无report_methodology -json，改用文本rpt和get_methodology_violations全属性Tcl列表。help捕获于csr/local_help.txt、flow_help.txt；首次redirect命令本机不支持，随后用puts[help]捕获，失败日志保留，没有重启会话。方法学规则将在实际报告产生后按ID查阅；目前没有实际违例可分类或修复。
- 提交证据 `results/search_kernel_physical_submission_20261024_v1.json` SHA=`88af41cf94900c63781f80acc44c6c90459aceea5d6480851f8c529e25fcf408`，status=`two_mode_full_search_ooc_synthesis_started_not_yet_verified`。内部引用observation_0001与冻结plan。只是启动/许可/进程证据，未宣称综合/布局/布线成功。完成后审计各mode/state.json、error.txt、reports/*、synthesized/placed/routed.dcp，并结合MCP最终退出状态；须检查内部setup/hold、未约束路径、route状态和资源，保留警告。没有预先生成物理通过报告。
- 原XSim重放leaf2764812/2764813及旧heap HLS2468371最后仍实际live，HLS后继3099710等待replay；边界RTL尚未运行。完整真实CPU及XRT宿主接入均已完成各自CPU审计，不重启。物理工作可并行提供证据，不能代替待完成的RTL功能门控；XO/link/实卡入口继续要求那些门控。
- 前轮与本轮均progress；项目check通过，完整目标active。仍需完整RTL功能、物理结果审计、全部特殊资源、硬件外层协商/占用及真实平台DDR/HBM/功耗。

## 最新：完整路由XRT副本及上板来源校验入口已落地（2026-10-24，以本段为准）

- 新 `scripts/search_xrt_routes_transform.py` 与 `scripts/prepare_complete_search_xrt_router.py` 在独立副本替换binding/adapter/runtime；原CPU源码、运行副本和 `search_xrt_v1` 冻结库未改。宿主移除heap/index/records/keys分配，仅保留输出暂存；显式ExchangeScope调用驻留Session，快照/协商/占用更新仍CPU，无native邻接回退。
- `data/derived/complete_search_xrt_router_20261024_v1` 已终态complete（prepare owner3874905/exec63785退出0）。实际XRT完整路由二进制 `router_xrt` 严格警告编译链接通过，nm确认未链接search_kernel_csr/compact CPU核；两种真实图descriptor离线预检通过。**没有打开设备**。
- 同一新binding的驻留生产C核差分完成400随机全协商批次、4938搜索、3750快照、1250轮；节点历史2412、站点历史2106、站点路径2896，routed210/incomplete190。完整中间路径/状态/代价/unknown与每轮冲突一致，禁止native回退，全部生产工作区容量不变，ASAN/UBSAN通过。宿主session每个随机图重新初始化meta，backend内存复用；包含跨net/sink/round驻留状态验证，不是仅接口mock。
- `results/complete_search_xrt_router_20261024_v1.json` SHA=`2b27f915dc203692efdd5bc2f121575d8df74affd2b5d2a551ccd611c9282d36`，status=`full_search_xrt_router_compiled_resident_negotiation_cpu_verified_board_pending`。核对62输入、74产物及6份编译/预检/差分receipt；另绑定上板入口代码与27项合成拒绝测试日志。新源码/脚本已绑定，后续修改用新版本。
- 新 `scripts/search_xrt_board_link.py` 提供link/verify：强制原重放+状态容量RTL通过报告，XO所有Verilog和ROM.dat逐字节匹配所选CSR/compact的已审计综合产物，核对15参数XML，然后绑定完整v++命令/输入/config/platform/XO/log/xclbin。不能用相同核名/XML或mode参数替代二进制来源。**尚无完整搜索核XO导出或真实link**，脚本没有提前生成成功证据。
- 新 `scripts/run_complete_search_xrt_router.py` 是实际硬件完整路由入口，必须通过上述link来源校验、宿主准备与完整CPU真实1062网审计；按相同两批全工作量执行，并比较所有原始route/search/site/negotiation字段、三类计数与实际传输完成/流量/时间总计。硬件host不回退CPU。3组单元测试含27项损坏拒绝通过，日志 `results/full_search_xrt_board_contract_20261024_v1.log`；合成校验不等于实际板卡执行。运行说明 `hardware/vitis/SEARCH_XRT_ROUTER_V1.md`。
- **原完整搜索核真实CPU已独立全量审计通过**：`results/complete_search_router_audit_20261024_v1.json`，status=`two_full_router_kernel_conditions_independently_verified`，SHA=`fcd4e4007924bcc729d0f259959e5f9a0f0a267ff16a54ba4a1799e5bb9ca3d6`。CSR/compact各两批完整1062网，每批16836搜索；完整原始路径/状态/站点/协商结果相等，0 capacity/invalid。CSR每批KC=[batch,16836,4248,2431434032,9636444644,572381,441]，compact=[batch,16836,4248,2431502000,9636714020,572397,441]；这些word计数是CPU逻辑ABI量，不能当实测PCIe/HBM流量。pipeline3452597、后继owner2609626均终态complete，勿重启。RTL重放leaf2764812/2764813仍实际live/CPU活跃，最新仍0/2@128000ps；HLS后继3099710仍等replay，边界RTL未启动。旧独立heap HLS2468371仍live。继续各唯一owner。
- 前轮与本轮均progress；项目check通过，完整目标active。后续：完成现有真实CPU与RTL审计，推进独立副本的完整RTL物理综合/实现/时序；通过RTL门控后导出XO、按已准备入口做真实平台链接及板卡DDR/HBM/功耗。全部特殊资源语义、硬件外层协商/占用与实卡实验仍未完成；不把CPU协议或编译通过当整体完成。

## 最新：完整搜索核 XRT 宿主库编译及CPU协议验证通过（2026-10-24，以本段为准）

- 新独立库 `hardware/vitis/search_xrt_v1/`：ABI从已校验内存计划派生；读取物理MEM_TOPOLOGY/CONNECTIVITY及聚合GROUP_TOPOLOGY/GROUP_CONNECTIVITY，检查完整文件/表边界、U280布局、通道连续性、组容量及共享AXI映射。实际BO使用 `kernel.group_id()`，不混用物理bank索引。要求U280硬件xclbin、单一指定ap_ctrl_chain CU及15参数ABI；调用路径已和本机XRT2.14.354编译链接，**未打开板卡**。
- `Session<Backend>`保留图及生产工作区在设备，每次提交roots/packet，先校验返回头才按有效长度读path/unknown。初始meta=0，由生产核在首个有效查询初始化slots。传输/设备错误后poison；host输入预检失败不会poison。控制器预检可在旧非零epoch返回invalid且不改变workspace，现已正确接受，并补禁用target→拒绝→恢复回归；不能一律要求每次拒绝都推进epoch。
- 冻结构建入口 `scripts/prepare_search_xrt_interface.py --output <新目录> --cpu 119`；本轮bundle=`data/derived/search_xrt_interface_20261024_v1`，exec60331退出0，state complete。冻结副本中的exchange/topology均严格警告+ASAN/UBSAN通过；XRT实际路径编译链接通过。CSR/compact各11次真实生产C-model连续查询（全部生产容量、32/16/8满状态、三种overflow、兼容合并、冲突、无效包、禁用target、恢复），literal完整路径/65字state核对；共22事务。12传输异常拒绝并验证poison后不再读取，host前置拒绝后可恢复。合成拓扑三布局通过，16损坏+4截断拒绝，特意把group ID置于40以上，与物理bank编号分开。
- 结果 `results/search_xrt_interface_20261024_v1.json` SHA=`6e6dffd7c2fc59d5ecc1c17010551ae5d84e5619fced372f9f0bbc90ebb3da2a`，status=`full_search_xrt_host_interface_compiled_and_cpu_protocol_verified_board_pending`。再次核对44输入、46产物全部摘要与6份实际编译/运行receipt。旧开发期exchange20事务日志、link v1/v2及拓扑测试warning保留在原产物/会话；正式冻结副本用最终22事务源码，不改生产offset v3或正在跑的完整CPU副本。
- **尚未集成完整1062网XRT路由程序**；当前只是可编译宿主库与CPU协议验证。下一步在新副本替换binding，保留外层协商/动态占用和完整输出比较，并加入真实link报告/xclbin摘要门控。CSR/compact同核名同XML，不能仅凭XML或调用者mode参数证明二进制模式；Transport参数当前只校验图descriptor，真实运行入口必须外部绑定构建证据。实际U280 xclbin分组格式、BO分配、硬件执行、时序、DDR/HBM/功耗仍无证据。
- 当前完整搜索核CPU worker3452600/3452601实际live且CPU活跃，pipeline3452597尚无完成条件；RTL重放leaf2764812/2764813仍live/活跃，最近日志仍0/2@128000ps，不据此判死或重启。HLS唯一后继3099710等replay，边界RTL未启动；旧heap leaf2468371仍live。保留各唯一owner，不重复提交。
- 前轮与本轮均为progress。项目check通过，完整目标保持active；全部特殊资源、硬件外层协商/占用、完整真实流量RTL/物理与板卡实测仍缺。

## 最新：完整搜索核静态 DDR/HBM 布局已验证（2026-10-24，以本段为准）

- 新增 `scripts/search_kernel_memory_plan.py` 与 `hardware/vitis/search_kernel_memory_v1/` 三套连接配置，面向生产 offset v3 完整搜索核，保留旧译码器配置。核对源码及 CSR/compact 两份实际 `kernel.xml`：13 个 BO、2 个标量、7 个 AXI master，参数顺序和控制偏移一致。完整深度原始容量523788712字节；每 BO 按4096对齐后523800576字节（499.53515625 MiB）。keys=260MiB，单个256MiB HBM伪通道放不下。
- DDR共享池=`DDR[0]`；HBM共享池=`HBM[0:3]`；HBM分组把graph/input/heap/index/record/output分别映射0/1/2/3/4/5，keys映射6:7。每池预留16MiB是宿主规划策略，不是已测空闲容量。HBM分组属于独立拓扑实验。共享两通道在零预留下可容纳，但不满足此策略。拒绝单BO超容、总和超容、组部分重叠、同AXI bundle映射不一致及漏项/标量映射。
- `tests/test_search_kernel_memory_plan.py` 12项测试通过，包含实际参数容量及两份XML、边界、布局和ABI损坏拒绝。`scripts/check_search_kernel_memory_plan.py` 重读所有绑定输入/配置/容量表，生成 `results/search_kernel_memory_plan_20261024_v1.json`，status=`static_full_search_memory_plan_verified_board_pending`；另7项伪造/漂移拒绝记录于 `results/search_kernel_memory_plan_negatives_20261024_v1.json`。`python3 scripts/run.py check`通过。
- plan SHA=`9b55d77097d4d31c8334251c2687c4f1436221c9bec009a86b3edcf909030c8e`。新生成器/配置已绑定，后续修改用新版本。实际平台链接、完整搜索核XRT宿主与板上BO分配尚缺；应按 `kernel.group_id(arg_id)` 分配，不能把聚合group ID当物理MEM_TOPOLOGY bank下标。教程在U50演示分组，不证明本地U280链接；早期hbm_large_buffers示例排除表包含U280，不能据此声称本板已支持/验证。详见新目录README及官方链接。
- 最新真实word_snapshot四条件×两批完整1062网**已独立审计通过**：`results/word_snapshot_router_audit_20261024_v1.json`，status=`four_full_router_word_snapshot_conditions_independently_verified`，SHA=`e8ad8379929a2631dd3a53a6cc12682fc0ee347d2438b170b4139379236c92c8`。原owner2734393和chain1991787终态，不重启。后继owner2609626已自动启动完整搜索核真实CPU实验：pipeline3452597，CSR/compact worker3452600/3452601均实际live/CPU活跃；bundle=`data/derived/complete_search_router_20261024_v1`，stage=`four_full_workloads`（两表示各两批），尚无终态结果，不能手动重复提交。原CSR/compact RTL重放leaf2764812/2764813仍live且CPU活跃；HLS后继链3099710等待replay，边界RTL未启动。独立heap HLS leaf2468371仍live。继续沿用各唯一owner。
- 上一状态回复轮核实了具体live进程，为verified wait；本轮为progress。完整目标仍active：静态布局不是板卡证据，全部特殊资源语义、硬件外层协商/占用更新、完整真实流量RTL/物理时序及DDR/HBM/功耗实测仍未完成。

## 最新：满状态容量HLS准备已审计，独立RTL验证链接管后续（2026-10-24，以本段为准）

- `scripts/prepare_search_kernel_boundary_rtl.py` 已终态complete，原owner2962113/exec61353退出0。新项目 `build/search_kernel_boundary_rtl_20261024_v1/{csr,compact}` 从原已完成综合副本派生，只替换验证testbench路径；全部生产syn产物逐字节不变。两模式均实际通过HLS Csim 8事务与C激励生成8事务，生成的RTL TB事务数均为8，原literal C postcheck二进制已生成；**边界RTL尚未运行**。
- 独立准备审计 `results/search_kernel_boundary_setup_20261024_v1.json` SHA `c65fc1d802333b4ec18d418051874deead432f99a4023ad590363226ce18176f`，status=`state_capacity_boundary_hls_setup_verified_rtl_pending`；绑定原证据/生产综合及新的输入vector、testbench、postcheck。full32/16/8状态容量、完整heap/labels/workspace不变，未通过缩小设计或改RTL绕过边界。
- 本机2022.2实际help不支持`remove_files`，证据 `/tmp/a_search_boundary_hls_help_20261024_v1/help.log`；v2 help确认`cosim_design -setup`只生成仿真文件、不运行RTL。新副本`hls.app`仅精确替换唯一tb路径；原生产源码仍引用冻结source，未改原工程。argv均空，对应无参数main。成功help已复制进新bundle并绑定。
- **新增唯一HLS后继链已运行**：`scripts/supervise_search_kernel_verification.py` owner3099710/exec45038，bundle `data/derived/search_kernel_verification_chain_20261024_v1`。已自动完成boundary_setup_audit，现等待原replay owner2749618/exec86939终态。之后自动运行原重放独立审计→`search_kernel_boundary_rtl_pipeline.py`（两模式8事务、64MiB栈、100ms仿真上限、原C postcheck）→`check_search_kernel_boundary_rtl.py`。不要另行启动这些auditor或边界pipeline，与此链竞争。失败停止，不重启或覆写；后续物理实现尚未启动。
- 预期边界RTL报告为`results/search_kernel_boundary_rtl_audit_20261024_v1.json`，status=`production_search_top_full_state_capacity_boundaries_rtl_verified`。新golden/transaction解析契约7项拒绝探针通过；没有提前发布RTL成功报告。
- 原64MiB栈重放CSR/compact leaf2764812/2764813均已实际核实live、CPU活跃；仍为0/2完成，最新打印128000ps。进程fd显示已读入首事务各AXI输入块，尚未报告完整功能结果。不能因耗时或打印未更新而重启。原v3 HLS失败证据保留，重放成功也不能改写原flow为通过。
- 真实word_snapshot四条件最新已完成[1,3,0]，仅条件2仍在跑；原链owner1991787和完整搜索核后继owner2609626均保留。完整搜索核真实1062网实验尚等待word独立审计，不手动提交。
- A Vivado MCP重新检查：会话`vivado-20261023-072116-f6c0019b` idle、pid2607458仍live；实际只读execute成功返回`A_SESSION_CHECK 2022.2 checkpoint_routed project_routed_19`。列表metadata的version字段虽然显示Tcl stack错误，**不代表实际Tcl会话不可用**。未更改design/project或B会话，后续物理工作仍优先用MCP。
- 上一目标轮、本轮均为progress。完整目标保持active：仍缺完整真实流量RTL/物理时序、全站点特殊资源语义、硬件外层协商/占用更新和实卡DDR/HBM/功耗。准备与组件通过均不替代完整目标完成。

## 最新：完整搜索核后继已排队；快照通过；XSim栈恢复正在验证（2026-10-24，以本段为准）

- `snapshot_router` 四条件×两批完整1062网独立审计已通过：`results/snapshot_router_audit_20261024_v1.json` SHA `d1571df80450ab4270f7d4a4eb9939a65b745dcd8042fc7db45caf3275c2b17d`。本轮核验audit receipt/log及15项非raw绑定；每批SC=[batch,4248,4247,3186,4232,0,265,0,14,0]，CC与controller前驱相同。原snapshot owner2050070已终态，不重启。
- 原唯一链owner1991787/exec84678已自动启动`word_snapshot_router_pipeline.py` owner2734393，worker2734553/2734555/2734558/2734562（CPU122/124/125/126）。bundle `data/derived/word_snapshot_router_20261024_v1`；四条件完整1062网仍运行，以实际进程/receipt为准。
- 真实完整搜索核实验已编译、冻结：`data/derived/complete_search_router_20261024_v1`（prepare exec97487退出0）。2条件CSR/kernel与compact/kernel，各2驻留批完整1062网，链接真实offset v3生产top；native adjacency fallback直接抛错，宿主仍负责快照/外层协商/占用更新。逻辑packet word计数不能当实测PCIe/HBM流量。
- 已启动新增**唯一后继管理进程** `scripts/supervise_complete_search_router.py` owner2609626/exec50829，bundle `data/derived/complete_search_router_chain_20261024_v1`。观察原chain终态并核验word audit/gate后，单次启动`complete_search_router_pipeline.py`，自动完整raw审计。现在等待word，完整搜索核真实全量**尚未启动**；不要手动竞争提交。预期报告`results/complete_search_router_audit_20261024_v1.json`，status=`two_full_router_kernel_conditions_independently_verified`。
- 生产top完整协商CPU组件已通过：`results/kernel_route_component_20261024_v1.json` SHA `ec6bed54431d6238fee39a5a520b9ca00678226d01d1d6a9de09b073b5449436`。400合成完整多网批次（每表示200）、3750 snapshots/4938 searches/1250 rounds，节点历史2412/站点历史2106/site paths2896，routed210/incomplete190；逐项比较所有中间路径/状态/代价/unknown与每轮冲突，禁止native fallback。bundle `kernel_route_checks_20261024_v2`终态，不重复。
- HLS v3两模式实际Csim和综合均通过：`results/search_kernel_synthesis_review_20261024_v3.json` SHA `5ffaf3708d24694250eb64eae0bb6e87335420f711dfd6896ebcb5ebc2a9f94d`。估计3.756ns；CSR/compact LUT355208/369458、FF167307/174585、BRAM69/DSP77/URAM3。5ns减1.35ns uncertainty后的3.65ns预算未满足，不能宣称timing closure。
- **原HLS v3已经失败终态**，owner2191556/exec18662退出1，不再是RTL运行中。两模式XSim在0ps的巨大next-state组合进程崩溃，未执行完整事务；Csim/综合证据保留。`results/search_kernel_xsim_failure_20261024_v3.json` SHA `86c4ee4fb07faf5bbd7161892e96f87563d3ae7f496bbb6d865fbdb8290016e6`：生成native函数各需要12406024字节栈，当前父进程soft limit8MiB（原child limit未单独保存）。Ross `vivado-simulate-rtl`诊断与官方文档检索已做；AR64434只适用于综合，不能称本例已知XSim bug。环境doctor依赖解析通过；MCP已有A/B会话仍在，查询version返回Tcl栈错误，未操作B。
- 独立重放 `scripts/replay_search_kernel_xsim_stack.py` owner2749618/exec86939，bundle `data/derived/search_kernel_xsim_stack_20261024_v1`。逐文件绑定/复制原已编译XSim snapshot、全部RTL、输入vector与原C postcheck；**只对子进程设64MiB栈**，bounded `run 100 ms`。CSR/compact XSim leaf2764812/2764813，CPU120/123；已越过0ps，到128000ps并实际执行，仍无完整pass。旧project/失败日志未改；不要重启。完成终态后运行`python3 scripts/check_search_kernel_xsim_replay.py`，预期`results/search_kernel_xsim_replay_audit_20261024_v1.json`。该独立checker检查2个RTL transaction与原golden postcheck、所有输入/输出绑定；4项transaction解析拒绝探针通过。重放pipeline不会自动调用checker。
- 为综合的state-array越界warning补了真实生产top边界测试：`tests/test_search_kernel_state_boundaries.cpp`，链接原审计ASAN/UBSAN top对象、保留全部生产workspace容量。两表示各8事务：满32/16/8、三种overflow、满容量兼容重叠、最后一位/分类值冲突、失败后恢复；65字结果使用独立literal oracle。16事务全部通过独立审计：`results/search_kernel_state_boundaries_20261024_v1.json` SHA `f44b74691dbeaea854e4e854bfb201d4f5cbe40d3ce883f802cb4f4042c5608a`；bundle `search_kernel_state_boundaries_20261024_v1`、exec10180均终态。这是CPU边界证明，尚未加入当前2事务RTL激励，不能当RTL饱和覆盖。
- 曾因命名冲突覆盖旧`prepare_kernel_router.py`，现已从会话原始patch逐字恢复，SHA `06943b22c2b928200df920881c850a5334e41e27611a2cd3f5baeb4c7af5bea7`与两份旧plan完全相同。原pipeline/checker没有覆盖。恢复证据`results/kernel_entrypoint_restore_20261024_v1.json`；错误新bundle `data/derived/kernel_router_20261024_v1/INVALIDATED.json` **禁止运行**。正确新入口均为`complete_search_router`，其运行输入未漂移。
- 本轮`python3 scripts/run.py check`通过。完整目标仍active：所有特殊资源语义、全部FPGA协商/占用更新、物理实现/时序、板卡DDR/HBM与功耗尚未完成；当前只有14物理验证site实例，不能扩称全站点语义。旧独立heap HLS v2最后仍活跃，需核实owner2468333/leaf2468371，不与已失败search_kernel v2/v3混淆。上一目标轮为verified wait，本轮为progress。

## HLS v3最新观察：综合前检查通过，尚未完成综合/RTL

- 两模式已实际完成工具Csim和`Finished Checking Synthesizability`，v1/v2的pointer-to-pointer错误已不再出现在v3日志；仍是运行中，未获`SEARCH_KERNEL_SYNTHESIS_COMPLETE`或RTL通过。启动child CSR2192191/compact2192193；实际HLS leaf需用proc树核实。不要把通过前检查写成完整综合成功。
- 下一会话先检查原exec18662 / owner2191556及`data/derived/search_kernel_hls_20261024_v3/{csr,compact}/flow.log`，继续原任务。若成功终态运行已准备独立HLS审计；若失败按具体报错创建新版本。完整snapshot→word任务链owner1991787仍负责CPU后继。

## 最新补充：offset v3 CPU通过，第三次HLS已启动

- `data/derived/search_kernel_cpu_20261024_v3`已经终态complete（原owner2175810/exec66275），packet两表示各6事务/38拒绝、10000 native ledger offset代价对照、每表示32真实查询全部通过；两个真实模式均found32/expanded217245/site_paths0/unknown证据32。`results/search_kernel_cpu_component_20261024_v3.json` SHA `cc6bee082b82c64a35b15bf3e08be20f88825405d1c340594d19f4e9e328665f`。ASAN/UBSAN、完整输出与工作区guard通过；真实probe仍不代表完整协商或真实site路径。
- v3精确派生脚本及20个文件已冻结；Source位于`hardware/vitis/search_kernel_offsets_v3/`。新增OffsetSearchController、SearchOffsetProvider、SearchOffsetCost、OffsetImageAdjacency；Cost/Provider/Adjacency对象不保存缓冲区pointer，word offset/计数替代成员指针，所有image/packet/flags/requirements基址从函数显式传入。搜索算法/队列/状态/容量/packet ABI未缩小或改变。生产top额外链接missing host_contract include路径的开发编译错误已修正，之后严格编译通过。
- `scripts/search_kernel_hls_offsets_pipeline.py`已启动，exec18662，owner2191556；bundle`data/derived/search_kernel_hls_20261024_v3`，两个HLS分别CPU120/123，project`build/search_kernel_hls_20261024_v3/{csr,compact}`。Csim/综合/RTL按Tcl顺序，原二事务preflight binary只作共同ABI/golden校验（明确不是v3执行证据）；实际v3由新的CPU audit及工具Csim验证。新HLS尚无成功终态，先核实原进程/日志，不重启或改冻结源码。
- 成功终态后运行：`python3 scripts/check_search_kernel_hls.py --bundle data/derived/search_kernel_hls_20261024_v3 --output results/search_kernel_hls_audit_20261024_v3.json`。pipeline结束只标flow_complete_pending_independent_audit，**不会自动审计**。该checker验证两模式Csim、RTL前/后两份golden、2个RTL transaction、器件时钟、RTL/报告/receipt/hash；仍不替代真实流量、全容量搜索峰值或板卡验证。若再次失败，新版本保留所有失败证据继续修复。
- 原controller终态后任务链已自动启动snapshot owner2050070：worker PID2050908/2050910/2050913/2050915，最后四个live CPU100%；chain owner1991787/exec84678继续等待完整audit。word_snapshot由该唯一链在snapshot通过后启动，勿单独提交。前一目标轮为verified wait，本轮明确progress，完整目标active。

## 最新：完整搜索硬件入口进入综合；全量快照队列已启动（2026-10-24）

- 原controller四条件×两批完整1062网已独立审计通过：`results/controller_router_audit_20261024_v1.json` SHA `9c3667cdc721f2fe58696e853dfd59d91488c7364c49f16ec52ec834d2366ed9`。每批16836 searches、298041785 pushes、165864259 pops、0 improvements、16836 found、0 capacity/invalid，peak heap73388/labels265239/probes14。原owner1278270已终态，勿重启。
- 现在有实际后续任务管理进程：`scripts/supervise_search_router_chain.py` owner1991787/exec84678，bundle `data/derived/search_router_chain_20261024_v1`。已核验controller audit receipt/log与15项非raw绑定，自动启动snapshot owner2050070，bundle `data/derived/snapshot_router_20261024_v1`。四worker使用122/124/125/126；不得另行启动snapshot或word。该管理进程等待snapshot完整审计，再单次启动word_snapshot；未知失败停止、不自动重启。完整目标仍active。
- 上轮新增word协商接口已通过12原有完整协商场景及200随机完整批次：1875 snapshots/2469 searches/625 rounds；node history1206/site history1056/site paths1445；routed105/incomplete95。证据`results/word_snapshot_routes_component_20261024_v1.json`。`data/derived/word_snapshot_router_20261024_v1`已准备/严格编译/冻结，尚未全量运行；其8项审计测试通过。新adapter明确选择WordSearchController，避免Provider旧Core别名误用。
- 真实静态图邻接 `hardware/vitis/search_graph_adjacency.hpp` 已完整扫描两种图：每种274732 nodes/220973 known/53759 unknown/1100754 directed edges/maxdegree642，所有7字段及native搜索稳定顺序一致，保留并行边/属性/未知状态，含边界输出guard与无效配置拒绝。审计`results/search_graph_adjacency_component_20261024_v1.json` SHA `236fa9366626dee1539647ddbc2d2066cceadfd687e4bde46b12388707b908a6`。原exec42589已经终态，勿重跑。只是CPU邻接证明。
- 新flat控制器 `hardware/vitis/search_controller_flat.hpp` / `src/native/search_flat_controller_adapter.hpp` 把unknown PIP改为uint64(tile<<32|pip)，路径改为每边8×uint32(source,dst,tile,pip,up,down,attr,dir)，搜索算法由`derive_search_flat_controller.py`精确派生。1000 native+1000 snapshot随机完整搜索、10容量类、3 C++14事务、literal路径/PIP/guard/epoch回绕全部通过；`results/search_flat_controller_component_20261024_v1.json` SHA `505f821b2bd0676eeaa9621f50190d31a9b9ea9f618f17847e7af3c148978ec3`。bundle flat_controller_checks已终态。
- 新完整单次搜索入口 `hardware/vitis/search_kernel.hpp` / `search_kernel_top.cpp`，CSR/compact分别编译同一top。Packet v1为32字header+65字初始state+forbidden/node costs/flags/protected PIP/semantic keys/requirements/owners/history/fixed连续段，严格长度/计数/规范化校验；roots单独uint32输入，result81×uint64，meta=[epoch,key_count]。工作区容量仍heap131072/labels524288/slots1048576/state32/16/8等；不缩小到toy容量。CPU serializer在`src/native/search_kernel_packet.hpp`。
- 原指针版完整top CPU检查通过：每表示32真实查询（16空动态快照+16非零节点占用/history惩罚），全部found，展开217245，32次含unknown，**site_paths=0**。原生完整path/state/status/cost/unknown/计数一致；另每表示6合成事务覆盖非零站点owners/history/fixed，38类非法preflight保持工作区/meta和guard不变。审计`results/search_kernel_cpu_component_20261024_v1.json` SHA `4913df52964564e9fc236bec642023824f9c2c9ed31af1712b4c5ef2be495122`。不能把真实probe视为完整协商或真实site路径证明。
- HLS v1/v2两模式都Csim通过，综合precheck失败：对象里的pointer成员被2022.2拒绝为pointer-to-pointer。v2仅增加19个函数作用域INLINE，错误减少但仍存在。保留`data/derived/search_kernel_hls_20261024_v{1,2}`及失败证据`results/search_kernel_hls_pointer_failures_20261024_v1.json`；不要覆盖或重启。原pipeline owner1965013/2023714已失败终态。两版均没有综合/RTL成功证据。通用HLS审计脚本`check_search_kernel_hls.py`及3项解析器测试已就绪，完成后按bundle运行，不能提前出通过报告。
- 正在修复的独立v3：`scripts/derive_search_kernel_offsets.py`生成`hardware/vitis/search_kernel_offsets_v3/`。保留原packet ABI/算法/容量，Cost/Provider只保存整数offset/count，image/packet/flags/requirements以显式参数传入，邻接对象不再存image pointer。packet测试已再次通过两模式各6事务/38拒绝；v3真实查询及10000随机offset代价对照正在准备/执行，运行状态以各state.json和活进程为准。后续`run_search_kernel_offsets_cpu.py`→`check_search_kernel_offsets_cpu.py`→`search_kernel_hls_offsets_pipeline.py`。HLS v3未有成功终态，不推断修复有效。
- HLS采用本机2022.2经典Tcl、xcu280/5ns、两模式分别CPU120/123，Csim→csynth→cosim（相同无参数两事务TB，全容量AXI buffer分配），阶段依赖已写入Tcl。本机help确认config_compile支持pipeline_loops，设0，仍需检查综合实际日志。没有Unified IDE HLS接口或luna选择工具；现有单一进程管理，不伪称模型切换。旧独立heap HLS v2 PID2468371/exec16547最后确认仍live，勿与新search_kernel v2失败混淆。
- 项目check通过。本轮为progress：完整controller终态、新完整top/flat实现和CPU证据、HLS实际失败定位/修复、自动后继队列。完整FPGA协商/占用更新、所有特殊资源、板卡DDR/HBM/功耗与物理时序仍未完成；XRT此前0设备。下一步首先读取新v3状态，失败则修新版本，不覆盖冻结输入；成功则独立审计并接完整1062网协商路径，再继续硬件/物理验证。

## 最新：协商快照接入通过；字布局控制器通过；原controller全量已启动

- 标签记录四条件×两批完整1062网已独立审计通过：`results/label_records_router_audit_20261024_v1.json` SHA `d5a8e3299c487dc787b0c3ce255d5768745f5ee55d41d7339b49266cf45c28b0`。owner633188/exec24322终态complete，勿重启。本轮核验receipt exit0/log与13项非raw绑定，未重新读全部巨大raw。每批16836 searches、298041785 appends、0 improvements、16836 validated paths、0 failures、peak265239；完整原始路由/站点/协商结果等价。
- 已启动冻结`controller_router_pipeline.py`：owner1278270 / exec32146；bundle`data/derived/controller_router_20261024_v1`。worker0 CSR/direct PID1280872 CPU122，worker1 CSR/expanded PID1280877 CPU124，worker2 compact/direct PID1280882 CPU125，worker3 compact/expanded PID1280888 CPU126。最新原进程live，自动后继`check_controller_router.py`，期望`results/controller_router_audit_20261024_v1.json`。勿重复提交。
- 新`src/native/search_snapshot_route_adapter.hpp`及`snapshot_routes_transform.py`在独立副本接入静态Provider：旧net路由释放后，从当前规范node owners/history与site_demands/site_history构建只读快照，明确排除当前net旧需求，同net多个sink复用快照；原协商/占用更新/冲突检测保留，Core直接调用静态语义/兼容/代价Provider。构建/邻接/外层协商仍CPU。元数据容量semantics256/attributes65536/protected_pips1048576/site_owners65536/site_history65536/fixed65536；超限/非法快照明确失败。
- 12既有完整协商场景差分通过（严格g++17、ASAN/UBSAN，58.990s）；含信号/配置冲突、兼容共享、多sink、protected、unknown及budget。另200随机完整多网批次逐字段比较**全部中间搜索路径**、状态、unknown、最终树及每轮conflicts/incomplete：1875 snapshots、2469 searches、625 rounds，节点历史快照1206、站点历史1056、带site成功路径1445；routed105/incomplete95，全部等价。证据`results/snapshot_routes_component_20261024_v1.json`和对应日志。
- 已准备并冻结`data/derived/snapshot_router_20261024_v1`：严格生产编译通过，26项generated绑定核验；**尚未运行全量**。等待controller v1完整审计后运行`python3 scripts/snapshot_router_pipeline.py`。自动审计逐份完整raw，要求CC完全匹配controller前驱；snapshot数等于全部net-round数、occupied=snapshots-1，节点/站点history覆盖由原每轮conflicts独立推导，history峰值为原冲突resource并集，要求真实动态site路径覆盖与容量/失败约束。审计5类测试包含缺失/漂移/历史丢失/动态site缺失/超容量/前驱改变拒绝，允许真实site-history为0。期望`results/snapshot_router_audit_20261024_v1.json`。
- 新`hardware/vitis/search_key_words.hpp`：Key使用固定65×uint64=520字布局（32/16/8容量），头字node+三8位count+reserved0；随后成对signal IDs、成对bit field IDs、mask/value字、categorical字段和值。写时unused清零，读时忽略unused但严格验证active归一化与reserved/count；保留零mask字段身份。满524288标签pool为272629760字节（260 MiB），**只是payload，不是已验证HBM分配/板卡容量**。WordLabelIndex保持原hash、全字段比较、探测顺序、ID与epoch语义。
- 显式13字literal ABI oracle、3容量×20000 find/insert/reset操作、原Key数组索引差分、失败原子性、guard、epoch回绕、输出不变与malformed编码拒绝通过；C++14 ASAN/UBSAN。日志`results/search_key_words_20261024_v1.log`。新`hardware/vitis/search_controller_words.hpp`复制冻结完整算法，只替换索引/keys指针和pop/回溯时受检load；`src/native/search_word_controller_adapter.hpp`是独立CPU桥接。
- `scripts/run_word_controller_checks.py`精确核对上述派生差异，保存`data/derived/word_controller_checks_20261024_v1`源码/二进制/plan/四份receipt（全部exit0）。新word Core通过原native随机1000、静态Provider随机1000、10容量类与语义边界、C++14完整3事务/metadata拒绝，状态分布与旧对应测试相同。证据`results/search_word_controller_component_20261024_v1.json` SHA `f1128e8e8b7f4d780867177d34d003257f4b2b23dcd0937b645d51edef343ec9`。这些新文件已冻结，不覆盖改写。
- 下一步：先保持controller→snapshot现有全量审计链。为word Core创建新的协商接入版本（不要改已冻结snapshot v1）：Provider的State类型仍兼容，但其Core别名仍为旧Core，新的route adapter需显式选WordSearchController并使用word_controller_adapter::storage/counters。准备对应完整真实路由对照；随后将真实图解码接入硬件静态邻接、为全word工作区/输入输出建立HLS top，验证2022.2下循环与接口实现，再综合/RTL/物理实现。当前没有完整controller/Provider/word Core的HLS top或RTL证据。
- 原HLS v2 owner2468333/HLS PID2468371/exec16547仍live且CPU活跃（约2h07m），无最终报告，不按耗时判死或重启。已完成v4/外部堆不重启。完整特殊资源、全部FPGA协商/占用更新、板卡DDR/HBM/功耗仍缺。前轮、本轮均为progress；项目check通过，完整目标保持active。

## 最新：静态站点/代价Provider通过差分与真实查询；标签记录全量已启动

- 标签索引四条件×两批完整1062网独立审计已通过：`results/label_index_router_audit_20261024_v1.json` SHA `583e437353f8be77cb4f01b81baf25bf56af5a820b94899255ad150570f86cc1`。原owner4152982/exec45511终态complete，勿重启。本轮核验audit_receipt exit0、log与13项非raw绑定，未再次读全部大raw。各批16836 searches、547134608 lookups、298041785 inserts、0 failures，峰值265239 labels/14 probes/state5/3/2；堆峰值73388，完整原结果等价。
- 已启动冻结`label_records_router_pipeline.py`：owner633188 / exec24322，bundle`data/derived/label_records_router_20261024_v1`。worker0 CSR/direct PID634220 CPU122；worker1 CSR/expanded PID634225 CPU124；worker2 compact/direct PID634222 CPU125；worker3 compact/expanded PID634227 CPU126。最新四个worker原进程live，尚无终态审计。其自动`results/label_records_router_audit_20261024_v1.json`成功后，启动已准备的`python3 scripts/controller_router_pipeline.py`；controller全量尚未启动，不绕过门控。
- 新`hardware/vitis/search_cost_snapshot.hpp`：有界只读代价快照，owner/fixed每条4×uint64字，history每条2字；物理(kind,field)与owner严格排序，绑定时验证域/排序/重复/mask。固定约束与路径state容量独立；动态owner仅计惩罚、排除自身，只对before/after真正变化字段计费，保留零掩码字段历史；节点/资源项/站点总和/组合代价的溢出均显式失败，输出失败不提交。快照创建与更新仍为调用方责任。
- 新`hardware/vitis/search_snapshot_provider.hpp`直接连接完整SearchController，静态实现protected PIP/属性/规范节点过滤、已验证PIP需求查找、未知伪PIP及方向/类型拒绝、固定兼容与代价；邻接为可替换静态接口。源码没有native回调/STL/动态分配；尚无该Provider的HLS top、综合或RTL证据。`src/native/search_snapshot_inputs.hpp`是独立host构建器，不属于硬件调用图，负责真实site配置归一化、状态容量校验和元数据数组。
- 成本10000随机对原DemandLedger/SiteState：compatible1252/incompatible8748；另954字段全局fixed、零掩码、当前net排除、各类溢出、输入拒绝通过。新Provider直连Core的1000完整搜索随机差分通过：found451/budget138/incomplete81/no_path207/unknown123，比较完整path/state/unknown集合及计数。C++14纯静态完整搜索3事务（含非零节点/站点惩罚、未知PIP、fixed冲突）及元数据拒绝通过。严格警告与ASAN/UBSAN通过。
- 真实site两种表示各14项需求、954 fixed字段，对三个net ID检查原生语义和兼容完全一致。第一次测试错误预设attributes<=4096失败，保留`results/search_snapshot_real_sites_20261024_attempt1.log`；实际CSR43770/compact43834，修正测试上限65536，不能使用小随机图的属性容量替代真实域。
- `data/derived/search_snapshot_probes_20261024_v1`已完成，两模式各16个真实source→first-sink查询（每67th net），预算200000，真实fixed/protected/reserved约束；动态占用/history明确为空。两边均found16、展开105236、16次含unknown证据，完整输出和原native完全一致。**site_paths=0**；不能把这组抽查当作真实站点路径或完整协商路由证明。真实metadata与随机/C++14站点路径测试是分开的证据。exec71923终态，两receipt exit0；输入/代码/二进制/提交/日志均绑定，勿重跑冻结probe bundle。
- 终态审计`results/search_snapshot_provider_component_20261024_v1.json` SHA `47fea2d56fa33df7fc7a60ada3671fe64365f0d44b2ddc867d4f601832057bc2`，由`check_search_snapshot_provider.py`验证。snapshot源码已经由probe plan/report绑定，后续修正应使用新版本，不覆盖冻结结果。开发期两次测试命名/缩进编译错误已修正；最终测试均成功。
- 下一步优先把新Provider接入完整1062网协商路由：每net在旧route释放后，从规范node owners/history和各net site_demands/site_history构建准确只读快照，当前net排除，复用同net多sink搜索，保持原native层的冲突检测与完整结果导出，独立对照全部原始结果。需要独立新副本，不能修改当前records运行或已冻结controller v1。随后解决全规模key/state外部字布局、用真实解码器替换native邻接，并接HLS top/综合/RTL/物理实现。不能把目前空占用探针替代这一工作。
- 原HLS v2 PID2468371/owner2468333/exec16547仍live综合，最近约1h43m持续CPU活跃；没有终态报告，不按等待时长判死/重启。完整特殊资源语义、全部FPGA协商/占用/端到端、实卡DDR/HBM/功耗仍缺。前轮与本轮均为progress；完整目标active。项目check通过。

## 最新：完整单次搜索控制器CPU差分通过，全量副本已冻结

- 外部三字堆完整路由四条件×两批已独立审计通过：`results/external_heap_router_audit_20261024_v1.json`，SHA `67291933be3a42608a03e1ad3d58dc2e7f7dcbc6839b9132778e00d96e435708`。本轮核验exit0 receipt/log和13项非raw绑定；终态审计已逐份完整raw比较，本轮未重复读全部巨大raw。原owner3364284终态，勿重启。
- 标签索引完整路由**已运行**：owner4152982 / exec45511；四worker PID4154172..4154175，bundle `data/derived/label_index_router_20261024_v1`。最新state已完成worker1/3（两种expanded），worker0/2（direct）PID4154172/4154174仍live，各占约一个CPU，尚无终态审计。已出各批计数label峰值265239、探测峰值14、路径state峰值5/3/2、0容量失败；仅活跃日志观察，不能代替完整raw终态审计。等待其自动`results/label_index_router_audit_20261024_v1.json`通过，再运行已冻结的`python3 scripts/label_records_router_pipeline.py`。标签记录全量尚未启动。
- 新`hardware/vitis/search_controller.hpp`把root初始化、完整state索引、有界外部堆、十字标签记录、状态合并、未知节点/PIP集合、预算与回溯串为一个静态模板单次搜索。保留target先于budget、未知邻接不计expanded、严格更小cost更新、完整并行边/属性、未知PIP优先于incomplete。核心无动态内存/STL/函数指针；调用方提供存储，邻接/semantics/compatible/step_cost由静态Provider提供。
- `src/native/search_controller_adapter.hpp`仅为CPU桥接：native raw需求归一化、邻接/固定兼容/代价回调和输出容器仍CPU；不能将此称作完整FPGA router。RegionLimits=nodes/roots1048576、degree1024、unknown_pips1100754、path/labels524288、expansions200000、heap131072、slots1048576、state32/16/8。超限显式capacity_exhausted，批处理拒绝出具成功结果。
- 1000随机图完整native差分通过（found570/budget182/incomplete70/no_path119/unknown59），比较status/cost/expanded/blocked/完整path edge字段/demands/unknown集合，另epoch回绕通过。10类容量及语义优先级、错误cost/overflow、非法root/state边界通过；12个既有native场景差分通过（本轮23.414s）。C++14纯静态provider两次完整调用验证路径、需求、未知PIP和epoch；严格警告及ASAN/UBSAN通过。证据`results/search_controller_component_20261024_v1.json`及四份controller日志。
- 新`data/derived/controller_router_20261024_v1`从冻结原native源码替换完整search，严格生产编译通过、22项generated摘要核验；**尚未运行全量**。待label_records全量独立审计通过后运行`python3 scripts/controller_router_pipeline.py`。不应绕过前置门控或改动已冻结源码/plan。审计`check_controller_router.py`比较全部原始批结果并核对每次search/found、push/pop/improvement/heap峰值/labels峰值/探测峰值与前一层审计；11字段损坏、缺失/重复/驻留漂移、截断前驱计数拒绝测试通过。期望`results/controller_router_audit_20261024_v1.json`。
- 旧HLS v2 owner2468333、HLS PID2468371、exec16547仍live且CPU活跃，未获得最终综合报告，不因等待时长重启。v4/外部堆终态勿重启。当前无完整控制器HLS top/综合/RTL/物理实现证据；下一步需把邻接、站点约束/代价快照接为硬件Provider，解决全规模key外部存储布局，再接HLS顶层。完整协商/动态占用、全部特殊资源与实际板卡DDR/HBM/功耗仍未完成。
- 本轮为progress：边界/C++14/接口验证、完整运行副本与独立审计器落地；项目check和smoke通过。前轮状态回复核实具体live进程，为verified wait。完整目标保持active，不把CPU控制器或小组件通过当作完整实验完成。

## 最新：有界标签记录替换vector，CPU组件与搜索接入通过

- 新`hardware/vitis/search_label_records.hpp`提供显式十uint64字ABI：cost,parent,root,dst,tile,pip,up,down,attr,dir；key由既有完整state索引按相同label ID持有，不重复存动态Normalized。记录append/read/cost/improve均有界，失败不提交；只接受严格更小cost，父记录cost必须更小；validate_path检查完整父链，不假设parent ID早于child ID。
- 3容量×20000随机操作与独立vector记录oracle通过：2720新增、1402改进、55878拒绝；每步比较全记录、随机路径、失败原子性与guard。边界含更晚创建的父标签、最大有效cost、零/max拒绝、越界parent、伪造环、非法flag/edge宽度/count和输出不变。g++14严格警告+ASAN/UBSAN通过，日志`results/search_label_records_component_20261024_v1.log`。
- `src/native/search_record_adapter.hpp`和checked transform在独立搜索中删除labels vector，改为相同十字记录数组与既有bounded key数组；每次弹出仅解码本地native视图供旧回调，找到目标先验证父链再回溯。12个原native搜索场景差分、ASAN/UBSAN通过。初次编译曾因一处misleading-indentation失败，已修正；最终测试24.020s通过。证据`results/search_label_records_component_20261024_v1.json`。
- 已准备但**未启动**`data/derived/label_records_router_20261024_v1`，严格生产编译通过。待label_index完整全量审计成功后运行`python3 scripts/label_records_router_pipeline.py`。自动后继`check_label_records_router.py`比较完整原参考结果，并验证record/index/heap的search数相同、record appends=index inserts、appends+improvements=heap pushes、记录峰值=索引峰值、validated_paths=参考全部found结果数。期望`results/label_records_router_audit_20261024_v1.json`。plan及代码已冻结。
- 当前原external全量owner3364284/exec67537继续：worker1/3/0完成，worker2 compact/direct PID3366351仍live。先等其自动审计，再启动已准备的`label_index_router_pipeline.py`，通过后才启动records这一层；不要跳过全量验证或重复提交。旧HLS v2 owner2468333/exec16547仍在综合，未替换/重启。
- 本轮为progress：真实存储组件与独立搜索接入完成CPU验证、生产副本与后续审计已准备。尚无记录组件HLS/RTL证据，也未完成全部搜索控制器、临时站点处理/输出/邻接/占用/协商硬件化和板卡实验；完整目标保持active。

## 最新：有界堆全量与外部堆RTL均审计通过；标签索引副本已准备

- 原heap四条件完整1062网×两批独立审计完成：`results/search_heap_router_audit_20261024_v1.json` SHA `ac033729979514d242dc8546b66d87feca61673ff96923a1216a6e029621bc21`。owner2550136/exec45419终态complete，勿重启。每批16836 searches、298041785 pushes、165864259 pops、0 failures、peak73388。独立审计逐份完整raw比较路由树/站点/协商/搜索结果，本轮重新核验receipt/log及13项非raw绑定，未再次读全部巨大raw。
- 外部堆HLS owner2992261/exec69195终态complete，自动独立审计`results/search_heap_external_audit_20261024_v1.json` SHA `51b7168c483ff09653b5a17211de2cddc0a6bbf06b95a6ff0b2d0ecfca1f296d`；15项artifact及audit_receipt重新核验。七RTL事务cycles=2103850/5536915/5899882/349165/212/212/212。3.650ns综合估计、BRAM0/FF19672/LUT45460/DSP0/URAM0；仅AXI模型+预置有效大堆，不是全部真实搜索操作回放、物理时序或板卡测量。勿重启已终态flow。
- 已启动external三字布局堆完整路由：owner3364284 / exec67537；bundle `data/derived/external_heap_router_20261024_v1`。CSR/direct PID3366345 CPU122；CSR/expanded PID3366346 CPU124；compact/direct PID3366351 CPU125；compact/expanded PID3366349 CPU126。四个原进程均live，自动后继`check_external_heap_router.py`，最终`results/external_heap_router_audit_20261024_v1.json`。原1023项自动流水化v2 owner2468333/exec16547仍live综合，未判死/重启。
- 新`search_label_index.hpp`：规范node+完整归一化site state作为key，哈希仅寻址、同桶逐字段精确比较，线性探测有界；find不写，get_or_insert按插入顺序给label ID，显式容量/非法状态失败且不修改数组/count/id。epoch隔离每次查询，回绕必须清slots；单控制器调用，动态占用仍按物理规范节点。尚无该索引HLS top/综合/RTL，不宣称完整FPGA搜索。
- 三种slot/label容量共60000随机场景（各find+get_or_insert），STL完整规范key oracle、碰撞/探测回绕/满表重复查找/零掩码/同node不同state/同state不同node/非法输入/epoch回绕/live tag错误通过；严格g++17及ASAN/UBSAN通过。另C++14 helper编译与find/insert运行通过。`test_label_index_integration.py`12搜索场景对原native结果、根初始化/扩展两种容量失败通过，ASAN/UBSAN通过。证据`results/search_label_index_component_20261024_v2.json`。
- 已准备但**未启动**`data/derived/label_index_router_20261024_v1`：继承external堆，仅替换搜索ids map为上述完整key索引，成本/父边label和站点/协商仍native。key容量32 signals/16 bits/8 values，当前两份14实例fixture需求并集18/11/7，固定954字段不存入路径key；label524288/slots1048576为待全量验证的显式试验上限。CPU Key sizeof608字节不是AXI格式承诺。plan及代码已冻结。
- 待external完整审计成功，再运行`python3 scripts/label_index_router_pipeline.py`。脚本前置门控external审计，执行四条件×两批、自动完整结果比较并验证LABEL_COUNTERS中的全部搜索调用/容量/探测/站点字段峰值，终态`results/label_index_router_audit_20261024_v1.json`。不要绕过原owner或替换正在运行的源码。
- 本轮为progress：两个终态审计核对、新全量任务提交、索引实现/差分测试/真实副本准备。完整目标active，继续标签状态与完整控制器硬件化、特殊资源及板卡证据。

## 最新：131072项AXI外部堆已综合、RTL运行；完整路由副本已准备

- `search_heap_external.hpp`用显式三个uint64字(cost,serial,label)读写调用者存储，避免AXI struct padding，容量131072；保持有界堆排序/失败不变性。`search_heap_external_top.cpp`四个AXI内存接口，meta=[count,status]跨调用保留；非法count/operations拒绝，空/满/未知opcode返回失败response。命令loop PIPELINE off。只是组件验证ABI，完整控制器应直接调用helper，不能把它解读成每搜索操作一次host launch。
- `test_search_heap_external_top.cpp`七场景：空队列、73388预置有效堆、跨调用延续、131072满队列、非法131073计数、4097操作拒绝、零操作。每次检查全部活动条目的multiset和堆序，与独立STL队列一致；检查response、元数据、guard和未访问尾部。g++14严格警告及ASAN/UBSAN通过；HLS Csim也通过。错误拒绝两场景不能据此宣称验证所有非法指针/别名输入，调用方需提供足量独立buffers。
- 外部堆HLS owner2992261 / exec69195，child2992262，taskset CPU120；`data/derived/search_heap_external_20261024_v1/state.json`。综合完成、XSim活跃，最新完成1/7 RTL transaction。结束后pipeline自动运行`check_search_heap_external.py`，期望报告`results/search_heap_external_audit_20261024_v1.json`。审计解析器10类坏证据拒绝通过。此前1023项v4已终态勿重启；v2 owner2468333/exec16547仍在综合，不据等待时长判死。
- 已准备`data/derived/external_heap_router_20261024_v1`：从冻结前一完整路由副本复制，仅将queue存储换为相同external helper/三字布局并改容量131072，其余搜索/站点/协商原样。原输入/参考/二进制/生成源码均绑定；12场景与原native搜索差分、ASAN/UBSAN通过（driver_tests.json）。这是CPU host存储接入，不是板卡运行。
- **新external完整路由尚未启动。** 原heap四条件owner2550136/exec45419已完成worker1/3/0，worker2 compact/direct PID2551393仍运行，最终自动审计未出。待`results/search_heap_router_audit_20261024_v1.json`成功后运行`python3 scripts/external_heap_router_pipeline.py`；该脚本有前置审计门控，执行相同四条件×两批并自动生成`results/external_heap_router_audit_20261024_v1.json`。勿重复启动前一pipeline。
- 阶段证据`results/search_heap_external_stage_20261024_v1.json`。前轮、本轮均为progress；完整目标active。下一步核实原终态/外部堆RTL，启动已准备完整路由验证，并继续有界label索引和站点状态接入。完整FPGA控制器/板卡/特殊资源证据仍缺。

## 最新终态：堆v4 Csim/综合/RTL独立审计通过

- `results/search_heap_hls_audit_20261024_v4.json` SHA `eeaf4b8e3d3b49ba64f4b0b3a914b079e6ea8c24ba86bab669cd035d7646200f`，status `heap_component_csim_synthesis_rtl_independently_verified`；14项artifact绑定重新核验。v4 owner2820096 / exec90044已退出，勿重启。两次完整4096操作RTL transaction为 **545717 / 445222 cycles**，Csim及RTL前/后黄金日志均一致。综合估计3.650ns、BRAM_18K12/FF4976/LUT7006/DSP0/URAM0。
- 这只证明1023项堆组件在测试ABI下通过；未做该组件OOC实现、外部存储或完整路由FPGA测量。保留less函数签名复制、AXI同步低有效复位、XSIM环境变量warning。不能用综合估计周期当物理时序闭合或板卡性能。
- 原v2 owner2468333/exec16547仍活跃综合，未获最终报告，不据此做v4相对性能结论。v3脚本testbench路径失败记录保留；v4只关闭外层命令loop pipeline，原heap算法和测试输入未改。
- 四条件真实路由首批现在全部报告相同计数：16836 searches、298041785 pushes、165864259 pops、0 failures、peak73388。owner2550136/exec45419继续执行驻留批并将自动完整审计；这些日志计数仍不能替代终态等价结果。
- 下一步除检查原运行终态外，需要支持至少已观察73388项的硬件堆存储接口（当前24字节entry对应1761312字节有效载荷，未含总线对齐/其它状态），不能沿用1023项小组件容量；继续将已CPU验证的有界站点状态接入标签存储/索引及完整搜索。完整实验目标保持active。

## 最新：有界站点状态CPU组件通过，堆v4已综合并进入RTL仿真

- 新`hardware/vitis/search_site_state.hpp`：调用者提供原始数组，编译期容量的有序信号/配置位/类别数组；normalize、merge支持重复合并、冲突检测、显式capacity_exhausted/unverified/invalid，失败不修改输出，merge允许输出别名。保留零掩码字段与物理资源ID。无STL/动态内存/递归/系统调用，仅组件源码，尚无HLS top/综合/完整路由接入。
- `tests/test_search_site_state.cpp`以冻结native normalize/merge为oracle，4容量×10000随机用例、边界、无效count/排序/掩码、raw上限空指针提前拒绝、后阶段冲突原子性、双向输出别名通过；ASAN/UBSAN及严格编译通过。另C++14编译/运行空merge通过。CSR/compact全部14项站点需求及固定配置合并检查通过。原1100条fixed bit记录归一化为954字段；不能以32项随机测试容量代替全局固定配置容量。证据`results/search_site_state_component_20261024_v1.json`和log。
- 原四条件owner2550136/exec45419继续。最新CSR/direct、CSR/expanded、compact/expanded首批均报告：16836 searches、298041785 pushes、165864259 pops、0 failures、peak73388；compact/direct尚无首批计数。仅活跃日志观察，完整raw审计未完成；峰值已超过1023项组件容量，后续完整硬件需按真实峰值规划存储。勿重启原进程或据局部计数宣称完整等价。
- HLS v2 owner2468333/exec16547 CPU121仍综合。日志明确外层命令loop自动pipeline，间接展开push/pop的31层循环；pop II187。新增独立单因素对照仅在命令loop内加PIPELINE off，使用`search_heap_top_v3.cpp`。v3因脚本把testbench文件名也改错而失败，记录保留；修正后的v4 owner2820096/exec90044、CPU120，bundle`data/derived/search_heap_hls_20261024_v4`，Csim通过、综合完成，已进入RTL协同仿真。综合估计3.650ns、BRAM_18K12/FF4976/LUT7006/DSP0/URAM0，尚未经独立终态审计或物理实现，不宣称优于v2。
- v2/v4完成后分别运行`check_search_heap_hls.py --bundle data/derived/search_heap_hls_20261024_vN --output results/search_heap_hls_audit_20261024_vN.json`（N替换2或4）。原full-router pipeline自动审计保持。阶段快照`results/search_site_state_stage_20261024_v1.json`。
- 本轮为progress：新增可用状态组件并差分测试、获得真实队列容量观察、提交HLS单因素对照并获得综合报告。下一步核验原运行终态，规划有界标签索引/状态存储并接完整搜索；保留完整目标active。

## 最新：有界堆接入真实搜索，四条件全量验证已启动

- 旧HLS v1因`open_project`不接受绝对工程名失败，记录保留；新`run_search_heap_v2.tcl`先cd父目录再以basename建工程。v2 owner2468333 / exec16547，HLS进程2468371，CPU121；`data/derived/search_heap_hls_20261024_v2/state.json`。Csim两批4096操作已通过，最新仍综合；pop调度报告II187，尚无最终综合/RTL或性能结论。不要重复启动。
- 独立复制所有native头文件及runtime，仅将STL队列替换为同一`search_heap.hpp`有界堆；搜索仍保留labels/site map、占用、协商和所有异常语义。CPU测试适配器用host分配1048576项存储，统计每批push/pop/峰值/失败；这不是1023项HLS顶层的完整工作负载验证。溢出返回capacity_exhausted，runtime拒绝出具成功批结果，不静默截断。
- `tests/test_search_heap_integration.py`：12场景与原STL搜索比较、初始化/扩展两种溢出和小容量未知语义保持；g++17严格警告、ASAN/UBSAN通过。HLS审计解析器2测试（10类坏证据拒绝）通过；项目check通过。证据`results/search_heap_integration_stage_20261024_v1.json`。
- 四条件owner2550136 / exec45419：`scripts/search_heap_router_pipeline.py`，bundle`data/derived/search_heap_router_20261024_v1`。CSR/direct CPU122 PID2551385；CSR/expanded CPU124 PID2551388；compact/direct CPU125 PID2551393；compact/expanded CPU126 PID2551391。每条件两批完整1062网，原参数cache4096/iterations80/budget200000/cap8。最新均live；峰值与完整等价尚未知。plan绑定源码/输入/参考/二进制，此后冻结，不编辑或重启原owner。
- pipeline结束后自动调用`check_search_heap_router.py`，逐份完整raw比较所有路由树、站点需求、逐轮冲突及搜索结果，仅排除六项度量；验证实际每次搜索均调用堆、两批计数相同和无溢出。期望终态`results/search_heap_router_audit_20261024_v1.json`；不能用部分进度代替该审计。
- HLS v2完成后独立执行：`python3 scripts/check_search_heap_hls.py --bundle data/derived/search_heap_hls_20261024_v2 --output results/search_heap_hls_audit_20261024_v2.json`。核对Csim/RTL黄金日志、两个transaction、源/RTL摘要、器件/时钟和资源；未测试operations>4096的早退路径。尚未配置自动后继审计，后续会话需核实原owner终态后运行。
- 前轮只答状态为no progress；本轮修复流程、实现CPU接入、通过新测试并提交全量验证，为progress。下一步依据真实队列峰值确定硬件存储，再实现有界label/配置状态与完整搜索控制；完整目标保持active，板卡与完整特殊资源证据仍缺。以下旧快照按时间解读。

## 最新：完整FPGA搜索开始迁移优先队列组件

- `hardware/vitis/search_heap.hpp`新增调用者提供存储的有界最小堆，精确保留原`site_search.hpp`的(cost, serial, label)排序；保留stale entries供搜索控制器按label cost过滤。push/pop无动态内存、递归或STL容器，循环上限31。容量/无效count失败不修改存储与count；控制器需显式报告capacity_exhausted，不能当no_path。
- `tests/test_search_heap.cpp`用独立STL tuple priority_queue对照600000随机操作，覆盖6种容量、排序同值、uint64最大值、空/满/非法count及guard；g++17 Wall/Wextra/Werror及ASAN/UBSAN通过。证据`results/search_heap_component_20261024_v1.json`绑定源码与测试。
- **仅组件CPU等价检查完成**，尚未综合、接完整搜索或获得RTL/板卡证据。下一步建立HLS top并综合，独立副本替换原搜索队列后验证真实全部查询；继续实现有界label/站点状态、占用与协商。原冻结基线不修改，完整目标保持active。

## 最新：站点路由63次统计及独立审计完成

- `results/native_site_runtime_statistics_audit_20261023_v1.json` 状态 `complete_site_runtime_matrix_independently_audited`，63/63完成，9条件各7次；pipeline为complete。报告SHA `1e01f27fe321ae8d7d82503f07fac1b482948d10f0bd27a813d20dc05c396051` 与pipeline一致。原owner1739121及driver3457381已退出，不重启。四组已提交CPU统计均已终态，不再依据下方历史PID等待。
- 本次核对pipeline的5项文件绑定及审计的254项非raw绑定；审计包含317项artifact绑定，独立审计已逐份重读63份raw、检查各两批1062查询及完整参考语义。本次收尾没有再次重读63份大型raw，不能称为重新全量审计。
- cache=0/64/4096时，compact/direct相对同repeat、同capacity的CSR/direct进程耗时比中位数为 **1.481497/1.457522/1.417052**；即该CPU实验中压缩直接执行更慢。compact/expanded相应比值 **0.993132/0.931596/0.866275**；expanded绕过LRU，其capacity标签只是重复对照，不能解读为expanded缓存收益。
- cache=0首次路由耗时中位数CSR/direct **448.283s**、compact/direct **671.222s**、compact/expanded **445.654s**；两批完整进程wall中位数依次 **937.479s/1389.108s/931.040s**。保留全部观测，包括expanded capacity64 repeat0耗时比1.766313，未剔除异常值。共享主机/页缓存未控制，不宣称显著性或FPGA加速。
- 解释及完整配对比值：`results/native_site_runtime_interpretation_20261024_v1.json`。范围仍为14个已物理测试site实例；转换在native计时外，expanded展开计入准备时间，驻留批重置占用/history，峰值包含trace。完整特殊资源语义、真实板卡DDR/HBM/功耗、完整FPGA搜索仍未完成，完整目标保持active。

## 最新：模板共享粒度35次统计及独立审计完成

- `results/template_scope_runtime_statistics_audit_20261023_v1.json` 状态 `complete_scope_runtime_matrix_independently_audited`，35/35完成，5条件各7次；pipeline状态complete。审计报告SHA `3e735b14ddd82d9255cfc9926076bf72fd6575ab1e576c49093d6e632de4a93c` 与pipeline一致。已重新核对pipeline的7项文件绑定及统计report绑定；本次未重读全部大型raw，不把终态摘要核对称为全量重审。原owner2703564及审计3073464已退出，不重启。
- 7配对块的process wall/CSR耗时比中位数：global **1.427734**、span16 **1.433213**、span4 **1.430644**、span1 **1.447702**。各条件process wall中位数依次为CSR **1067.247s**、global **1508.341s**、span16 **1518.782s**、span4 **1511.069s**、span1 **1529.024s**。全部压缩条件在该CPU实验中更慢；这些描述统计不证明各压缩条件间差异显著。
- 图像大小CSR/global/span16/span4/span1：98255808/93507968/93946944/96954624/107368384字节。缩小共享范围没有显示速度收益，span1图像还大于CSR；保留global为本次压缩容量参照，不据此宣称直接执行加速。
- 范围：1062查询、14个已物理测试site实例、direct执行、cache4096、每worker两批完整路由、批间占用和history重置、固定CPU126。只改变字典共享范围，未重训模板；排除图像生成、器件采集和bank训练。共享主机与页缓存未控制，峰值含trace，不能当作纯图内存或板卡实测。
- 站点路由统计最近核实51/63退出码0，第52次进程4044004仍活跃，driver3457381；最终审计尚无。完整实验目标保持active，真实板卡测量和完整特殊资源语义仍未完成。以下旧进度记录保留为历史。

## 最新：端到端21次统计及最终审计完成

- `results/source_to_route_statistics_audit_20261023_v1.json` 状态 `complete_source_to_route_statistics_audited`，21次完成，3条件各7次；pipeline状态complete。报告SHA **b661a32d6e9c1011276b288daba60465616b438105b578c559fd7b6dcc8d5f95** 与pipeline记录重新核对一致；block006报告3/3通过。本次未重新读取全部大型raw绑定，勿将报告摘要核对描述为全量重审。原source统计驱动3986466及最后block审计32154已退出，不重启。
- 已捕获TSV→重新生成图像/输入→两批完整路由的application wall中位数：CSR/direct **1138.353s**、compact/expanded **1020.230s**、compact/direct **1623.146s**。每个repeat配对compact/expanded对CSR耗时比的中位数 **0.895203**（耗时减少10.48%）；compact/direct比 **1.423974**（耗时增加42.40%）。这是该CPU工作负载的描述统计，不是FPGA加速或显著性证明。
- 计时含转换、中间验证、导出和两批路由；不含Vivado采集、bank训练、板卡传输及物理回读。完整进程wall另含预检/后审；共享主机、page cache和缓冲写入未受控。父进程转换峰值与子进程峰值不得相加，子进程RUSAGE可能继承fork前峰值，不能据此声称独立native内存优势。
- 剩余site与template原驱动3457381/2458493仍在运行；本次观察正常退出25/63与16/35，原生子进程61127/148852存活。完整特殊资源语义、板卡DDR/HBM/功耗、完整FPGA搜索及剩余统计仍未完成；完整目标保持active。以下较早状态为历史快照。

## 最新：旧规范节点统计63次独立审计完成

- `results/native_runtime_statistics_audit_20261023_v1.json` 已生成，SHA **3643468540902ddbb887e8bdce861af085ab2e8127ab9ddd2225aae9dfd03494**。原后继270441及审计3786562已退出；state为complete/all63_independently_audited，receipt exit0，报告及日志摘要已核对。独立审计报告包含319项artifact绑定，确认63次完整raw工作负载及63条提交命令；本次收尾未再次重读所有大raw文件。
- 9条件各7次。cache=0时首次路由中位数：CSR/direct 134.922s，compact/direct 330.658s，compact/expanded 129.102s。只能作为该旧CPU模型的描述统计；共享主机/page cache未受控，不能推断显著性或FPGA加速。
- **旧canonical-only物理站点验证失败**；不得与后续site模型混合，不证明合法物理路由。转换不含在native计时内；进程峰值含trace，不含Python审计父进程。
- 其余原统计继续：最近site15/63、source12/21、template8/35正常退出。完整目标仍未完成，保留原owner推进及后继审计，不重启已完成63次。

## 最新：真实known miss加权三核RTL全部终态并独立审计

- owner1283819/exec28638已终态complete/independently_audited，全部CSR/compact/tile_cache 6批完成，勿重启。`results/vitis_miss_weighted_audit_20261023_v1.json` SHA **473b0d60735c7e3762db0096172d754733178137ce672dd0e22d4f71c55fc5e7**；audit_receipt exit0及log/report摘要核对，68个报告绑定重新hash通过。两份黄金日志、每批transaction及syn RTL身份均一致。
- 六批128请求CSR周期88279/86124/85508/84654/87468/84388；原compact3521849/3302610/3290486/3189182/3466032/3146104；tile-cache2837669/2655180/2640494/2583654/2782398/2530888。候选每批相对compact周期减少18.987%..19.754%，但仍为CSR29.991..32.144倍。768请求样本合计CSR516421/compact19916263/tile-cache16030283；候选较compact-19.5116%，仍为CSR31.0411倍。
- 解释`results/vitis_miss_weighted_interpretation_20261023_v1.json`。这些是实际known miss分布有放回抽样的RTL周期；3seed×首次/驻留，每批128，重复保留。排除hit/unknown，无真实时间顺序，不能外推完整router时延、主机逐行launch成本或板端DDR/HBM流量。默认核不提升；局部缓存优化有效但未改变CSR明显占优的样本结论。
- OOC已另行证明内部200MHz时序通过，仍无平台外部AXI/板卡证据。四组原CPU统计尚未终态，最近canonical55/63、site11/63、source10/21、template5/35正常退出；继续原owner及终态审计链。CPU121/122/123/124已随上述硬件实验释放，用前再核实进程。
- 前轮verified wait，本轮新终态复核/解释为progress。完整目标保持active：正式重复统计、完整特殊资源语义、平台板卡DDR/HBM/功耗和完整FPGA搜索仍缺。

## 最新：tile-cache OOC v2 终态通过内部时序/布线/DRC审计

- owner1187652/exec39950已结束，勿重启。`data/derived/vitis_tile_cache_ooc_20261023_v2/audit_receipt.json` exit0，报告/log摘要一致；pipeline保留complete/await_independent_report是冻结设计，最终权威为audit_receipt。
- `results/vitis_tile_cache_ooc_audit_20261023_v2.json` SHA **ee645e2db9b318714eccc0d6bbfcfc49e4067d36ef54265d9a1dcccb1af7d259**。33项绑定重新核验；与原OOC55项绑定同时复核。5ns/200MHz，37174 setup/hold endpoints，WNS0.534ns、WHS0.040ns，TNS/THS0，内部无未约束端点/no_clock0；24444/24444可布线nets完成，routing errors0、DRC0。
- Postroute LUT12444、FF15416、BRAM34、DSP0、URAM0；较原compact LUT12339/FF15285分别+105/+131，BRAM不变。原WNS0.561→0.534ns。比较证据`results/vitis_tile_cache_ooc_comparison_20261023_v2.json`。外部612输入/314输出无delay，不能称平台AXI或板端时序闭合，更不能称完整router加速。默认核未替换，v1失败记录保留。
- 加权RTL owner1283819/exec28638继续，CSR六批已完成并核对两份golden日志、RTL身份和transaction：88279/86124/85508/84654/87468/84388 cycles。阶段证据`results/vitis_miss_weighted_csr_stage_20261023_v1.json`，只CSR不能替代最终三核审计。compact/tile-cache仍运行，最近1/6批；CPU122已随OOC释放，其他121/123/124按原owner状态确认再用。
- 最近正式统计正常退出canonical51/63、site10/63、source9/21、template4/35，尚无终态结论。前轮verified wait，本轮终态审计复核/比较为progress。完整目标仍active。

## 最新补充：加权RTL独立审计器故障注入回归通过

- `tests/test_vitis_miss_weighted_audit.py`使用临时合成证据，验证正例及12类错误拒绝（缺marker、ERROR、黄金计数/完成标记缺失、摘要篡改、Verilog Fail、transaction索引/零周期/重复、RTL改变、冻结manifest改变、非零退出）。不修改运行中的源或bundle。连同抽样/重复编码测试共5项通过；证据`results/vitis_miss_weighted_auditor_tests_20261023_v1.json`及log。
- 已重新确认weighted owner1283819、OOC owner1187652和原四统计owner/driver及canonical后继270441均存活。weighted进入仿真编译，OOC仍综合；尚无新终态审计。上一轮progress；本轮新增审计故障覆盖为progress。等待原owner完成，不重复启动。

## 最新：真实 known miss 加权匹配 RTL 对照已启动

- `scripts/prepare_vitis_miss_weighted.py`读取已独立审计首次/驻留两份完整canonical访问TSV，摘要与逐行计数/度数/汇总全部核对。按每节点known miss整数权重、有放回抽样：每分布3个独立固定seed、每批128请求，合计768请求；顺序与重复均保留，最后一批127个不同节点。其余5批128个不同节点；仅最后一批抽中1个degree12，其余degree0..8，明确小样本可能漏稀有行。
- bundle `data/derived/vitis_miss_weighted_fixtures_20261023_v1/plan.json`；跨CSR/compact规范8字段/属性/方向/多重边一致，分别保留各表示本地ID。序列化结果逐请求验证，重复节点不转为字典去重。3项单测覆盖零权重/复现/分布、异常权重、重复payload与12类字节/截断破坏及顺序错误拒绝。项目check通过。prepare及plan绑定输入已冻结。
- 唯一owner **1283819** / exec **28638**：`scripts/vitis_miss_weighted_pipeline.py`，状态`data/derived/vitis_miss_weighted_cosim_20261023_v1/state.json`。CSR child1285746 CPU121；compact child1286328 CPU123；tile-cache child1285862 CPU124。均独立复制原已审计工程、保持syn RTL，不改默认核。新审计器`scripts/check_vitis_miss_weighted.py`自动核对各6批两份黄金日志、transaction周期、RTL身份，再输出`results/vitis_miss_weighted_audit_20261023_v1.json`。本次提交前曾因旧baseline审计字段名artifacts而在创建OUT前退出，已兼容该实际格式后提交；无重复worker。运行plan及脚本冻结。
- 当前仅启动，无新RTL周期结论。采样条件是known miss，排除hit/unknown；无原访问时间顺序，不冒充trace或全router时延。128请求批量调用不同于现direct逐行调用，不据此推算host launch/PCIe开销。存储仍HLS AXI模型。
- tile-cache OOC v2 owner1187652/exec39950仍活跃，已通过IP导出并进入Vivado synth_1，尚无postroute结论。上一轮与本轮均progress，完整目标仍active。

## 最新：tile-cache OOC v2 已启动，修复导出副本缺失目录

- v1 `data/derived/vitis_tile_cache_ooc_20261023_v1`已失败并保留：HLS详细日志报告找不到`solution/impl/verilog/graph_accel.v`，尚未进入布局布线。原因是已审计cosim副本创建时排除了impl目录。
- v2使用独立脚本`scripts/vitis_tile_cache_ooc_pipeline_v2.py`和审计器`scripts/check_vitis_tile_cache_ooc_v2.py`；复制原cosim工程后，从同一候选原综合工程补齐47个impl文件。启动前确认原综合与已审计cosim的19个syn RTL完全一致；全部staging文件纳入plan摘要绑定，逐文件验证副本。不改原核、原工程或v1记录。
- 唯一owner **1187652** / child **1188569** / exec **39950** / CPU122；状态`data/derived/vitis_tile_cache_ooc_20261023_v2/{pipeline,compact.state}.json`，工程`build/vitis_graph_compact_tile_cache_ooc_20261023_v2`。运行后自动独立审计内部200MHz时序、布线、DRC、资源及RTL身份，期望`results/vitis_tile_cache_ooc_audit_20261023_v2.json`。这些新增脚本及plan.files已冻结，不重提。
- 当前只是实现已启动，尚无新postroute结论。项目check通过；真实miss加权RTL请求尚未启动。OOC不证明平台外部AXI时序或板端收益。完整目标仍active。本轮progress；上一问答轮为核实原统计进程存活的verified wait。

## 最新：分层基线已独立审计，完整路由XRT接口完成离线准备

## 最新：完整接口路由、真实访问分布与tile-cache RTL均已独立核验

- **三个原owner均终态，勿重启**：kernel_router2924311/exec26410，access113851/exec58200，tile-cache4065010/exec69036。`results/router_and_tile_cache_terminal_stage_20261023_v1.json`复核对应18/8/26及比较27个绑定，并交叉验证真实访问计数与两模式kernel调用次数。
- `results/kernel_router_integration_audit_20261023_v1.json` SHA **5552e5b3b6b590fc95b1da6df3248567b2363d8701fb07c7066c1eaea3c06631**：CSR/compact × direct/expanded四条件，各首次/驻留两个完整1062网批次，全部路径、边属性、站点需求、轮次搜索结果与冻结原生参考一致。direct每批kernel_calls=136095859/136095833，与独立访问诊断miss完全相同；expanded运行期calls0，准备阶段通过核解码全图。只证明CPU Vitis-ABI C模型集成，时延含provider/guard、n=1，不作FPGA加速。真实XRT运行前的Cmodel门槛已满足，但仍缺平台/板卡。
- `results/router_access_profile_audit_20261023_v1.json` SHA **7e655f37d265d5bfe718bb8fcc139e12a1b615fe2a6b3219aa7581bc93100d3f**，完整两批已审计。每批165847423次neighbors，141876005 known、23971418 unknown；221484个不同规范节点。hits5780146/5780172，miss136095859/136095833，known hit率约4.074%。known miss中92.0165%来自degree1..8，7.7838%空行，0.19965%degree9..63。**degree>=64实际访问为0**。原高出度排序收益不能代表此工作负载。`results/router_access_interpretation_20261023_v1.json`保留解释；其中“尚未交叉核对Cmodel”的历史限制已由上述terminal_stage解除。
- `results/vitis_tile_cache_cosim_audit_20261023_v1.json` SHA **c77f5d99da0afc0e197224e4d469113795730aecbf660968d6960ec308fc428a**；匹配比较`results/vitis_tile_cache_comparison_20261023_v1.json` SHA **9a0a09c3a5570a2905badb3de06e14d718b7a20941b93263b8e0b5b1713e64da**。全部12批两份黄金日志与RTL身份通过。非空分层相对原compact周期-13.903%..-23.558%，uniform64 2108498→1662934（-21.132%），empty/unknown/wrong-mode不变；capacity负例单独保留。
- **改善仍不是胜过CSR**：degree2/4/6-8样本新核分别仍慢15.50/24.20/33.65倍，uniform64慢36.87倍。每层2节点及均匀64请求不能作实际router估计。缓存候选尚无postroute/板端证据，默认核不变；归并候选不提升。
- 下一步：用已审计真实known miss权重构造可复现、跨表示规范身份一致的匹配RTL请求（保留重复次数；无时间顺序，不能冒充访问trace或总体时延）；候选已经有低度数正收益，可在独立副本做OOC时序/资源核验。**尚未启动这些后续实验**，先查目录避免重复。136M次逐行调用的主机成本必须单独评估，不由CPU/RTL推算板时延。
- 原正式统计仍运行：最近canonical48/63、site10/63、source8/21、template4/35为正常退出数，最终审计由原队列负责（canonical独立后继270441/exec39921）。CPU121/122/123/124已从上述实验释放，后续用前再次查实际进程。
- 前若干轮为verified wait，本轮新终态证据核验/交叉验证为progress。目标active：完整特殊资源语义、重复统计终态、真实平台与板卡DDR/HBM/功耗、完整FPGA搜索仍未完成。

## 历史：旧63次统计已配置唯一终态独立审计

原canonical统计queue3591840/driver4146936当前仍运行，最近44/63正常退出；原脚本终态只停在await_independent_statistics_audit。现已补唯一后继owner **270441** / exec **39921**：`scripts/native_runtime_final_audit_pipeline.py`，状态`data/derived/native_runtime_final_audit_20261023_v1/state.json`，当前wait_original_statistics。它核对原owner的/proc start_ticks/命令身份和成功终态及report摘要，然后在原CPU0空出后运行完整63次独立审计，不重启求解、不改原脚本。

新`check_native_runtime_bound.py`复用冻结原auditor的完整raw/矩阵/统计验证，另核对每worker实际提交的binary/image/fixture/cache/limits/execution与owner/child。14类错误拒绝通过；旧raw没有execution标签，明确保留该格式限制，不伪造运行记录。**旧canonical物理站点验证失败，不能将这条统计当后续site模型或实板结论。** 新队列plan.files及新增auditor/测试均冻结；期望终态`results/native_runtime_statistics_audit_20261023_v1.json`。证据`results/native_runtime_final_audit_stage_20261023_v1.json`，项目check通过。本轮progress；完整目标仍active。

原site8/63、template3/35，source原队列继续；tile-cache RTL4065010、完整Cmodel2924311及访问profile113851/117200均确认活跃，无重提。其后继审计已各自配置。

## 历史：完整路由访问分布诊断已启动

- 新`src/native/router_access_profile.hpp`只观察实际neighbors调用的规范node、已知/未知、cache hit/miss及度数，每批重置计数，保持图/cache驻留。未知邻接不会把旧out向量计作边；空邻接仍是已知行。输出每批完整274732节点TSV，包括未访问节点，不是只保留热门节点。
- `scripts/prepare_router_access_profile.py`生成`data/derived/router_access_profile_build_20261023_v1/site_runtime.cpp`及`runtime.diff`：搜索、排序、占用、站点语义和完整原始输出保持，唯一算法外变化是计数/写文件；该诊断只跑compact/direct/cache4096，不用计时作性能比较。g++17 O2 Wall/Wextra/Werror通过，实际计数器ASAN/UBSAN通过8种异常拒绝及重置检查。
- 独立`check_router_access_profile.py`从原AGR解析每规范节点度数（含remove/add/fallback），核对每行访问守恒、未知行、未访问行、原生hit/miss总数及全部search expanded总和。解析器3项测试通过，含18种篡改/计数错误拒绝；真实274732节点、53759未知、1100754边、max642度一致。最终还必须重读全部两批raw JSON并与原compact完整1062网参考比较所有路径/属性/站点需求/轮次搜索结果，当前尚未完成。
- 唯一运行owner **113851** / child **117200** / exec **58200** / CPU **123**：`scripts/router_access_profile_pipeline.py`；状态`data/derived/router_access_profile_run_20261023_v1/state.json`。所有1062网、首次/驻留两批、cache4096、原80轮/200000预算/cap8；原owner自动独立审计，期望`results/router_access_profile_audit_20261023_v1.json`。**prepare/run plan.files/generated以及新增header、脚本、测试和二进制均冻结，勿修改或重提。**
- `results/router_access_profile_stage_20261023_v1.json`绑定准备、回归、启动及真实/proc快照；103个运行依赖已核验。`results/project_check_after_access_profile_20261023_v1.log`通过。计数是CPU真实路由访问，不能称板端AXI流量，也不保留访问顺序；诊断运行额外开销不混入原统计。
- 原tile-cache RTL 4065010/4065711/exec69036/CPU121继续（最近5/12），其余完整router Cmodel2924311、direct3371574/3373595及四条统计原owner继续，不重启。下一步先验原RTL、Cmodel和访问分布终态，再据真实miss权重选择匹配请求，而非从均匀小样本推断router总收益。
- 本轮为progress，前轮亦progress。完整目标仍active：全特殊资源语义、正式重复统计、平台/板卡DDR/HBM/功耗和完整FPGA搜索未完成。

## 历史：单项 tile 查找缓存已通过全图验证与综合，匹配 RTL 对照运行中

- 新实验只在每个节点的 decode 内保存最近一次成功的 tile 坐标→tile ID；模板规则及增加例外共用该局部缓存，失败查找使缓存失效，每节点重新初始化。规范节点、别名、属性、方向、重复边、插入排序、ABI和时钟均保持；未叠加归并排序，动态占用不进入缓存。
- `data/derived/vitis_tile_cache_kernel_20261023_v1/plan.json`与`algorithm.diff`冻结；`scripts/prepare_vitis_tile_cache.py`、`hardware/vitis/test_tile_cache.cpp`及全部绑定文件冻结。773项真实helper比较/边界/失败/先前错误/新图重置检查通过ASAN+UBSAN。未插桩候选完整+分层23批黄金通过；两份插桩代码各完整11批、旧RTL3批、新分层12批黄金通过。基线计数逐项复现旧profile，非tile计数逐项相同。
- `data/derived/vitis_tile_cache_profile_20261023_v1/report.json`：完整274732节点/1100754边的tile calls1100754→224912（-79.567%），tile二分迭代14738053→3011501，alias迭代仍43987731；tile+alias总迭代约-19.968%。这些是CPU算法计数，不是RTL周期、AXI事务或router访问权重。未知/空行及capacity/wrong-mode负例单独保留。
- HLS综合owner3992116/exec41845已终态，勿重提。`data/derived/vitis_tile_cache_synthesis_20261023_v1/report.json`：同样23批HLS Csim通过；BRAM_18K16→16、LUT38632→39014、FF20364→20427，估计4.337ns。lookupII74、exception indexII73、sortII11、outputII8；总latency仍undefined、时钟仍超过3.65ns有效预算，没有候选postroute。生成RTL确有valid/x/y比较与命中旁路，decode内valid清零。
- 综合审查`results/vitis_tile_cache_synthesis_review_20261023_v1.json` SHA `b2b34d152513faaa8eba68115f87fcd501ed4fd0fecdd1bbfd76ed672250686f`。已复核profile172、synthesis178、review38个绑定；HLS仅复用classic2022.2，已读Ross pragma scope/run-flow，本机无vitis-run/Unified入口。
- 新唯一RTL owner **4065010** / child **4065711** / exec **69036** / CPU121：`scripts/vitis_tile_cache_cosim_pipeline.py`，`data/derived/vitis_tile_cache_cosim_20261023_v1/state.json`。工程`build/vitis_graph_compact_tile_cache_cosim_20261023_v1`为综合工程的真实副本，原工程不改。12批相同输入，自动独立黄金/RTL身份审计和已完成baseline周期对照；期望`results/vitis_tile_cache_cosim_audit_20261023_v1.json`、`results/vitis_tile_cache_comparison_20261023_v1.json`。**尚无候选RTL结果；不自动impl、不提升默认核。新pipeline及审计依赖冻结。**
- 原完整router Cmodel owner2924311仍运行，expanded2/4退出0，direct3371574/3373595仍活跃，待原四条件独立审计。原统计正常退出快照：canonical43/63、site8/63、source6/21、template2/35；source block000/001共6条件已有独立审计，其余不能仅按exit0称最终通过。不要重启原owner。
- `results/vitis_tile_cache_stage_20261023_v1.json`绑定本轮证据和真实/proc快照；`results/project_check_after_tile_cache_20261023_v1.log`通过。前一状态问答为verified wait，本轮为progress。目标仍active：实际特殊资源完整语义、统计终态、平台/板卡DDR/HBM/功耗及完整FPGA搜索仍未完成。下一步先读原tile-cache RTL结果、四条件Cmodel与统计终态；归并实验已完成但收益混合，仍不提升。

补充终态：归并owner2530145/exec39091及child2532179已结束，勿重启。`results/vitis_merge_cosim_audit_20261023_v1.json` SHA `aa263be97f98334401134b477a612f0cd3bf08e2ebada18202e5d573995f7093`，`results/vitis_merge_comparison_20261023_v1.json` SHA `c7f530b9927b54ed42377307918cbb4e06e34a1f3ede1286f517a97de34efbf1`，29个比较报告绑定文件已复核。642度样本9136018→7311608周期（-19.969%），120度-8.614%，146度+0.155%；低度数层略慢，uniform64为2108498→2115442（+0.329%）。**不替换默认核、不宣称完整router收益、不自动做候选impl**；原variant及全部负结果保留，`results/vitis_merge_decision_20261023_v1.json`记录判断。下一步优先查找路径单因素对照/实际访问特征，不能仅按度数阈值假定排序必然受益。CPU121/123现已释放；新full-router仍用原v2核，直接条件继续CPU122/124。

- 原分层baseline1811479/exec94314已终态，勿重启；`results/vitis_stratified_audit_20261023_v1.json` SHA `b87a445ee83f4f8935ff1e9657dcd5b7517edb5c2642083958045d5be865faae`，原audit_receipt及51绑定文件已复核。每模式12批、两份黄金日志和全部transaction通过，RTL与原XO一致。`results/vitis_stratified_interpretation_20261023_v1.json`保留解释。
- 对相同请求，compact/CSR周期比：degree2层17.998、degree4层29.939、degree6/8层42.887、degree12层57.076、degree120层106.534、degree146层98.393、degree642层130.889；每层仅2节点，不是总体估计。uniform64：CSR45108、compact2108498周期，比46.743；51known/13unknown，其中4空行、一个146度节点占146/368输出。不能将121倍旧样本或46.74倍均匀小样本称完整router代价。capacity负例409.289倍仅负例探针；unknown/wrong-mode相同，不混入正常吞吐。
- `hardware/vitis/router_xrt_transport.hpp`及`router_exchange.hpp`实现真实XRT回调：要求hw xclbin和明确DDR[0]/HBM[0]，核对全部6参数实际group/tag/type，图/config仅上传一次，按声明窗口同步请求/输出/result/counts及8guard，等待ERT完成，失败不回退CPU。记录BDF/name/UUID/groups、setup/graph upload及成功调用累计传输字节/host kernel wall。搜索/占用/协商仍CPU，不是完整FPGA搜索。
- `data/derived/kernel_router_xrt_20261023_v1/report.json`离线准备通过：g++17 O2 Wall/Wextra/Werror成功，真实XRT2.14.354链接；两模式shape preflight成功；nm确认无CPU核函数，未链接graph_body/graph_accel实现。新增硬件入口来源于已测试Cmodel router副本，源及binary绑定。**该report.files/generated及对应header/scripts冻结。**
- `test_router_exchange.cpp` ASAN/UBSAN模拟设备交换8组、失败launch8组、越界参数3组通过；验证同步顺序、完整尾guard、device→host数据及resident graph不重传。它不是XRT真实设备测试。`tests/test_kernel_router_board.py`合成完整结构正例direct/expanded及20类篡改拒绝通过；也不是板执行证据。
- 新`kernel_router_board.py`只在完整四条件Cmodel独立审计及显式platform link收据通过后运行，绑定host/input/reference/xclbin；无自动设备或平台选择。`check_kernel_router_board.py`独立比较全部1062网结果/site demands/轮次状态、两批以及传输/guard字节和时间。实际平台时序/频率仍需独立证据，200MHz请求不当作实测。未执行该硬件run。
- `results/xrt_router_environment_20261023_v1.log`最新probe：0devices，XOCL/XCLMGMT版本unknown。`results/kernel_router_xrt_stage_20261023_v1.json`汇总离线边界。平台/板卡DDR/HBM/功耗仍缺，不重复请求许可。
- CPU完整集成owner2924311/exec26410继续：expanded worker000/001已exit0，尚待完整原始独立审计；direct worker002 CSR3371574/CPU122、003 compact3373595/CPU124当前运行。不得把正常退出先称语义通过。唯一原checker在四条件都结束后运行。
- 归并sort owner2530145/2532179/exec39091仍12批RTL（已进展到10/12），原自动候选审计/与baseline匹配比较链保持。baseline终态后CPU123已空出；不重启原任务。其余source/template/site/canonical统计继续。
- 本轮progress：真实XRT接口编译/离线契约及启动/审计入口、baseline RTL终态量化证据。目标active；完整特殊资源语义、重复统计终态、候选RTL/后续实现、实卡测量及完整router硬件实现仍未完成。

## 历史：Vitis ABI邻接提供器全图通过，四条件完整路由C模型集成运行中

- 端到端统计实际已完成block000三条件独立审计：`data/derived/source_to_route_statistics_20261023_v1/block_000/audit.json`，SHA `518d54744fe3479ebd27678534373b8429144350d0b1210adb7131cae57f132e`。block001已有worker002成功、worker001正在执行。**结果位于block_*/worker_*，不能用顶层worker_*.json数量当进度**。当前至少4/21执行器完成、3/21独立审计，不是终态统计结论；继续原3986466/queue2407216。
- 新`hardware/vitis/router_provider.hpp`提供与原`site_native::route_batch`匹配的node_count/neighbors接口，通过明确KernelCall回调调用已审计Vitis v2原核ABI。静态邻接cache按规范node独立，动态占用/历史/site状态仍归原router管理；不把归并实验核混入集成。status2/3/4直接报错，未知status1保持未知，不会默认为no_path；逐行核验起点/度数/状态、8字段边身份范围、排序、多重边和尾部guard。
- `data/derived/kernel_router_cmodel_20261023_v1/preparation.json`已通过且二进制/测试日志hash复核。CSR与compact各自完整274732节点/1100754边/53759未知行与原黄金逐字段一致；20种异常返回均拒绝，另验LRU命中/淘汰、重复请求、预展开后全部行及invalid node。编译日志无警告。原数值ID跨表示不同，仍分别使用各自镜像/黄金/route/site输入。
- 原`src/native/site_runtime.cpp`及所有search/ledger/cost/occupancy头文件未修改，新`runtime.diff`只替换提供器/增加config参数和CPU backend标记/独立payload与调用计数。原router全部1062网、四轮轨迹/未知集合/路径/site demands输出保持；新`kernel_payload_bytes`是ABI逻辑载荷，不是旧logical_bytes或PCIe/片外访存测量。
- 新唯一四条件owner2924311/exec26410：`scripts/kernel_router_pipeline.py`，状态`data/derived/kernel_router_integration_20261023_v1/state.json`。CSR CPU122首expanded child2925693，compact CPU124首expanded child2925694，各完成后同core跑direct；每条件首次/驻留两批，全域不缩减，cache4096。expanded先经核C模型批量解码全图，再CPU搜索；direct缓存miss逐行调用核C模型。**当前均为CPU执行，没有XRT/实卡，不是完整FPGA搜索或硬件加速结论。**
- 四条件完成后原owner自动调用`check_kernel_router.py`重读完整原始JSON，与已独立审计native各模式reference逐项比较全部route trees/属性/需求/每轮search结果，输出`results/kernel_router_integration_audit_20261023_v1.json`。当前没有完整router新结果，勿预先宣称等价。preparation plan.files/generated、integration plan.files及全部关联源码/二进制冻结；不能修改原统计源或重提。
- guard范围是每次声明容量及8个尾guard word，不冒充完整最大AXI地址空间检查；原HLS黄金TB仍有完整最大缓冲区检查。Cmodel测试/guard开销不外推板端性能。提供器已留明确transport回调，但**XRT transport尚未实现/执行**。
- 原排序baseline1811479/compact2186943仍在12批RTL，CSR已工具通过；merge2530145/2532179继续同样12批，自动原审计/比较链不变。CPU121为merge、123为baseline、122/124为新完整router、125/126/127为原source/template/site统计。不要争用或重启这些owner。上一轮为progress，本轮全图ABI提供器与实际完整集成提交也是progress。
- 后续先核验原RTL审计/比较与四条件router集成；有证据后才决定候选impl。继续实现并验证真实XRT transport/平台链接、完整特殊资源语义、正式统计终态、板端DDR/HBM/功耗和完整router硬件接入，目标active。

## 历史：完整router容量审计完成，单一归并排序对照已进入RTL

- `data/derived/site_capacity_region_20261023_v1/independent_audit.json`6/6独立核验完成，SHA256 `3a7b8b47da358235a2eb6a6687f12561938da3d4a18167d5927f8e3939ac6334`；owner3749868/audit2190410已终态，勿重启。三种表示均在4096MiB RLIMIT_AS完成两个完整1062网批次，在3072MiB均严格std::bad_alloc。此网格没有容量可行性差异，不能沿用仅解码96MiB格优势；不是精确最低容量、RSS或实板容量，含完整状态/输出轨迹，且每条件只有一次新进程。
- 模板共享五条件完整首次/驻留路由审计完成：`results/template_scope_runtime_validation_audit_20261023_v1.json`，SHA `10ab49a44260b82f7c1e7b9b46283f927cfd32bc84ce788303c186667e4dcef0`。n=1仅语义协议验证，不外推统计结论；原queue2703564已启动35次driver2458493/CPU126。span16进程总wall含导出/共享主机干扰，不能只看该单次wall称机制退化。
- 新单一改动`hardware/vitis/merge_sort.hpp`：把compact插入排序替换为稳定bottom-up归并，额外MAX_DEGREE scratch BRAM；lookup/exception/ABI/频率/全部黄金TB保持。`data/derived/vitis_merge_kernel_20261023_v1/algorithm.diff`只增加helper include及替换sort循环。全部新源与helpers、plan.files/generated均冻结。
- `results/vitis_merge_sort_stress_20261023_v1.json`：真实排序函数ASAN+UBSAN下5125组通过，长度0..1024×随机/升序/降序/相同前缀末字段/全UINT32_MAX五模式；保留重复/七字段、尾部和边界guard。原完整274732请求/1100754边、原负例和新分层在普通CPU与HLS Csim各23批完全通过。
- 新综合owner2408114/exec4639已终态；`data/derived/vitis_merge_synthesis_20261023_v1/report.json`及`results/vitis_merge_synthesis_review_20261023_v1.json`。归并output II11/depth18（log19，XML18原证据保留），copy II7/depth8；旧插入while II11/depth17。编译器自动pipeline/展开比较字段，外层无法flatten；scratch真实推断BRAM，没有ignored pragma。综合估计BRAM_18K16→32、LUT38632→39233、FF20364→20702，时钟估计4.337ns；都不是新布局布线结果。lookup仍II73/74、输出II8，总综合latency均undefined，不能宣称综合周期改善。
- **可能退化的证据必须保留**：按完整真实度数分布，旧insert实际shifts4957233+最终placement891694=5848927次record赋值；merge精确控制流模型6618088次，约+13.15%。这是算法赋值计数，不是RAM事务/周期。高节点可能改善，但全图/低度数不保证。没有将单一排序替换成混合策略或同时改lookup。
- 新唯一归并cosim owner2530145/exec39091、child2532179/CPU121：`data/derived/vitis_merge_cosim_20261023_v1/state.json`，工程`build/vitis_graph_compact_merge_cosim_20261023_v1`真实副本，无hardlinks；原综合工程不修改。`scripts/vitis_merge_cosim_pipeline.py`两份黄金日志/12个RTL transaction和全部RTL身份由`check_vitis_merge_cosim.py`独立审计，候选报告`results/vitis_merge_cosim_audit_20261023_v1.json`。随后等待原分层baseline审计收据，再自动发布`results/vitis_merge_comparison_20261023_v1.json`。**该pipeline plan.files及全部关联源码/报告冻结。**不自动impl；先读全部分层退化/收益再决定。
- 原分层baseline owner1811479/exec94314继续，CSR12批已工具完成，compact2186943仍RTL，尚无最终独立全报告。不可将CSR单方终态当双模式完成。归并与baseline的12批路径/请求/黄金完全相同。原CSR/compact XO/OOC终态不变。
- 其余CPU原链最近canonical34/63、站点统计5/63、source21次继续；各原owner活跃，不重提。当前完整目标仍active：时钟/特殊资源完整语义、重复统计终态、实卡DDR/HBM/功耗和完整router FPGA仍缺。
- 本轮使用本地classic2022.2验证/综合流程。已读Ross hls-optimize及init参考，但本机没有vitis-run/Unified报告函数，因此未执行该完整Unified技能流程，也未伪建git/vitis-comp工程；遵循用户2022.2兼容替代规则，版本目录+哈希保留实验。pragma scope规则已遵守；新scratch绑定在声明后的函数体内。

## 历史：Vitis副本OOC全部通过，按度数分层RTL运行中

- `results/vitis_ooc_audit_20261023_v1.json`独立审计通过，SHA256 `56fef832a7fb8845ceed4cd7332cea4152b7deb52459637c91e24d9796657cf8`，55个绑定文件已再次核验。原OOC owner1274778、audit1469666终态，勿重启。实际5ns/200MHz，CSR/compact WNS0.998/0.561ns、WHS0.011/0.040ns；setup/hold端点均非空，no_clock和内部未约束为0，所有可路由网完成、路由错误0、DRC0。post-route LUT6708/12339、FF9426/15285、BRAM报告34/34；外部612输入/314输出无delay，不能称平台AXI/板级时序闭合。
- 新唯一分层cosim owner1811479/exec94314，`scripts/vitis_stratified_pipeline.py`；状态`data/derived/vitis_stratified_cosim_20261023_v1/pipeline.json`，子进程CSR2186610/CPU122、compact2186943/CPU123。新工程`build/vitis_graph_{mode}_stratified_20261023_v1`均真实副本，无硬链接，排除旧sim/csim/impl；原算法与RTL不变，不重新综合。两模式离线C++黄金比较12批已通过，HLS当前C预处理生成向量，尚无新RTL周期结论。
- `data/derived/vitis_stratified_fixtures_20261023_v1/plan.json`：固定seed20261023，每个非空度数层抽2节点，额外独立均匀抽64节点，加原capacity/wrong-mode两负例，共12批/模式。度数256–511真实总体为0，明确记empty_strata；高层抽到两个642度节点。均匀64批含一个146度节点，仍不代表实际router访问分布。不能平均分层周期冒充全图加速。
- **两模式字符串ID不同**：例如节点196的PIP/wire数值ID偏移103，原始二进制黄金不可跨模式直接比较。新构造检查全部274732行status/degree一致，选中节点按实际镜像还原完整src/dst/tile/PIP/wire/属性/方向多重集合后比较，再保留各自编号的黄金8字段。数值相同才比较字节；不重编号内核输入。准备v1日志记录不成立的字节一致假设，v2日志记录空度数层，修正后v3成功；均保留。
- 原黄金TB未削弱：计数、每请求start/degree/status、全部8字段及输出/result完整尾部guard继续检查。`tests/test_vitis_stratified.py`涵盖13种坏输入拒绝，日志`results/regression_vitis_stratified_20261023_v1.log`通过。唯一pipeline两模式完成后自动调用`check_vitis_stratified.py`核验完整日志两份、连续transaction、与旧XO核相同RTL，输出`results/vitis_stratified_audit_20261023_v1.json`及独立`audit_receipt.json`。**新fixture plan.files/generated及cosim plan.files冻结，勿修改原脚本/源文件。**
- 容量owner3749868六格已运行完，原审计child2190410继续，`data/derived/site_capacity_region_20261023_v1/state.json`。执行器结果：三表示4096MiB均两批等价，3072MiB均std::bad_alloc，完整独立原始核验尚待终态。RLIMIT_AS包含router状态和轨迹，不是RSS、精确最低容量或FPGA容量；不沿用仅解码96MiB格的优势。
- 其余原链最近发布：canonical32/63、站点统计4/63、模板粒度验证4/5；source21次继续。owner与冻结依赖保持。上一问“什么队列”只核对原live PID，分类verified_wait；本轮OOC终态证据+分层构造/测试/实际提交构成progress。
- 下一步先检查上述唯一cosim及capacity审计，禁止重复提交；依据分层RTL与既有操作计数做单一排序算法对照，再另测lookup缓冲。完整特殊资源/时钟常量与反相、正式统计终态、真实U280平台/板卡DDR/HBM/功耗及完整router FPGA仍未完成，目标active。

## 历史：Vitis两核XO已独立审计，操作诊断完成，副本OOC实现运行中

OOC唯一后续独立审计owner1469666/exec8611已启动，状态`results/vitis_ooc_audit_pipeline_20261023_v1.json`，等待原OOC owner1274778结束后执行`check_vitis_ooc.py`，输出`results/vitis_ooc_audit_20261023_v1.json`。审核实际5ns/200MHz、非空setup/hold路径、no_clock/内部未约束为0、路由完整/0错误及0DRC；外部IO未约束单列。真实旧OOC正例和9类虚假闭合拒绝测试通过`results/regression_vitis_ooc_audit_20261023_v1.log`。**审计队列files及OOC plan.files冻结。**若流程退出0但质量失败，保留负报告，不自动重跑。

- `results/vitis_graph_kernel_audit_20261023_v2.json`全部通过，SHA256 d3e1313bde7b76712ac7aaa2b85e055b615bc0df59adf6b2ac119ded0c22fb84，与原audit队列及auditor源码绑定已复核。原HLS253757、audit505544都已终态，勿重启。两模式完整Csim274732请求/1100754边+负例，三批RTL及XO8参数ABI、包内全部RTL与各自综合工程逐字节一致。v1失败保留。
- 新Vitis匹配样本CSR38803周期、compact4700243周期，后者121.13倍；两者综合估计4.337ns、loop constraints NOT all satisfied。估计资源CSR22934LUT/12577FF，compact38632LUT/20364FF，各16 BRAM_18K，尚不能当布局布线资源。比值小于旧OOC224.89不表示优化：compact从4682265略增，CSR从20820增至38803，包装/AXI设置与仿真模型已改变。
- `data/derived/vitis_decoder_profile_20261023_v1/report.json`诊断CPU副本原黄金比较全通过；`results/vitis_decoder_diagnosis_20261023_v1.json`绑定原始输出和完整度数分布。compact全图1100754边，tile二分14738053次、alias二分43987731次、sort comparisons5744867、record shifts4957233。源代码已是二分查找，不要误提“改线性为二分”。计数不是周期/真实访存事务或板端时延。
- 220973已知行度数中位4、p95/p99均8、p99.9=146、max642；>=64的536行贡献82967边。RTL8请求样本中642度节点占664输出的642条，sort shifts92181，约138.83次/边，全图4.50次/边；查找迭代每边两者约53。**该样本不能外推完整路由121倍。**下一优化应单独试排序改动并按度数分层RTL，再另测lookup/local-buffer，不能一起改后归因。
- 新OOC owner1274778/exec35271：`scripts/vitis_ooc_pipeline.py`，状态`data/derived/vitis_ooc_20261023_v1/pipeline.json`；CSR CPU122、compact CPU123，工程`build/vitis_graph_{mode}_ooc_20261023_v1`是真实文件副本（无硬链接，sim仅保留报告），用已通过cosim的相同RTL执行classic2022.2 `export_design -flow impl`。**新plan.files冻结。**旧源、XO和报告不覆盖；阶段完成后仍需独立读实际route/timing/DRC/resource并检查原artifact hashes。工具设置允许时序失败仍退出0，不能只看完成marker。
- `results/clock_extended_observation_stage_20261023_v1.json`：Vivado额外连通/手工上下文和RapidWright2022.2.3只读DCP观测均完成。手工上下文没有暴露SITE_PIPS/反相；13外部节点均IS_GND=IS_VCC=0不证明内部tie。RapidWright保留baseline6/probe11 PIP且2时钟route-through精确一致，却没有两个隐式SiteInst/BEL attrs。不能把缺对象当空闲或常量，不扩充14实例模型。原baseline恢复、MCP3/3完成无在途调用。
- 新工具独立在`.tools/rapidwright_2022_2_3`，official releaseMD5核对，jar SHA e3eb4c91ac58b0b6408a5ff98aeb8894774709dc5dec0b2258c6267a7130e110；本机Vivado JDK11含javac/javap但不在PATH。设备DB已落本目录并绑定v2读取plan。`adapters/ClockConnectivityDumpV2.java`/`scripts/check_rapidwright_clock.py`不改DCP；勿调用参考工程的修改版launcher。reader1824cell与Vivado1833差9，恰有5GND/4VCC，但未做全cell对照，不宣称全设计等价。
- 原CPU链最近执行器发布：旧canonical29/63，站点统计3/63，模板粒度验证4/5；源图21次仍block000；容量3/6（当前compact/direct/3GiB child948504，owner3749868）。最终独立审计仍由各原队列负责。时钟语义、正式性能终态、实际U280平台/板卡DDR/HBM、功耗和完整router FPGA仍未完成，目标active。

## 历史：Vitis主机接入完成离线验证，v2核验证及自动审计继续

- `results/vitis_host_preparation_20261023_v1.json`：XRT2.14.354主机成功编译（最终log v4，需`-luuid`），两模式各10批/274736请求/1100754记录输入预检通过。3项主机测试含12类坏输入及10类读回篡改；3项kernel审计测试含15类证据错误；独立读回1项/15类错误拒绝通过。仅离线契约，不是板端执行。源码和最终binary `build/vitis_graph_host_20261023_v2`均绑定，**host报告artifacts冻结，后续修改用新版本**。
- v1 HLS在cosim插桩编译时因C/C++ linkage冲突失败，完整证据保留；不要重启原v1。新`hardware/vitis/v2/graph_accel.hpp`使用extern-C声明块，原算法保持；`data/derived/vitis_graph_kernel_20261023_v2` owner253757/exec9963，CPU122/123，完整Csim和综合均通过。CSR RTL三批通过并已导出XO；compact原xsimk303134仍运行，已完成第一批。**v2 plan.files/generated、pipeline.files冻结；新包装没有继承旧OOC时序。**
- 唯一后续审计owner505544/exec50921，`results/vitis_graph_audit_pipeline_20261023_v2.json`，等待原HLS owner终态后自动执行`check_vitis_kernel.py`，最终输出`results/vitis_graph_kernel_audit_20261023_v2.json`。审计冻结依赖不可修改；完整Csim/RTL样本、8参数ABI、XO全部RTL与对应综合工程逐字节相同均需通过。失败停止、不自动重试。再次会话先核对/proc和状态，勿竞争重提。
- 主机和平台入口`hardware/vitis/README.md`、`scripts/vitis_board.py link/run`：明确.xpfm，DDR[0]/HBM[0]分别连接全部6个buffer；核验实际bank类型/group并保存设备BDF/name/xclbin UUID。主机全量guard读回、独立`check_vitis_readback.py`及输入/链接/执行哈希绑定已具备。硬件link/run尚未成功执行，不能称端到端实测；单次run的重复是图驻留重复，正式统计还需独立进程与随机顺序。
- 最新XRT探测`results/vitis_board_environment_20261023_v1.json`：0 devices；默认2022.2 base_platforms无U280.xpfm。需要实际匹配shell的平台与板卡才能接续DDR/HBM/功耗；不拿其他器件平台替代。`results/vitis_integration_stage_20261023_v1.json`保存本轮证据与进程快照，未来实时状态以原pipeline为准。
- 原CPU链保持：旧canonical执行器26/63、站点统计1/63、模板粒度验证3/5；源图21进程仍block000。容量owner3749868已发布2/6，CSR/3GiB明确分配失败，CSR/4GiB两批语义由执行器核验；compact/direct/4GiB child247066继续，最终全部独立审计未到。先前只有首失败格做了独立partial审计，勿把新第二格称最终独立完成。
- `python3 scripts/run.py check`通过。完整特殊资源模型、正式统计终态、平台后时序/资源、实卡DDR/HBM/功耗和完整router FPGA接入仍缺，目标active。

# 历史：源图三条件已审计，21次统计与6格完整router容量继续

`results/source_to_route_validation_audit_20261023_v1.json`3/3完整原始结果通过；原validation2142179/audit2205877均结束。原queue2407216已启动21次统计driver3986466，CPU125，继续原链及冻结依赖。n=1的验证耗时不作加速结论。

新增`data/derived/site_capacity_region_20261023_v1` owner3749868/exec42804，CPU124，三个表示×3072/4096MiB RLIMIT_AS，共6个完整1062-query两批进程，全部完成后自动独立审计。首CSR/3GiB分配失败已独立partial审计1/6，`results/site_capacity_partial_001_20261023_v1.json`；当前CSR/4GiB child3948120。先核实state.json与/proc，不重提，不改plan.files。后续需完成所有条件及审计；意外信号/异常不当作容量失败。RLIMIT_AS不是RSS或板容量，14实例模型仍不完整。

时钟所有公开属性已审计并恢复A原checkpoint，`results/clock_property_surface_stage_20261023_v1.json`。getter的IS_INVERTED为空而report_property显示只读bool0，原因未证实；不要据此填写实际反相值。常量/反相/leaf delay/test/保护占用仍需其他物理证据。

旧canonical22/63、站点63次正式统计第一进程、模板共享验证1/5仍在原链。完整模型、性能终态、实卡平台DDR/HBM/功耗继续；全目标active。

# 历史：真实规模与受限CPU解码容量已完成，继续原性能链

`data/derived/scale_domain_region_20261023_v1/report.json`四个嵌套真实域、每域CSR/compact全部静态与原生邻接通过；最大域274732节点/1100754边且镜像与原版本逐字节相同。`results/scale_capacity_region_audit_20261023_v1.json`独立审计48个受限新进程：最大域96MiB RLIMIT_AS下compact通过、CSR分配失败，128MiB双方通过。只证明CPU解码器虚拟地址空间可行性，不能推导精确最低内存、RSS、完整路由器或板端容量；空间前缀资源组成不同的限制保留。

规模3361172和容量3549882都已正常退出，勿重启。三个回归日志及完整原始收据已保存。下一步继续原四条性能链（旧canonical20/63、站点正式统计第1进程、源图验证2/3、共享粒度验证1/5），等原门控独立审计后分析完整矩阵。继续补实际时钟常量/反相/占用与完整router/板级容量及DDR/HBM/功耗；完整目标active。

# 历史补充：时钟证据已归档，保持原CPU实验链

先读`results/clock_semantics_stage_20261023_v1.json`。真实捕获v3和16组/192样本的本机XSim原语行为已审计，但实际常量/反相/leaf delay/test/固定占用仍不完整，不能扩大14实例授权。v2捕获误标证据保留，勿复用。A会话恢复原site_full checkpoint。

站点验证原owner1716135及独立审计3328897已完成，`results/native_site_runtime_validation_audit_20261023_v1.json`全部3/3完整原始数据通过，SHA256为3591fd8ecd96715a08df7b5cd685889c093f01143983f983e3129f1afe5e7455。原queue1739121已启动63次统计owner3457381。源图原owner2142179已完成前两条件，正在compact/direct；下游原审计2205877及21次queue2407216保持。旧规范模型已执行器验19/63；模板粒度首span4两批执行器通过，正执行第二条件，完整独立审计仍待5条件。以上是本地CPU后台链，不是启智GPU队列。所有冻结依赖保持不变。

规模与容量的上述两步现已完成，见顶部证据。CPU124无本轮残留求解进程；旧输出和绑定不得覆盖。

# 历史：模板共享粒度完整等价通过，实际全网路由/统计已开始

`data/derived/template_scope_region_20261023_v1/report.json`：全区域/16×16/4×4/单tile共享的274732节点、1100754有向边与未知行状态完全一致；镜像93.51/93.95/96.95/107.37MB，单tile已大于CSR98.26MB。仅共享范围变化，固定训练规则和实例例外。

新唯一pipeline2703564/exec62529，验证driver2703565/native2710957 CPU126当前span4。状态 `results/template_scope_runtime_pipeline_20261023_v1.json`；先五条件完整1062网首次/驻留验证及独立审计，再7×5=35进程统计及独立审计。保护冻结plan/state依赖，不重复提交；绑定 `results/template_scope_execution_binding_20261023_v1.json`。

源图到两批路由首CSR已独立partial审计（1/3，1118.713秒），其余条件和21进程门控仍继续。注意 `results/source_to_route_memory_scope_20261023_v1.json`：RUSAGE_CHILDREN包含fork/pre-exec继承RSS，native批次VmHWM是exec后口径，不相加也不混称。原站点验证已执行器验CSR/compact-expanded，现compact-direct；原旧canonical统计仍运行。

后续保持所有原实验链，依据终态做完整统计和分析；继续完整特殊资源/时钟语义、规模与实卡DDR/HBM/功耗。全目标active，部分模型和邻接等价不代替完整实验。

以下为历史检查点。

# 最新：完整软件链路统计队列已提交，转换14进程审计完成

转换矩阵 `results/packed_conversion_statistics_audit_20261023_v1.json` 全14/14通过：CSR/compact各7次转换中位数38.224/56.338秒，非完整端到端。旧转换owner/queue已完成，不重跑。

源图→新AGR→新fixture→两批全网native验证 owner2142179/CPU125，独立audit2205877；其下游统计queue2407216/exec50824等待原audit成功后运行7×3=21进程，再逐块原始语义审计和总审计。状态 `results/source_to_route_statistics_pipeline_20261023_v1.json`，绑定 `results/source_to_route_statistics_execution_binding_20261023_v1.json`；各层plan/state.files冻结，先实查进程，不修改依赖或重复提交。验证与重复统计都尚未完成，不能提前给总链路性能结论。

站点first/resident验证CSR完成、compact/expanded第二批运行，owner1716135/queue1739121继续。原canonical4146936为12/63，模型物理失败限制不变。完整时钟/其他特殊资源语义、模板粒度/规模和真实板级DDR/HBM/功耗仍需推进；不能将部分模型/软件两批计时替代完整目标。

以下为历史检查点。

# 最新：同一运行内重建图镜像和原生输入的接口已验证

`data/derived/runtime_fixture_rebuild_20261023_v1/report.json`验证新转换CSR/compact镜像能生成字节完全相同的1062-query routing/sites/queries/symbols四种产物；3类错误输入拒绝。下一步以 `src/runtime_fixture_builder.py` 接read_export→write_packed→fixture→native实际执行并直接测总时长，仍需保留完整范围与证据验证，不能将阶段中位数相加称端到端。

原转换1876655/审计1900286为10/14；站点验证1716135/CSR1723135和门控1739121继续；旧canonical4146936为11/63。都先实查原句柄，禁止改冻结依赖或重复提交。完整时钟语义、实卡DDR/HBM与功耗仍待完成。

以下为历史检查点。

# 最新：源图转换成本与站点运行时并行测量

转换owner1876655/exec29579，独立审计queue1900286/exec62541：`data/derived/packed_conversion_statistics_20261023_v1`，执行器3/14，首CSR已独立partial审计。保持plan/queue冻结依赖。完成后自动发布完整14进程审计；目前没有两模式统计结论。

站点完整first/resident验证1716135（CSR1723135）及门控queue1739121继续；旧canonical矩阵4146936为10/63。三条链都不可重复提交。准备成本还需query/site fixture、采集/训练边界与完整同批源图到route计时；时钟常量/反相/占用、实卡DDR/HBM/功耗仍未完成。不要将独立阶段中位数相加称实测端到端。

以下为历史检查点。

# 最新：站点完整首次/驻留验证及后续独立审计/统计链运行中

查 `results/native_site_runtime_pipeline_20261023_v1.json`（queue1739121/exec87865）与验证owner1716135/exec75213、初始CSR1723135。完整1062查询三条件各两批后自动独立审计，再门控63进程统计和最终审计。禁止重复提交或修改plan/pipeline冻结依赖。小协议已通过，完整验证尚未发布。

旧canonical统计queue3591840/statistics4146936仍在原链（10/63）；其结果不可代替物理有效站点模型。其他可并行任务：完善时钟常量/反相/占用语义、计入源图/fixture转换成本、真实平台DDR/HBM与功耗。全目标仍未完成。

以下为历史检查点，以AGENTS顶部和实时进程为准。

# 最新：原生站点全网等价与锁定引脚联合时钟探针已完成

先读 `results/native_site_routing_check_20261023_v1.json` 与 `results/clock_row_locked_stage_20261023_v1.json`。原native执行/审计链均已完成，禁止重启；CSR/compact全部1062网/17682 PIP/16836连接记录匹配已物理通过的Python部分站点模型。源码存档native_site_verified_20261023_v1。

下一步：为这一物理有效站点模型补公平first/resident/expanded/cache统计；原canonical63进程矩阵仍在原queue3591840/statistics4146936，已9/63，不要改其冻结依赖。时钟联合探针用原1099 LUT LOCK_PINS后严格端点/保护/DRC通过，但仍需明确常量/反相、共享配置与占用语义，不能仅凭一条物理路径扩充模型授权。实卡平台/DDR/HBM/功耗仍待完成。

以下为历史检查点；native运行/探针失败待修复等以本段和AGENTS顶部为准。

# 最新：行时钟探针需锁定LUT物理引脚后重测

完整probe的目标路径/1277网路由/DRC通过，但564网物理site_pin因Vivado重布线改变，严格审计失败：`data/netlist/clock_row_route_probe_full_20261023_v1/verification.json`。保留负结果，读取原LUT逻辑→物理pin映射，核实LOCK_PINS再做新目录实验；不放宽端点保持条件。A会话已恢复原完整site_full checkpoint。

原native CSR/compact执行与自动审计链继续；当前compact第四轮附近，原统计8/63。不要改冻结依赖或重复提交。完整目标仍包括未验证资源语义、公平站点模型性能及实卡平台/功耗。

以下为历史检查点。

# 最新：CSR站点全网已执行完成，compact与自动审计继续

保持owner983662/compact1200236及审计queue1111940原链；CSR汇总1062网/17682 PIP/4轮866→205→21→0匹配Python，但完整逐项审计尚待两模式终态。不要竞争重跑，不改冻结文件。原统计执行器7/63，仍运行。

新增行时钟映射 `results/clock_row_mapping_20261023_v1.json` 完成26 PIP/39端点/13站点的Vivado对两镜像核对。下一步可设计row CE/CLK两种路径的配置/占用探针；端点映射或IS_USED=0均不能授权合法性。继续全模型、物理有效路由公平统计与实卡平台/功耗目标。

以下为历史检查点。

# 最新：全网原生站点审计已自动排队

检查原执行owner983662与下游审计1111940（exec92181/69369），状态 `results/native_site_audit_pipeline_20261023_v1.json`；勿重复提交。CSR+compact正常退出后会自动运行完整独立比较并发布 `results/native_site_routing_check_20261023_v1.json`；失败需依据日志诊断，不能把进程结束当通过。checker与队列依赖也冻结。此时CSR第三轮运行中，尚未获得真实审计结论。

原统计矩阵执行器6/63，继续原队列。后续仍须补完整站点资源模型、针对物理有效站点路由的公平性能、实卡平台/DDR/HBM/功耗；以下历史状态需以AGENTS顶部与进程实查更新。

# 最新：原生完整站点路由运行中

先查 `data/derived/native_site_routing_20261023_v2`、owner983662/exec92181与子进程；CSR后自动compact，不竞争重跑、不修改plan.files冻结依赖。结束后新增独立检查器，反解每模式编号池与物理resource symbols，与已物理通过的Python全1062网站点routes比较最终树、需求和每轮全部保留状态/计数。暂不能声明native/compact站点等价。

原63进程统计queue3591840/statistics4146936仍活跃，当前5/63执行器核验；保持原输入源码冻结。完整特殊资源语义、站点模型公平性能、板级DDR/HBM/功耗仍未完成。

以下为历史检查点，以本段和AGENTS顶部为准。

# 最新：独立区域完整查询物理验证通过，完整目标仍active

优先看 `results/site_full_stage_20261023_v1.json`：1062网/17682 PIP在已测14实例的站点模型下完成，并通过全部读回/保护/放置/连接和质量检查。仅此查询集和部分模型，不是完整模型或加速结论。原Python站点进程与MCP应用已结束，历史“仍运行”勿照做。

1. 继续原63进程统计队列3591840（statistics owner4146936），不改冻结runtime代码、不竞争提交；结束后用 `scripts/check_native_runtime.py`做独立全矩阵审计。它测旧canonical模型，不能当作本次有效站点路由的性能。
2. 将已验证的native站点事务/配置标签搜索接真实实例证据、站点协商ledger和全部1062查询；与新Python结果做最终树与状态对照，再完成站点模型CSR/模板对照及物理复核。
3. 推断v3表仍不可整体作为已验证需求；补足特殊资源语义与保护占用覆盖。实卡DDR/HBM、外部IO平台、功耗与完整端到端仍未验证。

以下为历史检查点，若冲突以本段与AGENTS顶部为准。

# 最新：区域 HLS 对照已完成

独立报告 `results/hls_region_check_20261023_v1.json`：双方完整Csim、采样RTL、OOC实现通过；压缩核LUT约1.96倍、采样周期224.89倍，未见加速收益。下方等待HLS实现的描述已过时，禁止竞争重跑。完整物理站点模型、原生全路由、公平统计和实卡实验仍待完成；先继续原站点路由1396247，并在终态后独立审计及物理读回。

# 当前执行顺序（2026-10-23）

1. 继续观察原站点路由 PID1396247 和 HLS 队列 PID1525674，先查真实进程；不得竞争重跑或修改冻结依赖。最新状态见 AGENTS.md 顶部。
2. compact 区域 RTL 联合仿真已通过，待原队列实现完成后生成独立区域 HLS 对照报告，保留周期负结果与外部约束限制。
3. 站点路由只覆盖14已测LUT实例；完成后独立验证全树，再验证真实物理回写。继续补齐其他站点族语义，不能把部分覆盖当完整合法性模型。
4. 完整原生路由、公平准备/缓存/内存统计、实卡DDR/HBM与功耗仍缺。独立域原1062网软件等价虽通过，物理回写失败；旧域成功不能替代。

区域采样RTL周期已独立核验：CSR 20,820、compact 4,682,265，后者224.89倍；证据 `results/hls_region_rtl_cycles_20261023_v1.json`。当前源码每条模板边需tile与两次alias二分查找，完成行后还需插入排序；这些是待量化的优化候选，尚不能归因各自周期占比。后续须保留规范源验证、并行边及完整属性/顺序，不通过删除校验制造性能收益。

以下为历史记录，运行进程及待办以本段和 AGENTS.md 顶部为准。

# 最新检查点：独立区域采集完成，全量路由运行中（2026-10-23）

更新：原队列及worker已正常退出，队列exit_code=0。完整 `report.json` 已发布，7份产物哈希逐一复核一致；两份完整路由JSON去除wall_ms后直接比较相同。全部1,062网、17,336 PIP，双方4轮完成且0冲突、0未完成。单批Python路由约3571秒/7994秒，不是统计性能结论。下面“运行中”为此前检查点。

当前下一步先修正 `scripts/prepare_netlist_routes.py` 的旧参考域硬编码：绑定本实验冻结配置/capture/快照和产物哈希，再独立验证新域全部树，生成新目录候选后进行Vivado读回/质量验证；不能直接用旧域验证独立区域路径。

采集和严格合并已完成，见 `results/region_u280_capture_20261022_v1.json`；不要重启采集。独立域包含220,973个源、274,732个规范节点、1,100,754条有向边。

原路由队列PID2113276、worker PID3090103已实查存活。全部1,062网的CSR在第4轮达到0冲突/0未完成；模板表示前3轮汇总依次为632、87、1处冲突，均0未完成，第4轮计算中。这些汇总不能证明完整路径/状态等价；须等 `data/derived/region_all_nets_cap8_20261022_v1/report.json` 发布后核验。

后续依次检查完整语义报告、准备无冲突候选的Vivado精确回写和保护/质量验证、运行公平统计对照。独立域两份AGR镜像均超过旧64MiB核容量；新硬件/C模型实验必须显式扩容并验证完整输入，禁止截断。板级DDR/HBM、功耗和端到端测量仍未完成。

以下为历史检查点；采集运行中和等待采集的描述已过时。

# 历史：独立区域采集执行中（完整目标仍 active）

自动后续队列PID2113276 / exec36724已运行，等待采集后做全部1,062网独立域实验；见AGENTS最前段。禁止竞争提交或改冻结代码。测量驱动已验证于 `netlist_runtime_validation_20261022_v1`；最终统计对照须在采集结束后运行，并根据完整独立域成功/失败结果先分析覆盖与预算，不将16网验证当成全量性能。

先核实 owner PID1959703 / exec session90514 与 `results/region_u280_capture_20261022_v1.json`。8分片独立只读采集220,973源，自动严格合并；不得竞争重启/finalize。冻结规则、训练无重叠和pilot见AGENTS最新段。完成后接入独立域全部1,062网搜索，并实现公平缓存/准备/内存/重复顺序统计。域外未知保留，不能为复现旧路径补入5个域外参考源。

# 第四轮有界全网集成已完成

先读 `results/netlist_stage_20261022_v1.json` 与 `AGENTS.md` 最后“以本段为最新状态”段。以下历史段的export/软件/HLS队列均已完成，**不要再次启动、finalize或覆盖产物**。

已完成1,062网/4,209 sink的CSR/模板/C模型等价、全Vivado节点/PIP精确回写及保护/质量验证；58项回归通过。主20轮与同22轮原代价策略有2冲突，cap8跟进22轮通过，均保留。真实U280 HLS也已完成，但模板周期慢38.55倍，不能推断实卡加速。

下一步：
1. 从固定placement与全部真实端点定义独立区域资源域，不按参考路径选行；预登记选择规则/训练冻结/预算与未知边界，按需要并行只读导出并严格合并属性/别名/完整邻接。保护时钟与常量，保持规范节点，不按坐标合并。
2. 做公平缓存/运行时对照（CSR同等缓存、直接模板、展开模板、缓存容量/重复/顺序），把准备与峰值内存计入；当前Python单批缓存时间只是集成诊断。保持失败状态，不把未知行当sink。
3. 实现并验证独立域/更大输入上的硬件或C模型接口，继续保留负结果，不预设收益。当前HLS有64MiB声明容量；超出须显式处理，禁止截断。
4. 实卡DDR/HBM、平台、外部IO约束、功耗和完整端到端仍待真实资源；不能用AXI模型或OOC替代。

MCP先list_sessions，只使用A自己的会话 `vivado-20261022-165536-938cabaa`；不要操作B方向会话。A目前加载cap8候选，恢复原baseline后再采集新域。

---

# 最新：回写预检完成，单一后续队列已运行

优先读取 `AGENTS.md` 最后“回写预检与单一后续队列”段。原导出 PID 2173511、后续队列 PID 3431763 都已实查仍在运行。**不要手动运行下面历史段列出的 finalize 和 netlist-check**；队列会在原导出结束后依次执行，状态在 `results/netlist_pipeline_20261022_v1.json`。

16 条原参考树/990 PIP 已精确回写，保护网与 placement 均不变，质量检查通过。证据 `data/derived/netlist_preflight_20261022_v1/manifest.json`。搜索生成的新路径尚待域导出与软件路由完成，不能把接口预检当成完整路由实验。

接下来观察队列；阶段完成/失败后读取其阶段日志并处理。软件结果位于固定新目录 `data/derived/netlist_integration16_20261022_v1` 与 `data/derived/netlist_all_nets_20261022_v1`。之后使用原 baseline checkpoint 经 MCP 应用完整无冲突候选，再运行读回与质量比较。当前 MCP 已重新加载 baseline。

---

# 第四轮当前检查点（2026-10-22）

完整持续目标仍未完成。优先读 `AGENTS.md` 最新第四轮段、`EXPERIMENT_STATUS.json`、`results/hls_check_20261022_v2.json`。

1. **不要重启当前导出。** 独立 batch 原 PID 2173511，日志 `results/vivado/export_netlist_domain_20261022.stdout`，目标 18,243 行。确认 `NETLIST_DOMAIN_COMPLETE` 后运行 `python3 scripts/finalize_netlist_capture.py`。SLR0 训练已冻结在 `data/derived/netlist_u280_bank_20261022_v1`。
2. 运行 `python3 scripts/run.py netlist-check --max-nets 16` 先检查真实网集成；通过后运行默认全 1,062 条。必须读取 capture.json 并核对哈希。路由代码、准备 FIXED_ROUTE 和独立读回检查已编写，尚未实际回写验证。CSR/模板共用规范占用与协商拥塞，惰性缓存的额外内存明确计入。
3. 从无冲突完成的输出用 `scripts/prepare_netlist_routes.py` 生成 TSV；通过 MCP 查询并复用已加载 U280 基线的会话，加载 `adapters/apply_netlist_routes.tcl`，调用 `netlist_apply::apply`。只保存到新目录；不调用 Vivado 自动修复候选路径。再用 `scripts/check_netlist_readback.py` 检查全部未选中网及 placement。比较 DRC/时序：原路由工作负载基线有一条时钟缓冲器 LOC 缺失 HDOOC-4（`results/netlist_baseline_drc_20261022.rpt`）。
4. 现域依赖参考路由节点，只能称集成域。必须继续按未知边界扩展并建立独立搜索域，才能讨论完整路由性能；当前 hop/congestion 成本尚无校准时延模型。
5. HLS 参考核已完成 Csim、csynth、两轮 cosim 和 OOC 布局布线；不要重复运行覆盖。`hardware/hls/README.md` 有复现命令。实测仿真周期为模板慢 36.7–82.7 倍；`results/hls_ii_diagnosis_20261022_v1.json` 有映射查询与排序瓶颈证据。后续实现完整网表后端、独立 CSR/模板硬件对照；当前核仅支持 8 MiB 输入镜像，不得默默截断较大的 U280 图。
6. 实卡与平台仍缺：XRT 枚举 0 卡，无 U280 xpfm；板级 IO/DDR/HBM、功耗和端到端收益不能由 OOC/AXI 仿真代替。

最新测试：全套旧 44 项通过；随后新增端点保护回归，10 项路由测试单独通过（合计 45 项）；`scripts/run.py check` 通过。

---

以下为历史检查点：

# 当前下一步（第三轮已完成）

先读 `EXPERIMENT_STATUS.json`、`PACKED_FORMAT.md`、`results/packed_check_20261022_v2.json`。完整持续目标尚未完成。

1. U280 基线已经完整保存：`data/netlist/routeracc_cost_u280_20261022_v1/capture.json`，placed.dcp、routed.dcp、利用率/路由状态/时序报告齐全。1,833 原语、1,277 可布线网全部完成、0 路由错误。内部 WNS 6.530 ns、WHS 0.020 ns；外部 168 输入/175 输出无 IO 延迟约束，不能称完整时序签核。MCP 消失实际由 WebTalk/libudev 崩溃引起；仅对子进程 `LD_PRELOAD=/lib/x86_64-linux-gnu/libudev.so.1` 后正常退出，成功日志 `results/vivado/resume_u280_20261022_preload.log`。不要重跑并覆盖基线。
2. 从放置/布线后的 U280 网表导出真实源/目标 site pin、规范节点、参考 PIP 路径以及其他 net 的占用/保护表。两端点/多端点、局部连接、未知边界与失败状态分别验证。该工作负载是现有 RouterAcc cost_calculator 的寄存器包装，不是压缩加速器，也不是生产规模基准。
3. 以独立 U280 训练/评估资源接入同一搜索与成本/占用模型，验证回写路由、route_status、DRC、时序与端到端成本。VU13P 冻结库不能无说明当成 U280 同器件模型。
4. 实现匹配的 CSR/模板 FPGA 后端，完整语义 testbench，C/RTL 仿真、综合、实现/时序。HLS 必须先读匹配 Ross Skills，2022.2 用兼容 Tcl 流程。
5. 实卡 DDR/HBM 仍需可用 U280 与平台包；当前 XRT 为 0 卡。只将实际已完成项更新为完成，不用微基准代替全目标。

第三轮复现：`python3 scripts/run.py packed-check`；回归：`python3 -m unittest discover -s tests -v`。35 项已通过。保留负结果：总文件仅缩小 2.09%，直接模板比 CSR 慢；全展开快的部分必须计入准备与分配。v1 的 getrusage 内存数不可用，v2 已纠正为 VmHWM。

以下为上一轮历史上下文（其中“下一轮”条目 1–3 已由第三轮完成）：

# 方案 A 继续研究入口

2026-10-22 已完成两轮真实器件实验。先读 `results/README.md`、`configs/region_query.json`、`EXPERIMENTS.md` 和 `AGENTS.md`。

```bash
python3 scripts/run.py check
python3 scripts/run.py smoke
python3 scripts/run.py real-check
python3 scripts/run.py region-check
python3 -m unittest discover -s tests -v
```

当前最终报告为 `results/region_check_20261022_v2.json`，26 项回归通过。原始源码与其他方案目录未修改。

## 已完成，避免重复当作新进展

- 首轮规范邻接：534 个源节点、5,005 个规范节点、4,886 条有向边；例外、方向、并行边、属性、别名及 11 种故障注入通过。
- 冻结模板留出：SLR0 384 行拟合 110 个模板，随后加载 SLR1–3 828 行。478 行直接精确，183 行属性例外，167 行连接例外；补齐后全部精确，25 个跨 SLR 节点被覆盖。
- 搜索域：3 个源、四跳域，深度 0–3 共 229 个源已完整展开；875 个规范节点、1,076 条有向边，646 个深度 4 节点未知邻接。
- 同一单位跳数 BFS：16 个查询的 CSR/原始模板/预处理模板路径、状态和 trace 一致。12 个一至四跳查询计时，另有四个语义探针。
- CPU 负结果：7 次驻留批次中位时间 0.625 / 20.956 / 2.891 ms；相应 provider 初始化 1.063 / 0.579 / 10.759 ms。预处理消除了每次查询的 JSON/深拷贝主开销，但仍慢于 CSR。
- 泛化缺口：搜索域 186/229 行属于未见 family，显式回退 820 条规则。规则类型采样与实际搜索访问分布不同。

## 下一轮优先做什么

1. **用独立训练搜索域改善模板覆盖。** 在 SLR0 选择与本轮等价规则的 BFS 起点/深度，采集真实访问行；与当前 intent 代表点训练比较。冻结训练库后再测，不把已有 SLR1–3 评估结果反过来直接加入训练。当前评估区域已被多次观察，若调整策略需预先登记新的未见区域作最终留出。分别报告已知 family 精确率、连接/属性例外、未知 family 回退和访问加权回退率。
2. **定义紧凑二进制布局并测完整成本。** 当前模板、节点、别名与属性都是 Python/JSON 审计表示。设计全体表、索引、对齐、例外、回退与规范映射；使用真实分配/序列化后的字节数，不能从模板数推压缩率。将属性补丁与连接例外分层，避免 SPEED_INDEX 改动导致整条规则 remove/add。
3. **沿已保存轨迹测试邻接访问。** 首先比较显式 CSR、预处理共享规则以及 packed decode，保持邻接排序、PIP 身份、方向和访问次序一致。初始化、首轮、驻留、回退及整批成本分别计时；保留无收益结果。
4. **接入真实网表 source/sink、约束与完整搜索。** 当前查询由真实器件连通性构造，并非实际网表任务。需要运行时数据/轨迹，或另行导出小型放置后设计；增加规范资源占用、受保护资源、合法性/拥塞与时序模型。不能将四跳未知边界当 sink。
5. **证据支持后再缩定硬件范围。** 目前尚不能从 Python 差异推断 FPGA 收益。先依据 packed 格式与访问热点选择规范映射、例外索引、模板读、邻接流或缓存，再使用适用 Ross Skill 与 Vivado 2022.2 流程。

## 仍然存在的边界

- 冻结模板的“补丁后精确”仍依赖评估真值，不是无数据库的预测。
- 跨 SLR 源分组不代表独立器件，物理导线/目标可以跨组；当前训练源、留出源无 ID 重叠。
- 扫描 36 tile / 62,136 PIP 未命中 excluded，真实网表保护与动态占用仍未验证。
- `.rdv/.atc`、RapidWright 运行时、真实网表轨迹未在原始包中找到，原 C++ router 未接入。
- 无 GPU/FPGA/板卡/时序质量结论；U280、XRT 与平台包仍待实际环境核实。

适配与改写保留在本目录。阶段和待确定项不是审批流程，按已有授权自主推进。
