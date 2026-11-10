# 正常双查询与共享释放回归

在 transaction_fence_static_v2、13 个 retired_idle 导出、真实 journal adapter、recovery/config/label 控制器均保持原样的组合上运行原双查询 stimulus。build_tb.py 只替换故障 fixture 的测试激励，不重新实现 fabric 连线。编译完整真实 graph/design/pager/owner/cost/table/connection/heap/HLS 链；不以 mock 服务替代原服务。

输入为真实 logicnets 两条同网 connection。只在开始导入 CPU 已知的 328 标签联合工作集，后续由实际 POLL 返回 parent 并读取真实邻接/资源/成本数据。CPU candidate/cost/poll 文件只作结果核对，不能作为硬件选择下一 parent 的驱动。第二条查询继承首查询状态，执行 5 个标签准备字段更新。逐查询最终标签、第二查询准备标签、CPU q3 owner、全部物理帧和所有 AXI 字节仍独立核对。

四个 owner 阶段依次为 q1 commit、q2 commit、q1 ripup、q2 ripup。两条路径内部共享 554512 和 263946；共享节点 refs 1→2→1→0，但 occupancy 仍按 net 计为 1→1→1→0。journal 必须先于实际 owner 修改，共 24 条修改握手，去重后 10 个 node/net 条目；正常运行不清 journal、不伪造 checkpoint 推进。已有 checkpoint17 仅作为初始化的可信标记，本测试未执行恢复，不能据此声称第二查询或完整设计写入可以回滚。

每次前端 FS、原服务 FD、后端回复 FB 均记录，前后请求 packed payload 必须一致且无重复/遗漏。最终要求所有主事务退休、七 AXI 排空、原服务 retired_idle、fabric IDLE、无异常 reset/recovery。32 槽和单槽均使用相同 CPU 契约。这两条查询只有六类 AXI 实际产生读取，table AXI 未触发，不能作为 table 活跃排空覆盖。测试仍由 TB 实现搜索外层与 snapshot 生产，尚非可综合完整系统 top、未知页动态初始化或板卡实验。

transaction_fence_normal_dependent_v1 在这套真实双查询中，对每条查询的首个 root 回复插入真实 center HLS 和 cost AXI 读取续接。先消费前端父回复，再持有两个子回复 7 周期，要求原 operation_pending 和排他主机屏障维持到子回复及后端父回复全部退休。center 输入零坐标/零中心，期望状态0/距离0；cost 读取 source65185 的历史成本，期望原输入文件 float32 1.0。额外读取不修改路由状态，完整路径、标签、owner/design/cost 图像应与无续接基线一致。该场景补真实子服务退休边界；不等同恢复请求与搜索续接并发、任意外部写入恢复或完整恢复期故障覆盖。
