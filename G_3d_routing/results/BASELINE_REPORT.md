# 原始 VPR 基线接入与复现（2026-10-22）

本轮完成：固定原始 VPR 工具链、导入完整原生 CHANZ RRG、建立 G 目录独立运行与审计入口，并复现两种 ex5p 布局各 3 次。6/6 次通过原生 FULL 检查、独立审计、SQLite 图核对和归档参考一致性检查。没有修改相邻研究工程或公共基线。

## 固定输入与范围

- VTR 提交：`0b912334fdd83bb754b302146ac0d1ec9edc9a0e`，报告版本 `9.0.0-dev+0b91233`；此次未克隆 LaZagna，也未从相邻修改中工作树重编译。
- 基线程序 SHA256：`37cc22c8b1b5d9d378e25379e85afcb7e56b5f1f6f72e3e9186e5e107ed5ce62`。归档构建记录的 source_status 为空、补丁哈希为空文件哈希；详细证据见 [工具链锁](../configs/vpr.lock.json)。
- Hecate 原生 CHANZ 三维架构模型，device_width=30、W=100、seed=1、num_workers=1，timing-driven、flat_routing=off。
- 同一 BLIF、packed netlist 和 XML RRG，两种 placement：原始 ex5p；将 78 个 CLB 中的 39 个移到另一层、保持 XY/subtile 的人工压力例。比较算法时必须固定其中一种 placement。
- CPU：Intel Xeon Gold 6530，Ubuntu 22.04 环境；串行 route-only，没有重新 placement。原始输入只引用，运行前后校验 SHA256。

## 结果

| 布局 | 成功次数 | 跨层源汇连接 | 使用 CHANZ | CPD (ns) | 水平线长 (tool unit) | 原生路由时间中位数 [min,max] (s) | 进程 wall 中位数 (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 原始布局（端点跨层负对照） | 3/3 | 0 | 323 | 5.17424 | 20656 | 0.82 [0.81, 0.82] | 5.874 |
| 平衡层压力布局（人工构造） | 3/3 | 1016 | 652 | 5.61388 | 19666 | 0.64 [0.53, 0.65] | 5.624 |

两种布局均为 679 个已路由 net、1,979 个 sink，溢出资源数为 0。各自 3 次的路由记录、CPD、线长完全一致，并与先前归档的原始 VPR 结果一致；比较只忽略 route 文件头的路径文本，节点、switch、分支重启和 sink pin index 均保留。

原布局用了 323 个 CHANZ，但没有端点跨层连接；使用垂直通道不等价于存在跨层源汇需求。人工压力例有 1,016 个跨层源汇连接，是下一步候选评估的语义测试输入，不能据此声称自然三维布局质量。

上述时间来自 CPU 实测，不是 FPGA 周期估算。原生 Routing took 的打印精度为 0.01 s；进程 wall 包括读取 RRG、routing 和 analysis，不含哈希、导出或独立审计。共享主机负载、缓存和 case-major 顺序未受控，只有一个 seed。本表是描述性基线，不提供加速比、置信区间或两种布局间的算法收益结论。CPD 是模型 STA，不是实物签核。

## 完整 RRG 与候选语义

[导出摘要](../data/derived/ex5p_w100/summary.json)对应 264,994 个节点、2,366,014 条有向边、6 个 switch、6,658 个 CHANZ。400,256 条边与 CHANZ 相接，没有绕开 CHANZ 的直接跨层边。

每个 CHANZ 容量为 1；该模型垂直导线 R/C 都为零。入/出边使用不同 switch，实际 Tdel 分别可为 0.142 ns 和 0.09877 ns，不能把任一个值当作完整跨层路径延迟。SQLite 中未显式写出的可选 timing 属性保持 NULL，不静默替代为测量值。

6,254 个 CHANZ 同时有入边和出边；另 404 个两者都没有。这 404 个不能成为候选，剩余通道仍须针对具体 source/sink 验证有向可达性。容量属于 CHANZ 节点，所有入/出边共享它，不给每条边独立预算。源图 XML 继续作为 VPR 权威输入；SQLite 是用于搜索与候选算法的投影。

## 验证与失败记录

- 7 个适配器测试全部通过：稀疏 ID、平行边、方向/switch 身份、共享容量、坏分支、缺失 timing、非法图、哈希漂移和禁止覆盖等语义。
- 6 次原生 FULL checker 均通过。独立 XML 审计检查有向连接、switch、树结构和节点/垂直资源容量；派生图检查覆盖每条实际路由节点/边。
- 独立审计不单独认证端点对网表映射、局部 OPIN 预留、非配置边闭包和 bus mux 选择；这些仍依赖 VPR。
- `check`、`plan`、`smoke` 均通过。数据登记有 2 条 ready 的模型输入；plan 有 2 条可执行原 VPR 基线，其余算法待实现。
- 首次 6 次启动因当前容器缺少 `libtbb.so.12` 等库而退出，未发生布线，保留在 [失败批次](baseline_20261022T145539.324186Z/summary.json)。随后从 Ubuntu apt 索引下载并在 G 目录解包 TBB 依赖，包与库哈希进入锁文件，增加启动前依赖检查。未全局安装，未修改其他项目。

## 可复现产物

- [成功批次完整 summary](baseline_20261022T145747.876726Z/summary.json)：每次完整命令、输入/代码/程序哈希、环境、指标、检查及原始文件哈希。
- [原始布局第一次运行](baseline_20261022T145747.876726Z/ex5p_natural_r1/result.json)；[跨层压力布局第一次运行](baseline_20261022T145747.876726Z/ex5p_balanced_r1/result.json)。相邻目录保存全部日志、route、时序报告和独立审计。
- [原始布局输入](../data/raw/ex5p_natural.json)、[压力布局输入](../data/raw/ex5p_balanced.json)、[接口约定](../INTERFACES.md)。

```bash
python3 scripts/run.py baseline
```

后续任务是基于冻结图的离线候选端口选择、有向可达性及共享容量验证，然后接回相同 placement 的完整协商布线对照。简单垂直惩罚、CPU 候选选择、树 DP、GPU/FPGA 后端尚未在本目录实现；相邻项目已有算法结果不计作本目录新实验。
