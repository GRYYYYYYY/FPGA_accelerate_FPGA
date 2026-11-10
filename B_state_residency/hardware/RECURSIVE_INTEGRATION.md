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

# Immediately recursive candidate integration

This is an implementation contract for work still pending, not a completion claim.
Current evidence: `results/iterative_recursion_20261025`,
`results/children_frames_20261025`, `results/expansion_capture_20261025`,
and the candidate-capture experiment. Existing immutable results remain baselines.

## Target/owner conditions update 2026-10-25

Three explicit target conditions now pass with 32 slots and one slot: free
resources clear a nonempty heap on EARLY; foreign-owned targets do not clear and
use the occupied price; same-net refs2 with occupancy1 do clear and use sharing
factor3. Target survives every native cost ACK and page eviction. Ancestors either
drain without access on EARLY or re-read visited before skipping. All physical
label pages match CPU labels. See `results/recursive_target_matrix_20261025.md`.
Owner counts are initial read-only snapshots; actual reference mutation/overflow,
natural search traces, full routing, joined failures and board tests remain open.

## Joined descendant update 2026-10-25

A synthetic five-node convergent graph now passes the actual complete recursive
candidate/graph/metadata/native-label/geometry/cost/commit/OFFER path with 32 slots
and one slot. Parent resumption reads the descendant's actual visited=77 and
skips the sibling. All five final native labels and the full physical page image
match the original CPU fixture. See `results/recursive_join_20261025.md`.
Target EARLY, nonzero owners, natural recursive traces, full search/backtrace,
joined failures and board performance remain unverified. Older checkpoints follow.

## Implementation update 2026-10-25

`recursive_controller_v1` now implements descent/restore and exposes the current
parent. `candidate_recursive_v1` wires that parent into postprev/commit. Seven
component cases pass with mock backends, and the actual pipeline's 160-parent
nonrecursive prefix passes. Real descendant native-label/cost/OFFER integration
is **not yet verified**. See `results/recursive_controller_20261025.md`. The
acceptance evidence below is still required; the older capture boundary follows.

## Current boundary

`candidate_capture_v1` captures all static children of a parent before the existing
metadata/access controller sees them. It preserves a single outstanding parent
operation. Action 2 still returns a callback. It does not initiate a descendant.
The real expansion controller is authorized by the accepted parent operation,
since its request now reaches it after the original frontend handshake.

`expansion_capture` stores a 512-bit context as follows, low bits first:

| Bits | Field |
| --- | --- |
| 31:0, 63:32, 95:64, 127:96 | ymax, ymin, xmax, xmin |
| 159:128, 191:160, 223:192, 255:224 | flags, route sequence, net, sink |
| 287:256, 319:288, 351:320, 383:352 | hasLaguna, prune, parent, frame cookie |
| 447:384, 479:448 | full design identity, full price version |
| 483:480, 485:484, 511:486 | price, query, reserved zero |

This contains static connection fields and identity. Connection State weights are
kept separately by the enclosing connection reader; it is not a snapshot of
parent upstream or the child's visited/prev labels.

## Required scheduling changes

1. After an action-2 candidate's three verified native ACKs and complete response
   retirement, suspend the parent's next-child cursor and descend immediately.
   A sibling must not enter metadata/access before the child subtree completes.
   Preserve original shared earlyTermination propagation through ancestors.
2. Give every frame a checked identity. Save/restore parent, sink, net, sequence,
   flags, bounding box, query, price, full version and full design. Do not reuse
   an ordinal alone as a globally unique frame identifier. Handle cookie overflow
   explicitly. All frames belong to the same protected connection lifecycle.
3. On resumption, issue actual metadata/access requests for the next sibling.
   Read visited/target/prev again; read current parent upstream for every allowed
   candidate. Do not retain pre-recursion access decisions or distance validity.
4. Propagate current parent to the outer pipeline. In `candidate_offer_engine`,
   `held_parent` is updated only by an external expansion handshake and feeds
   postprev requests, commit requests and their identity comparisons. Reusing it
   unchanged for descendants writes the root as predecessor. Expose and bind a
   current-parent signal; keep it stable throughout a candidate's whole lease.
5. Preserve connection State while descending; frontend `q_meta_valid/q_cookie`
   currently follow root expansion admission, and `q_sink/q_net/q_connection`
   bind the State reader. Distinguish connection identity from frame identity.
   A descendant of the same connection does not justify a configuration change.
6. Keep query ownership and every host/configuration fence active across the
   complete stack, including intervals with no physical graph request. A shared
   design/graph change or identity drift invalidates suspended frames too.
7. Decide descend-versus-return before a last-child completion is offered by the
   frame adapter. Once offered, completion VALID and its entire payload must be
   preserved under backpressure. The present adapter requires result_ready low
   during a new expansion admission; a recursive scheduler must honor this or
   replace that contract with an independently verified command protocol.
8. EARLY clears the actual frontier before the corresponding prev/cost/label
   sequence; skip does not commit; action 1 offers actual total only after all
   ACKs; action 2 never offers. FULL after commit stops, without silent loss,
   speculative rollback or a hot retry.
9. Stack/children overflow, abort, identity drift, outstanding-service drain and
   restart require a coordinated whole-engine protocol. Component reset is not
   sufficient evidence. Current capture composition has no joined failure proof.

## Acceptance evidence needed

- Original immediate-recursion CPU semantics on an explicitly documented
  multi-child convergent graph. The five-node existing counterexample must
  distinguish the implementation from deferred recursion.
- Actual descendant expansion before the next parent's sibling metadata request;
  actual dynamic label replies showing recursion changes that sibling's decision.
- Actual geometry/cost/commit/OFFER and final native checkpoint reads, including
  nonzero parent upstream inherited from the just committed descendant path.
- Frame/current-parent/full identity and stable held responses verified through
  normal and pressured memory configurations. Separate real graph provenance
  from explicit synthetic geometry/topology stress.
- Existing no-recursion replay, unchanged source bindings and full byte-memory
  audits remain passing. Cycles are simulation receipts, not measured speedups.
