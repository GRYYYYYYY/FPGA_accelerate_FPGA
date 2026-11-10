# 完整系统换代后 warm 故障恢复通过（2026-10-26）

详见 results/warm_system_20261026.json 与 hardware/variants/warm_system_v1/CONTRACT.md。选定 warm_system_v2，32槽/单槽两例真实G2发布后，q2首个owner写B发生SLVERR；真实fence和coordinator从G2只读窗口两轮GET修复一项journal（node1231788/net2717，目标ref0/occ0），不是TB伪造owner/完成回复。

原生标签模块经实际DDR/pager写入和回读328记录，原生路径恢复q1槽，原生查询以原始G2镜像/CRC转换到新attempt5/query3/price5并保留seq1。实际标签回复可先消费，三种回执全齐/退休、最终恢复回复消费后才放行业务；无需普通checkpoint lease（实际pc_owned0）。q2随后通过CPU独立数值oracle：43poll/42expand/176candidate/122cost及最终标签；两条原生路径可拆线，共享263946/554512引用1→2→1→0。全8AXI/最终DDR、恢复真实标签数据、源查询字节、G2修复地址及全部回执顺序重放通过，其他net状态保留。

修复两处接线/阶段问题：前端ready本身就是后端受理，必须在真实backend offer选择模式并同沿arm；标签恢复自身建立新上下文，不能在启动前要求它已经建立。旧完整实例出现wm_mode0未arm失败；旧上下文join在140ns/check9失败。新上下文原生切片405检查通过，两负例及修复证据均保留。关闭warm的normal_v2两容量共28文件和周期精确匹配前轮。五归档实际恢复重审audit一致，源冻结results/warm_system_sources_20261026。

JSON另列行为RTL仿真阶段周期（owner、label、path、query及故障到重试），不是板卡时间或加速比。价格/history DDR始终不变，attempt标签改变；不能宣称任意价格变化下距离标签有效。

当前只覆盖一个net/两路径、capacity0的首个q2 owner-B故障。共享节点故障、多项journal、恢复流/AXI在途取消、非冷复位失败重试、epoch回绕/未知页、通用多net/overflow、运行中工作DDR快照、持久化认证/下限、综合时序和板卡仍缺。下一优先共享资源写故障（G2应恢复ref1，区别旧G1的ref0）及多项journal，再取消/退休与无冷复位重试。研究继续，goal active。
