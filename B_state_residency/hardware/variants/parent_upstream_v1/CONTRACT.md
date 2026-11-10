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
