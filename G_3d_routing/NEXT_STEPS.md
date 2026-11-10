# 方案 G 继续研究入口

先阅读 [本轮基线记录](results/BASELINE_REPORT.md)、[INTERFACES.md](INTERFACES.md) 和 `configs/vpr.lock.json`。已从 CPU toy 推进到原始 VPR 模型基线、完整 RRG 导出及独立审计。原始素材与相邻研究工程保持原状。

```bash
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
python3 -m unittest discover -s tests -v
python3 scripts/run.py baseline
```

`baseline` 默认 seed=1、W=100、两种 ex5p 布局各 3 次串行 route-only。运行库已在 `toolchain/runtime/`，不要依赖容器的全局 TBB 安装。原布局虽使用 CHANZ，但端点没有跨层连接；平衡 CLB 布局是人工压力例。模型 CPD 不等于实物签核，当前没有加速收益结果。

1. 实现离线候选选择入口，从冻结的路由树分支构造任务；保留 source/sink 的精确 RR ID、net ID 和 occupancy/price 版本，明确是否允许多次跨层。
2. 将原生 `CHANZ` 作为共享有容量节点。排除无入/出边的 404 个通道，再按精确有向可达性筛选；不能仅凭坐标距离或层差判断。
3. 首先比较全图搜索、简单垂直惩罚、分层候选选择的相同目标函数，并报告候选数、不可达、回退和无收益案例。不要把单连接最短路当作完整协商布线质量。
4. 验证相同 net 的多分支共享、容量冲突和原生延迟模型后，再接回完整 VPR 的拥塞协商及时序刷新。其他项目的 H3D 改动可阅读和按哈希引用，不能当作本方向已经实现的算法。
5. 扩展真实自然跨层布局、多个电路/种子和密度/延迟配置；现有两种布局不能互相作为算法收益对照。质量容差仍未设定，先报告完整差值。
6. 根据实测热点决定 HLS/FPGA 候选评估范围，届时按 Ross Skill 和 Vivado MCP 规则执行。当前阶段不需要启动 Vivado。

`configs/experiment.json` 仍兼容共享脚手架的状态枚举；本地 plan 和 `standalone_status` 描述已接入的原始 VPR 入口。其他算法变体不可用，禁止将它们指向 toy 或原始 VPR 并称作算法对照。

待确定信息：正式电路矩阵、质量容差、候选预算、板卡/XRT 条件。它们是研究待办，不是额外审批步骤；可依据已有数据与授权继续推进。
