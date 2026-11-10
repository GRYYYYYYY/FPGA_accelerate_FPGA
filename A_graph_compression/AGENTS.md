## 2026-11-08：原 O0 日志推进至约 410.588 ms

- 原 O0 PID3191525 身份重新核验有效，固定日志新增 `1 / 4 @ 410587778000 ps`，由此前约360.588ms推进至410.587778ms，仍1/4；无RTL退出回执、输出快照或所检查的资源终止原因。证据保存到 `data/derived/native_o0_410ms_observation_20261108_v1/observation.json`，原日志快照SHA256为 `2beb3c91abe4672ba8bf3ddd7b32bafbc1972fa053aef0e7d87b14fdb0e5f8b3`。这是非原子只读观察，不是完整绑定审核、当前内部状态或功能验收。
- 同次O2 PID576099身份有效，step2761、时钟55219974、第一段扫描2034480、第二段2097152、0/4；无RTL退出回执、独立审核报告或终态回执。原native及三个接续监督身份有效，后三项仍等待各自前置验收。保留既有运行、冻结输入和原门槛，不重复启动；交接入口仍为 `HANDOFF_20261107.md`，下方旧采样仅为历史记录。

## 2026-11-07：再次切换账号前的交接入口

- 后续现场更新：v29 已记录原 O0 **1/4 事务完成、约360.588ms**，PID3191525 身份有效；尚无 RTL 退出回执或输出快照。v30 最近实查 O2 step2208、第一段扫描618816、第二段2097152、0/4，PID576099 身份有效；无 RTL 退出回执、独立审核报告或终态回执。三个接续监督身份有效且仍等待前置验收。下述09:47记录为历史快照；首事务完成不代表完整功能验收，继续现场核验，不重启任务。
- 新会话先读 `HANDOFF_20261107.md`，优先于 11 月 6 日历史交接；现场观察保存到 `data/derived/account_handoff_20261107_v1/observation.json`。记录时间 09:47 UTC，原容器和 `/tmp`、`/proc` 可访问，O2/O0、native 监督与三个接续监督身份有效；未停止、重启、替换后台任务，未改冻结输入或验收门槛。
- O2 最近 step2042：时钟40839974、第一段扫描193863、第二段2097152、0/4，无 RTL 退出回执/独立审核报告/终态回执。O0 日志约350ms、0/4，无退出回执和输出快照。仅记录时刻观察，不是功能接受或当前内部状态。
- 切换后先确认原环境再运行 v30/v29；项目位于 GPFS，但活跃 trial 在容器 overlay 的 `/tmp`，保留原容器与临时目录。PID 不可见或权限不足不等于任务失败，禁止据此重启。当前接续仍依赖 O0；O2 若先通过须先完整复核并版本化接续，保证单执行 owner。

## 2026-11-07：原 O0 最新日志推进至约 350 ms

- v29 重新核验原 XSim PID3191525 身份一致，日志从此前约300ms推进至约350ms，仍0/4；无RTL退出回执或输出快照。日志变化证明已记录的仿真时间推进，不是事务接受或当前内部状态。所检查的资源终止原因为空，三个接续监督身份有效并继续等待前置验收。
- 同轮O2 PID576099身份有效，最近step1987的本轮第一段扫描索引53088、第二段2097152、0/4；无RTL退出回执、独立审核报告或终态回执。保留两项运行及原门槛。

## 2026-11-07：交接后恢复，O2 已观察到扫描索引转换

- 已保存固定原日志及只读观察到 `data/derived/native_o2_scan_transition_20261107_v1/observation.json`，日志快照 SHA256 `5b82db8b28f9038f90ff3769fd4ae76814d89a5b440c0af46ad1209fe851b8b7`。1975 组完整采样中，step1965/1966 的 trace 子模块 `ap_done=1`、`ap_start=0` 且两个索引均2097152；step1967 转为 `ap_start=1`、`ap_done=0`，第一索引1888，随后step1968/1969为4448/7008。对应现有runner的探针7/8/9/10；证明所采trace子模块出现完成与再次启动的序列，不是顶层事务完成。原始X/Z保留，仅已知十六进制索引参与变化比较。
- 用户已恢复目标；交接文件中目标暂停属于历史状态。交接后实查原 O2 PID 576099、原 O0 PID 3191525 和三项接续监督身份均有效，现有 `/tmp` trial 可访问，无需重复启动。
- O2 step 1974 采样：第二段扫描索引 2097152，第一段索引 19808，完成 0/4，表明相对交接时第二段已到末值且第一段索引再次变化；仅是观测值，尚不能据此确认完整事务或推断剩余工作。无 RTL 退出回执、独立审核报告或终态回执。
- O0 最新记录约 300.000163 ms、0/4，仍在运行；bus64/full50/full30-read 监督仍等待各自前置验收。继续使用 v30/v29 检查实际状态，保持冻结输入、既有进程和原验收门槛。

## 2026-11-06：跨账号交接

- 先阅读 `HANDOFF_20261106.md`，其中记录了当前后台进程、临时目录、接续门槛和换账号可能导致的容器/权限风险。用户已暂停当前目标；不要将目标暂停误认为后台进程已经停止。
- 新会话先核实同一容器、`/tmp` 和 `/proc` 可见性，再运行 `python3 scripts/experiment_status_v30.py` 和 `python3 scripts/experiment_status_v29.py`；禁止仅根据 PID 缺失或旧快照判断失败并重启。

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

## 2026-11-03：完整 O2 四态运行已启动，使用 v30 查看新任务

- 新O2已实际采到100us和200us：初始化索引5575→15575、clk_cnt19974→39974，仍0/4；两次采样墙钟间隔97.876秒，仅该初始化窗口约204.34周期/墙钟秒，不能外推trace阶段或完成时间。首个100us的7个共同探针与历史O2的100us逐值一致，报告`results/native_o2_full_run_first_sample_20261103_v1.json`；不是事务接受。新O2与原O0实际身份均重新核实有效。
- `scripts/run_native_o2_full_rtl_v1.py` owner554290/starttick1688359826已启动；独立trial `/tmp/A_graph_compression_recovery_20261025_v1/native_o2_full_rtl_20261103_v1`，实际xsimk576099身份由该trial的`rtl.actual_limits.json`记录并已重新核实。启动记录`data/derived/native_o2_full_rtl_preparation_20261103_v1`。先读实际state/receipt/proc，禁止重复启动或编辑已绑定runner/checker。
- 复用现有O2编译及独立短窗口审核的快照，完整重读311输入/快照绑定、原compiler审核并复制完整输入。**此次完整运行未采用任何FSM常量或内存初始化改写**；四态XSim2022.2、4事务/44指针/30模型、原全部容量/guards/C后检查保持。AS96GiB/stack256MiB/core0，新OOM/reset停止自有子进程；原O0运行和原接续监督均未替换。
- 新Tcl每100us查询13项只读信号，包括完成数、时钟计数、初始化索引、两段trace扫描索引。最多累计10秒仿真上限，完成4事务后退出；45天墙钟只是运行保护上限，不是完成时间预测。完整运行结束自动执行原C后检查，再调用`check_native_o2_full_rtl_v1.py`独立复核四份各946498280字节快照、原/fresh C、25原始输出、4条正周期和全部绑定/回执。预期报告`results/native_o2_full_rtl_audit_20261103_v1.json`；未实际生成通过前不得计验收。
- 只读`python3 scripts/experiment_status_v30.py`显示O2实际身份和最新完整采样；`--json`同时保留v29原链状态。采样时刻的寄存器值不等同于当前内部状态，报告存在也不等于审核回执通过。O2通过后的接续门槛尚未改接；需届时版本化处理，不能伪造旧native接受报告或形成两个执行owner。
- 新`scripts/program_u280_xclbin.py`为离线准备/显式执行的XRT用户镜像加载入口，默认不打开板卡，要求指定BDF和预期SHA256，以xclbinutil检查文件；`--execute --output NEW_DIR`才调用xbutil program并保留回执。仅准备了加载代码，没有生成当前核的最终xclbin，也未烧写、闪存更新或上板验收。离线3项拒绝检查在`data/derived/u280_programmer_offline_checks_20261103_v1`。

## 2026-11-03：辅助后端兼容性路径已拒绝，保留证据

- Verilator原154源码预检900秒超时，未执行RTL。独立十六进制常量归一化核63882个同宽同值one-hot常量及逐字节逆变换；原源码不变。hex预检148.735秒因64GiB AS限制std::bad_alloc退出，没有新增cgroup OOM。
- 私有30个AXI模型的四页数组零初始化改成静态初始化函数：容量/页数/地址/时序逻辑不变。XSim2022.2的6项四态测试（32/64/512位、17/257深度、四页初值及X/Z后续写）通过，证据`data/derived/native_memory_initializer_contract_20261103_v1`，仅支持初始化改写的局部契约。
- 完整static-init预检30.395秒到达45项`Unsupported tristate construct: INITITEM`错误，全部位于原AXI控制TB的image_mem_* Z初值。其Z用于首次寄存器写的!==比较，不能简单改零。工具虽有--fourstate，但实际警告不受支持/开发中，完整v4仍报同样错误，小型Z数组复现又报不支持与内部错误。故未进行Verilator全运行、未关闭X/Z检查，也未将其当验收后端；v1-v4日志/退出回执全部保留。原O0及新完整O2输入均不受这些试验改动。

## 2026-11-03：用户明确当前优先完成 RTL 验收，板卡先准备部署代码

- 用户说明 U280 尚未插入；本阶段准备部署/烧写代码即可，不把未插卡作为 RTL 验证工作的阻塞项。先解决完整 RTL 尚未验收的问题，实板测量留待插卡后。
- `data/datasets.json` 中两个旧 pending 项只能说明尚未在该清单登记，不能推断整个项目缺真实数据。已有真实器件图、放置网表和当前完整 RTL 输入；禁止再用这两项 pending 解释当前 0/4。
- 原 native 进程本轮身份核验有效，运行约94小时、最近日志150ms/0事务；只读 `/proc/PID/mem` 被系统拒绝，没有附加调试器或改变原进程。原测试台在4事务完成后自动 `$finish`；`run 10 sec` 不是必须跑满的时长，但其后的探针无法实时报告进度。
- 新增独立 `scripts/probe_native_verilator_v1.py`，核对原154份源码和4事务/44指针/30模型范围，以AS64GiB/stack256MiB/core0、900秒墙钟上限、OOM/reset自有进程清理运行兼容性预检。输出 `data/derived/native_verilator_compatibility_20261103_v1`，以实际state/receipt判定，不能将预检当作执行通过。原XSim及全部冻结DUT/输入/checker保持。
- Verilator wheel包元数据5.48.0，下载SHA256 `37c4baba6a268f6e0a15b4917dbbc45dcf23ddea1498d059f8259a34072ac427`，本地二进制自报 `rev vUNKNOWN-built20260516-4e853d8`，位置 `/tmp/A_graph_compression_tools/verilator_5_48_0`。该辅助后端的二态语义不能覆盖原X/Z检查，不得直接替代原XSim验收或改写接续门槛。

## 2026-11-02：native RTL 日志推进至约 150 ms

- `python3 scripts/experiment_status_v29.py` 实时核验原 native PID3191525 身份一致，最新日志由约 100 ms 推进至约 150 ms，仍为 0/4 事务；无 RTL 退出回执或输出快照。日志证明仿真时间推进，但不证明事务通过或当前内部仿真时间。
- native 监督运行中，bus64、full50、full30/read 接续监督身份有效并等待各自前置验收。保留原运行及冻结输入，不重复启动；完整 RTL、物理实现与上板验证仍未完成。

## 2026-11-02：trace可信存活计数提前停止的真实数据可行性筛查

- 新scripts/analyze_native_trace_live_scan_v1.py，按已审核mode0 CPU trace、完整44端口快照及固定测试中的77/节点1种子，独立重建3个有效事务的8条net操作及哈希表。各条node_meta[2]与重建存活项数一致、owned_keys顺序一致；三个事务末的全部2097152个flags及非零槽位keys与完整快照一致。脚本AST及实际哈希碰撞、墓碑重用检查通过。
- results/native_trace_live_scan_reconstruction_20261102_v1.json SHA256=6803d77deb32d734f4900467ffe57f46006e2f818f5606787c14d3b9d0177463。若使用可信存活总数在找到所有live项后停止，case0两net每次槽扫描由2097152降到1443136（少31.19%）；case1四net为2024189（少3.48%）；case2两net为348919（少83.36%）。这是从真实CPU状态推演的迭代数，不是RTL周期或端到端性能。
- 该候选依赖NodeOccupancy所述可信、互不重叠且独占状态及meta[2]准确；元数据和flags不一致时可能改变行为，不能声称对任意外部输入等价。四事务中的invalid case不属于本3个有效事务，尚需专门覆盖错误/容量/原样输出和全部原功能门。尚无候选HLS代码/综合/RTL，不改原运行及冻结checker。
- 已阅读hls-pragma-scope与hls-optimize及其init要求；本机2022.2有vitis_hls但无vitis-run，插件未暴露对应HLS报告工具，且完整cosim/post-route基线尚缺，不能按该技能宣称HLS优化或测得改善。后续若采用2022.2批处理替代，必须另建隔离候选、证明可信状态不变量和字节级差分，再按原完整范围C/HLS/RTL/physical验证。当前原native继续0/4，完整实验未完成。

## 2026-11-02：O0/O2重复100us对照完成并独立复核

- 原诊断owner3414115已complete并退出；四次O0/O2/O2/O0实际exit0/无abort，各20采样×21探针逐值一致。O0耗时353.105895/353.426002秒，中位353.265948秒；O2耗时305.946727/306.091316秒，中位306.019021秒，O2/O0=0.8662567759，即此窗口耗时低约13.37%。
- 原报告results/native_xsim_optimization_diagnostic_20261102_v1.json SHA256=232cc8b9b2658bbd4d84650dfd83b34ee8d89358af8002000e55635a30cdb3e3；新增独立复核results/native_xsim_optimization_independent_audit_20261102_v1.json SHA256=3ffe578fc49991e45fcca1e4f4ddc2d9f1edc4f3c1a71486d31bf89908dee729。重读报告全部文件及311项运行输入/快照绑定，独立解析每条采样、唯一结束标志、回执/log SHA、两项编译命令差异与中位数计算。
- 比较只覆盖100us早期初始化、含启动和探针查询、共享主机负载及缓存不受控；不能证明全事务/全输出等价或对后续trace扫描及端到端加速作外推。O2编译本身3377秒、峰值156774092KiB；不因本诊断替换/中断已运行69小时的原完整RTL或变更其接续gate。原native仍0/4，全部功能链、physical及board等缺口保持。

## 2026-11-02：两次O2短重放完成，最后O0进行中

- replay_2_O2 exit0/无abort/306.091秒，日志SHA和唯一完成标记已核；此前O0、两次O2的20采样×21值重新解析全部一致。三次分别约353.106/305.947/306.091秒，含启动和查询、共享主机，最终重复比较尚待第二O0和完整绑定重核，不能外推全程或计功能通过。
- owner3414115已进入replay_3_O0，实际xsimk671111/starttick见actual_limits并核身份；原native仍有效0/4。完整实验未完成。

## 2026-11-02：首次O2短重放完成，第二次O2进行中

- replay_1_O2实际exit0/无abort/305.947秒，日志SHA及唯一完成标记重核；与replay_0_O0的20采样×21值逐项一致。两次分别含启动和查询，只是100us早期窗口且共享主机负载不控，不是完整功能接受或重复性能结论。
- owner3414115已自动进入replay_2_O2，实际xsimk566360/starttick1679213846身份有效；之后仍需第二O2、最后O0完整重放及逐值核查，最终性能报告当前尚无。原native实际仍运行0/4，完整实验未完成。

## 2026-11-02：首次O0短重放完成，首次O2短重放进行中

- optimization诊断replay_0_O0实际exit0、无abort、353.106秒，回执log SHA和唯一完成标记已核；重新解析其20采样×21值，与原O0短重放全部一致。此为100us早期诊断，非四事务接受。
- owner3414115已进入replay_1_O2，实际xsimk460948/starttick及96GiB AS/stack256MiB/core0实核；初始采样21值与O0初始采样一致，完整O2窗口尚未结束。后续依次另一O2、另一O0；需保留完整比较和共享主机/计时限制。原native仍有效、最近0/4；完整实验未完成。

## 2026-11-02：独立O2编译成功，重复短重放已开始

- native_xsim_optimization_diagnostic_v1的xelab3425427已退出；elaborate_O2.receipt.json实为exit0、无abort、3377.077秒，日志SHA256=ac9589e7cb7a4c2451ed9bb5e706c505bd5f51f0010d0f3f7020d8d11deab0d8且Built simulation snapshot，peak RSS=156774092KiB，未新增OOM。实际O2 kernel SHA256=77b9e2b1dec7e2420fc0391048c1eeab822d838d11bb730f5b478b854f5004e7；这是编译成功，不是RTL功能接受或性能结果。
- 原诊断owner3414115自动进入replay_0_O0，实际xsimk339431/starttick1679146051及AS96GiB/stack256MiB/core0已核；完整顺序O0/O2/O2/O0，逐次20采样×21信号须匹配历史O0。当前无短重放完成回执或最终性能报告，不重启/编辑活跃driver。
- 原native3191525仍运行，最后0/4 @100000143000ps，接续监督等待原独立验收。原9要求8变体、physical及板卡缺口保持，完整实验未完成。

## 2026-11-02：已完成O0短重放的输入及快照未变

- 为提前核验正在运行的O0/O2诊断的完整性假设，只读比较原已审核compiler trial与已完成的native_first_transaction_diagnostic_replay_v1：原快照9文件逐SHA一致、无缺失；重放新增5个运行时文件。原compiler plan的293项输入在重放后逐SHA一致、无缺失（约6.91GB）。未修改活动trial或checker。
- 这只说明实际O0短重放未改写原有快照和输入，不能证明O2的文件行为、功能等价或事务通过。O2诊断仍运行，状态和进程须重新实查；原native及接续链不变，完整实验未完成。

## 2026-11-02：独立O2编译与重复短窗口性能诊断已启动

- 新scripts/benchmark_native_xsim_optimization_v1.py，owner3414115/starttick1678802546，控制记录data/derived/native_xsim_optimization_diagnostic_20261102_v1；实际输出/tmp/A_graph_compression_recovery_20261025_v1/native_xsim_optimization_diagnostic_v1。已全读原编译独立gate、核原诊断证据、复制原plan实际列出的764文件及空目录；不修改原native活跃输入/快照或接续链。
- 当前实际xelab3425427/starttick1678806056，阶段elaborate_O2，/proc身份/argv及AS192GiB/stack256MiB/core0已核。同2022.2、全4事务44指针30模型与原DUT/ROM/guards，只将编译--O0改--O2并使用独立snapshot名；仍-mt off。无raw-free门槛，新OOM/reset只停止本诊断自有进程。编译墙钟上限7200秒，后续各次RTL诊断1800秒、AS96GiB。
- 编译成功后自动O0→O2→O2→O0四次独立进程、相同100us Tcl与21只读探针；每次20采样必须逐值匹配原O0短诊断，全原输入及两个快照受哈希保护。任何缺探针/值不符/异常即失败，不降低可观察范围。计时含启动和查询，共享主机/缓存不受控；即使成功，也只比较早期初始化，不证明首事务、后续trace扫描、完整功能等价或板上性能。
- AST、真实原日志解析及缺探针/重复采样/缺窗口拒绝通过；原日志包含Tcl回显，准备测试最初替换到回显导致用例未改变实际采样，已改为只改真实采样行；完成标记也精确匹配真实行而不计回显。未修改冻结原checker。
- 预期结果results/native_xsim_optimization_diagnostic_20261102_v1.json当前不存在，无提速结论。脚本/plan现冻结，勿重复启动；v29尚不展示此独立诊断，需另核上述state/actual_limits/receipt及/proc。原native仍运行0/4，原9要求8变体及全功能/physical/board缺口保持。

## 2026-11-02：30秒原进程调度观察未见资源等待瓶颈

- 原native PID3191525/starttick1654203702采样前后身份一致。只读证据results/native_scheduler_sample_20261102_v1.json，SHA256=5a68f0d7eaf7c801f82f3842094b6caff0b49ccce7068541761d17af524d36f2；未修改原运行。
- 30.0317秒窗口worker3191528运行约30.0318秒、runqueue等待0.000067615秒；进程用户态30.01秒/内核态0.02秒。无新增cgroup限流/OOM/memory或IO pressure，进程磁盘读写字节及major faults增量0，minor faults增33589。窗口内主要消耗用户态CPU，不是CPU排队或磁盘等待证据；微小比例超1来自非原子读取时差，不能推广为完整运行归因。
- 本机perf/pidstat/gdb/pstack不可用、perf_event_paranoid=4，未获得函数级profile，FSM/AXI等各因素占比仍未知。原RTL与三个接续监督继续有效，最近0/4；无新功能接受，不重启/替换冻结输入与快照。完整实验及原9要求8变体缺口保持。

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

## 2026-11-02：trace提前停止的可信状态边界已实证

- tests/test_trace_live_count_contract.cpp以原小容量Trace/Node运行通过：人为将2个live项的meta[2]改为0后，valid_meta仍为真，原trace仍按flags记录2项，除序列化meta外输出不变。该注入违反NodeOccupancy可信状态契约，不是实际损坏。batch顶层reset_state=0接受外部状态且只做元数据范围检查；不能把范围检查视为flags计数一致性证明。若采用提前停止，必须明确/证明可信状态调用链或保留不可信状态原行为；尚未修改DUT或实现候选。详细命令及SHA见NEXT_STEPS.md，原RTL与接续链保持，完整实验未完成。

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

## 2026-10-30：CPU六排列18项最终独立通过；原nonzero RTL地址检查失败，串行链已关闭

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

## 2026-10-30：CPU顺序补充14/18完成，第五组最后一项CSR已运行

- block_004/worker_002 compact/direct已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。11项artifact与原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0和顺序[1,2,0]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_004/worker_002/report.json` SHA256=a49fdc4295184d09836e9c5157964e1a0ede659a9f8a39733a186a40c2f3c9f0；outer receipt SHA256=5d110f3413d4282eddb8f403ae22ebbfef59221c7f311ed5b5cfc9e4a6518f4d。
- application=1594.725875974秒，完整输出核对另耗234.375022070秒。当前14/18 worker完成、4/6独立组通过，第五组audit.json仍不存在；须等最后CSR完整输出和原整组checker，不提前计第五组通过或形成完整补充性能结论。全部六排列18项、原9要求8变体保持。
- 旧worker1491212/native1516682均已退出；原监督2624526（句柄27488）/driver2660361自动进入block_004 position2 csr/direct worker2064317/starttick1649524887、native2083780/starttick1649530975，已实读/proc核实际argv/CPU121/AS16GiB/core0。下一轮重新核身份，不沿用旧1516682；观察入口仍v19。
- 原RTL2005478继续运行、最近0/4，未新增OOM；原完整功能链与physical/board等缺口保持，完整实验未完成。下方13/18及第五组第二项活跃信息为历史，CPU日志round/batch解释纠正继续有效。

## 2026-10-30：CPU顺序补充13/18完成，第五组第二项已运行

- block_004/worker_001 compact/expanded已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。11项artifact与原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及顺序[1,2,0]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_004/worker_001/report.json` SHA256=b34493e9a4fb89d7a3b70f0aa6348ef48e3fbcd06ad1534ef431fe89e55d86dd；outer receipt SHA256=4bbc35ad666a85fccb0c1476f65d7129dd72113eb4e7fcacf205a1c4cea24750。
- application=999.201088604秒，完整输出核对另耗234.494706227秒。当前13/18 worker完成、4/6独立组通过，第五组audit.json仍不存在；尚需compact/direct、CSR及原完整组审核，不提前计第五组通过或形成完整补充性能结论。全部六排列18项、原9要求8变体保持。
- 旧worker1064901/native1095112均已退出；原监督2624526（句柄27488）/driver2660361自动进入block_004 position1 compact/direct worker1491212/starttick1649341000、native1516682/starttick1649349064，已实读/proc核实际argv/CPU121/AS16GiB/core0。下一轮重新核身份，不沿用旧1095112；观察入口仍v19。
- 原RTL2005478继续运行、最近0/4，未新增OOM；原完整功能链和physical/board等缺口保持，完整实验未完成。下方12/18及第五组首项活跃信息为历史，CPU日志round/batch解释纠正继续有效。

## 2026-10-30：CPU顺序补充第四组独立通过，第五组已启动

- `data/derived/training_order_control_20261029_v1/block_003/audit.json`已为all_source_to_route_integration_trials_audited、3/3，原checker完整重新核三个条件各两批1062网输出。报告全部43文件SHA另行逐项重读通过，完整绑定集合与三worker artifacts/报告/提交/退出回执及组plan/report相同，计时字段和顺序[0,2,1]非重叠回执另核一致；原auditor SHA=c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5保持。audit SHA256=90ef25f0f1cc2a8277c59b7bfdd1ff7e30b5c10823cd30ea863fc77102b52eb1；audit.log SHA256=0c068f295317716f81f6badc89ec221736608cf79b5810cc8e7dc3b6504ced9c。
- 第四组checker810147已退出；原监督2624526（句柄27488）/driver2660361自动进入block_004顺序[1,2,0]，即compact/expanded→compact/direct→csr/direct。新plan的files/expected_inputs/jobs与前组完全一致。首项worker1064901/starttick1649216673、native1095112/starttick1649224668已实读/proc核argv/CPU121/AS16GiB/core0；下一轮用`block_004/worker_001/native.submission.json`与实际/proc重新核身份，不沿用第四组旧进程。
- 当前12/18 worker完成、4/6独立组通过，第五组首项仅运行，不计完成。仍须完整六排列18项及最终独立审核，补充结果不与原7组混池，不从四组提前形成完整性能结论。原RTL2005478继续运行、最近0/4，未新增OOM；原9要求8变体、完整功能链及physical/board缺口保持，完整实验未完成。观察入口仍v19；下方3/6及第四组checker运行信息为历史。

## 2026-10-30：CPU顺序补充12/18完成，第四组原独立审核已运行

- block_003/worker_001 compact/expanded已通过原worker完整两批各1062网输出校验，native和外层worker均exit0。11项artifact及原compact参考另行逐文件SHA重读通过，1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及顺序[0,2,1]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_003/worker_001/report.json` SHA256=c08b90fb4eeac76d5c232dc387bf275a3c20615d9d9b7f32ed56f1172ef3d88b；outer receipt SHA256=f3b8a7847acdf4320136d4271018d9c9aa20a569eb90fb6df114b86766c4eda1。
- application=1017.722897576秒，完整输出核对另耗236.889652146秒。当前12/18 worker完成、3/6独立组通过；第四组audit.json及block_004仍不存在，不提前计第四组通过或形成完整补充性能结论。全部六排列18项、原9要求8变体及不与原7组混池的限制保持。
- 旧worker370602/native399588均已退出；原监督2624526（句柄27488）/driver2660361自动进入original_full_block_audit。实际checker810147/starttick1649145036已逐/proc核cwd、完整argv且无--partial、CPU121/AS16GiB/core0；原检查器SHA仍c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。下一轮核该checker与第四组完整报告，不沿用旧计算进程、不另起checker。
- 原RTL2005478继续运行、最近0/4，未新增OOM；原完整功能链和physical/board等缺口保持，完整实验未完成。观察入口仍v19。下方11/18及第四组最后一项计算活跃状态为历史，CPU日志round/batch解释纠正仍有效。

## 2026-10-30：CPU顺序补充11/18完成，第四组最后一项已运行

- block_003/worker_002 compact/direct已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。11项artifact和原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及顺序[0,2,1]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_003/worker_002/report.json` SHA256=9d8ac675a2b1798122c49638fed824824274d4e30176664cadb083f99e1a456d；outer receipt SHA256=1624612deaec79163409e7a8ea2e6e5fcaf282464bf085ab63ebf0d6d0ad721a。
- application=1573.133521583秒，完整输出核对另耗234.276284767秒。当前11/18 worker完成、3/6独立组通过，第四组audit.json仍不存在；须等最后compact/expanded完整输出及原整组checker，不提前计第四组通过或形成完整补充性能结论。全部六排列18项、原9要求8变体保持。
- 旧worker3945682/native3974169均已退出；原监督2624526（句柄27488）/driver2660361自动进入block_003 position2 compact/expanded worker370602/starttick1649018306、native399588/starttick1649026702，已实读/proc核实际argv/CPU121/AS16GiB/core0。下一轮重新核身份，不沿用旧3974169。观察入口仍v19。
- 原RTL2005478继续运行、最近0/4，未新增OOM；原完整功能链及physical/board等缺口保持，完整实验未完成。下方10/18及第四组第二项活跃信息为历史，CPU日志round/batch解释纠正继续有效。

## 2026-10-30：CPU顺序补充10/18完成，第四组第二项已启动

- block_003/worker_000 csr/direct已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。10项artifact和原CSR参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、CSR不训练的原语义、实际argv/CPU121/AS16GiB/core0和第四组顺序[0,2,1]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_003/worker_000/report.json` SHA256=b62f2a6168c424dbd74ead0136a8097f6199bccf041038dc8349d540f27fdba1；outer receipt SHA256=5217ed4061b46bc41820aa64d6bad7eae1f1f474515d0167aa73835a61f6dd32。
- application=1098.740113921秒，完整输出核对另耗231.744503522秒。当前10/18 worker完成、3/6独立组通过，第四组audit.json仍不存在；尚需compact/direct、compact/expanded及原完整组审核，不提前计第四组通过或形成完整补充性能结论。全部六排列18项、原9要求8变体保持。
- 旧worker3498402/native3518408均已退出；原监督2624526（句柄27488）/driver2660361自动进入block_003 position1 compact/direct worker3945682/starttick1648836422，新native3974169/starttick1648844698已从`block_003/worker_002/native.submission.json`和实际/proc核对；worker/native实际argv/CPU121/AS16GiB/core0均已核实。下一轮重新核身份，不沿用旧3518408。观察入口仍v19。
- 原RTL2005478继续运行、最近0/4，未新增OOM；原完整功能链和physical/board等缺口保持，完整实验未完成。下方9/18及第四组首项活跃信息为历史，CPU日志round/batch解释纠正继续有效。

## 2026-10-30：CPU顺序补充第三组独立通过，第四组已运行

- `data/derived/training_order_control_20261029_v1/block_002/audit.json`已为all_source_to_route_integration_trials_audited、3/3，原checker重新核三个条件各两批1062网完整输出。报告全部43文件SHA另行逐项重读通过，完整绑定集合与三worker artifacts/报告/提交/退出回执及组plan/report相同，计时字段和顺序[1,0,2]的非重叠回执另核一致；原auditor SHA=c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5保持。audit SHA256=4d1e885a429c88fc51be58a3605cfcefc9dfe86fc5f38c451577346279894c10；audit.log SHA256=0c068f295317716f81f6badc89ec221736608cf79b5810cc8e7dc3b6504ced9c。
- 第三组checker3246405已退出；原监督2624526（句柄27488）/driver2660361自动进入block_003顺序[0,2,1]，即csr/direct→compact/direct→compact/expanded。新plan的files/expected_inputs/jobs与前组完全一致。首项worker3498402/starttick1648702385、native3518408/starttick1648708377已实读/proc核argv与CPU121/AS16GiB/core0；下一轮重新核身份，不沿用第三组旧进程。
- 当前9/18 worker完成、3/6独立组通过，第四组首项仅运行，不计完成。仍须全部六排列18项及最终独立审核，补充结果不与原7组混池，不从三组提前形成完整性能结论。原RTL2005478继续运行、最近日志0/4，未新增OOM；原9要求8变体、完整功能串行链和physical/board等缺口保持，完整实验未完成。只读入口v19保持；下方2/6及第三组checker运行信息为历史。

## 2026-10-30：CPU顺序补充9/18完成，第三组原独立审核已运行

- block_002/worker_002 compact/direct已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。11项artifact与原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及顺序[1,0,2]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_002/worker_002/report.json` SHA256=e1603bb318d97ac07e59a751bf7e003754efcd78f50e1db9258ebf7d2541eb53；outer receipt SHA256=77857200f85eb3f6d0c6d88f451c7a2a942d244ba6cb5bc02029bc070ba5619a。
- application=1600.924263120秒，完整输出核对另耗238.301012194秒。当前9/18 worker完成、2/6独立组通过；第三组audit.json及block_003仍不存在，不能提前计第三组通过或形成完整补充性能结论。原六排列18项、9要求8变体及与原7组不混池的限制保持。
- 旧worker2617400/native2645430均已退出；监督2624526（句柄27488）/driver2660361自动进入original_full_block_audit。原checker3246405/starttick1648630162已实读/proc核cwd/完整argv且无--partial、CPU121/AS16GiB/core0；原检查器SHA仍c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。下一轮核该checker与最终第三组报告，不沿用旧计算进程、不另起checker。
- 原RTL2005478继续运行、最近日志0/4，未新增OOM；原完整功能链和physical/board等缺口保持，完整实验未完成。只读状态入口仍v19。下方8/18及第三组最后一项活跃状态为历史，日志round/batch含义纠正仍有效。

## 2026-10-30：CPU顺序补充8/18完成，第三组最后一项已启动

- block_002/worker_000 csr/direct已通过原worker完整两批各1062网输出校验，native和外层worker均exit0。10项artifact及原CSR参考另行逐文件SHA重读通过，1426871976个非metric语义值字节/四字段、原输入/counts、CSR不训练的原语义、实际argv/CPU121/AS16GiB/core0与第三组顺序[1,0,2]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_002/worker_000/report.json` SHA256=7248468bce293c72327f46c7a73a48880b5005f199d3bdd89d74c91429b216a8；outer receipt SHA256=a37c7a3f94a9a93af683a0c9dffd8309b9aca2002a4d441b349d9afa99306952。
- application=1098.324305454秒，完整输出核对另耗232.176048972秒。当前8/18 worker完成、2/6独立组通过，第三组audit.json仍不存在；必须等最后compact/direct完整输出与原整组checker，不提前计第三组验收或形成补充性能结论。全部六排列18项、原9要求8变体保持。
- 旧worker2143113/native2163692均已退出；原监督2624526（句柄27488）/driver2660361自动进入block_002 position2 compact/direct worker2617400/starttick1648445066，新native2645430/starttick1648453319已从`block_002/worker_002/native.submission.json`及实际/proc核对；worker/native实际argv/CPU121/AS16GiB/core0均已核实。下一轮重新核当前身份，不沿用旧2163692。观察入口仍v19。
- 原RTL2005478继续运行、最近日志0/4，oom=0/oom_kill=2无增加；原完整功能串行链和physical/board等缺口保持，完整实验未完成。下方7/18及CSR活跃信息为历史，CPU日志round/batch纠正继续有效。

## 2026-10-30：CPU顺序补充7/18完成，第三组第二项CSR已启动

- block_002/worker_001 compact/expanded已通过原worker完整两批各1062网输出校验，native及外层worker均exit0。11项artifact及原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及第三组顺序[1,0,2]的非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_002/worker_001/report.json` SHA256=04e652d0d971f3f6b3e12ca92f41f5a3a310cd95c01872e0ef2de7a698bd2c8f；outer receipt SHA256=cb1994d7ce6cab1d1306dd2df535b8323fd7552185a4226398f98ca1f60c4458。
- application=989.261957269秒，完整输出核对另耗232.604900096秒；当前7/18 worker完成、2/6组独立验收。第三组audit.json仍不存在；还需CSR、compact/direct及原整组独立审核。全部六排列18项保持，单项/两组结果不用于完整补充性能结论，不与原7组混池。
- 旧worker1717258/native1742584均已退出。原监督2624526（句柄27488）/driver2660361自动进入block_002 position1 csr/direct worker2143113/starttick1648310928，新native2163692/starttick1648317064已从`block_002/worker_000/native.submission.json`与实际/proc核对；worker/native的实际argv/CPU121/AS16GiB/core0均已核实。下一轮重新核当前身份，不沿用旧1742584。只读入口v19保持。
- 原RTL2005478继续运行、最近日志0/4，oom=0/oom_kill=2无增加，原功能串行链、9要求8变体和physical/board等缺口保持；完整实验未完成。下方6/18及第三组首项活跃状态为历史，CPU日志round/batch纠正继续有效。

## 2026-10-30：CPU顺序补充第二组独立通过，第三组已运行

- `data/derived/training_order_control_20261029_v1/block_001/audit.json`已为all_source_to_route_integration_trials_audited，completed_workers=planned_workers=3。原checker完整重核三个条件各两批1062网，原auditor SHA=c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5保持。报告全部43文件SHA另行逐项重读通过，完整绑定集合与三worker artifacts/报告/提交/退出回执、组plan/report相同，计时字段、原输入和串行顺序另核一致。audit SHA256=fc0a95d3b2703f5e09366f15caf281224ca8fb0fa91677c29b064122375821e0；audit.log SHA256=0c068f295317716f81f6badc89ec221736608cf79b5810cc8e7dc3b6504ced9c。
- 第二组checker1485890已退出，原监督2624526（句柄27488）/driver2660361自动进入block_002顺序[1,0,2]，即compact/expanded→csr/direct→compact/direct。新plan的原files/expected_inputs/jobs与第二组完全一致。首项worker1717258/starttick1648187792、native1742584/starttick1648195676已实读/proc argv及CPU121/AS16GiB/core0核对；下一轮重新核身份，不能沿用第二组旧进程。
- 当前6/18 worker完成、2/6组独立验收，第三组首项仅运行，不计完成。仍须全部六排列18项完成及最终独立审核后解释补充性能，不与原7组混池。原RTL2005478仍运行、最近日志0/4，未新增OOM；原9要求8变体、完整功能链及physical/board缺口保持，完整实验未完成。只读入口v19保持，下方1/6及第二组checker运行信息为历史。

## 2026-10-30：CPU顺序补充6/18完成，第二组原独立审核已运行

- block_001/worker_000 csr/direct已通过原worker完整两批各1062网输出校验，native与外层worker均exit0。10项artifact及原CSR参考另行逐文件SHA重读通过；1426871976个非metric语义值字节/全部四字段、原输入/counts、CSR不训练的原语义、实际argv/CPU121/AS16GiB/core0及第二组顺序[2,1,0]非重叠回执均核对一致。报告`data/derived/training_order_control_20261029_v1/block_001/worker_000/report.json` SHA256=a2c5a6840a46a2def6839ac7b1311a1778620eb8936f5c0aa094a3df6199ec7b；outer receipt SHA256=d844f3d06bcd7a08c20ecf5c9b535934922a8d23495cdd7a04b80dcd488038a4。
- application=1084.127768243秒，完整输出核对另耗230.387815878秒；当前6/18 worker完成、1/6组独立通过，第二组audit.json及block_002仍不存在，不能提前计第二组通过或形成完整补充性能结论。六排列18项、原算法/完整输出oracle和全部限制保持。
- 旧worker1057672/native1075344均已退出。原监督2624526（句柄27488）/driver2660361已进入original_full_block_audit，实际checker1485890/starttick1648116303已逐/proc核cwd、完整argv且无--partial、CPU121/AS16GiB/core0；原`check_source_to_route_with_training_v2.py` SHA仍c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。下次核该checker和最终组报告，不再沿用旧CSR进程，不另起checker。
- 原RTL2005478继续运行、最近日志0/4，oom=0/oom_kill=2无增加；原功能串行链、9要求8变体及physical/board缺口保持，完整实验未完成。观察入口仍v19。下方5/18及第二组CSR运行状态为历史，日志round/batch纠正继续适用。

## 2026-10-30：CPU顺序补充5/18完成，第二组最后一项CSR已运行

- block_001/worker_001 compact/expanded已通过原worker完整两批各1062网输出检查，native与外层worker均exit0。11项artifact及原compact参考另行逐文件SHA重读通过；1426871976个非metric语义值字节、四字段、原输入/counts、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及顺序[2,1,0]非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_001/worker_001/report.json` SHA256=28e4984a1c5e4099a4d510138d5c991a00bf0623e2b8e4561bf61891e8dbfa78；outer receipt SHA256=4ea8a8cd73784df39eddcac1cfe36be2a2f3b09455e36e27e8550a55bad2adc2。
- application=995.507300057秒，完整输出核对另耗232.237270279秒；当前5/18 worker完成、1/6组独立通过，第二组audit.json仍不存在，不能提前计为第二组通过或推断补充性能结论。原六排列18项及独立原block checker保持。
- 旧worker659505/native684636均已退出。原监督2624526（句柄27488）/driver2660361自动启动block_001 position2 csr/direct：worker1057672/starttick1647983968、native1075344/starttick1647989830已实读/proc argv与实际CPU121/AS16GiB/core0核对；下次重新核实时身份。当前只读入口v19，原RTL2005478仍运行、最近日志0/4，oom=0/oom_kill=2无增加，三个下游监督身份匹配且等独立前置。
- 下一步等待CSR完整输出和本组原checker，然后按冻结顺序继续。原9要求/8变体、完整RTL串行链及physical/board等缺口保持，完整实验未完成。下方4/18及第二组第二项运行信息为历史；CPU日志round不是batch的纠正仍有效。

## 2026-10-30：CPU顺序补充4/18完成，第二组第二项启动

- block_001/worker_002 compact/direct原worker完整两批1062网输出校验通过，native及外层worker均exit0；11项artifact及原compact参考另行逐SHA重读通过。完整1426871976个非metric语义值字节/全部四字段、原容量和生成输入、3761训练源/440模板/bank、实际argv/CPU121/AS16GiB/core0及第二组顺序[2,1,0]的非重叠回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_001/worker_002/report.json` SHA256=c6d744553da2c633b6fe0e046326763017376a2219468afb776c0076c76d4afd；outer receipt SHA256=75b187b88d6a16c09fc49bba2d6ce2e0d568b9be4060582240963be965f96876。
- application=1605.042915750秒，worker完整输出核对另耗234.280100368秒；尚无补充实验完整性能结论。当前4/18 worker完成、1/6组独立通过；第二组audit.json未生成，须等本组三项完成再由原checker审核。第一组43绑定验收事实和报告保持。
- 第二组首项worker77421/native102261均已退出。原监督2624526（句柄27488）/driver2660361自动启动block_001 position1 compact/expanded worker659505/starttick1647860142，实际argv/CPU121/AS16GiB/core0已核。下一轮从该worker的`native.submission.json`与实际/proc读取新native身份，不沿用旧102261。只读入口仍v19，原RTL2005478继续运行、最新0/4、未新增OOM。原六排列18项、9要求8变体、完整RTL链及physical/board缺口保持；下方3/18和第二组首项运行状态为历史。

## 2026-10-30：CPU顺序补充第一组独立验收通过，第二组已运行

- `data/derived/training_order_control_20261029_v1/block_000/audit.json`已为`all_source_to_route_integration_trials_audited`，completed_workers=planned_workers=3。原checker逐完整输出重新校验三条件各两批1062网、原训练/输入/计时范围；auditor SHA保持c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。报告全部43文件绑定已另行逐文件重读，完整集合与三个worker artifacts/提交/退出回执及组plan/report一致，实际CPU/AS记录和串行顺序另核通过。audit SHA256=33c1834d8b2d53b00b4256baca9d8608b6bc355b022315a93c10c00cf27357f2；audit.log SHA256=0c068f295317716f81f6badc89ec221736608cf79b5810cc8e7dc3b6504ced9c。
- 第一组checker4050806已退出，driver2660361已按冻结顺序[2,1,0]进入block_001。当前第二组首项compact/direct worker77421/starttick1647675255、native102261/starttick1647683319实读/proc argv/starttick匹配，实际CPU121/AS16GiB/core0核实；监督2624526及工具句柄27488保持。当前3/18 worker完成、1/6组独立验收，不能把下一组已启动计为完成。
- 后续继续第二组compact/direct→compact/expanded→csr/direct及其原独立组审核，保留全部六排列18项。已有1组不作为补充性能结论，不与原7组混池；最终完整18项/6组验收仍未生成。原RTL kernel2005478继续运行，最新v19仍0/4，未新增OOM；原9要求/8变体、完整RTL串行链、physical/board缺口及完整未完成结论保持。下方0/6及checker运行信息为历史；CPU日志round不是batch的纠正仍有效。

## 2026-10-30：CPU顺序补充3/18完成，第一组独立审核已实际运行

- block_000/worker_002 compact/direct的原worker完整两批各1062网校验通过，C++native及外层worker均exit0；11项artifact及compact原参考另行重读SHA通过，1426871976个非metric语义值字节/全部四字段、3761训练源/440模板、原生成输入/bank/argv/CPU121/AS16GiB/core0及串行回执均核对一致。报告`data/derived/training_order_control_20261029_v1/block_000/worker_002/report.json` SHA256=1d76da2335466659cd1fea74e4f7a30d38c11e5bdd6d10a01a641640330da802；outer receipt SHA256=e6e87bb89e01aef9897bfcd72c0a1a188f8c630ae01b7ad210095c4fd585d639。application=1588.440367362秒、worker完整输出检查另耗232.029077359秒；未据此提前判断补充实验性能。
- 旧worker3488238/native3512317已结束；监督2624526（句柄27488）/driver2660361保持。driver已进入`original_full_block_audit`，原`check_source_to_route_with_training_v2.py` checker4050806/starttick1647604240已实读/proc核唯一argv/cwd及AS16GiB/core0/CPU121。当前3/18 worker完成、0/6组独立验收；`block_000/audit.json`及block_001均尚不存在，不能称第一组独立通过，也不要另起checker或下一组。
- 原RTL kernel2005478继续运行，最新v19仍0/4，未新增OOM；其余原功能链依赖不变。下次先核v19、现有handle和checker实际身份/终态报告；完成后原driver自动进入第二组顺序[compact/direct,compact/expanded,csr/direct]。原9要求/8变体、六排列18项和完整physical/board缺口保持。下方2/18及第三项运行信息为历史，日志round/batch纠正仍有效。

## 2026-10-30：CPU实时进度含义纠正（不改变验收计数）

- `NATIVE_SITE_PROGRESS <round> <done>`的第一个数字是每批内部的协商迭代编号，不是batch编号。`src/native/site_runtime.cpp:66`显式执行两个batch，但第74行callback仅打印round/done；`src/native/site_routes.hpp:80`及第86行传入iteration和本轮网数，每个batch重新从iteration=0开始。两份源码SHA已重新与当前block_000/plan.json绑定核对，分别bc2eb59d87c53c48136275abc0809fe6a5d46dd70cd3f1f01463288955b50f26和aee0022e561fc8cd18de322bf76d1bfdcf4ecc26dc963ff478849d1a50f7ed12。
- 之前会话把日志`1/2 1062`解释为两批完成不准确；以后只按“迭代轮次/本轮网数”描述部分日志，不能据此计完成批次、完成worker或验收。已完成2/18来自实际两个worker的exit0、完整两批输出校验和文件绑定，不依赖该日志推断，结论保持。第三项仍须等待原worker最终报告和整组独立checker；活跃代码和原日志均未修改。

## 2026-10-30：顺序补充第二项完成，第三项compact/direct实际运行

- block_000/worker_001 compact/expanded的原worker报告已为`regenerated_inputs_and_two_full_batches_verified`，C++native和外层worker均exit0。两批各1062网，完整非metric语义值比对1426871976字节；11项artifact及compact参考文件另行逐SHA重读通过，生成输入、3761训练源/440模板、训练bank、实际CPU121/AS16GiB/core0、argv及串行回执核对一致。报告`data/derived/training_order_control_20261029_v1/block_000/worker_001/report.json` SHA256=22fa10b1e6382d72ad625399ae27602d7bfdc56122695edfa1cd2e7096ecbeed；outer receipt SHA256=5adb9ff0dc476e5f4ff5dec14fbb144ed4c1b59e228ff5c559a92759319dc51c。
- 该项application耗时1005.998847006秒，原worker完整输出检查另耗233.005002219秒；单项计时不构成新性能结论。当前2/18 worker完成、0/6组独立验收，`block_000/audit.json`仍不存在；须等三个条件全部完成后由原checker独立审核，不把worker内部通过称为独立组验收。
- 原worker3103426/native3127640均已结束。现有监督2624526（句柄27488）/driver2660361自动启动block0 position2 compact/direct：worker3488238/starttick1647421250，native3512317/starttick1647429225已实读/proc匹配；下次重新核实，不重启旧任务。完整六顺序/18项/两批原oracle保持。
- 原RTL kernel2005478/starttick1646941760仍live；最新v19日志0/4，下游按原独立前置等待，oom=0/oom_kill=2未增加。物理v2仍仅准备，原9要求/8变体及所有实卡/物理/特殊资源缺口保持，完整实验未完成。下方1/18及第二项运行状态为历史。

## 2026-10-29：顺序补充首项CSR完成，第二项compact/expanded实际运行

- `data/derived/training_order_control_20261029_v1/block_000/worker_000/report.json`已为`regenerated_inputs_and_two_full_batches_verified`，外层worker及C++native退出码均0。两批各1062网，完整比对1426871976个非metric语义值字节，字段iterations/routes/scope/status；10项worker artifact SHA另行重读通过，原生成输入、参考绑定、执行顺序和实际CPU/AS记录核对一致。报告SHA256=4d041916be08cb1214ab8ab8f65f5166db22a3de68cc1f1086c217be5815d51c；outer receipt SHA256=5fe43b7018ecf1ae0265c17843caffd838a24e0dbac387dbb327c4f7aa8c40e1。
- 首项应用耗时1111.483455764秒，原worker内完整输出核对另耗230.682661073秒；这是单个CSR样本，不能与原中位数直接构成新的性能结论。当前1/18 worker完成、0/6组独立验收；block_000/audit.json仍不存在，原独立block checker将在三条件全部完成后运行，不能称第一组已独立通过。
- 原CSR worker2680365/native2698665均已退出，不要再当live或重启。原监督2624526（句柄27488）/driver2660361自动按冻结顺序启动block0 position1 compact/expanded：worker3103426/starttick1647296423，实际native3127640/starttick1647304264均/proc实证live。下一条件仍compact/direct，全部六顺序/18完整worker/原oracle保持。
- 原RTL kernel2005478仍live，日志0/4，原三个下游owner继续等待独立前置；oom=0/oom_kill=2未变。只读实时入口仍`python3 scripts/experiment_status_v19.py`。本节为时点观察，后续须重新核实际进程。完整9要求/8变体、CPU顺序/共享主机限制和全部physical/board缺口保持，完整目标未验收完成。

## 2026-10-29：完整六顺序CPU补充对照已实际启动，实时状态入口v19

- 新`training_order_control_contract_v1.py`、`run_training_order_control_v1.py`、`check_training_order_control_v1.py`及`supervise_training_order_control_v1.py`冻结独立补充实验：六种排列各一次、共18完整worker，每条件在三个位置各出现两次、任意两条件先后各3次、组内每个相邻有向条件对各2次。seed=20261029，原条件索引0=csr/direct、1=compact/expanded、2=compact/direct，实际固定顺序[[0,1,2],[2,1,0],[1,0,2],[0,2,1],[1,2,0],[2,0,1]]。这是看过原结果后新增的顺序控制，不替代/混池原7组21项，也不是冷缓存实验。
- 完整复用冻结`source_to_route_with_training_v2.py`与`check_source_to_route_with_training_v2.py`，SHA分别9c1871cb2aa99292a61c46e9e241b53a1a4007529bd46dca8ffdfa2c70ab0da7、c6c152ad1d00d828fb042f3b2a3152154fe04b09159cf5d8bcff2114c228d4f5。保留274732节点、1062查询、14已验证站点、全部固定/保护资源、cache4096及原预算；每worker仍重新训练compact的3761源/440模板并转换输入、完整路由两批各1062网。每组三条件完成后由原checker重新逐完整输出核对，最后独立核全18项/6组、实际顺序/非重叠时间/CPU和worker/native实际limits。
- `results/training_order_control_preparation_20261029_v1.json`冻结493绑定，SHA256=b4dcf6338502d8e3c761618dcc0f2bcaa4c88f68c9288c063c81cc623d6cc692。启动前4单测通过：六种完整排列/缺项重复拒绝、18项完整配对与部分/错误矩阵拒绝、真实一次性child在rawfree0但无新OOM时正常完成、模拟新增OOM只停止自有进程组且保存失败。实际driver缺准备及checker缺trial均exit1、无提前trial/报告创建。检查中修正了用空白拆分argv的问题，现直接核/proc的NUL分隔argv；冻结前完成。原顺序验证函数AST与旧7组checker完全相同。
- 单worker仍AS16GiB/core0/CPU121；新监督采用统一无rawfree门槛POLICY，新增OOM/oom_kill或计数重置时只停止本次进程组，不重试、不升cap。完整历史约32GB原始证据在准备/启动时审核，worker启动仅使用原输入/参考及代码闭包109项，避免每worker额外扫描历史21次输出改变预热过程。CPU121只约束本次worker，并不保证独占；原RTL未改affinity，仍有共享主机/缓存和并发RTL影响。
- 唯一监督2624526/starttick1647143316，工具句柄27488；driver2660361/starttick1647154633，第一组CSR worker2680365/starttick1647161285，实际C++ native2698665/starttick1647167071均实读/proc活跃，AS16GiB/core0/CPU121符合。首worker新image/routing/sites/symbols/queries均逐SHA等于原完整输入。状态目录分别`data/derived/training_order_control_supervision_20261029_v1`与`data/derived/training_order_control_20261029_v1`；当前0/18、0/6，最终`results/training_order_control_audit_20261029_v1.json`尚不存在。
- `results/training_order_control_launch_20261029_v1.json`16绑定另行重读通过，SHA256=6b9d4bd8fa20097ad557467f66818b994d38f0eea2de760ec25b6591309c70bb；仅证明启动时实际owner/driver/worker/native与原RTL并发存活、首输入一致，不证明后续存活/输出或性能。下次应重新核实际进程，不能重复启动。
- 当前只读入口为`python3 scripts/experiment_status_v19.py`（或--json），保留原v18全部RTL/组件/原CPU状态并增加本补充监督及worker/组计数。原native RTL2005478/starttick1646941760仍live/0-of-4，原三个下游监督1271339/1381048/1879400仍live等待独立前置；oom=0/oom_kill=2未变。没有新HLS/RTL编译或Vivado物理任务，原物理v2仅已准备。原9要求/8变体、完整completion_proven=false和平台/板卡/完整特殊资源等缺口保持。

## 2026-10-29：21项含训练CPU实测图表完成，实际顺序不均衡限制已核实

- 当前native RTL kernel2005478/starttick1646941760再次/proc实证存活，owner1121343/driver1128465仍running/rtl，日志0/4；未新增OOM。原串行链及只读入口v18保持，未启动新的CPU统计/大型编译/物理会话，完整验收仍待原C与4完整快照。
- 新`scripts/plot_training_inclusive_cpu_v2.py`从原已接受7组/21worker统计及320绑定完整性报告读取，重新核SHA、配对算术、每组21份submission/receipt实际顺序/CPU/时间不重叠，再生成`results/figures/training_inclusive_cpu_20261029_v2/`：21行workers、14行paired_ratios、7行execution_order、3行summary CSV，两图各PNG/SVG/PDF、analysis、中文独立report.html、requirements和manifest。复现：`PYTHONPATH=/tmp/A_graph_compression_recovery_20261025_v1/plot_dependencies_v1 python3 scripts/plot_training_inclusive_cpu_v2.py --output NEW_OUTPUT_DIRECTORY`。旧v1仅第二图legend遮挡数值，v2修正布局，原v1源/产物保留。
- 另行独立重算全部CSV原时长/配对比/均值与中位数/阶段相加及原执行顺序，337绑定重读通过；`results/training_cpu_figures_integrity_20261029_v2.json` SHA256=16ea85faacb51da9e56ebef82a07d8fffb17f46480a67edeee7c4363523dd4d1，图manifest SHA256=1d08f175b2323971d072a2932620ea77c25f0a773059e7a63d8c485b5c461319。两张最终PNG均实际view_image检查。该审核没有重新执行native语义oracle，未把图表生成视为新的路由测量。
- 应用中位数CSR/direct1084.871s、compact/direct1547.898s、compact/expanded988.355s；原配对比中位数1.4338400098和0.9096898965不变。均为含compact新训练、TSV转换、输入生成及两批各1062网的CPU应用时长。阶段图用逐worker差值的算术均值保持可相加，不相加阶段中位数；未用继承RUSAGE_CHILDREN峰值冒充native-only内存。
- **新核实的公平性限制**：实际随机顺序只有CSR→compact/direct→compact/expanded（2组）和compact/direct→compact/expanded→CSR（5组）；direct在全部7组先于expanded，CSR从未处于第二位。原随机种子执行有效，但顺序并未均衡，页缓存/前序worker影响未隔离。不能将观察到的expanded耗时降低认定为顺序独立、冷缓存或板级收益。保留全部7配对值（含第6组ratio0.99133），未声称置信区间/显著性。
- 后续若补公平顺序控制，应保持原完整3条件/工作负载/C与原始输出验收，在新的独立补充实验中覆盖全部6种条件排列；保留原7组结果，不能换种子重跑后挑较好结果。当前尚未准备/启动此补充实验，不存在相应等待监督。14站点模型、共享主机、Vivado采集/板传输/物理读回等原限制保持，原9要求/8变体及completion_proven=false不变。

## 2026-10-29：native v2 编译成功并进入 RTL；当前物理入口 v2 已验证、尚未执行

- `results/native_v2_compile_transition_audit_20261029_v1.json`冻结17项绑定，另行重读通过，SHA256=7357854a6d562a277fbb9ccbb6bedebbd06c7c9359b10fe4afc2bdecb73fe203。xelab1138642已退出0，实际完整编译2989.592859秒，GNU time最大RSS158319368KiB（约151GiB），工具peak159690384KB单独记录；编译AS192GiB/stack256MiB/core0。最低采样rawfree1097728bytes，没有触发旧16GiB门，oom=0/oom_kill=2未变。该报告只核完成编译回执、命令/limits和RTL启动观察，不代替最终完整输入/输出审计。
- 实际RTL kernel2005478/starttick1646941760已启动，owner1121343/driver1128465仍live，AS96GiB/stack256MiB/core0实读一致；日志0/4 @128000ps。4tx/44指针/30模型/全部depth/4pages、原C postcheck和四个完整946498280byte快照均仍须验收。新native最终accepted报告尚不存在，原零地址postcheck失败和旧资源中止保持。下一会话重新核实际状态，不能把本节观察当作未来存活证明。
- 配对监督1271339、tree监督1381048、snapshot/read监督1879400本次/proc身份匹配、全线程children为空，等待的是上游完整独立验收。现有native→CSR→compact→full50 tree→full30 snapshot→full2 read串行链保持。只读实时入口仍`python3 scripts/experiment_status_v18.py`；本轮没有再启动大型A编译/实现。
- 新`encoded_physical_entry_v2.py`、`prepare_encoded_physical_execution_v2.py`、`check_encoded_physical_execution_v2.py`与目录`data/derived/encoded_physical_execution_20261029_v2`已冻结。入口要求当前native v2、两配对非零v2、tree v2、snapshot v5、read v4全部实际typed验收和所有SHA，以及当前snapshot/read监督完整终态。每个物理DUT/ROM还必须逐SHA绑定对应模式的**实际已接受**RTL副本，准备报告不能代替该前置。
- 新物理入口取消旧rawfree启动/运行门，以同一POLICY记录memory事件；专有Vivado进程AS从旧无限收紧至192GiB/core0（若已有更小限制则拒绝，不自动升cap），新OOM或计数重置只停止身份匹配的本次owner。原2022.2 Tcl综合/布局布线/报告流程和clock.xdc逐byte不变：U280/5ns/1.35ns/2threads；所有原DRC、methodology、timing质量门保持，负结果不能算时序闭合。
- `results/encoded_physical_execution_preparation_20261029_v2.json`861绑定，SHA256=e7069002c91aab3afef6ed6207d77a8de047a16ca46a0c2ff30df725600ae7ed；`results/encoded_physical_entry_validation_20261029_v2.json`1173绑定，SHA256=43787ad00c9e8974b5fab0740221ab883e60433f0b6b1d578eceff515d757b7e，均另行逐文件重读。CSR115/compact118/read60个完整DUT/ROM与当前对应准备源全部一致；8项单测通过，覆盖错模式/损坏/缺失实际DUT绑定、部分read及错误snapshot前置、错误MCP终态/重复执行、PID复用和真实一次性child的OOM终止（模拟计数，不改真实cgroup）。rawfree=0而无新OOM的终态fixture不会触发中止。
- 实际三种arm缺native验收均exit1，三种checker缺物理state均exit1；没有创建guard/state/session/验收文件。MCP查到的两个会话均属B，未操作。**物理任务仅入口已准备，没有物理监督在后台等待，也未创建A Vivado会话。**完整RTL链独立通过后，再使用专有MCP Tcl会话按csr→compact→read逐项执行和收集原始MCP history/status、DCP/报告，独立审核并退出本模式会话后进入下一项；不能直接source绕过entry.tcl。
- 原9要求/8变体、完整completion_proven=false及原物理负结果/平台DDR-HBM/实卡功耗/真实流量/完整端到端等缺口保持；仍不是只剩上板验证。以下历史中native“正在编译”、物理入口“尚未对齐”的描述已由本节取代。

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

## 最新：完整30tx snapshot DPI入口/独立审核已接到现有batch后，当前只等待（2026-10-25）

- 新scripts/run_snapshot_dpi_rtl_v1.py、check_snapshot_dpi_rtl_v1.py、snapshot_dpi_output_oracle_v1.py已准备。完整30tx/13pointer/10model/各4pages/所有原depth保持，复用原cosim.pc.exe和resident_snapshot_rtl_contract.py literal30rows及full-state checks；输出packet每事务完整524288x512bits、result全部512bits按原C prepared vectors逐字节/逐值对照，EOF/顺序/unknown/payload错误拒绝。8个全只读bundle另加纯AW握手禁止写monitor，不改DUT/原模型协议。
- 新唯一snapshot supervisor3465022/exec24950（scripts/supervise_snapshot_dpi_rtl_v1.py，data/derived/snapshot_dpi_supervision_20261025_v1）只等待原batch2747433完成独立审核，再184GiB rawfree下跑一次snapshot/DPI及独立audit；AS160GiB/core0/16GiB runtime门。采用原generated默认编译优化（无额外--O0），未测性能不宣称内存收益。当前未创建local snapshot_dpi_rtl_v1目录/未编译。
- output oracle2tests与status3tests通过，实际原C result30records按空白/完整512bit严格解析通过；缺batch gate和原failed nativecompile均被拒绝且无success文件。results/snapshot_dpi_execution_preparation_20261025_v1.json仅准备证据，不是RTL通过。goal active，原compact1509104继续，search2747344/batch2747433/snapshot3465022串行链不重复提交。

## 最新资源终态：snapshot原native编译主动中止；compact同一PID已恢复R（2026-10-25）

- snapshot2516537已在anon+kernel/page-table>285GiB/300GiB、swap0且内存持续增长时保存现场后主动资源中止：先设置该自有compiler core0，再pidfd SIGTERM。原owner2508987正确failed/elaborate，exec92733已收exit1，未进入RTL，不再活跃。data/derived/snapshot_compile_resource_abort_20261025_v1及results/snapshot_compile_resource_abort_20261025_v1.json保存真实终态/receipt/原log/压力；原完整30transactions/13pointer depths输入和验收仍需完成，不能以2tx DPI小回归代替。
- 原compact恢复controller1665449已自动完成，exec50427收exit0；同xelab1509104/startticks1605777574恢复R（不是重启），owner1504642继续原full44/4tx流程，后续execution1537035/final1553441仍原链。DPI v7 owner2747344/exec8267严格等该原workflow结束，batch2747433/exec66927等DPI独立audit。
- 最后空闲site Vivado2607458也已在MCP idle/queue0/code0且24项site/clock文件关闭前后SHA不变后释放，results/idle_site_vivado_release_audit_20261025_v1.json保存证据，DCP全保留。所有五已完成A会话当前均已关闭，不对旧PID/session发命令；B会话未动。OOMkill仍2未新增。goal active。

## 最新：DPI v6并发余量保护中止；v7严格等待原native任务退出（2026-10-25）

- attemptv6 failed/elaborate，receipt resource_admission_abort=true/exit-15；原snapshot同时涨至207577764KiB RSS导致共享CG余量不足。此结果不证明64GiB AS不够，也非功能反例。results/search_axi_dpi_capped_attempt_incident_20261025_v6.json保留原证据。原search2519968/exec81980与batch2537792/exec41590均收exit1，不再活跃。
- 唯一新search owner2747344/exec8267（scripts/supervise_search_axi_dpi_serial_capped_replay_v7.py，data/derived/search_axi_dpi_serial_capped_supervision_20261025_v7）冻结原snapshot owner2508987与compact owner1504642身份，必须两原workflow退出后再等rawfree>=152GiB，才运行新attempt search_axi_dpi_replay_v7。继续AS64GiB/core0/16GiB运行门，不未经证据增加64上限，不缩full2tx/4pages/depth/golden；复用独立checker v6完整语义。
- 唯一新batch owner2747433/exec66927（supervise_compressed_bus64_dpi_rtl_v5.py，data/derived/compressed_bus64_dpi_supervision_20261025_v5）接新v7独立audit，完整4tx/44ports/160GiB/core0/184GiB门不变。当前两者只waiting，未创建v7实验目录。原snapshot2516537 R、compact1509104 T/controller1665449继续，goal active。

## 最新：48GiB v5已失败；64GiB v6正在实际编译，四完成会话已释放（2026-10-25）

- DPI v5终态failed/elaborate，LLVM memory/exit134、MaxRSS48620136KiB、resource_admission_abort=false；core0生效无core文件。search2024814/exec11212与batch2051098/exec26871均已收exit1，不再活跃，失败证据results/search_axi_dpi_capped_attempt_incident_20261025_v5.json。
- 通过MCP list+4个status确认idle/lastcode0/queue0后，仅关闭四个已完成A Vivado会话PID4146646/4159154/633621/497587；426项原审核文件关闭前后全部SHA不变，data/derived/idle_completed_vivado_release_20261025_v1及results/idle_completed_vivado_release_audit_20261025_v1.json保存证据/冻结logs。无Tcl新命令，用pidfd终止进程避免改写冻结log；DCP/源/报告全保留，不动B会话或oldsite2607458。上述四session已不可复用，需新session读保存DCP。原native/compact任务不动。
- 新唯一search supervisor2519968/exec81980（scripts/supervise_search_axi_dpi_capped_replay_v6.py）→driver2520077，local search_axi_dpi_replay_v6当前elaborate。AS64GiB/core0/88GiB admission/16GiB runtime门，全部原2tx/exactcycles/输出/PCpostcheck不变。新batch等待2537792/exec41590（supervise_compressed_bus64_dpi_rtl_v4.py，data/derived/compressed_bus64_dpi_supervision_20261025_v4）等待v6真实独立audit，原batchv2 full44规则不变。status入口已优先新链并3tests通过。完整目标active。

## 最新执行：core已完整无损归档，DPI v5正编译顶层（2026-10-25）

- core archive1970412/exec18780已complete/收exit0，manifest保存原32492687360bytes SHA与压缩5884336984bytes SHA，独立完整解压校验后才unlink原core。实际闭合，不再等待该owner。cold_archive_cache_hint.json仅记录对该已fsync归档file的POSIX_FADV_DONTNEED提示（测得即时CG未变），不是清全局cache/修改配额，归档内容保留。
- search supervisor2024814/exec11212已自动启动driver2191734，local search_axi_dpi_replay_v5当前elaborate；实际wrapper2199664/leaf2199697的/proc limits均验证AS48GiB/core0，存data/derived/search_axi_dpi_capped_supervision_20261025_v5/enforced_elaborator_limits.json。最新编译到search_kernel_top，尚未RTL/postcheck。新batch2051098/exec26871仍等真实search独立audit。原snapshot2516537继续R，compact1509104 T/controller1665449仍活跃。完整目标active。

## 最新等待链：DPI v5采用48GiB/core0，先等core完整归档（2026-10-25）

- 原32GiB attemptv4/combined1789765与batch1802141均failed且句柄已收，证据不改。唯一新search supervisor2024814/exec11212（scripts/supervise_search_axi_dpi_capped_replay_v5.py，data/derived/search_axi_dpi_capped_supervision_20261025_v5）当前waiting_lossless_core_archive_and_cgroup_admission；须原core archive1970412/exec18780 complete且manifest已独立全解压验证/source_removed=true，再CGrawfree>=72GiB才启动local search_axi_dpi_replay_v5，AS48GiB/core0/原16GiB runtime保护/原全部2tx精确验收不变。当前未编译新v5。
- 唯一新batch supervisor2051098/exec26871（scripts/supervise_compressed_bus64_dpi_rtl_v3.py，data/derived/compressed_bus64_dpi_supervision_20261025_v3）等新v5独立search审核，仍184GiB准入；新batch driver/checker v2采用AS160GiB/core0，完整4tx/44ports/快照保持，目标attempt compressed_batch_bus64_dpi_rtl_v2与canonical audit v1。均无自动重试。只读status入口已优先选择新链，3tests通过。
- core archive1970412仍运行，先检查其state再新动作，不重复提交/提前删core。原snapshot2516537继续R、compact1509104 T/controller1665449活跃；完整目标active。

## 最新覆盖：受限DPI v4已失败，后续batch监督失败；core无损归档运行中（2026-10-25）

- local search_axi_dpi_replay_v4终态failed/elaborate，LLVM ERROR out of memory，32GiB AS上限确实继承；receipt另记录resource_admission_abort=true/exit-15，未进入RTL。search owner1789765/exec59512与batch等待1802141/exec66903均failed且已收exit1，不再是活跃链；不要重复等/声称在编译。results/search_axi_dpi_capped_attempt_incident_20261025_v4.json绑定原失败。原snapshot2516537继续R，compact1509104仍T/controller1665449活跃。
- 此次生成31GiB ELF core.1797616，造成额外文件缓存，现由scripts/archive_capped_xelab_core_v1.py owner1970412/exec18780无损压缩到data/derived/capped_xelab_core_archive_20261025_v1；必须完成整core独立解压SHA/size/fsync后才删原unbound core释放缓存。当前状态以state.json为准，勿重复归档。下一次资源配置需计编译器本体开销并加--core=0，不能把4.19GB backing当编译峰值；不得缩full scope。旧wait-only链196239/247521/731182已superseded不复用。

## 最新DPI监督交接：完整搜索核受限回归已实际编译（2026-10-25）

- 原三个wait-only supervisors196239/247521/731182已在未启动任何DPI实验时交接终止（exec82074/42992/46217均收143）；原snapshot2516537和compact1509104/恢复controller1665449未动。权威data/derived/search_dpi_supervision_handoff_20261025_v4/terminal.json及旧目录handoff.json。
- 新唯一search owner1789765（exec59512，scripts/supervise_search_axi_dpi_capped_replay_v4.py）实际运行driver1789768，local search_axi_dpi_replay_v4已elaborate。7模型全部full depth/4pages的四态backing=4190310144bytes，原rawfree约77.7GiB下用64GiB admission+每process RLIMIT_AS32GiB+16GiB CG运行门；实际xelab继承limits已保存enforced_elaborator_limits.json。不是缩scope：2full transactions/所有完整输出和exactcycles[2132461,12404]/原PC postcheck不变。新独立checker v4接受后仍写canonical results/search_axi_dpi_replay_audit_20261025_v3.json（audit语义版本不代表attempt目录）。
- 新唯一batch等待owner1802141/exec66903（scripts/supervise_compressed_bus64_dpi_rtl_v2.py，data/derived/compressed_bus64_dpi_supervision_20261025_v2）衔接新search owner，仍184GiB准入、4tx/44ports+完整snapshots+独立audit。旧等待链不再活跃，勿重复启动v3或旧batch owner。只读scripts/experiment_status.py已识别交接与新链，3tests复核通过。完整目标active。

## 最新调度覆盖：globalbus64物理尝试已主动资源中止，不再是挂起（2026-10-25）

- 原Vivado1924562/session vivado-20261025-044405-144bb05a及资源controller1037647已终止且/proc确认不存在；controller exec48654已收exit143。不是OOM或工具失败归因：anon>280GiB/300GiB、swap0且暂停Vivado仍持约47GiB，先冻结日志/状态再仅终止自有未产checkpoint的尝试，为原snapshot2516537释放内存。最新权威data/derived/bus64_physical_resource_abort_20261025_v1/terminal.json与results/compressed_bus64_physical_resource_abort_20261025_v1.json；原running state保持历史不改写。勿恢复旧PID/重复source，不对消失会话发新命令。后续物理需新trial，严格等大编译串行释放。snapshot继续R、compact1509104仍由1665449管理，DPI串行链保持，goal active。下方旧“暂挂”提醒已被此条覆盖。

## 当前自有进程调度提醒（2026-10-25）

- globalbus64 Vivado PID1924562/session vivado-20261025-044405-144bb05a已由资源controller1037647（exec48654，scripts/serialize_bus64_physical_memory_v1.py）SIGSTOP，原source未完成，不能重复source/重启。先读data/derived/bus64_physical_memory_serialization_20261025_v1/state.json及/proc；controller按原snapshot/compact活跃compiler与64GiB rawfree条件恢复同PID。若controller失败须先处理遗留挂起PID。T期间不对该会话执行MCP新命令；原snapshot2516537继续R、compact1509104仍由既有controller1665449管理。目标保持active，不是用户请求暂停。

## 紧急资源实态：CSR整批xelab已SIGKILL；compact同一PID暂挂起等待内存（2026-10-25）

- CSR guarded owner334627/child342081已failed/elaborate，exit137/SIGKILL、2202.9465s、MaxRSS157933656KiB≈150.6GiB；依赖执行397193与最终审核779628也failed。exec4723/51340/47375本轮全部收exit1，不能再按旧条目称它们运行或RTL通过。全部原scope/源码/44depth/4tx及失败日志保留，不盲重跑。results/compressed_batch_csr_elaboration_memory_incident_20261025_v1.json记录。
- 当前cgroup memory.max=322122547200bytes=300GiB，memory.events oom_kill2（早前1），本机/proc/MemAvailable约1.2TiB不能代表会话配额！dmesg被拒，OOM计数无精确PID时间，所以只称与内存压力一致，不断言OOM已归因此PID。memory.events max/oom仍0，可能上级/其他OOM事件，勿夸大根因。未来大编译须按cgroup当前余量与已观测峰值留裕量，不能只看主机空闲。
- 自主调度修正：仅owned compact实际xelab PID1509104（owner1504642/exec13729、cwd compact_rtl_guarded_v1/sim/verilog）已SIGSTOP，ps状态T，约6.6GiB，保留同一进程/完整输入/源码/容量；未杀掉/重启，goal仍active。新scripts/serialize_compact_rtl_memory.py controller1665449/exec50427，state=data/derived/compact_rtl_memory_serialization_20261025_v1/state.json，核对startticks+cmd+cwd，等待原snapshot compiler2516537结束且cgroup free>=184GiB才SIGCONT恢复同一1509104。若controller意外退出，必须先检查state/身份/配额再处理该挂起PID，不能忘记或重复启动。
- snapshot恢复2508987/实际xelab2516537仍running（约80.8GiB），继续原任务；compact执行/审核监督1537035/1553441仍等待原编译。没有大规模新xelab通过内存门前启动；不以缩声明深度/删除交易代替完整验证。CSR失败后另新revision的串行恢复仍待可用内存。

## 当前交接修正（2026-10-25）

- 持久归档完成：data/derived/frozen_local_evidence_20261025_v1，8168文件33.87GB，9关键报告的2024个local依赖hash覆盖通过。复原/tmp缺失路径可用restore_frozen_local_evidence.py；活跃snapshot恢复两目录排除，需后续归档。无需等待先前新存储目录问题。
- 已处理本项目旧heap的2.52TB未完成verbose诊断缓存，源/plan/log/头尾保存，仅停止该候选并删此可再生缓存，释放约2.3TiB。旧heap2468333/2468371失败、无SYN pass，勿重启。所有路由/源数据保留。
- 四真实压缩CPU批次和full44端口C/HLS快照及cosim setup已通过；尚未新top RTL。压缩HLS估计1922947LUT/4.509ns不达预算。根setup报告首次quota0byte已原子修复，详见NEXT顶部。
- 原packet-width64 RTL也已独立通过2笔[2132461,12404]，旧owners2297545/2339367已退出；CSR物理对照尚未做。snapshot local恢复2508987/exec92733仍活跃，按真实/proc接收不重复提交。完整实验未完成。

## 最新交接（2026-10-25，优先于下方旧记录）

- 四真实压缩CPU批次已全raw+trace独立通过，results/compressed_batch_real_audit_20261025_v1.json，每批95.958847MiB；所有旧real/HLS/prep owners已complete，无需等待/重跑。
- full44端口CPU双模式及CSR HLS full snapshot/cosim SETUP已通过，results/compressed_batch_full_depth_cosim_setup_20261025_v1.json；尚未执行新top RTL。下一步实际TV深度/RO AXI地址监测→新execution目录xelab/xsim/postcheck，不能把setup当RTL pass。
- 压缩HLS1922947LUT/4.509ns超资源参考/有效预算，仍无physical/板卡通过。使用v4 mixed reader及v2 round reader。
- 原snapshot848340已quota失败；local恢复owner2508987/exec92733在跑，30交易full深度不改，别重复。旧heap2468333/2468371已因2.52TB未完成verbose报告主动停止并清理仅此可再生缓存；failed且无SYN pass，源/日志/头尾保留，不等待它。
- 共享卷已恢复约2.3TiB，新frozen证据备份owner3940909/exec21589，data/derived/frozen_local_evidence_20261025_v1，活跃snapshot目录排除。manifest全部成功才产生；随后核对关键报告覆盖，必要用restore helper重链/tmp缺失路径。根文稿更新一律原子temp/fsync/replace，避免配额截断。详见NEXT_STEPS顶部；完整实验未完。

## 当前运行入口（2026-10-25，优先读NEXT_STEPS顶部）

- 四真实压缩诊断CPU批次owner1803274（exec28167），workers1804329/1804332，本机 compressed_batch_real，root同名data/derived pointer。首CSR实测trace95.96MiB无溢出，但全raw/trace审核尚待；原owner自动最终审核，勿重复。
- 新压缩top HLS owner1860773（exec61552），唯一监督1872988（exec72097），本机 compressed_batch_hls；Csim已过综合中。原无压缩local恢复1310895/1314947已complete，LUT估计1859019超整片参考/4.509ns超预算，不是可部署通过。
- 使用read_batch_trace_v4.py/read_round_trace_v2.py，400完整trace已验收。共享盘紧，新增大文件放/tmp隔离并记录持久pointer；已异步询问可用归档目录，尚未答复，持续local工作。其他旧owner请按/proc核实。

## 最新验收更正（2026-10-25）

- 全部400压缩trace已独立通过，见results/compressed_batch_trace_cases_20261025_v2.json；采用read_batch_trace_v4.py + read_round_trace_v2.py。旧round reader误把多个incomplete数量当action，原export pipeline1594056因此failed；输出完整且内核正确，旧失败state保留，不等待或重跑它。
- O2 v2已成功，local compressed_batch_router/router_v2及regular_build_complete_v2.json为真实后续入口，owner1687584已退出。下一步实际真实诊断四批尚未启动。详见NEXT_STEPS顶部。

## 构建补充（2026-10-25）

- 下方compressed O2 owner1620758已失败（内部batch_worker unused trace_control告警被-Werror拒绝）；新v2构建exec22477，regular_build_plan_v2.json记录新owner，输出router_v2。源码未改，仅top的unused-parameter保留warning，后续必须核对warning；不可按旧owner等候。

## 最新入口与任务指针（2026-10-25，优先于下方旧交接）

- 无损trace新入口search_batch_trace_top_v2.cpp / SearchTraceV3 type6已两模式CPU等价；400-case集成差分通过。独立400trace导出验收owner1594056（exec90320）与O2真实router构建owner1620758（exec92567）在/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router，详见NEXT_STEPS顶部，不重复启动。
- 原无压缩trace HLS687570已IO失败，当时共享卷0可用；缓存仅terminal部分逐hash搬到/tmp、原路径symlink。当前本机隔离恢复owner1310895（exec27921），监督exec80022；root data/derived/search_batch_trace_hls_local_recovery_20261025_v1/location.json给出路径。/tmp临时artifact需后续归档。
- snapshot恢复owner848340（exec16438）仍需按/proc核实；原failed v1 xsim cache已逐hash搬到/tmp并保持路径，不碰active恢复。共享卷空间紧张，新增大数据优先本机隔离目录和持久小pointer。

## 当前交接（2026-10-25，详细见 NEXT_STEPS.md 顶部）

- 整体batch CPU已通过400case及全真实CSR/compact各两批1062网的独立中间状态审核；不是RTL/设备通过。results/batch_router_audit_20261025_v1.json已冻结。
- 独立诊断batch trace top在CPU两模式/Csim已导出精确search/net/round/history/terminal；采用read_batch_trace_v2.py补充需求继承/逐net总量，旧v1 reader的反例保留。trace综合owner687570、唯一审核监督727144仍需按/proc核实，不重提交。
- snapshot原RTL v1 failed/elaborate/137，根因未证；隔离恢复owner848340（exec16438）复用全depth/30交易/原RTL，修改xelab线程/优化，自动最终审核。核实state与/proc后接收原结果，勿复制重跑。其他长任务和冻结证据请读NEXT_STEPS，不据旧PID直接判断运行/成功。

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

# 方案 A 工作上下文

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

## 历史：分层基线已独立审计，完整路由XRT接口完成离线准备

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

## 最新：Vitis主机接入完成离线验证，v2核验证及自动审计继续

- `results/vitis_host_preparation_20261023_v1.json`：XRT2.14.354主机成功编译（最终log v4，需`-luuid`），两模式各10批/274736请求/1100754记录输入预检通过。3项主机测试含12类坏输入及10类读回篡改；3项kernel审计测试含15类证据错误；独立读回1项/15类错误拒绝通过。仅离线契约，不是板端执行。源码和最终binary `build/vitis_graph_host_20261023_v2`均绑定，**host报告artifacts冻结，后续修改用新版本**。
- v1 HLS在cosim插桩编译时因C/C++ linkage冲突失败，完整证据保留；不要重启原v1。新`hardware/vitis/v2/graph_accel.hpp`使用extern-C声明块，原算法保持；`data/derived/vitis_graph_kernel_20261023_v2` owner253757/exec9963，CPU122/123，完整Csim和综合均通过。CSR RTL三批通过并已导出XO；compact原xsimk303134仍运行，已完成第一批。**v2 plan.files/generated、pipeline.files冻结；新包装没有继承旧OOC时序。**
- 唯一后续审计owner505544/exec50921，`results/vitis_graph_audit_pipeline_20261023_v2.json`，等待原HLS owner终态后自动执行`check_vitis_kernel.py`，最终输出`results/vitis_graph_kernel_audit_20261023_v2.json`。审计冻结依赖不可修改；完整Csim/RTL样本、8参数ABI、XO全部RTL与对应综合工程逐字节相同均需通过。失败停止、不自动重试。再次会话先核对/proc和状态，勿竞争重提。
- 主机和平台入口`hardware/vitis/README.md`、`scripts/vitis_board.py link/run`：明确.xpfm，DDR[0]/HBM[0]分别连接全部6个buffer；核验实际bank类型/group并保存设备BDF/name/xclbin UUID。主机全量guard读回、独立`check_vitis_readback.py`及输入/链接/执行哈希绑定已具备。硬件link/run尚未成功执行，不能称端到端实测；单次run的重复是图驻留重复，正式统计还需独立进程与随机顺序。
- 最新XRT探测`results/vitis_board_environment_20261023_v1.json`：0 devices；默认2022.2 base_platforms无U280.xpfm。需要实际匹配shell的平台与板卡才能接续DDR/HBM/功耗；不拿其他器件平台替代。`results/vitis_integration_stage_20261023_v1.json`保存本轮证据与进程快照，未来实时状态以原pipeline为准。
- 原CPU链保持：旧canonical执行器26/63、站点统计1/63、模板粒度验证3/5；源图21进程仍block000。容量owner3749868已发布2/6，CSR/3GiB明确分配失败，CSR/4GiB两批语义由执行器核验；compact/direct/4GiB child247066继续，最终全部独立审计未到。先前只有首失败格做了独立partial审计，勿把新第二格称最终独立完成。
- `python3 scripts/run.py check`通过。完整特殊资源模型、正式统计终态、平台后时序/资源、实卡DDR/HBM/功耗和完整router FPGA接入仍缺，目标active。

## 最新：源图完整软件链路三条件审计完成，完整查询router容量实验启动

- `results/source_to_route_validation_audit_20261023_v1.json`全部3/3通过，SHA256 ec9eb3a2da3e04bc8c7d9c684af738c5cf3915de1b21160a7bc6e3eece90e146，已核对原audit队列和统计门控绑定及auditor源码摘要。每条件实际重新生成AGR和全部fixture，消费新产物并完成两批1062网，原始语义独立匹配。原owner2142179、audit2205877/3842700均终态，不重启。
- 原21次统计queue2407216已进入statistics，driver3986466、当前block child3995518，CPU125；`results/source_to_route_statistics_pipeline_20261023_v1.json`。三次验证application wall为CSR/direct1118.713秒、compact/expanded1035.448秒、compact/direct1601.256秒，均n=1，不作统计加速。仍是捕获TSV到两批软件路由，不含采集/训练/板传输/物理读回。
- 新`data/derived/site_capacity_region_20261023_v1` owner3749868/exec42804，CPU124，固定原`native_site_runtime_20261023_v1`及原14实例模型，全部1062网首次/驻留两批；CSR/direct、compact/direct、compact/expanded各在3072/4096MiB RLIMIT_AS下执行，共6个新进程。未改运行中的原代码/输入。driver`site_capacity_experiment.py`每格核验完整语义或严格std::bad_alloc，结束自动调用独立`check_site_capacity.py`，异常停止，不自动重试。**plan.files全部冻结。**
- 首worker000 CSR/3072MiB已明确分配失败，`results/site_capacity_partial_001_20261023_v1.json`独立1/6审计通过，保留不完整stdout和完整stderr。现worker001 CSR/4096MiB child3948120继续；`results/site_capacity_execution_binding_20261023_v1.json`实查该child的4294967296字节soft/hard limit、CPU124与start_ticks。绑定采集时首worker已完成，勿把4GiB child误标成首3GiB条件。回归2项/10类失败或语义错误拒绝通过`results/regression_site_capacity_20261023_v1.log`。
- 容量限制覆盖native镜像、搜索/占用和完整结果轨迹，但不含输入转换/Python审计；RLIMIT_AS不是RSS或板存储，且模型仍仅14已测实例。当前仅一个失败条件，不能宣称任何表示在4GiB通过或完整router容量收益。
- 时钟补充`results/clock_property_surface_stage_20261023_v1.json`：两检查点各60对象/1132公开属性、零读取错误、仅四项变化，与原capture一致。`get_property IS_INVERTED`四个BEL均空，ROW IINV的`report_property`却显示bool0且只读；显示/getter差异未解释，不能把表格0当实际物理极性。直接查询routing BEL要加`-include_routing_bels`。完整捕获/恢复/5类篡改拒绝已归档，A恢复site_full checkpoint，3/3todos完成，无在途MCP调用。实际常量/反相/leaf delay/test与保护占用仍缺。
- 原旧canonical统计执行器22/63，站点63次统计第一进程、模板粒度验证1/5继续。新增容量是另一CPU124实验，原四条链不重启。全部目标仍active，不能用上述局部模型和CPU证据代替实卡DDR/HBM/功耗与完整特殊资源语义。

## 最新：四种真实规模完整等价与48格CPU解码容量实验完成

- `data/derived/scale_domain_region_20261023_v1/report.json`全部通过。按源anchor tile的(SLR,COLUMN,ROW,name)顺序取1/16、1/4、1/2、全部空间前缀；冻结原bank、完整保留选中行全部出边/目标节点/别名，未选源的邻接仍未知。规范节点3537/54627/156827/274732，已知行471/28640/115095/220973，有向边7066/159761/552176/1100754。最大域与原CSR/compact镜像逐字节相同。
- CSR字节3508416/19547200/55321280/98255808；compact3508608/18922112/53211136/93507968。最小组多192B，其余减少3.198%/3.814%/4.832%。每组Python按原始source逐字段/逐边核对，并比对原生完整8字段记录转储，包含未知和已知空行；不是仅边数比较。空间前缀也改变资源组成，不能称纯节点数缩放规律。
- `results/scale_capacity_region_audit_20261023_v1.json`全部48条件独立审计：4域×2模式×8/16/32/64/96/128MiB，固定seed随机次序，CPU124，每格新进程，`prlimit --as=soft:hard`的两个上限取相同字节数。每次成功必须与相应已穷举验证native结果完全一致；只有exit3及精确ALLOCATION_FAILED才作容量失败，其他故障停止。
- 最大域96MiB限制：compact完整扫描通过、CSR分配失败；128MiB双方通过。前三组最低已测成功上限双方同为16/32/64MiB。**这是整个native解码进程RLIMIT_AS（虚拟地址空间），不等于RSS、完整router或板卡容量；未测精确最低门槛，不能声称节省128−96=32MiB。**转换、fixture、搜索占用/轨迹不在受限进程里。各格单次，不作速度统计。
- 规模owner3361172/exec14732、容量owner3549882/exec93312及独立审计均结束，不重跑。新文件`src/scale_domain.py`、`src/native/scale_domain_scan.cpp`及scale相关脚本已绑定；保留产物和源码。回归日志`regression_scale_domain`、`regression_scale_capacity`、`regression_scale_capacity_audit`均在results的20261023_v1版本，含真实图、未知边界、坏记录、错误资源上限/缺格/错结果拒绝。
- 原四条CPU链仍运行：旧canonical20/63；站点正式63次统计第1进程；源图验证2/3；模板共享验证1/5。当前状态以/proc和原pipeline为准，不增加竞争队列。完整特殊资源模型、完整性能终态、完整router容量及实卡DDR/HBM/功耗尚未完成，目标保持active。

## 站点首次/驻留三条件独立审计完成，正式63次统计已启动

- `results/native_site_runtime_validation_audit_20261023_v1.json`：3/3条件全部两批1062网原始结果独立复核，CSR/direct、compact/direct、compact/expanded与冻结参考语义一致。报告SHA256 3591fd8ecd96715a08df7b5cd685889c093f01143983f983e3129f1afe5e7455，已与原pipeline绑定和auditor源码摘要核对。
- 原validation1716135与audit3328897均终态；原queue1739121已自动进入statistics，owner3457381，CPU127，63进程，状态`results/native_site_runtime_pipeline_20261023_v1.json`。勿重启验证或改冻结依赖。这里只每条件1次，尚无重复统计结论。首批route诊断CSR496.032秒、compact/direct764.017秒、compact/expanded453.575秒，展开成本已另计准备；共享host与14实例模型限制保留。
- 旧canonical统计已执行器验19/63，仍非物理有效模型；源图验证前两条件通过、第三compact/direct继续；模板粒度首span4完成两批，原driver进入第二条件，独立全5条件审计未到。下方历史进度不再作为实时状态。

## 时钟物理观测与原语行为已审计，尚未授权完整时钟模型

- `results/clock_semantics_stage_20261023_v1.json`汇总物理捕获与实际Vivado2022.2 XSim原语行为；本轮复核5个绑定文件摘要。`results/clock_semantics_capture_20261023_v1.json`的权威输入为`data/netlist/clock_semantics_capture_20261023_v3/{baseline,probe}.tsv`：两站点、8BEL、33BELpin、13sitepin、4sitePIP、21配置值。4个探针sitepin有真实网所有者，尽管IS_USED=0；不能将该字段等同空闲。
- ROW观察CE_TYPE=ASYNC、leaf观察DELAY=VAL0；两份timesim netlist都没有显式BUFCE实例，不能据此推断内部常量或反相。v2/baseline.tsv因MCP重复setter被跳过而误标，`INVALID_CAPTURE.txt`保留，不用于结论。后续MCP状态赋值/source使用唯一运行标记并核实实际状态。A会话恢复`site_full_applied_20261023_v1/routed.dcp`。
- `data/derived/clock_primitive_sim_20261023_v1/report.json`：未改本机vendor原语，ROW/LEAF×SYNC/ASYNC×CE/I反相共16组，192行为样本全部通过；XIL_TIMING编译，无SDF，不是物理时序签核。保留输出done声明初始化警告VRFC10-8426，独立trace审计验证每组12样本及全部完成ID；未抑制断言。回归`results/regression_clock_semantics_evidence_20261023_v1.log`含14类证据篡改拒绝。
- 真实常量连接、实际反相选择、leaf delay/test及共享/保护占用仍缺。不得把两个联合探针实例直接并入已有14实例模型。

以下性能链的历史进度须以原进程和终态证据为准；新规模实验正在另行验证。

## 最新：四种模板共享粒度全区域等价通过，五条件完整路由与35进程统计已门控启动

- 新 `src/template_scope.py`只改变冻结模板字典的空间共享范围：全区域、同SLR内16×16、4×4、1×1 tile网格；原规则/例外、规范节点、wire别名、属性和未知域完全不变。不重新训练family，不按模板合并动态资源。粒度是共享范围，不是重新学习规则或删减图。
- `data/derived/template_scope_region_20261023_v1/report.json`全部4种通过独立静态/例外/分组审计及 `src/native/template_scope_check.cpp`逐节点完整邻接比较。每模式274732nodes、220973known、53759unknown、11913known-empty、1100754directededges完全一致。全区域产物与原compact逐字节相同。regression5项通过 `results/regression_template_scope_20261023_v1.log`，包含真实capture所有行、错误alias/属性、越组共享、非法粒度/CSR/覆盖拒绝。
- 镜像字节global93507968/span16 93946944/span4 96954624/span1 107368384；模板数440/3774/26388/104278，规则记录1868/16596/117552/467218；116695个fallback源保持。单tile共享已大于CSR98255808B。这是存储证据与完整邻接语义，不是路由性能统计。
- 新pipeline2703564/exec62529已实查存活，driver2703565/native2710957，CPU126，当前验证worker0 span4。`results/template_scope_runtime_pipeline_20261023_v1.json`：先CSR/global/span16/span4/span1五条件各首次+驻留两批全1062网，原生binary和mode-specific routing/sites输入复用既有验证版，cache4096/direct；全5进程原始语义独立审计通过后才自动执行7重复×5=35进程，最终再次独立审计。任何失败停止，不重提。
- 输出 `data/derived/template_scope_runtime_{validation,statistics}_20261023_v1`，目标 `results/template_scope_runtime_{validation,statistics}_audit_20261023_v1.json`；绑定 `results/template_scope_execution_binding_20261023_v1.json`。新checker的9类绑定/完整性/计时错误拒绝通过 `results/regression_template_scope_runtime_20261023_v1.log`。**该pipeline/state及验证plan.files已经冻结，勿修改相关脚本/源码/二进制/证据。**
- 源图集成首CSR已独立审计 `results/source_to_route_partial_001_20261023_v1.json`，仅1/3：新镜像/全部fixture实际消费、两批1062网语义通过，application1118.713s、outer process1215.609s；read14.932s/serialize22.399s/image-adapter8.163s/fixture-build2.462s/native-process1069.258s。尚不能比较两种表示。源owner2142179现执行compact/expanded（worker2635316）；audit2205877和21进程queue2407216仍原链。
- 内存口径补充 `results/source_to_route_memory_scope_20261023_v1.json`：该CSR的native_child_peak_kib=6221632来自RUSAGE_CHILDREN，含fork/pre-exec继承的高水位；native batch VmHWM为3635188/3635348KiB，是exec后的程序峰值。两个口径不混同、不与parent峰值相加。本机探针 `results/fork_memory_accounting_20261023_v2.json`复现ru_maxrss74888KiB vs post-exec VmHWM9556KiB。v2在platform查询可能产生辅助进程前捕获usage；v1保留为初步记录。未改冻结计量或结果。
- 原站点first/resident验证CSR和compact/expanded执行器已验，现compact/direct2615722，owner1716135/queue1739121继续；旧canonical4146936继续。全目标仍缺完整特殊资源模型、规模范围、反复性能终态及实卡平台DDR/HBM/功耗，不宣称完成。

以下为历史检查点；活跃状态以/proc和原队列为准。

## 最新：转换统计已独立审计，完整软件链路验证及21进程统计门控已提交

- `results/packed_conversion_statistics_audit_20261023_v1.json` 已完成14/14独立审计，SHA256 `9c650cfb0fdd4b5d20b74ac7c9a3a17191463a27911ff0e449732ce93707b63e`。CSR/compact各7次，捕获TSV→AGR中位数38.224/56.338秒、进程wall40.835/59.065秒、child峰值6205536/7015116KiB；全部产物与原图镜像逐字节一致。转换旧owner1876655和queue1900286已经终态，不要重启。范围不含采集/训练/fixture/路由/板端；页缓存、并发host、非fsync写入限制保留。
- 新 `scripts/source_to_route_experiment.py` 在同一worker内实际read_export→新AGR→全1062查询/14实例site输入→native首次与驻留两批。图镜像和四类fixture逐字节校验，native命令指向新文件；直接测application总时长，预检/后审计在外层process wall内单列，两个进程峰值不相加。当前 `data/derived/source_to_route_validation_20261023_v1` owner2142179/worker2145509/native2169527（CPU125）仍运行；这是每条件1次的三条件验证，尚非重复统计。
- 独立集成audit queue2205877等待原执行，状态 `results/source_to_route_audit_pipeline_20261023_v1.json`，目标 `results/source_to_route_validation_audit_20261023_v1.json`。冻结该state.files及源plan.files，勿改依赖或重提。
- 新统计queue2407216/exec50824已实查存活，`results/source_to_route_statistics_pipeline_20261023_v1.json` stage wait_existing_integration_audit。等前述原audit完整通过后，自动执行 `scripts/source_to_route_statistics.py`：7块×3条件=21个新进程，CPU125，每块随机顺序、每进程重新生成全部输入并执行两批全网路由。每块由原冻结 `check_source_to_route.py` 重读原始语义审计，最后 `check_source_to_route_statistics.py`核验全部哈希/顺序/计时/7重复，输出总体和配对比值。任何失败停止不重试。输出 `data/derived/source_to_route_statistics_20261023_v1`，目标audit `results/source_to_route_statistics_audit_20261023_v1.json`。当前尚未开始21进程；绑定 `results/source_to_route_statistics_execution_binding_20261023_v1.json`。
- 统计审计两项测试/13类故障拒绝通过 `results/regression_source_to_route_statistics_20261023_v1.log`；这里只证明覆盖/顺序/计时检查，不是全数据已通过。队列state.files已冻结，不再修改driver/checker/测试日志。
- 原站点首次/驻留验证1716135及queue1739121仍活跃，CSR两批执行器已验，当前compact/expanded child2185883；原canonical4146936执行器12/63，运行第13进程。原canonical候选物理失败，不能当物理有效站点模型性能。后续保持原链。
- 全目标仍active：14实例以外的特殊资源常量/反相/动态保护语义、模板粒度/规模、真实平台DDR/HBM/外部IO/功耗仍需完成。新application wall是已捕获TSV到两批软件路由，不冒称全Vivado采集到板端端到端。

以下为历史检查点；进程状态以上述实查和实时/proc为准。

## 新生成图镜像→完整原生查询/站点输入的重建接口已验证

- 新 `src/runtime_fixture_builder.py::build_runtime_payloads(image,snapshot,queries,fixed,proofs,pip_records)`复用已验证编号/保护/14实例模型规则，只使用调用方提供的已加载数据，不重读全图或隐式取旧输入。调用方必须验证证据摘要；辅助函数本身不是证据授权器，也未扩大模型范围。
- `scripts/check_runtime_fixture_builder.py`校验全部旧输入/物理证据摘要后，读取完整独立域，再使用转换矩阵worker000 CSR与worker001 compact新生成镜像构建。`data/derived/runtime_fixture_rebuild_20261023_v1/report.json`通过：每模式routing.txt/queries.json/sites.txt/symbols.json四文件与原已验证输入逐字节一致，全部1062网/274732节点、4399保护节点/2787保护PIP、1100固定bit记录/14实例。
- 重复探针证据、非法64bit配置值、改变物理PIP属性三类输入被拒绝。绑定 `results/runtime_fixture_rebuild_binding_20261023_v1.json`。测试已结束（exec37680退出0），不是新驻留任务；单次image_load/build计时仅诊断，尚无fixture统计或完整端到端结论。
- 下一步用该接口串联同一worker的read_export→write_packed→fixture生成→native路由，实际消费新产物并整体计时，逐个与参考哈希/语义核验；别把独立阶段中位数相加冒充端到端。可使用独立CPU125，与现有CPU0/126/127队列区别，但并发host限制仍要披露。
- 转换owner1876655/审计queue1900286均活跃，执行器10/14，最终独立审计尚未开始（仍首worker独立partial）。站点验证1716135/CSR1723135、queue1739121仍在原链，CSR两批尚未发布；旧canonical4146936执行器11/63，当前worker011 compact/direct/cache64。保持所有plan/queue冻结依赖，不竞争重跑。

## 捕获TSV→AGR转换成本矩阵运行中，首worker独立审计通过

- 新 `scripts/packed_conversion_benchmark.py`固定独立域948MB TSV及原训练bank，CSR/compact各7个新进程，seed20261023逐重复随机顺序、CPU126；分别记录read_export、必要bank_load、serialize、conversion总计、校验时间、进程wall和child峰值。CSR不承担无用的模板例外生成成本。每次产物必须与已验证原AGR逐字节相同。
- 输出 `data/derived/packed_conversion_statistics_20261023_v1`；owner1876655/exec29579，当前执行器3/14通过。前两次预检分别因bank文件没在旧plan直接列出、文件SHA与对象SHA混用而退出，未启动worker/生成输出；保留v1/v2日志。实际运行日志 `results/packed_conversion_statistics_20261023_v3.log`，文件摘要按冻结config、对象摘要按冻结report独立核对。
- 首CSR已独立重读原始文件/二进制header/sections、计时闭合与收据，`results/packed_conversion_partial_001_20261023_v1.json`，仅1/14：read15.395s、serialize22.500s、conversion37.895s、child峰值6205320KiB、process40.727s。不能据单样本比较性能。真实worker正常审计及伪造wall/图范围拒绝测试通过 `results/regression_packed_conversion_audit_20261023_v1.log`。
- 唯一下游audit queue1900286/exec62541，状态 `results/packed_conversion_audit_pipeline_20261023_v1.json`，等原owner结束后自动独立审计全部14进程，目标 `results/packed_conversion_statistics_audit_20261023_v1.json`；失败不重试。冻结conversion plan.files和queue.files，勿改源/依赖/输入或重复启动；绑定 `results/packed_conversion_execution_binding_20261023_v1.json`。
- 成本范围仅已捕获TSV→AGR，仍不包括Vivado采集、bank训练、query/site fixture准备、路由和板传输。无fsync，文件页缓存与并发host不受控；不能称完整源图到板端到端。后续需把fixture成本与同批路由接入直接测量，不能简单相加不同重复的中位数冒充实测端到端。
- 站点first/resident验证owner1716135/CSR1723135及统计门控queue1739121仍实查活跃；当前CSR首批完成4轮，完整2批结果尚未发布。旧canonical统计4146936已10/63，worker010仍运行。

## 物理有效站点模型first/resident验证已启动，正式统计按独立审计门控

- 新 `src/native/site_runtime.cpp`/binary `build/native_site_runtime_20261023_v1`：完整站点协商每进程两批，保留graph/cache、重置node/site占用与history；CSR/direct、compact/direct、compact/expanded，展开时间计入准备。每批route、逻辑访问/缓存差分计数、进程生命周期VmHWM；导出单独计时并flush。输入转换仍在child计时之外，不称source-graph端到端。
- `results/native_site_runtime_protocol_20261023_v1.json`三条件真实单查询协议通过（两批语义等于原native、direct驻留零miss、expanded绕过LRU、峰值/时间字段合理），不是全量结论。独立审计器 `scripts/check_native_site_runtime.py` 的正例和7类语义/计时/收据篡改拒绝测试通过，日志 `results/regression_native_site_runtime_audit_20261023_v1.log`。
- 全1062查询验证已启动：`data/derived/native_site_runtime_validation_20261023_v1`，owner1716135/exec75213，初始CSR child1723135，CPU127，3进程×2批，cache4096/repeat1。driver `scripts/native_site_runtime_benchmark.py` 每批与已独立验证的native site参考全部语义字段比较。
- 唯一下游queue1739121/exec87865，`results/native_site_runtime_pipeline_20261023_v1.json` stage wait_validation。验证结束先独立原始审计3条件，通过后自动启动63进程（3表示×cache0/64/4096×7重复、固定seed），最后独立审计全部统计。任何失败停止后续，不自动重试。**验证plan.code_inputs_and_references及pipeline.files全部冻结，勿改源/头/输入/检查器或竞争启动。** 执行绑定 `results/native_site_runtime_execution_binding_20261023_v1.json`。
- 旧canonical统计queue3591840/statistics4146936仍存活，执行器10/63，当前worker010 compact/direct/cache4096；CPU0。两套模型不可混称，两个队列均保留。并发host/OS page cache不受控已在plan披露；正式统计尚无结论。

## 原生真实站点完整等价通过；锁定引脚后的联合时钟探针通过

- 原native执行owner983662/CSR987785/compact1200236与审计1111940/1494418均完成，不再当运行任务。`results/native_site_routing_check_20261023_v1.json` status verified_native_site_routing，pipeline complete且报告hash已复核。
- 两模式全部1062网/17682 PIP、四轮866→205→21→0、16836连接的最终树/真实边属性/站点需求/冲突/状态/成本/expanded/blocked/完整unknown集合，与已物理验证Python站点参考一致。每模式3网有site需求。只覆盖14已测实例模型，非完整器件语义；Python未保存逐连接路径，不声称该项等价。物理结论由最终树精确相同继承，不是新全网Vivado重跑。
- 单次native route_ms：CSR504868.566892、compact721806.770494；两者cache_hits5780146/misses136095859。仅并发环境下诊断，不是统计加速。源码/二进制/审计结果存档 `results/source_snapshots/native_site_verified_20261023_v1/manifest.json`；保留原哈希绑定文件。
- 新 `adapters/complete_clock_row_probe_20261023_v2.tcl`从原baseline读取1099 LUT的逻辑→物理输入映射，核对isolated一致，再完整设置LOCK_PINS并重布1061网。Vivado2022.2官方UG912文档与本机会话验证支持。输出 `data/netlist/clock_row_route_probe_full_20261023_v2`。
- `scripts/check_clock_row_probe_locked.py` 独立检查通过：1099 LUT REF/LOC/BEL/INIT/原pin映射/LOCK_PINS一致；1833cell、全部物理端点和逻辑连接、1576保护网组不变，目标11 PIP保持，1277可布线网全完成/0错误/仅旧HDOOC-4；WNS6.265/WHS.014，外部168in/175out仍未约束。行CE_TYPE=ASYNC、叶DELAY=VAL0全上下文与isolated一致。综合索引 `results/clock_row_locked_stage_20261023_v1.json`。
- 旧未锁定版本564网端点变化失败证据保留。新探针只覆盖BUFCE_ROW_FSR_X21Y6 CE→OUT与BUFCE_LEAF_X110Y26 CLK_IN→LEAF这条联合路径；常量/反相及完整动态/保护占用仍未完整建模，未把两个实例直接加进14实例模型。A MCP恢复原site_full验证checkpoint，2/2 todos done，无待处理调用。
- 正式旧canonical统计执行器9/63，当前worker009 compact/expanded/cache64，原queue3591840/statistics4146936继续。下一步做物理有效站点模型的first/resident/expanded/cache公平统计，并补完整时钟语义与实卡DDR/HBM/功耗；不能把旧canonical统计当新站点性能。

## 行时钟联合探针：完整路由/DRC通过，但端点保持失败，不能授权模型

- 新 `scripts/plan_clock_row_probes.py`在完整CSR域内、保护节点/PIP不变下检查26行时钟PIP。普通边上下文无候选；允许pseudo的诊断上下文找到10条CE候选，每条还需要1个未验证leaf CLK_IN→CLK_LEAF，CLK_IN行时钟候选未找到。`results/clock_row_probe_plan_20261023_v1.json`保留所有26×2策略结果；域内/最短子路径过滤结果不是全器件不可能性证明。
- 最短11边真实单sink网 `original_cost/genblk1[3].h_val_y_reg[55]_i_2_n_0`；实例BUFCE_ROW_FSR_X21Y6（CE_PRE_OPTINV→CLK_OUT）+BUFCE_LEAF_X110Y26（CLK_IN→CLK_LEAF）。输入绑定 `results/clock_row_probe_input_20261023_v1.json`。隔离应用 `data/netlist/clock_row_route_probe_20261023_v1`显示ROUTED，但RTSTAT-13导致部分路由DRC未运行，不能仅凭该阶段认证。
- 保持探针固定并由Vivado重布其余1061网，输出 `data/netlist/clock_row_route_probe_full_20261023_v1`。完整1277网全路由/0错误/仅旧HDOOC-4，WNS6.248/WHS.007；目标11 PIP和规范节点不变，保护网与cell LOC/BEL/逻辑连接保持。行CE_TYPE=ASYNC、叶DELAY=VAL0在isolated/full阶段一致。
- **`verification.json` status probe_validation_failed：564网site_pins改变**；样例cg_q[10] B4→B6、B5→B4等，显示Vivado路由后的LUT输入重映射，目标探针网本身端点没变。保持严格端点不变条件，不将无DRC当模型通过。下一步读取原LUT逻辑pin→BEL pin映射，核实支持的LOCK_PINS操作，锁定原物理引脚再重测；不得改旧失败证据或降低比较要求。
- 审计器 `scripts/check_clock_row_probe.py`，日志v1因baseline DRC路径错误退出（无报告），改用已有 `results/netlist_baseline_drc_20261022.rpt` 后v2正常发布上述负结果。A MCP已恢复 `data/netlist/site_full_applied_20261023_v1/routed.dcp`，3/3 probe todos done；无未完成MCP调用。执行器/审计队列冻结依赖未改。
- 原native compact1200236第三轮已结束进入第四轮附近，owner983662、审计1111940仍在原链；正式统计执行器8/63，当前worker008 compact/direct/cache64。再次工作先实查，不重复提交。

## 行时钟端点映射补齐；原生CSR完成，compact仍运行

- 复用A MCP会话只读导出 `adapters/export_clock_row_pins_20261023_v1.tcl` → `data/raw/region_u280_20261022_v1/clock_row_pins_20261023_v1.tsv`。实际Vivado2022.2/xcu280，39端点/13 BUFCE_ROW_FSR站点，26 PIP（CE_PRE_OPTINV→CLK_OUT与CLK_IN→CLK_OUT各13）。没有改变载入设计或现有模型。
- `scripts/check_clock_row_mapping.py`在CSR/compact分别核对全部26条forward pseudo/directional边、端点规范节点与别名，输出 `results/clock_row_mapping_20261023_v1.json`。全部通过；CE端点跨tile别名也一致。`tests/test_clock_row_mapping.py`真实capture+5类不完整/歧义输入拒绝通过，日志 `results/regression_clock_row_mapping_20261023_v1.log`。
- 这只补端点映射，配置观察多数NOT CONFIGURED；IS_USED=0不等于可用，不能将默认SYNC/VAL0当已验证需求。下一步需验证两类row route-through的CE/CLK输入、常量/反相、delay/test及保护占用。现有冻结14实例模型不变，v3仍推断表。
- 原生CSR987785已正常退出，`csr.receipt.json` exit0；原始结果汇总1062网/17682 PIP，四轮node冲突866→205→21→0，site冲突/未完成均0，route_ms504868.566892。仅汇总与Python一致，完整checker还未执行，不作完整等价或统计性能结论。
- owner983662已自动启动compact child1200236（CPU127，exec92181）；审计queue1111940/exec69369仍等原执行完整终态。原统计执行器已验7/63，当前worker007 compact/expanded/cache4096。继续保护所有冻结依赖，不竞争重跑。

## 原生站点独立审计器与下游队列已就绪（结果待运行完成）

- 新 `scripts/check_native_site_routing.py` 按模式反解独立编号池，逐边核对方向/完整属性，重算最终site需求；与已物理验证Python结果比较全部最终树、需求、每轮node/site冲突、未完成网及每连接status/cost/expanded/blocked/unknown完整集合。Python未保存连接路径，不声称逐连接路径等价。两模式完成才给完整状态；单模式明确partial。
- `tests/test_native_site_verifier.py`正常样例及9类篡改拒绝通过，日志 `results/regression_native_site_verifier_20261023_v1.log`；尚无真实全网审计结论。
- 唯一下游审计queue PID1111940/exec69369，`results/native_site_audit_pipeline_20261023_v1.json` status waiting_existing_execution；绑定原owner983662的proc启动ticks，等待原执行结束，再自动运行两模式独立审计，目标 `results/native_site_routing_check_20261023_v1.json`。失败只记录，不重提任务。**该state.files中的checker/queue/依赖也已冻结，不要修改或重复启动。**
- 原生执行owner983662/CSR987785实查存活，第三轮已到450网，随后自动compact；原统计queue3591840/statistics4146936存活，已执行器验6/63，当前worker006 compact/expanded/cache0。保留历史PID但以实查为准。

## 原生真实站点全网执行已启动（尚未独立审计）

- 新 `src/native/site_inputs.hpp` 严格解析NATIVE_SITES_V1，保留uint64配置mask、物理资源ID、分类配置与固定占用；非法整数/越界/重复/矛盾/尾随数据拒绝，其他pseudo仍未知。新 `site_bench.cpp` 接完整站点协商，输出最终树、需求、每轮冲突和连接状态/成本/计数/unknown集合。
- `results/regression_native_site_integration_20261023_v1.log`：6项测试通过，含两种真实模式的14实例payload及1100固定bit记录、11类错误输入、原事务/search/ledger/多网差分。不是完整真实路由已通过。
- 原生全1062网已启动 `scripts/native_site_experiment.py`，输出 `data/derived/native_site_routing_20261023_v2`；owner983662/exec92181，首次CSR child987785，CPU127，之后自动compact。plan冻结所有证据/源码/二进制/输入，80轮/200000预算/cap8/cache4096。**不要修改plan.files中的文件或竞争重跑**；终态后独立反解与4.5GB Python站点routes逐轮比较。执行绑定 `results/native_site_execution_binding_20261023_v1.json`。
- 首次v1在启动worker前因provenance辅助模块路径写错退出，日志保留；已修正为scripts/real_experiment.py，v2才是实际执行。不要将空v1目录当运行。
- 原统计queue3591840/statistics4146936已实查存活，执行器已验5/63，当前worker005 CSR/direct/cache64；仍仅首worker有独立partial审计。它测旧canonical模型，不是当前物理有效站点模型。

## 原生真实站点输入适配完成（尚未运行native站点全网）

- 新 `scripts/prepare_native_site_inputs.py --mode csr|compact`分别生成 `data/derived/native_site_{csr,compact}_inputs_20261023_v1/{sites.txt,symbols.json,manifest.json}`。两模式均14已测PIP、1100固定bit记录（1099功能LUT+仅1个已复现默认约束）、990物理资源符号，反解完整payload一致；复核 `results/native_site_inputs_check_20261023_v1.json`。
- 绑定已物理验证site_full_stage、原Pythonplan全部冻结输入/代码、4.5GB routes输入摘要、固定配置和所有物理探针证据。逐PIP从真实原始capture取up/down/属性，再核对各AGR canonical alias、唯一forward边和全部属性，不凭名称推断合法性。
- sites.txt schema NATIVE_SITES_V1：resource/value/attribute counts；fixed bits三元组、fixed signals和fixed categorical counts（本次后两者均0）；14需求各自(tileID,pipID)+signal/bit/value条目；末尾pseudo属性ID列表。CSR/compact编号池不同，后续CLI/调度必须把manifest.image、routing_fixture与sites.txt哈希成组核对，不能跨模式复用。
- 其他pseudo仍未知，不读取/授权v3推断表、不删除图边。准备完成不代表native站点路由已跑；下一步新增CLI使用site_routes.hpp跑全部1062查询并逐轮对照新Python参考，再检查压缩表示等价。
- 正式runtime执行器已核验3/63，当前第4进程CSR/direct/cache4096；queue3591840/statistics4146936继续冻结运行。仍只有首worker有独立partial审计，最终统计尚未完成。

## 原生站点多网协商组件组合完成（真实集成待做）

- 新 `src/native/site_routes.hpp`组合配置标签search、canonical节点占用和DemandLedger：释放旧树/站点需求、多sink继承、node/site历史代价及cap、固定site约束、保护/保留端点、失败状态均实现；未改冻结runtime源。
- `tests/test_native_site_routes.py`编译-Werror，12场景对照Python最终nodes/PIPs/site_demands、每轮canonical/site冲突、未完成网和连接成本/计数/unknown；覆盖三类站点冲突、兼容mask、固定配置、未知语义、预算、多sink、同时node/site冲突及protected PIP。日志 `results/regression_native_site_routes_20261023_v2.log`，源码闭包绑定 `results/native_site_routes_binding_20261023_v1.json`。
- 下一步新增真实适配：用各模式独立编号池映射保护/PIP属性、14实例完整证据payload、1099功能LUT与已验证默认位，资源ID必须是物理身份；再跑全1062查询CSR/compact并与 `site_routing_all_known_instances_20261023_v1` 精确比较。不能批量授权推断v3表或把12合成场景称真实全网。
- 正式runtime统计执行器已核验2/63，目前第3进程CSR/direct/cache0；原queue3591840/statistics4146936仍运行。仅首worker已独立partial审计，尚无最终统计结论，继续冻结此前runtime代码。

## 原生站点协商账本组件通过差分检查；正式统计已审计1/63

- 新独立 `src/native/site_ledger.hpp`实现signal/INIT bits/categorical三类协商资源，按冲突owner集合统计、release/replace和与Python相同的新增/扩展需求历史代价；不提前硬拒绝待协商冲突。
- `tests/test_native_site_ledger.py`编译-Werror，8步与Python DemandLedger逐步比较所有冲突owner和4组增量penalty，覆盖兼容/不兼容mask、同net排除、已存在需求不重复收费和释放；日志 `results/regression_native_site_ledger_20261023_v1.log`，绑定 `results/native_site_ledger_binding_20261023_v1.json`。
- 下一步组合native配置标签搜索、canonical占用和本ledger成完整站点多网驱动，接实际14实例证据与全1062查询，和新Python站点结果比较；组件测试不是实际全网集成。
- 正式63进程矩阵首worker（compact/direct/cache0）已完成并独立原始审计 `results/native_runtime_statistics_partial_001_20261023_v1.json`，仅1样本，不做性能推断。queue3591840/statistics4146936仍运行，当前worker001 child225659（compact/direct/cache4096）。此前runtime依赖继续冻结，不竞争重跑。

## 最新：完整1062网站点候选物理验证通过，统计矩阵继续

- `results/site_full_stage_20261023_v1.json`：全1062网/17682 PIP，4轮866→205→21→0；完整准备、Vivado应用、独立readback与quality均通过。原Python1396247、准备32948及MCP cell1531已结束，不要重跑或把下文历史PID当存活。
- `data/netlist/site_full_applied_20261023_v1/{readback_check,quality_check}.json`：1833单元放置和所有连接不变，1576保护网组不变，1062路径精确，1277可布线网全完成/0错误，无新增DRC（仅原HDOOC-4）；WNS5.946ns/WHS0.015ns，较基线-0.584/-0.005ns，内部约束仍满足，外部168in/175out未约束。
- 只覆盖已测14 LUT实例的模型，3网实际有站点需求；全查询物理通过不等于所有图资源族模型完整，也未完成站点模型CSR/模板等价、native实际站点适配或实卡性能。旧84站点失败证据保留，不得冒称旧候选修复为同一路由。
- A MCP `vivado-20261023-072116-f6c0019b` PID2607458当前载入新全网候选，3/3todos done，maxThreads1；操作前list_sessions核实，B会话不动。
- 三条件完整first/resident独立审计通过 `results/native_runtime_validation_audit_20261023_v1.json`。正式63进程仍运行：queue3591840/session44414，statistics owner4146936，首child4146940，日志 `results/native_runtime_pipeline_20261023_v1.log`；此前runtime源/输入继续冻结。统计仍针对旧canonical模型，不自动代表本次物理有效站点路由。

## 当前最优先：完整站点候选Vivado回写进行中

- 原Python站点1396247/session69275已完成退出，不再运行：4轮866→205→21→0规范节点冲突，全部1062网/17682 PIP、0site冲突/0未完成，report独立检查通过已提供的14实例模型；3网实际有site_demands。模型仍部分覆盖，不是全模型完成。
- `prepare_site_routes.py`全量重算验证已完成，候选 `data/derived/site_routing_all_known_instances_20261023_v1/candidate_routes.tsv`，日志 `results/site_full_candidate_preparation_20261023_v1.log`。routes.json约4.5GB，勿无目的重复整载。
- A MCP `vivado-20261023-072116-f6c0019b` PID2607458已实查并恢复原baseline，maxThreads1；正在 `source adapters/apply_site_full_20261023_v1.tcl`，functions exec cell1531仍等待。不能在同会话执行其他Tcl或竞争重跑；先wait原cell/查status与本地日志。输出 `data/netlist/site_full_applied_20261023_v1`，失败会保存failure报告。B会话不动。
- 完成后检查具体成功/失败，再依次做 `check_netlist_readback.py .../routes.json .../applied_dir` 与 `check_netlist_quality.py`；不能只看节点/PIP数或MCP退出码。todos baseline已done、apply_full active、audit_full待做。
- 三条件完整首次/驻留独立审计通过 `results/native_runtime_validation_audit_20261023_v1.json`，原验证3563530/3828645已退出。原队列3591840已启动正式63进程矩阵，统计owner4146936、首次child4146940，日志 `results/native_runtime_pipeline_20261023_v1.log`，输出 `data/derived/native_runtime_statistics_20261023_v1`。继续冻结此前runtime代码/输入，不竞争提交。

## 原生配置标签搜索组件完成差分验证（尚未真实集成）

- 新独立 `src/native/site_search.hpp`按(node, signal/bit/categorical demands)保留不同标签，以serial稳定处理等代价；支持多根初始树需求、固定/动态兼容回调、unknown pseudo/unknown adjacency区别和预算。正整数hop/congestion代价；不支持Python可接受的任意浮点代价。
- `tests/test_native_site_search.py`编译-Werror，12场景与Python site_search对照，包括同节点替代配置、已有树需求、固定/动态占用、未知、预算、非法需求和代价。日志 `results/regression_native_site_search_20261023_v1.log`；绑定 `results/native_site_search_binding_20261023_v1.json`。
- 仍缺真实ID/逐实例证据适配与站点协商ledger、完整1062查询对照及物理验证。verified标记不能取代证据payload绑定，v3推断表不得批量授权。没有修改任何运行依赖。
- 长任务继续：站点1396247第四轮已1050网；完整first/resident验证3563530当前compact/direct3828645接近结束，原统计队列3591840等终态。任何新动作先实查进程/receipt，不竞争重跑。

## 原生站点事务组件完成差分验证（尚未接搜索）

- 新独立 `src/native/site_state.hpp`实现物理信号资源独占、64bit INIT掩码兼容、分类配置共享、固定约束、原子replace/release；不依赖/改动运行中的原生或Python模型。
- `tests/test_native_site_state.py`编译-Werror，18动作与Python SiteState逐步比较接受/拒绝和完整动态状态，含重叠位、冲突事务保留原状态、释放、固定资源、无效/未验证需求；日志 `results/regression_native_site_state_20261023_v1.log`，绑定 `results/native_site_state_binding_20261023_v1.json`。
- Native Demands.verified只是输入防错标记，不是合法性证书。后续适配必须绑定真实物理ID和逐实例证据payload；不得把v3推断表批量设为verified。尚缺配置标签搜索/站点协商ledger与全网真实对照。
- 原长任务不变：Python1396247第四轮已到750/1062；验证3563530当前direct compact3828645，原统计队列3591840等三条件全部通过。继续冻结其依赖。

## 最新：两条件首次/驻留审计通过，通用MUX推断足迹修正

- `results/native_runtime_two_conditions_audit_20261023_v1.json`独立重读CSR/direct与compact/expanded各两批全1062网，均语义/哈希/时间汇总闭合；2/3条件，仍不是正式统计结果。原验证3563530/session27491当前compact/direct child3828645；统计队列3591840仍等待。
- `results/site_requirement_footprint_gap_20261023_v1.json`发现通用v2推断表缺OUTMUX输出独占及D6选择：7个已有MUX探针均有缺口；正在跑的14实例runner早已补这两项，不受影响。
- 新 `scripts/complete_inferred_site_footprints.py`输出 `data/derived/region_all_nets_cap8_20261022_v1/site_requirements_v3.json`，42970 PIP全保留，为20832 MUX推断条目补足约束；14物理探针完整payload匹配，全部实例status保持不变，仍是partial/inferred，不得整体当可用搜索需求或合法性证书。未修改任何运行模型、v2、baseline或图。
- 站点全网1396247第四轮已开始50网；第三轮21冲突/0未完成，继续冻结依赖。

## 最新：CSR完整首次/驻留独立审计通过，其他条件仍运行

- `results/native_runtime_csr_partial_audit_20261023_v1.json`重读原始两批和回执：worker000两批完整1062网语义与已验证native一致，指标与汇总/哈希对应，process wall覆盖加载+两轮route+导出阶段。只是1/3验证条件，不是正式63进程结果。
- 新独立审计器 `scripts/check_native_runtime.py`核验固定seed矩阵、全部原始语义与计时闭合并重算汇总；完整验证完成后用 `--capacities 4096 --repeats 1`，正式矩阵完成后默认参数。`--partial`只审计已发布worker，明确不作完整结论；输出使用新路径。
- 原验证owner3563530/session27491继续，当前compact/expanded worker001 PID3717098，随后compact/direct；队列3591840/session44414仍等待，禁止竞争提交或改冻结代码。
- materialized/expanded模式绕过行LRU，cache容量条件作为控制，不应解释为其真实缓存容量收益。原native两模式表、完整站点/物理验证和实卡限制仍适用。

## 当前运行：完整原生首次/驻留验证与唯一统计后续队列

- 完整1062查询验证owner PID3563530 / exec session27491，输出 `data/derived/native_runtime_validation_20261023_v1`，日志 `results/native_runtime_validation_20261023_v1.log`；首worker PID3563848，固定CPU见plan。3条件（CSR direct、compact direct/expanded）各同进程first/resident两批，全部语义须与已审计native完整结果一致。
- 唯一后续owner PID3591840 / session44414，`scripts/native_runtime_pipeline.py`，状态 `results/native_runtime_pipeline_20261023_v1.json`。先核实真实进程，不竞争重跑。原验证真正退出且三条件全量通过、plan/原始输出哈希核对后，才运行正式63新进程：3条件×cache0/64/4096×7重复，固定随机种子20261023。失败即停，无自动重试。
- 冻结 `scripts/native_runtime_{benchmark,pipeline}.py`、`src/native/{netlist_runtime.cpp,netlist_routes.hpp,netlist_connect.hpp,packed_graph.hpp}`、binary和全部plan输入，绑定 `results/native_runtime_execution_binding_20261023_v1.json`；不要运行时改源码或覆盖原输出。旧集成源码/二进制快照保持。
- 当前只是提交/运行，不称全量首次/驻留通过或正式统计完成。输出/导出成本和native子进程全生命周期单列，保留完整相同轨迹；fixture/packed转换在进程外、Python父进程RSS不计子进程，不能称原始图端到端或完整物理路由。
- 站点Python PID1396247继续，前3轮866→205→21规范节点冲突、0未完成；其冻结依赖继续不改。完整站点模型、物理全网验证、DDR/HBM实卡和功耗仍缺。

## 首次/驻留原生计时入口已做协议验证

- 已验证原生v1源码/binary/报告归档 `results/source_snapshots/native_region_verified_20261023_v1/manifest.json`，9份原物/快照哈希一致，原路径未改。
- 新独立源码 `src/native/netlist_runtime.cpp` / binary `build/native_runtime_20261023_v1`，在同一Graph/行缓存下运行首次与驻留两批，每批重置netlist route_batch占用/history，分别统计计数差、route_ms、VmHWM，并单列输出序列化时间export_ms。两批保留相同完整轨迹；fixture预处理仍在进程外，不能漏记。
- `results/native_runtime_protocol_20261023_v1.json`：CSR/direct、compact/direct、compact/expanded，真实第一查询两批所有语义一致；direct首次248miss/0hit，驻留0miss/248hit。只是协议验证，不是完整1062网或统计收益。
- 下一步用完整1062查询验证两批与冻结Python语义，再运行固定随机顺序、cache0/64/4096、7重复的同策略统计，准备、首次/驻留、导出及进程外fixture成本分开计。不得修改已归档集成源冒充同一版本。
- Python站点全网1396247第三轮完成：21规范节点冲突、0site冲突、0未完成，前两轮866/205；仍运行后续轮次，冻结依赖不改。

## 最新：原生两模式真实全查询核验完成

- 原owner3164210 / session67277及compact child3234729均已退出0；`execution_complete.json`为await_independent_semantic_validation，随后独立 `results/native_region_check_20261023_v1.json`已通过。不要把下方历史PID当运行状态或竞争重跑。
- 双方1062网、4轮、17336 PIP、16836次连接，完整最终树/每轮冲突、unknown、history、全部保留Python搜索计数一致；native输出边属性属于各自AGR。Python未保存的逐连接路径只校验native图内合法/连续，不能声称参考路径相等。
- 单批CSR169977.210ms、compact378897.845ms，后者2.229倍；cache hit6648887/miss147344725均相同。仅单次规范节点工作负载，保留完整native轨迹；准备fixture/父进程和统计/驻留比较未计全，不作跨语言或全物理端到端加速结论。
- 结果校验拒绝篡改回执哈希且不发布报告，证据 `results/native_verifier_rejection_20261023_v1.json`。
- 后续正式统计/站点扩展前保存冻结原生源码与binary快照，不能改旧来源使已验证报告不可复核。站点Python原进程1396247仍需核查；下一步保留全部1062网补齐站点模型、全物理验证与公平统计。实卡DDR/HBM/功耗仍缺。

## 原生CSR真实全查询核验通过，compact仍运行

- 原owner3164210 / session67277已完成CSR，4轮1062网routed；`results/native_region_csr_check_20261023_v1.json`独立校验通过，最终完整树/每轮冲突/历史/连接代价与全部保留计数均与冻结Python一致。`scripts/check_native_routing.py`还检查输出边和属性确属对应AGR。
- 原Pythonfull_trace=False未保存逐连接参考路径，因此只比较其长度、未知数与全部保留计数；native连接路径做图内合法/连续检查，不冒称逐连接参考路径相等。
- compact child PID3234729正在运行同一原生队列，日志 `data/derived/native_region_routing_20261023_v1/compact.log`。继续冻结原生4源文件、binary及runner。终态后运行同verifier两模式输出新报告，勿覆盖CSR报告。
- 轨迹范围：native保留每条连接的路径和unknown ID列表，原Python full_trace=False只留计数；两种native模式一致，但不能直接作跨语言内存收益比较。后续正式统计须对齐轨迹策略并单列准备/首次/驻留与导出成本。
- 单次native计时不含预生成fixture成本，RSS为native child，不含Python调度/审核父进程；并发主机噪声存在。当前不能做统计性能或跨语言端到端加速结论，仍不含站点配置状态。

## 当前原生完整查询实验正在运行（禁止修改冻结原生依赖）

- owner PID3164210 / exec session67277，日志 `results/native_region_routing_20261023_v1.log`，输出 `data/derived/native_region_routing_20261023_v1`。CSR child首次PID3164211；先查真实进程/receipt，不竞争重跑。完成CSR后原owner自动运行compact。
- `scripts/native_routing_experiment.py`已绑定plan code_and_binary；冻结 `src/native/{packed_graph.hpp,netlist_connect.hpp,netlist_routes.hpp,netlist_bench.cpp}`、binary及runner，不在运行期间改动。真实模式fixture与两镜像/输入哈希已核对。
- `RoutingGraph`显式按Python的(dst,pip,direction,src_wire,dst_wire)排序；完整1062查询、相同4096行缓存/80轮/200000预算/cap8，输出完整numeric边、各轮冲突/连接路径/计数/history。两模式字符串与属性池不同，各用对应fixture。
- 当前是规范节点模型真实全查询集成，不含站点配置标签，也不是统计性能报告。终态后必须逐项与原Python独立域csr_routes.json比较最终树/全轮状态和计数，并正确解码模式各自ID；通过后再谈测量范围。
- 原Python站点全网1396247独立继续，第三轮已开始50网。不要修改其冻结Python依赖。

## 原生真实输入准备完成

- `scripts/prepare_native_routing.py --mode csr|compact`绑定独立域audit/config/capture/queries及两AGR哈希，按各自真实字符串/属性编号生成完整1062查询与保护/排除属性fixture。
- `data/derived/native_region_{csr,compact}_inputs_20261023_v2`均完成，manifest与输出哈希复核；274732规范节点的词法顺序摘要及1062数值查询一致。两个表示池编号不同，必须用各自routing.txt；不能跨模式复用PIP/属性编号。v1错误共享池假设已拒绝，无部分输出，日志保留。
- 下一步实现真实Graph原生CLI，邻接排序显式对齐Python(dst,pip,direction,src_wire,dst_wire)，再运行全量规范多网对照；站点配置标签仍未接原生，不应宣称完整物理模型或性能完成。Python全网1396247保持运行。

## 原生多网协商组件已验证

- `src/native/netlist_routes.hpp`复用原生多源搜索：旧树占用释放/重建、sink排序、保留端点独占、冲突历史和present上限、预算/未知/不完整终止均实现；回调仍需接实际PIP保护和属性。仅规范节点协商，未实现站点配置状态。
- `tests/test_native_routes.py`与Python逐轮对照：最终节点/PIP路径、每轮冲突、未完成网、未知源、history及连接代价/计数；收敛、迭代耗尽、搜索耗尽、未知边界、cap1共5项通过，日志 `results/regression_native_routes_20261023_v2.log`，无编译警告。
- 下一步绑定真实packed节点名称顺序、query/protection/属性映射和完整序列化，再做独立区域全量对照；不能把合成差分测试称真实全网或性能验证。运行中的Python全网1396247依赖未修改。

## 原生多源代价搜索组件已验证

- `src/native/netlist_connect.hpp`复用共享Graph边格式，实现多源Dijkstra、保护/保留资源过滤回调、正整数代价、完整边回溯，以及unknown/no_path/budget区别。节点ID必须保持参考规范名称排序，属性/保护及占用历史代价由调用者提供，不能漏接。
- `tests/test_native_connect.py`通过编译驱动对照Python `netlist_routing.connect`，5项/10种条件逐项比较路径PIP、代价、expanded/examined/fetched/blocked与unknown。日志 `results/regression_native_connect_20261023_v2.log`，零编译警告。
- 仍只是搜索组件，尚未接真实packed图全网、迭代协商或站点配置标签；不能称完整原生router或性能验证。下一步实现真实输入映射与多网驱动，再做完整对照。

## 原生完整路由后端准备

- 已将原C++ Graph读取/译码/cache实现原样提取到 `src/native/packed_graph.hpp`，旧 `packed_bench.cpp` include复用；`scripts/packed_experiment.py`产物来源哈希增加该header。未改运行中站点Python代码。
- 原生/二进制9项回归通过，`results/regression_native_graph_extraction_20261023_v1.log`；含全部边、路径、终止状态和缓存检查。当前可执行仍只有有界BFS，不能宣称原生完整router已实现。
- 下一步使用共享Graph接入多源带代价搜索、真实多网占用/保护与协商及站点需求，再做完整路径与计时对照；保留同一译码器避免两个实现漂移。

## 最新单网物理验证通过（仅接口覆盖，全网尚未完成）

- 范围审计 `results/site_g37_physical_scope_20261023_v1.json`：该新路径site_demands三类均为空，未实际使用站点穿越；物理成功只验证新准备/回写接口，不能证明新站点约束被执行。
- `data/netlist/site_g37_applied_20261023_v1/{readback_check,quality_check}.json`：g[37] 14PIP精确读回，1833单元放置/全部连接不变，2637受保护网组资源/状态不变；1277可布线网全完成、0路由错误、DRC仅原HDOOC-4、内部WNS6.530/WHS0.020不变。不能作为全1062网通过的证据。
- 新A MCP会话 `vivado-20261023-072116-f6c0019b` PID2607458，Vivado2022.2 Tcl无GUI，maxThreads1，LD_PRELOAD libudev；当前载入上述单网候选。需任何后续操作先list_sessions核实，保持B会话不动。全网回写前恢复原baseline。
- 完整区域站点路由PID1396247仍在运行，不修改冻结依赖。

## 站点候选准备接口已验证

- 新入口 `scripts/prepare_site_routes.py EXPERIMENT --output NEW.tsv` 不修改运行中的site runner；校验plan冻结代码/输入、base配置/capture/queries与全部探针证据，再从真实路径重算规范和站点需求。仅routed且独立验证通过才发布；部分14实例范围与物理验证要求写入meta。
- 真实g[37]生成 `data/derived/site_routing_probe_g37_20261023_v1/candidate_routes.tsv`：1网14PIP，SHA256 7bb264dbaaa346bd3e22816193884d0d185f269d73ded9a1e32eeb3f3eba9292。未完成批次拒绝且不产生输出的负检查通过。尚未做该候选的Vivado读回。
- 全网原进程1396247继续运行；结束后使用同入口准备全网候选，不能把单网通过当全网完成。下一步可在独立baseline副本上验证g[37]物理读回，同时保持全网运行依赖冻结。

## 最新完成：128MiB 独立区域 HLS（2026-10-23）

- 原队列1525674已发布complete，两种模式synth/cosim/impl均退出0且完成标记齐全。独立报告 `results/hls_region_check_20261023_v1.json` 已生成并退出0；勿重跑或覆盖原产物。下方“仍运行/实现中”属于历史状态。
- 双方完整Csim覆盖9批、274732节点请求、1100754边记录，53759域外未知请求显式返回未知；采样RTL匹配8请求/664记录并含容量/错模式探针。
- CSR/compact实现分别5763/11307 LUT、8540/14283 FF、33/33 BRAM；5ns目标内部WNS0.908/0.524ns，WHS0.009/0.034ns；DRC均0，12564/22217可布线网分别全部完成。外部612输入/279输出未约束。
- 匹配采样周期20820/4682265，compact为CSR的224.89倍。保留负结果，不称加速；OOC和AXI模型不代表实卡DDR/HBM或完整router。
- 站点全网路由1396247仍须实时核查；第二轮已处理50网，首轮866规范节点冲突。冻结代码与14实例部分语义范围仍适用。

## 最新运行检查点：128MiB 区域 HLS（2026-10-23）

- fixture 已完整生成，不能再重启生成器。队列 PID1525674 / session60495 仍运行，状态 `results/hls_region_pipeline_20261023_v1.json`；冻结代码规则继续有效。
- CSR 已完成完整 Csim、采样 RTL 联合仿真和 OOC 实现，证据 `results/hls_region_csr_check_20261023_v1.json`：5763 LUT、8540 FF、33 BRAM，内部 WNS 0.908ns、WHS 0.009ns、DRC 0、12564/12564 可布线网完成。外部612输入/279输出未约束，不是板级验证。
- compact 完整 Csim 与3案例 RTL 联合仿真通过；matched 案例8请求/664记录，另含容量和模式错误探针。当前 impl 子进程2093805，须重新核查实际状态，不竞争重跑。完成后运行 `scripts/hls_fixed_report.py --kind region` 独立汇总。
- 全查询站点路由 PID1396247 / session69275 仍运行，首轮全部1062网完成：866规范节点冲突、0站点冲突、0未完成。后续轮次尚无最终结论，不改其冻结代码与输入。
- 原64MiB容量拒绝证据仍保留；128MiB只扩接口与完整输入验证，不代表DDR/HBM或实卡端到端完成。

## 当前运行：站点模型全1062查询集成（2026-10-23）

- `scripts/site_routing_experiment.py` 真实区域单网g[37]已完成：`data/derived/site_routing_probe_g37_20261023_v1`，14 PIP/一轮，独立规范及站点检查通过；不是全目标完成。
- 已启动全1062冻结查询，worker PID1396247 / exec session69275，日志 `results/site_routing_all_known_instances_20261023_v1.log`，输出 `data/derived/site_routing_all_known_instances_20261023_v1`。先核实进程，勿竞争重跑或修改plan冻结的脚本/src。原始完整区域图不变；只使用14个实际验证LUT实例需求，其他伪PIP保持未知而非无约束。这是明确部分语义覆盖的全查询集成，不能冒充完整站点模型实验。
- 新驱动 `src/site_netlist_routing.py` 协商规范节点/站点输出/配置位/分类配置冲突，独立验证从真实路径重算需求。最近完整99项回归通过 `results/regression_20261023_site_router_v1.log`；之后新增的runner已运行真实g[37]。
- `fixed_site_state_v2.json` 1099功能LUT按真实常量输入限制可达INIT位，合法基线共享自洽；153无单元常量配置单列，不全部假设逻辑固定。当前仅加入G6已复现默认冲突。`site_constant_coverage_v1.json`：功能61冲突+默认53冲突+动态资源可回顾覆盖全部84 DRC站点，无额外站点，14成功探针保留；不是独立验证。
- RapidWright单纯往返baseline通过1833单元LOC/BEL与1277全路由/零错误。显式内部穿越v1因不存在逻辑实例导致7单元失去放置；v2改关联后放置保持但仍PDIL-1/CONFLICTS，`data/netlist/explicit_site_probe_20261023_v2/verification.json`。不能把原理性内部route-thru API调用当修复成功。
- `clock_route_probe_20261023_v2`已保存DCP/可读EDIF，cx_q[6] ROUTED；RapidWright SiteInst导出漏掉3个隐式clock站点，覆盖缺口已记录。`cell_pin_ownership.tsv`导出11516逻辑/物理引脚，G6对应CARRY S6/S7逻辑未连接，需区分功能需求与工具默认编程。

## 最新站点语义修复检查点（优先于下方会话状态）

- A MCP `vivado-20261022-165536-938cabaa` 已在全网诊断崩溃，不再可用。多线程CheckNetlistWorker段错误复现2次；单线程本机Vivado完成 `data/netlist/region_all_diagnostic_20261023_v3`。全部1062候选节点/PIP回写精确，但最终755候选网未ROUTED、84个PDIL-1非法站点、908受保护网组状态改变；完整目标仍active。B会话勿操作。
- 站点模型核心 `src/site_resources.py`（输出独占与配置位共享分开）、`src/lut_equation.py`；配置状态搜索 `src/site_search.py` 不按节点合并不同配置标签。真实多网集成尚未完成。搜索拒绝直接消费带status/未完成需求的诊断记录，`verified_requirements`必须逐实例匹配证据payload；未知伪PIP保持未知，不当成无约束。
- 实测探针：`data/netlist/lut_route_probes_20261023_v{1,2}/verification.json`，5网14项LUT方程/12类输入输出、7项OUTMUX:D6通过。LUT站点PIP的IS_USED在这些合法穿越中全为0，不能作为唯一判据。`clock_route_probe_20261023_v1`证明cx_q[6]的3处CE_INT穿越合法，CE_TYPE=ASYNC/DELAY=VAL0；常量输入/极性仍需完整建模。
- 已有需求表 `data/derived/region_all_nets_cap8_20261022_v1/site_requirements_v2.json` 只作部分诊断，不能整体视作已验证规则，v1已由v2更正时钟族探针范围表述。原图全部42970伪PIP保留。
- RapidWright2025.2.1已复制到A的 `data/raw/rapidwright_2025.2.1`，使用Vivado附带Java11。只读Java适配器在adapters；读取 `build/site_ownership/checkpoint/routed.dcp` 工作副本及自动生成可读EDIF。`baseline_site_ownership.tsv`：203站点13963导线57102 BEL引脚，manifest已存。原冲突G6LUT归属缺失，有GLOBAL_USEDNET占位，跨工具归属尚需校验。首次失败自动创建原baseline旁routed.dcp.edf目录，原DCP/快照未改。
- `route_thru_availability.tsv` 使用成熟RouteThruHelper：30994可用11976不可用，但已知G6冲突也报可用，不能独立作为合法性oracle。时钟端点映射 `clock_leaf_mapping.json` 覆盖全部1280 RCLK伪PIP和候选35项。
- 最近完整回归81项通过（加入site_search前），`results/regression_20261023_site_resources_v1.log`；site_search目前6项单独通过。下一步补齐固定内部归属/动态多网需求、完整搜索集成及新的全量物理验证，保留既有失败与负性能结果。

## 最新：独立域软件等价完成，物理回写失败待修复（2026-10-23）

- 原队列2113276/worker3090103已退出0，不再运行。`data/derived/region_all_nets_cap8_20261022_v1/report.json`：全部1062网、17336 PIP，双方4轮零规范节点/PIP冲突，完整JSON除wall_ms外直接相等，7份产物哈希复核通过。单批Python时间不是统计性能结论。
- `scripts/prepare_netlist_routes.py --config configs/region_u280_v1.json` 已绑定本次配置/capture/快照/查询/路由哈希并独立验证全树；candidate_routes.tsv已生成。不要覆盖旧实验或删除失败证据。
- A会话回写在cg_q[2]停止，ROUTE_STATUS=CONFLICTS，节点/PIP精确读回但物理不合法。证据 `data/netlist/region_cap8_applied_20261023_v1/{failure_snapshot.tsv,cg2_route_status.rpt,failure_drc.rpt,root_cause.json,site_transition_v2.tsv}`。PDIL-1：SLICE_X22Y411/G6LUT穿越G5到GMUX要求O6=A5，却与GLOBAL_LOGIC0的OUTMUXG/D6及常量方程冲突。原基线及unroute后O6=0，应用cg_q[2]时变为O6=1。无单元占用不代表BEL未编程；不能把所有伪PIP删除作为精确模型修复。
- 原基线区域BEL配置已导出 `data/raw/region_u280_20261022_v1/bel_config.tsv` 及manifest，16776 BEL、78751项配置、99个无单元占用但常量编程的LUT。下一步补站点/BEL配置需求及内部常量路由归属，保留全资源图，再做全量搜索与物理验证。
- A MCP `vivado-20261022-165536-938cabaa` 当前已重新加载原baseline（BEL导出脚本），使用前仍list_sessions；B的全部会话勿操作。以下运行中描述均为历史。

## 最新：独立区域已合并，完整路由运行中

- 2026-10-23：8个分片全部退出0并通过分片校验；原owner完成严格合并，`data/raw/region_u280_20261022_v1/capture.json` 已发布。220,973 roots、274,732 nodes、1,028,572 aliases、1,099,762 PIPs、1,100,754 directed edges，训练源重叠0。region.tsv SHA256 `8a30d3357811c528b113e7f66bd6bac48c962e4a61e5e85f1cc663ba58c42575`。下面采集中描述为历史。
- 原队列PID2113276已自动启动完整1062网路由，child PID3090103；状态 `results/region_routing_pipeline_20261022_v1.json`，日志 `results/region_all_nets_cap8_20261022_v1.log`。先核实真实进程；不要竞争重跑或修改冻结代码。输出目录已出现queries/reference_availability，但report尚未发布，不能据此宣称路由成功。

## 此前准备与历史记录

- `scripts/netlist_cmodel_check.py --config ...` 现可从源实验绑定配置/capture解析独立域，核对查询/快照/图镜像和fixture哈希；整图超过冻结核容量明确报错，禁止截断。当前完整64MiB核未修改。通用入口实测通过 `data/derived/netlist_cmodel_generalized16_20261022_v1/report.json`：16网两模式路径/状态/计数均与软件CSR相同；这仍用原参考域，独立域C模型待采集/路由/新fixture完成。

- 已启动**唯一后续队列 PID2113276 / exec session36724**，状态 `results/region_routing_pipeline_20261022_v1.json`，冻结命令/代码哈希 `.plan.json`。等待原采集owner1959703完成严格合并后，运行全部1,062网（80轮上限、present_cap8、200000扩展/搜索、双方4096行LRU），输出 `data/derived/region_all_nets_cap8_20261022_v1`；失败停止，不自动修改图/删查询/重启。不要手动竞争同名输出或修改冻结代码。
- `scripts/netlist_runtime_benchmark.py` 提供独立进程、固定CPU、各轮seed随机条件顺序、相同有界LRU、准备/首轮/驻留时间、VmHWM/VmRSS和完整结果验证。支持csr/direct/prepared/expanded、多个容量，默认7次；仍是Python/全审计图驻留，非native/实卡性能。
- 测量流程验证 `data/derived/netlist_runtime_validation_20261022_v1/report.json` 已完成：16网、csr/prepared、64行、各2次，4个新进程的首轮/驻留均与已审计结果一致。模板准备与路由更慢/内存更大；并行采集造成主机干扰且重复仅2次，不作最终性能推断。新实验设计3项测试通过，完整回归日志 `results/regression_20261022_runtime_v1.log`（先确认末尾OK）。

- 后续代码已接入：`scripts/netlist_experiment.py --config configs/region_u280_v1.json` 在 capture 完成后读取独立 region.tsv，验证原冻结 bank/training 哈希和源不重叠；参考路径仅作域内可用性诊断，不要求重现、不补行、不删查询。尚未对完整独立域执行。
- `--row-cache-capacity N` 对CSR与prepared模板使用同一有界LRU（0禁用）；原默认策略保留复现。统计行/边数，不能替代进程内存/统计性能。代码 `src/row_cache.py`。69项全回归通过，`results/regression_20261022_domain_cache_v1.log`。
- 16网共同64行缓存集成已完成（exec session98971退出0）：日志 `results/netlist_shared_cache16_20261022_v1.log`，结果 `data/derived/netlist_shared_cache16_20261022_v1/report.json`。这个验证使用旧参考域，不能替代独立域实验或统计性能对照。

- 规则冻结于 `configs/region_u280_v1.json`：固定端点 tile 矩形外扩2行/列，960 tiles、220,973个规范源；不使用参考路径选择资源。训练源重叠0，全部查询端点在域内，原参考路径有5个源在域外，禁止据此补入参考行或改选择框。
- 24行 pilot 全属性/别名/有向边/oracle 等价；新增4项严格合并测试通过。计划、分区、代码哈希在 `data/raw/region_u280_20261022_v1/{execution_plan,orchestration_receipt}.json`。
- **单一采集 owner PID1959703，exec session90514**；状态 `results/region_u280_capture_20261022_v1.json`，8个独立只读Vivado2022.2进程各1线程。先核实真实进程，不要重启或手动竞争 finalize。全部分片通过后自动合并为 region.tsv/capture.json；当前尚未完成。
- 合并拒绝重复源、共享属性冲突和缺失源；未知域外行仍未知。下一步将独立 capture 接入同一全部1,062网实验并建立公平缓存/运行时对照，不能用旧参考域成功代替。
- A MCP此前已恢复原baseline routed.dcp；B会话勿操作。此前第四轮队列均完成，下面历史PID不再运行。

- 本目录研究：资源图压缩与直接执行。研究问题：压缩资源图能否在保持规范节点、边和资源属性一致的前提下，降低真实搜索的访问成本或扩大可处理规模？
- 优先阅读 README.md、EXPERIMENTS.md、INTERFACES.md、NEXT_STEPS.md。原始论文与公共参考源码位于上级目录，路径已列出。
- 已完成 Python CPU 合成样例及 Vivado 2022.2 xcvu13p 真实采样语义验证：534 个完整源节点、5,005 个规范节点、4,886 条有向边。真实布线性能基线、GPU 与 FPGA 实现尚未完成。不要将逻辑计数、JSON 大小或验证时间解释为压缩率/实测加速。
- 用户要求吸纳其他场景的成熟方法以提高可实现性；不能仅因方法已有基础就排除创新可能，也不能未经比较宣称新颖或保证收益。
- 第二轮已完成冻结模板留出：SLR0 384 个源节点拟合 110 个模板，SLR1–3 828 个源节点中 478 个无需例外，350 个需例外，补齐全部等价。四跳搜索域 229 个源节点/875 个节点/1,076 条边，186 个源节点未见模板类型需显式回退。16 个查询的 CSR/原始译码/预处理译码路径、状态和轨迹一致，26 项测试通过。
- 优先阅读 results/README.md、configs/region_query.json、adapters/README.md。命令：`python3 scripts/run.py region-check`、`python3 -m unittest discover -s tests -v`。首轮仍可 `real-check`。下一步按独立训练搜索轨迹改善模板覆盖，固定新的未见评估区，并做紧凑布局/完整成本对照，不要重复首轮导出作为新进展。
- 第二轮 CPU 微基准测得：12 查询批次中位 CSR 0.625 ms、原始译码 20.956 ms、预处理译码 2.891 ms；预处理初始化 10.759 ms 单独计入。仅为同进程驻留 Python 单位跳数 BFS，查询由真实器件构造，不是网表路由性能，更不是硬件加速。
- 仅 roots 的邻接已知。四跳域展开深度 0–3，深度 4 是明确未展开边界，不能当 sink。节点/别名/属性表仍显式保存。首轮同样本拟合，第二轮冻结训练模板但例外/回退仍读取留出真值。未验证真实网表保护/占用、时序、excluded PIP、全器件搜索及硬件。
- 原始参考源码保留在 `../_shared/assets/gpu_router_original/` 和 `../FPGA-Routing-main/`。本方案改写与适配放在本目录，避免无意改变其他方案的基线。若需公共改动，说明影响并运行受影响目录的检查。
- 沿用上级 AGENTS.md 的 FPGA/AMD 工具规则：按任务选择并阅读 Ross Skill；纯算法/代码/文稿任务无需启动 Vivado。实际 Vivado 操作优先检查并使用现有 MCP 会话，默认 Tcl 无 GUI；默认版本 2022.2，先核实新功能支持。
- 在已有授权内自主推进，不把实验阶段或文档中的待办项当作额外审批要求。

本方向重点语义：

- 不同物理资源即使模板相同，也必须拥有独立的动态占用。
- 跨 tile 的同一物理导线必须映射到同一规范节点；不要只按坐标合并节点。
- 保持并行边、开关方向、属性和特殊资源语义；不能只比较边数。

## 当前持续目标与第三轮检查点

- 当前持续目标是“实现完整实验”，状态与完成条件在 `EXPERIMENT_STATUS.json`；不要把阶段微基准标为完整目标完成。
- 第三轮已完成独立搜索训练、AGRAPH01 与同一 C++ BFS：优先读 `PACKED_FORMAT.md`、`results/packed_check_20261022_v2.json`。训练 3,831 行，评估 2,866 行/10,274 节点/12,824 边；回退 2,442 -> 3 行；总文件仅缩小 2.09%，直接译码仍慢于 CSR。35 项回归通过。
- 入口 `python3 scripts/run.py packed-check` 需 Linux/g++。v1 的 getrusage 峰值继承父进程，应读 v2 的 VmHWM。缓存未证明稳定性能优势。已有数据/报告独占创建，不覆盖。
- 正在接入真实放置网表：原样引用 RouterAcc 的 `cost_calculator.v` 与 `dly_cell.v`，本目录 `workloads/routeracc_cost_registered.v` 添加寄存器包装，只作为路由工作负载，不能称为压缩加速器。
- VU13P 综合在 Common 17-345 因缺少 Synthesis 许可失败；U280 在 Vivado 2022.2 Standard 中受支持且已成功综合。独立数据目录 `data/netlist/routeracc_cost_u280_20261022_v1`，不得与 VU13P 器件样本混合。
- 原 MCP 会话 `vivado-20261022-161303-3b8091da` 已丢失且进程退出；不能继续用该 ID。已启动本机 Tcl `adapters/resume_netlist_u280.tcl` 从 placed.dcp 恢复，检查完成标记/产物再进行后续操作，不重复运行覆盖输出。
- 实卡：XRT 2.14.354 枚举 0 设备，U280 xpfm 未发现；证据 `results/environment_goal_20261022.json`。用户已收到许可证来源说明，尚未提供授权/板卡地址。仍有软件/仿真工作可推进，不应仅因此将完整目标标 blocked。

- U280 恢复已完成（不再运行中）：`data/netlist/routeracc_cost_u280_20261022_v1/capture.json` 含所有哈希/命令。1,833 原语、1,277 可布线网完整、0 路由错误，已保存 routed.dcp。内部 WNS 6.530 ns/WHS 0.020 ns，但外部 IO 未约束。
- 两次原 Vivado 退出实际是 WebTalk 主机信息采集调用 libudev 时的 realloc 崩溃；`config_webtalk -info` 已关闭仍发生。仅对新进程预加载 `/lib/x86_64-linux-gnu/libudev.so.1` 后同一 placed.dcp 恢复成功；这是本地验证过的兼容性处理，未修改系统/安装库或许可证逻辑。后续工具进程可使用相同 env 前缀并记录；MCP 会话已不存在，需先查询会话再决定本机 Tcl fallback。

## 第四轮进行中（后续状态优先于上面历史描述）

- 已新建 MCP `vivado-20261022-165536-938cabaa` 并加载 U280 routed.dcp。使用前仍须 list_sessions。长邻接导出在独立 batch，不要重复启动或覆盖：`adapters/export_netlist_domain.tcl`，日志 `results/vivado/export_netlist_domain_20261022.stdout`，原 PID 2173511。需等 `NETLIST_DOMAIN_COMPLETE` 后运行 `python3 scripts/finalize_netlist_capture.py`。
- 快照 `data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv` 按物理网层次组聚合：2,638 组、1,833 原语。1,062 条可重布 SIGNAL 网、4,209 规范 sink；共享常量节点只属于同类常量网，其他资源受保护。仅完全一致的重复 site-pin 记录去重。
- 使用 `configs/netlist_u280_v2.json`，v1 的 VU13P LAGUNA seed 名在 U280 不存在，已在读取邻接前修正。训练完成并冻结：3,761 roots、14,559 nodes、18,043 edges、440 templates，SLR0；`data/derived/netlist_u280_bank_20261022_v1/manifest.json`。评估为 18,243 个参考路由源的完整邻接，仍在导出。该域有参考路径条件，不能称独立全器件路由性能。
- 新路由器 `src/netlist_routing.py` 使用规范节点占用、保护所有非选中网与所有端点、多端点树和协商拥塞。未知邻接记录并跳过该分支，不能当 sink；失败状态保留。10 项路由回归通过；此前全套 44 项通过，后来新增端点保护项，合计目前 45 项（新增模块已单独复测）。
- 新入口 `python3 scripts/run.py netlist-check` 等 capture.json 完成后运行；默认全 1,062 条网，可 `--max-nets 16` 先小范围集成。默认模板使用惰性行缓存，额外展开内存必须计入；不能冒充纯压缩性能。`scripts/prepare_netlist_routes.py`、`adapters/apply_netlist_routes.tcl`、`scripts/check_netlist_readback.py` 已编写，尚未用候选路由验证。
- 硬件见 `hardware/hls/README.md`。同一 mode 核直接执行 AGRAPH01 CSR/模板，Csim 与 csynth 已通过；v2 六批 XSim cosim 通过，impl 已完成，日志 `results/hls_impl_20261022_v2.log`。v3 真实并行 PIP 和各表示相同规范请求的五批 cosim 也已通过，日志 `results/hls_cosim_20261022_v3.log`。v2/v3 核源码相同，测试负载不同，保留所有原产物。
- HLS 2022.2 不接受 open_project 的绝对路径名，脚本通过 cd 到父目录再打开 basename；v1 失败日志保留。现代 skill 的 vitis-run 路径不适用，本机 classic Tcl 已验证。综合估计 36,570 LUT/16 BRAM18K，多个自动流水线 II 未满足，尚无吞吐优势结论。AXI 仿真不是实卡 DDR/HBM。

- 第四轮 HLS 最终报告 `results/hls_check_20261022_v2.json`：OOC 12,179 LUT/14,932 FF/33 BRAM18K，5 ns 目标下 WNS 0.531 ns/WHS 0.024 ns，DRC 0，23,689 条网全部布线；612 输入/279 输出未约束外部延迟。CSR/模板相同请求周期比为模板慢 36.70/36.53/82.72 倍。不是实卡性能或完整 FPGA router。
- 已用 Ross `hls-ii-diagnose` 读取原始 scheduling 报告，证据在 `results/hls_ii_diagnosis_20261022_v1.json`：映射二分查询的 70-stage AXI readreq 使 II=74，排序 BRAM 端口受限使 II=11；未修改当前核，保留负结果基线。
- 原 RouterAcc OOC 网表 baseline DRC 有 1 条 HDOOC-4（clock_buffer 无 LOC），见 `results/netlist_baseline_drc_20261022.rpt`。这不同于 HLS 核 DRC=0，不要混淆两种设计的报告。

## 第四轮回写预检与单一后续队列

- 已实际验证 16 条原参考树的 canonical FIXED_ROUTE：990 PIP 精确回写、2,622 个未选中物理网组和全部 1,833 单元 LOC/BEL 不变；WNS/WHS 和 DRC 均与 baseline 相同。产物 `data/netlist/preflight_applied_20261022_v1`，清单 `data/derived/netlist_preflight_20261022_v1/manifest.json`。这是原路径接口预检，尚非新搜索路径的回写。层次 PIP 重复记录 996 条，只合并完全相同项。
- `scripts/check_netlist_readback.py` 修复了未知候选网名可能漏报的问题，6 个故障注入通过。`scripts/check_netlist_quality.py` 比较全部路由完成率、DRC 增量、时序与约束覆盖，5 个质量门禁故障测试通过。
- MCP 已通过 close_design/open_checkpoint 恢复原 baseline routed.dcp，16 条预检网的 fixed 标志不留在当前加载设计中；原 baseline 文件未修改。
- **单一队列已启动，不要手动竞争 finalize/netlist-check。** `scripts/netlist_pipeline.py` PID 3431763（exec session 62824），锁 `results/netlist_pipeline_20261022_v1.lock`，状态 `results/netlist_pipeline_20261022_v1.json`。它等待原 exporter PID 2173511 结束，随后依次 finalize、16 网比较、全 1,062 网比较。每步失败即停止并保存日志，不恢复/重启原导出。观察前先查真实进程。
- 队列输出固定新目录：`data/derived/netlist_integration16_20261022_v1`、`data/derived/netlist_all_nets_20261022_v1`。完成后由主会话分析并经 MCP 应用真实搜索候选；当前不会自动应用。若队列失败先读具体阶段日志，不另建竞争进程。
- 本环境未发现可选择 luna 的切换/委派接口，已向用户说明；继续用现有确定性等待链，不声称切换模型。

- 最新全量回归：`results/regression_20261022_preflight_v1.log`，56 项全部通过。

## 分离固定模式硬件流程（仍在执行）

- 为补齐面积对照，已从原核只替换模式判断/校验，生成独立 CSR/compact 核；原硬件文件、旧报告未修改。冻结源与清单 `data/derived/hls_fixed_modes_20261022_v1`，生成器 `hardware/hls/prepare_fixed_modes.py`，classic Tcl `hardware/hls/run_fixed.tcl`。不是新增吞吐架构或实卡后端。
- 两个版本的全量 Csim、csynth 与匹配请求 cosim 均已通过（含模式不匹配拒绝测试），impl 正在运行。CSR supervisor PID 3547765（exec session 49325），compact PID 3547998（exec session 99293）。每个由 `scripts/hls_fixed_pipeline.py` 依序完成各阶段，失败即保存状态并停止，禁止重复启动。状态 `results/hls_fixed_{csr,compact}_20261022_v1.json`，逐阶段日志同前缀。
- 综合估计 CSR 为 19,630 LUT/11,386 FF/16 BRAM18K，compact 为 35,328 LUT/19,173 FF/16 BRAM18K；等待布线后实际面积/时序，不用此估计替代最终资源。
- 两个状态均 completed 后可运行 `python3 scripts/hls_fixed_report.py --output results/hls_fixed_check_20261022_v1.json`，它检查匹配工作量、布线/时序、保留哈希。当前还不能生成完成报告。
- 原导出仍运行，最近实查 13,750/18,243 行。软件队列 PID 3431763 仍等待原 PID 2173511，勿手动竞争 finalize 或 netlist-check。

## 分离模式已完成；真实 U280 图验证仍等待数据

- `results/hls_fixed_check_20261022_v1.json` 是分离固定模式的最终报告。CSR 布线后 5,763 LUT/8,540 FF/33 BRAM18K；compact 11,307 LUT/14,283 FF/33 BRAM18K。200 MHz 约束下内部 WNS=0.908/0.524 ns，WHS=0.009/0.034 ns，DRC 均 0；外部 IO 仍未约束。两版本 AXI 数据端口宽度相同。
- 匹配批次周期：CSR 6,555 vs traversal 303,855、intent 302,393；并行 PIP 留出 CSR 8,007 vs compact 752,727。模板慢 46.35/46.13/94.01 倍。该结果来自 VU13P 图输入的通用 U280 核，不能当成真实 U280 网表的后端验证。两个 fixed supervisor 已完成，不要再启动。
- 真实 U280 图后端新队列 `scripts/hls_u280_pipeline.py`，PID 49613（exec session 33159）；状态 `results/hls_u280_pipeline_20261022_v1.json`。它等待已有 integration16/report.json，然后调用 `hardware/hls/prepare_u280_fixtures.py` 生成64 MiB声明容量的冻结源/输入，依次 Csim/csynth/cosim/impl（两模式独立并行），不重启软件链。完整节点按请求/输出上限分批，全已知行必须成功，禁止静默截断。
- 后续真实图产物 `data/derived/hls_u280_fixtures_20261022_v1`、`build/hls_u280_{csr,compact}_20261022_v1`、`results/hls_u280_{csr,compact}_20261022_v1.json`。两者完成后：`python3 scripts/hls_fixed_report.py --kind u280 --output results/hls_u280_check_20261022_v1.json`。当前数据未到，尚不可运行完成报告。
- 新 `src/hls_cmodel.py` 通过 ctypes 执行同一 HLS C++ 顶层，输出经完整 packed 属性/身份解析后接公共搜索接口。`data/derived/cmodel_check_20261022_v2/report.json`：两模式各2,866已知行/7,408未知行/12,824边及16个 BFS 路径/轨迹通过。v1 在测试起点选择上 StopIteration，保留失败日志；v2 使用采集元数据起点。所有执行均为本机 CPU C 模型，不能称 FPGA 实测。
- U280 software all_nets 报告和 hls_u280 冻结源到齐后，可运行 `python3 scripts/netlist_cmodel_check.py --output data/derived/netlist_cmodel_20261022_v1`，比较全部网的搜索树/占用/计数与软件 CSR，结果再经 Vivado 回写验证。该脚本已编写，尚未对真实 U280 图执行。
- 新鲜 XRT 核验仍为0设备：`results/xrt_recheck_20261022_v1.json`，`configs/platform.json` 现在明确记录版本/无卡及 OOC 验证范围。

## 第四轮已审计完成：以本段为最新状态

- 当前综合阶段报告 `results/netlist_stage_20261022_v1.json`，入口 `python3 scripts/run.py netlist-report --output results/NEW.json`。它重新比对4套完整路由结果、当前物理快照/约束/质量、原始输入哈希、硬件门禁和58项回归。`full_goal_complete=false`，完整目标仍 active。
- 原导出已终止并完整保存，**不再运行**：18,243 roots、51,596 nodes、131,721 aliases、83,931 PIPs、83,995有向边；SLR1来源，训练为SLR0 3,761行/440模板。`data/raw/netlist_u280_20261022_v1/capture.json` 已审计。原PID2173511/软件链PID3431763均已完成，不要重启或再次 finalize。
- 初次全1,062网20轮仍有2规范节点冲突，保留 `data/derived/netlist_all_nets_20261022_v1`。跟进发现历史代价被指数present压低，`present_cap=8,max_iterations=80` 在第22轮无冲突；同22轮原策略仍留同2冲突（`netlist_all_nets_exp22_20261022_v1`），不把失败改写为通过。新设置在 `netlist_experiment --present-cap`，报告保存route_settings和代码哈希。
- 完整通过结果 `data/derived/netlist_all_nets_cap8_20261022_v1`：1,062网/4,209唯一sink，17,120 PIP，CSR/惰性缓存模板的树、状态、迭代和计数一致。静态完整文件CSR10,883,328字节、compact10,323,904字节；缓存是额外展开的主机内存，Python单次时间不能当压缩收益。
- 全路径已实际写入Vivado并精确读回：`data/netlist/all_nets_cap8_applied_20261022_v1`。1,576保护组和所有1,833单元LOC/BEL/连接不变；1,277可布线网全部完成，0路由错误；DRC仅保留原HDOOC-4。内部WNS6.524ns（原6.530，下降.006）、WHS.020ns不变；168输入/175输出无IO延迟，不能称板级签核。A MCP目前加载的是此已保存候选，下一阶段取基线时先close_design/open_checkpoint原routed.dcp。
- 16网候选也通过于 `integration16_applied_20261022_v2`。v1目录来自一次输入准备尚未结束的失败读取（未改路径），保留该失败目录；后续务必等待exec子进程结束后再执行依赖操作。
- 真实U280图的两模式完整Csim（51,596请求/83,995边）、匹配RTL子集（9请求/37边+容量/模式错误）和OOC实现均通过。`results/hls_u280_check_20261022_v1.json`，64MiB声明容量，仍是外部AXI仿真/单核OOC。CSR5,763 LUT/8,540 FF，模板11,307 LUT/14,283 FF，两者33 BRAM18K；内部WNS.908/.524、DRC0，外部612/279端口无延迟。匹配周期4,920 vs189,675，模板慢38.55倍。HLS U280队列PID49613现已完成，勿重启。
- 精确HLS C++经ctypes运行于CPU，复用同一路由控制：`data/derived/netlist_cmodel_cap8_20261022_v1/report.json`，两模式全部1,062网路径/占用/计数与软件CSR一致。每模式13,016,703调用（其中8,737,854未知）、19,959,522返回记录；只是C模型集成，不能称FPGA执行/时延。
- `write_new` 已改为同文件系统临时文件写完后硬链接原子独占发布，避免下游看到半JSON；验证了工作目录真实文件系统，58项全回归通过：`results/regression_20261022_cap8_v1.log`。新源和旧失败源分别保留，原外部参考目录没修改。
- **下一阶段仍需独立搜索域、公平缓存/运行时统计对照与更大/独立工作负载，以及实卡DDR/HBM/板级IO/功耗/端到端。** 当前域由参考路径节点构造，不得当全器件或独立域性能。当前主机XRT仍0卡，无U280平台包；有软件工作可做，不能仅因此标目标complete/blocked。
