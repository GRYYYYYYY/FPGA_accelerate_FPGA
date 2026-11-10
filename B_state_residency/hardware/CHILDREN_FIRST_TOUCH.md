# 首次邻接过滤的服务边界

已验证算法组件：`search/children_machine.hpp`；CPU接入器：`../adapters/build_children_router.py`。它只替换原 `getChildren` 的首次过滤循环，不替换缓存命中、原始邻接获取/节点intern、缓存所有权获取或发布。原排除逻辑沿用已经验证的 `search_filter::Machine`，未来可委托实际 `paged_exclusion_engine`。

| 请求 | 服务动作和提交条件 | 后继 |
|---|---|---|
| NEXT | 按原始CSR或已完成intern的rawChildrenStore顺序取得第position条边；prune启用时先计算deadChild，更新any_alive；节点须小于2^24 | EXCLUDE |
| EXCLUDE | 读取当前动态created与稳定属性，完成排除判断及其条件标签读取；不是“初始created”快照 | 排除则下一边，否则CREATE |
| CREATE | 将设计级created[child]设为1，确认写入后才能继续 | CLASSIFY |
| CLASSIFY | 先读type；INACCESSIBLE直接丢弃，否则仅在prune启用时检查deadEnd | 丢弃则下一边，否则EMIT |
| EMIT | 保持原顺序追加child，允许重复child，完成缓存存储写入后应答 | 下一边或结束 |
| CHECK_DEAD | 仅prune启用且没有结构存活子节点时，查询canBeDeadEnd(parent) | 可标记则MARK_DEAD，否则PUBLISH |
| MARK_DEAD | 设置设计级deadEnd[parent]，不能将瞬态排除判断作为依据 | PUBLISH |
| PUBLISH | 完整列表（包括空列表）持久保存并发布valid；必须保证未来缓存命中不重新过滤 | DONE |

`NEXT→EXCLUDE→CREATE→CLASSIFY→EMIT` 中的副作用次序不能交换。尤其INACCESSIBLE或已dead的节点，只要未被isExcluded排除，原程序仍先调用getOrCreate；重复边的后一次判断会看到前一次创建的结果。any_alive来自结构谓词，在排除判断之前更新，不能用输出列表非空替代。

缓存为设计生命周期状态。首次结果可能受当时created/prev/visited影响，但原CPU发布后不因connection/query/price切换重新过滤。未来硬件不能仅因驻留槽淘汰就丢掉缓存并重新执行EXCLUDE；应保存列表/顺序位图及有效性至后备存储，或者证明其他表示的等价性。空列表valid和“尚未构建”必须区分。raw CSR、首次过滤缓存、查询级标签和设计级created/deadEnd是四种不同状态。

当前helper仅为单个首次构建的可等待算法状态；错误phase调用返回false且不推进。它没有并发所有权、硬件token、跨复位响应保护或在线取消。CPU适配器保留原有sentinel/锁/发布块；测试的锁分支是串行调用，不构成并发正确性证明。硬件控制层仍须携带构建generation、parent、position、phase与查询上下文，拒绝过期/重复回复；只有全部副作用和存储成功后才能发布valid。部分创建后失败的恢复不能假定撤销已经发生的设计级副作用。

预上传图镜像固定节点编号和raw CSR，已核验真实图最大度18；其他输入不能未经检查沿用18项容量。当前完整真实对照为nonlazy固定图，单元测试同时覆盖已有raw数组和简化lazy fetch，但未证明在线JNI节点增长或并发intern的硬件实现。

CPU验证：`../results/children_first_touch_20261024.md`。后续已实现 `hls/children` 硬件协议控制器，Csim/综合/RTL cosim、直接复位及实际Vivado结构审计通过，见 `../results/children_protocol_20261024.md`；还没有实际图AXI读取器或设备缓存存储。调用收集和构建级服务调度已在 `variants/children_engine_v2` 完成实际HLS联调，见 `../results/children_engine_20261024.md`；下一步接真实图读取、动态设计状态和已验证自动换页边引擎。一次构建跨多次EXCLUDE，整个构建期间须保护query/price和相关标签状态，不能仅依赖单边引擎的锁定。
