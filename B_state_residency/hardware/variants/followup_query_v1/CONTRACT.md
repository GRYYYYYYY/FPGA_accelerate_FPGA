# 真实第二轮准备态 RTL 验证

从已通过natural_stages TB生成独立测试台，生产RTL/dat沿用candidate_recursive_pilot冻结文件，不做功能修改。输入为logicnets iteration2/sequence180327、connection170782、net26422、source66893、sink204279；170次expand全部已缓存。

- 加载完整warm design16B记录、owner primary、53734项pool（补齐64B）及allocator。pool base=primary+145424192，allocator=pool+859776；单文件146284032字节，三个区间不重叠。
- 加载第二轮history/价格/net成本/CPS1表。旧prev/visited及source准备态标签从CPU保守读闭包导入，不将其清零。搜索sequence180327为32bit，存储query/price epoch由原分页控制器独立管理，不能把两者混用。
- 实际heap POLL返回parent，实际host target标签决定停止。CPU事件仅用于评分，不为下一parent赋值。外层调度仍为TB而非可综合自主search。
- 期望171POLL、170expand、853捕获child、849候选判定、421cost/OFFER、1263标签ACK、EARLY1；最后4个captured child应排空而不再判定/成本/提交。
- 原32槽与单槽分别运行，预导入822条标签/403逻辑页。最终完整物理页、design、owner、cost与全部AXI字节日志独立核对。

这验证从CPU准备态恢复一个后续query，不包含从前一query在同一RTL实例连续提交/切换。未知工作集标签初始化、warm cache全图构建、硬件backtrace/owner commit及板卡测量仍未实现。不得把本仿真称为完整多query生命周期或全设计FPGA路由。
