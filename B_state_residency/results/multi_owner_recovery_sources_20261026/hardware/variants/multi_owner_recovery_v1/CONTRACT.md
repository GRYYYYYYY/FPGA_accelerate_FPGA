# 同资源多net、满overflow池恢复

当前候选coordinator由build.py从已审计warm_retry_system_v2生成，只增加有界容量延后状态；不改变原始共享基线文件。正常无CAPACITY路径仍沿用原两轮修正/验证。

## 实际反例与修复

真实iteration2 CPU快照：N=9,089,009，overflow capacity/live/next_unused均53,734，free_head=0。节点208292原始owner为net6632/ref1与net17601/ref2，occupancy2；overflow slot1属于后者。

变更序列是基于真实快照构造的确定压力输入，不是自然路由轨迹。在真实可写owner引擎依次执行并先记journal：删除net6632（提升net17601并释放slot1）、加入net0（复用slot1）、net17601引用增加两次。四次mutation仅产生三项(node,net)去重键，occupancy仍2。旧coordinator首先补回net6632时返回CAPACITY5，继而恢复status3/J3；后续net0本可被删除释放槽位，因此最终快照放得下而中间顺序失败。

新coordinator只对INC的status5、cookie匹配、count/occupancy与此前GET相同、missing refs=0且尚未追加修正轮的已知无写入拒绝，记录一次延后并继续。后续net0删除释放槽位，net17601减回2；追加一轮补回net6632，再整轮验证全部key/ref/occupancy。若追加轮仍遇容量不足，则返回原失败status3并保留journal，不循环等待。物理总线错误与其他逻辑错误仍走失败出口。追加轮使用独立authority cookie位，旧回执不能混入。

## 证据范围

- multi_owner_capacity_negative_v4：旧生产coordinator在真实快照/owner/authority组件上复现status3/J3，第一次authority实际SLVERR后非冷复位重试仍失败。
- multi_owner_capacity_fixed_v1：同样初始状态与请求，修复后恢复成功，实际4次修正、J0；原pool大小不变，allocator回到满池状态。只在目标节点/slot1发生合法布局变化，所有其他owner节点/池条目字节保持。
- 独立CPU owner_store模型逐条检查实际21个owner操作与每个响应、逐条匹配16个物理record写，并比较最终146,284,032字节；原始CPU节点/overflow映射和只读快照也独立交叉检查。negative对应6操作/8写。所有live/snapshot AXI读写重放通过。
- multi_owner_capacity_bound_v1：模拟的永久无写入CAPACITY回调，恰两次拒绝、一轮追加后status3/J1，成功标签回调从未发生。此项为控制器单元，不是AXI实验。
- multi_owner_normal_full_v1/pressure_v1：新coordinator用于完整系统正常G2共享恢复；两容量28文件及周期与既有shared-last基线精确匹配。

owner/authority/coordinator实验的reconfigure和labels_done是模拟回调，尚不是完整warm路由系统的多net快照恢复。正常完整系统回归仍是原capacity0 fixture，不可将两者合并宣称完整多net warm恢复已完成。并发上下文、任意journal排列、持久化认证/floor、运行时快照、变价有效性、综合时序和板卡仍待验证。
