# 首个自然查询快照与原CPU搜索重放通过（2026-10-25，优先历史）

本轮从真实logicnets完整原始串行路由中采集首个自然查询，不改图、不设合成owner/target、不复用旧脚本oracle。机器证据 results/natural_query_20261025.json，汇总 scripts/summarize_natural_query.py。采集链接 results/natural_query_v2；独立恢复搜索链接 results/natural_query_replay_v1。原始参考源码和共享基线均保持。

查询identity：attempt/sequence1，iteration1，connection_index16506/id37267，net2717，source65185，sink150697，fanout257。实际bbox x[38,46]/y[283,295]；State share/wire/estimate raw bits分别3f800000/3e4ccccc/3f4ccccd，present factor为3f000000，cross=0、landmark=0、dead-end pruning=0，hot/prefetch/bbox启用。原prepare已经执行rip-up、设置target并将source入队；此时才保存快照，因此独立重放不可再执行prepare。

全节点initial_nodes.u32与search_final_nodes.u32各9089009行，每行11个32bit字段（lb/upstream/history/prev/visited/target/ownerNet/ownerCnt/occupancy/created/type）。另存完整256价格、溢出引用、已有children cache、真实State和逻辑heap。ownerNet沿用原CPU -1为空/零起net编号，不是FPGA net+1编码。所有节点都存，既有标签/历史/占用不能按默认值替代。格式与事件契约在 adapters/natural_query_v1/README.md；无需Vivado即可完成本轮CPU工作。

自然事件共72次扩展、271条有序children和271次候选检查、171次搜索内成本push、73次POLL；含prepare源push则172，与前轮完整普查相同。目标150697在父1411724下触发一次EARLY/CLEAR，CLEAR后目标入队并出队，found=1/aborted=0/剩余heap0；最终目标成本bits40267287。无lookahead。171个不同节点标签改变，202个created状态0到1。完整节点审计确认history、owner、引用和occupancy在搜索内保持，而不是随标签清零。快照结束点在原搜索循环之后、saveRouting/occupancy commit/target cleanup之前，不是完成连接提交后的状态。

采集器由 derive.py 只插入观测，删去观测逐字节恢复 build/real_trace/original.cpp；完整12轮路由结果与冻结原串行结果逐字节相同。audit_natural_query.py逐候选核验读前标签、prev/lb/upstream/visited/target提交和全部节点最终状态，并独立实现原8叉heap/POLL/CLEAR顺序。它不独立重算成本或过滤条件。

独立CPU重放进一步使用同一原Router和实际cost/filter/push，加载原RRT后恢复快照、cache、prices和State，重建HotExpand，再执行从原源码提取的搜索循环（不重新prepare）。make_replay.py生成driver；run_natural_query_replay.py与audit_natural_query_replay.py核验。全部9个文件逐字节一致：全节点前后状态、overflow、cache、prices、State、初末heap、全部events。因此是自然查询可独立恢复搜索的CPU oracle；尚无该查询的RTL执行、板卡性能或数学独立cost证明。

原natural_query_v1在生成源码时因非唯一poll文本锚点停止，未编译/执行，保留scratch；v2改为唯一完整while锚点。通过结果从不覆盖。采集26文件归档14710474B，重放29文件归档11269548B，位于 results/offer_archives_20261025。两者完整移开后解包逐成员核验，并重建汇总逐字节一致；恢复凭据 results/natural_query_restore_20261025.json。tmp丢失时按两个同名JSON索引运行restore_offer_result.py。

下一步：从此快照与事件生成自然查询的graph/design/owner/native label/64B State输入，先独立核验codec与实际geometry/cost输入，再驱动完整POLL→expand→filter→cost→三ACK→OFFER→target CLEAR搜索循环。当前只有每扩展候选链与合成递归组合，不能把72个父节点当作互相独立的旧脚本向量；须保持动态created/cache、标签写后读、全局heap与target位。测量query级State加载和重复准备可避免多少工作必须给真实计数，不能由逻辑次数直接声称加速。MCML自然查询快照/重放、多查询/跨价格有效性、真实多net提交与板卡实现仍待完成，研究goal active。

