# 新会话交接入口（2026-11-04）

用户要求在新对话继续，本轮已完成交接。**先读 [HANDOFF_20261104.md](HANDOFF_20261104.md)**，沿已有新机独立执行授权接续，无需重新请求授权。本轮仅交接，没有启动新实验或修改生产RTL。goal工具当前返回null，不把历史paused/active/blocked当当前线程状态。

当前完整shadow v7已完成主审、冻结及实际恢复验收：`full_system_functional_netlist_validated=true`；`physical_gate_open=false`，时序/板卡验收仍false。**不重跑58控制，不重复提交完整v7。**监督器旧awaiting_main_review/false是保留的自动历史回执，接受依据为20261103新主审与最终冻结报告。

2026-11-04T03:22:57Z本机核对四个相关原runner均不存在、无active_process；按研究根/runner名扫描无匹配进程，MCP无活动Vivado会话，恢复根无新物理运行目录。见 [状态快照](results/session_handoff_state_20261104.json)、[关键证据SHA索引](results/session_handoff_artifacts_20261104.json) 和 [MCP回执](results/session_handoff_vivado_sessions_20261104.json)。两份v7终态/主审归档SHA本次重新核对一致。

下一从绑定v7的新物理gate/prepare/runner/auditor及fresh输入准备、独立审计接续；旧physical v5仍绑定失败v6/旧机路径/KA正stall，不能直接执行。保持10ns OOC原约束、连续60s≤225GiB且≤cgroup75%准入。start/release反例、caller仲裁与隔离互锁候选仍独立未决，修改生产源后须建立新证据。详细工具、路径、恢复关系、成果边界和接续顺序见新交接文件。

以下保留历史，旧“运行中/待主审/网表false/暂停”均不代表当前状态。

# 静态stage候选：面积下降，完整综合网表验证进行中（2026-10-30）

静态stage候选的同条件OOC为LUT132426、FF87968，较CP基线减少7055 LUT和80 FF；布局前WNS −4.796ns，仍未满足10ns，尚未选为替代基线。SLOTS32完整RTL配对已通过，参见[候选综合证据](results/stage_static_cp_synth_20261030.json)和[完整RTL配对](results/stage_static_cp_host_full_static_20261030.json)。

旧综合网表shadow v3/v4在无效期未初始化payload比较处失败并保留。新三组接口观察器已通过[59个独立控制例及实际恢复](results/shadow_payload_contract_controls_20261030.json)，只读日志也经[两例校准及实际恢复](results/shadow_payload_monitor_controls_20261030.json)。完整shadow v5现已启动，**尚无完整综合网表通过、物理收益或板卡结论**。实时任务所有权与下一步见[NEXT_STEPS.md](NEXT_STEPS.md)。

以下保留历史。

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

# 当前研究进度（2026-10-29）

十一源版本的八场景行为矩阵已全部通过，216份输出比较及归档实际恢复复审完成，见[矩阵结果](results/query_native_matrix_20261028.json)。后续候选的验证范围分别记录，不能沿用该矩阵作为新候选的全部覆盖。

当前保留的较优综合基线为checkpoint_edit_synth_v1：同133生产源/U280/10ns，组合环与自动切环均为0，LUT139481、FF88048、BRAM163、DSP23，布局前WNS为−4.948ns。结果已独立检查DCP、归档实际恢复并冻结，见[CP综合结果](results/checkpoint_edit_synth_20261028.json)。仍未满足10ns目标，尚无物理时序或板卡加速结论。route_label候选实测退化到−5.852ns且资源增加，已[明确不选](results/route_label_selection_20261028.json)。

上一轮研究路径寄存器的同周期写入结构分解。该候选[12个单元测试](results/route_path_units_20261028.json)及[完整CRC压力例](results/route_path_system_crc_20261028.json)通过：27份输出和48288200ns结束时间与基线精确一致，并增加4×32路径字的旧控制树参考检查；379文件归档实际恢复复审通过，184文件已冻结入库。新候选的完整八场景矩阵尚未执行。

本候选的[匹配OOC及归档恢复复审](results/route_path_synth_20261028.json)已完成，165文件冻结核验通过：LUT132021、FF87929、BRAM163、DSP23，组合环与自动切环为0；相对CP减少7460LUT（约5.35%）和119FF，但WNS退化至−5.841ns。[选择记录](results/route_path_selection_20261029.json)保留CP为时序基线并保存本轮面积收益。实际最差端点转到cp_stage写使能，下一研究入口见[NEXT_STEPS.md](NEXT_STEPS.md)。上轮磁盘配额导致的入库失败已恢复并保留[失败与入库记录](results/route_path_storage_recovery_20261029/publication.json)。

当前进一步分解cp_stage暂存银行的同周期写入口，保留原控制树和事务保护。[12个单元测试](results/route_stage_units_20261029.json)及[完整CRC压力例](results/route_stage_system_crc_20261029.json)均通过并实际归档恢复：27输出及结束周期精确一致，新增156字银行参考覆盖10次捕获、1248次导入、1259次检查；完整系统184文件冻结核验通过。[同条件综合及独立恢复复审](results/route_stage_synth_20261029.json)也已完成，167文件冻结核验通过：LUT131318、FF87983、WNS−5.614ns，零组合环及自动切环。相对CP减少8163 LUT但WNS差0.666ns；相对path减少703 LUT、WNS改善0.227ns但多54 FF。[三者比较](results/route_stage_tradeoff_20261029.json)保留三个资源/时序取舍点，没有生产选择或板卡频率结论。

新最差路径含64级LUT及两级MUX，终点转到搜索响应状态寄存器。旧解析器只计LUT的[失败证据](results/route_stage_timing_parser_failure_20261029.json)已保留；v2解析及9文件分析冻结通过。[唯一v2后续队列](results/checkpoint_edit_physical_queue_v2_launch_20261029.json)已接管CP参考的完整布局布线测量，内存连续60秒不超过225/300GiB后准入。仍待物理实测及实际恢复复审，新候选八场景矩阵也未完成；实际阶段、句柄与所有权见[NEXT_STEPS.md](NEXT_STEPS.md)。

以下保留历史。

# 当前研究进度（2026-10-27）

十源合并版本完整匹配OOC及独立DCP检查确认零组合环（check_timing/LUTLP-1），已归档实际恢复复审并189文件冻结。资源139803LUT/88045FF/163BRAM/23DSP；10ns下WNS仍-7.111ns，物理时序尚未通过。见results/native_retirement_synth_20261027.json/.md及71级最差路径分析native_retirement_timing_path_20261027.json/.md。

完整CRC压力行为已通过，可计矩阵1/8。结构门槛通过后唯一串行队列已启动第一项off/full回归，目前仿真中；其余按队列逐例运行、审计、归档实际恢复和缓存释放，尚不能称8/8。队列所有权/进程及禁止重复启动要求见NEXT_STEPS.md。

以下保留历史。

当前剩余七项回归已排入唯一串行队列，等待同源零环结构审计及实际恢复通过；准入内存上限为容器限额75%，每例结束后审计、归档恢复和定向缓存释放。当前仍只有CRC压力1/8通过；队列/进程详见NEXT_STEPS.md。

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

源标签CRC硬件绑定已在32槽/单槽G2 warm恢复中通过，并验证错误CRC失败隔离，见 [本轮报告](results/label_source_crc_20261027.md)。新校验默认关闭，实验显式开启；初始CPU读闭包与板卡验证仍未完成。

原生目录/标签导出已接入32槽/单槽 G2 warm恢复，见 [本轮报告](results/runtime_label_snapshot_20261027.md)。恢复输入来自实际403页/822条输出，初始CPU未来读闭包仍未移除。

运行中 owner 增量快照已通过32槽/单槽 G2 发布与 warm 恢复联动，见 [本轮报告](results/runtime_owner_snapshot_20261027.md)。候选从初始 G1 副本起步，实际 RTL 跟踪并复制4条脏行；标签目录导出、通用 epoch 轮转和板卡收益仍未完成。

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

[最新进展：单命令查询生命周期RTL](results/query_lifecycle_20261025.md)。硬件prepare/search/commit/目标清理通过28模型及两种缓存真实双query，完整OOC 86880 LUT/62800 FF。真实生命周期故障、完整checkpoint与板卡仍待完成。

[最新进展：自主搜索接口资源对照](results/search_optimization_20261025.md)。回复静态改写无资源收益；四路搜索注入为86129 LUT（较v1减少13.418%），行为/周期/完整图像保持。prepare、提交编排、完整checkpoint与板卡仍待完成。

[最新进展：设备侧自主搜索与完整组合综合](results/search_scheduler_20261025.md)。40模型场景及两种缓存真实双查询独立审计通过；完整top 99477 LUT/61700 FF/160.5 BRAM/23 DSP。prepare、提交编排、完整checkpoint与板卡仍待完成。

[最新进展：独立服务系统顶层与完整组合综合](results/residency_system_20261025.md)。14次正常/续接/故障运行与抽取前逐周期一致；完整组合OOC为79811 LUT、60324 FF、160.5 BRAM Tile、23 DSP，零latch/黑盒。设备侧自主搜索、完整checkpoint及板卡仍待完成。

[最新进展：围栏正常双查询与真实续接回归](results/transaction_fence_normal_20261025.md)。四次32槽/单槽完整搜索、共享释放和真实成本子回复背压通过独立审计；路由状态保持，组合仿真周期增加约0.42%／0.51%。完整top、自主搜索、任意写入恢复和板卡仍待完成。

[最新进展：16入口事务围栏与静态切片](results/transaction_fence_20261025.md)。11模型/5退休检查与10真实数据RTL故障恢复通过；静态切片保持逐cycle/AXI/图像一致，组件OOC6908LUT/3040FF。完整top/正常search与legacy写恢复仍待推进。

[最新进展：常驻配置快照与硬件恢复](results/config_restore_20261025.md)。六服务配置发包与完成已移入RTL，27恢复响应/37次装载模型和10真实故障通过；统一生产围栏、完整snapshot读取/search及板卡仍待完成。

[最新进展：硬件标签恢复服务](results/label_restore_20261025.md)。协调器直接启动OPEN/探测/流写/CHECKPOINT/整条读回；30模型响应与10真实故障恢复通过。配置与authority仍TB，完整自主checkpoint/search及板卡尚未完成。

[最新进展：恢复协调器接入真实服务](results/recovery_join_20261025.md)。独立journal/reset/两遍owner恢复已在真实10故障中通过；完整owner与CPU一致。配置、authority和标签仍TB回调，完整自主checkpoint/搜索及板卡尚未完成。以下保留历史记录。

[最新进展：可综合恢复协调器组件](results/recovery_coordinator_20261025.md)。journal/排空复位/两遍owner修复已通过28次模型响应与默认32项OOC；新模块尚未接真实服务恢复链，完整checkpoint和搜索外层仍未完成。

[最新进展：同实例提交checkpoint协调恢复](results/route_recovery_20261025.md)。10例真实故障在排空后复位，经实际owner修复及新epoch标签重载后恰重新提交一次；恢复协调器仍TB，非完整search/任意工作集或耐掉电恢复。

[最新进展：真实故障排空屏障修复](results/route_drain_20261025.md)。旧adapter已确认native错误早于AXI余拍排空即完成；隔离drain变体通过10故障与正常双query回归。失败可能已有owner副作用，尚无自动恢复/完整外层或板卡结论。旧成功基线和反例均保留。

[最新进展：路径控制器接入真实分页标签与owner AXI](results/route_join_20261025.md)。同实例双查询、共享提交/ripup及完整状态/AXI审计通过；外层search/prepare仍TB，工作集仍CPU预知，真实故障恢复/价格切换/未知页及板卡未完成。下方保留历史阶段记录。

[设备侧Config14元数据](results/metadata_20261024.md)已用实际图/设计AXI生成12790份快照、179060字，与原CPU配置一致；全部后备字节、created/dead/claim生命周期及错误边界通过审计。独立完整服务综合2824LUT/2578FF、零RAM/DSP/组合环，未布线。下一步共享children设计状态并串联access_owner；本阶段尚未替换整合顶层的外部req_config输入。

[共享访问＋真实占用后端](results/access_owner_20261024.md)已完成实际联接：11664组合成、512真实图和614单槽样本及全部后备/AXI审计通过，CLOSE后设计计数保持、整个child期间禁止外部更新。身份桥15检查及默认容量4故障/5恢复通过，完整组合综合24634LUT/20366FF/375BRAM/3DSP、组合环0，未布线。下一步设备侧metadata生产；真实设计导入/提交、完整search与板上仍未完成。

[真实设计占用AXI模块](results/owner_axi_20261024.md)已通过13549命令/全部AXI字节及最终窗口审计、22项故障与恢复；四记录提交、半提交失败停止和VALID保持经过实际RTL验证。默认综合4866LUT/3081FF、零RAM/DSP/组合环，未布线。下一步接完整请求身份桥及共享访问模块，当前kind4/6尚未替换模型。

[设计占用存储布局](results/owner_store_20261024.md)已通过20万次原函数随机增减、320万次逐net查询及18515060次真实更新重放；主记录、溢出池和allocator最终全字节审计通过。支持可回收共享池、显式容量耗尽与16位边界；当前是CPU可执行规范，下一步实现实际AXI存储和kind4/6身份桥，尚未替换fabric模型。

[真实占用与同网引用统计](results/owner_profile_20261024.md)已对完整CPU路由的18515060次引用更新独立重放通过，路径/metadata/采样标签访问与基线一致。同net引用峰值255、不同net占用峰值4、overflow同时条目峰值53734；加载阶段已有180326次预引用，必须纳入设计初始化。下一步实现实际占用服务与显式容量处理，当前不是物理硬件或速度结果。

[访问性共享服务](results/access_fabric_20261024.md)已接通实际标签、图和坐标后端：11664组合成、512组真实图及614组单槽样本，19次故障/恢复和默认容量冷启动均通过。修复完整综合检出的组合反馈后，v3实际综合19739LUT/16938FF/375BRAM/3DSP，组合环0；未布线。占用/同net引用端口仍为模型，metadata生产、完整搜索与板上测量待接入。下方保留历史阶段记录。

[访问性驻留服务](results/access_service_20261024.md)已自动完成46656个child判定、195175次实际HLS调用和148519次动态请求；全量顺序/结果、720收集排列及96个复位偏移审计通过。实际综合1675LUT/2687FF，零RAM/DSP/组合环，未布线。动态后端目前为参考轨迹模型；下一步接实际标签/坐标/占用共享服务，尚无完整路由或板上收益结论。

[坐标服务](results/coordinate_service_20261024.md)已接通实际图/表读取和分页标签：真实23957、合成与压力各740请求，覆盖全部11520个真实SLL；57项组件边界及7项实际组合故障/恢复通过独立审计。保留空prev0与dense默认−1差异，前驱只读静态endY。完整服务实际综合17873LUT/14570FF/375BRAM/3DSP，零组合环，未布线。下一步是访问性状态机与动态服务的驻留连接；仍无完整FPGA路由或板上加速结论。

[可访问性决策状态机](results/search_access_20261024.md)已通过46656组原函数/动态读取顺序差分、195184次实际RTL调用和完整570286次CPU搜索核对。实际764LUT/756FF、零DSP/RAM/组合环，未布线。下一步接设备侧标签、动态坐标/SLR和占用服务；尚非完整FPGA搜索或板上加速结果。

[整数几何距离](results/search_geometry_20261024.md)已通过9496组实际RTL/37984字核对，接回完整570286次CPU搜索保持路径、metadata和采集访问一致。明确处理原Laguna哨兵溢出；实际综合1145LUT/408FF、零DSP/RAM/组合环，未布线。下一步访问性、表/价格服务及完整搜索，尚无端到端FPGA加速结论。

[代价调用服务](results/cost_service_20261024.md)已接实际整数HLS核：21576向量逐位一致、720复位时刻、120输出排列/18协议故障和45实际核故障恢复通过。完整服务实际8038LUT/5814FF/20DSP、零RAM/组合环，未布线。下一步接几何、价格与完整搜索控制器，尚无完整FPGA路由或板上加速结论。

# 方案 B：驻留状态与稀疏初始化

[搜索代价数值硬件](results/search_cost_numerics_20261024.md)：原生float RTL有158组差异，已实现整数binary32版本；21576组/107880字RTL逐位一致，完整CPU路由保持一致。实际综合7543LUT4791FF20DSP/零RAM、组合环0；尚需cost包装、几何/访问性与完整搜索接入，未布线/板上。

[搜索代价与查询内CLEAR](results/search_cost_and_clear_20261024.md)：补齐提前target所需CLEAR5；Frontier v3全回归/七故障通过，实际3768LUT2297FF116BRAM。纯浮点代价拆分通过262144组逐位对照及完整570286次CPU搜索，路径/metadata/采集访问保持一致；尚无代价HLS/完整硬件搜索。

[Frontier查询生命周期](results/frontier_service_20261024.md)已完成：确认原HLS冷复位保留旧堆，新增启动CLEAR与查询归属服务；实际64K满堆、192中断时刻、390启动清堆和独立故障审计通过。完整服务综合3760LUT/2297FF/116BRAM、组合环0，未布线。下一步接距离代价及完整搜索调度；仍无完整FPGA路由或板上性能结论。

[真实首次扩展组合](results/node_expansion_20261024.md)已把图/设计存储/构建HLS/分页排除实际联接：1212扩展、550缓存hit、3229输出与原CPU一致；压力27checkpoint及15组边界通过。完整默认容量综合21726LUT/20299FF/375BRAM/3DSP、组合环0，未布线。下一步接Frontier、距离代价、回溯与提交；尚非完整路由或板上性能结果。

[设计级状态与持久过滤缓存](results/design_store_20261024.md)已完成实际AXI服务：98893命令/17故障、完整145424192B后备文件与独立预期一致，4524发布/命中、890空缓存，全部写成功B后返回。实际综合1059LUT/1056FF、零RAM/DSP、组合环0。下一步把图/存储/构建/排除服务联接；当前过滤决策仍是测试输入。

[真实图AXI读取器](results/graph_reader_20261024.md)已通过64806请求、221640总读事务及19故障场景；独立原文件/逐笔返回审计passed。实际综合1829LUT/873FF、零RAM/DSP、组合环0。下一步将真实CSR度数/属性接入构建引擎，并实现设计状态与持久缓存；尚未完整整合或板上验证。

[首次构建引擎整合](results/children_engine_20261024.md)通过93728构建/813439服务的实际HLS联调及26故障场景；collector顺序/背压和真实编号耗尽也通过。完整控制组合综合1550LUT/2047FF、零RAM/DSP、组合环0。下一步优先接实际图读取、设计状态和持久缓存；当前服务仍是测试模型。

[首次过滤硬件接口](results/children_protocol_20261024.md)已通过918795次RTL协议调用、缩位实际耗尽和八阶段冷复位测试；独立实际综合944LUT/881FF、零RAM/DSP、组合环0。下一步接调用收集、图/设计缓存服务及自动换页边引擎；尚未形成完整设备节点扩展。

[首次邻接过滤状态机](results/children_first_touch_20261024.md)通过93728组原函数对照和完整570286次真实CPU搜索核对；路径、全部搜索元数据、已采集标签访问一致。保留先创建后类型筛选、重复child和首次缓存语义；下一步实现硬件请求控制器及图/设计状态服务，目前该模块尚无HLS/RTL。

[自动换页整合](results/auto_pager_20261024.md)已完成五组实际HLS/原生端点/AXI字节模型验证与独立审计：完整27681边、34898标签响应、185502检查，真实16位事务/绑定边界及三种后备故障通过。完整默认容量综合16528 LUT/15156 FF/375 BRAM/3 DSP，组合环0；尚未布线，也未接完整图搜索与板上。下方为历史阶段记录，当前下一步是图读取和动态created/getChildren首次过滤缓存。

[排除边引擎v4](results/exclusion_edge_engine_20261024.md)已连接实际HLS与标签端点，27680条边/110686项检查及恢复测试通过。修复HLS静态状态未复位与握手组合环；整合模块实际综合1172LUT/2190FF、组合环0。下一步接自动分页；尚无完整路由或板上加速结论。[复位边界勘误](hardware/HLS_RESET_BOUNDARY.md)优先旧独立组件描述。

[标签读取适配器v2](results/exclusion_label_adapter_20261024.md)已连接原生状态端点RTL并通过2250项检查、实际编号耗尽与独立审计；修复了增强测试发现的同拍故障问题。实际综合163LUT/191FF、零BRAM。下一步接HLS输出收集与页解析器，尚非完整设备搜索。以下保留各阶段记录，最新状态以AGENTS.md/NEXT_STEPS.md顶部为准。

[邻接排除硬件接口](results/exclusion_protocol_20261024.md)已通过354530次RTL调用及缩小编号宽度的实际耗尽验证；布线后791LUT/1415FF/零BRAM，当前10ns内部时序通过。按[标签接入约束](hardware/EXCLUSION_LABEL_BOUNDARY.md)已实现独立服务适配器，尚待整链路集成，尚非完整设备搜索。

[完整38查询消融](results/sparse_full_ablation_20261024.md)全部完成：WB减少3.3188%，WB/RF组合减少9.5213%，AXI字节不变。[邻接排除状态机](results/exclusion_machine_20261024.md)已通过27648组语义/读取顺序检查和完整570286次CPU搜索核对，下一步接入硬件控制接口。

[写回稀疏完整38查询](results/sparse_writeback_full_20261024.md)通过独立审计，端点回放时间减少3.3188%，38/38收据区间更快；组合WB/RF全量已自动启动。[完整真实图输入](results/graph_image_20261024.md)也已通过全图加载器核对及逐字节RRT1重建，尚未设备上传。

[Frontier容量与组件验证](results/frontier_component_20261024.md)：完整570286次真实搜索峰值38638，同一64K helper已保持完整CPU路由结果；C++边界验证通过。HLS首轮启动错误保留，独立恢复已通过Csim/综合/完整RTL协同仿真及审计，Vivado实际综合为3411LUT/1794FF/116RAMB36E2，布局布线已完成（3394LUT/116BRAM，WNS1.336ns/WHS0.039ns），尚无完整路由或板上性能结论。

[稀疏组合高地址接入](results/sparse_records_address64_20261024.md)通过32槽背压/8CP与19查询先导，时间收据保持一致；默认综合增加106LUT/68FF，内部物理WNS1.134/WHS.028ns。仍缺高地址全38、XRT/平台/板上。[主机控制边界](results/native_host_envelope_20261024.md)补充条件工作量与连接级搜索所有权审计，未实现完整搜索内核。

[回填稀疏控制增量](results/sparse_records_20261024.md)已通过七组正确性与先导审计：19查询相对WB-only再减少2.83%，相对原生16位共减少8.13%；通道相对背压相位配对仍有2.816%–2.832%增量。192B页/AXI量不变。默认综合12706LUT/375BRAM，内部物理已通过当前10ns模型（WNS1.100/WHS.035），组合全量已排队等待原WB全量终态，尚无全量或板上收益结论。

[写回稀疏记录控制](results/sparse_writeback_20261024.md)独立变体通过256位图、故障、背压和19查询审计：仿真时间减少5.46%，页字节/AXI量不变；默认综合增加126LUT/8FF。内部物理检查已通过当前模型（WNS1.726/WHS0.039ns），完整38继续运行，尚无本变体全量或板上收益结论。

[查询生命周期与页密度](results/query_lifetime_and_density_20261024.md)：6/16位目录均通过四查询隔离、ID耗尽及完整fence后复用检查，各56项；38查询全部页传输中60.7893%的记录位置无效。该比例仅为控制优化候选工作量，未实现稀疏传输或获得对应加速。

[长期epoch取舍](results/epoch_lifecycle_20261024.md)已补真实570286次搜索尝试普查及回绕阻塞实测：38查询没有覆盖长期清表频率。16位候选通过先导、完整计数回绕、故障及内部物理检查，额外72BRAM；其完整38查询已通过且逐查询周期与6位组合一致。条件工作量模型不等于全FPGA性能，6位快照与源包保持不变。

[原生组合完整38查询与源包](results/record_epoch6_full_20261024.md)已通过并审计：保持1.7067%原型周期收益，资源为12396LUT/303BRAM（布线后）；可复现源包在hardware/candidates/native_epoch6_record，独立仿真和干净综合重建通过。38查询未覆盖目录epoch长期回绕性能，平台/完整路由/板上仍未完成。

[64位后备基址接入先导](results/address64_endpoint_20261024.md)已通过配置、32槽背压和地址高位进位检查；默认容量综合增加78LUT/68寄存器，高基址19查询实际值先导及独立物理也通过；平台接口预算仍缺，尚未接入XRT/实卡，原生组合全量也已完成，仍非板上加速。

[记录响应直通完整38查询](results/record_response_full_20261024.md)已通过并审计：仿真时间减少1.7067%，38/38查询区间缩短，传输字节不变。静态codec/epoch6组合的物理与回绕检查也通过，组合完整回放已完成；均非板上加速。

[组合兼容性先导](results/record_epoch6_pilot_20261024.md)通过：静态codec/epoch6与记录响应直通可在19查询中保持完全相同周期；默认容量综合12434LUT/303BRAM，组合物理实现正在运行，组合全量尚未验证。

[记录响应直通消融](results/record_response_fallthrough_20261024.md)已实现独立变体：19查询先导仿真时间减少1.35%，功能、阻塞与九类故障检查通过；默认容量综合增加258 LUT/13寄存器，BRAM/DSP不变；布局布线内部10ns模型通过（WNS0.943ns），平台约束仍不完整；完整38查询回放继续，尚无全量收益结论。

[清表与传输等待重叠核对](results/transfer_clear_overlap_20261024.md)已通过19查询先导：直接观测到252357个重叠周期，纠正了将全部262144清表周期归入写回等待的判断；下一步研究记录逐条队列往返成本。

截至2026-10-24：小页动态epoch8、静态epoch6及修正版64节点基线均已完成38查询并核验。整体配置比较中小页仿真时间减少78.2114%、传输字节减少87.1297%，见[全量比较](results/small_page_full_comparison_cycle64_20261023.md)。这些是原型访问回放，不是完整布线或板上加速。

[目录hash单因素消融](results/directory_hash_ablation_20261024.md)已完成：18→17位在19查询先导减少6.27%，但完整38查询增加0.1323%；功能结果一致、零探测溢出，保留18位默认配置。[初始化观测](results/initialization_observer_pilots_20261024.md)确认了目录就绪边界，未将其等同整个端点就绪。

常量切片codec将端点综合LUT从14651降至11688；epoch6候选减少16个BRAM、增加568个LUT，已通过全量等周期回放与内部10ns物理时序验证。平台约束、完整FPGA路由和实卡验证仍未完成。后续状态以[NEXT_STEPS.md](NEXT_STEPS.md)顶部及实际结果为准。

以下保留此前阶段记录，其中“当前”“最新”和“待完成”均指该条记录产生时的状态。

最新：[7个完整大查询RTL](results/rtl_streaming_large_20261023.md)全部通过；[端点checkpoint先导](results/rtl_retained_endpoint_20261023.md)完成21次自动排空/恢复与旧查询回归。全38查询checkpoint回放、综合及实卡验证待完成。

新增：[保留后备数据的标识回收软件验证](results/retained_checkpoint_plan_20261023.md)通过全部38查询、1404.8万字段访问及31次回收；RTL checkpoint仍待实现。

当前：[七个完整大查询流式回放](results/rtl_streaming_large_20261023.md)已提交，尚未完成；流式小查询与旧向量及周期完全一致。[时钟壳配对实现](results/rtl_clock_shell_20261023.md)已结束，但两版保持违例和上游时钟/接口模型缺失均保留，未通过时序或模型完整性验收。

最新：[索引端点完整回放](results/rtl_indexed_endpoint_20261023.md)通过19真实小查询的原字节/协议检查，含初始化总周期减少11.63%，整体综合6015 LUT、5288 FF、43 BRAM、3 DSP。3个查询变慢，尚无实卡或完整搜索路由加速证明；大查询和时钟闭合继续推进。

最新：[有界目录索引RTL](results/rtl_indexed_directory_20261023.md)已通过独立行为、四项负例与默认容量综合审计，保留溢出回退和回绕清表。代价为+267 LUT、+106 FF、+21 BRAM、+3 DSP，尚无整体性能收益证明。[显式时钟壳配对实验](results/rtl_clock_shell_20261023.md)仍在运行：原版已完成但未满足声明的接口时序预算，宽版继续实现。

最新：[原版/宽codec配对实现](results/rtl_codec_timing_20261023.md)完成相同10ns约束下的OOC布局布线与审计。最终建立裕量+4.395/+4.280ns、保持裕量+0.036/+0.016ns，两版路由错误为零；内部模型无需为宽版降频。宽版实现后5626 LUT/5184 FF/22 BRAM tile。接口延迟、实际时钟源及平台集成仍缺失，不能解释为实卡频率或加速证明。以下为此前阶段记录。

最新：[周期测量与宽codec实验](results/rtl_wide_codec_20261023.md)在相同真实小查询下将仿真周期减少21.56%，全部回归/故障对照通过；整顶层5684 LUT、5185寄存器、22 BRAM tile。代价为+383 LUT、+80寄存器、+1.5 BRAM tile；尚待实现时序和实卡验证。

最新：[闭合页槽与AXI状态端点](results/rtl_memory_endpoint_20261023.md)已通过19个真实小查询的77099条公开命令、6086次完整页传输及边界/故障测试；整体综合5301 LUT、5105寄存器、20.5 BRAM tile。页完成、地址退休和双域回收已由RTL闭合；仍无完整FPGA路由或实卡加速证明。

最新：[可综合记录级后备适配器](results/rtl_record_backing_20261023.md)已通过1144服务检查、4288记录核验和7项负例，整体综合2078 LUT、3035寄存器、18.5 BRAM tile。记录校验、内存响应与codec提交/中止已由RTL协调；页槽COMPLETE/地址RETIRE/双域fence闭环仍待完成，无板级加速结果。

最新：[页codec与AXI串接验证](results/rtl_page_codec_20261023.md)已通过独立5645检查、串接910服务检查和6项故障对照；codec综合1 RAMB18E2、965 LUT、1469寄存器。可综合总适配器与页完成/地址回收/fence协调仍待实现，无板级性能结果。

这是可独立继续研究的实验目录。现有 Python 语义样例、C++ 状态原语合成微基准，以及 FPGA24 `logicnets_jscl` 真实设计的完整串行 CPU 布线基线、阶段计时与访问轨迹。GPU/FPGA 后端尚未接入。

最新后备存储进展：[地址租约与AXI页服务](results/rtl_backing_axi_20261023.md)已通过905检查及默认容量综合，读错误突发排空问题已修复。该独立模块为18 BRAM、932 LUT、1416寄存器；仍待与页槽/codec/fence组合，线性目录需优化。当前容器XRT可见设备0，无实卡结果。

最新队列进展：[有界队列与有限fence RTL](results/rtl_queued_endpoint_20261023.md)已通过三组XSim、五个故障对照与综合；内部生成闭合队列排空条件，整体2 BRAM、2708 LUT、1653寄存器。实际内存完成与地址租约尚待接入。

最新RTL进展：[页传输端点控制器](results/rtl_page_controller_20261023.md)已通过边界/真实值XSim与综合，472,689条真实回放命令，2 BRAM、2,154 LUT、1,605寄存器；远端排空证明和实际DMA仍待实现。

最新进展：[实际五字段值采集与后备池先导](results/real_field_values_20261023.md)已通过完整CPU路由等价检查和逐读位模式核验；38查询/14047736次实际字段访问，hist独立观测。30 MiB固定字节池的完整真实值回放及终态审计已通过；首个页槽RTL已通过XSim及U280独立综合，映射2个BRAM，见[RTL报告](results/rtl_scratch_20261023.md)。此前[13 MiB合成值后备回放](results/bounded_backing_real_addresses_20261023.md)已全部通过；这些均不构成硬件加速数据。

新增 [身份校验先导](results/identity_pilot_20261022.md)：进一步压缩标签容量，但四组单次时间未改善。

方法迁移、成熟机制与未验证差异见 [RELATED_WORK.md](RELATED_WORK.md)。

## 研究问题与方法来源

按器件、设计、net 和 connection 生命周期组织状态，能否减少初始化、重复准备和主机—设备同步？

可迁移基础：FlightLLM 的中间状态复用；KV-Direct 的依赖跟踪与更新转发；已有 SparseLabels 分页与代次标记。

成熟方法的迁移可以成为主贡献候选。以具体机制、最近邻工作和受控实验判断贡献，不因为压缩、驻留、调度等方法已有基础而预先否定，也不预设加速比或发表结论。

最新 [78次正式报告](results/research_matrix_20261022.md)（过程见 [第二阶段记录](results/research_stage2_20261022.md)）：第二真实设计已接入，紧凑标签池通过语义检查，78次正式矩阵已完成并复核；四个唯一输出全布通，但第二设计存在待解释的RTSTAT-10警告。

## 从这里开始

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
python3 scripts/run.py benchmark --self-test-only --sanitize
python3 scripts/run.py benchmark
python3 scripts/run.py profile-real
python3 scripts/run.py benchmark-paged-real --skip-self-test
python3 -m unittest discover -s tests -v
```

原有 `check`、`plan`、`smoke` 仅需 Python 3 标准库。新增 `benchmark` 需要 g++/C++17，按 [state_microbench.json](configs/state_microbench.json) 运行五个状态实现、四类合成负载和三种页大小；默认 396 个样本，每个样本分别记录首次和复用运行。只在本目录编译提取片段，不启动 Vivado/CUDA，不修改原始工程。输出位于本目录 `results/`，指定 `--output` 也不会覆盖已有文件。

样例内容：稠密清零与有限位宽 epoch 标签执行同一组读写；覆盖搜索切换和 epoch 回绕。只统计逻辑操作。

Python smoke 仅覆盖单上下文标签。C++ 检查另覆盖页池增长、静止边界回收、独立上下文、epoch 回绕、同网分支引用与共享集重建；没有并发原子性、运行中页替换或 PathFinder 状态机。

`smoke --variant <真实变体名>` 仍明确报错。C++ 微基准通过独立的 `benchmark` 入口运行，结果为 `synthetic_state_microbenchmark`；其 CPU 状态阶段计时不是完整路由或硬件加速数据。

2026-10-22 完成首轮测量：[实验记录](results/state_microbench_20261022.md)。页内逐节点初始化在分散访问上减少整页清零开销，但串行标记对照仍最快；同网哈希引用索引没有显示整体收益，长局部访问也没有稳定改善。

同日完成 [真实路径实验](results/real_trace_20261022.md)：27,960 个 net、180,326 条连接，三次原始布线耗时 23.001–23.221 s，12 轮收敛，导出图检查无错误。记录 570,286 次搜索路径，抽样 1,113 次查询并补齐全部 19 次超大搜索。真实标签访问很稀疏，但首次标签分配仅约 42 ms；不能将分页槽位放大解释为加速比。详情、采样误差和验证边界见报告。

`profile-real` 使用 [real_trace.json](configs/real_trace.json) 和已导出的真实 RRT，需要先运行 `python3 adapters/build_real_router.py`；结果目录不覆盖。首次准备/后续分析命令见真实实验记录。`plan` 仍输出共享脚手架的候选实验表，真实基线通过独立入口执行。

继续完成了 [真实分页消融](results/paged_real_20261022.md)：三次重复中，逐节点 epoch 将同序串行分页从 57.428 s 降至 33.165 s，固定批处理从 50.635 s 降至 35.279 s；同调度输出与收敛一致、图验证通过。原始串行标记 24.389 s 仍最快，epoch 数组增加内存。入口 `benchmark-paged-real` 使用 `configs/paged_real.json` 和冻结构建 `build/paged_real_v2/`；没有匹配的语义检查记录时去掉 `--skip-self-test`，自动运行 ASan/UBSan 检查。

## 目录入口

| 路径 | 内容 |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | 假设、基线、消融、指标与阶段验证 |
| [INTERFACES.md](INTERFACES.md) | 数据、状态、结果与真实工具接入约定 |
| [NEXT_STEPS.md](NEXT_STEPS.md) | 下一次会话可以直接开始的任务 |
| [configs/experiment.json](configs/experiment.json) | 实验变体、指标和未设定的真实运行参数 |
| [configs/platform.json](configs/platform.json) | U280 DDR/HBM 平台计划，实际环境待记录 |
| [data/toy.json](data/toy.json) | 明确标为 synthetic_smoke 的小型输入 |
| [data/datasets.json](data/datasets.json) | 已接入真实设计与后续数据清单 |
| [src/reference.py](src/reference.py) | 可运行 CPU 参考例 |
| [src/state_bench.cpp](src/state_bench.cpp) | C++ 状态实现、微基准与语义检查 |
| [adapters/extract_state.py](adapters/extract_state.py) | 原始代码片段提取、行号和哈希溯源 |
| [scripts/benchmark.py](scripts/benchmark.py) | 编译、随机顺序测量、差分检查与结果保存 |
| [scripts/profile_real.py](scripts/profile_real.py) | 真实布线重复测量和输出一致性检查 |
| [scripts/analyze_real.py](scripts/analyze_real.py) | PC 采样、访问密度和路径事件检查 |
| [scripts/benchmark_paged_real.py](scripts/benchmark_paged_real.py) | 真实串行/批处理分页消融与内存统计 |
| [adapters/build_paged_router.py](adapters/build_paged_router.py) | 逐节点 epoch 与原始分页的隔离构建 |
| [adapters/README.md](adapters/README.md) | 真实工具适配入口 |
| [hardware/README.md](hardware/README.md) | 硬件模块与实现流程起点 |
| results/ | 本目录独立的计划和验证输出 |

## 现有代码与资料

优先阅读 main.cpp 的 NodeDyn、SparseLabels、gatherShareSet、flushDirtyToGpu 与资源提交函数。

- [cpp_router/src/main.cpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp)
- [cpp_router/src/gpu_route.cu](../_shared/assets/gpu_router_original/rewrite/cpp_router/src/gpu_route.cu)
- [cpp_router/include/gpu_route.hpp](../_shared/assets/gpu_router_original/rewrite/cpp_router/include/gpu_route.hpp)

- [RouterAcc RTL](../FPGA-Routing-main/FPGA-Routing-hw/src/astar_top.v)
- [RouterAcc 论文](../72_file_Paper%20(12).pdf)
- [DFMAcc 论文](../2026_ICCAD_DFMPM%20(2).pdf)
- [AccDRC 论文](../DAC2026_周茹平_最终稿.pdf)
- [完整研究报告](../FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [公共素材与溯源清单](../_shared/sources.json)

公开参考（框架建立时未克隆这些外部项目）：

- [FlightLLM](https://arxiv.org/abs/2401.03868)
- [KV-Direct](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/12/kv-direct.pdf)

## 当前推荐的下一步

补第二个独立设计，评估真实页粒度、紧凑槽位和回收策略。逐节点 epoch 已改善原始分页，但未超过串行标记且增加标签存储；保留这些对照与限制，详见 NEXT_STEPS.md。
