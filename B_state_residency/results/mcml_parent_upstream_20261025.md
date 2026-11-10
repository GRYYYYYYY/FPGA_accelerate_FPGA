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
