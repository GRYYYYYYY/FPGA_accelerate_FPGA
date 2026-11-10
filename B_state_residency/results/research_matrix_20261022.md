# 两真实设计、页粒度和标签布局：78次正式结果

全部78次运行通过：两个设计×13配置×3次重复，正式矩阵与链均passed。独立存量证据复核 `research_chain_20261022T183749Z/completion_audit.json` 已重算78个结果SHA、重解析日志/时间/RSS并比较label数据，复核冻结输入/构建/驱动绑定以及四个物理输出证据。完整数据 `research_chain_20261022T183749Z/summary.json`，原始结果 `research_chain_20261022T183749Z/matrix/`。先导不计入统计。

原始串行在两个设计上仍最快。紧凑布局的主要实证收益是减少标签context容量；时间收益依赖调度和页粒度，不能宣称普遍加速。

## 三次运行中位数与范围

| 设计 | 调度 | 变体 | 页节点数 | route中位秒 [最小,最大] | 结束时context容量MiB |
|---|---|---|---:|---:|---:|
| logicnets_jscl | serial | original | — | 24.947 [24.231,25.231] | 未单独记录 |
| logicnets_jscl | serial | paged | 64 | 34.563 [34.507,35.124] | 49.08 |
| logicnets_jscl | serial | node_epoch | 64 | 34.263 [32.995,34.463] | 57.08 |
| logicnets_jscl | serial | compact | 64 | 35.204 [33.347,35.436] | 29.08 |
| logicnets_jscl | serial | paged | 512 | 57.536 [57.100,58.024] | 192.14 |
| logicnets_jscl | serial | node_epoch | 512 | 33.877 [33.810,34.034] | 224.14 |
| logicnets_jscl | serial | compact | 512 | 35.151 [33.060,35.563] | 76.14 |
| logicnets_jscl | serial | paged | 4096 | 335.914 [332.221,340.131] | 192.02 |
| logicnets_jscl | serial | node_epoch | 4096 | 35.085 [34.783,35.889] | 224.02 |
| logicnets_jscl | serial | compact | 4096 | 35.773 [35.317,36.293] | 76.02 |
| logicnets_jscl | batch | paged | 512 | 50.995 [50.927,51.171] | 192.54 |
| logicnets_jscl | batch | node_epoch | 512 | 36.520 [35.999,37.450] | 224.54 |
| logicnets_jscl | batch | compact | 512 | 35.682 [35.600,36.330] | 70.54 |
| vtr_mcml | serial | original | — | 93.390 [92.020,94.741] | 未单独记录 |
| vtr_mcml | serial | paged | 64 | 128.223 [123.843,130.558] | 49.79 |
| vtr_mcml | serial | node_epoch | 64 | 127.174 [127.057,127.868] | 57.79 |
| vtr_mcml | serial | compact | 64 | 132.014 [131.909,134.182] | 23.79 |
| vtr_mcml | serial | paged | 512 | 190.543 [187.369,193.231] | 96.22 |
| vtr_mcml | serial | node_epoch | 512 | 128.483 [124.662,130.753] | 112.22 |
| vtr_mcml | serial | compact | 512 | 132.618 [131.282,132.972] | 38.22 |
| vtr_mcml | serial | paged | 4096 | 709.185 [690.707,710.616] | 384.03 |
| vtr_mcml | serial | node_epoch | 4096 | 132.617 [132.501,134.964] | 448.03 |
| vtr_mcml | serial | compact | 4096 | 134.420 [132.853,136.018] | 134.03 |
| vtr_mcml | batch | paged | 512 | 215.254 [214.028,217.125] | 192.89 |
| vtr_mcml | batch | node_epoch | 512 | 168.225 [167.934,170.445] | 224.89 |
| vtr_mcml | batch | compact | 512 | 142.395 [139.939,144.179] | 70.89 |

## 结果解读

- 512节点页中，逐节点epoch相对整页初始化的同序串行耗时降低41.1%（logicnets）和32.6%（MCML）；固定batch分别降低28.4%和21.8%。但这些适配仍慢于原始串行，不把改善分页对照解释为整体胜出。
- compact相对node_epoch的512页串行context容量减少66.0%和65.9%，串行中位时间反而增加3.8%和3.2%。logicnets的compact串行范围较宽，三次数据不足以主张小差异稳定或统计显著。
- 同页固定batch中，compact相对node_epoch时间下降2.3%（logicnets，差异较小）和15.4%（MCML），context容量减少约68.6%和68.5%。改善不能跨调度与原始串行混算。
- 页粒度非常关键。paged4096串行335.914/709.185s，而paged64为34.563/128.223s；MCML的paged64略快于其node_epoch64和compact64。不能仅报告最大页的坏基线来放大改进。
- compact64串行context仅29.08/23.79MiB；512页为76.14/38.22MiB。全局dyn与其他路由结构仍存在，容量变化不等于进程整体内存等比例变化。

## 内存观察边界

context容量为结束时pool、epoch、页表、compact payload分配之和，不含全局dyn、allocator或其他路由结构，也不是峰值。三次全进程峰值RSS受加载阶段主导：logicnets约2607MiB、MCML约4036MiB，各变体几乎相同；不能据此说布线阶段没有节省。

512页batch的加载后外采样峰值RSS（中位数）：logicnets node_epoch约2505MiB、compact约2313MiB；MCML分别约3771/3484MiB。500ms外采样可能漏掉瞬时峰值，包含布线/写出，不是硬件内存流量。完整分项在summary.json。

## 可复查的质量与实验约束

串行CPU8，batch CPU8–12，固定4-worker参数与原冻结配置一致；逐进程、分重复块随机顺序。每设计/调度组内部输出SHA及逐轮收敛一致；四个唯一结果通过独立图检查（端点、边、环、跨net冲突、未布通均0）。跨串行/batch结果不同，不把调度引起的质量或时间变化归给标签布局。

对应四个结果已经严格物理比较和Vivado2022.2验证：logicnets两调度均27961/27961可布net布通、routing errors=0、RTSTAT=0；MCML两调度均70982/70982布通、routing errors=0，仍各有一条RTSTAT-10警告，涉及72net。72net的pin/port/PIP/状态与原输入相同，但警告触发原因未定，不忽略或宣称零违规。没有全DRC或时序结论。证据 `vivado_state_quality_20261022/all_outputs_quality_manifest.json`。

## 研究仍未完成的部分

完成的是两设计CPU消融矩阵，不是GPU/FPGA加速器。已有真实路径协议回放和缓存容量模型，但尚无真实设备同步、真实history事件回放、运行中页置换、有限版本排空或综合/实卡结果。后续优先评估成熟dense/sparse反向身份校验能否减少元数据与访问链，保持原始串行及最优小页分页对照；或先完成带写回/换入的正确性协议。任何新变体使用独立构建和独立实验，保留本次冻结结果。
