# CP布线恢复已验收，10ns时序尚未闭合（2026-10-30）

[完整物理恢复](results/checkpoint_edit_route_recovery_20261030.json)已完成独立DCP重开、203文件归档实际恢复复审，210份物理冻结文件及16份路径分析文件已核验。188481条可布线网全部完成，路由错误0；LUT139612、FF88186、BRAM163、DSP23，最终WNS **−4.059ns**、WHS0.007ns。外部IO延迟与时钟来源仍未完整指定，尚无时序闭合或板卡结论。

[实际最差路径](results/checkpoint_edit_route_recovery_timing_20261030.json)从directory lease状态到config_restore描述符写使能，48层逻辑、数据延迟13.956ns；其中一条扇出2369的网占2.275ns。[报告分类](results/checkpoint_edit_route_diagnostics_20261030.json)核对路后与重开报告逐项一致：DRC84项为37 Warning和47 Advisory，无报告Error；47项检查因端口过多未执行，不能视为全检查通过。TIMING-16/18仍有未解决记录。

CP[完整矩阵](results/checkpoint_edit_matrix_20261030.json)已 **8/8 完成实际恢复并冻结**，216份输出比较通过，217份冻结文件来源SHA核验通过。最后CRC/full的27输出/周期及133生产源已独立复核，旧队列正常退出。实时所有权与下一步见[NEXT_STEPS.md](NEXT_STEPS.md)。

[真实主机写入双运行](results/checkpoint_host_edit_system_20261030.json)已完成27份完整输出/事件/周期精确比较、实际恢复及433文件冻结核验。1次写入、238次原子检查，旧干净checkpoint被拒、合法脏checkpoint清除恢复等待；原trace前缀保留，其余25份输出不变。这补上了旧矩阵edit=0的定向覆盖缺口。

[原版通用七例](results/config_publication_probe_20261030.json)与[原生二十例](results/config_native_feedback_probe_20261030.json)已恢复冻结，分别138和689项检查。[原生反馈候选](hardware/variants/config_native_publication_v1/manifest.json)的[五模式单元比较](results/config_native_publication_units_20261030.json)及[扩展完整系统](results/config_native_publication_system_20261030.json)也已实际恢复冻结。完整系统27输出/周期与参考精确一致，4,829,223次完整状态/输出比较通过，205份冻结文件核验通过。[同条件OOC](results/config_native_publication_synth_launch_20261030.json)已启动，严格使用133生产源并排除观察器；尚无新的资源、WNS或物理收益结论。

以下保留历史。

# CP物理运行库故障已复现，恢复任务进行中（2026-10-30）

CP剩余七场景的[来源预检](results/checkpoint_edit_matrix_preflight_20261030.json)已通过，[唯一等待队列](results/checkpoint_edit_matrix_queue_launch_20261030.json)已启动。它等待当前物理恢复及主模型路后分析冻结，再按内存门槛串行运行；当前没有新编译/仿真，也没有新的八场景通过结论。第八项计划复用已恢复的CP CRC pressure。此矩阵仅针对CP，不能扩展为path/stage验证。

原CP完整物理任务在布线日志报告完成后因libudev/WebTalk路径中的realloc错误退出，尚未保存路后DCP，不能验收。[运行库对照](results/udev_runtime_recovery_20261030.json)已实际归档恢复并冻结：原版库预加载使小型真实Vivado例完成布线、保存和重开检查点，独立C对照也复现了分配器与深绑定交互故障。两库均未修改，不改变许可或全局设置；小例不是完整系统证明。

[完整系统恢复](results/checkpoint_edit_route_recovery_launch_20261030.json)已从同一保存布局启动，保留133生产源、原参数与10ns约束。新进程与唯一后续审计/归档/实际恢复/冻结链均已实际启动；当前尚无新的完整系统路后验收结果。原v1失败记录保留，实时句柄及不可重复启动要求见[NEXT_STEPS.md](NEXT_STEPS.md)。磁盘当前可写，项目余量约1.38TiB、/tmp约2.52TiB，非此次崩溃原因。

以下保留历史。

# 当前实验范围与证据（2026-10-29）

`query_native`十一源版本的八场景行为矩阵已完成，216份输出比较及归档实际恢复复审通过，见[矩阵结果](results/query_native_matrix_20261028.json)。后续CP、path、stage候选的测试范围分别记录，旧矩阵不能自动证明新候选也通过八场景。

| 候选 | LUT | FF | 10 ns下布局前WNS | 证据状态 |
| --- | ---: | ---: | ---: | --- |
| CP时序参考 | 139481 | 88048 | −4.948 ns | 独立检查、实际恢复、冻结完成 |
| path写入口候选 | 132021 | 87929 | −5.841 ns | 独立检查、实际恢复、冻结完成 |
| stage暂存写入口候选 | 131318 | 87983 | −5.614 ns | 独立检查、实际恢复、冻结完成 |

三者BRAM163、DSP23、URAM0。对应[CP结果](results/checkpoint_edit_synth_20261028.json)、[path结果](results/route_path_synth_20261028.json)、[stage结果](results/route_stage_synth_20261029.json)。Stage的179文件归档实际恢复后审计字节一致，167文件冻结逐SHA核验通过。[三者比较](results/route_stage_tradeoff_20261029.json)保留三个非支配点：CP布局前WNS最好、stage的LUT最少、path的FF最少，没有生产选择。Stage比CP减少8163 LUT及65 FF，但WNS差0.666ns；比path减少703 LUT、WNS改善0.227ns，同时多54 FF。所有WNS均为相同133生产源集合、U280、参数及10ns约束下的布局前估计，不能换算为板卡频率。

[Stage实际最差路径](results/route_stage_timing_path_20261029.json)从directory lease_phase到search_ctl/rsp_status[0]/D，共66级逻辑（64 LUT、MUXF7和MUXF8各一），数据延迟15.596ns=2.745ns逻辑+12.851ns未布局net估计。它与CP/path最差端点不同，不能当作同一路径因果证明。原LUT-only解析器未计MUX而断言失败，已保留[失败证据](results/route_stage_timing_parser_failure_20261029.json)；v2通过三份真实报告及三项损坏反例后完成分析，分析与比较共9文件冻结核验通过。

Stage候选的[十二单元例](results/route_stage_units_20261029.json)与[一个完整CRC压力例](results/route_stage_system_crc_20261029.json)已实际恢复并复审。完整例27份输出及48288200ns结束时间精确匹配，原path/CP/query/backend/capture观察保留；新增156字暂存银行参考覆盖10次capture、1248次import、1259次检查。完整系统184文件冻结核验通过。CP/path/stage的新完整八场景矩阵仍未完成。

整系统物理测量工具已准备，版本与预检失败边界见[工具准备记录](results/state_ooc_physical_tools_preparation_20261029.json)。原后续队列在路径解析失败时退出，尚未创建物理实验；修复后的[唯一v2队列](results/checkpoint_edit_physical_queue_v2_launch_20261029.json)已完成Stage分析与冻结，按内存门槛对既有CP参考进行整系统布局布线测量。物理源、Tcl、审计器、冻结器及约束均未改变，当前没有新整系统物理通过结论。已有[postprev与center模块物理结果](results/parent_physical_20261025.json)仅适用于该模块；平台I/O、物理时钟来源、板卡测量、固定价格之外的有效性等范围限制继续保留。实时阶段与任务所有权见[NEXT_STEPS.md](NEXT_STEPS.md)。

当前CP实际布线日志进一步确认[OOC端口约束缺口](results/checkpoint_edit_physical_ooc_port_observation_20261029.json)：Route35-198指出外部端口没有HD.PARTPIN_LOCS，Route35-197指出clk没有HD.CLK_SRC。即使后续可布线网络计数全部完成，也不能扩展为外部端口路由或平台时钟验证完成；消息被限次显示，出现次数不是受影响端口数。原研究约束保持，运行中的Intermediate Timing Summary不作最终路后结论。

另一个尚未实现的结构假设是缩小搜索READY选择范围。[源码绑定模型](results/search_ready_selection_20261029.json)覆盖4096个四值投影组合，支持保留现有通道掩码、仅让12个非搜索case的内部selected_ready保持默认零。完整reply选择与16路host接口不变；分析器和报告已冻结。此处只有Python模型，无候选RTL、功能回归或资源/时序收益，是否进入实验待当前CP物理测量后判断。

以下保留历史。

# 当前研究进度（2026-10-27）

十源合并版本完整匹配OOC及独立DCP检查确认零组合环（check_timing/LUTLP-1），已归档实际恢复复审并189文件冻结。资源139803LUT/88045FF/163BRAM/23DSP；10ns下WNS仍-7.111ns，物理时序尚未通过。见results/native_retirement_synth_20261027.json/.md及71级最差路径分析native_retirement_timing_path_20261027.json/.md。

完整CRC压力行为已通过，可计矩阵1/8。结构门槛通过后唯一串行队列已启动第一项off/full回归，目前仿真中；其余按队列逐例运行、审计、归档实际恢复和缓存释放，尚不能称8/8。队列所有权/进程及禁止重复启动要求见NEXT_STEPS.md。

以下保留历史。

# 当前研究进度（2026-10-27）

十源合并版本完整CRC压力回归已通过：27文件/48288200ns精确匹配，4828815周期backend与capture退休观测通过，379文件归档实际恢复复审一致，192文件冻结。见results/native_retirement_system_crc_20261027.json/.md。直接对原始CRC参考的133源/输入/oracle/27输出核对也通过，可计最终行为矩阵1/8。

同源综合仍运行，唯一结构后续链将自动独立重开DCP、审计、归档实际恢复与冻结；当前没有合并版本无环结论。其余七项回归等待同源零环结构门槛，尚未提交。实际句柄及入口见NEXT_STEPS.md，勿重复启动或读取正在恢复的根。

以下保留历史。

# 当前研究进度（2026-10-27）

原生backend互斥候选完整CRC压力回归通过：27文件/48288200ns精确匹配，4828815周期原生互斥观测、26 authority与32 owner请求回复通过；379文件归档实际恢复复审一致，184文件冻结。见results/recovery_backend_system_crc_20261027.json/.md。

添加capture零depth退休条件精简后的十源合并版本已进入完整仿真，匹配综合也仍运行；均无最终通过结论。原路由门控基线结构仍5环/-9.340ns。八项矩阵的全部原参考133生产源与10源候选预检完成，后续七例工具已准备但未提交；门槛为合并CRC恢复审计和同源无环结构恢复审计。实际链/进程及入口见NEXT_STEPS.md，勿重复启动。

以下保留历史。

# 当前研究进度（2026-10-27）

路由门控完整综合及独立DCP审计已归档实际恢复：5组合环、WNS -9.340ns，仍不通过硬件验收；见results/route_block_synth_20261027.json/.md。对剩余capture退休反馈，8192组源码绑定二态检查证明零depth已排除capture结果，独立候选仅删该冗余退休条件。与原生backend互斥候选合并后，native_retirement_synth_v1已启动；完整行为由唯一native_retirement_followup_v1链等待旧backend CRC完成并审计恢复后串行启动，详情及活进程见NEXT_STEPS.md。合并候选尚无完整通过结论；八项最终矩阵、物理时序和板卡收益仍待验证。

以下保留历史。

# 当前研究进度（2026-10-27）

路由门控版完整综合报告剩5组合环、WNS -9.340ns，仍不满足硬件验收；独立DCP诊断链正在运行，最终归档恢复待完成。最新原生backend互斥候选保留通用默认接口，九项coordinator测试及实际恢复审计通过；详见results/recovery_backend_native_20261027.json/.md。完整CRC压力V2已编译展开且仿真中，不能称完整通过；见NEXT_STEPS.md的实际进程/入口及禁止重复启动要求。新候选尚未完整综合，其余七项最终矩阵及物理时序/板卡结论仍缺。

以下保留历史。

# 路由门控完整CRC回归通过，NORMAL准入组件候选通过（2026-10-27）

详见results/route_block_system_crc_20261027.json/.md。route_block_system_crc_pressure_v1仅在已恢复五源combined基线上增加route controller idle_fault与adapter block_external两源变化，累计七源。完整27文件（12AXI/native事件与周期/最终DDR/恢复流）逐字节匹配，结束48288200ns一致；真实CRC失败、保持/退休、旧attempt拒绝、新attempt非冷恢复781标签/156path/10query、CPU q4 83/82/402/231及foreign net保留结论适用于相同观察。379文件归档实际恢复重审audit一致，180文件冻结results/route_block_system_crc_sources_20261027。归档e45678e9bacf7aca586e0338eb09647d2fb4e0f27d5e20d02691a71e2b88f2b2，audit57ac7014644f7a42eeb961db5a71924b66c5009e0522d607594f753257b7820b。运行器/审计器/variant已冻结，不覆盖修改。原仿真PID1005792/会话63725已终态，已完成根缓存释放98.53→96.96GiB，无错误、未删证据。

route_block_synth_v1仍实际综合运行，最近Vivado PID969366/runner969094/会话92622；禁止覆盖重启。已有core can_start、authority rearm/req_ready的Synth8-326警告，results/route_block_synth_observation_20261027保存前缀及活进程，当时7次是发生次数而非唯一/最终环数，也不能由没有route告警认定route环已消失。当前只有完整行为通过，未获完整结构通过。旧combined五源终态仍21环/100-LUT区域/WNS-12.538ns，不能移作新七源的最终计数。

后续诊断链已实际提交：会话8503/Python PID1370396，等待原PID969366且核对start ticks；只在原综合manifest observed/exit0后顺序运行inspect_restore_seed_synth.py、analyze_restore_seed_loops.py、audit_route_block_synth.py，失败即停，不重启综合；等待上限1200秒仅停止观察。下一会话先查现有链/原进程/diagnostic manifest，禁止另起同名诊断。结构审计器尚未实际执行；结构归档/恢复/冻结待终态完成。

独立新候选见results/recovery_normal_native_20261027.json/.md，选定recovery_normal_loops_v2。只将coordinator五个原有NORMAL/!cold_rst门控输出staged_valid/permit_work/j_ready/recover_ready/cfg_ready中的fault/unexpected特化为正常阶段谓词，不再引用AS/OS READY；完整fault/fail_now/unexpected/attempt_reset与全部时序逻辑不变，重试safe/drained/retired覆盖保留。source-bound二态65536组等价检查通过。原生REARM fixed切片仅替换coordinator，3场景179检查、31条事件及3836ns与参考一致，15字段写/3条回读/10失败拒绝/3成功，J0/无owner-authority请求，RAM/config/外部退休模型。不是结构、AXI或完整系统证明。

初版recovery_normal_native_v1因normal_fault在timeout声明前使用而VRFC10-3380编译失败，无展开/仿真；v2先声明wire再在原timeout定义后赋值，单独目录保留失败。失败14文件与成功40文件归档均实际恢复重审audit一致，35文件冻结results/recovery_normal_native_sources_20261027；对应variant/工具/证明已冻结。此NORMAL候选尚未接入route_block两个完整任务；其baseline coordinator与实际运行route源SHA相同。下一须结合新DCP残余路径接入，不替换任意publication/global fault消费者，不将局部恒等式称通用无环。

八项最终矩阵仍只有当前CRC pressure一项通过，其余七例未提交。固定价格、可信初始快照、持久化floor/认证、自然overflow分配回收、物理实现/板卡缺口保留。研究继续，goal active。

以下保留历史。

# 完整五源结构仍拒绝，路由空闲封锁候选开始验证（2026-10-27）

详见results/combined_loops_synth_20261027.json/.md。combined_loops_synth_v1综合与独立重开DCP诊断均终态；173文件归档实际恢复重审audit字节一致，177文件冻结results/combined_loops_synth_sources_20261027。产物完整性审计passed，但design_acceptance=rejected_combinational_loops、timing_qualified=false。check_timing21环，LUTLP-1一个100-LUT区域，文本仅5条闭合pin walk；不能把5当全部21，也不能将原20→21解释成独立故障数增减。原参考区域107LUT。

新LUT139647/FF88310/BRAM163/DSP23/URAM0，端口63637位、零latch/blackbox。相对原开启参考LUT-105/FF+155，布局前WNS -12.538ns（原-9.910ns），最差路径96级/22.434ns，directory lease_phase→search error_code CE。完整设计未获时序改善或无环结论。methodology仍SYNTH-10=23/TIMING-16与18各1000/TIMING-23=1，1000非全端点数量。无人工waiver/false-path；Vivado自动环切断及未定义IO/时钟位置边界均保留。归档cc87ede113697e9f9f66ef5a37b8031b6cdd9689321f8ec3487ea9f44fe1eb28，audit990e14c888ffce7d0f1d943aac88ade9c781e134fcda17d25a98661fde5c4e95。已完成根缓存释放86.19→85.72GiB，无错误。

实际闭合路径包含route_join/controller rc_fault→host请求门控/dispatch→ready→rc_fault。基于results/route_block_identity_20261027.json的262144组二态恒等式，独立route_block_loops_v1只改两个文件：controller新增idle_fault=!rst&&(stopped||abort)；adapter block_external=held||c_busy||c_idle_fault，命名接口接线。完整fault表达式、FSM/回复/journal/checkpoint及在途事务逻辑原字节不变。idle_fault使用实际controller rst，包含cp_reset_held；该约简只在adapter held/busy资格和回复held掩码下成立，不能替代任意controller完整fault，未证明X/Z或时序等价。

两个新实验已实际运行，尚无终态通过：route_block_synth_v1（会话92622，runner969094，Vivado969366）在已恢复五源综合参考上仅再改上述两源，累计七源；同133RTL/参数/器件/10ns/Tcl/XDC。入口prepare_route_block_synth.py/run_restore_seed_synth.py，终态后inspect_restore_seed_synth.py、analyze_restore_seed_loops.py、audit_route_block_synth.py；新审计器已准备未执行。route_block_system_crc_pressure_v1（会话63725，runner991295，XSim1005792）已compile/elaborate并模拟中，参考已恢复combined_loops_system_crc_pressure_v1；TB/输入/参数不变，run_route_block_system.py与待执行audit_route_block_system.py要求27文件/native周期/12AXI/DDR/恢复流及结束时刻字节精确比较。禁止覆盖重启实际运行根。

旧综合PID155768、诊断链758368/会话92483均已终态，不再等待或重复开其diagnostic目录。旧五源CRC pressure27文件/48288200ns通过及172文件冻结保持有效，不能算新两源回归已经通过。新variant和新runner/auditor尚未冻结，运行期间不要修改其绑定源。八项矩阵其余七例仍未提交，待最终候选统一验证；固定价格、可信初始快照、持久化floor/认证、自然overflow分配回收、物理实现/板卡缺口保留。研究继续，goal active。

以下保留历史。

# 五源合并CRC完整重试通过，综合仍有环警告（2026-10-27）

详见results/combined_loops_system_crc_20261027.json/.md。combined_loops_system_crc_pressure_v1将capture两源与REARM三源合并到真实完整query系统；其余RTL/TB/输入/参数与restore_seed_retry_crc_pressure_v1相同。27文件的12AXI、native事件及实际周期、最终DDR与恢复流逐字节一致，结束48288200ns一致。新增父层residency_system的rearm_retired接线已在完整编译仿真中验证，不能仅拿原J0组件替代本系统证据。由相同观察继承原CRC失败/保持退休、旧attempt拒绝、新attempt8非冷恢复781标签/156path/10query、CPU q4 83poll/82expand/402candidate/231cost、owner/foreign net保留结论。

379文件归档已实际恢复重审audit字节一致，172文件冻结results/combined_loops_system_crc_sources_20261027。归档e8ff53ec4a4edccf9508d994cee61a55af7b2333420cc8400de3468ebb1c362a，audit92bc9cb6a7cb3ea7e3a0ec88044251235eaa235852794f00ebae2445662a464e。run_combined_loop_system.py/audit_combined_loop_system.py/freeze_combined_loop_system.py已冻结，不覆盖修改。已完成原根与preserved根干净缓存释放97.71→96.14GiB，无错误、未删除证据。旧仿真PID287696/会话16914已终态，不再运行。

combined_loops_synth_v1仍为实际本机Vivado综合运行（最近PID155768），同133RTL/原参数/10ns；先核对实际进程，禁止覆盖重启。已出现Synth8-326自动打断环警告，涉及route_join host/owner/label、authority rearm/req_ready及publish_valid；results/combined_loops_synth_observation_20261027保存前缀和存活证据，其中11次只是当时发生次数，后续增加，不能当最终或唯一环数。五源修复未获得完整无环结论；终态后顺序inspect_restore_seed_synth.py、analyze_restore_seed_loops.py、audit_combined_loops_synth.py，后者尚未执行。无waiver/false-path或虚造IO约束。

下一诊断见hardware/variants/combined_loops_v1/NEXT_DIAGNOSIS.md。source-bound分析results/route_block_identity_20261027.json验证262144组二态赋值：在实际adapter响应资格下，held||c_busy||c_fault可等价化为held||c_busy||(!controller_rst&&(controller_stopped||controller_abort))，controller_rst含cp_reset_held；full fault本身不能删除错误检测。仅局部布尔恒等式，无RTL修改/结构消环/时序证明；须与最终DCP对应，再用显式接口做隔离候选，不能层次引用私有状态当生产实现。

results/combined_loops_matrix_preflight_20261027.json已核对八项参考的实际恢复审计及五源baseline/candidate绑定，预检不是回归通过。当前仅CRC pressure一项合并回归通过；正常off/on双容量、cancel双容量和CRC full其余七项未提交。原固定价格、外部初始快照、持久化floor/认证、自然overflow分配回收及物理时序/板卡收益缺口保留。研究继续，goal active。

以下保留历史。

# 两项完整回归与REARM组件通过，五源合并综合运行中（2026-10-27）

查询展开修复的capture_loops_system_on_full_v1与capture_loops_system_crc_pressure_v1已完成：各27文件、共54文件的12AXI/native事件与周期/DDR/恢复流逐字节匹配已实际恢复审计参考，结束44590330ns/48288200ns。两个归档实际恢复重审audit一致，177文件冻结results/capture_loops_system_sources_20261027；详见results/capture_loops_system_20261027.json/.md。仅这两配置通过，不等于完整矩阵。

REARM三源候选见results/rearm_loops_component_20261027.json/.md与rearm_loops_v1。原生coordinator+label切片baseline一个环、fixed LUTLP-1/check_timing均零环，2313端口位/零latch/blackbox。新增不被同步rst掩盖的label rearm_retired；父层retry_safe使用它；REARM时attempt_reset用无authority/owner回复等价替换unexpected。父层residency_system未在切片编译。两版各3场景179检查、事件/3836ns一致：实际CRC失败及回复保持退休、旧attempt拒绝、safe撤销或迟到回复不清服务、更高attempt非冷重试。15字段写/3条回读，J0且无AXI；不能替代完整warm系统。局部1024/32二态赋值核对，不是完整形式等价。

早期rearm_loops_component_v1为TB offer初始化错误，probe只读诊断后仅TB两行改连续assign；生产源未变，不能称生产RTL反例。成功95/失败55/probe38文件三归档均实际恢复重审audit一致，61文件冻结results/rearm_loops_component_sources_20261027。已完成根缓存释放无错误，未删除证据。

combined_loops_synth_v1已实际启动本机Vivado2022.2（最近PID155768），合并capture两源与REARM三源；133RTL/原参数/10ns实验clock完全匹配restore_seed_synth_on_v1。须先查真实进程及manifest，禁止覆盖重启。入口prepare_combined_loops_synth.py/run_restore_seed_synth.py；终态后依次inspect_restore_seed_synth.py、analyze_restore_seed_loops.py、audit_combined_loops_synth.py。新合并审计器已准备但尚未执行；旧完整root仍是20环/时序验收失败，不能用组件结果推翻。

完整优化off/on双容量与取消/CRC非冷重试矩阵仍待合并候选统一执行，避免重复对仅部分修复跑剩余六例。combined_loops_system_crc_pressure_v1已实际完成compile/elaborate并进入XSim（最近PID287696，runner273737，会话16914），五生产源均绑定两个已恢复审计组件；参考restore_seed_retry_crc_pressure_v1，TB/输入/参数保持相同。入口run_combined_loop_system.py，终态后audit_combined_loop_system.py要求27文件的native周期/12AXI/DDR/恢复流逐字节匹配；新审计器尚未执行。合并候选尚无完整行为通过结论。下一先取得完整网表残余环，再定位authority/owner/fault反馈。无顶层IO约束/物理实现/板卡收益；固定价格、外部初始快照、持久化floor/认证、自然overflow分配回收缺口保留。研究继续，goal active。

以下保留历史。

# 最新：查询展开组件消环通过，完整回归运行中（2026-10-27）

见results/capture_loops_component_20261027.json/.md。原生三组件基线实际3-LUT组合环，两个源的隔离修复后LUTLP-1/check_timing均零环；递归、取消/错误、回复保持/退休回归及独立CPU/128组局部二态检查通过，归档恢复复审一致，35文件冻结。完整真实系统正常恢复及单槽CRC失败非冷重试两例正在XSim运行，尚无完整验证结论。完整query root其他恢复/authority/owner反馈仍待修复，无时序闭合或板卡收益结论。

以下保留历史。

# 最新：匹配综合发现组合环，硬件设计验收未通过（2026-10-27）

见results/restore_seed_synth_20261027.json/.md。优化off/on两组完整OOC及独立DCP检查完成，check_timing各20组合环，LUTLP-1分别103/107个LUT反馈区域；10ns布局前WNS为-9.941/-9.910ns。资源LUT140295/139752、FF88213/88155、BRAM163/DSP23相同。两归档实际恢复复审一致，186文件冻结；产物审计passed与设计rejected明确分开。尚无硬件时序/板卡结论，既有周期减少仅行为仿真。下一优先hardware/variants/timing_loops_v1/PLAN.md的隔离消环及完整协议回归；当前无生产修复或waiver。

以下保留历史。

# 最新：优化恢复的完整故障重试通过（2026-10-27）

见results/restore_seed_retry_20261027.json/.md与restore_seed_retry_v1/CONTRACT.md。32槽/单槽各第三字段写在途取消和最后记录CRC错误，共四例通过；保留journal、退休后失败且业务封锁、旧attempt7拒绝、新attempt8非冷重试、781标签完整回读和原path/query CRC、CPU q4重试及全部12AXI/最终DDR独立审计通过。生产RTL不变，4归档恢复复审一致，187文件冻结。此前正常恢复周期减少23.6%/30.3%的结论仍限行为仿真。匹配参数query root OOC关闭/开启两组综合运行中，10ns仅布局前实验约束，尚无资源/时序/板卡收益结论。

以下保留历史。

# 最新：恢复写重复初始化消融通过（2026-10-27）

见results/restore_seed_20261027.json/.md及hardware/variants/restore_seed_bypass_v1/CONTRACT.md。默认关闭兼容性及开启后完整G4恢复的32槽/单槽四例通过，12AXI/最终DDR/CPU重试和归档恢复重审均验证；标签恢复仿真周期分别减少23.6%/30.3%，保留原始CRC与781条回读。8份隔离生产源新增默认0的ENABLE_RESTORE_SEED_BYPASS及start锁存的restore_seed_enable，原生WS/WW来源与恢复fence共同授权；普通未知记录初始化不改。源码及审计器已冻结，不就地改已审计候选。开启优化后的系统级取消/CRC错误和attempt8非冷重试在独立restore_seed_retry_v1中运行，尚无结果；没有资源/时序/板卡收益结论。

以下保留历史。

# G4最后primary owner释放后的warm恢复通过（2026-10-27）

详见results/fourth_warm_20261027.json/.md与fourth_warm_phases_20261027.json。选定fourth_warm_full_v2/pressure_v2，全部生产RTL与正常fourth_system SHA一致，仅TB变化。原生q4 ripup清空990178 primary并使558358/265324 refs3/4后，第一个图R发生真实SLVERR；search status8/1poll/1次失败展开/0candidate，query status7/detail8/committed0/route_acked0，三键journal保持，未发生commit写。

原生G4/CP20两轮authority GET、工作6GET+3INC修复：990178从全零重新创建net26422/ref1/occ1，另两refs3→4、4→5，外来net23916/ref1与满pool/allocator不变。恢复实际G4源6/0/6、781标签/393页、156路径字、10query字；source path CRC f00b72b4/query327d3916、full/pressure标签083ee4ad/ae573141。781实际写及回读、原始路径/query字节和三类真实回执/退休/最终成功消费后才放行，target7/1/7，无外部cold reset或工作DDR重装。

失败attempt6在受理时已消费sequence180330。新attempt7由原生target reset/rebase恢复G4源floor180329；空第四槽上的180329被status1拒绝、prepare_acked0且无工作副作用，再重新登记历史路径/ripup及180330重试。这不是“未消费序号重试”，也不是跨attempt全局永不重复或持久化floor证明。

两容量重试83poll/82expand/402candidate/231cost均CPU匹配，全部12AXI/37个owner物理record写/146284032B最终owner/781标签393页及3MB物理页核对。最终四路径CRC eec36b70/query8a39d874/version7/flags5d/floor180330、slots15/CP20/journal3。结束4547230/4775002周期仅行为仿真；owner修复579/578周期、label恢复374180/290780周期，不是板卡收益。

两成功与一个仅TB声明顺序编译失败归档均实际恢复重审audit字节一致；编译失败未运行仿真，不是生产RTL反例。496文件冻结results/fourth_warm_sources_20261027。新阶段统计确认781次baseline读、3905恢复字段写之外另有3905 seed写，下一优先hardware/variants/restore_seed_bypass_v1/PLAN.md的隔离恢复开销消融：默认关闭精确回归、开启后保留普通未知记录baseline语义及CRC/完整回读/取消失败退休边界。优化尚未实现。

任意故障/取消、变价标签有效性、持久化writer/认证/floor、baseline reseed、自然overflow新增回收、综合时序/板卡仍缺；初始clones/full baseline及历史路径元数据外部可信。已审计归档收尾释放本轮干净缓存，不删证据。研究继续，goal active。

以下保留历史。

# 四路径G4发布与自然第四查询通过（2026-10-27）

详见results/fourth_system_20261027.json/.md及hardware/variants/four_path_v1/CONTRACT.md。选定fourth_system_full_v2/pressure_v2，沿用全部生产RTL，TB显式PATH_SLOTS4、156字实际导出。先完成已有G3 warm前缀，再原生lease下重arm累计四行owner复制到未使用A区，并用781标签/393页、前三路径加空第四槽156字、query10字/floor180329三方共同发布G4/CP20。authority第72读beat后实际退休轮换，全部85读beat分别按旧A=G2/新A=G4核对；不能拿最终A解释旧读。

自然q4 sequence180330/connection170791/net26422/source66893/sink6954：登记历史路径6954→990178→558358→265324→66893后原生ripup，990178最后primary owner实际写全零，另两refs4/5→3/4；连续搜索提交回1/4/5。两容量83poll/82expand/402candidate/231cost全部CPU匹配，12AXI/31owner物理写/146284032B最终owner/781标签393页及3MB物理页核对通过，新增baseline miss0，旧三路径与外来net23916保留。无外部cold reset/工作DDR重装。

G4源path CRC f00b72b4/query327d3916，full/pressure标签083ee4ad/ae573141（同集合不同顺序）；最终四路径CRC eec36b70/query bcf23ef5、floor180330/slots15/CP20/journal3。结束4165462/4482678周期仅行为仿真，不是板卡速度。最终四路径尚未发布G5。

开发full_v1生成器误把两处查询序号断言写成190328，原生实际导出180329后失败；修正版只改两断言，共有native事件/周期和12AXI前缀逐字节一致，不是生产RTL反例。两成功加一开发失败归档均实际恢复重审audit字节一致，489文件冻结results/fourth_system_sources_20261027。q4独立cost/filter、四槽组件3275/126检查与另外四归档复审、34源文件冻结见results/four_path_inputs_20261027.json。

下一按four_path_v1/NEXT.md，在q4已原生释放最后owner而尚未commit时注入图R故障，验证G4三键原生INC恢复及保存路径/标签/query恢复和未消费序号重试。G4 warm尚未实现。固定价格/history、初始外部可信clones/full baseline、持久化writer/认证/floor、任意变价、baseline reseed、自然overflow新增回收、当前层级综合时序及板卡仍缺。每轮审计归档后释放本轮干净缓存，不删数据。研究继续，goal active。

以下保留历史。

# 自然第三查询G3 warm恢复与下一查询最后owner释放采集通过（2026-10-27）

详见results/third_warm_20261027.json/.md、third_warm_phases_20261027.json与iter2_fourth_20261027.json/.md。选定third_warm_full_v2/pressure_v2，生产RTL全部SHA等于前轮正常三槽系统。真实q180329先拆旧路径，三个journal键990179/558358/265324；第二个commit写558358的B错误后工作refs2/4/4，status7/detail5/committed0/acked1。G3/CP19两轮authority核对目标2/4/5，实际6GET+1INC，仅265324补4→5，其他net23916/ref1保留。

原生恢复G3 source5/3/5、781标签/393页、117字q1/q2加空第三槽、10字query及floor180328。原path CRC f4394572/query9493257c，full标签742f5a50/pressure2f1c12da；全部781实际写入/回读，三回执全齐/服务退休/成功回复消费后才放行。无外部cold reset或工作DDR重装；新6/0/6保留floor180328，再登记q3旧路径、原生ripup与重试。失败前和重试均CPU114poll/113expand/565candidate/302cost匹配，全部12AXI/25个owner物理写/146284032B最终owner与G3相等/全部3MB标签页通过。最终三路径CRC437e9a9a/query03650e61、floor180329/CP19/journal3；尚非G4发布。

本轮仅修TB槽号观察：旧slot2日志被最低位截为0并写入旧q1观察数组；v2完整slot2与旧数组范围修正，两版12AXI/所有最终镜像/事件周期完全相同，仅46处槽号日志差异。两个选定v2及两个legacy_stable对照包均实际归档恢复重审字节一致。原v1归档审计曾因目录遍历导致JSON键序变化而字节失败，语义/数据哈希一致，失败记录和旧归档保留；稳定包明确repackaged_from，不冒充新仿真。236文件源冻结results/third_warm_sources_20261027。

结束3760351/4010239周期仅行为仿真。label恢复阶段373309/290752周期，781次baseline读、3905次恢复字段写、总7810次底层字段写，提示后续可研究冗余初始化；尚无该优化或板卡收益结论，不能由两容量不同顺序直接推断缓存优劣。

下一自然q4 query180330/connection170791/net26422/source66893/sink6954已CPU采集；旧/新路径6954→990178→558358→265324→66893。原生准备释放990178唯一owner，refs1→0/occ1→0/owner-1，另外两节点4→3、5→4。独立CPU83poll/82expand/402candidate/231标签更新，全9089009行q3提交→q4准备仅五行变化，overflow/prices不变；两采集10文件相同/全路由原哈希不变，归档实际恢复及prepare/transition复审字节一致，14文件冻结results/iter2_fourth_sources_20261027。231尚非独立cost oracle，q4 RTL尚未接入。

下一按hardware/variants/third_warm_v2/NEXT.md生成q4独立cost/filter、验证四路径槽及156字镜像，再接实际G4发布/连续q4与资源释放生命周期。不能拿q2/q3槽代替q4，也不能把117字CRC当156字G4源。G4、q4 RTL、q3其他故障/取消、任意变价、持久化writer/认证/floor、baseline reseed、实际overflow新增回收、当前层级综合时序和板卡仍缺。每轮审计归档后按目录释放干净文件缓存，不删数据。研究继续，goal active。

以下保留历史。

# 三路径槽与完整自然q3连续执行通过（2026-10-27）

详见results/path_capacity_20261027.json/.md、results/iter2_third_cost_20261027.json/.md及results/path_capacity_third_20261027.json/.md。PATH_SLOTS默认2、实测3，参数贯通route/host/query/residency/search/boot/export，完整路径镜像78→117字。三槽controller2494检查、export126检查、query29场景通过；默认export114检查与旧事件一致。默认两槽32缓存槽/单缓存槽各28文件（共56文件）、12AXI/native trace/结束周期逐字节匹配原G3基线。组件后端mock与完整系统证据分开。

q3 query180329/connection170785/net26422/source66893/sink151354的独立cost/CPS1/filter oracle通过：114poll/113expand/565candidate/302cost，cost与CPS1工作输入同q2字节一致。584标签保守闭包仅用于审计，未预加载硬件。

选定path_capacity_third_full_v1/pressure_v1。三槽完整系统先实际G3/CP19共同发布，保存source5/3/5、floor180328、781标签、q1/q2及空第三槽117字path。原生lease登记q3历史路径元数据、不加owner引用；实际ripup把990179/558358/265324 refs2/4/5降至1/3/4，再实际搜索提交回2/4/5。q1/q2和其他net23916/ref1保留，无冷复位/工作DDR重装。两例CPU逐项数值、全部12AXI、781标签/393逻辑页/全部3MB物理页通过；q3新增baseline miss0。新增6条owner record写，总19条；最终146284032B owner等于G3图像。结束2857604/3114246周期，仅行为仿真。

G3原始117字path CRC f4394572；最终三路径导出CRC437e9a9a、query CRC583925e2、floor180329，最终槽位图7/CP19/journal3。最终三路径未共同发布G4，不能冒充G3恢复源。六个组件/默认系统、两份CPU输入、两个三槽系统共十份归档已实际恢复重审，audit字节一致；222文件冻结results/path_capacity_sources_20261027。输入恢复曾因并行恢复依赖目录而暂缺文件，按依赖完成后重审通过，原因记入恢复凭据，不是RTL反例。

下一优先按hardware/variants/path_capacity_v1/NEXT.md在隔离候选接q3第二个commit owner-B故障与G3 warm恢复。拆旧路径已产生三个journal键；恢复可能需要INC补回尚未提交的引用，不能套用q2两键DEC假设。G3源CP19/5/3/5/781标签/117字两有效路径/floor180328；attempt>5，实际回执和退休全齐后才放行，重新登记q3旧路径并ripup再重试。

仍无q3故障/G3 warm、G4发布/恢复、任意变价、持久化writer/认证/floor、baseline reseed、实际overflow新增回收、综合时序或板卡收益证明。初始G1与全图baseline外部可信、价格/history不变。已审计实验收尾按目录释放干净文件缓存，不删数据、不做全局drop_caches。研究继续，goal active。

以下保留历史。

最新实验：[真实G3/CP19联合发布](results/owner_g3_publish_20261027.md)在32槽/单槽通过，十归档恢复复审一致，183文件冻结；[自然q180329采集与全量转换](results/iter2_third_20261027.md)也通过。下一优先扩展固定两路径槽及快照协议，再接q3独立cost oracle/连续RTL与G3 warm；尚无板卡收益结论。

最新实验：实际owner累计脏行重arm与完整G3候选通过；详见[实验记录](results/cumulative_owner_system_20261027.md)。当前发布仍G2/CP18；G3/CP19三方发布及其临时busy/回执接线待验证。

最新实验：真实777标签恢复的baseline AR/R在途取消与非冷复位重试通过；详见[实验记录](results/label_baseline_cancel_20261027.md)。下一优先G3 owner writer重arm，尚未实现。

最新：[777条CRC失败后非冷重试](results/label_baseline_crc_retry_20261027.md)双容量通过：776部分写、同attempt拒绝、更高attempt恢复777；生产RTL未变，全部11AXI/归档复审一致。

最新：[零预加载777标签G2 warm恢复](results/label_baseline_warm_20261027.md)双容量通过。修复管理空探测误触发seed，保留真实present校验；1562基线读/全部11AXI审计及六归档恢复复审一致。固定价格行为仿真，非板卡证明。

最新：[第九路AXI排空覆盖/取消退休](results/label_baseline_fence_20261027.md)双容量通过，正常17文件精确匹配。反例只证明旧物理指标漏计，不证明提前reset；G2 warm实际恢复仍待接入。

最新：[两条完整自然查询零预加载/原生按需标签](results/label_baseline_pair_20261027.md)双容量通过：q1加载777，q2新增4；默认关闭16文件精确匹配。G2 warm及第九路AXI恢复退休联锁尚待接入。

最新：[原生manager缺失填充/dirty写回](results/label_baseline_miss_20261027.md)组件双容量通过；默认关闭全系统19文件精确匹配。完整自然query启用接入仍待完成。

最新：[全节点标签基线与只读reader组件](results/label_baseline_20261027.md)通过；完整manager按需加载尚待接入，初始CPU闭包依赖仍在。

最新：CRC失败后非冷复位重试的32槽/单槽完整验证通过，见[实验记录](results/label_crc_retry_20261027.md)。生产RTL未变；初始CPU闭包和G1 clone仍为前提。

## 源标签CRC绑定（2026-10-27）

入口scripts/run_label_source_crc.py ROOT --full-only/--pressure-only；审计audit_label_source_crc.py。--bad-crc负例审计audit_label_source_crc_reject.py，--default回归审计audit_label_source_crc_default.py。单元run_label_crc_unit.py（--disabled）/audit_label_crc_unit.py。正式full_v2/pressure_v2、bad_full_v3、default_full_v1、unit_v1/unit_default_v1，结果results/label_source_crc_20261027.json；六归档恢复重审一致。

## 运行中标签导出与恢复（2026-10-27）

入口scripts/run_runtime_label_snapshot.py ROOT --full-only/--pressure-only；审计audit_runtime_label_snapshot.py。--default运行旧正常查询回归，审计audit_runtime_label_default.py。单元run_label_snapshot_unit.py/audit_label_snapshot_unit_hold.py。正式证据full_v3/pressure_v3、default_full_v2、unit_v4，结果results/runtime_label_snapshot_20261027.json。初始CPU读闭包与G1 clone仍为前提，无板卡性能结论。

## 运行中 owner 增量快照联动（2026-10-27）

执行 scripts/run_iter2_runtime_owner.py ROOT --full-only/--pressure-only，再执行 scripts/audit_iter2_runtime_owner.py ROOT；单元入口 scripts/run_owner_snapshot_unit.py 与 audit_owner_snapshot_unit.py。正式选定 full_v4/pressure_v4、unit_v3，结果见 results/runtime_owner_snapshot_20261027.json。新增第9 AXI口实际复制/回读4条脏行并门控G2发布，之后保留真实G2 warm故障/822恢复/CPU重试链。初始基线clone与标签未来读闭包仍为前提，无板卡加速结论。

# 真实iteration2的822标签G1 warm恢复通过（2026-10-26）

详见results/iter2_warm_20261026.json及hardware/variants/iter2_warm_v1/CONTRACT.md。query/search/residency三层增加RESTORE_RECORDS参数，默认512，本例显式1024；822标签、probe204279及stream末尾821同步接入。32槽/单槽均通过完整warm恢复。G1/CP17初始PC租约实际导出empty path78字/CRC4ca00bd5和query10字/CRC4aaeb774，后者version3/flags0x0d/无已消费sequence，未手填旧seq1。

真实自然query180327的第二个owner写（558358）BRESP2，第一写339193成功，形成两键journal；query status7/detail5/committed0。原生G1两轮authority核对与2次DEC恢复339193至0/0、558358/net26422至refs3/occ2，另一net23916/ref1保留。新attempt4/query2/price4恢复822条标签并实际回读验证822；empty path与初始query原字节/CRC经原生回执消费，三类receipt与服务退休联合完成，最终成功回复消费后才放行，无外部cold reset/工作DDR重装。

故障前和重试的两轮171poll/170expand/849candidate/421cost均与原CPU数值oracle一致。重试成功提交三节点、target清理、原生ripup、重复完整sequence180327拒绝通过。822标签、403逻辑页对应全部3MB物理页、10次owner record写、最终146284032B owner图像及全部8AXI重放通过。source price/history未变。默认512的旧328标签G2共享恢复，两容量28文件及周期精确匹配原基线。

同时采集并审计下一自然sequence180328：connection170996/net26422/source66893/sink67922，113expand/114poll/564candidate/302标签更新；原CPU全路由哈希不变。下一prepared-state在558358/265324上的refs为3/4，而上一提交后为4/5，存在额外准备阶段owner变化，不能直接装新快照冒充连续G2执行。新query的独立cost/CPS1/oracle/闭包及RTL仍未生成或验证，具体接入要求见G2_NEXT.md。

四个RTL实验与一份CPU采集均已归档并实际恢复重审，audit字节一致；源冻结results/iter2_warm_sources_20261026。未完成本数据G2三方发布/连续下一query故障恢复、任意未知页/全局cache构建、运行中硬件快照writer、持久化floor/认证、变价有效性、综合时序或板卡收益。当前822 labels仍依赖CPU保守未来读闭包，本自然路径不新增overflow slot。研究继续，goal active。

以下保留历史。

# 真实iteration2接入当前完整查询生命周期通过（2026-10-26）

详见results/iter2_lifecycle_20261026.json及hardware/variants/iter2_lifecycle_v1/CONTRACT.md。选定full_v5/pressure_v5，真实connection170782/net26422/source66893/sink204279，完整sequence180327与存储version3/query1/price3分离。使用同一CPU prepared-state的design、146284032B owner primary/pool/allocator、history/price/net/CPS1及822条保守标签闭包，不混用原q1/q2 oracle。先通过原生PC租约/只读authority验证真实overflow链，再由当前query_lifecycle、自主search、实际heap POLL、回溯和owner引擎完成整条查询。

两容量均171poll/170expand/849candidate/421cost通过原CPU数值oracle；822标签与403逻辑页对应的全部3MB物理页（含空页）、全部8AXI逐字节重放通过。真实previous-pointer链含三个内部节点339193/558358/265324，提交refs1/4/5、occupancy1/2/1，节点558358另一net23916始终ref1。原生ripup回refs0/3/4，整个146MB owner图像逐字节等于输入，pool/allocator与其他net未破坏。重复sequence180327被status1拒绝且prepare_acked0，最终存储context仍3/1/3。

本轮不新增生产RTL修复，沿用已审计multi_owner_capacity_fixed_v1 coordinator和warm_retry_system_v2其余生产层级。两个归档实际恢复重审audit字节一致，源冻结results/iter2_lifecycle_sources_20261026。以上为行为仿真；本自然路径不新增overflow slot，不能将前轮组件满池修复与本轮正常查询合并为完整多net warm恢复结论。

仍缺本数据的G2三方发布、warm故障恢复、任意未知页/全图cache生成、任意变价、持久化floor/认证、综合时序和板卡收益。822条CPU未来读闭包是当前前提；恢复服务MAX_RECORDS仍512、旧fixture snapshot_count仍328，下一阶段须显式参数化到1024并迁移822流/实际path/query CRC。WARM_NEXT.md记录G1两项真实owner-B故障恢复的接入要求，以及G2后续query须新CPU oracle、不可重用已消费sequence的约束。研究继续，goal active。

以下保留历史。

# 同资源多net与满overflow池的恢复顺序修复（2026-10-26）

详见results/multi_owner_recovery_20261026.json及hardware/variants/multi_owner_recovery_v1/CONTRACT.md。真实iteration2快照的overflow池capacity/live均53734且无free项。节点208292原net6632/ref1、net17601/ref2；基于真实快照构造确定压力变更（非自然路由轨迹），通过实际owner引擎删除主owner、加入net0、两次增加net17601引用，四次mutation产生三个去重journal键。旧生产coordinator先补回net6632，在后续net0释放空间之前遇status5 CAPACITY，恢复status3/J3；negative_v4保留实际反例。

新候选只对匹配cookie/原GET值且无写入的INC CAPACITY拒绝延后一次，继续处理其余journal，再追加一轮修正并最终完整验证。真实组件fixed_v1通过：先释放net0并修正net17601，再补回net6632，4次修正/J0，池大小仍53734、allocator回到满池。追加轮有独立authority cookie；永久CAPACITY模拟单元恰2次拒绝后status3/J1，不能无限循环或放行业务。

独立CPU模型与原CPU快照映射检查修复例21个真实owner操作/全部响应，逐条匹配16个物理record写，比较最终146284032字节；其余节点/池条目不被破坏，live和snapshot AXI全部重放通过。新coordinator用于完整系统正常G2回归，32槽/单槽共28文件及周期精确匹配旧基线。五归档实际恢复重审audit字节一致，源冻结results/multi_owner_recovery_sources_20261026。

范围必须分开：多net满池测试为真实owner/authority/coordinator组件，但reconfigure/labels回调模拟；完整系统回归仍为原capacity0单net两路径。尚未完成完整warm系统的多net快照发布/路径查询恢复，也无通用所有排列、并发回收、任意变价、持久化floor/认证、运行时快照、综合时序或板卡性能结论。

下一优先依NEXT_INTEGRATION.md，将已有真实iteration2 prepared-query、capacity53734布局和数值oracle接到当前query_residency_system/三方发布/保存状态恢复；不要重写已验证owner基本单元或混用原q1/q2单netoracle。新候选coordinator位于multi_owner_capacity_fixed_v1/sources，其余warm层级沿用warm_retry_system_v2。研究继续，goal active。

以下保留历史。

# 成功回复发布后的abort边界与J0重试通过（2026-10-26）

详见results/warm_late_abort_20261026.json与hardware/variants/warm_late_abort_v1/CONTRACT.md。32槽与单槽各覆盖成功回复背压后abort、成功回复消费同沿abort，共四例。真实完成G2/CP18六项修复与三类回执后，原生coordinator已提交5/3/5、journal清零并发布status0/cookie c0010001/corrected6。held场景继续在abort下背压8周期，edge场景于同一实际消费边沿断言abort；成功回复VALID及全部检查的状态/cookie/corrected保持稳定，不能把已经发布的成功改写成取消失败。

消费后仍warm owned/fault、业务关闭，current5与attempt floor5/J0保留，不能称此前成功被回滚。旧回复/fence退休后，相同attempt5原生status1拒绝，更高6/query0/price6以新cookie非冷复位重试成功，不重装工作DDR。J0分支无authority/owner journal访问，不伪造六键GET；重新恢复并验证全部328标签、78路径字和10query字后才允许正常业务。CPU oracle43poll/42expand/176candidate/122cost、最终标签、两路径拆线及共享2→1→0通过，全部8AXI/DDR重放通过。

本轮仅改独立TB，生产RTL逐文件SHA等于warm_retry_system_v2；成功发布前的事件/周期与既有shared-last基线精确匹配。四归档实际恢复后重审audit字节一致，源冻结results/warm_late_abort_sources_20261026。行为仿真不能作为板卡速度、任意竞态或取消回滚证明。

固定价格/history、一个net两路径/capacity0与两个确定边沿仍是本轮范围。晚到abort是否需另设显式状态/确认尚未形成通用接口；持久化floor/认证、运行中快照、多net/overflow、任意变价距离有效性、综合时序及板卡仍缺。下一优先扩展真实多net/overflow与资源回收生命周期，避免只在capacity0单net fixture上得出普遍结论；研究继续，goal active。

以下保留历史。

# 标签写入/校验阶段的AXI在途取消与非冷复位重试通过（2026-10-26）

详见results/warm_axi_cancel_20261026.json与hardware/variants/warm_axi_cancel_v1/CONTRACT.md。32槽、单槽各覆盖R与B两种取消点，共四例。R场景328标签已写完但第一项读回校验未完成，真实AR已受理但R未返回；B场景32槽/单槽分别写完53/36项，AW及完整W已受理但B未返回，此时触发abort；延迟agent真实响应32周期，期间物理drained为false、label busy、owned/fault持续、恢复完成VALID为false且业务封锁。没有DUT握手掩码或伪造回复。

放行后实际R最后一拍/B握手、原生标签status7回执消费、服务退休先于coordinator status6；journal6/CP18保留。相同attempt5被原生拒绝，再以新cookie的attempt6/query0/price6非冷复位重试；不重装工作DDR。原生G2两轮核对保留的六键，工作owner仅12次GET、无DEC、corrected0，全部328标签重新写入并验证，q1路径/原始query重建后成功放行。CPU oracle43poll/42expand/176candidate/122cost、最终标签、两路径拆线和共享2→1→0通过，独立重放全部8AXI与最终DDR。

本轮无新增生产RTL修复：全部生产源逐文件SHA等于已审计warm_retry_system_v2。仅改独立TB与AXI内存agent延迟接口，取消前前缀逐行/周期匹配既有基线。四例归档实际恢复后重审audit字节一致；源冻结results/warm_axi_cancel_sources_20261026。结论为行为仿真正确性，不是板卡速度或加速比。

仍是一个net两路径/capacity0、价格/history内容不变、两个确定在途取消点；不能声称覆盖任意取消、永久不返回、协议违规从设备或晚成功abort。下一优先晚成功abort与提交/回复消费边界，然后持久化floor/认证、运行中快照、多net/overflow、任意变价距离有效性、综合时序及板卡。研究继续，goal active。

以下保留历史。

# Warm取消后非冷复位重试通过（2026-10-26）

详见results/warm_retry_20261026.json与hardware/variants/warm_retry_v1/CONTRACT.md。基于warm_cancel_fixed_v2，隔离变体只改receipt join和顶层命令选择；失败回复消费、旧fence释放、新fence重获且实际服务/物理事务退休后才允许重新arm。HALT至新WAIT始终owned，普通业务持续关闭；真实新backend offer选择新recover字段并同沿锁存，避免再次送旧attempt。

35项门控单元检查通过。真实32槽与单槽两例均在G2共享六项修复、query9/10取消后，保留journal6/CP18；相同attempt5返回原生status1，新cookie的attempt6/query0/price6非冷复位重试成功，不重装工作DDR。原生REARM/target_reset后两轮G2读取再次核对全部六键，仅12次工作GET、无DEC、corrected0，journal只在最终成功清零。重新恢复328标签、78路径字、10query字，source4/2/4映射到6/0/6、sequence1；真实回执与最终成功回复消费后才放行。

q2 CPU数值oracle43poll/42expand/176candidate/122cost、最终标签、原生两路径拆线及共享2→1→0通过；独立审计全部8AXI与最终DDR。健康两容量回归共28文件及周期精确匹配shared-last基线。四归档实际恢复后重审audit字节一致，源冻结results/warm_retry_sources_20261026。以上为行为仿真正确性，不是板卡速度或加速比。

价格/history内容不变；仍为一个net两路径、capacity0。下一优先标签或AXI在途取消、已受理回复退休与重试，以及晚成功abort；通用多net/overflow、运行中快照、持久化认证与floor、任意变价有效性、综合时序和板卡仍未完成。研究继续，goal active。

以下保留历史。

# Warm查询取消的错误出口与退休修复通过（2026-10-26）

详见results/warm_cancel_20261026.json与hardware/variants/warm_cancel_v1/CONTRACT.md。真实G2共享故障修复后，在query原始镜像9/10字取消。两个实际反例：旧LABELS仍等成功joined，原生query错误回复已消费后仍卡住；只修错误出口会在旧query回复尚未消费时提前返回失败。最终LABELS错误独立转FAILWAIT，并以真实warm服务/回复退休约束失败完成，包含CF busy/回复观察。

warm_cancel_fixed_v2的32槽和单槽通过：原生query status2/CRC0保持8周期时恢复完成VALID始终0；消费后才返回status6，journal6/CP18保留，服务均退休。最终失败回复消费后仍HALT/owned/fault，业务关闭，未假装已经允许重试。实际工作owner图像等于G2快照，全部8AXI/DDR重放通过。健康六项共享恢复normal_v2两容量共28文件及周期精确匹配既有baseline。四归档实际恢复重审audit一致，源冻结results/warm_cancel_sources_20261026。

本轮不是AXI在途中断，也未实现失败后非冷复位重试、晚成功abort或任意取消点。下一优先HALT在旧回复/fence全部退休后，为新attempt6/query0/price6重新arm并选择新命令字段；真实G2只读复核保留journal，corrected0，再恢复保存状态/重试，详见HALT_REARM_NOTES.md。标签/AXI取消、通用多net/overflow、运行中快照、持久化认证、综合时序及板卡仍缺。研究继续，goal active。

以下保留历史。

# 两共享资源故障与5/6项journal修复通过（2026-10-26）

详见 results/warm_shared_20261026.json 与 hardware/variants/warm_shared_v1/CONTRACT.md。选定 warm_shared_first_v1/last_v1，仅改变TB错误注入时机及观察；所有生产RTL与warm_system_v2逐文件SHA一致，无新增生产修复。

真实q2共享节点554512/263946分别是第5/6次owner写。32槽和单槽共四例通过：前4/5个物理B成功，第5/6个SLVERR，产生5/6项实际journal。G2原生两轮GET返回四个新资源ref0和一/两个共享资源ref1；旧G1对应共享行全零。工作owner实际GET/DEC/GET验证，共享ref2降至1而occupancy保持1，保留q1关系，不能混同旧G1的ref0。第5写场景中未纳入journal的另一共享行也保留。

同实例不中途冷复位/重装工作DDR，完成328标签、q1路径与源查询镜像恢复及新attempt5/3/5下q2重试。CPU数值oracle43poll/42expand/176candidate/122cost、最终标签、两条原生路径拆线、共享2→1→0通过。独立字节/事件审计全部8AXI及最终DDR，核对5/6键、G2两轮地址/返回、15/18工作owner操作和全部回执；其他net状态保留。两归档实际恢复重审audit一致，新增源冻结results/warm_shared_sources_20261026。JSON阶段周期仅行为仿真，不是板卡速度或加速比。

价格/history内容不变，仅attempt标签变化。仍是一个net/两路径、capacity0的两个确定共享写错误点；无任意价格变化距离有效性、通用多net/overflow、运行中工作DDR快照、持久化认证/下限、综合时序或板卡结论。下一优先真实恢复流/AXI在途取消、已受理回复退休及恢复过程失败后非冷复位重试，再回绕/未知页等。研究继续，goal active。

以下保留历史。

# 完整系统换代后 warm 故障恢复通过（2026-10-26）

详见 results/warm_system_20261026.json 与 hardware/variants/warm_system_v1/CONTRACT.md。选定 warm_system_v2，32槽/单槽两例真实G2发布后，q2首个owner写B发生SLVERR；真实fence和coordinator从G2只读窗口两轮GET修复一项journal（node1231788/net2717，目标ref0/occ0），不是TB伪造owner/完成回复。

原生标签模块经实际DDR/pager写入和回读328记录，原生路径恢复q1槽，原生查询以原始G2镜像/CRC转换到新attempt5/query3/price5并保留seq1。实际标签回复可先消费，三种回执全齐/退休、最终恢复回复消费后才放行业务；无需普通checkpoint lease（实际pc_owned0）。q2随后通过CPU独立数值oracle：43poll/42expand/176candidate/122cost及最终标签；两条原生路径可拆线，共享263946/554512引用1→2→1→0。全8AXI/最终DDR、恢复真实标签数据、源查询字节、G2修复地址及全部回执顺序重放通过，其他net状态保留。

修复两处接线/阶段问题：前端ready本身就是后端受理，必须在真实backend offer选择模式并同沿arm；标签恢复自身建立新上下文，不能在启动前要求它已经建立。旧完整实例出现wm_mode0未arm失败；旧上下文join在140ns/check9失败。新上下文原生切片405检查通过，两负例及修复证据均保留。关闭warm的normal_v2两容量共28文件和周期精确匹配前轮。五归档实际恢复重审audit一致，源冻结results/warm_system_sources_20261026。

JSON另列行为RTL仿真阶段周期（owner、label、path、query及故障到重试），不是板卡时间或加速比。价格/history DDR始终不变，attempt标签改变；不能宣称任意价格变化下距离标签有效。

当前只覆盖一个net/两路径、capacity0的首个q2 owner-B故障。共享节点故障、多项journal、恢复流/AXI在途取消、非冷复位失败重试、epoch回绕/未知页、通用多net/overflow、运行中工作DDR快照、持久化认证/下限、综合时序和板卡仍缺。下一优先共享资源写故障（G2应恢复ref1，区别旧G1的ref0）及多项journal，再取消/退休与无冷复位重试。研究继续，goal active。

以下保留历史。

# 原生标签/路径/查询回执联合逻辑通过（2026-10-26）

详见 results/warm_receipt_join_20261026.json 与 hardware/variants/warm_receipt_join_v1/CONTRACT.md。选定 warm_receipt_join_v4：锁存 G2/CP18 快照身份、目标上下文、cookie、标签数量与原始 path/query CRC；只有实际原生受理/消费形成回执。标签回复即使先消费也保留成功记录；路径/查询各只准入一次；已受理导入的 admin_safe 不随自身 busy 关闭。全部回执齐全并退休后才 joined，最终恢复回复消费前保持 owned；abort 同拍不放行。

389次检查、9场景，8轮原生 label_restore 的2624行回读验证/13120字段真实RAM写入；原生路径78字及 ENABLE_REBASE=1 查询40B实际恢复（新上下文5/3/5、seq1）。回复保持、标签持续start offer、部分路径/查询、物理退休暂停、错误cookie/CP/上下文、CRC错误、原生成功但不符选定bundle CRC的镜像均验证。独立逐周期模型核对72个状态观察，标签写入/读回请求和源数据/CRC重放通过。归档实际恢复复审一致，源冻结 results/warm_receipt_join_sources_20261026。

范围仍是原生三控制器切片：标签后端为可变RAM模型；recovery_owned/owner_repaired/活动上下文来自TB，没有完整fence/coordinator、工作owner AXI修复或q2搜索重试。HALT当前只支持退休后的冷复位，不是无复位恢复证明；无距离标签跨价格有效性、持久化授权、综合时序或板卡结论。

接入约束已明确：现有 lr_rsp_ready=!k_labels_valid 必须在warm模式替换，避免与联合完成相互等待；用 label_allow 屏蔽持续 labels_valid 重启。joined 的 retired 不能包含正等待该回调的coordinator busy/recovery-owned。下一优先实际backend recover握手arm、recovery fence管理员和三层接线，再完整G2换代后q2故障/原生GET修复/保存q1状态/新上下文CPU重试。研究继续，goal active。

以下保留历史。

# 查询恢复上下文转换通过，完整 warm 恢复仍待接入（2026-10-26）

详见 results/query_warm_rebase_20261026.json 与 hardware/variants/query_warm_rebase_v1/CONTRACT.md。选定 query_warm_rebase_v3：原生 query_lifecycle 增加默认关闭的 ENABLE_REBASE；开启后以恢复许可与选定 source 上下文验证原始40B镜像及原 CRC，再把 ledger 原子绑定到新 attempt 上下文，保留序号下限。不改输入字节，不伪造原 CRC，也不把距离标签自动视为新价格下有效。

真实 G2 bundle version4/query2/price4/seq1 → version5/query3/price5/seq1。119次检查、12事务和独立事件/字节CRC状态机审计通过：无许可、错误 CRC/generation/source、部分流、完整包后发布前许可撤销、abort、序号回退均不发布；成功后导出新上下文与新CRC，seq1重放被拒绝。此处恢复许可及source descriptor来自TB，尚未接完整恢复fence。

默认 ENABLE_REBASE=0 的完整32槽与单槽回归 query_rebase_normal_v2 通过：每例8 AXI+4 DDR+完整native协议+directory，共28文件逐字节及最终周期一致，保留前轮共同发布/G2原生GET/q2能力。两归档实际恢复后重审audit一致；源码冻结 results/query_warm_rebase_sources_20261026。

尚未实现或验证完整换代后的 warm 故障恢复。下一优先 recovery fence 下管理员资格、label/path/query真实回执联合完成（label回复可先被消费）、上下文转换接线，再G2原生GET修复/恢复q1保存状态/新上下文q2重试。运行中工作DDR快照、多net/overflow、持久化认证、综合时序和板卡仍缺。研究继续，goal active。

以下保留历史。

# 完整系统共同发布及正常 q2 连续性通过（2026-10-26）

详见 results/checkpoint_commit_20261026.json 与 hardware/variants/checkpoint_commit_v1/CONTRACT.md。选定 checkpoint_commit_v6；在已审计 checkpoint_system_v4 的 query root 增加受原生 lease 保护的只读 authority 检查接口，其余生产 RTL 不变。

32 槽与单槽压力两例先完成真实工作写故障/修复/q1重试及取消检查，随后在真实 lease 下准备三个组件。候选 authority 使用已提交 bundle 的完整 owner 图像，与原工作结果逐字节一致。保持准备回复时旧身份不变，每例只有一次 111 共同发布：G1/CP17/journal6 → G2/CP18/journal0；完成消费前 lease 保持。配置仅检查布局、不读 DDR。发布完成后，公开 ap 接口通过原生 reader 拒绝旧 generation 请求，再 GET 六个目标资源及已有 node0/net4754；七次成功 GET 从新窗口读取14个 beat，完整字节重放与回复保持/lease 封锁核验通过。

发布后原 G1 查询镜像导入失败；新 G2 导出40B镜像与 bundle/query.bin 一致，序号下限1保留，成功导入后才释放 lease。真实 q2 正常继续，43 poll/42 expand/176 candidate/122 cost 均对照 CPU oracle；两个共享节点 ref1→2→1→0、42 次 owner probe、两条原生路径拆线通过。全部八路 AXI/最终 DDR 独立重放，原其他 net 状态保留。前缀工作事务与旧已审计完整日志逐字节一致。归档已实际恢复重审，audit 逐字节一致，新增源冻结 results/checkpoint_commit_sources_20261026。

本轮只证明同一上下文 version4/query2/price4 下的正常换代与继续工作。新 authority 节点 GET 已通过公开只读接口验证；普通查询仍访问工作 owner。尚未执行换代后的故障/target reset；保存 path/query/label 与序号下限的 warm 恢复联锁仍待实现和验证。manifest_ready 是外部测试输入，无运行中工作 DDR 快照生产器、通用多 net/overflow、持久化认证/原子提交、综合时序或板卡加速结论。

下一优先完整系统换代后 q2 故障恢复：实际从 G2 authority 修复 owner，target reset 后恢复保存的 q1 路径、查询与标签及下限，再放行业务和重试。研究继续，goal active。

以下保留历史。

# 完整层级元数据准备与取消通过（2026-10-26）

详见 results/checkpoint_system_20261026.json 与 hardware/variants/checkpoint_system_v1/CONTRACT.md。选定 checkpoint_system_v4，将双槽 authority、发布屏障、coordinator/config shadow 通过三个实际层级接入 query_residency_system，沿用原生 checkpoint lease 和真实物理/逻辑退休信号。共同发布许可与新准备请求许可分离，避免 commit 自身关闭 publish_ready。

32 槽和单槽压力两例完成真实查询、owner 写故障、修复及重试，再在实际工作产生的六项 journal 上准备 coordinator/config、保持准备回复、提供路径/查询导入争用、取消、保持完成回复。取消始终保留 checkpoint17、旧 generation 和六项 journal；完成消费后继续成功导出保存路径、查询序号、配置和 journal。两例共 24 文件与既有已审计基线逐字节一致：每例八路 AXI 日志和四份最终 DDR。原生准备/回复/取消/丢弃/完成事件独立核对，保存路径、配置、上下文、journal 与恢复 floor 导出一致。归档已实际恢复重审，audit 逐字节一致；源码冻结 results/checkpoint_system_sources_20261026。

本轮没有准备 authority 候选或在完整层级成功发布；三方同拍提交目前仍只由前轮元数据切片证明。manifest_ready 仍为外部输入。完整换代后故障恢复，尤其 target reset 后保存 path/query/label 与序号下限恢复再放行业务，仍未实现/验证。运行中工作 DDR 快照生产、多 net/overflow、综合/时序/板卡收益仍缺。

下一步在完整层级接入实际 warm authority 图像并验证三方共同提交，再执行换代后故障恢复，完成路径/查询/标签恢复联锁。研究继续，goal active。

以下保留历史。

# Checkpoint 元数据联合发布通过（2026-10-26）

详见 hardware/variants/checkpoint_stage_v1/CONTRACT.md 与 results/checkpoint_joint_20261026.json。选定 checkpoint_joint_v7，真实 lease guard 下，双槽 authority、coordinator checkpoint/journal 和有效配置影子状态由共同发布屏障协调。

205 次检查与独立审计通过。四个事务依次为身份错配、显式取消、配置槽 abort 后部分取消、成功发布，状态 1/2/2/0。前三者保留旧 checkpoint17、generation1 与六项 journal；成功事务只有一次共同发布沿，切至 checkpoint18/generation2 并清 journal。准备回复、旧 GET 回复与完成回复保持时的封锁得到验证。发布后同版本恢复请求被原生 coordinator 拒绝，attempt floor 保留。5 个 GET、8 个 AXI 读 beat 与完整两份 owner 图像独立重放一致。

归档已实际移走原目录后恢复、重新独立审计，audit 逐字节一致。当前源码冻结 results/checkpoint_joint_sources_20261026。

范围仅元数据切片：journal 来自已验证 bundle 六项 delta 的接口输入，没有新执行工作 owner 写；无 route engine，route_retired 固定1，manifest_ready 为测试输入。没有执行真实恢复或原生配置 provider 回调，尚无 path/query/label 联合恢复、运行中工作 DDR 快照生产、多 net/overflow、综合/时序/板卡收益证明。

下一优先将屏障和影子元数据接入完整顶层的真实退休/lease/manifest 条件；验证换代后 q2 故障恢复，在 target reset 后恢复保存的 q1 path/query/label 与序号下限，再放行业务。研究继续，goal active。

以下保留历史。

# 双槽authority组件通过并修复身份回退（2026-10-26，优先历史）

详见 results/authority_rotate_20261026.md/.json 与 hardware/variants/authority_rotate_v1/CONTRACT.md。选定authority_rotate_v6：双原生reader槽、共用串行只读AXI；配置处理阻止GET，准备完成后未publish前仍服务旧槽。发布需两槽退休/无争用/外部许可，单拍切换；held回复、discard和abort行为验证。

真实v5反例：rearm取消使configured=0后，旧包装器允许重初绑，从G2退回G1且无publish。修复首次绑定资格改查保留的bound_generation，服务就绪与身份存续分开。224检查、28GET、7配置+2rearm、45R beat，G1→G2→G4两次publish、原生布局失败/取消/SLVERR、恢复原身份通过。全图像/AXI/独立状态机审核，两归档实际恢复复审一致，源冻结results/authority_rotate_sources_20261026。

初始图像并非空表，其他net已有占用；warm仅新增六个目标资源，所有其他字节不变，已有node0/net4754与六个新资源实际GET验证。G4复用warm图像，仅组件namespace测试。未接全系统，publish_permit为TB输入；无联合journal/config/path/query/label提交/恢复、工作DDR快照生产或新综合/时序/板卡结论。

下一优先coordinator/有效配置影子prepare/publish与真实lease联合提交，再warm换代恢复（target reset后必须恢复路径/序号等才放行）。通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 普通启动回归与新顶层OOC通过（2026-10-26，优先历史）

详见 results/cold_validation_20261026.md/.json。cold_axi_abort_v1明确boot_required=0，与原bundle_capture_v3同TB/输入/CPU/故障：32槽/单槽各14文件（8AXI、4DDR、完整native协议和目录）逐字节一致，28文件；周期836290/893444、repair1一致。

完整U280 OOC 113043LUT/73882FF/160.5BRAM/23DSP；相对bundle_capture增LUT +7588、FF +2840，BRAM/DSP不变。122生产RTL，runtime配置输入保留，零latch/blackbox/file-agent/observer。专用Vivado2022.2 MCP会话关闭；两归档实际恢复复审audit一致，源冻结results/cold_validation_sources_20261026。

本轮仅代表fixture普通启动回归和未约束OOC，不证明形式等价/时序闭合/板卡收益。下一优先运行中authority换代与统一发布，再通用多net/overflow快照。带约束时序/实现、无复位恢复、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# AXI在途取消后的回复退休修复（2026-10-26，优先历史）

详见 results/cold_axi_20261026.md/.json 和 hardware/variants/cold_axi_abort_v1/CONTRACT.md。真实AR受理/R前abort的旧版反例：AXI排空但前端8192周期仍phase2/all_drained1/normal_retired0/backend_idle0。新增16bit已接受host回复归属，abort不清；请求mask继续封锁，回复mask|owned只让旧回复退休，不伪造payload/status。

32槽/单槽各读R、写B在途边界，共四例通过。读数据逐字等于bundle，写cut AW=B+1、退休AW=B；原native读/flush成功完成。旧回复背压8周期，新请求/boot成功仍关闭；完整物理与逻辑退休后才cold reset，同实例不重装外部DDR重建328标签/path/query。旧seq1拒绝、CPU q2 43poll/42expand/176candidate/122cost、42owner probes及refs1→2→1→0通过。全8AXI/最终图像与两归档实际恢复复审一致，源冻结results/cold_axi_sources_20261026。

后续使用cold_axi_abort_v1；旧variant保留历史反例。下一优先普通启动完整回归与新顶层综合/时序，再运行中authority换代。无复位恢复、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 部分恢复流取消通过（2026-10-26，优先历史）

详见 results/cold_stream_20261026.md/.json、hardware/variants/cold_stream_abort_v1/CONTRACT.md和cold_stream_late_v1/CONTRACT.md。生产root/gate与cold_abort_fixed_v1逐字节不变。path39/78、query5/10与9/10中断，32槽/单槽共六例；第一条path整条与query序号下限分别已送达，仍未发布，真实取消status2，错误回复保持8周期业务/lease释放关闭。

query实际S流逐字与bundle比对，部分前缀后同一实例cold reset、不重装外部DDR，完整10字恢复。各例第二轮328标签/路径/序号导入、旧seq1拒绝、CPU q2 43poll/42expand/176candidate/122cost、42owner probes及refs1→2→1→0通过。全部8AXI/最终图像审核通过，两归档实际恢复复审audit一致；源冻结results/cold_stream_sources_20261026。

尚未AXI在途中断或无复位恢复；下一优先真实R/B在途取消及退休、普通启动回归与新顶层综合。运行中authority换代、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 启动完成abort反例已修复（2026-10-26，优先历史）

详见 results/cold_abort_20261026.md/.json、hardware/variants/cold_abort_v1/CONTRACT.md。旧cold_boot_v1在恢复完成回复被保持时未接入abort取消，完整系统复现“abort与消费同拍仍输出成功”。唯一生产差异：gate work_rst(rst||abort)。同一stimulus修复后屏蔽成功、清除资格并保持业务/lease释放封锁；不强制释放可能持有事务的lease。

32槽/单槽在同一实例cold reset、不重新装载外部DDR，第二轮328标签重建与path/query导入成功；旧seq1拒绝、seq2 CPU oracle43poll/42expand/176candidate/122cost及共享refs1→2→1→0通过。全部8AXI重放/最终owner和42probes通过。旧失败与新成功两归档实际恢复复审一致，源冻结results/cold_abort_sources_20261026。后续使用cold_abort_v1；旧variant保留为历史反例。

本轮只覆盖已完全退休的完成回复边界。下一优先导入流/AXI中途中断、普通启动回归及新顶层综合，再运行中authority换代。无复位恢复、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 冷恢复后继续真实查询通过（2026-10-26，优先历史）

详见 results/cold_boot_20261026.md/.json 与 hardware/variants/cold_boot_v1/CONTRACT.md。选定cold_boot_v2：新RTL实例冷复位后从已提交G2/checkpoint18 bundle恢复，真实8配置回执、owner/authority绑定、328标签native重建/CRC/count、path/query导入回执及完成回复消费共同开放业务。修复更新/完成同周期旧资格复活；组件31项检查通过。

32槽/单槽均拒绝合法上下文空闲slot的旧seq1（零prepare/commit），seq2对照独立CPU为43poll/42expand/176candidate/122cost。共享263946/554512 refs1→2，双ripup2→1→0；每例42owner probes，全部8AXI字节重放/最终owner图像通过。周期344879/344954包含恢复/查询/核验/撤销，非加速。两归档527文件实际恢复复审audit一致；当前源冻结results/cold_boot_sources_20261026。

这是capacity0/同网两路径的主机预载参考冷恢复，不是FPGA自主DMA/板卡证明。下一优先：完整系统恢复中断/错误与普通启动回归，补新门控综合；再运行中authority换代与通用多net/overflow快照。持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 新提交代健康边界参考bundle通过（2026-10-25，优先历史）

详见 results/bundle_capture_20261025.md/.json、bundle_capture_coverage_20261025.json 和 hardware/variants/bundle_capture_v1/CONTRACT.md。选定bundle_capture_v3：qc_cp_generation握手锁存目标G2，降低代拒绝，G2导出不激活仍运行G1的authority；合法CRC未来代导入仍拒绝，默认G1重放保持。生产只改query root，目录仅加仿真条件观察器。

同一真实lease下导出query40B/path312B，捕获实际working owner/allocator/design/cost/labels与active/attempt上下文；目录由真实native握手重建120frame/328record，非数组伪造，仍非生产导出端口。新参考checkpoint18/G2吸收6个ref1资源，原实例仍G1/journal6。raw配置3须按实际active4覆盖word70。主机staging/fsync/manifest+COMMIT/rename包校验及24检查通过（2有效、22拒绝），未声称断电或认证/反重放。

两容量各330824322数据字节，13组件11份同字节，目录/标签物理布局不同而328逻辑record相同。完整U280 OOC 105455LUT/71042FF/160.5BRAM/23DSP，增183/88，零latch/blackbox/file-agent/observer；三归档1658文件实际恢复复审一致，23当前源冻结。

本轮是健康静止点/host参考包，尚未冷恢复或运行中换代。下一明确实验：新RTL实例cold reset，按effective4/query2/price4配置G2；真实label IO重建并硬件CRC/count核验；path/query导入实际receipt齐备且完成回复消费后才解除boot业务门控；拒绝旧seq1，再用已有followup_q2 oracle执行seq2并验证warm共享owner1→2、双ripup2→1→0。当前capacity0一路径fixture，不宣称通用多net/overflow快照。生产目录导出、持久化下限/认证、unknown页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

# 查询checkpoint已接入真实系统租约（2026-10-25，优先历史）

详见 results/query_checkpoint_join_20261025.md/.json、query_checkpoint_join_coverage_20261025.json 和 hardware/variants/query_checkpoint_join_v1/CONTRACT.md。两生产组件改写，120生产RTL继承。qc_cp复用实际lease，生产导入受理即pending，只在成功导入回复消费后清除；错误/部分导入及 held成功回复不能释放lease。query/path流互斥，诊断默认关闭。

32/单槽共六例：真实owner B恢复及完整CPU重跑后，局部query状态丢失导入、默认关闭诊断的生产导入、接口闲置。前四例40B导出、坏CRC拒绝、CRC正确但generation高32位错误拒绝、正确重放；旧sequence1以空闲slot/合法上下文提交而被拒绝且零prepare/commit。pending104/88周期。全部8AXI+4图像每例字节同旧基线，共72文件比较通过；不是加速。

完整U280 OOC 105272LUT/70954FF/160.5BRAM/23DSP，零latch/blackbox/file-agent；较旧增1128/577。五归档2585文件实际恢复复审一致，17当前源冻结。仍只丢query控制器，其余状态保留，不是冷启动；cold reset会清pending/lease。

frame的generation绑定旧authority基线，不等于当前working owner的新快照；禁止与初始owner图像单独配对冷恢复。下一优先健康边界pending bundle generation/实际全状态捕获与真实receipt boot门控、原子提交/快照轮换，保存实际active配置与attempt下限，再完整warm-owner冷恢复。未知页/旧prev/frontier、价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

# 查询序号checkpoint组件通过（2026-10-25，优先历史）

详见 results/query_checkpoint_20261025.md/.json、query_checkpoint_coverage_20261025.json 和 hardware/variants/query_checkpoint_v1/CONTRACT.md。新增原生query_lifecycle的10字CRC32快照，保存sequence_seen/last_sequence、design/version/query/price与dirty，绑定generation64。14查询/27checkpoint、实际S/M流和独立状态机/zlib审核通过；冷复位未导入会接受旧序号，正确导入后拒绝且无后端请求。

CRC/身份/规范/次序/last、部分导入、权限/漂移、背压取消、空图像/序号耗尽和原子发布验证。真实旧clean导入清dirty反例已修复：同生命周期sequence及dirty不能回退。开发失败/监视编号审计失败保留。原生组件OOC 1695LUT/1734FF，比原573/1133增1122/601，均0BRAM/DSP/latch/blackbox。四归档235文件实际恢复复审一致，12当前源冻结。

本轮后端为注册mock，新接口尚未接完整query/AXI；上一轮完整系统基线保持。version/query/price只做上下文相等，恢复协调器attempt下限仍未序列化；cold-reset本地floor不能阻止更早可信图像重放。恢复前必须外层admit门控到全部同代状态恢复完毕。下一优先统一描述/发布/快照轮换及完整冷恢复集成，再warm非零owner；未知页/旧prev/frontier、价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

# 通用owner authority已接入完整查询（2026-10-25，优先历史）

详见 results/authority_query_20261025.md/.json、authority_query_coverage_20261025.json 和 hardware/variants/authority_query_v1/CONTRACT.md。选定authority_query_v4/retry_v3，三生产层改写+reader新增，118生产RTL继承。六行表只作正常probe期望值，不再生成authority回复；第八路AXI实际读完整初始owner图像，单快照绑定design64/checkpoint32/generation64。

32槽/单槽共四例owner B故障及其后的snapshot R二次SLVERR，全部恢复并完整CPU重跑。首次二次故障status6/journal1保留，显式新query/version重试修复1项、journal清零；真实328标签写回/核验，非mock。普通故障原七AXI+四图像共22文件与旧基线字节一致；周期835704/892858，二次故障836213/892858，不是加速结论。

修复目标rst误清reader绑定，以及私有rearm仅AXI排空却未逻辑退休的过早target reset，实际反例保留。完整U280 OOC 104144LUT/70377FF/160.5BRAM/23DSP，零latch/blackbox/file-agent。六归档2789文件实际恢复复审一致，19当前源冻结。

仍只有一个绑定初始快照与已知328标签；本轮完整query authority key的初始owner为空，warm非零/overflow仅此前组件验证。统一checkpoint同代发布、轮换、query序号/epoch/version下限冷恢复、未知页/旧prev/frontier、实际价格/回绕/容量/耐掉电/板卡仍缺。下一优先统一描述与恢复下限，goal active。以下保留历史。

# 版本化owner快照与恢复子系统通过（2026-10-25，优先历史）

详见 results/checkpoint_authority_20261025.md/.json、checkpoint_authority_coverage_20261025.json 和 hardware/variants/checkpoint_authority_v1/CONTRACT.md。新增design64/checkpoint32/generation64绑定的通用只读owner快照服务；真实完整primary/pool/allocator图像，两份各9089009节点，第二份53734 overflow。728向量+8错误/重启探针共736回复，含58 overflow查询，非全量硬件穷举。

接既有协调器与真实可写owner引擎，journal先于变更；两例首次snapshot R SLVERR保留3/5项，再以新version/query显式重试成功。验证INC/DEC、overflow引用与primary promotion。独立CPU oracle、全部AXI字节、完整owner语义与未涉及字节一致，allocator一致；iter2内部编码顺序不同。旧fault污染重试的真实反例保留，修复仅安全rearm清暂态，身份/journal保留。

读取组件U280 OOC 4537LUT/3973FF/0BRAM/0DSP，零latch/blackbox；不是全系统资源或加速。五归档269文件实际恢复复审一致，14当前源冻结。labels_done仍mock，完整query top尚未接新authority，旧完整query基线保持。

下一优先统一checkpoint描述绑定路径与全状态，真实labels恢复和完整query接入，序号/epoch/version下限恢复。快照真实性/不可变、外部持久化仍调用方保证；未知页/旧prev/frontier、实际价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

# 路径checkpoint接入系统与真实AXI通过（2026-10-25，优先历史）

详见 results/route_checkpoint_join_20261025.md/.json、checkpoint_join_coverage_20261025.json 和 hardware/variants/route_checkpoint_join_v1/CONTRACT.md。硬件q1/q2完成后，在排空且无既有offer时取得显式lease，封锁16host/query/route/recovery。RTL导出78字→诊断仅丢失路径→坏CRC拒绝→原图像重放/再导出→实际AXI共享ripup refs2→1→0；32槽/单槽均通过。其他backing保留，不是全系统checkpoint恢复。

六派生组件（5改写+1新增guard）、117继承RTL/dat保持。全部入口争用1424周期、持有1425周期，无新增AXI访问，journal10/last_sequence2/配置保持，七AXI和四图像与旧基线字节一致。正常24文件字节一致，周期657222/724963；CPP闲置时两例owner B错误完整恢复重跑。lease26单元含退休后错误释放，未证明真实checkpoint持有期AXI错误接管。

完整U280 OOC 99321LUT/66384FF/160.5BRAM/23DSP，387端口57270位，零latch/blackbox/file-agent，默认诊断关闭。较旧版增10659LUT/2859FF，暂存开销仍高，无时序/板卡收益。五归档1632文件实际恢复复审一致，32源冻结，开发失败和scope文案修正证据保留。

下一优先版本化checkpoint描述绑定路径与owner等全部状态，通用authority读取与query序号/epoch/版本下限恢复。外部路径buffer、同代owner可信前提、仅两slot/MAX_PATH32、未知页/旧prev、frontier重启、真实价格/回绕/容量/耐掉电/板卡仍缺。继续优化暂存多读口。goal active。以下保留历史。

# 保存路径checkpoint组件通过，完整checkpoint继续推进（2026-10-25，优先历史）

详见 results/route_checkpoint_20261025.md/.json、checkpoint_coverage_20261025.json 和 hardware/variants/route_checkpoint_v1/CONTRACT.md。新增两slot路径CRC32导出、逐项/逐对语义校验和原子导入；8/32容量各31路由+27checkpoint检查，真实CPU两同网路径在控制器reset后恢复并ripup共享refs2→1→0，未读label。注册mock后端，尚未接真实AXI/统一围栏，cp_safe和同一owner快照由调用方保证。

三组件OOC LUT12897/13825/12061，选逐对扫描5751FF，零latch/blackbox/BRAM/DSP。固定slot选择负结果保留；较首版减836LUT，但较原2144LUT控制器仍增9917，资源开销较高。三版本两容量事件字节一致，另增满长度合成边界检查；非周期等价/系统资源/板卡性能证明。11归档373文件实际恢复复审一致，20源冻结。

下一优先优化暂存多读口开销并接入系统围栏/真实AXI一致保存恢复；完整checkpoint必须覆盖owner/allocator、design/cache、history/价格、labels/目录、配置、journal和query序号/版本下限。last_sequence当前reset清零，不能只恢复路径；frontier重启边界、未知页/旧prev、真实价格/回绕/容量/耐掉电/板卡仍缺。原研究目标保持，goal active。以下保留历史。

# 保留journal的恢复失败后重试通过（2026-10-25，优先历史）

详见 results/recovery_retry_20261025.md/.json 和 hardware/variants/recovery_retry_v1/CONTRACT.md。业务owner B错误后，恢复owner GET R/DEC B、标签eviction B/CHECKPOINT B/核验R二次真实故障，各32槽/单槽共10例全部在显式新命令下成功恢复并完整CPU重跑。保留journal/authority/配置描述，只在旧回复消费、物理和逻辑退休后REARM清理恢复暂态；新version/query身份拒绝旧尝试。DEC B已实际修复时重试不重复扣减。不是自动重试或完整checkpoint。

协调器39/配置32单元检查、真实七AXI/全图像/完整CPU与第一故障基线前缀审计通过。三生产组件改写、119继承RTL/dat保持；正常双查询共享ripup的24文件与旧基线字节一致，周期657222/724963。完整U280 OOC 88662LUT/63525FF/160.5BRAM/23DSP，零latch/blackbox/file-agent。六归档1442文件实际恢复复审一致，29源冻结，开发失败保留。无板卡加速结论。

下一优先完整checkpoint与未知页/一般reroute。仍q1六行authority/328已知标签、design backing保留、snapshot外部新cookie重放；实际价格未变，回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

# 恢复期间真实二次故障验证通过（2026-10-25，优先历史）

详见 results/recovery_fault_20261025.md/.json 和 hardware/variants/recovery_fault_v1/CONTRACT.md。业务owner B错误后，在恢复owner GET R/DEC B、标签写入eviction B/CHECKPOINT B/核验R注入第二次真实SLVERR，各32槽/单槽共10例，全部通过失败关闭契约。恢复返回错误、实际AXI/回调退休、journal=1保留、回复背压及消费后拒绝业务和新恢复接受。不是二次故障后恢复成功/自动重试。

122继承RTL/dat哈希不变；全CPU查询前缀、七AXI字节、完整图像、owner实际副作用和snapshot计数独立审计通过。DEC B错误物理修复已发生但确认数0，标签失败前owner已修复1仍不放行。623文件归档实际恢复复审一致，9源冻结，验证编译失败保留。本轮无需重综合，无板卡性能结论。

下一优先完整checkpoint和保留journal的恢复失败后重启协议。仍依赖q1六行authority/328标签，design backing保留；cold reset会丢日志，不能当恢复算法。未知页/任意reroute/真实价格/回绕/容量/耐掉电/板卡仍缺，goal active。以下保留历史。

# 搜索错误事务退休修复完成（2026-10-25，优先历史）

详见 results/search_fault_retire_20261025.md/.json 和 hardware/variants/search_fault_retire_v1/CONTRACT.md。选择v6冻结版本：原11例真实AXI故障全部恢复并完整CPU重跑，新增深层graph/cost六例及capture九错误场景通过。修复错误帧/候选下游/coordinate请求/connection元数据取消的退休；保持已暴露握手，要求真实HLS/内部回复/AXI排空。目录memory lease为故障后保留锁，不作为在途事务归零条件；开发反例已冻结。

正常32槽/单槽双查询与共享ripup审计通过，周期657222/724963；24份cycle轨迹/七AXI/完整图像与旧正常版本字节一致。十组件改写、112生产RTL/dat保持。完整U280 OOC 88652LUT/63485FF/160.5BRAM/23DSP，零latch/blackbox/file-agent；五归档1841文件实际恢复复审一致，33源冻结。无route/Fmax/板卡加速结论。

下一优先完整checkpoint与恢复期故障。仍只有初始328标签/q1六行authority受信任、design backing保留；真实价格、未知页、任意reroute、回绕/容量/耐掉电仍缺。新入口run_query_fault.py RESULT --search-fix（--deep深层），run_search_retire_join.py正常；原默认基线不变。goal active。以下保留历史。

# 真实查询故障矩阵与路由退休修复（2026-10-25，优先历史）

详见 results/query_fault_20261025.md/.json。原版真实 AXI 故障11例：5例恢复并完整重跑，6例卡住（graph/cost/owner各两种容量）；独立七AXI字节/全owner/CPU重跑审计通过仅表示结论可信，不能说所有故障恢复通过。源标签R、单槽prepare B、cleanup B可恢复；cleanup已提交6项，先修复6项再重跑。

隔离 query_recovery_v2 仅改外层排空谓词，解决route adapter busy包含锁存fault导致的DRAIN死等；仍要求normal_retired、backend_idle、AXI全排空、search退休，额外接受rc_fault且fence BLOCKED。32槽/单槽owner B错误各1例均修复实际副作用1项（ACK=0）后恢复初始328标签并完整重跑，最终全owner与CPU精确一次提交一致。显式入口run_query_fault.py RESULT --route-fix；旧正常入口与原基线不改，新谓词尚未重综合。

下一优先graph错误的capture/frame/递归完成退休、cost错误的候选链失败退休：两者AXI虽空但内部仍owned，不能跳过退休强制reset。原版反例已保留。完整checkpoint仍缺，q1六owner authority/328已知标签受信任、design backing保留；无未知页/任意reroute/真实价格变化/耐掉电/板卡加速结论。以下保留历史。

# 单命令查询生命周期RTL通过（2026-10-25，优先历史）

详见 results/query_lifecycle_20261025.md/.json 和 hardware/variants/query_lifecycle_v1/CONTRACT.md。基于search_sparse_v3新增source根检查→4次prepare写→真实search→自动route commit→清target→CHECKPOINT/排空，主机只需一条查询命令；全生命周期16host+route围栏。28模型、32槽/单槽真实双query及全CPU/1650host标签写/2713请求/七AXI/全状态独立审计通过，四owner阶段和路径数学保持。每query完成后target=0。120旧资产不改，qc_*避免连接服务q_busy/q_fault重名（首版失败已保留）。

完整U280 OOC 86880LUT/62800FF/160.5BRAM/23DSP，零latch/blackbox/file-agent，358端口/56927位；143源冻结、三归档实际恢复复审一致。周期657222/724963不能与旧682354/745363直接解释为加速，因为移除了328条prepared评分读取且增加清理/刷回；未route/Fmax/板卡。

下一优先真实生命周期故障/恢复交接和完整checkpoint。单sink/空saved-slot、严格递增sequence及固定上下文；初始目标集合受信任，初始328标签/authority/snapshot生产、ripup发令仍外部。取消保持已发VALID，route可能已提交；rsp_committed只是native提交报告，status0才表示完整成功；永久后端停顿仍可不返回，无回滚。journal仍仅route-owner；altSink/任意reroute、非空CLEAR实测、unknown-page、价格/序号回绕/容量/耐掉电/板卡仍缺，goal active。以下保留历史。

# 自主搜索接口资源对照完成（2026-10-25，优先历史）

详见 results/search_optimization_20261025.md/.json。回复静态切片v2仍99477LUT/61700FF（负结果保留）；四路搜索注入v3为86129LUT/61699FF/160.5BRAM/23DSP，较v1减少13348LUT（13.418%），下一实验选`search_sparse_v3`。v3只限制私有scheduler为6/8/11/12，主机16路全保留；无效payload可变，有效事务载荷/控制等价，非法私有lane拒绝。FSM/top/TB不改，每个join120源保持。

两变体各20模型、69632/17420组并行接口比较、各32槽/单槽共4真实运行通过；全部cycle轨迹/七AXI/四图像与独立CPU审计v1字节相同，周期682354/745363。八归档实际恢复复审一致、129源冻结；零latch/blackbox/file-agent，未route/Fmax/板卡，无吞吐加速声明。入口run_search_sparse_join.py显式选v3，旧默认仍v1。

下一优先硬件prepare和search→commit编排；search_prepare_analysis_20261025.json确认当前5次prepare写仅3值变化，不能删去任意source仍需的lb/upstream归零。真实search fault/非空CLEAR、完整checkpoint/unknown-page/价格回绕/容量/耐掉电及板卡仍缺；goal active。以下保留历史。

# 设备侧自主搜索循环与完整OOC通过（2026-10-25，优先历史）

详见 results/search_scheduler_20261025.md/.json 和 hardware/variants/search_scheduler_v1/CONTRACT.md。可综合FSM已接管prepared query的实际堆POLL→标签→expand→目标→CHECKPOINT/排空，16host+route全查询围栏与恢复取消交接。20独立FSM+20组合模型、32槽/单槽两次真实双query及CPU/全状态/七AXI独立审计通过；116POLL/114expand/447判定/293cost/879ACK、四共享commit/ripup保持，117旧资产不改。七AXI/四完整图像与旧版本字节一致；43标签read只忽略字段差异显式检查。cycle为682354/745363（旧683640/747471），非板卡收益。

完整U280 OOC：99477 LUT/61700 FF/160.5 BRAM/23 DSP，零URAM/latch/blackbox/file-agent；342端口/56716位，默认32槽/16384帧。四结果实际解压复审、源闭包与开发失败保留。无place-route/Fmax/板卡。

下一优先宽接口静态切片资源对照（本轮LUT增加19666，约24.6%），然后硬件prepare与search→commit编排、真实search故障/非空目标CLEAR和完整checkpoint。取消/超时保持已发VALID，永久后端停顿仍可能不返回；无search回滚。初始import、query间prepare、route发令、authority/snapshot生产仍外部；CPU已知328标签/120页，table闲置。route-only journal、完整warm/frontier/path/created-cache、unknown-page、价格回绕/容量/耐掉电及板卡仍缺，goal active。以下保留历史。

# 独立服务系统顶层抽取与完整组合OOC通过（2026-10-25，优先历史）

详见 results/residency_system_20261025.md/.json，入口 hardware/variants/residency_system_v1/residency_system.sv、interface.json、CONTRACT.md。13个硬件实例从TB迁出，313逻辑端口/55702接口位；原116组件RTL/dat保持。恢复snapshot描述握手时锁存，故障fixture随后反转输入仍恢复成功。正常默认诊断关闭2例、真实续接2例、route故障恢复10例共14运行及逐cycle/七AXI/四完整图像对比通过，均与抽取前相同。

完整32槽/16384帧U280 OOC 79811 LUT/60324 FF/160.5 BRAM Tile/23 DSP，零URAM/latch/blackbox/文件agent实例；原生Tcl535.115s exit0。5026警告分类保留，含counts/cursors数组落寄存器；未约束/未place-route/Fmax/板卡。综合原会话观察超时后继续至成功，没有重启，已关闭临时综合会话。四归档1628文件实际解压复审audit逐字节一致，收据residency_system_restore_20261025.json；87文件源冻结。

下一优先设备侧search/prepare调度（真实POLL→parent/展开→目标/提交）及完整checkpoint；现有服务组合已独立，但外层搜索/authority/snapshot生产仍TB或外部，宽接口尚需总线包装。仅route owner修改journal，legacy写和完整warm/frontier/path/created-cache未覆盖；CPU已知328标签、table闲置、恢复期真实fault、unknown-page、价格回绕/容量/耐掉电及板卡仍缺，goal active。以下保留历史。

# 事务围栏正常搜索与真实续接回归通过（2026-10-25，优先历史）

详见 results/transaction_fence_normal_20261025.md/.json。静态 fence/13 retired_idle 导出/journal 与恢复组件 RTL 不改，两套真实双查询激励各32槽/单槽共4运行及独立CPU/完整图像/AXI审计通过：116POLL/114expand/447判定/293cost/879ACK，四阶段共享refs1→2→1→0、occupancy按net计。3032普通请求逐载荷/退休核对，续接版3036；每query真实center HLS+cost AXI两个子回复背压7周期，前端父回复先消费、后端上下文保留至子回复退休。六AXI实际活跃，table无流量。

相较围栏前，路由语义、四完整图像与七AXI文本逐字节相同；整段仿真周期32槽680767→683640（+0.422%），单槽743652→747471（+0.514%），包含journal/恢复组件整体开销，非板卡结果。两份归档916文件实际解压复审逐字节一致（transaction_fence_normal_restore_20261025.json）；73文件冻结及开发失败日志保留。下一优先完整可综合top与自主search/prepare、legacy写日志/完整snapshot；初始化authority仅q1六行，本轮未恢复，不能推广到第二query或任意写入恢复。恢复期fault、table活跃、unknown-page、实际价格/回绕/容量和板卡仍缺，goal active。以下保留历史。

# MCML真实查询RTL与parent缓存对照通过（2026-10-25）

第二个真实设计vtr_mcml已完成原图导出、完整输入codec、独立成本/过滤oracle，以及未优化/parent_upstream_v1变体各32槽和单槽的四次actual closed-loop RTL运行。机器证据 results/mcml_parent_upstream_20261025.json；阶段分解 mcml_stages_baseline_20261025.json 与 mcml_stages_cached_20261025.json。主结果 mcml_query_baseline_v1、mcml_query_cached_v1，默认基线源码保持不变。

## 原始数据与独立oracle

mcml_graph_v1包含14991410节点、66907822原始边、max_degree16。全部offset/edge/32B属性由原RRT无损拆分，原CPU Router loader逐字段全量比较，独立按RRT1语法重组后的SHA仍68431e9730197f0b89c4b287822a5d7360f4df0478955eb0556212121dab6577。借用的是已冻结原Router loader源码，不是借用logicnets的图内容或通过结论。图和节点编号未裁剪/重映射。

mcml_query_inputs_v1从已通过MCML真实首查询快照恢复搜索：connection_index89391/id227074、net28747、source41486、sink41981、fanout391，bbox x[26,33]/y[40,52]；cross=0、landmark=0、pruning=0。全部14991410节点design/owner/history/native label和224819个CPS1连接记录独立核验，224819个初始sink引用保留。cost price_offset59965696、net_offset59966720，rows311/columns0；initial overflow/cache为空，capacity0适用且非空时导出器拒绝。178个实际成本包的4094输入字与890结果字全部按binary32独立重算。

mcml_query_oracle_v1从原CSR重新执行eager getChildren、exclusion、access、visited与target条件：81次扩展，418原始边→327完整children→326实际判定。177普通push+1target；50visited跳过、40graph-access拒绝、56非目标exclusive sink拒绝、2bbox拒绝。178个成本child类型为NON_LOCAL109/LOCAL_BOTH4/LOCAL_EAST64/EXCLUSIVE_SINK_EAST1。217个created变化与CPU全快照一致，根前保守标签读取范围282节点/114页，所有字面字段实际经host接口导入。

## 自然EARLY结束语义

最后parent2178064处理target41981后触发actual CLEAR；完整捕获children中仍有child124201。该child已参与getChildren构建副作用，但没有进入metadata/access、输出或prev/cost提交。四次运行均保持327个捕获children、326个判定/输出，不以少一个child当作丢数据，也不替CPU额外执行它。测试台下一parent始终由actual heap POLL给出；CPU事件仅评分，不供应搜索顺序。

各运行实际82POLL、81expand、326metadata/access/visited、178geometry/cost/OFFER、534有序成本ACK与178次child.prev写；source种子OFFER另计，State读81次不变，没有叠加State缓存。四次完整282条native读回及全部16384帧/3145728B后备、239862592B design、owner/cost文件通过逐字节审计。labels.bin SHA四次均5930e7dd4320d36664df282f4bc423aa6ca86696cf8f80d25e97d308dc159b73。由最终硬件读回prev链得到sink→source：[41981,2178064,3520228,2162154,1981148,845929,340802,41486]，与CPU8节点路径长度一致；这是读回推导，不是已经新增硬件backtrace控制器或owner提交。

## 相同输入与工作量对照

| 配置 | 基线总周期 | 缓存总周期 | 总周期下降 | 基线POLL窗口 | 缓存POLL窗口 | 窗口下降 |
| --- | --- | --- | --- | --- | --- | --- |
| 32槽 | 469637 | 465321 | 0.92% | 351913 | 347616 | 1.22% |
| 单槽 | 509553 | 463766 | 8.99% | 420424 | 374501 | 10.92% |

parent原生读取178→59，复用119次，child.prev写178次保持。完整功能事件payload（去除周期）、cost packet、ACK、队列顺序与最终所有状态逐字一致；新变体只替换post模块一份生产RTL，其余108份RTL/dat保持，TB源文件在两组相同，PARENT_CACHE define只改变读次数检查器。

| 配置 | 标签AR基线→缓存 | 读拍基线→缓存 | 写B基线→缓存 | 写拍基线→缓存 |
| --- | --- | --- | --- | --- |
| 32槽 | 311→310 | 915→912 | 210→210 | 615→615 |
| 单槽 | 940→699 | 2781→2067 | 412→290 | 1209→852 |

单槽减少238个192B页读和119个页写，共68544B；AR/B因4KiB拆分不能直接当页数。post阶段单槽74243→43781，三标签提交32239→16299，geometry+cost保持78904周期。post与提交节省46402周期，略大于净窗口节省45923，其他阶段握手相位差抵消一部分。只报告同模型下实际区间，不把所有差异假设成一个固定读延迟。

已有logicnets首query窗口改善为32槽1.44%/单槽12.07%，MCML是1.22%/10.92%，两个真实设计各一个query支持帧内复用能减少本路径重复读取。它们仍都是初始价格、无landmark/crossSLR的小查询，不是全设计布线、拥塞重路由分布、吞吐或板卡加速证明。窗口含TB POLL标签观察、输出背压，外层循环仍为测试台调度。此前同一post缓存OOC路后代价+107 LUT/+166FF/+18CARRY8及10ns内部时序结论可引用，但不是本整套MCML链的资源/Fmax。

## 范围与后续

本轮label导入范围由CPU真实轨迹及独立oracle预先得到，用于有限窗口的等价验证；生产路由不能依赖事先知道未来读取集合。尚未证明未知工作集的按需默认初始化/完整初始prev适配，也未解决跨query保留prev与清除距离有效性的所有语义。不能把这组输入codec和闭环仿真表述为可直接部署的完整器件后端。

下一优先应进入多query和价格生命周期：采集后续query、非空owner引用/overflow、真实历史标签，明确unknown-page与旧prev的初始化/持久规则，并让冷/热路径和完整身份失效可重放；扩展owner池codec时保留边界与拒绝策略。继续保持parent缓存只在排他decision lease内有效，!decision_lock即清，不能把State只读缓存的跨lock-gap规则套过来。然后将外层search/backtrace/owner提交移到实际控制器并测板卡；默认基线不提升，goal active。

## 保存与验证

脚本export_mcml_graph.py / audit_mcml_graph.py、prepare_mcml_query_inputs.py / audit_mcml_query_inputs.py、verify_mcml_query_filters.py、run_mcml_query_rtl.py、audit_mcml_query_rtl.py、analyze_mcml_stages.py、compare_mcml_parent_upstream.py和TB生成器/源码固定于mcml_query_sources_20261025。MCP既有B session/PID147904、Vivado2022.2，基线179.363s/缓存172.855s，均exit0；收据mcml_query_completion_20261025.json。run.py check也通过，其范围仅文件/配置，功能结论来自上述审计。

完整归档位于offer_archives_20261025：graph21文件/290713158B，inputs43文件/20889764B，oracle4文件/3662B，baseline437文件/12027893B，cached437文件/12039853B。五根scratch均实际移开到.preserved后解包逐成员SHA核验；两份阶段JSON与比较JSON重建逐字节一致，凭据mcml_query_restore_20261025.json。依赖MCML原始RRT、CPU捕获/replay、原基线源码与父值缓存边界证据仍按各自索引保存。


# Parent upstream缓存的物理代价对照（2026-10-25）

已将未改基线postprev_inputs与隔离parent_upstream_v1缓存变体，在同一Vivado2022.2、xcu280-fsvh2892-2L-e、10ns research_clock和Default综合/布局/布线流程下完成模块级OOC对照。两者都包含相同8份实际center服务/算术RTL，只改变post模块一份源码；默认MAX_CYCLES=1048576与实际集成实例相同。机器证据 results/parent_physical_20261025.json，主结果 parent_physical_v2，审计scripts/audit_parent_physical.py。

| 阶段/资源 | 基线 | 缓存 | 增量 |
| --- | --- | --- | --- |
| 综合 LUT | 2620 | 2729 | +109 |
| 布线后 LUT | 2576 | 2683 | +107 |
| FF（综合/布线后相同） | 1951 | 2117 | +166 |
| CARRY8（综合/布线后相同） | 123 | 141 | +18 |
| BRAM / DSP / latch | 0 / 0 / 0 | 0 / 0 / 0 | 0 |

这是post+真实center子模块的代价，不是整套路由引擎面积。综合与实现LUT数分别报告，不把综合109与路后107混用。此前同自然query的仿真POLL窗口改善仍为32槽1.44%、单槽12.07%；本轮未重新测系统吞吐或板卡性能。

| 布线后检查 | 基线 | 缓存 |
| --- | --- | --- |
| WNS（10ns内部约束） | +2.847ns | +2.786ns |
| WHS | +0.041ns | +0.042ns |
| TNS / THS | 0 / 0 | 0 / 0 |
| setup / hold / pulse-width失败端点 | 0 / 0 / 0 | 0 / 0 / 0 |
| routable / fully routed nets | 3583 / 3583 | 3783 / 3783 |
| routing error / DRC violation | 0 / 0 | 0 / 0 |

两者有约束的内部寄存器路径在10ns检查下均满足。最差setup路径均在相同center算术层级中，但端点不同；单次布局的61ps slack差不能当作普遍Fmax变化。没有frequency/placement seed扫参、post-route功能仿真或全加速器实现。

限制必须保持：XDC只有研究时钟，没有外部input/output delay，也没有HD.CLK_SRC假定。两者check_timing均报告939个no_input_delay和771个no_output_delay；methodology文本各列1000项TIMING-18，未waive或禁用。不存在no_clock/unconstrained_internal_endpoints/loops/latch_loops，仍不能将模块内部10ns通过称为平台I/O时序闭合或板卡Fmax。真正集成时需要连接上下游、确定时钟/外部预算后重新布局布线。

流程兼容性：读取Ross vivado-timing-methodology-checks后确认其要求2026.1+；本机help已验证2022.2只支持report_methodology文本-file，不支持示例-json，按本机功能取报告。读取TIMING-18参考并保留未约束I/O的诊断，不编造预算。最早parent_physical_v1在综合前因不存在的redirect命令停止，v2使用报告-file与普通Tcl milestones，失败run/manifest固定parent_physical_failure_20261025。源脚本和审计器固定parent_physical_sources_20261025。v2路径TSV原始分隔符是字面\t，审计显式规范化为tab后解码，原报告不修改；2022.2 Timing Summary与utilization的器件/状态标题格式不同，审计分别按真实格式和完整route状态核验。

已有B MCP会话/PID147904执行source，300s观察返回running后继续同一命令，没有重启；最终exit0/467.116s。完成后无project/design打开并恢复原工作目录。收据parent_physical_completion_20261025.json。根归档57常规文件/12929233B，包含综合/placed/routed DCP和全部报告，逐压缩成员与共享盘copy SHA验证，实际移走scratch后恢复；恢复凭据parent_physical_restore_20261025.json。

并行工作：第二个真实设计MCML的首查询已完成全节点快照与原CPU精确恢复搜索，详见natural_mcml_query_20261025.md/.json。它还没有MCML RTL/parent缓存收益，下一优先为导出MCML原CSR/输入codec、独立geometry/cost/filter oracle，测试自然target EARLY之后剩余一个child的drain；随后再扩大多query与不同生命周期覆盖。仍保留默认基线，完整可综合search loop、backtrace/owner提交和板卡端到端比较未完成，goal active。


# 第二个真实设计MCML：自然查询快照与CPU恢复搜索（2026-10-25）

results/natural_mcml_query_v1与natural_mcml_query_replay_v1通过独立审计；汇总natural_mcml_query_20261025.json。全MCML原串行48轮路由输出与冻结matrix/vtr_mcml_serial_original_p0_r0.result逐字节相同（SHA a74c8a1b190c70559adf0dbb686ca4d55e786fda2d55c7928e2dbb534faa30ec），overused=0、totalPushes390136023保持。观测源码反向删去增量后逐字节恢复原始源码。运行时间只作收据，不是加速实验。

选择实际attempt/sequence1，connection_index89391/id227074、net28747、source41486、sink41981、fanout391，bbox x[26,33]/y[40,52]，cross=0、landmark=0。快照取在原prepare的rip-up/target setup/source seed之后，结束于search循环之后而不是owner commit之后。全部14991410节点前后11字字段、初始owner溢出、cache、256价格、State、初末heap和完整事件均保存。

实际81扩展、327个完整filtered children、326次候选判定、178次搜索内push（加source为179）、82次POLL；178个label记录变化，217个created变化，1次target CLEAR。自然最后parent2178064处理目标后仍有child124201没有进入判定，因此K比C多1；这个差异是原算法EARLY行为，不是截断。后续RTL应构建/捕获完整children并静态drain剩余项，不能额外访问/提交它或忽略其已经发生的created副作用。

独立恢复驱动使用同一原RRT、保存的真实标签/owner/cache/prices/State和原search循环/Router方法；全部9个采集文件逐字节一致，包括两个全节点快照和所有事件。audit_natural_mcml_query.py还独立重放真实8叉heap与CLEAR、每条候选标签读写顺序、全部节点最终标签以及history/owner/occupancy保持。成本数值在这里仍是原CPU观测，未独立重算，也没有MCML硬件codec、RTL、父值缓存收益或板卡性能结论。

源脚本run_natural_mcml_query.py、run_natural_mcml_query_replay.py与审计/汇总器已固定parent_physical_sources_20261025。CPU8执行，清理RW_/B_和LD环境后使用与冻结串行实验相同的显式环境。capture归档26文件/23085084B，replay归档29文件/16674423B，位于offer_archives_20261025。两根目录实际移开到.preserved后解包核验全部成员，汇总重建逐字节一致，恢复记录与physical对照同在parent_physical_restore_20261025.json。

下一步独立导出这个MCML RRT的全图CSR/属性和设计输入，再重算成本/过滤，基线与父值缓存按同一自然closed-loop TB对照。不能沿用logicnets固定节点数、identity、bbox、326/327计数或其111页读取范围。


# 帧内parent upstream复用通过（2026-10-25）

同一真实logicnets首查询中，隔离post模块将parent upstream原生读取从171次降至58次，复用113次；32槽和单槽均通过完整CPU成本/队列/标签/设计状态与AXI字节审计。原State reader仍每查询72次读取，没有叠加前轮State缓存。机器比较 results/parent_upstream_20261025.json，阶段分解 parent_upstream_stages_20261025.json，递归回归 parent_upstream_recursive_regression_20261025.json。

| 配置 | 基线总周期 | 新总周期 | 总周期下降 | 基线POLL窗口 | 新POLL窗口 | 窗口下降 |
| --- | --- | --- | --- | --- | --- | --- |
| 32槽 | 430263 | 425737 | 1.05% | 311297 | 306813 | 1.44% |
| 单槽 | 470003 | 424330 | 9.72% | 378601 | 332917 | 12.07% |

POLL窗口严格为首次实际heap POLL到目标POLL，仍包含TB每次POLL后的host标签观察和输出背压；总周期还含初始化、检查点、最终读回。两类周期分开报告，不把总周期差冒充纯搜索收益，也不跨配置按总周期说单槽优于32槽。slave为同一确定性行为模型，时间相位会随请求提前而变化。结果仅是单自然查询的行为仿真cycle改善，没有板卡运行、Fmax、资源或能效测量。

## 机制与合法范围

变体 hardware/variants/parent_upstream_v1/postprev_inputs.sv，由derive.py从未改candidate_postprev_v1/postprev_inputs.sv精确派生。原EARLY CLEAR→child.prev写ACK顺序保持。随后若当前排他decision lease内已读过同parent upstream，直接复用该32bit值；否则发原native field1读，并只在成功且present、parent!=child时填充。后继fresh geometry/center/cost和lb/upstream/visited三ACK、实际OFFER不改变。

缓存键为parent32、query2/price4、完整version32/design64，值32bit。!active、!decision_lock、context变化、fault/reset均失效；parent切换或child写入缓存parent也失效。自别名parent==child既不命中也不填充。与State缓存不同，正常lock gap必须失效，因为gap内host可以合法修改父标签。absent父记录不缓存，避免以后创建仍返回旧零值。

集成前提：整个lease内禁止其他主机/上下文改标签；实际搜索中parent已经visited，允许的cost写目标只能是当前child，不能任意改parent upstream。现有query core围栏和原访问判定提供这个条件。模块不是带任意外部写一致性侦听的通用标签缓存；如果解除围栏或引入并行写者，必须重新设计失效协议。缓存存储复用也不表示跨价格版本的距离有效。

## 功能、流量与阶段审计

主结果 results/parent_upstream_query_v2：73POLL、72expand、271metadata/access、171成本/OFFER、513有序ACK、171次child.prev写保持。parent_trace.txt独立匹配每条CPU成本顺序，58个有成本parent首次各读一次；同帧其余113次无parent read。全部成本23输入/5输出、语义事件payload（除时间戳）、308最终native记录、111有效页/全部16384个物理帧、145424192B design和完整owner/cost结果等于未优化基线。109份生产RTL/dat中只替换一份postprev文件，其余108逐SHA不变；State、访问、成本、heap和图服务不改。

| 配置 | 标签AR基线→新 | 标签读拍基线→新 | 写B基线→新 | 写拍基线→新 |
| --- | --- | --- | --- | --- |
| 32槽 | 257→257 | 747→747 | 188→188 | 549→549 |
| 单槽 | 802→575 | 2364→1686 | 387→273 | 1143→804 |

单槽减少226次192B页读与113次页写，共65088B标签总线传输；AR/B受4KiB分割影响，不能直接乘3。32槽标签外存流量不变，仍省原生读/控制等待。阶段观测中，32槽post区间35255→31713，单槽72088→42431；单槽三标签提交31437→16027，geometry+cost保持78230周期。单槽窗口少45684周期，其中post与提交区间合计少45067；这与避免child.prev→parent read→child commit的单槽页切换相符。其他微小差异由事务时序相位改变，不将每项都强行归为单一算术延迟。

审计 scripts/audit_parent_upstream_query.py 复用完整原CPU/全字节验证并严格核验唯一RTL派生；compare_parent_upstream.py另逐条核验parent请求、所有功能事件payload和最终文件；analyze_parent_upstream_stages.py给出无缝、无重叠的观测区间。未修改原通过目录或把CPU预定parent注入DUT，下一parent始终来自actual heap POLL。

## 边界与递归回归

results/parent_upstream_bounds_v1：实际post及center算术模块，native/geometry/frontier为明确响应模型。21项检查全部通过，15次parent读、21次prev写、1次EARLY CLEAR；包括cold/hit、lock gap内合法host改值后重新读取、parent切换与返回、version高位/price/query/design切换、inactive、两次自别名及后续caller改父值、absent后创建、EARLY命中仍CLEAR、warm写错误停止、timeout/abort排空后错误、late drift背压时响应保持。不是集成AXI故障恢复或任意并行上下文证明。

results/parent_upstream_recursive_v1补跑原0->{1,2},1->{2}合成递归联合用例，32槽/单槽均通过原始CPU成本、子帧读取刚提交parent upstream、祖先visited跳过、完整字节审计；周期37242/38150与原相同。这两个成本各来自不同parent，因此不增加同父命中覆盖；更深递归、祖先恢复后再次允许成本分支仍需独立补测。

MCP既有B session/PID147904、Vivado2022.2：自然162.433s、边界12.699s、递归72.884s，全部exit0。首轮v1仅TB变量声明在使用后引起VRFC10-3380，移动到module顶部后运行v2，post RTL未因此变更；失败manifest/log/TB留在 parent_upstream_compile_failure_20261025。实际源码、生成器、TB和审计依赖固定于 parent_upstream_sources_20261025；终态收据 parent_upstream_completion_20261025.json。

归档offer_archives_20261025：query_v2为437文件/10651299B，bounds_v1为257文件/1155907B，recursive_v1为429文件/8369946B。三根scratch全部实际移开到.preserved后解包逐成员SHA核验，阶段分析和比较JSON重建逐字节一致；凭据 parent_upstream_restore_20261025.json。原图/自然输入/oracle和旧基线仍按各自索引保存。

下一步先量化该可选变体的综合资源/Fmax代价，再扩展到MCML与多查询、更多label页工作集，以及祖先恢复再次命中的递归场景；确认收益不只限这个单槽对照后再考虑默认接入。继续保留State驻留“减流量无时延收益”的负结果。完整可综合search loop、backtrace/owner提交、多价格有效性、真实板卡和CPU端到端公平比较仍未完成，研究goal active。


# 自然搜索阶段归因通过：State不在等待链上（2026-10-25，优先历史）

本轮在不改109份生产RTL/dat的前提下，仅给真实自然搜索TB追加只读时间戳。32槽/单槽实际Vivado2022.2 XSim均通过，原natural_trace.txt（含周期）、完整design/label/owner/cost及全部AXI字节日志逐SHA等于已通过基线。主结果 results/natural_stages_v1；primary audit scripts/audit_natural_stages.py；精确区间分析 scripts/analyze_natural_stages.py → results/natural_stages_20261025.json。不是更换CPU oracle或减少实际工作量。

测试台 hardware/variants/natural_stages_v1/tb_natural_stages.sv由build_tb.py生成，新增stage_trace.txt。72组expand/State request/reply/meta-ready、271组metadata reply/access decision、171组prefetch/post/geometry-cost/三标签commit/OFFER request与首次valid全部齐全。所有新探针只读，无force/backdoor/信号驱动。通过原成本、队列、标签、全页后备和design语义审计后，再断言每个阶段identity、先后顺序及区间无缝连接。

分析窗口严格取实际首次POLL到目标POLL，32槽311297周期、单槽378601周期。所有时间被划成互不重叠的20类区间，逐段连续且总和恰等于窗口，没有把并行State读再次加到总时间。窗口包含TB每次POLL后的真实host标签读取、扩展调度、输出背压等验证开销，因此不是纯硬件自主search controller吞吐。下面是服务级elapsed区间，包含服务自己的握手/访问，并非纯算术或STA时钟关键路径。

| 阶段 | 32槽周期 | 占窗口 | 单槽周期 | 占窗口 |
| --- | --- | --- | --- | --- |
| geometry+cost服务 | 78230 | 25.13% | 78230 | 20.66% |
| children构建到结果握手 | 69972 | 22.48% | 73035 | 19.29% |
| access判定 | 62944 | 20.22% | 65856 | 17.39% |
| prev/geometry/center准备 | 35255 | 11.33% | 72088 | 19.04% |
| metadata | 24237 | 7.79% | 24167 | 6.38% |
| 三标签提交 | 14934 | 4.80% | 31437 | 8.30% |
| owner/history/price/net预取 | 12080 | 3.88% | 11673 | 3.08% |

其余区间（POLL标签观察和expand admission、结果到POLL、heap OFFER、输出退休/派发等）在JSON完整列出。geometry+cost共171次，各390..486周期；没有证据把整个服务区间都归为浮点算术。首组到末组State实际request→reply32槽4..21周期、单槽4..20周期；q_meta_valid最迟仍分别早于对应children结果561/572周期，范围561..2003与572..2181。JSON中seal命名的margin实际锚点是ce_result握手S，并非后继帧capture封存握手；metadata消费还在S之后。由此直接验证当前State读完成早于候选消费，结合上一轮72→1但所有事件周期不变，不能把State流量减少称为加速。

单槽窗口比32槽增加67304周期；其中prev/geometry/center准备增加36833、标签提交增加16503，两项共53336、占差额79.25%。TB的POLL标签观察与admission区间另增加8470；children增加3063、access增加2912。metadata/预取有小幅负差，属于同一确定性slave握手相位变化，不把所有阶段都当单调容量收益。该对照只有SLOTS变化，逻辑工作量和最终字节一致；未测板卡、不外推速度或能效。

下一优先候选是**当前扩展帧内的parent upstream复用**。真实171个成本调用只涉及58个有成本候选的parent，同帧parent upstream raw bits完全相同，且该帧内没有child push写回当前parent；潜在重复parent读113次。证据 results/natural_parent_upstream_candidate_20261025.json绑定真实输入审计。这只是可测假设，尚无parent缓存RTL或收益。缓存应只活在decision lease内，在!decision_lock、parent/context切换、fault/reset时失效；query间或扩展间允许host标签写入，不能套用上一轮State缓存“不随正常lock gap清除”的规则。后代递归和恢复父帧必须重新核验，不能复用陈旧距离标签。仍须保持child.prev写入、upstream读取/缓存、geometry/cost和三ACK/OFFER因果顺序。

建议下一轮用隔离post模块实现该帧范围复用，并保留未优化自然基线；实际验证parent读次数、所有cost/native/design/heap和总周期。只在真正命中同帧父值时省读，cold/新parent/锁间隙与外部写入必须重新读，补身份/背压/取消测试。不要仅因113次重复计数就预设会加速。geometry+cost和children/access仍占多数，必要时再拆内部等待；State缓存资源代价、多查询/MCML、完整自主search/backtrace/owner提交与板上测量仍未完成，goal active。

持久化：natural_stages_v1归档435常规文件/10618855B，位于results/offer_archives_20261025；所有压缩成员和copy SHA核验。原scratch实际移到.preserved后恢复435文件，分析JSON重建逐字节一致，凭据 natural_stages_restore_20261025.json。审计/分析/TB生成器和依赖固定在 natural_stages_sources_20261025。B MCP同PID147904、exit0/169.774s收据 natural_stages_completion_20261025.json。没有生产RTL改动、没有新工具功能或新HLS生成，本轮只是只读归因。

# 查询级State驻留验证：读流量72→1，周期不变（2026-10-25，优先历史）

同一自然logicnets首查询、同一TB和全部既有真实输入，在隔离variant中加入一行64B State缓存后通过32槽/单槽实际XSim。结果 results/natural_query_resident_v2，边界回归 connection_resident_bounds_v1。比较证据 results/query_residency_20261025.json（compare_query_residency.py），两个主审计 audit_natural_query_resident.py、audit_connection_resident.py。原109份生产RTL/dat中只在冻结新实验的params/connection_state_reader.sv替换一份，108份逐SHA保持；基线目录与原connection_state_v1源码未改，不自动提升为默认实现。

| 项目 | 基线32槽 | 驻留32槽 | 基线单槽 | 驻留单槽 |
| --- | --- | --- | --- | --- |
| State 64B读拍 | 72 | 1 | 72 | 1 |
| 仿真总周期 | 430263 | 430263 | 470003 | 470003 |
| 首次到目标POLL周期差 | 311297 | 311297 | 378601 | 378601 |

每配置少71次读/4544B，非State的完整natural_trace.txt（含逐事件周期）逐字节一致，design/labels/owner/cost完整文件和graph/design/label/owner/cost/table所有AXI字节日志均逐SHA一致。qstate日志恰等于原日志第一组AR/R，其他71组消失。73POLL、72expand、271candidate、171cost/commit/OFFER、513ACK、308最终记录和111物理有效标签页保持。没有仿真搜索时延改善；这与State读取被并行扩展准备所覆盖相符，但尚未做受控memory latency扫参或实际板上性能测量，不能宣称加速、能效改善或板卡收益。

实现 hardware/variants/connection_resident_v1/connection_state_reader.sv，由derive.py从未改基线精确生成。缓存完整512bit State，不缓存任何距离/visited标签。key核验query2bit/price4bit、完整version32/design64、connection/net/sink/cross、configured profile revision32。原bad_request/bad_identity检查仍先执行，原row/RID/RRESP/RLAST/timeout/drift/abort及排空保持；仅在所有检查通过的R回复填充一行。命中重新回显本次cookie/身份并提供独立稳定响应。表在configured生命周期不可变，不能绕过所有者在后台修改后备。

query inactive、上下文或revision变化、任何fault/abort均清cache_valid；rst也清。decision_lock正常在父扩展之间下降不失效，但请求和未退休响应仍沿用原锁/身份约束。新connection/net/sink/cross键不匹配会走原实际读与原row检查，未把某次缓存有效当作新请求合法。配置revision只允许冷复位后重新配置，测试revision2复位后首次miss。没有改变标签生命周期或价格版本距离有效性规则。

独立边界TB保留原182个真实row及fault/drain回归，并增加无AR命中、cookie更新、lock-gap复用、query关闭重开miss、版本高16位变化miss、price/query变化miss、warm-cache错误net/sink/cross实际读后拒绝、profile冷重配、64bit design错误无AR拒绝、缓存响应背压期间late drift保留原响应且fault停止。终态CONNECTION_RESIDENT_PASS successes=195 errors=11 AR=199，所有195条完整row独立匹配原180326行表；错误/timeout/abort排空保持。不是并行多context或热profile修改证明。

MCP已有B session/PID147904、Vivado2022.2：自然两组166.122s/exit0，边界10.265s/exit0。最早natural_query_resident_v1因生成器拼接endend编译失败，修正end后空格才运行v2；原失败manifest/log/reader固定在 results/query_residency_compile_failure_20261025，未改已通过基线或通过产物。最终源码/derive/TB/runner/审计依赖固定在 results/query_residency_sources_20261025；终态收据 query_residency_completion_20261025.json。没有新增工具版本要求，无新HLS内核或厂商补丁。

持久化：offer_archives_20261025/natural_query_resident_v2.tar.gz为433常规文件/10585397B；connection_resident_bounds_v1.tar.gz为33文件/98754B。压缩成员与共享盘copy SHA核验，两个scratch目录实际移开到.preserved后解包恢复，完整对照JSON重新生成逐字节一致；凭据 query_residency_restore_20261025.json。依赖原自然输入、oracle、graph和baseline仍按各自索引保持。

下一步优先测真实自然搜索的关键等待：State驻留已经减少流量但没有时延收益，不能继续把重复读取计数当加速依据。先用不改生产行为的观测TB拆出图/首次过滤、metadata/access、几何/成本、标签提交与队列等待，确认State miss完成相对扩展/metadata消费的时间；必要时受控总线延迟扫参。再按关键路径选择设计/查询级驻留，保留动态created/cache/owner语义和同一自然oracle。这个可选缓存尚未综合/布局布线或量化资源开销，若保留需补资源代价；完整可综合search controller、backtrace/owner commit、多查询/MCML/价格版本与板卡性能仍待完成。goal active。

# 首个自然查询RTL闭环搜索通过（2026-10-25，优先历史）

实际Vivado2022.2 XSim在已有B MCP会话 vivado-20261023-140925-d95d4d2b（PID147904）完成32槽/单槽两次主运行，exit0/166.75s。结果 results/natural_query_rtl_v1；机器汇总 natural_query_rtl_20261025.json，终态收据 natural_query_rtl_completion_20261025.json，独立审计 audit_natural_query_rtl.py + audit_natural_axi.py。本轮只加测试台/运行/审计，109份生产RTL/dat与既有通过基线逐SHA一致。

输入仍为真实logicnets首查询：connection_index16506/id37267、net2717、source65185、sink150697、sequence1，实际bbox与64B State、owner/history/价格保持。全图9089009节点/40469536边来自已审计原CSR/RRT32，不改成小图，不设置合成占用或target。host接口实际逐字段导入308条字面标签，再将原prepare已seed的source以实际heap OFFER入队。query/price/version=1/3/3和design_id为TB身份编码，不是从CPU推断的价格版本；实际price table/present-factor保持CPU快照。

新TB hardware/variants/natural_query_v1/tb_natural_query.sv（build_tb.py生成）让actual heap POLL返回node成为下一次expand_parent，每次POLL后通过真实host label读target位来决定停止。CPU P/C/cost文件只作断言评分，不供应下一parent或候选。POLL→实际graph/design首次过滤→metadata/access→geometry/cost→native提交/三ACK→actual OFFER→target EARLY内部CLEAR均通过现有实际链；外层POLL/扩展调度目前是TB顺序逻辑，不是新增可综合的自主search controller。仍未执行backtrace/saveRouting/owner commit/target cleanup。

两配置各73次真实POLL、72次扩展、271次metadata/access/visited判定、171次实际geometry/cost、171组成本提交/513有序ACK与171次成本OFFER；source种子OFFER另计。382条原始边与271条候选的顺序等于原CPU，自然目标出现一次EARLY，实际内部CLEAR使用frontier op5（op3是PEEK），然后目标以40267287出队并停止。关闭前对308条完整native记录逐字检查。整个扩展期间同时排队CLOSE和host label/design/owner请求，围栏保持，内部CLEAR/OFFER继续完成。

完整持久状态独立审计：145424192B design结果与原CSR、CPU逐候选时刻标签/created及过滤重新推导的全部字节一致；72个缓存发布、202个新created。CREATE对24个raw已created sink也设置冗余store.created位，这是幂等getOrCreate的实际结果，不是新建计数24；运行时created始终raw OR store。主owner+allocator145424256B及cost36804480B保持；全部物理标签3145728B的16384个192B帧匹配原CPU308记录分布的111有效逻辑页+16273零页（允许分配帧置换）。两配置物理labels.bin SHA实际相同04fa55e4283c1d4d5c56c3b977b1c97265dd2cddf5bc423d3728e9fd7015629d。

| 配置 | 仿真总周期 | 标签AR事务 | 标签读拍 | 192B页读 | 写B回复 | 标签写拍 | 192B页写 | State读拍 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32槽 | 430263 | 257 | 747 | 249 | 188 | 549 | 183 | 72 |
| 单槽 | 470003 | 802 | 2364 | 788 | 387 | 1143 | 381 | 72 |

页大小192B，跨4KiB边界时三拍页拆为2+1或1+2，故不能将AR事务/B回复乘3当总拍数。32槽读burst长度3/2/1分别241/8/8，写178/5/5；单槽读774/14/14，写375/6/6。新audit_natural_axi逐实际地址/长度验证4KiB分割、后续页片段、完整每拍与WSTRB及最终全文件，不改旧小用例已通过审计。上述周期包括host初始化、POLL标签观察、检查点和最终读回，不是纯搜索计时或板上加速。

两组其他实际总线流量相同：graph4685读拍、design1068读/298写拍、owner422读、cost513读、connection State72读，table0。State72次×64B与72个parent对应，是后续query级驻留的实测仿真流量基线；不能现在就声称省71次后能带来多少速度。32槽面对111页也会驱逐，不是全驻留上界。目录仍FRAMES16384/INDEX14/HASH15，递归DEPTH4/CAPACITY32；本自然输入lookahead0，不增加递归覆盖。

初次辅助审计先后暴露旧假设：CLEAR opcode应为5而非3，design.created位允许对raw创建冗余设置，标签页跨4KiB会拆突发。按既有生产代码和真实事务修正独立模型后所有严检查通过，未改生产RTL或重新运行以躲避失败。两份未通过审计源码及最终审计/辅助/TB生成器已固定在 results/natural_query_rtl_audit_sources_20261025（manifest逐SHA绑定）。唯一编译警告为旧axi_file_memory输出计数初始化VRFC10-8426，无错误/fatal；不是时序/综合结论。

归档 results/offer_archives_20261025/natural_query_rtl_v1.tar.gz：433常规文件/10579578B压缩，逐成员与共享盘copy SHA核验。实际移走scratch到.preserved后解包433文件，重新汇总逐字节一致；恢复凭据 natural_query_rtl_restore_20261025.json。原始图、natural_query_inputs_v1与natural_query_oracle_v1依赖需按既有索引保持。普通run.py check也通过，但仅证明配置/文件可用，功能证据是本次RTL审计。

下一优先任务：在新隔离RTL variant实现每query/connection State驻留，使本自然查询72次重复State读取减少，并保持全部输出/heap/native/design/owner/cost不变；缓存命中必须核验query/price、完整version/design、connection/net/sink/cross、profile revision，不能把新State缓存误作距离标签有效性。切换连接/版本/生命周期应明确失效或拒绝，补负向身份测试。用同自然输入/同TB计数和公平搜索窗口比较，保留本基线。随后将外层search loop移入可综合控制器、实现backtrace与owner提交，扩至多查询/MCML/跨价格有效性及板卡。当前仅一个自然query，goal active。

# 自然查询硬件输入与独立过滤/成本oracle通过（2026-10-25，优先历史）

机器汇总 results/natural_query_inputs_20261025.json；脚本 summarize_natural_query_inputs.py。已将真实首查询快照生成graph绑定、design/owner/cost/connection State/native label硬件格式，并独立核验实际过滤和全部成本值。仍未执行此自然查询的RTL搜索循环，不能把输入通过表述为硬件通过。

主输入 results/natural_query_inputs_v1，从已通过的natural_query_v2快照恢复原Router，新增只读成本观测和输入导出；派生器 adapters/natural_query_v1/derive_cost_inputs.py，codec export_inputs.hpp，运行 prepare_natural_query_inputs.py。全部9个既有搜索文件仍逐字节等于自然采集：前后全节点状态、events、State、heap等，不改变搜索顺序。原成本函数在push前仅记录23输入/5结果，去掉新增观测恢复既有Router。独立audit_natural_query_inputs.py检查源、依赖、完整文件及数值。

全9089009节点：design.bin按16B flags/count/mask/reserved编码，created只取相对raw初始标记的增量（本快照0），design_sink来自原RRT全部连接及替代sink；owners.bin按net+1主key、refs低16/occupancy高16编码；cost.bin保留全history与256价格及27960个net的几何/fanout；initial_labels.native160为全节点lb/upstream/prev/visited/target五字记录。真实180326个sink预引用/活跃owner节点和180326个总引用完整保留，不得把owner区清零。初始overflow/cache为空，pool capacity0，allocator独立64B全零；若换到非空溢出池或预热cache，本codec显式拒绝，不会静默丢失。所有64B区尾填零已审计。

connections.bin含全部180326条64B CPS1记录，其identity和初始串行权重逐条从RRT解码校验；当前query index16506的权重来自实际State。全表不是所有未来时刻的State快照。cost price_offset=36356096、net_offset=36357120；rows311、columns0、hasLaguna0。原完整graph直接绑定 results/graph_image_20261024（9089009节点/40469536边）及同一RRT SHA，未改图或复制成小合成图。

171个实际成本包全部独立按binary32逐阶段舍入重算，3933输入字/855结果字一致；geometry从原RRT坐标及动态prev/current upstream重建，不能用前轮合成常量代替。child类型NON_LOCAL96、LOCAL_BOTH4、LOCAL_EAST70、EXCLUSIVE_SINK_EAST1；查询net引用最大1，目标成本1次。本轮没有landmark/crossSLR/SLL成本覆盖，其他用例已有覆盖不能自动算入这个自然查询。

独立过滤oracle results/natural_query_oracle_v1，由 verify_natural_query_filters.py 从完整原CSR和根前快照重新执行getChildren/excluded/access/visited/target判定。72次真实扩展、382条原始边→271条保留候选、0cache hit；170普通push+1target push，8bbox拒绝、28visited跳过、24graph_access拒绝、40非目标exclusive sink拒绝。lookahead0，EARLY1，全部202个created增量与完整搜索后快照一致。此oracle不依赖旧1216-parent脚本向量。

从所有原始候选及实际标签读导出的保守读取范围为308节点/111个8-node逻辑页；initial_label_imports.u32逐行(node,lb,upstream,prev,visited,target)，expected_label_reads.u32为同节点搜索后记录。必须在自然查询开始前实际host导入这些字面值（包括prev=-1和source已seed状态），再让硬件自己驱动搜索。全量native160文件不是现有paged backing格式，也不能直接当label AXI后备；308条host导入只保证这个已审计query的读取范围，不能据此假定其他节点或后续查询的默认值正确。读集合由本次观测路径和独立过滤共同约束，硬件偏离路径应立即失败，不能再从CPU脚本替它选下一parent。

持久化：natural_query_inputs_v1归档43文件/14032515B，natural_query_oracle_v1归档4文件/3587B，索引在 results/offer_archives_20261025。两个scratch根均实际移开后解包逐成员核验，重新汇总逐字节一致，凭据 results/natural_query_inputs_restore_20261025.json；输入原有图与natural_query_v2依赖仍需存在。原通过结果/共享基线保持不变。

下一步为这个真实输入编写闭环TB：actual heap POLL产生parent→实际graph/design首次过滤→metadata/access→geometry/cost→prev及三ACK→actual OFFER；目标实际CLEAR后POLL到target停止，持续同一State/标签/heap/设计。对照72扩展/271候选/171成本/73POLL及308最终记录和202 created，测试32槽与单槽或其他压力容量。不要向TB逐parent注入CPU预定顺序，不要在候选间重置query标签或owner。按Ross技能和现有B Vivado MCP会话执行真实仿真。query级State驻留/提交优化尚需实现和公平计时，不能将减少加载次数估计为实测加速。后续多查询/价格版本/回溯与owner提交/MCML/板卡仍待完成，goal active。

# 首个自然查询快照与原CPU搜索重放通过（2026-10-25，优先历史）

本轮从真实logicnets完整原始串行路由中采集首个自然查询，不改图、不设合成owner/target、不复用旧脚本oracle。机器证据 results/natural_query_20261025.json，汇总 scripts/summarize_natural_query.py。采集链接 results/natural_query_v2；独立恢复搜索链接 results/natural_query_replay_v1。原始参考源码和共享基线均保持。

查询identity：attempt/sequence1，iteration1，connection_index16506/id37267，net2717，source65185，sink150697，fanout257。实际bbox x[38,46]/y[283,295]；State share/wire/estimate raw bits分别3f800000/3e4ccccc/3f4ccccd，present factor为3f000000，cross=0、landmark=0、dead-end pruning=0，hot/prefetch/bbox启用。原prepare已经执行rip-up、设置target并将source入队；此时才保存快照，因此独立重放不可再执行prepare。

全节点initial_nodes.u32与search_final_nodes.u32各9089009行，每行11个32bit字段（lb/upstream/history/prev/visited/target/ownerNet/ownerCnt/occupancy/created/type）。另存完整256价格、溢出引用、已有children cache、真实State和逻辑heap。ownerNet沿用原CPU -1为空/零起net编号，不是FPGA net+1编码。所有节点都存，既有标签/历史/占用不能按默认值替代。格式与事件契约在 adapters/natural_query_v1/README.md；无需Vivado即可完成本轮CPU工作。

自然事件共72次扩展、271条有序children和271次候选检查、171次搜索内成本push、73次POLL；含prepare源push则172，与前轮完整普查相同。目标150697在父1411724下触发一次EARLY/CLEAR，CLEAR后目标入队并出队，found=1/aborted=0/剩余heap0；最终目标成本bits40267287。无lookahead。171个不同节点标签改变，202个created状态0到1。完整节点审计确认history、owner、引用和occupancy在搜索内保持，而不是随标签清零。快照结束点在原搜索循环之后、saveRouting/occupancy commit/target cleanup之前，不是完成连接提交后的状态。

采集器由 derive.py 只插入观测，删去观测逐字节恢复 build/real_trace/original.cpp；完整12轮路由结果与冻结原串行结果逐字节相同。audit_natural_query.py逐候选核验读前标签、prev/lb/upstream/visited/target提交和全部节点最终状态，并独立实现原8叉heap/POLL/CLEAR顺序。它不独立重算成本或过滤条件。

独立CPU重放进一步使用同一原Router和实际cost/filter/push，加载原RRT后恢复快照、cache、prices和State，重建HotExpand，再执行从原源码提取的搜索循环（不重新prepare）。make_replay.py生成driver；run_natural_query_replay.py与audit_natural_query_replay.py核验。全部9个文件逐字节一致：全节点前后状态、overflow、cache、prices、State、初末heap、全部events。因此是自然查询可独立恢复搜索的CPU oracle；尚无该查询的RTL执行、板卡性能或数学独立cost证明。

原natural_query_v1在生成源码时因非唯一poll文本锚点停止，未编译/执行，保留scratch；v2改为唯一完整while锚点。通过结果从不覆盖。采集26文件归档14710474B，重放29文件归档11269548B，位于 results/offer_archives_20261025。两者完整移开后解包逐成员核验，并重建汇总逐字节一致；恢复凭据 results/natural_query_restore_20261025.json。tmp丢失时按两个同名JSON索引运行restore_offer_result.py。

下一步：从此快照与事件生成自然查询的graph/design/owner/native label/64B State输入，先独立核验codec与实际geometry/cost输入，再驱动完整POLL→expand→filter→cost→三ACK→OFFER→target CLEAR搜索循环。当前只有每扩展候选链与合成递归组合，不能把72个父节点当作互相独立的旧脚本向量；须保持动态created/cache、标签写后读、全局heap与target位。测量query级State加载和重复准备可避免多少工作必须给真实计数，不能由逻辑次数直接声称加速。MCML自然查询快照/重放、多查询/跨价格有效性、真实多net提交与板卡实现仍待完成，研究goal active。

# 两个真实设计的自然递归普查（2026-10-25，优先历史）

完整原始串行搜索的观测普查和独立审计已通过；机器证据 results/natural_recursion_census_20261025.json，由 scripts/summarize_natural_recursion_census.py 汇总。

| 真实设计 | 查询次数 | 扩展次数 | push次数 | lookahead | 最大观测深度 |
| --- | --- | --- | --- | --- | --- |
| logicnets_jscl | 570286 | 47721796 | 130334832 | 0 | 1 |
| vtr_mcml | 718921 | 198273738 | 390136023 | 0 | 1 |

合计1289207查询、245995534扩展、520470855次push，全部found/routed，无abort。两个设计使用同一观测二进制，分别12轮/48轮收敛到overused=0；最终完整路由文件各自与冻结原串行基线逐字节相同。没有修改原图去制造递归。全部观测State profile的cross=0、landmark=0；结论仅限这两个设计及当前串行配置，不能推断其他器件/跨SLR场景不会递归。

观测源码删去新增观测后可逐字恢复冻结原始源码。正负合成对照使用同一header及同一原Router：Laguna正例lookahead=1、剩余兄弟=1、深度2；负例lookahead=0、深度1，故计数器具备实际递归触发覆盖。审计逐行检查34字段、query序列、每轮查询数、push总量及 expansions=pops-found-aborted+lookahead，未截断普查。审计脚本 audit_natural_recursion_census_v1.py 保留首次logicnets已冻结审计版本；通用 audit_natural_recursion_census.py 供MCML使用，其第三参数指向第一个普查目录绑定相同对照源码。

结果链接 results/natural_census_v1、natural_census_controls_v1、natural_mcml_census_v1；三个完整归档位于 results/offer_archives_20261025，同名JSON为恢复索引，分别18/10/18文件。实际移开三个scratch目录后恢复并核验全部成员，重新汇总应与恢复前逐字节一致；凭据 results/natural_recursion_restore_20261025.json。不存在GPU/FPGA实测加速结论，观测运行时间不作为性能基准。

下一优先工作改为采集自然普通查询的真实根前快照和逐候选事件，而不是继续寻找本配置未触发的递归。logicnets首选attempt1、connection_index16506/id37267、net2717、source65185、sink150697、fanout257：72扩展/172push，initial_queue=1、targets=1、最大raw/filtered degree8。MCML首选attempt1、connection_index89391：81扩展/179push。须在原ripup/prolog/prepare后的实际时刻保存State、bbox、标签、owner/history/价格和队列；真实队列长度用queue.sz，不能用底层h.size()。首查询present_factor bits为1056964608，不能从迭代日志推断时刻价格。

尚未输出这些自然查询的可重放状态快照、逐child事件或新RTL oracle；既有1216-parent脚本向量与合成递归矩阵不能充当自然轨迹金标准。接下来研究query级State驻留/重复准备，保留合成递归正确性覆盖；跨价格版本标签有效性、真实owner生命周期、完整搜索/回溯/提交与板卡性能仍待完成。研究goal active。

[递归target/占用/共享三条件矩阵](results/recursive_target_matrix_20261025.md)已完成3种合成初态×32/1槽六个实际全链运行。空闲target与同net refs2/occupancy1均EARLY/CLEAR；异net占用target禁止EARLY、保留seed且用price[1]。原CPU成本逐bit、target跨ACK/换页、祖先排空或真实visited重读、全部物理页审计通过；1395文件归档后真实恢复重检一致。没有自然搜索或板上速度结论；下一步真实CPU递归事件与初始快照oracle。下方保留历史阶段结果。

[设备侧Config14元数据](results/metadata_20261024.md)已用实际图/设计AXI生成12790份快照、179060字，与原CPU配置一致；全部后备字节、created/dead/claim生命周期及错误边界通过审计。独立完整服务综合2824LUT/2578FF、零RAM/DSP/组合环，未布线。下一步共享children设计状态并串联access_owner；本阶段尚未替换整合顶层的外部req_config输入。

[共享访问＋真实占用后端](results/access_owner_20261024.md)已完成实际联接：11664组合成、512真实图和614单槽样本及全部后备/AXI审计通过，CLOSE后设计计数保持、整个child期间禁止外部更新。身份桥15检查及默认容量4故障/5恢复通过，完整组合综合24634LUT/20366FF/375BRAM/3DSP、组合环0，未布线。下一步设备侧metadata生产；真实设计导入/提交、完整search与板上仍未完成。

[真实设计占用AXI模块](results/owner_axi_20261024.md)已通过13549命令/全部AXI字节及最终窗口审计、22项故障与恢复；四记录提交、半提交失败停止和VALID保持经过实际RTL验证。默认综合4866LUT/3081FF、零RAM/DSP/组合环，未布线。下一步接完整请求身份桥及共享访问模块，当前kind4/6尚未替换模型。

[设计占用存储布局](results/owner_store_20261024.md)已通过20万次原函数随机增减、320万次逐net查询及18515060次真实更新重放；主记录、溢出池和allocator最终全字节审计通过。支持可回收共享池、显式容量耗尽与16位边界；当前是CPU可执行规范，下一步实现实际AXI存储和kind4/6身份桥，尚未替换fabric模型。

[真实占用与同网引用统计](results/owner_profile_20261024.md)已对完整CPU路由的18515060次引用更新独立重放通过，路径/metadata/采样标签访问与基线一致。同net引用峰值255、不同net占用峰值4、overflow同时条目峰值53734；加载阶段已有180326次预引用，必须纳入设计初始化。下一步实现实际占用服务与显式容量处理，当前不是物理硬件或速度结果。

[访问性共享服务](results/access_fabric_20261024.md)已接通实际标签、图和坐标后端：11664组合成、512组真实图及614组单槽样本，19次故障/恢复和默认容量冷启动均通过。修复完整综合检出的组合反馈后，v3实际综合19739LUT/16938FF/375BRAM/3DSP，组合环0；未布线。占用/同net引用端口仍为模型，metadata生产、完整搜索与板上测量待接入。下方保留历史阶段记录。

[访问性驻留服务](results/access_service_20261024.md)已自动完成46656个child判定、195175次实际HLS调用和148519次动态请求；全量顺序/结果、720收集排列及96个复位偏移审计通过。实际综合1675LUT/2687FF，零RAM/DSP/组合环，未布线。动态后端目前为参考轨迹模型；下一步接实际标签/坐标/占用共享服务，尚无完整路由或板上收益结论。

[坐标服务](results/coordinate_service_20261024.md)已接通实际图/表读取和分页标签：真实23957、合成与压力各740请求，覆盖全部11520个真实SLL；57项组件边界及7项实际组合故障/恢复通过独立审计。保留空prev0与dense默认−1差异，前驱只读静态endY。完整服务实际综合17873LUT/14570FF/375BRAM/3DSP，零组合环，未布线。下一步是访问性状态机与动态服务的驻留连接；仍无完整FPGA路由或板上加速结论。

# 可访问性决策验证（2026-10-24）

[报告](results/search_access_20261024.md)：46656原函数场景、195175正常转移+9非法包、1171104实际RTL返回字passed；完整570286次CPU搜索路径/metadata/采集访问一致。实际764LUT756FF、零DSP/RAM/组合环，未布线。lookahead决策覆盖5329组，但递归执行/设备服务/完整FPGA性能仍未验证。

---

# 整数几何验证（2026-10-24）

[报告](results/search_geometry_20261024.md)：9496组实际RTL与8192原函数定义域差分passed，原INT_MAX+det溢出负例已复现；完整570286次CPU搜索路径/metadata/采集访问相同。实际1145LUT408FF、零DSP/RAM/组合环、未布线。v1/v2验证脚本负例及首次全路由预条件停止记录保留。访问性、完整设备搜索及板上尚未完成。

---

# 代价调用服务验证（2026-10-24）

[报告](results/cost_service_20261024.md)：实际整数HLS服务21576向量、23019请求22299响应、111485有效输出字及720复位时刻passed；120排列/18协议故障、45实际核边界/44单拍复位恢复passed。v1测试台delta采样负例保留，v2仅修测试台。完整服务实际8038LUT5814FF20DSP、零BRAM/URAM/latch/组合环；未布线、无完整设备路由/板上收益结论。

---

# 代价算术CPU/RTL数值验证（2026-10-24）

[报告](results/search_cost_numerics_20261024.md)：nativefloat实际158组331字差异，cosim完成不等于数值通过；整数binary32 5001280 primitive软件检查与21576组107880 RTL输出字全部一致，含16224真实包和576双NaN。整数运算接回完整570286次CPU搜索保持路径/metadata/已采集访问一致。实际7543LUT4791FF20DSP/零RAM/组合环，未布线、未接完整设备搜索。v1双NaN负例和全部来源/完成证据保留。

---

# 搜索代价与CLEAR验证（2026-10-24）

[报告](results/search_cost_and_clear_20261024.md)：Frontier v3全64K/192中断时刻/390boot与七故障passed，实际综合3768LUT2297FF116BRAM、组合环0、未布线；纯float helper原函数262144组exact bits/UBSan及完整570286 CPU搜索对照passed。全轨迹每次查询均清非空队列，未触发lookahead，因此递归硬件仍需另证；无成本算子HLS或完整FPGA性能结论。

---

# Frontier生命周期验证（2026-10-24，优先下方历史）

[报告](results/frontier_service_20261024.md)：原HLS ap_rst后size2/旧id可见负例，显式CLEAR隐藏旧堆；新服务实际64K全量入出、135150响应独立重放、192中断时刻、390成功boot、collector120排列12故障和服务6故障通过。v1 TB delta采样失败保留，v2仅改稳定采样。实际综合3760LUT2297FF116BRAM、组合环0，未布线，无完整搜索/板上收益结论。

---

# 真实首次扩展组合验证（2026-10-24，优先下方历史）

[报告](results/node_expansion_20261024.md)：原CPU getChildren观察oracle+完整sink解析；实际RTL1212扩展/550hit/3229输出/10753服务，32槽与单槽压力（CP27）逐事件、全AXI字节、完整设计后备均一致。15组组合故障/真实缩位耗尽通过。完整FRAMES163840实际综合21726LUT20299FF375BRAM3DSP、组合环0；功能FRAMES256，未布线、未接距离/Frontier/回溯/提交，无完整路由或板上加速结论。Python预检查与history日志截断问题已保存并解决，RTL无因此修改。

---

# 设计级持久存储验证（2026-10-24，优先下方历史）

[报告](results/design_store_20261024.md)：v3实际RTL+AXI文件后备，98893命令、68287逐笔AR/17821 W+B顺序、4524命中/890空缓存，完整145424192B独立重放核对；17故障含B失败已写字节但保留claim停止。真实节点/度数输入，过滤keep决策仍是测试输入，非完整getChildren联调。v1 TB保留字失败、v2改名和v3日志增强证据保留，RTL/oracle不变。实际1059LUT1056FF/零RAM/DSP、组合环0，未布线，无平台/板上性能结论。

---

# 真实CSR/属性AXI读取验证（2026-10-24，优先下方历史）

[报告](results/graph_reader_20261024.md)：原始完整二进制文件AXI模型，10163抽样父节点/64806请求/221602逐笔核对正常事务，覆盖全部8875个CSR offset 4KiB边界；含故障总221640 AR/R、19故障、28配置。独立auditor重读真实文件核对所有地址和响应；不是全图硬件遍历。实际综合1829LUT873FF166CARRY8/零RAM/DSP/latch、组合环0，未布线；未与children/pager及动态设计状态整合，无性能收益或板上结论。

---

# 首次构建引擎整合验证（2026-10-24，优先下方历史）

[报告](results/children_engine_20261024.md)：实际HLS+collector+服务调度组合，full93728构建/813439服务、907281 HLS调用、26故障/协议场景；collector4228组事件顺序/19故障、gen3两轮耗尽通过。独立源绑定、逐事件结构及计数审计passed；v1采样失败与v2仅TB修复的证据保留。实际控制组合1550LUT2047FF/0RAM/DSP、组合环0，未布线；服务仍为模型，不能当作图/设计缓存设备服务或完整路由性能证据。

---

# 首次过滤硬件协议验证（2026-10-24，优先下方历史）

[协议报告](results/children_protocol_20261024.md)：32位93728上下文/918795调用与gen3实际7上下文耗尽的C++/Csim/Csynth/RTL cosim全部passed/audited；直接RTL八阶段复位、故障恢复和24位最高node通过（11复位63调用）。实际综合944LUT881FF36CARRY8/0RAM/DSP/latch，组合环0；未布线。外部服务是原函数/独立模型，不是完整图/设计缓存设备服务或全路由验证。

---

# 首次邻接过滤语义验证（2026-10-24，优先下方历史）

[报告](results/children_first_touch_20261024.md)：93728组对照原getChildren及同数缓存重访通过，含空列表、重复child、自环、创建后丢弃、结构prune、简化lazy和串行锁分支。真实完整570286次CPU搜索/130334832push/12轮与已有exclusion基线路径、全部元数据、已采集标签访问二进制一致；独立源绑定审计passed。前三轮测试脚手架编译失败保留，v4修复后通过；无helper语义失败证据，也不据此声称并发/硬件正确性或性能收益。

---

# 自动换页与实际 AXI 验证（2026-10-24，优先下方历史）

[自动换页整合报告](results/auto_pager_20261024.md)：五组实际HLS/native/AXI字节模型回归和独立审计passed。production32覆盖27680原始函数oracle边及1次查询重开边，34898标签响应、62579 HLS调用、26984 WB/97070 RF、185502检查；额外70000次访问跨实际TX16边界（max65503），自动CP1次。单槽GEN3触发651次自动CP；真实binding16执行65536次绑定，安全CP后编号1。B错误、HLS读取时R错误和目录FULL三组均保留必要状态且停止。

本次默认功能仿真目录256帧，wrap16/fault分别16/2帧。虚拟终点252026230ns属于合成语义工作负载，不是完整CPU路由重放或加速比；实际163840帧资源需查本报告的综合证据。既有端点全38回放9.5213%结论不变，但不可套用到新增管理器或全路由。

---

# 实际HLS—标签端点整合验证（2026-10-24）

[完整记录](results/exclusion_edge_engine_20261024.md)：最终v4用原始CPU函数生成27680条单边向量，与实际HLS/桥接/原生端点RTL对照。110686检查与13错误恢复通过；720种输出/done排列及gen3两轮耗尽通过。旧HLS静态复位缺陷有相同TB负/正例；v3综合组合环反例经v4消除。综合1172LUT/2190FF/零BRAM、loop0，未布线、无自动分页/AXI或完整搜索。下方阶段记录以最新报告为准。

---

# 标签读取接口验证（2026-10-24）

[适配器报告](results/exclusion_label_adapter_20261024.md)：连接冻结sparse_records端点RTL，1024项槽位/偏移/阶段矩阵及故障/背压共2250检查通过；缩位编号实际耗尽通过。相同增强测试在v1复现同拍故障错误，v2修正后通过，负例保留。独立综合163CLB LUT/191FF/零存储与DSP；未布线。HLS调用收集器、页解析器与整搜索尚未接入。下方旧实验状态为历史记录。

---

# 新增 Frontier 验证（2026-10-24）

容量来自完整真实570286次搜索的普查（max38638），不是合成队列假设。64K fixed helper已接回同一完整CPU路径，结果/全部元数据/已采集标签样本一致。独立C++参考与候选各135228命令、1000169组比较通过。目录和证据见results/frontier_component_20261024.md。

HLS2022.2首轮因绝对工程名启动失败，失败保留；仅改Tcl工程入口的恢复版已完成Csim/Csynth，完整64K RTL cosim正在运行。终态自动独立审计，随后用Vivado核实AUTO RAM真实物理资源；HLS报告不作为物理容量证明。原CPU队列已驻留且clear为O(1)，本组件不是已证明的初始化优化，也未集成完整设备搜索。

---

最新[高地址稀疏组合](results/sparse_records_address64_20261024.md)先导/背压/综合/内部物理均审计；原生两项全量链保持，包装层没有全38或平台结论。[主机边界条件模型](results/native_host_envelope_20261024.md)使用公开命令字段量与假设串行延迟，不能当成PCIe/XRT实测。

最新[回填控制增量](results/sparse_records_20261024.md)：组合WB/RF七组审计与19查询通过，增量−2.83%；65536合法回收/真实16位回绕也过。组合全量等待原WB完整终态，先导不外推全量；默认综合/内部物理已完成（WNS1.100/WHS.035），平台约束仍不完整。

最新消融：写回稀疏位图控制的证据、失败保留、配对重试与全量门禁见[实验报告](results/sparse_writeback_20261024.md)。原生16位全38已审计，稀疏WB内部物理已审计（WNS1.726/WHS.039），全38仍活动。

当前新增[长期epoch取舍](results/epoch_lifecycle_20261024.md)：真实尝试数普查、默认容量清表阻塞、16位65536回收和资源/内部物理检查已完成；16位完整38回放待终态。6位短轨迹收益不代表长期最优。

# 当前组件级补充（2026-10-24）

[组合全38与干净重建](results/record_epoch6_full_20261024.md)已通过；hardware/candidates/native_epoch6_record为可复现原生状态端点，不等于下表规划的完整FPGA路由变体。下一阶段评估实际回收频率下的epoch清表代价，不能把未回绕的38查询当长期无成本。

# 方案 B 实验设计

新增[大查询需求审计](results/large_query_demand_20261023.md)：先完整回放全部7个符合当前单fence标识预算的大查询，另12个纳入checkpoint研究；禁止截断溢出访问或把无checkpoint需求计数当作可执行流量。

新增：[真实脏页键集合实验](results/directory_keysets_20261023.md)比较两种哈希和两种表容量，并给出单query/price低负载对抗控制。将集合探测数、目录RTL周期和完整传输/路由收益分别验证；不能用集合命中统计代替未命中、回收或协议回放。

## 工作假设

按器件、设计、net 和 connection 生命周期组织状态，能否减少初始化、重复准备和主机—设备同步？

对照层次保持分开：已有方案、成熟方法的直接迁移、当前场景的适配方案；同时区分软件算法改动与 FPGA 执行收益。可以让本方向单独成为论文主贡献，不要求拼齐其他所有方案。

## 已实现与计划变体

| 变体 | 含义 | 状态 |
|---|---|---|
| `reference` | 稠密清零与有限位宽 epoch 标签执行同一组读写；覆盖搜索切换和 epoch 回绕。只统计逻辑操作。 | 可运行 CPU 样例 |
| `cpu_dense_init` | 每 connection 全量清零搜索 scratch，设计状态独立 | 可运行状态微基准；完整路由待接入 |
| `cpu_serial_stamp` | 稠密存储 + 访问标记 + target 显式清理 | 可运行状态微基准；对应现有串行策略 |
| `cpu_existing_paged` | 原始 SparseLabels 分页/epoch 原语 | 微基准及真实串行/批处理入口已接通 |
| `cpu_paged_node_epoch` | 复用页池，用逐节点 epoch 替代首次触页整页清零 | 微基准及真实串行/批处理消融已完成 |
| `cpu_lifetime_residency` | 逐节点 epoch + net→resource 引用哈希索引 | 可运行状态微基准；同网准备消融 |
| `fpga_per_query` | 每查询准备状态的 FPGA 基线 | 待实现/接入 |
| `fpga_resident` | 驻留图与活跃状态 | 待实现/接入 |
| `fpga_resident_sparse_init` | 驻留 + 稀疏初始化 | 待实现/接入 |
| `fpga_net_tree_reuse` | 同网路由树/工作集复用 | 待实现/接入 |

`configs/experiment.json` 的共享变体入口仍为 planned；合成微基准由独立的 `configs/state_microbench.json` 配置，真实串行基线由 `configs/real_trace.json` 和 `profile-real` 执行。不能用同名变体混淆测量范围。

## 已完成的真实路径实验（2026-10-22）

logicnets_jscl / xcvu3p 的 180326 条间接连接，冻结真实 RRT1，三次原始运行、三次阶段计时/PC 采样、一次固定间隔访问记录和一次超大查询补充记录。全部八次输出与收敛过程一致，12 轮到零过用；独立图级检查通过。详见 [真实报告](results/real_trace_20261022.md)。

布线中位数 23.220 s（含约 4.57 s bbox），标签初始分配 42.19 ms，rip-up/commit 合计约 319.5 ms。标签访问相关源码采样约 3.43%、预取 4.84%、同网查询 6.87%；源码采样不等于精确访存延迟或可消除成本。

记录全部 570286 次搜索路径与访问计数；每 512 次抽样一次得到 1113 个完整查询，另覆盖全部 19 个 pops≥16384 查询，无截断。512 节点页触达密度分别 0.538%/3.480%，为逻辑布局统计。随后完成下面的真实分页消融；尚无回写后 Vivado DRC/时序、GPU 或 FPGA 结果。

## 已完成的真实分页消融（2026-10-22）

固定同一真实输入和 512 节点页，分别在相同串行顺序、相同 4-worker batch 调度内比较原始整页清零与逐节点 epoch；原始串行标记另外保留。五种配置各三次，共 15 次性能运行；同模式输出与收敛一致，独立图检查通过。原始 RRT1 已含完整 CSR，本地公共适配校验邻接后设置 flatGraphBuilt，使原有 batch 入口可用。

串行分页 57.428→33.165 s（-42.2%），batch 分页 50.635→35.279 s（-30.3%）；原始串行标记为 24.389 s，仍更快。两种模式各自保持结果，跨模式 totalLen 变化约 +0.556%，不可归因于标签策略。逐节点方案增加 4 B/物理槽位，本例结束时多 32 MiB，未缩小池容量。

性能程序不计逐访问事件，独立诊断程序统计清零槽位并再次校验结果；两种实际标签类通过 ASan/UBSan 增长、槽位换绑、epoch 回绕、独立上下文及回收检查。完整数据、阶段 RSS 观察、实际配置和限制见 [分页报告](results/paged_real_20261022.md)。

## 已完成的状态原语实验（2026-10-22）

从源 `main.cpp` 原样提取 NodeDyn、SparseLabels、owner-slot 引用计数、rip-up/commit 和 gatherShareSet。串行 scratch 使用 visited 序号，原始路由器并非每查询全量清零；`cpu_dense_init` 是全量初始化消融，不是唯一现有基线。gatherShareSet 是原始 GPU flood 的主机准备函数，普通串行 CPU 搜索并不会调用它；将其纳入微基准是为了研究准备成本，不能等同于串行完整布线时间。

四类负载：局部短访问、分散短访问、高扇出（每 net 128 分支）、局部长访问；262144 个资源，页大小 64/512/4096，种子 1/2/3，各重复三次，随机化执行顺序并绑定单个 CPU。每个样本在同一状态上运行两轮，第二轮只复用存储，仍使每个 connection 的距离标签失效。以独立路径重建检查占用和引用，并跨全部变体比较标签、共享集和脏增量指纹。

计时拆分为标签首次分配、显式 reset、标签访问（含惰性初始化）、同网准备、rip-up、commit 和主机增量打包。额外用独立插桩运行测量已有分页的首次触页处理，插桩数据不能用于速度比较。共享状态构造、生成输入、路径生成、验证、图遍历和设备传输不计入状态阶段合计。

首轮结果和负例见 [实验记录](results/state_microbench_20261022.md)，原始 JSON 保存各样本、命令、环境、源码/二进制哈希和全部页大小结果。页内稀疏初始化在分散访问上有收益，未超过现有串行标记策略；同网哈希索引的维护成本不可忽略。尚不能据此宣称完整路由或 FPGA 加速。

## 消融变量

- 状态驻留开/关
- 初始化：稠密 / epoch / 按需页
- 页大小、上下文数、同网任务分组

先选能够回答主假设的最小对照，不强制穷举组合。交叉实验应检查相互作用，例如压缩与驻留、驻留与调度、内存后端与数据布局。

## 指标

| 指标 | 单位 |
|---|---|
| `init_ms` | ms |
| `state_bytes` | byte |
| `state_page_hit_rate` | ratio |
| `sync_bytes` | byte |
| `reroute_iterations` | count |
| `routing_ms` | ms |

计时分别记录准备/构图、首次加载、状态初始化、内核、结果回溯、提交/同步、回退和完整流程。首次运行与驻留复用运行分别报告。硬件有效频率以实现报告/实际运行配置为准；CPU toy 的逻辑次数不换算成硬件周期或速度。

## 阶段验证

1. 接通真实软件基线，固定输入、工具/代码版本、环境变量与约束。
2. 接入真实数据接口，先验证与源工具的资源和结果语义一致。
3. 实现直接迁移的软件原型，复现和分析无收益案例。
4. 实现本方向的场景适配机制，与相同算法目标的基线比较。
5. 接入硬件并进行仿真/综合/实现或实卡验证，记录实际覆盖范围。
6. 回到完整布局/布线流程，检查质量、成功率、迭代变化和端到端收益。

这些是可复用的推进顺序，并非审批流程。根据已有授权与具体研究进展可以调整。

## 必须保持的语义

- 设计级占用/历史拥塞不能随 connection 标签一起清零。
- 同网多分支共享资源需引用关系，资源占用按不同 net 计数。
- 跨价格版本复用距离标签需要明确失效或修复条件；存储复用不等于距离有效。
- epoch 回绕、并发上下文和页回收不能暴露旧状态。

## 可重复性与结果边界

真实结果保存数据哈希、代码版本、完整命令、设备/驱动/平台包、随机种子、重复次数和计时范围。`configs/experiment.json` 中尚为空的阈值和版本必须按真实实验填写，不能把 null 当作零。

相同输入与约束下比较，并报告失败、预算耗尽、回退及完整流程结果。若主张时序质量，需加入布后时序或经过验证的时序模型；线长不能代替时序。当前合成样例结果不能纳入正式论文性能表。
