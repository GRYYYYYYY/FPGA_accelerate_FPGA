# 整条记录存储的codec变体

`memory_scratch_endpoint_wide` 只替换codec存储与转换实现；顶层控制、记录级后备服务、页槽、队列、目录和AXI协议保持原语义。`make_wide_codec_composition.py` 仅改模块名称及子模块引用，生成新组合和相同测试台，不修改冻结基线。

## 数据组织

`scratch_page_codec_wide` 将原320×32位word RAM改为64×136位label RAM。两个float32位模式、两个int32及target uint8均按原始位保存；160位记录高24位padding不存储，但输入编码和原始页解码时仍必须检查为零。对不存在节点，全部160位载荷仍须为零。

编码在每次合法记录握手时写入整条label。全部64条记录通过校验后，按原页格式输出：bitmap8B、64×20B记录、56B零尾，共21个512位拍。每条label同步读取一次，低32位立即参与输出，其余字段从136位缓存生成；不再每个32位word单独读取RAM。

解码仍逐32位word解析原始512位拍，在第5个word到达时将完整136位label写入RAM。整页规范检查和成功commit后，每条记录一次同步读取，再补高24位零输出。尚未优化逐word页解析；它可能成为后续瓶颈。

## 不变条件

所有start/record/raw/done握手、背压保持、64条记录顺序、present-zero与absent-zero区别、位模式、整页校验、成功commit才发布、失败commit及cancel行为沿用[原codec契约](PAGE_CODEC_CONTRACT.md)。RAM不批量清零，任何页面在读取前均覆盖全部64条label；中止后不能通过旧label暴露数据。

高24位padding被截去不是允许非零padding：新增故障对照专门移除解码padding检查，确认测试能抓住“直接截断但错误接受页面”的变体。

[记录级服务](RECORD_BACKING_CONTRACT.md)的错误租约保留以及[闭合端点](MEMORY_ENDPOINT_CONTRACT.md)的COMPLETE→RETIRE和FINISH→RECYCLE顺序不变。只允许替换模块引用，不能借性能优化放宽这些约束。

## 性能解释

配对比较使用相同19个真实小查询、相同公开命令与独立预期AXI字节、相同周期性调度/总线背压函数及同一只读观察器。观察器统计上升沿前状态，逐命令记录接受、首个响应valid与响应消费周期；顶层21个阶段互斥，模块内部活动会重叠。

较早到达某接口会改变周期性背压函数的相位，因此不能把每一阶段的差值都当作孤立优化收益。报告的是这一固定模型下完成相同工作所需周期的配对变化。未测布局布线后的频率、真实内存延迟、功耗或板级吞吐；不直接外推为CPU/GPU/FPGA路由加速比。

宽RAM可能消耗更多BRAM原语，逻辑位数减少不意味着物理块数减少。必须使用整体综合的层级资源报告计入代价，不能只比较136位与160位载荷。
