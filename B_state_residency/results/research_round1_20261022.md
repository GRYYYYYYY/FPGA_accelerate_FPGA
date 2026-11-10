# 正式矩阵第一轮完整覆盖

26个配置各完成1次且通过同调度输出/收敛及图检查。以下仅第一轮原始值，不是三次中位数；78次正式矩阵仍继续。快照 `research_round1_20261022.json` 包含完整命令、环境、输出SHA和收敛数据。跨调度不计算状态实现收益。

| 设计 | 调度 | 变体 | 页节点数 | route秒 | 结束时context标签容量MiB | 全进程峰值RSS MiB |
|---|---|---|---:|---:|---:|---:|
| logicnets_jscl | batch | compact | 512 | 35.682 | 70.54 | 2607.4 |
| logicnets_jscl | batch | node_epoch | 512 | 37.450 | 224.54 | 2607.4 |
| logicnets_jscl | batch | paged | 512 | 51.171 | 192.54 | 2607.3 |
| logicnets_jscl | serial | original | — | 24.231 | 未单独记录 | 2607.3 |
| logicnets_jscl | serial | compact | 64 | 33.347 | 29.08 | 2607.2 |
| logicnets_jscl | serial | node_epoch | 64 | 32.995 | 57.08 | 2607.3 |
| logicnets_jscl | serial | paged | 64 | 34.507 | 49.08 | 2607.3 |
| logicnets_jscl | serial | compact | 512 | 33.060 | 76.14 | 2607.3 |
| logicnets_jscl | serial | node_epoch | 512 | 33.877 | 224.14 | 2607.3 |
| logicnets_jscl | serial | paged | 512 | 57.100 | 192.14 | 2607.3 |
| logicnets_jscl | serial | compact | 4096 | 35.317 | 76.02 | 2607.3 |
| logicnets_jscl | serial | node_epoch | 4096 | 34.783 | 224.02 | 2607.2 |
| logicnets_jscl | serial | paged | 4096 | 332.221 | 192.02 | 2607.2 |
| vtr_mcml | batch | compact | 512 | 142.395 | 70.89 | 4035.8 |
| vtr_mcml | batch | node_epoch | 512 | 167.934 | 224.89 | 4035.8 |
| vtr_mcml | batch | paged | 512 | 215.254 | 192.89 | 4035.9 |
| vtr_mcml | serial | original | — | 92.020 | 未单独记录 | 4035.7 |
| vtr_mcml | serial | compact | 64 | 132.014 | 23.79 | 4035.7 |
| vtr_mcml | serial | node_epoch | 64 | 127.057 | 57.79 | 4035.7 |
| vtr_mcml | serial | paged | 64 | 123.843 | 49.79 | 4035.8 |
| vtr_mcml | serial | compact | 512 | 131.282 | 38.22 | 4035.7 |
| vtr_mcml | serial | node_epoch | 512 | 124.662 | 112.22 | 4035.7 |
| vtr_mcml | serial | paged | 512 | 187.369 | 96.22 | 4035.8 |
| vtr_mcml | serial | compact | 4096 | 132.853 | 134.03 | 4035.7 |
| vtr_mcml | serial | node_epoch | 4096 | 132.501 | 448.03 | 4035.7 |
| vtr_mcml | serial | paged | 4096 | 690.707 | 384.03 | 4035.7 |

标签容量是结束时context数组容量之和，不含全局dyn、allocator和其他路由结构；不是峰值，跨worker峰值不能简单相加。全进程峰值RSS包含加载峰值，加载后采样峰值由独立汇总器提供。

原始串行在两个设计中仍优于本轮全部标签适配。64节点页抑制了整页清零的放大，紧凑池减少context分配容量，但是否值得额外映射开销必须等重复数据；不能据单轮为硬件定案。物理质量证据只覆盖对应结果哈希：MCML仍保留1条RTSTAT-10警告，未验证全DRC和时序。
