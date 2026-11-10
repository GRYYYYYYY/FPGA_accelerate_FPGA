# 单命令查询生命周期RTL通过（2026-10-25）

`query_lifecycle`与`query_residency_system`在已验证的四路搜索注入版上新增外层编排。主机一次命令后，硬件执行source根标签检查、目标/源标签准备、真实堆搜索、路径提交、目标清除、标签CHECKPOINT和物理排空；完成响应消费前始终保持16入口+手动route围栏。120个旧RTL/dat/top保持，358逻辑端口/56927接口位。新`qc_*`端口避免与连接服务的`q_busy/q_fault`重名。

每次准备只写sink.target=1、source.lb=0、source.upstream=0、source.visited=sequence。设计级占用、历史拥塞和其他标签保留。搜索成功才发路径提交，提交后清sink.target并刷回。新命令必须使用空saved-slot和严格递增非零visited序号，且同一设计/query/price/version上下文；原source.prev必须是root sentinel。自动查询开始后的外部标签写会使后续命令被拒绝，直到正确复位/重建标签状态；手动ripup仍通过既有入口。

## 验证

- 28模型场景通过：连续双查询、接受后输入复用、源不存在/非root、准备/搜索/提交/清理故障、错误cookie/目标/ACK计数、限时、各请求阶段取消、物理排空/完成背压、序号重用/外部标签编辑拒绝、source=sink零内部节点路径。
- 32槽和单槽两次真实服务执行，各包含两个自动查询和两个外部saved-path ripup。查询期间全部16host+手动route竞争；接受后反转命令source/slot/descriptor/cookie仍得到正确结果。
- 116POLL/114expand/447候选判定/293cost-OFFER/879标签ACK与CPU逐位一致，CPU路径回溯也一致。四阶段owner全图像及共享refs1→2→1→0、不同net占用1→1→1→0保持，CPU q3双提交快照再次确认。
- 独立审计覆盖每次2713普通服务请求的载荷与退休、1650host标签写（1640初始导入+每query5次生命周期写）、两次全328标签准备态推导、七AXI字节重放、整个design/owner和16384标签帧。六AXI活跃，table仍无流量。
- 最终328条标签读回在每query完成后执行，目标位必须为0。原CPU抓取位于清理前，审计只对本次sink.target应用原源码的清理语义；路由控制器读取标签时target仍为1。不是沿用旧标签图像哈希冒充清理成功。

| 整段仿真 | 32槽 | 单槽 |
| --- | ---: | ---: |
| 新生命周期版 | 657222 | 724963 |
| 旧外部准备/提交版 | 682354 | 745363 |
| 标签读事务 | 490 | 1414 |
| 标签写回复 | 263 | 618 |

**不能把这组周期差当作加速倍数**：新测试移除了旧TB查询间328条prepared评分读取，同时增加source校验、q1初始准备、q2目标清理和最终刷回。确认的是硬件完成单命令生命周期，搜索数学与状态正确；端到端同等负载性能仍需另测。

## 完整综合与代价

Vivado2022.2/U280，默认32槽/16384帧，诊断关闭；原生Tcl 585.752s exit0。300秒观察交回后继续监督原PID，没有重启。

| 资源 | 上一四路搜索版 | 生命周期版 | 增量 |
| --- | ---: | ---: | ---: |
| LUT | 86129 | 86880 | +751 |
| FF | 61699 | 62800 | +1101 |
| BRAM Tile | 160.5 | 160.5 | +0 |
| DSP | 23 | 23 | +0 |

零URAM/latch/blackbox/file-agent实例。2441条警告分类保存在审计JSON，包含继承HLS未使用端口和数组落寄存器等。没有时钟约束、布局布线、Fmax或板卡测量。

## 失败与后续

取消/超时不撤已发请求。特别是search descriptor已暴露时，先允许其接受，再向inner search传播取消；route已暴露时可能完成owner提交后才报告取消。返回保留确认ACK和native提交报告；`rsp_committed`不是独立成功证明，外层status0才表示清理/排空完成。错误B回复也可能已有未确认副作用。失败锁住普通流量，响应消费后可移交既有恢复；本轮没有新增真实生命周期故障恢复证据，也没有rollback。后端永久不响应时不能保证有限完成时间。

首次初始化目标集合必须为空或仅含首命令的单sink。多altSink/任意reroute不在当前接口覆盖内；它们和真实search/prepare/cleanup阶段故障、非空目标堆CLEAR、完整snapshot/unknown-page/价格与序号回绕/容量预约/耐掉电是后续任务。当前authority/snapshot生产、初始CPU已知328标签导入和ripup发令仍外部；route-only journal不能当成完整search checkpoint。

源/入口：`hardware/variants/query_lifecycle_v1/CONTRACT.md`、`query_lifecycle.sv`、`query_residency_system.sv`、`interface.json`；运行`run_query_lifecycle_join.py RESULT INPUT`，审计`audit_query_lifecycle_join.py RESULT`。三结果归档实际移开原件/解压/逐文件校验/重审，audit字节一致：`query_lifecycle_restore_20261025.json`。143文件源冻结`query_lifecycle_sources_20261025`。首版接入因新旧q_busy/q_fault重名而watchdog失败，其源码/日志保留在`query_lifecycle_development_20261025`；修正版qc命名与构建碰撞检查通过，不把首版算作成功。

下一优先真实生命周期故障注入/恢复交接及完整checkpoint，再扩展目标集与任意工作集，并开展同等负载的性能测量。研究goal保持active。
