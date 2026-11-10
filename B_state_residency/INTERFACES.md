# 当前接口与验证范围（2026-10-29）

当前`route_stage_write_v1`候选调整route controller内部path和cp_stage银行的写入口。controller的`FACTORED_PATH_WRITES`与`FACTORED_STAGE_WRITES`默认均为0；候选adapter在实例化controller时显式将两者设为1。参数入口与实际接线见[controller](hardware/variants/route_stage_write_v1/fixed/route_commit_controller.sv)和[adapter](hardware/variants/route_stage_write_v1/fixed/route_commit_host_adapter.sv)。原CRC、取消、fault、漂移、握手、索引、last及重复节点保护保留，未增加流水周期；实际验证覆盖范围如下。

[十二单元例](results/route_stage_units_20261029.json)比较baseline/default/factored与原route、CP8、CP32、generic同拍回复刺激。八组完整事件、结束时间、path及stage字变化周期比较一致，generic行为保留。[完整CRC压力例](results/route_stage_system_crc_20261029.json)使用真实4槽、每路径32节点的系统连接，比较27份输出及结束周期，并保留CP/query/backend/capture原监视。监视器通过旧控制树计算期望银行，直接观察实际字变化，不读取候选新增的写事件信号。

完整fixture的path银行为4×32字；stage银行为4×39字，共156字。stage实测10次整组capture、1248次流式import、1259次检查；path实测18次单节点写、8次整银行发布、27次检查。检查在NBA后比较整个对应银行，覆盖本fixture观察到的写入时机、索引及数据。不是任意参数、任意输入或X/Z形式等价证明。该完整例的query CP edit计数为0，不能称完整系统编辑入口已被非空覆盖。

旧[十一源八场景矩阵](results/query_native_matrix_20261028.json)已完成8/8、216比较和实际恢复；这不替代CP/path/stage的新矩阵。stage综合已完成但仍待独立复审，[预读结果](results/route_stage_synth_preaudit_20261029.json)尚不能作为最终验收。所有完整实验入口与输出格式保持按各自冻结源码和审计器解释；新整系统物理测量、平台I/O预算、板卡行为及频率结论仍缺。任务顺序和唯一所有者见[NEXT_STEPS.md](NEXT_STEPS.md)。

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

## 可选源标签CRC绑定（2026-10-27）

CHECK_LABEL_CRC默认0，经三层传播至CHECK_SOURCE_CRC。新增snapshot_label_crc32，在backend recover受理时与其他snapshot_*字段锁存；leaf启动再次锁存。lr_source_crc32为已接收node32+五payload32 LE字的CRC32/IEEE（init/final xor ffffffff，poly edb88320）。启用时末条CRC不符返回新label status8，不写末条且不做checkpoint/verify；此前行可能已写，业务仍须隔离。成功仍须全部原生readback/receipt/retirement。默认关闭保留trusted stream行为，仅覆盖本仓库具名参数/端口兼容，CRC不是认证。详见hardware/variants/label_source_crc_v1/CONTRACT.md。

## 原生目录/标签快照研究接口（2026-10-27）

ENABLE_FRAME_SCAN默认0；只读scan_valid/ready/frame与独立rsp(status/frame/owner27/published)经实际层级连通，query root检查PC租约/退休，pager要求全部驻留槽刷回清空。label_snapshot_reader输出node32+payload160流，成功完成携带count/pages/CRC32；顺序为物理帧/slot，不保证node排序。状态1启动边界、2取消/退休丢失、3目录拒绝、4选定页未发布、5AXI读错误、6格式/边界、7状态错误。仅成功且回复消费后许可发布；恢复端源CRC强制绑定未实现。详见hardware/variants/label_frame_export_v1/CONTRACT.md。

## 运行中 owner 增量快照研究接口（2026-10-27）

新增 `incremental_owner_snapshot` 与 `owner_snapshot_checkpoint_adapter`，接口/限制见 hardware/variants/owner_snapshot_writer_v1/CONTRACT.md。命令握手锁存 source/destination/span/cookie，地址与长度64B对齐，目标须为准确基线 clone。实际 AW 范围形成累积 dirty 表（默认64行），一次一个源写事务；复制为源 R→独立 AW/W/B→目标 R 回读验证。busy包含保持的完成回复，适配层在cmd_valid或busy时封锁lease释放及manifest许可；成功回复退休后receipt才可用于发布，后续源AW使其失效。

status：0成功；1启动边界不安全；2运行中取消/lease或源退休条件丢失；3源写/跟踪错误或dirty满表；4布局/地址错误；5源读错误；6目标写回复错误；7回读错误/字节不等；8内部状态错误。此接口尚无持久化身份、原生epoch rearm或全状态目录导出。

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

# 事务围栏与静态切片真实接入通过（2026-10-25，优先历史）

详见results/transaction_fence_20261025.md/.json及transaction_fence_v1/CONTRACT.md。16主机/admin入口+route缓存/回复归属，允许既有expand必要续接排空，恢复回调逐端口pending；七AXI观察器。13隔离retired_idle出口区分故障锁存busy与真实owned/HLS未退休，97旧RTL/dat保持。11模型/5 HLS退休检查、32槽/单槽真实route10故障、16入口竞争94081–129186周期、全图像/AXI独立审计通过。

采用transaction_fence_static_v2：仅将捕获改为常量lane切片，与动态版事件/逐cycle/AXI/全部图像一致；绑定16字段OOC 6908 LUT/3040 FF、零RAM/DSP/latch，Tcl91.061s exit0，无route/Fmax/板卡。旧动态综合启动器超时后实际PID继续监督，静态版验证后主动停止旧变体，未伪报旧综合通过；开发和收据保留。

下一优先完整生产top抽取及新fence正常search/共享ripup回归，并补legacy owner/design/cost写日志与完整snapshot；目前checkpoint仍仅route提交范围，初始快照/CPU authority/标签流外部，不能外推任意入口失败。新五类观察器在本fixture闲置；续接为mock证据。恢复期故障、warm/frontier/path/created、unknown-page、价格回绕、容量与耐掉电/板卡仍缺，goal active。以下保留历史。

# 常驻配置快照与硬件恢复通过（2026-10-25，优先历史）

详见results/config_restore_20261025.md/.json及hardware/variants/config_restore_v1/CONTRACT.md。独立cold域驻留2304位六服务描述符，checkpoint17在正常route前装载；target reset后硬件按独立握手/响应退休重配，connection先于其余五lane，错误/取消不撤已暴露VALID。27恢复响应/37次load模型、32槽/单槽真实route10故障及手工六payload/七类AXI/全图像审计通过，成功重提交后load18，110原RTL/dat保持。U280 OOC 683 LUT/2520 FF、零RAM/DSP/latch，未route/Fmax。

下一优先统一生产top/全入口围栏、真实恢复期fault，再正常共享/ripup回归与完整checkpoint/search。初始可信descriptor安装、CPU authority/标签snapshot生产仍外部；不是完整自主snapshot读取。配置自身错误/超时当前仅mock，完整warm/created/frontier/path、unknown-page、实际价格与回绕、journal容量预约、耐掉电及板卡仍缺，goal active。以下保留历史。

# 硬件标签恢复真实接入通过（2026-10-25，优先历史）

详见results/label_restore_20261025.md/.json与hardware/variants/label_restore_v1/CONTRACT.md。新增512条缓存RTL服务，协调器直接启动/接收完成，OPEN/absent、328×5字段写、CHECKPOINT、328整条读回与排空均由硬件调度；TB只送snapshot流。30次模型响应含同实例复用及错误/取消/超时/流边界通过；32槽/单槽真实route五故障共10例恢复重提交及七类AXI/全owner/标签帧独立审计通过，110旧RTL/dat不改。默认U280 OOC 441 LUT/534 FF/3 BRAM、零latch/DSP，未route/Fmax。

下一优先配置回调硬件化、统一生产围栏与真实恢复期故障注入，再完整checkpoint/prepare/search。CPU authority和配置仍TB，外部快照集合完整性仍可信前提；absent仅单探针，非未知页/全图证明。新label服务错误/取消仅mock证据，完整warm/frontier/path、正常共享ripup回归、价格回绕、容量预约/耐掉电/板卡仍缺，goal active。以下保留历史。

# 恢复协调器真实服务接入通过（2026-10-25，优先历史）

详见results/recovery_join_20261025.md/.json。可综合独立journal/准入/reset/两遍owner修复接入真实pager/owner AXI，32槽/单槽共10故障通过；journal至少早于owner转发一拍，target reset不清日志。实际GET/DEC及第二遍验证后，新epoch2/version4标签absent探测、328重载/读回、恰6ACK重提交及checkpoint17→18通过。完整owner等于CPU q2准备态，七类AXI全字节与全部标签帧独立审计。110原RTL/dat逐SHA保持，隔离新adapter，源冻结recovery_join_sources_20261025。

下一优先把cfg/标签恢复回调迁为硬件服务、统一生产围栏并补新adapter正常共享/ripup回归；CPU authority/配置发包/标签重载当前仍TB，非完整自主checkpoint。容量需事先预留；没有完整warm搜索状态、unknown-page、真实价格/epoch回绕、耐掉电或板卡加速结论。完整checkpoint与prepare/search外层仍待研究，goal active。以下保留历史阶段记录。

# 可综合恢复协调器组件通过（2026-10-25，优先历史）

详见results/recovery_coordinator_20261025.md/.json及hardware/variants/recovery_coordinator_v1/CONTRACT.md。新增独立journal/准入/reset/两遍owner恢复FSM，权威refs非固定0；先修refs、再验证occupancy，支持同资源多net中间态。28次mock操作及交接/容量/身份/故障边界通过；同实例checkpoint推进后两次恢复。默认32项U280 OOC2187 LUT/2568 FF、零latch/BRAM/DSP，未route/Fmax。

下一优先把该模块接入真实10故障链（journal先于修改、target reset不清journal、实际owner修复），之后实现真实cfg/label回调与统一生产围栏。当前新协调器只mock组件，先前真实10例仍TB协调，不能互相替代证据。容量须事先预留，cfg_authoritative依赖外部真实snapshot，日志非耐掉电；完整checkpoint/search/unknown-page/回绕及板卡仍缺，goal active。

# 同实例提交checkpoint协调恢复通过（2026-10-25，优先历史）

详见results/route_recovery_20261025.md/.json。五故障×32槽/单槽共10例：排空/围栏后同DUT reset，journal真实GET发现副作用、DEC修复、再GET归零；query epoch2/price4/version4冷探测absent、328权威标签重载/读回后完整6ACK重提交。全owner最终均等于CPU q2准备态，未双倍INC；跨reset AXI字节严格重放通过，无文件替换/清owner/backdoor。生产RTL不改，恢复journal/准入/流程仍TB协调器。

此checkpoint只覆盖回溯提交操作标签/owner，不是完整search warm/created/frontier/path表恢复；已知328工作集、非回绕epoch/版本、无并发/实际价格变化或耐掉电保证。下一优先可综合恢复协调器和完整checkpoint，再prepare/search及unknown-page；goal active。

# 真实组合早完成缺口已隔离修复（2026-10-25，优先历史）

详见results/route_drain_20261025.md/.json。旧adapter在label RRESP2后native错误先返回、AXI仍余2拍即给完成；反例保留route_fault_counterexample_20261025。新route_commit_join_drain_v2加单挂起AXI观察器/backend_drained完成及admission屏障。32槽/单槽共10故障通过；owner B错误ACK0但物理已改1节点，取消/版本输入漂移ACK1改1，label/owner R错误不改owner。严格错误字节/排空及故障围栏审计通过。正常双query新旧全部周期轨迹、七类AXI及完整图像逐SHA一致。

旧成功基线保留，仅正常路径有效；需要上述故障保证时用显式drain变体，不可把native完成等同物理排空。观察器非通用多ID AXI；没有自动rollback/协调reset-reload恢复、真实超时/协议损坏或价格/epoch更新。下一优先统一生产围栏/权威状态恢复，再prepare/search外层与unknown-page，goal active。

# 可综合路径控制器真实服务接入通过（2026-10-25，优先历史）

详见results/route_join_20261025.md/.json。新增route_commit_host_adapter，原109RTL/dat不改+2模块，替换TB回溯提交循环：四条命令驱动实际16标签读/24owner修改及保存路径ripup。32槽/单槽两query447decision/293cost/879ACK与四阶段完整owner、CPU q3、328标签/120页/16384物理帧及七类AXI均通过；全部配置/control/expand/frontier/host冲突入口正常路径围栏测试通过。整体adapter资源/时序未测。

下一优先补真实组合故障/排空与统一围栏生产top，再迁移prepare/search外层和unknown-page生命周期。当前真实成功路径已接通，但外层search/prepare仍TB、328联合工作集CPU预知；core mock25项不能外推组合故障恢复，价格/epoch/altSink/板卡仍缺，goal active。

# 可综合回溯/路径提交控制器首版通过（2026-10-25，优先历史）

详见results/route_commit_20261025.md/.json及hardware/variants/route_commit_v1/CONTRACT.md。独立五状态RTL、两个保存路径slot，先验证整链再提交，ripup不重读prev；完整上下文/设计归属、背压故障排空。真实CPU payload+注册mock后端25项通过；U280默认MAX_PATH32 OOC综合2144 LUT/2924 FF、0latch/BRAM/DSP；仿真MAX_PATH8。未place/route/约束/Fmax。错误回复/取消可能已改owner，ACK计数不是副作用上界，无热重试/自动rollback。

下一优先将模块经host接口仲裁和全程lease接入真实pager/owner AXI，替换连续查询TB回溯提交循环，再验证共享/ripup及故障边界。当前只是组件mock与OOC，非真实后端/完整search集成；TB验证不等于可综合外层已完成。价格/epoch/unknown-page、自主search及板卡仍缺，goal active。

# 真实共享分支提交/ripup通过（2026-10-25，优先历史）

详见results/shared_ripup_20261025.md/.json。同实例q1/q2实际路径保存，第二分支提交与两分支依次ripup；共享554512/263946 refs1→2→1→0，occupancy1→1→1→0。24次真实owner修改B、四阶段48 GET、全owner图像及七类AXI独立通过；第二分支提交图像还与原Router sequence3全9089009节点owner字段一致，完整CPU路由hash保持。32槽/单槽447decision/293cost/879ACK均通过，109生产RTL/dat未改。最终owner恢复原始，label/design/history不清。

下一优先将TB实际回溯/路径保存/提交/拆除移为可综合控制器并补故障中断/完成屏障，再推进价格/epoch/unknown-page生命周期。当前仍TB调度、CPU预知328联合工作集，未覆盖价格更新/并发或板卡性能，goal active。

# 同实例同网连续查询通过（2026-10-25，优先历史）

详见results/continuous_query_20261025.md/.json。一复位/配置/初始328联合记录，同RTL实例q1实际搜索→7prev跳转→6真实owner INC→5标签准备写→q2实际搜索；无q2标签/owner/design重装。32槽/单槽均116POLL、114expand、447判定、293cost/OFFER、879ACK，两个末态及中间328准备态、完整design/owner/cost/16384物理帧和七类AXI独立通过；109生产RTL/dat未改。价格/存储epoch相同，仅完整搜索sequence1→2。

回溯/提交/prepare仍TB经真实接口调度，非可综合自主控制器；q2路径尚未提交。下一优先q2提交/同网共享引用与ripup，再迁移自主backtrace/commit，并继续价格/epoch/unknown-page生命周期。328联合工作集仍CPU预知，板卡/完整系统未实现，不宣称仿真周期为加速，goal active。

# 第二轮真实准备态 RTL 闭环通过（2026-10-25，优先历史）

详见results/followup_rtl_20261025.md/.json。Vivado2022.2同B会话，32槽/单槽均通过171POLL、170expand、853捕获/849判定、421cost/commit/OFFER、1263ACK及最后4child EARLY drain。实际sequence180327进入32bit visited，owner pool53734条真实AXI读，第二轮共享/overflow/history成本一致。完整822 native记录/403页、16384物理帧及全design/owner/cost和七类AXI逐字节审计通过；两配置label SHA相同。109生产RTL/dat未改，总周期1049101/1067253只仿真。

仍是从CPU准备态恢复一个后续query，非同一RTL实例前query提交/价格切换/后query prepare的连续生命周期。TB外层调度、CPU预知822标签工作集、未知页初始化、自主search/backtrace/owner commit和板卡仍缺。下一步优先同网连续query的实际路径提交与准备态切换，并明确unknown-page持久prev/距离标签规则；不要扩大当前证明范围。保持goal active。

# 后续成本/过滤及输入绑定通过（2026-10-25，优先历史）

详见results/followup_cost_20261025.md与followup_{q2,iter2}_inputs_20261025.json。query2/iteration2成本122/421次独立binary32重算；全history/价格/net/CPS1表通过，九文件actual search保持。iteration2有106共享调用、10overflow本net、26history>1、最大refs166；170expand全部warm hit，created不增加。独立warm/cold过滤通过，标签闭包194/822记录、75/403页；仍CPU预知工作集。region binder核验同一base和history/价格，将warm真实pool容量覆盖cost-only旧0占位。不代表多query RTL或unknown-page已完成。下一步接实际AXI/RTL后续query，保持完整32bit搜索sequence与2bit存储epoch分离，再推进多query切换/未知页默认值及自主search/backtrace/owner commit。

# Warm持久状态codec通过（2026-10-25，优先历史）

详见results/warm_state_20261025.md/.json及adapters/warm_state_v1/CONTRACT.md。两准备态各9089009行独立解码通过；iteration2恢复1647675 warm parents（1878空缓存）与53734 owner overflow entries。实际owner C++布局模型全primary/overflow GET及节点208292主owner删除提升/空闲链复用通过。只扩持久子集，不是完整cost/State表或RTL多query。prune关闭、静态type一致、度数<=32；pool恰满无新增容量余量；重复child以最早匹配位置恢复序列，非不可见位置身份。下一步扩完整cost/State codec、标签epoch/unknown-page策略及实际AXI/RTL多query验证，默认基线保持。

# 后续真实查询生命周期通过（2026-10-25，优先历史）

详见 results/followup_lifecycle_20261025.md/.json。logicnets sequence2及iteration2/sequence180327完整CPU路由hash保持，准备态独立恢复实际搜索的九文件逐字节相同。全9089009节点审计：首query末态→同网query2准备态仅9行变化，精确为6内部路径owner提交、target切换、source初始化。query2保留171旧标签/72 warm cache parents；iteration2有2467619旧visited、2439660非默认prev、50416 history>1/多net节点、53734 overflow引用、1647675 cache parents。present factor0.5→1.0。

这只是CPU持久状态充分性证据；未知页默认初始化、warm/overflow硬件codec及多query RTL尚未完成。不要随connection标签清除owner/history/children，不要把旧距离标签当有效，也不能无证明把prev=-1改成0。下一步明确持久prev与query有效距离的契约，扩codec/按需页初始化后做多query硬件闭环。保持既有首query/仿真周期收益适用范围。

# MCML自然查询RTL对照完成（2026-10-25，优先历史）

详见 results/mcml_parent_upstream_20261025.md/.json。MCML全图14991410节点/66907822边无损导出与独立成本/过滤通过；327children/326判定的自然EARLY正确drain未判定child124201（parent2178064）。四次基线/缓存32槽/单槽闭环通过82POLL/81expand/178cost/534ACK及完整状态。parent读取178→59；POLL窗口下降1.22%/10.92%，只是行为仿真单query。五归档已实际恢复，mcml_query_restore_20261025.json。

当前两个真实设计各首query，不是全设计FPGA布线或板卡加速。默认基线不提升，外层仍TB；label导入用CPU+oracle预知工作集，未知页按需初始化/跨query旧prev语义尚未证明。parent缓存只在排他lease内复用，lock gap/context/父子别名/fault必须失效。

下一优先：多query/价格生命周期，后续query的真实owner/overflow/history/旧标签与未知页默认初始化，先明确持久prev与距离有效性再扩codec/控制器。自主search/backtrace/owner提交和板卡仍未完成。保留已有仿真收益与OOC资源证据的适用范围，goal active。

# Parent缓存物理代价与MCML CPU oracle完成（2026-10-25，优先历史）

详见 results/parent_physical_20261025.md/.json 与 natural_mcml_query_20261025.md/.json。相同U280/10ns模块OOC：路后LUT2576→2683（+107）、FF1951→2117（+166）、CARRY8+18，BRAM/DSP仍0；两者内部setup/hold通过，WNS2.847/2.786ns。I/O939/771未约束、TIMING-18保留，不能称整机Fmax或板卡时序闭合。57文件物理归档含综合/placed/routed DCP，已实际恢复。

MCML首query已采集并精确CPU重放：index89391/id227074、net28747、source41486/sink41981、81expand/178搜索内push/82POLL；327 children而326判定，EARLY后parent2178064剩child124201未访问。14991410节点前后快照与9文件精确重现，完整48轮路由hash保持；尚无MCML codec/独立cost/RTL结果。

下一优先：导出MCML原RRT全图和硬件输入/独立成本过滤oracle，验证真实EARLY剩余child drain与父值缓存收益，不复用logicnets硬编码尺寸和读取范围。多query/生命周期、完整自主search/backtrace/owner提交及板卡仍待完成。默认基线保持，goal active。

# 帧内parent upstream复用已通过（2026-10-25，优先历史）

详见 results/parent_upstream_20261025.md / .json。隔离variant parent_upstream_v1，真实首query的parent读取171→58；32槽POLL窗口311297→306813（-1.44%），单槽378601→332917（-12.07%），功能与完整状态一致。这里只是仿真周期，未测板上/Fmax/资源；未替换默认post或基线。21项边界和原两层合成递归回归均通过，三个归档已实际恢复，证据parent_upstream_restore_20261025.json。

语义：缓存只在排他decision lease中有效，!decision_lock即清，与State缓存正常lock gap保持的规则不同。parent/context改变、fault/reset、自别名都不得用旧值；child.prev写ACK仍在读/缓存父值之前。active/version/design/query/price完整标签检查，absent父值不填充，lease内禁止任意并行写者。源码/审计固定parent_upstream_sources_20261025。

下一优先：综合资源/Fmax代价、MCML/多query和祖先恢复后仍有允许成本分支的递归测试，之后才考虑默认接入；自主search/backtrace/owner commit和板卡仍未完成。保持goal active，不把单例cycle收益外推为系统加速。

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

# 实际递归target/占用/共享三条件矩阵通过（2026-10-25，优先历史）

本轮在实际递归graph/metadata/access/native标签/geometry/cost/三ACK/OFFER链中完成3种target初态×32槽/单槽共6个主运行。机器汇总results/recursive_target_matrix_20261025.json，组合审计scripts/audit_recursive_target_matrix.py，实际恢复凭据recursive_target_restore_20261025.json。109份生产RTL/dat跨三条件逐SHA相同，本轮新增输入、TB与审计，不改生产RTL或旧已通过结果。

拓扑沿用明确合成逻辑0->{1,2},1->{2}，物理映射0,8,16,24,32，在33-node CSR中有28个无入边padding节点。目标标记设在逻辑2/物理16，而几何sink仍逻辑4/物理32；这是原算法target-marker条件测试，不代表已到达实际sink或完成连接布线。五条标签以实际host IO初始化prev=-1、node16.target=1，五个8-node页分开；heap另以fixture预置node24/key=3f800000。查询net0，资源CAPACITY=1。

| 条件 | owner主记录(key,refs,occ) | 查询net引用 | occupancy | 价格索引/值 | 共享因子 | EARLY/CLEAR | 祖先剩余兄弟 | node16 total bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| free 空闲目标 | (0,0,0) | 0 | 0 | 0 / 1.0 | 1 | 是 | 静态排空，无metadata | 4089999a |
| foreign 异net占用 | (2,1,1)，net1拥有 | 0 | 1 | 1 / 2.0 | 1 | 否 | 重新读visited77后SKIP | 40a9999a |
| shared 同net共享 | (1,2,1)，net0拥有 | 2 | 1 | 0 / 1.0 | 3 | 是 | 静态排空，无metadata | 40199999 |

owner key=net+1。shared将两个引用与一个占用net分开，不能把refs2当成occupancy2。foreign与shared均配置2个net，并保持cost.bin完全相同（price[1]=2.0），查询始终net0；free只配置1个net且未用的price[1]=1.0。不是单变量性能消融；所有几何、connection State、第一包成本完全相同，第二包23字输入只有count字段word1和实际price字段word4变化，其他21字逐位相同。没有收益、新颖性或路由质量提升结论。

CPU prepare_recursive_early.py / prepare_recursive_occupied_target.py / prepare_recursive_shared_target.py保持原Router递归/成本/标签push/8叉heap，新增成本与CLEAR前heap-size观测。去掉观测后逐字恢复既有observed Router；构造器/原State initializer保持，只在搜索前设定明确owner/target/price/seed初态。独立audit_*_inputs.py逐字段重建CSR/RRT32/设计/owner/成本/64B State/最终label，并逐阶段binary32重算每条件56个cost输入/输出字及CPU事件/POLL。原CPU fixture预置childrenCache，硬件从同拓扑CSR构建，因此仍只覆盖全部created、无复杂排除的构建条件，不是自然图动态过滤轨迹。

free/shared两组都验证：root(frame100,parent0)提交node8三ACK后立即下降；child(frame101,parent8)实际读取target16并判断不overuse，非空heap由seed-size1经CLEAR(status0,size0)清空。CLEAR回复严格早于node16.prev=8的native请求/ACK、parent upstream读取、实际geometry/cost、lb/upstream/visited三ACK与实际OFFER。node16全部三个成本ACK均保留target=1，parent8标签visited77/upstream3fa66666没有被heap CLEAR清掉。子OFFER成功后返回root，D日志显示remaining child16在controller NEXT_CHILD/early=1被直接消费，无第三次metadata/access/输出。只做2次候选判定，但静态expanded/raw计数仍3。

foreign两组相反：真实owner服务读出same-net refs0、occupancy1，目标被判overuse；没有任何CLEAR命令。实际prefetch使用price-index1/value40000000，目标成本total40a9999a；heap保留seed并达到size2。子树返回后root发起第三次metadata，实际VISITED返回77并SKIP。最终验证POLL按原CPU顺序先返回node24/3f800000，再node16/40a9999a及EMPTY。shared实际count2/occupancy1/index0/value3f800000，sharing-result40400000，total40199999（保留原逐步浮点舍入，不能替换成十进制2.4的另一个raw值）。free/shared CLEAR后只返回目标与EMPTY。

所有运行都把外部CLOSE和host label/design/owner请求排队在递归期间；围栏保持，内部CLEAR/OFFER仍可完成。每组2次实际递归扩展、2次成本/geometry、2次成本标签提交/6有序ACK、1次成本OFFER；seed OFFER另计。free/shared visited/metadata/输出各2次，foreign各3次；每组均消费3条静态children。最终checkpoint后五条完整160bit native记录（25字）与原CPU一致，node16.prev=8、visited77、target1，原其他节点状态保持；owner和history/price/net后备不被标签或heap操作清除。

主审计audit_recursive_early.py / audit_recursive_occupied_target.py / audit_recursive_shared_target.py核验完整事件顺序/ACK/成本/队列/全部AXI字节。各条件额外复用audit_recursive_join_backing.py：3145728B标签后备全部16384个192B页匹配原CPU五个已存在页和16379个全零页（允许分配器页位置置换），并有五个带node读回关联；每条件32槽/单槽最终labels.bin实际SHA也相同。证明文件recursive_early_backing_20261025.json、recursive_occupied_target_backing_20261025.json、recursive_shared_target_backing_20261025.json。

| 条件 | 32槽周期 | 单槽周期 | 32槽标签读突发/写回 | 单槽标签读突发/写回 |
| --- | --- | --- | --- | --- |
| free | 37127 | 38282 | 5 / 5 | 14 / 10 |
| foreign | 37288 | 38484 | 5 / 5 | 14 / 10 |
| shared | 37166 | 38285 | 5 / 5 | 14 / 10 |

每个标签突发3拍：32槽15读拍/15写拍，单槽42读拍/30写拍。周期只是仿真收据，不比较不同逻辑工作量的速度。free/shared的graph38读拍、design12读/2写拍；foreign graph44读、design13读/2写；各组owner6读、cost6读、State1读、table0读。owner640B和cost1280B完整保持。仍用FRAMES16384/INDEX14/HASH15与递归DEPTH4/CAPACITY32，只走两层，不是默认大目录综合或板卡可行性证明。

持久化：offer_archives_20261025下6个主包 early_inputs_v1、recursive_early_v2、occupied_target_inputs_v1、recursive_occupied_target_v1、shared_target_inputs_v1、recursive_shared_target_v1，共1395常规文件27171163B，逐成员和copy SHA核验。六个scratch目录全部实际移到.preserved后解包恢复1395文件；恢复后矩阵重新生成与原JSON逐字节相同。results的6个对应链接分别为recursive_early[_inputs]_20261025、recursive_occupied_target[_inputs]_20261025、recursive_shared_target[_inputs]_20261025；tmp丢失对索引运行restore_offer_result.py。最新MCP终态0/72.561s在recursive_target_completion_20261025.json。最初free v1普通检查已通过，v2只加D日志和drain计数断言、RTL不变；v1源/文本/log子集146文件235334B在recursive_early_history_20261025.*，不是主证明或大型binary的完整归档。

边界：owner refs/occupancy是显式初始快照，仅查询，没有更新同网多分支引用、增添其他net或触发overflow池（本例pool capacity0）。未证明真实网表自然搜索轨迹、复杂过滤、实际landmark/crossSLR、价格跨版本距离失效修复、实际满堆停止、联合故障排空/reset/reload、完整search/backtrace/owner提交或板上加速。下一优先任务从原真实CPU搜索采集可重放的递归事件、根前标签/owner/history和实际State快照，生成新递归oracle；不能把旧1216-parent无递归向量直接当新结果金标准。旧真实CPU矩阵及“原串行基线仍最快”等结论保持，研究goal active。

# 实际RTL递归汇合联合用例通过（2026-10-25，优先历史）

这次真正执行了后代的graph/metadata/access/native标签、geometry/cost、三项标签ACK与实际OFFER，不再只证明mock调度或无action2前缀。主结果results/recursive_join_20261025（recursive_join_v1）完整32槽/单槽均通过；输入results/recursive_join_inputs_20261025（join_inputs_v1）。CPU/接口生成prepare_recursive_join.py，输入审计audit_recursive_join_inputs.py；运行run_recursive_join.py，主审计audit_recursive_join.py，额外完整物理标签语义审计audit_recursive_join_backing.py。综合收据recursive_join_revision_20261025.json。

图是明确合成：逻辑0->{1,2},1->{2}，五个逻辑节点映射到物理0,8,16,24,32，坐标仍0..4，sink坐标4，33节点CSR含28个无入边padding节点。这样五个显式初始标签处于五个8-node页，单槽确实触发驱逐/重载。所有标签先用实际host native写prev=-1，以匹配原dense CPU初态；不是默认稀疏absent-prev=0的测试。所有类型NON_LOCAL，root Laguna，非crossSLR，landmark inactive，owner占用0、history/price均1、net center0/fanout1/doubleHPWL10。没有修改任何共享或原始基线。

CPU使用前轮完整原Router立即递归类/实际成本/原push/原heap；去掉新增纯cost观测后逐字恢复前轮observed source，构造器与State initializer保持，非cost事件与原5节点金标准逐行相同。原CPU fixture预先提供childrenCache；硬件从同拓扑原始CSR建立缓存，因此本例验证的构建条件是全部已created、无排除的简单条件，不代表复杂过滤/新建状态的递归组合已覆盖。RRT32、CSR、design/owner/cost、64B connection State及最终label镜像经独立逐字段重建；56个cost23输入/输出字还以逐阶段binary32重算。不是自然器件路由轨迹。

实际顺序：root(frame100)处理node8并提交lb/upstream/visited三ACK，action2退休后才启动child(frame101,parent8)；child处理node16并提交三ACK，然后实际OFFER(node16,total=0x4089999a)，成功退休后才恢复root对node16的metadata。此时真实VISITED读返回77，root以SKIP退休，没有重复入队或重新成本计算。主auditor检查E→seal→M→O→子E→子seal→子M→六次有序W/A→OFFER→子O→父M→V(77)→父SKIP及全部payload，明确区别于延后递归。

关键最终标签（物理ID，映射后的原CPU结果）：

| node | prev | upstream bits | total/lb bits | visited |
| --- | --- | --- | --- | --- |
| 8 | 0 | 3fa66666 | 406ccccd | 77 |
| 16 | 8 | 402ccccd | 4089999a | 77 |

node16成本输入里的parent upstream确实为node8刚提交的3fa66666；prev=8证明外层当前parent接线进入了实际postprev/commit。checkpoint后五条完整160bit native记录（25字）与原CPU一致，node0/24/32仍prev=-1且未visited。随后两次验证POLL返回node16/4089999a和EMPTY，再CLOSE；这些POLL是验证fixture，不是已实现的完整搜索循环，也没有到达sink32或完成回溯/占用提交。

两组各2个真实扩展、3次metadata/判定/visited读、2次实际geometry+cost23、2次成本标签提交/6有序ACK、1实际OFFER。实际root/descendant frame context及连接State通过原已验证组合；109份既有RTL/dat全部同SHA，本轮只换输入和TB，不改已验证递归core/top。TB在整次递归期间排队外部CLOSE以及host label/design/owner请求，全部被围栏挡住；内部OFFER仍完成，实际CLOSE只在最终验证后发到heap。因此覆盖了正常递归时queued-CLOSE与内部OFFER共存，不是故障恢复证明。

内存独立审计：graph44读拍/全1344B源镜像，design13读拍/2写拍/576B最终缓存状态，owner4读拍/640B与cost6读拍/1280B源镜像保持不变，connection State1读拍/64B，table0读。完整标签3145728B逐读拍/字节写掩码/B日志重放；另按原codec的bitmap8+8×160bit记录+zero tail，从CPU五条最终记录独立编码，全部16384个192B物理页多重集匹配5个有效页+16379个全零页，并以五个带node的native读回验证关联。额外证明是results/recursive_join_backing_20261025.json，不覆盖已归档的主审计。

32槽标签5个读突发/15读拍、5个写回/15写拍；单槽13读突发/39读拍、9写回/27写拍。不可把AR事务数与burst beat数混用。两组最终labels.bin SHA均为7605ac01a9c4462c48fed6e3a005d14fc1718323f40eb04eb54baa1292d9a374。周期37242/38150仅仿真收据，非加速指标；仍用FRAMES16384/INDEX14/HASH15、递归DEPTH4/CAPACITY32，只走两层，不证明默认大配置资源可行性或深度边界。

B原MCP同进程72.965s/exit0，receipt recursive_join_completion_20261025.json。两个主归档在offer_archives_20261025：join_inputs_v1为35文件693729B，recursive_join_v1为429文件8349727B；压缩成员与共享盘copy SHA验证，真实联合结果已移开scratch到.preserved后恢复429文件核验。restore_offer_result.py恢复原路径；tmp丢失需同时恢复输入和结果。先前所有通过的基线/失败记录保持。

下一步补带target EARLY与预置非空heap的真实递归用例：在原CPU逻辑node2置target并在其queue预置node3，使子树EARLY实际CLEAR先于prev/cost/标签/OFFER，root未处理兄弟应排空而不进入metadata，target位必须跨三ACK/驱逐保留。然后再扩至原真实图的新递归CPU轨迹；旧1216-parent无递归oracle不能直接沿用。非零owner/ref、复杂children过滤/多net生命周期、真实landmark/crossSLR、实际满堆停机、联合故障排空/reset/reload、完整search/backtrace/occupancy提交、综合与板卡性能仍未完成。研究goal active。

# 立即递归controller与当前parent接线（2026-10-25，优先历史）

新增hardware/variants/recursive_controller_v1/recursive_candidate_controller.sv及derive_controller.py/TB；新增candidate_recursive_v1/core/top及derive_core/top.py。控制器实际联接已验证expansion_capture/children_frames。OUTPUT退休action2后进入DESCEND，在父下一项metadata前压子帧；子frame完成后RESTORE从完整512bit context恢复父/cookie/prune/hasLaguna/flags/bbox，再实际发起下一项metadata/access。共享early使祖先只排空剩余静态项，不判定后续兄弟。每次operation保持同一net/sink/sequence/query/price/full version/design，并对漂移停机。frame cookie在单次根operation内单调递增，返回不回退分配counter，32bit溢出显式停止；不宣称跨根operation/重启全局唯一。

新增out_parent/out_root_cookie；实际新core把controller当前parent输出到外层held_parent wire，替代只在外部expand时更新的reg。postprev、commit的请求和身份校验仍使用held_parent，因此现在结构上跟随当前帧。连接级q_meta/q_connection/q_net/q_sink仍由根operation持有，递归不会重新加载或变更连接State。原capture/OFFER/成本/标签服务均未改；新core/top由此前冻结capture结果内存重建逐字审计。旧candidate_capture与先前通过的完整组仍保留。

有效组件results/recursive_controller_20261025实际recursive_controller_v3，run_recursive_controller.py / audit_recursive_controller.py通过7项：多子汇合（E0→O0,1→E1→O1,2→重新读root child2 visited1→SKIP）、三层嵌套、子树EARLY向祖先传播、九层链/逐层回返、空根；另cookie=0xffffffff需要下降时只停止、不发wrapped请求，以及输出持有时full version高位漂移停止。全部76事件与独立Python DFS/visited模型一致，完整metadata上下文、544bit候选/parent背压与197bit终态回复保持由TB断言。组件使用DEPTH16/CAPACITY4。graph/metadata/access/标签提交回调为mock；visited在非skip输出退休时由TB更新，不是实际native ACK。不得据此声称真实标签/成本/入队递归或联合故障恢复。

新controller result_count为所有帧已退休候选总数，result_expanded_count/raw_count为各帧完成计数之和，mask/hit只表示根帧，result_cookie为外部根cookie；out_cookie为当前frame cookie，out_root_cookie单独保留根身份。祖先EARLY排空项计入expanded/raw但不计入已退休候选。错误终态计数不承诺完整汇总。原非递归oracle不能直接套到包含后代的新输出。

实际完整链回归results/candidate_recursive_pilot_20261025通过160根扩展/169 metadata及判定/40真实geometry+cost/40成本标签提交/120ACK/40实际OFFER，920输入成本字和200输出字逐bit相同，73条队列命令/回复相同，完整3145728B标签后备检查通过。52份旧baseline、61份prior和6份center RTL保持核验。该前缀无action2，未走真实下降，不代表真实后代计算通过；新core functional DEPTH4/CAPACITY32也未验证九层硬件容量。audit_candidate_recursive_pilot.py强制limit<=160，明确禁止将旧oracle应用到新递归输出。旧无递归完整32/1槽门禁是candidate_capture_full_20261025，不是这版新递归top的完整矩阵。

负证据recursive_controller_v1由TB在赋新READY前记holding，误把已合法退休的输出当成必须保持，出现假失败；v2修正监控时序并加强完整回复/计数断言，RTL不变，五项正常通过。v3只增加两项终态测试（RTL仍相同）。历史27个源/文本/log文件22596B已逐成员SHA归档recursive_controller_history_20261025.*，不包含大型build。旧5项auditor保留audit_recursive_controller_v1.py。有效7项auditor和pilot auditor均绑定最终manifest及新controller SHA。

持久化offer_archives_20261025/recursive_controller_v3.tar.gz 37文件164553B，candidate_recursive_pilot_v1.tar.gz 289文件5460177B，成员及copy SHA核验；实际新pipeline pilot已移开scratch后真实恢复289文件验证。组合收据results/recursive_revision_20261025.json。check仅文件/配置可用，不当功能证明。

下一步必须建立真实后代的CPU/硬件联合oracle。优先复用明确合成5节点汇合图0->{1,2},1->{2}，原Router实际成本/标签/立即递归作为金标准，生成与实际graph reader、design/owner/cost、connection State ABI一致的小型AXI镜像，接本版完整geometry/cost/三ACK/OFFER与最终native读回，证明root后续兄弟真正读到子树提交visited、node2.prev=1及parent upstream继承，而不只mock测试。再加入EARLY与压槽回放，扩至原真实图脚本的新递归CPU轨迹。旧1216输入唯一action2在E304,parent5123419→6431273，两者原图degree都1，不能作为多兄弟证据；真实子节点也有1条边，不能假设空子帧。不要用旧heap/cost/label期望强行放行新递归结果。

联合abort/drain/reset/reload、配置lease跨所有帧、实际FULL停止/重放、landmark/非零owner与真实crossSLR、默认大目录综合及板卡性能仍未完成。组件的cookie溢出/版本漂移停止没有证明这些组合恢复。目标保持active。

# 封存children已联接实际候选/成本/提交/入队链（2026-10-25，优先历史）

hardware/variants/candidate_capture_v1新增candidate_capture_query_core.sv、candidate_capture_engine.sv、TB和derive_core/top.py。core从guarded commit core派生，仅在原expansion_controller与candidate_controller之间插入已验证expansion_capture/children_frames；metadata/access及其实际标签端口保持原接线。真实扩展请求较父请求晚一拍，因此expansion.enable改为已受理operation_pending且配置无错，不能继续使用要求!operation_pending的can_start。外层operation_pending/host/config围栏覆盖整个父操作，底层expander释放后仍不提前放开。capture fault进入组合fault，但联合故障排空仍未证明。

512bit帧保存12个连接/父字段及完整version32/design64/query/price，未缓存动态标签。实际metadata请求必须发生在物理expander完成、seal后，TB检查物理expansion.state=0及捕获适配器state=0；context父/cookie/完整身份与当前controller及外层版本逐项一致。独立auditor逐E/D重建384bit字段并验证保留位零、每帧完成children数以及S→M顺序。原cost/label/OFFER/journal全部保留。derive_core与derive_top均从先前冻结结果在内存重建逐字比较；其余53份旧baseline、62份prior与6份center RTL核验保持。

主结果results/candidate_capture_pilot_20261025（160扩展/169判定/40 cost OFFER）与candidate_capture_full_20261025（完整32槽/单槽）通过。完整每组1216 seal/3066次seal后metadata、702实际geometry+cost23/702成本标签提交/2106有序ACK/701实际成本OFFER/65非空CLEAR，195 seed另计。16146成本输入与3510输出逐bit一致；978条队列命令/回复与原CPU8叉堆逐字段一致，关闭前验证POLL仅4条有效输出，不是真实搜索POLL。最终checkpoint后436条标签/2180字读回一致。13个prior-commit visited skips等压力仍来自前轮脚本输入，不是本轮实现递归的证据。

完整后备标签3145728B及逐字journal核验；graph43888R（49短拍零填充）、owner1620R、cost2107R、tableR0；design145424192B/owner145433472B/cost36812672B后备全部核验。设计级owner/history未随标签清零；所有allowed owner仍为0，不能混称已覆盖非零owner组合。32槽label843R/1362W；单槽具体计数见revision JSON。周期仅仿真收据，不能宣称硬件加速。仍沿用受控4个SLL beginY修改及hasLaguna压力、landmark inactive/crossSLR0和跨扩展复用seq脚本，不是自然全连接搜索。

run_candidate_capture.py为运行入口；最终audit_candidate_capture.py包含seal计数、完整384bit context与reserved检查。先导最初auditor在归档前已通过并冻结为audit_candidate_capture_v1.py，其原SHA与归档保持；后来加强的先导复核单独保存candidate_capture_pilot_stronger_20261025.json，不覆盖归档source_bound_audit。完整组最终主审计使用加强版；completed_full_audit只是运行中中间审计，不作为最终manifest凭据。组合收据results/candidate_capture_revision_20261025.json。

尚未做递归：candidate_controller仍保留单parent pending，action2仍为回调。封存后每项重新实际metadata/access已接通，但没有子树挂起/返回，自然不能声称已验证返回后的标签重读。下一步除保存/恢复controller父context，还必须把当前parent送外层postprev/commit；现有held_parent只在外部expand更新，直接内递归会把根parent写给子帧。连接State的q_meta/q_connection/q_net/q_sink与frame cookie也须分离。详细契约hardware/RECURSIVE_INTEGRATION.md列出身份、立即下降、early传播、reply背压、FULL与联合恢复要求。真实landmark/非零owner/完整搜索回溯与板卡性能仍未完成。

持久化offer_archives_20261025中的pilot/full两个包，成员与copy SHA核验，完整组已实际移开scratch后恢复验证；精确数量与bytes见revision JSON。B同进程跨300s观察交还继续，无超时重启。研究goal继续active。

完整/单槽最终实测仿真计数（仅收据）：

{
  "full": {
    "cycles": 2453955,
    "label_R_beats_checked": 843,
    "label_W_beats_checked": 1362,
    "sealed_frames": 1216,
    "sealed_before_metadata": 3066
  },
  "pressure": {
    "cycles": 2470765,
    "label_R_beats_checked": 3639,
    "label_W_beats_checked": 3714,
    "sealed_frames": 1216,
    "sealed_before_metadata": 3066
  }
}

# 真实children扩展器整帧捕获通过（2026-10-25，优先于历史）

新增hardware/variants/recursive_frames_v1/expansion_capture.sv、tb_expansion_capture.sv、tb_expansion_capture_unit.sv；复用children_frames.sv（与前轮最终v2 SHA一致）。run_expansion_capture.py / audit_expansion_capture.py为真实图组合入口；run/audit_expansion_capture_unit.py为同RTL mock边界入口。主结果results/expansion_capture_20261025实际capture_v3；组件results/expansion_capture_unit_20261025实际capture_unit_v2。组合收据results/capture_revision_20261025.json passed。

实际组合保持42份原基线文件同SHA，原graph reader、persistent design、children HLS、paged exclusion与原CPU getChildren对照不变。新增捕获适配器先受理begin、保存完整请求和不透明512bit context，向真实expander发出稳定请求，接收完整352bit node/position/ordinal/attrs流；完成cookie/count/序号检查并seal后才回放静态children。每帧独立保存165bit完成回复。TB明确断言每条回放前适配器物理请求state=0且真实engine_busy=0，完整context相同。回放期间外层围栏继续阻止host/config类入口，不依赖已释放的真实engine busy。当前TB只对host ctrl/io及expand有显式额外围栏，其他配置本场景不发起；生产组合需统一全部配置/图生命周期lease。

先导16扩展/6 children通过。完整32槽和单槽各1212扩展/550缓存命中/662 build/3229 children/10753真实children服务/240 native读，CPU语义、全部事件与全部后备内存字节审计通过。graph19280读、design6109读/2500写；完整checkpoint2、label0读/18写；单槽checkpoint27、label15读/25写。周期484146/483559仅仿真收据，不是加速比较。TB functional FRAMES256、帧DEPTH4/CAPACITY32，实际输入原degree<=32；未验证大配置容量/综合。真实图脚本生命周期回放不是完整搜索。

嵌套定向测试使用同一适配器/帧RTL但mock expander：ITEM10:1→ITEM20:3→RESULT20→ITEM10:2→RESULT10；完整165bit回复在背压时尝试新请求仍保持稳定并拒绝新请求；请求暴露期间前端cookie/parent改变不影响已锁存字段。最终v3用result_offered锁定已对外呈现的完成回复，不能因后来的嵌套请求撤回VALID。尚未present时同拍请求可优先压子帧；一旦present，则先退休该完成回复，不能再将此时的请求解释成它的子帧。调用方应在最后一项退休后立即提出lookahead，在该完成回复present之前确定是否下降。原型expand admission同时要求result_ready=0，调用方不能常拉高result_ready再期望发起新扩展。这里尚无真实expander嵌套调用、动态标签重读、成本/提交/队列或完整递归调度证据。

接口限制：frame context不透明，适配器不自行校验active version/design漂移；调用方须覆盖完整身份并保持全查询lease。frames fault/abort后仍接收已开始捕获的物理输出直至完成；新的适配器未做故障注入，不能由上一轮帧组件mock排空外推到本组合恢复。未实现本地timeout/整体reset-reload协议。非零result status会使frame fault停机，不回放部分children，外层必须处理fault。深度/容量溢出同理，不能热重试已提交标签。

负证据：capture_v1触发旧TB忙时expand_ready禁止断言；v2在顺序回放入口添加显式expand门控（保留旧断言），普通回放通过，但没有完成回复present后的保持改进；有效v3修正该边界并重新完整运行，不能用旧v2替代。capture_unit_v1编译因item task漏seq实参失败，v2补实参后通过，RTL与真实v3同SHA。上述历史144个源/文本/log文件969720B压缩并逐成员SHA核验，results/capture_history_20261025.*；大型二进制/内存镜像未列入该历史包。

持久化：offer_archives_20261025/capture_v3.tar.gz为277文件5606949B，capture_unit_v2.tar.gz为35文件76525B；成员和copy SHA核验，真实capture_v3已实际移到.preserved后解包恢复277文件验证。restore_offer_result.py可恢复。下一步优先将captured frame消费接进candidate_controller的metadata/access路径，并在子树返回后重新实际读visited/parent upstream；再联接现有cost/commit/OFFER。当前只是成功解耦真实children生产与静态回放，尚未完成立即递归RTL，研究目标保持active。

# children静态帧缓冲RTL组件（2026-10-25，优先于历史记录）

新增hardware/variants/recursive_frames_v1/children_frames.sv与tb_children_frames.sv，脚本run_children_frames.py / audit_children_frames.py。最终有效结果results/children_frames_20261025指向frames_v2；results/frames_revision_20261025.json passed。XSim2022.2通过9项：三层嵌套/空子帧后恢复父游标、512bit上下文及352bit静态记录背压保持、帧槽复用无旧尾泄露、depth越界、children容量越界后继续排空producer、finish计数错、abort后排空、producer非零status、reset空帧及abort当拍屏蔽消费。其中嵌套和复用消费顺序10:1→20:3→10:2→40:4。frames_v1为早期8项通过结果，未覆盖abort同拍屏蔽；final v2增加!abort准入并保持首错码，不能把旧v1推广为该边界通过。未改旧成功组合/原始/shared基线。

协议：begin携带不透明完整父context，成功受理后下一拍capture_active才能启动上游expander（depth溢出begin仍可受理报告fault，但不会进入capture_active）。capture阶段接受有序child_record，每条352bit预留node/position/ordinal/attrs；finish携带已输出children计数与status，必须匹配已捕获数，不是raw图邻接数。child与finish应串行；同拍finish优先，child_ready=0。整帧成功封存后才允许item消费，item_ready只推进当前帧游标；父项推进后可begin子帧。子帧frame_done后pop恢复父游标。begin/pop必须互斥，当前二者同时提出不受理；frame未耗尽不允许pop。异常后fault保持，已暴露capture继续接受children并丢弃直到finish；不提供热恢复，reset为独立组件清空。捕获无本地timeout，集成时需统一watchdog/abort与物理排空；不能只重置本模块忽略其他在途服务。

动态标签不存入本帧。恢复后visited/access/prev/upstream必须由后续控制器重新实际读取。本轮mock producer组件没有标签服务，因此尚未证明动态标签重读，也尚未接真实graph expander、State、owner、cost/commit或实际frontier。仍需改造candidate_controller，将捕获和逐child访问分开，再把本帧接入立即递归调度；只加帧存储不能自动消除现有operation_pending限制。上下文宽度参数必须包含完整query/price/version/design及父连接State；512bit只是组件默认，集成须按实际字段核算。图/配置生命周期lease需覆盖所有挂起帧。默认DEPTH64/CAPACITY256未做综合或器件容量可行性证明；本次只测试DEPTH3/CAPACITY3，不代表64层RTL已测或资源已定。

归档results/offer_archives_20261025/frames_v2.tar.gz：33常规文件54097B，成员和共享盘复制SHA验证，并实际移走scratch后解包恢复33文件验证。目标继续active；下一步优先接真实expander捕获及新逐child控制器，不停留在独立组件。

# 显式父栈递归语义参考（2026-10-25，优先于历史记录）

上轮实际成本OFFER为已验证进展。本轮新增scripts/prepare_iterative_recursion.py与audit_iterative_recursion.py；结果results/iterative_recursion_20261025，组合收据results/iterative_revision_20261025.json。完整原Router立即递归与显式软件父栈在40个明确合成图上事件、所有成本标签及完整POLL输出逐行一致：1305次扩展、1926次push、2446次visited skip、421条POLL输出；2560条最终label记录。case0沿用多子汇合反例，case1为64层全lookahead链，其余为固定LCG生成的有环/汇合图，偶数case设node63为target。不是自然设计搜索或真实硬件调度证明。

变换只改变调度：push完成原三条标签赋值后，lookahead写iterative_child而不直接递归。每帧保存node和next；先把next推进，再完成当前child判定/提交，若需lookahead就压子帧。每轮从栈顶重新执行原visited/access/成本路径，不能缓存后续兄弟的访问结果。子树返回后父帧继续；共享earlyTermination令祖先逐层退出。独立auditor逆变换恢复整个原observed Router源码逐字一致，并绑定前一轮已审计observer源；完整成本函数/原heap未改。当前软件vector栈无容量上限，不证明硬件溢出/abort/排空。

现有RTL阻碍已从source确认：candidate_pipeline_v1/candidate_controller.sv以operation_pending覆盖整次父扩展，NEXT_CHILD直接持有e_out，OUTPUT退休才让expander继续；candidate_commit_query_core.can_start要求!operation_pending。因此把action2反馈成新expand会被父pending阻塞，不能仅在top增加反馈线。下一步需将有序children捕获与逐child判定解耦，使expander在进入递归前可归还；保存父游标/连接State/元数据身份，恢复后重读动态标签。可选实现为先捕获完整父children静态记录，再逐child消费；父缓冲和栈容量必须有显式越界停机，不能丢弃已提交标签或冒充成功。当前尚未实现这项RTL改造。

持久化results/offer_archives_20261025/iterative_v1.tar.gz为24个常规文件934538B，逐成员/压缩包复制SHA核验并实际移开原目录后恢复验证；旧目录.preserved留存。继续研究goal active。先前FULL实际满堆、外部CLOSE定向组合及完整搜索/回溯/板卡性能等缺口仍在，不由软件栈对照覆盖。

# 实际成本入队与递归顺序对照（2026-10-25，优先于历史记录）

当前可复核top为 hardware/variants/candidate_offer_v1/candidate_offer_engine.sv。实际cost23成功及lb/upstream/visited三项native ACK后，action1使用实际total/node进入同一个8叉frontier；action2只返回lookahead回调，不入队，尚未实现递归硬件调度。cost_offer拥有完整query/price/version32/design64身份与背压/排空状态；成功回复退休前禁止变更。外部CLOSE排队不能挡住当前decision必要的内部OFFER；该并发场景尚需定向组合测试。

results/candidate_offer_pilot_20261025与candidate_offer_full_20261025均通过source-bound审计。完整32槽和单槽各1216扩展、3066判定、702实际cost/label提交、2106有序ACK、701实际成本OFFER，65非空CLEAR。195条seed OFFER单独统计。每组978条完整队列命令/回复与原CPU DaryPQ(arity8)逐字段一致；checkpoint前后SIZE及关闭前验证POLL也在对照中。只有4条有效条目在关闭前被POLL，其余大多被EARLY CLEAR清除；这些POLL是验证fixture，不是真实路由搜索调度。峰值50，不构成真实满堆测试。成本输入16146字/输出3510字逐bit一致，全部3145728B标签后备及checkpoint后436条最终记录/2180字保持检查；设计级owner/history不随标签清零。周期2447921/2464419仅为仿真收据，不能宣称FPGA加速或全布线等价。输入仍是受控SLL几何和跨扩展脚本seq压力，详见下方历史。

scripts/audit_candidate_offer.py、audit_offer_trace.py、audit_offer_heap.py为当前审计入口。heap参考在results/offer_heap_inputs_20261025，原CPU堆体原样提取并以独立Python堆重放核验。guarded commit_v2 core保持不变。full批同一Vivado进程624.891s、exit0，300s仅观察交还，没有重启。

results/cost_offer_unit_20261025通过16项mock-backend组件测试并由audit_cost_offer.py独立校验：正常与原始key位保持、七种错回复、合法/不合法FULL、abort暴露SEND/等待回复排空、timeout、version高位漂移、成功回复后late设计身份故障、idle异常回复。FULL已在标签提交之后，必须停止；不做静默丢弃/重试/回滚。FULL仅注入组件，尚无实际满堆组合或联合AXI故障恢复证明。

results/recursion_order_20261025是明确合成5节点汇合图0->{1,2},1->{2}，使用完整原Router类/实际成本方法。audit_recursion_order.py去除纯observer后逐字恢复原source；deferred只改一处立即递归调用。立即递归使node2 prev=1,total=0x4089999a并入队一次；延后递归使prev=0,total=0x40400000且队列为空。这证明不能先完成父节点所有兄弟再处理lookahead。recursion_v1因Config未显式初始化被拒绝，仅留负证据；有效v2显式设定原0.8权重。这不是自然图样本或硬件递归通过。

下一步：实现可挂起/恢复父上下文的立即递归调度，恢复后重新检查动态标签，并用上述多子汇合对照验证；另补外部CLOSE排队/实际满堆停机定向组合。父expander当前pending限制需要真正解决。联合故障排空/reset/reload、真实landmark数据、非零owner与当前组合、默认大目录综合及板卡性能仍未完成。研究目标保持active。

归档入口scripts/archive_offer_result.py / restore_offer_result.py，持久化results/offer_archives_20261025，包含heap、pilot、full、unit、recursion五组逐成员SHA核验压缩包；最终归档清点见results/offer_revision_20261025.json。旧commit结果与源码不覆盖。

[成本标签提交契约](hardware/variants/candidate_commit_v2/CONTRACT.md)：实际cost23后按lb/upstream/visited写ACK，visited=route sequence；新版拒绝fault/坏身份/非零cost status后启动提交。完整/单槽702提交、2106 ACK及checkpoint后436记录五字段读回一致。13组件边界与2成本回复注入通过；不等于联合AXI恢复。成本OFFER/立即递归、全路由和板上仍缺。

[内部23字成本契约](hardware/variants/candidate_cost23_v1/CONTRACT.md)：实际State/owner/history/price/net及post-prev结果形成packet，经geometry_step和exact cost_step，713实际调用在完整/单槽逐位通过；保持完整版本/design归属与背压。当前profile landmark inactive/crossSLR0，额外mock分支不替代真实跨SLR联合验证。尚无lb/upstream/visited提交、OFFER/立即递归或板上收益。

[每扩展连接State契约](hardware/variants/candidate_params_v1/CONTRACT.md)：expand_connection绑定真实全局连接索引，每扩展读取一次不可变64B State参数；完整身份及独立profile revision，metadata先于post-prev与输出/空result退休。pending/busy加入统一围栏。完整32槽/单槽及2048拍延迟功能门禁通过；尚无23字成本计算/标签提交/递归或新联合故障恢复、综合与板上收益。

[METADATA_CONTRACT](hardware/METADATA_CONTRACT.md)：以父/child/sink实际图META和child设计GET生成448位Config14；外部仅提供连接选项及BB，不直接提供dead/static flags。created合并、claim发布和整个快照排他、三个N一致性及token耗尽已验证；owner配置和query上下文仍是上层输入，实际children/access串联待做。

[ACCESS_OWNER_CONTRACT](hardware/ACCESS_OWNER_CONTRACT.md)：kind4/6已经接实际owner AXI存储；桥快照完整身份、验证raw cookie，host_owner命令与整个child至最终回复退休排他，CLOSE/CP不清设计计数。功能、默认容量整合故障/冷扫描及零组合环综合已通过；Config14生产、跨区域设计配置一致性及完整搜索仍待接入。

[OWNER_AXI_CONTRACT](hardware/OWNER_AXI_CONTRACT.md)：实际GET/INC/DEC和三块外存记录，正常回应等待最后成功B；错误时保持已暴露AXI VALID，排空当前单拍后停止，半提交不回滚，需系统协调和设计后备重载。功能/22故障/默认零组合环综合已通过；kind4/6完整身份桥及与access_fabric的整个child排他联调待做。

[OWNER_STORE_CONTRACT](hardware/OWNER_STORE_CONTRACT.md)：16B primary/16B pool/16B allocator，引用按net计数、占用按不同net计数，主owner删除晋升并回收条目；池满、引用/占用耗尽显式失败。CPU更新计划和最终后备文件验证已通过，实际AXI握手、最后B后回应及错误部分写入停止待实现；不能将CPU原子commit解释为硬件回滚。

真实owner接口的初始化证据见[占用观测报告](results/owner_profile_20261024.md)：设计加载时先给sink及已有路径增加引用，不能随connection标签清空。后续kind4/6应读取设计级不同net占用和同net引用，增减/晋升及外部存储提交须保持原语义；样本峰值不构成硬件容量保证。当前占用后端仍未实现。

[ACCESS_FABRIC_CONTRACT](hardware/ACCESS_FABRIC_CONTRACT.md)：v3以access_pending寄存器持有整个child判定至最终响应退休的共享端口所有权；visited/target/prev接实际分页IO，ENDY/SLR/PREV_TILE接实际坐标服务，owner kind4/6仍为外部接口。默认服务预算524288拍包含目录冷初始化规模；所有故障停止，设计占用/history须独立于标签生命周期。实际功能/故障/默认cold与零组合环综合已通过，平台及物理owner后端尚未接入。

[访问性驻留服务](results/access_service_20261024.md)已自动完成46656个child判定、195175次实际HLS调用和148519次动态请求；全量顺序/结果、720收集排列及96个复位偏移审计通过。实际综合1675LUT/2687FF，零RAM/DSP/组合环，未布线。动态后端目前为参考轨迹模型；下一步接实际标签/坐标/占用共享服务，尚无完整路由或板上收益结论。

[坐标服务](results/coordinate_service_20261024.md)已接通实际图/表读取和分页标签：真实23957、合成与压力各740请求，覆盖全部11520个真实SLL；57项组件边界及7项实际组合故障/恢复通过独立审计。保留空prev0与dense默认−1差异，前驱只读静态endY。完整服务实际综合17873LUT/14570FF/375BRAM/3DSP，零组合环，未布线。下一步是访问性状态机与动态服务的驻留连接；仍无完整FPGA路由或板上加速结论。

# 可访问性决策接口（2026-10-24）

[SEARCH_ACCESS_CONTRACT](hardware/SEARCH_ACCESS_CONTRACT.md)：显式START/ADVANCE、20输入/6输出的access_step，11类条件动态请求，action0skip/1queue/2lookahead与target early CLEAR标志。原动态读取顺序及实际RTL通过；真实服务、query归属/代号/超时/复位包装与递归执行器仍需接入。

---

# 整数几何接口（2026-10-24）

[SEARCH_GEOMETRY_CONTRACT](hardware/SEARCH_GEOMETRY_CONTRACT.md)：13个int32标量输入、4个u32输出status/dx/dy/distance；status1无可用柱、2范围、4负长度，失败停止。原函数定义域/宽整数oracle及实际RTL通过；坐标应在prev写入后获取，不可复用访问性阶段的SLL endY。尚无查询归属包装、表读取和完整搜索联接。

---

# 代价调用服务接口（2026-10-24）

[COST_SERVICE_CONTRACT](hardware/COST_SERVICE_CONTRACT.md)：`cost_service_v2`23字输入握手快照、5字按址收集；ready前写出合法。外部active/query2/price4保持至退休、cookie32回显；status0正常/1inactive/2owner拒绝。1024拍计算超时，背压不计时；故障停止、已给响应稳定但须fault0，协调cold reset恢复。实际核联调/复位及完整服务综合通过，几何、价格与全搜索仍缺。

---

# 数值代价接口（2026-10-24）

[search_cost/ARCHITECTURE](hardware/hls/search_cost/ARCHITECTURE.md)：当前exact_v2顶层cost_step，23个32位输入字/5输出字，ap_ctrl_hs+双读/双写ap_memory。ap_ready与done在最终状态，输出早于ready，不能套Frontier collector；需快照、输出地址/重复校验、全字+done、query/price/cookie归属及复位故障包装。实际RTL数值门禁通过，原nativefloat准入失败。几何、价格服务与搜索副作用不属于该算子。

---

# 搜索代价与CLEAR接口补充（2026-10-24）

[SEARCH_COST_AND_SCHEDULE_CONTRACT](hardware/SEARCH_COST_AND_SCHEDULE_CONTRACT.md)记录浮点阶段、prev相关SLL坐标、首次push置visited、目标先CLEAR后offer及递归调度。Frontier当前v3新增op5：匹配active owner的查询内CLEAR，size0但不释放owner；不能由标签checkpoint触发。纯float helper尚无HLS证明，其余完整搜索服务仍待接入。

---

# Frontier查询服务接口（2026-10-24，优先下方历史）

[FRONTIER_SERVICE_CONTRACT](hardware/FRONTIER_SERVICE_CONTRACT.md)：单请求、boot自动CLEAR后ready；OPEN0/OFFER1/POLL2/SIZE3/CLOSE4，query2/price4归属，cookie32回显。OPEN/CLOSE等待真实CLEAR，页checkpoint不清堆；collector收齐四输出和done。容量65536，FULL2/EMPTY1正常，故障停止、已给响应稳定但须fault0；协调cold reset清旧流量后boot CLEAR恢复。尚未与外部查询/搜索控制器联接。

---

# 真实扩展组合接口（2026-10-24，优先下方历史）

[NODE_EXPANSION_CONTRACT](hardware/NODE_EXPANSION_CONTRACT.md)：expand(cookie/parent/prune/hasLaguna)→有序out(node/原始position/sequence/attrs256)→最终result(count/raw_count/mask/hit/status)。真实META决定count；CLAIM外层owner先于HLS generation，图/设计/排除另用每命令token，全部不回绕。整个扩展含重放/输出背压锁住host ctrl/io，pending主机回复也阻止新扩展。初始created合并、完整sink初始化、PUBLISH成功B后重放、晚到fault字段稳定但须检查fault。三路独立AXI（graph/design64、labels32）；平台聚合、布局布线、搜索/提交仍缺。

---

# 设计级持久记录接口（2026-10-24，优先下方历史）

[DESIGN_STORE_CONTRACT](hardware/DESIGN_STORE_CONTRACT.md)：一次base64/N配置；16B/node(flags/count/mask/reserved)，独立于query标签生命周期。GET/CLAIM/CREATE/DEAD/EMIT/PUBLISH/SINK，owner排他、空缓存valid、原始位置位图保序/重复、PUBLISH成功B后释放claim。32位置上限明确拒绝溢出。created须与图初始标志合并，sink须真实输入适配；CLAIM外层owner在HLS START之前分配。无多主/热取消/故障重滤恢复，B错可能已经写物理字节，协调终止设计后重启。

---

# 真实图AXI服务接口（2026-10-24，优先下方历史）

[GRAPH_READER_CONTRACT](hardware/GRAPH_READER_CONTRACT.md)：一次不可变64位三表基址配置；META读实际CSR start/count+属性，CHILD校验index后读原序child+属性，回显cookie/parent/index。全256位原始属性保留，单请求/单64B AXI读拍，跨offset边界两拍。输入错误拒绝、AXI/图损坏/无归属R停止；回复背压稳定，成功必须同时status0和fault0，协调冷复位。当前独立模块尚未接构建服务，不提供动态created或过滤缓存。

---

# 首次构建引擎接口（2026-10-24，优先下方历史）

[children_build_engine契约](hardware/CHILDREN_ENGINE_CONTRACT.md)：构建请求/最终结果、带generation/parent/position/phase/node/query/price归属的服务请求/回复、busy/fault。11路HLS输出和done完整收集后才推进；busy保持至最终结果退休。服务错误、错回显、异步fault明确停止；已提供结果保持，外层同时查status与fault。服务最早在请求握手后一拍回复。当前没有实际图/设计/缓存服务，busy须由整合层用于封锁整个构建的查询切换与相关标签修改。

---

# 首次过滤HLS命令接口（2026-10-24，优先下方历史）

[children_step协议](hardware/hls/children/ARCHITECTURE.md)提供START/RESPONSE/SNAPSHOT；11输出须完整收集，服务回复匹配build generation/parent/query/price/position/phase/node。服务错误锁存fault且禁止继续，PUBLISH应答前active保持；SNAPSHOT的status0不代表fault0。原helper语义不变，静态state冷复位已实际RTL验证；没有在线取消/旧回复跨复位隔离。整合层须锁住整个首次构建上下文，设计缓存hit不重新调用过滤器。服务仍为模型，尚未接图/缓存实际存储。

---

# 首次邻接过滤服务边界（2026-10-24，优先下方历史）

[首次过滤契约](hardware/CHILDREN_FIRST_TOUCH.md)定义NEXT/EXCLUDE/CREATE/CLASSIFY/EMIT/结构死端检查/发布请求。CPU helper已完成原函数与全真实路由对照，硬件控制器、图读取和设计状态存储尚未实现。CREATE先于类型/死端丢弃；缓存发布后跨查询保留，空缓存有效，不能在驻留淘汰后以重新过滤替代后备保存。设计级created/dead/过滤缓存和查询级标签分别管理。硬件服务需另补归属编号与失败恢复协议。

---

# 自动换页整合接口（2026-10-24，优先下方历史）

[auto_pager_v1 契约](hardware/variants/auto_pager_v1/CONTRACT.md)新增 `paged_exclusion_engine`：OPEN/CHECKPOINT/CLOSE 生命周期、通用标签 IO、串行边判断与 AXI512。顶层边和 IO 隐含当前 query/price；只有边引擎静止时接受生命周期和通用 IO。解析租约与所有原生命令由内部 `resident_page_manager` 独占，缺页执行 WB/RELEASE/BIND/RF，失败停止且保留未完成租约和脏页。

默认32槽、TX16、binding16、163840帧、目录epoch16。事务预算和绑定编号上限均触发安全自动 checkpoint，保留后备页、不重置HLS边编号；CLOSE完整回收查询。空记录0、显式prev=-1、有效全零记录与动态created分别处理。当前AXI为32位相对地址，未接已有独立64位基址包装层；没有并发访问/热取消/跨时钟域协议。五组仿真及边界/故障审计见[实验报告](results/auto_pager_20261024.md)。下方“尚无自动分页”仅描述旧版本。

---

# 实际排除边引擎接口（2026-10-24）

最终[exclusion_engine_v4契约](hardware/variants/exclusion_engine_v4/CONTRACT.md)：输入边cookie、父子node、flags/created/Laguna、query/price；串行执行START、条件标签读取与RESPONSE，返回判断或显式错误。status=0且fault=0方可使用excluded；错误后除非法输入外须协调排空/复位。外部页解析/租约接口仍保留，自动分页未实现。

必须采用新state-reset HLS，旧默认control复位不能清静态Controller。ap_start不得由含ap_ready的组合fault反馈驱动。详见[HLS复位与调用勘误](hardware/HLS_RESET_BOUNDARY.md)及[整合验证](results/exclusion_edge_engine_20261024.md)。既有页大小/原生opcode与标签字段布局不变。

---

# 新增排除标签桥接接口（2026-10-24）

最终使用[exclusion_label_v2契约](hardware/variants/exclusion_label_v2/CONTRACT.md)与[同拍故障修订](hardware/variants/exclusion_label_v2/REVISION.md)。串行node/generation/phase/query/price请求先解析页与独立token，再发原生READ。回复必须status=0且fault=0方可提交HLS；fault当拍可见、锁存后须协调冷复位。边generation32、读取token32与页binding16是三个独立编号域。解析器须持有页租约直到响应退休，自动换页仍未实现。

---

新增独立变体契约：[稀疏写回](hardware/variants/sparse_writeback/CONTRACT.md)。内部存储READ_MASK=6、WB起始响应mask、仅有效EXPORT；公开原生端点与192B页/AXI接口不变。直接控制器调用需遵循新WB位图协议，默认RTL不变。

目录EPOCH_BITS6→16候选仅扩展内部frame_index标签和计数器；TX/GEN、页格式、公开端口及CHECKPOINT语义不变。16位先导、65536回收、故障/阻塞和内部物理已验证，完整38查询待终态；合法FINISH FENCE_WAIT必须重试，不计作一次成功目录回收。

# 当前组件接口（2026-10-24）

[原生候选契约](hardware/NATIVE_CANDIDATE_CONTRACT.md)明确32槽/8节点页/192字节、公开CHECKPOINT和32位相对地址；[地址64契约](hardware/ADDRESS64_CONTRACT.md)为另一个一次性基址包装层。原生组合全38/物理/重建已验证，地址层仅19查询/综合/物理；两者均非完整路由器或平台闭合。旧宽页契约与历史结果保留，不混用端口或opcode定义。

# 方案 B 数据与接口

新增[完整大查询流式验证](results/rtl_streaming_large_20261023.md)：DUT接口不变，期望页流式读取；v1因测试台watchdog位宽失败，v2修正并通过小查询等价回归，完整7查询重跑中。显式时钟壳虽完成布线，仍缺上游时钟/物理接口上下文，不能把delay覆盖检查当作模型完整。

新增[索引端点组合契约](hardware/INDEXED_ENDPOINT_CONTRACT.md)：原宽codec服务/端点只替换目录并透传参数，回绕清表必须受顶层fence保护；19小查询完整字节/协议回放与默认容量整体综合已完成。

新增：[显式时钟壳契约](hardware/CLOCK_SHELL_CONTRACT.md)声明研究用BUFG时钟/接口预算；配对实现仍在运行，未宣称时序闭合。[有界目录索引契约](hardware/INDEXED_DIRECTORY_CONTRACT.md)保留frame地址、owner/published与租约语义，新增探测回退及epoch回绕清表；独立语义/综合已验证，尚未集成总端点。

新增[OOC配对实现的时序边界](results/rtl_codec_timing_20261023.md)：本轮接口/RTL未变，624输入与788输出缺少外部延迟，HD.CLK_SRC未设置。内部10ns时序检查不替代真实上层时钟/接口预算；RTSTAT-10未豁免。

新增[宽codec变体契约](hardware/WIDE_CODEC_CONTRACT.md)：内部按64×136位整记录存储，外部页格式与提交/中止约束相同，padding检查仍必须执行。[配对报告](results/rtl_wide_codec_20261023.md)给出周期与整体资源代价。

新增[闭合状态端点接口](hardware/MEMORY_ENDPOINT_CONTRACT.md)：公开命令不含EXPORT/BEAT/COMPLETE，4位响应区分后备缺页/满/故障；内部完成页提交→地址RETIRE→双域fence回收。单时钟串行入口，恢复与平台边界见契约。[本轮报告](results/rtl_memory_endpoint_20261023.md)。

新增[记录级存储适配器契约](hardware/RECORD_BACKING_CONTRACT.md)：3位命令含不分配的LOOKUP，内部连接codec与AXI，成功内存响应后才解码提交，完整记录消费后返回成功。故障封锁全部命令；页槽COMPLETE和fence协调仍待总顶层。[验证报告](results/rtl_record_backing_20261023.md)。

新增[页codec契约](hardware/PAGE_CODEC_CONTRACT.md)：160位记录↔512位页流，整页格式校验且成功commit后才输出记录，cancel仅本地中止。AXI/页槽协调仍需可综合适配器；编码done不能替代B成功响应。[验证报告](results/rtl_page_codec_20261023.md)。

新增[后备服务接口](hardware/BACKING_AXI_CONTRACT.md)：owner/frame/cookie租约与1344B页AXI，内存完成由总线引擎驱动；上游页提交与fence的绑定仍待总顶层实现。注意服务状态码与原页控制器不同。[验证报告](results/rtl_backing_axi_20261023.md)。

新增[闭合有界队列/fence接口](hardware/QUEUED_ENDPOINT_CONTRACT.md)：请求/工作/响应各4项，控制请求/ACK各2项；内部计算排空和有限tag复用，COMPLETE持久性与实际内存地址仍由待实现适配器负责。[本轮证据](results/rtl_queued_endpoint_20261023.md)。

新增[页槽传输控制器RTL契约](hardware/PAGE_CONTROLLER_CONTRACT.md)：公开接口限制传输中搜索/释放、完整描述符完成、全64位置发布，有限ID隔离至排空。远端有界队列、fence tag/ACK和地址后备池仍待RTL组合，COMPLETE和排空输入为可信适配器接口。[验证证据](results/rtl_page_controller_20261023.md)覆盖两种位宽和真实小查询。

## 当前参考入口

`src/reference.py` 提供 `run(case: dict) -> dict`，由 `scripts/run.py smoke` 加载。返回 `checks`（非空布尔集合）、`observations`（诊断或逻辑计数）、`outputs`（结果）。共享驱动添加输入/代码哈希与执行类型。

样例输入容量、epoch 位宽和 begin/read/write 序列，输出读值与清零操作数。真实接口需 task/net/resource ID、状态版本、页生命周期、同网引用关系与溢出策略。

字段样例以 [data/toy.json](data/toy.json) 为准。它是手写合成输入，不代表完整真实数据模式。

## 真实数据接入

把提取/转换脚本放入 `adapters/`，把用户原始数据的引用或本地副本放入 `data/raw/`，把派生文件放入 `data/derived/`。更新 `data/datasets.json` 的路径、器件、源版本与 SHA256。大器件库和基准不重复复制到七个目录；可以引用原始素材或公共缓存。

真实基准与合成样例分开。后续真实基准入口需显式选择真实适配器；当前 `benchmark` 仅接受合成状态配置，不要将所有变体映射到同一个 toy reference。

## 已接通的真实串行接口

`python3 scripts/run.py profile-real [--config PATH] [--output NEW_DIRECTORY]` 读取 `configs/real_trace.json`。要求 `dataset_kind=real_placed_netlist`、真实 RRT SHA256 及构建输入/二进制哈希全部匹配，拒绝覆盖结果目录。`adapters/prepare_real.py` 由真实逻辑/已布局物理 Interchange 导出 RRT1，`adapters/build_real_router.py` 生成原始兼容、计时采样和访问记录三个独立程序；原始快照保持只读。

`results/real_trace_*/manifest.json` 保存随机执行顺序、环境、命令、每次收敛数据/结果哈希和独立图级检查。`original_*.log` 的 load/route/write 是原始性能，route 含粗 bbox 预处理；一次性 Java 导出和外部验证不在分母内。`profile_*.json` 的 route_ms 排除采样缓冲设置，初始化在 load 内；mutable_state_initialization 包含 label_initial_allocation。逐阶段计时与 PC 采样只用于归因，完整 trace 的计时不得作为原始性能。

`profile_*.pcs` 每行是 PC 与最多七个调用者返回地址（十六进制）。`analyze_real.py` 解码时仅对调用者地址减一，使用同一非 PIE 二进制的 DWARF。归类先检查 bbox/rip-up/commit 等上下文，再按最内层实际源码行归类标签访问、预取等。采样比例不是精确的内存停顿或可实现加速比。

`trace_0.jsonl` 每行一个搜索 attempt，记录：

- 连续 attempt ID、拥塞 iteration、connection index/ID、net index、fanout、pops、总 TLD 调用数。
- previous_path 为本次 rip-up 前的 sink→source 路径，path 为本次结束后的路径；下一次同 connection 的 previous_path 必须等于上次 path。资源增删仍须沿用原程序的首尾端点排除/alt-sink 规则；不可把路径长度直接当作不同 net 占用量。
- accesses_selected、truncated、access_byte_offset 和 access_count；原始固定间隔每 512 次抽一个，单次上限 200000 个访问，未选记录访问数为 0。总访问计数覆盖所有 attempt。
- `.accesses` 是连续的小端 `(int32 dense_node_id, int32 trace_source_line)`，每条 8 字节；节点 ID 绑定冻结 RRT 哈希，source_line 绑定 trace.cpp 哈希。不是规范 tile/wire ID，也不是 DRAM 访问轨迹。

本轮严格串行。价格上下文由 `(iteration, attempt, 搜索阶段)` 唯一定位：本次 rip-up 后开始搜索、回溯后提交，然后 target 清理；迭代边界更新历史价格。它是串行事件顺序，不是已经实现的跨设备价格版本协议。每次搜索使用新 visited 序号，不复用旧距离；没有并发提交或价格修复。

`scripts/capture_tail.py RESULT_DIRECTORY` 从完整 attempt 元数据选出全部 pops≥16384 查询，生成独立 trace 副本及足够容量，不覆盖主实验二进制。尾部结果再次对照原始结果哈希、收敛和全体标签访问计数。两组访问样本分别汇总，固定间隔抽样具有顺序偏差，不能混成无偏总体样本。

原始最终检查验证冻结图上的端点、边、环路及不同 net 的资源冲突。新增回写与Vivado route-status/RTSTAT证据见 `results/vivado_state_quality_20261022/all_outputs_quality_manifest.json`：四个唯一输出全布通，MCML两输出各有一条待解释警告；全DRC和时序未测。真实 CPU 结果不可替代 GPU/FPGA 结果。

## 真实分页消融接口

`python3 scripts/run.py benchmark-paged-real [--config PATH] [--mode serial|batch|all] [--pilot] [--skip-self-test]` 读取 `configs/paged_real.json`，使用 `build/paged_real_v2/build.json`。默认每配置三次，逐进程随机块顺序运行。`--pilot` 只有一次，不作为正式报告。结果目录不可覆盖；真实输入、源码、头文件和二进制哈希须匹配。

`adapters/build_paged_router.py --output NEW_DIRECTORY` 生成两种真实路由器：paged 维持原始整页初始化，node_epoch 在相同物理池中增加 uint32 槽位代次，节点首次访问时初始化。epoch 回绕同时失效页表和节点代次，回收仅在 worker join 后进行，标签数组随池收缩。全局历史价格与占用不属于被 reset 的标签存储。串行分页由 B_SERIAL_PAGED=1 显式选择；未设置时只替换已有 batch 内的 SparseLabels。

RRT1 本来包含完整邻接 CSR，但上游 flatGraphBuilt 只在其他加载路径设定；本适配在 batchMin>0 时核验所有邻接范围后置位，供原有 batch gate 使用。此改变对两种分页相同；批成员、回退/提交策略均沿用原代码。串行组必须与此前原始串行结果哈希相同；batch 组只与同配置 batch 对照要求相同，并额外做图级检查。

`.labels.json` 给出 NodeDyn 大小、全局 dyn 容量、各上下文 pool 容量、节点代次数组/页表容量、历史最大池和增长次数。它不等于 RSS；各上下文历史峰值也未必同时出现。resets/page_claims/cleared_nodes 仅在 diagnostic=true 的独立计数构建中有效；性能构建中的 0 表示未计数。`diagnose_paged_real.py` 使用带 B_LABEL_DIAGNOSTIC 的单独构建，不将其运行时间用于速度比。

`tests/paged_semantics.cpp` 直接包含实际生成的 router.cpp，覆盖增长、物理槽位换绑、独立上下文、UINT32_MAX 回绕和回收后增长，以 ASan/UBSan 编译运行。--skip-self-test 只允许复用同一构建和相同测试源码的通过记录。

全进程峰值由 `/usr/bin/time -v` 记录；`observe_paged_memory.py` 可对已运行的 driver PID 每 500 ms 读取 /proc，记录加载后布线/写出期间的 RSS，可能遗漏短暂峰值。只观察，不重启或提交实验。

## CPU 状态微基准接口

新增 `python3 scripts/run.py benchmark [--config PATH] [--output PATH]`，目前**只接受** `dataset_kind=synthetic_state_microbenchmark` 配置，不接受真实数据或硬件变体。`--self-test-only --sanitize` 运行原语检查及 ASan/UBSan，不生成性能样本。编译输出保存在 `build/<UTC 时间戳>/`。

配置约束：nodes 在 256～1048576，page_bits 在 2～12，fanout 不超过 4096；queries 限制在 1000000 以下以避开原始有符号 sequence/shareMark 回绕。基准不承诺处理任意长时间的原始 shareMark 运行；逐节点 epoch 和原始分页 uint32 epoch 的回绕另有专门检查。

`adapters/extract_state.py` 对原始函数固定起止标记进行提取，布局变化时拒绝继续；manifest 保存整个源文件哈希、各片段起始行和哈希。周围的 SerialState 是串行实验上下文：HotExpand 仅保留占用镜像，history 独立持久存放，CPU 保有权威引用关系。同网索引按每次 commit/rip-up 更新，gather 在 rip-up 后执行，排除当前 connection。

每个合成路径都包含两个端点和共享干线/分支；沿用原始正常 sink 路径排除首尾节点的规则。路径没有对应器件图，不能判断连通性、线长、拥塞收敛或布线质量。每次访问前重置搜索代次，价格变化不能使旧距离合法；没有实现跨价格版本的距离复用。

结果含 `samples`、按 workload/variant/page_bits 汇总的 `summary`、单独的 `diagnostics`、环境与溯源信息。`first`/`reuse` 分别是预置占用后首次/第二次轨迹回放；不是首次加载器件和全流程重跑。`label_capacity_bytes` 只统计标签相关 vector 容量，不是进程 RSS，也不包含同网哈希索引。`sync_host_pack_ms` 使用合成价格公式打包脏节点，无 GPU/FPGA 调用；实际传输耗时保持 null。

## 与现有系统的边界

先由 CPU 持有权威占用，设备接收版本化增量；设备侧提交作为后续独立扩展。

### 可执行生命周期协议参考（未接入路由器）

`src/lifecycle.py` 是单线程CPU协议规格，不是设备驱动、并发实现或性能模型。`tests/test_lifecycle.py` 检查交错事件语义，不能替代多线程、RTL或实卡测试。

- Authority保存connection→net、已过滤资源集合、资源→net分支引用次数、历史价格。占用为不同net数；删除同net一个分支不会释放仍被其他分支引用的资源。这里资源集合已由调用方排除不参与占用的端点，不处理器件PIP或原始路径端点规则。
- 每次路径替换或历史价格更新产生全局递增版本；commit要求查询版本等于当前权威版本，过期拒绝且不修改状态。当前是粗粒度CPU串行化，冲突查询须取消并重算，不修复或复用旧距离。
- Delta携带design身份、before/after版本及脏资源的最终occupancy/history值。Replica仅接受相邻版本，最近一次重复交付幂等；缺口、较旧更新或其他design一律拒绝。apply返回已应用版本。Authority可生成完整Snapshot，Replica.install拒绝回退版本/跨design快照，完整替换状态并增加本地恢复generation，即使价格版本相同也使旧query失效。未实现真实网络ACK、重传队列或设备恢复。
- Context开始查询时要求Replica追上Authority；query handle按对象身份隔离，另记录context/incarnation/epoch/price_version。标签读取同时核验handle与Replica价格版本；价格变化后只能取消重启，不能认为旧距离有效。
- 访问页持有租约至finish，持有中的页回收被拒绝。模型没有物理页槽、运行中置换或异步DMA。epoch回绕在静止边界清理标签并增加incarnation；incarnation和价格版本使用Python无界整数，不声称已解决硬件有限位宽ABA，硬件需排空所有旧请求/ACK再重用。

测试含1000步随机路径替换/历史更新，以完整路径重新构造不同net占用作独立oracle；另测两个Context交错、过期提交、缺口/重复/跨设计增量、页租约、2bit epoch多次回绕、快照追平/同版本恢复失效，以及非法行/重复资源导致增量和快照原子拒绝。Authority、Replica和Context均不允许调用方绕过接口修改内部字典；模型不是不可信调用方的安全边界。

优先阅读 main.cpp 的 NodeDyn、SparseLabels、gatherShareSet、flushDirtyToGpu 与资源提交函数。

## 结果协议

现有 smoke 输出固定为 `execution_kind=synthetic_smoke`、`backend=python_cpu`，性能字段为 null。逻辑计数位于 observations。公共结构可参考 [result.schema.json](../_shared/schemas/result.schema.json)。

正式结果应另行实现 `execution_kind=real_benchmark`，明确 CPU/GPU/FPGA 后端与测量范围，保存真实时延/功耗及合法性检查。硬件仿真与实卡结果必须能区分；估计周期与 measured ms 不共用字段。

C++ 微基准为单独协议 `execution_kind=synthetic_state_microbenchmark`、`backend=cpp_cpu`，包含 CPU 实测状态阶段时间；不使用仅允许全 null 性能字段的公共 smoke schema。`checks` 同时记录 C++ 检查、差分比较和源文件未改动检查；失败记录保留已有样本并标记 failed。

## 限制

### 新增运行中页置换规格

`src/page_residency.py` 在独立的 `ResidentPages` 中建模物理槽、slot generation、pin租约、脏页写回、后备存储与换入完成。绑定 `lifecycle.Context` 的活query，所有读写校验query身份、价格版本与恢复generation。旧Context.labels与新页模型尚未替换集成；原真实路由器也未接入。

脏页evict先冻结数据并占用槽，直到精确的Transfer token完成才保存到后备存储并释放；换入完成前不能读写。只读返回副本，避免绕过dirty追踪。查询切换可丢弃旧有效标签，但旧IO和pin仍持有物理槽，必须收到完成/解除确认后才复用。旧完成只释放自己的租约，不写入新query；重复或伪造完成被拒绝。相同价格版本的快照恢复也会使旧query传输失效。

这是显式事件的单线程Python规格：假设足够后备容量、可靠完成通知、无界版本/generation；真实DMA的地址隔离、取消排空、有限位宽回绕、重试/故障与并发原子性均未实现。接口调用 `complete` 代表传输确已完成且旧写不会再访问原地址，不能仅凭软件忽略回调就声称防住真实迟到DMA。

`tests/test_page_residency.py` 包含6项检查：保存前槽不复用、换入恢复数据、迟到writeback/refill、伪造/重复完成、价格与恢复失效、旧pin确认及2000步随机值对照。没有真实距离值或时延/带宽数据。

Python 样例只处理单上下文标签；C++ 状态微基准检查独立上下文和静止边界页回收，不覆盖 PathFinder 状态机。真实串行入口已覆盖拥塞迭代；实际并发、运行中页替换、异步版本化同步仍未验证。

- 设计级占用/历史拥塞不能随 connection 标签一起清零。
- 同网多分支共享资源需引用关系，资源占用按不同 net 计数。
- 跨价格版本复用距离标签需要明确失效或修复条件；存储复用不等于距离有效。
- epoch 回绕、并发上下文和页回收不能暴露旧状态。

### 真实路径协议回放

`taskset -c 24 python3 scripts/replay_lifecycle.py [--config PATH]` 读取 `configs/lifecycle_replay.json`，绑定RRT/trace/metadata二进制SHA与预期事件/连接/资源总数；运行前后复核，未达预期拒绝通过。结果目录保存脚本与模型源码快照，禁止Python -O跳过断言。使用冻结原始loader导出的connection id/net/sink/has_alt/初始路径，以及真实trace_0.jsonl。普通sink且无alt时排除路径首尾，sink预占用独立保留；alt或其他sink按原函数保留全路径。先校验初始占用与原loader一致，再按rip-up和commit分两次版本更新，逐条检查previous_path。最终从原始最终路径独立重建不同net资源占用，核验Authority与Replica。

首次完整回放 `results/lifecycle_real_20261022T193455Z/`：570286次事件、180326连接、722477个最终占用资源，与原路由used_nodes相同；11次模拟丢包快照恢复与重复交付通过。`completeness_audit.json` 将事件总数对照原trace收敛记录中rerouted总和。轨迹未记录历史价格值，故没有真实history回放；没有并发路由搜索、设备传输、硬件有限位宽版本或距离计算验证。性能为空。

### 真实地址压力协议入口

`taskset -c 24 python3 scripts/replay_page_protocol.py` 分别重放1113间隔和19尾部查询的完整TLD地址；4槽×64节点，每访问写合成序号，逐读和最终全映射对照，跨查询延迟一个旧完成。结果 `results/page_protocol_real_addresses_20261022T215927Z/`。这不是实际距离/dirty/价格事件或DDR流量回放，performance为空，详细边界见独立报告。

### 实际C++标签引用租约先导

`adapters/build_resident_router.py` 在独立生成副本中将28处 `TLD(...).field` 改为RAII句柄的箭头访问；句柄持有页直到完整表达式结束，支持同表达式多引用。`adapters/resident_labels.inc` 使用固定页槽和同步C++后备拷贝，不能将其称为DMA实现。真正同步返回前完成写回/换入，所有页被pin时明确报错，不丢弃活引用。查询reset在存在pin时拒绝；页表epoch回绕清表。

`build/resident_real_v3/semantic_tests.json` 记录实际标签类ASan/UBSan检查；失败生成/兼容编译尝试保留在v1/v2目录。`scripts/benchmark_resident.py` 已完成3项真实质量先导并复核：RAII平坦控制、两设计resident64槽×64节点，均保持同序结果与收敛。报告 `results/resident_pilot_20261022.md`；未支持hash/overlap入口会明确拒绝，不能外推到其他并行模式。保留此构建，后续变体另建目录。

### 读写分离租约先导

`adapters/build_resident_rw_router.py` 在独立版本中审计18处只读和10处写入，`TLRead`句柄返回const指针、保持租约但不标脏，写句柄仍标脏。槽位新绑定完成后先清dirty再应用访问意图；v1检查捕获过dirty继承，成功v2已通过只读丢弃、脏值保持与干净换入不重复写回检查。`first_pages`计数在本版本仅表示无后备内容时的零初始化次数，不等于不同逻辑页数。

`scripts/benchmark_resident_rw.py` 已完成两设计×保守/显式读写的4次单次配对并复核，报告见 results/resident_rw_pilot_20261022.md。固定64槽×64节点、相同串行参数；是单次CPU发现性结果。旧resident_real_v3与此前正式矩阵均不改。

### 零页只读旁路

`adapters/build_resident_zero_router.py` 派生自冻结的resident_rw_v2。只有当前query下页不驻留且无后备记录时，TLRead才返回独立默认NodeDyn；不插入LRU、不分配页、不标脏。写路径保持原来的分配与租约规则。旁路引用不持有帧，默认存储在其他访问分配/写入或reset期间稳定；读取只代表取得引用时的默认快照，未承诺与后续写入别名。实际28处字段表达式保持原顺序，真实输出等价由本轮实验另行验证。

`zero_reads`是旁路的读取调用数；`first_pages`是整页默认初始化次数，两者单位不同，不能直接相加解释为逻辑页数。全局历史与占用不受影响。原生检查证据在build/resident_zero_v1/semantic_tests.json；真实配对已4/4完成并复核，见results/resident_zero_pilot_20261022.md。完成后用scripts/report_resident_zero.py审计源/二进制/输入/原生证明绑定、真实结果、收敛与计数。

### 驻留容量扫描

`scripts/benchmark_resident_capacity.py`固定zero_bypass算法、PBITS6和串行CPU8，比较64/256/1024/4096槽，两真实设计各单次完整运行。驻留载荷分别96KiB/384KiB/1.5MiB/6MiB，其他状态另计。允许大容量下refill降为零，不把零换入错误判断成路径未执行；仍核验旁路计数、页配置、输出与逐轮收敛。保持冻结构建和旧先导结果。

### 三重复与同轮原始对照

`scripts/benchmark_resident_repeated.py`已完成24次完整运行；`scripts/report_resident_repeated.py`统一审计通过，结果见results/resident_repeated_20261022.md。两设计、resident64/256/4096页和原始flat各三次。planned_cases记录随机区组顺序；报告保留三次原始值和同区组原始比值，所有resident仍更慢。后续性能拆解必须另建诊断版本，不能修改本轮冻结构建。

### 驻留CPU采样诊断

`adapters/build_resident_profile.py`直接读取冻结resident_zero_v1/router.cpp，仅新增real_profile.hpp以及主布线阶段的start/stop/report；SparseLabels至bSerialLabels之间含租约/零页接口的区域逐字节不变。继承原核心ASan/UBSan证明不代表信号处理器新增独立验证。`scripts/profile_resident.py`两设计代表容量各开/关采样一次，结果/完整收敛仍须等价；采样周期请求1009us，实际投递可能受内核粒度影响。样本为CPU时间分布，不能当成精确分阶段延迟或DDR事务。诊断总时间和开关扰动需报告，不能替代三重复正式耗时。

### 驻留标签预取消融

`adapters/build_resident_noprefetch.py`读取冻结resident_zero_v1源码，仅替换SparseLabels::prefetch函数为空；保留其他prefetch路径。新类通过tests/resident_zero_semantics.cpp实际ASan/UBSan检查。`scripts/benchmark_resident_prefetch.py`固定LogicNets256页/MCML4096页，两设计各开关单次，输出和逐轮收敛对照冻结参考，且开关标签计数必须完全一致。新结果为先导，不能直接宣称稳定收益或硬件收益。

预取消融已4/4完成并复核，见results/resident_prefetch_20261023.md。所有标签计数开关相同，本次整体时间差不足1%，不据采样预取比例宣称净加速。原prefetch-on基线继续保留。

### 固定槽索引LRU

`adapters/build_resident_index_lru.py`直接派生自冻结resident_zero_v1，prefetch-on保留。Frame存previous/next槽索引，队首/尾为int32，精确维护同一LRU序列，已在队尾时不更新链接；寻找victim从队首沿索引跳过所有pin，全部pin时报错。reset保留链顺序（与原版相同），仍拒绝活引用。新tests/resident_index_lru_semantics.cpp保留原零页/值保存/租约/wrap套件，并对2/3/17/256槽各5000步，以独立std::list顺序和pin oracle检查完整双向链、victim、全pin和reset。实际类ASan/UBSan通过。两设计完整路由先导仍待结果，必须输出/收敛/计数同序等价。

索引LRU先导已4/4完成并独立审计，见results/resident_index_lru_20261023.md。布局开关两次全部标签计数相同，输出/收敛同序等价。单次时间差2.14%/4.93%，尚未重复，不证明硬件或整体内存收益。

索引LRU三重复已12/12完成并统一审计，见results/resident_index_lru_repeated_20261023.md。三轮同序输出/收敛一致，全部标签计数一致；配对下降中位数1.73%/4.56%，只相对resident list基线，不是相对原始CPU或硬件加速。

### push作用域租约

`adapters/build_resident_push_lease.py`基于冻结resident_index_lru_v1，只把push里lb/upstream/visited三个相邻同节点写入改为一个局部TLD句柄，显式块在tl_pushes/dump/递归exploreAndExpand/queue.offer之前结束。块内无其他调用或分配，均访问同页，预期LRU顺序和换页计数不变，但需完整真实配对验证。新tests/resident_push_lease_semantics.cpp以外层固定页+1000次实际push检查三个字段、prev保持、队列值和dump记录、返回后pin数量，继承索引LRU/零页/回绕套件，ASan/UBSan通过。未合并其他读路径或延长跨函数pin生命周期。

push租约先导4/4已完成并独立审计，见results/resident_push_lease_20261023.md。配对输出/完整收敛/全部标签计数相同；单次下降4.24%/3.41%，尚未重复。原生专项实际push覆盖lookahead=false，完整真实等价运行含递归路径，不能冒称专项递归用例已覆盖。

push租约三重复已12/12通过并统一审计，见results/resident_push_lease_repeated_20261023.md。各设计六次全部计数相同，配对下降中位数4.24%/3.24%，只相对resident index逐字段CPU版本。后续设备有限位宽/排空/迟到完成仍未实现，不能拿Python对象身份或无界版本作为硬件协议证明。

### 有限完成所有权ledger

`src/finite_completion.py`独立有限字段模型，Descriptor按值匹配，已完成事务号隔离到可信排空，查询号/槽代次耗尽阻塞。新query使旧完成无效但不提前回收槽；fence期间禁止新发起，local pending/binding清空且外部peer_quiescent和completion_queue_empty成立后才允许编号复用。两个外部条件尚未接设备，实现必须保证旧请求/重传/完成队列及旧主机生产者全部排空。假排空导致相同旧描述符完成新事务的反例已测试，不能将有限ID本身视作无限迟到安全。8新增/48全套检查，报告results/finite_completion_20261023.md；未集成页值、DMA或RTL。

### 有界传输与模拟排空

`src/finite_transport.py`封装有限ledger，有界request/work/response，peer有限ID去重，重复包仅由现存队列复制。peer seal要求request/work空，finish要求三个队列空及ledger pending/bindings释放，不由外部传入布尔确认。8新增/56全套检查、200次1位ID随机排空复用通过，证据results/finite_transport_20261023.md。组合保证限于单owner封闭队列，不覆盖绕过domain封装、外部隐藏旧包、丢去重状态、旧fence-ACK或实际设备。尚无页值副作用和DMA；假排空ABA边界未被掩盖。

### 有限队列与实际页值组合模型

`src/finite_page_values.py`让dirty快照在peer publish时写入旧QueryKey隔离后备，host有效完成后才回收；refill在有效完成后发布，取消迟到完成只释放自身槽。命名空间和payload不在传输排空前复用。8项新增/64全套检查通过，2000步随机值逐读及完整逻辑映射oracle，报告results/finite_page_values_20261023.md。独立封闭单owner模型，尚未接真实C++/DMA；payload是Python值、后备为逻辑字典，无字节预算/物理地址分配器/控制wire握手，不能宣称硬件页协议已完成。

### 有限编号中途检查点与真实地址回放

FinitePageValues新增checkpoint/restore：要求local IO/pin全部确认，从当前resident+backing深拷贝实际状态；排空后fresh query仅同数值price/layout且空状态可restore，畸形页/offset先验证不部分安装。数值price匹配不等于跨设计或价格回绕的真实距离有效性证明，本回放逻辑价格固定。page_id_bits与页内page_bits分开，页号支持至32位，回放18位足够真实图。scripts/replay_finite_page_values.py完整读取1113间隔+19尾部真实TLD地址，数据为合成sequence，不是真实距离。编号耗尽时checkpoint并排空恢复实际数据，oracle只核对。额外查询末迟到写回探针ID不足时计skip，但真实访问不跳过。8新增/72全套检查通过，完整回放尚待结果；无DMA/RTL/性能主张。

有限ID分配器等价优化：src/finite_completion_fast.py利用issued集合始终为0..n-1（只增、仅排空清空）的不变量，以len(used)代替从0扫描。字段/隔离/回绕逻辑不变；1/2/4位逐事件差分和完整16位耗尽检查、回放fixture计数等价，全套74项通过。快速完整回放由scripts/replay_finite_page_values_fast.py独立运行。原慢回放因确认二次扫描在两组交叉验证后superseded，保留部分证据，不是超时重启；新结果未完成不能宣称全轨迹验证。

有限真实地址回放现已完整通过且终态审计，见results/finite_page_real_addresses_20261023.md。1113间隔+19超大、16151535访问、tail63中途恢复，最终probe_skip0。源/输入/快照绑定及覆盖检查通过；数据仍是合成序号，非实际距离。fast分配器按有限issued集合长度等价分配，无隐藏代次；原慢版保留部分证据并superseded。当前仍未实现wire fence控制与真实DMA。

### 有限fence控制报文

`src/fence_control.py`使用3字节opcode/tag bytes和有界request/ACK，控制tag可配1..16位。peer request/work清空才ACK，host当前tag ACK不替代控制/数据队列及payload全部排空。重复/不同tag ACK不提前复用编号。9新增/83全套检查通过，真实地址+合成值控制回放尚在运行，报告results/fence_control_20261023.md。安全仍依赖闭合单owner无隐藏延迟包/旧生产者，未解决真实reset/丢包/无界外部旧ACK，不宣称DMA/RTL已完成。

有限控制真实地址回放现已完整passed且终态审计，见results/finite_control_real_addresses_20261023.md。1132查询/16151535访问、63中途恢复、1195fence、298次2位控制tag回绕、2390重复ACK，全部数据事件与前一回放一致。闭合单owner/无隐藏包契约和逻辑后备字典边界仍成立，不证明真实物理地址回收、DMA或RTL。

### 有界后备物理地址模型

`src/bounded_backing.py`预分配固定bytearray与64B对齐页，归属(query,page)隔离到完整fence，传输描述符pin地址；单ACK不释放地址，容量不足/队列满不烧ID或丢dirty值。refill读取实际bytearray。int64合成页使用presence bitmap，64节点stride576B，非真实NodeDyn布局。9新增/92全套检查通过，报告results/bounded_backing_20261023.md；raw budget不包括host元数据/快照/诊断shadow和resident，尚无真实DDR/DMA/RTL或总内存预算证明。


完整地址查询容量审计见 `results/query_page_demand_20261023.md`：64节点一页，1132查询/16151535访问，最大23279唯一页。该统计只在每查询完整fence、单query池的条件下为checkpoint恢复提供充分上界，不代表最小缓存容量或并发需求。合成int64后备stride576B需13408704B，选13 MiB预算；原始NodeDyn每节点24B的页载荷换算为35756544B，不含其他状态，也未接入该codec。原始NodeDyn包含跨迭代hist，实际适配必须按design/价格生命周期单独保留，不能随connection页失效清零。

13 MiB固定字节池完整真实地址回放与终态审计已passed：1132查询/16151535访问、63次中途恢复、1195fence，直接解码raw池核验checkpoint/最终值，控制/数据计数与前版逐项一致，见 `results/bounded_backing_real_addresses_20261023.md`。仍为真实地址+合成int64值，不含实际距离/历史状态/DMA/RTL或速度结论。

实际五字段值采集见 `results/real_field_values_20261023.md`：38查询14047736访问，18读/10写静态站点，20B显式小端事件（node/source/valueBits/field/write/reserved/histBits）。记录实际位模式及全局hist，完整CPU路由结果/收敛一致。新ScratchLabel仅含lb_bits/upstream_bits/prev/visited/target，页codec含presence bitmap后stride1344B，非NodeDyn ABI，hist不在其中。真实值有限回放先导19查询56588访问及2次checkpoint通过；30 MiB完整38查询回放仍在运行，参见顶部活动记录。所有原始池预算不含host元数据/快照或全局occupancy/history；尚无DMA/RTL/实测加速。

完整真实字段有限回放 `real_scratch_full_20261023T024846Z` 已passed并审计：38查询14047736访问、31checkpoint、69fence、38迟到写回，30 MiB raw预算、峰值21883页。

首个RTL页槽接口见 `hardware/SCRATCH_FRAME_CONTRACT.md`。单写端口版本 `scratch_frame_store_bram.sv` 通过19个完整小查询对应98322条公开接口命令和29个定向命令，XSim及U280 OOC综合passed，2 RAMB36E2/1332 LUT/641 FF。冷reset、单owner、单未完成命令；CLEAN授权、有限ID回收与整页LOAD发布屏障均需外部控制器，不等同于已实现DMA。初版RAM退化寄存器保留作负例。未验证其他参数、物理时序或实卡速度。


## 完整真实图输入（2026-10-24）

`results/graph_image_20261024` 将已溯源RRT1拆分为保留原节点ID与子节点顺序的输入：9089009节点、40469536原始边，最大原始出度18。`scripts/export_graph_image.py`生成，`adapters/verify_graph_image.cpp`通过冻结的原CPU Router加载器核对全部节点已定义属性和全部邻接；`scripts/audit_graph_image.py`还重建完整RRT1字节并核SHA。不是过滤后的getChildren缓存，也不是当前搜索状态快照。

| 文件 | 编码与大小 | 含义 |
| --- | --- | --- |
| offsets.u32le | 4×(N+1)字节 | 从0起始的CSR偏移；保持原顺序，末值E |
| edges.u32le | 4×E字节 | 原节点ID，无重排/去重/预过滤 |
| nodes.rrt32 | 32×N字节 | 原RRT1节点固定属性前缀，无C++结构体padding |
| config_prefix.rrtbin | 原文件头至节点数量（含） | 完整配置、SLR/Laguna表、N |
| design_suffix.rrtbin | 节点区之后的原始字节 | nets/connections与初始路径原始数据 |

32字节节点属性布局：tileAddr i32@0、wireIndex i32@4、type u8@8、flags u8@9、beginX/beginY/endX/endY/length各i16@10/12/14/16/18、baseCost IEEE binary32原位@20、hashCode i32@24、prevInit i32@28；多字节均little-endian。flags沿用原RRT：createdAtInit=1、Laguna=2、pinfeed=4、pinfeedLeadsToLaguna=8、arcLockedInit=32、preserved=64、pinbounce=128；保留未定义bit16，不能借其表示新状态。getChildren还包含isExcluded、类型、deadEnd与created副作用，不可用raw CSR直接替代。

邻接198234184B，节点属性290848288B，合计489082472B，不含配置/设计后缀、动态标签或占用/历史/同网引用；不是板上容量/带宽实测。设备读图前仍需图发布/版本协议，当前未实现DMA/XRT上传。初始created/prev不能当当前查询标签；占用按不同net计数，设计历史不能随connection CLEAR清除。进入扩展/评分前还必须发布正确rip-up后的占用/同网引用/历史视图、连接边界与目标集合。


## 排除判断命令接口（2026-10-24）

`hardware/hls/exclusion/rearchitect/v1/src/exclusion_port.hpp`与kernel_hls.cpp实现单边上下文。START输入parent/child、RRT flags、created及hasLaguna；RESPONSE提交generation/phase/value；SNAPSHOT只读。成功START分配单调32位generation，已有待处理请求时返回BUSY，到UINT32_MAX后拒绝新START，不回绕。

输出request/node指定下一次标签读取，phase1=child.prev、2=child.visited、3=parent.visited、4=arc路径再次child.prev。只有当前generation与phase均匹配的RESPONSE才推进；旧编号/错误或重复phase均拒绝。request0且generation>0表示已完成边，excluded是其结果。无请求响应返回NO_REQUEST，非法命令/参数BAD。拒绝后的可见状态保持。

每次标量调用等待ap_done并捕获输出；尚无并发顶层调用证明、标签端点连接或自动图分页。冷复位会重置编号，必须由集成层先排空旧消息；没有在线RESET或取消命令。原query/price/设计成本视图必须由外层保证正确且在单边处理期间保持语义，generation不是价格版本。

32位实例354530调用/27648上下文的Csim、Csynth和RTL cosim已通过；相同代码gen3实例实际7上下文后拒绝再START，12调用通过。缩小实例的耗尽验证不等于执行2^32条生产上下文。独立源码与原函数golden/HLS终态审计：results/exclusion_hls_20261024/source_bound_audit.json；架构与完整状态码见hardware/hls/exclusion/ARCHITECTURE.md。
