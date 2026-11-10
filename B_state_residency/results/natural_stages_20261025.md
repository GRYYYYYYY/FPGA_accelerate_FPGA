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

