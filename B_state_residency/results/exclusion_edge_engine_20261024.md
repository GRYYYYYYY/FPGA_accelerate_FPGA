# 排除边引擎整合结果（2026-10-24）

最终 `hardware/variants/exclusion_engine_v4` 已把实际HLS排除判断、调用收集器、边调度器和label_v2桥接器连接起来，在冻结sparse_records原生端点RTL上完成判断/标签访问验证。页映射仍由测试代理提供，尚无自动分页或完整设备路由。

## 功能证据

| 检查 | 最终结果 |
|---|---|
| 原始CPU函数生成的边 | 27648组合＋32空记录边，共27680条 |
| 期望标签读取 | 34898次，判断、请求节点/阶段顺序、返回给HLS的值全部一致 |
| 完整回归（含错误/恢复） | 110686项检查；34911次标签请求、34906次原生READ、62592次HLS调用、34904次RESPONSE |
| 错误及恢复 | 13种场景，失败不再提交HLS RESPONSE；覆盖Machine四个标签等待阶段的中止/协调复位 |
| 调用收集器 | 五个独立ap_vld与ap_done全部720种排列，721次完整调用、9类故障通过 |
| 真实缩位HLS耗尽 | 3位编号两轮各7条成功/第8条拒绝；中间协调复位，共14成功、2耗尽、16次HLS调用 |

独立oracle使用原始CPU函数逐字节抽取，不调用候选helper。27648项含全部flags、created、Laguna及prev/visited关系组合，分布为同页/跨页/最高地址各9216项；拓扑与组合按顺序分配，并非每个组合又乘三种拓扑。空记录保持resident_zero原值，created不由present推断。

最终结果 `results/exclusion_edge_engine_v4_20261024`，独立 `scripts/audit_exclusion_edge_engine_v4.py` passed；manifest SHA256 `2c672896900d88a88f5db880214c0b16ba4b54ae4fc8d38fa6b183ce483cef6c`。源码、生成HLS RTL、原生端点、oracle/fixture、编译/仿真命令、各报告与前序门禁绑定。

## 实际发现与修复

1. **测试台超时采样错误。** 首轮在166951ns捕获了时钟沿前已消失的组合fault条件。VCD表明没有锁存故障。改为跨过规定期限检查锁存结果，保留原失败与波形，未修改RTL或降低通过标准。
2. **HLS静态状态未被ap_rst清除。** v2完成27680正常边后在复位恢复阶段失败。独立小用例直接证明旧构建复位后返回generation2。新 `hardware/hls/exclusion_reset_state` 使用2022.2支持的 `config_rtl -reset state`，算法源码不变；32位354530调用和gen3耗尽的C++/Csim/Csynth/RTL cosim重新通过。相同复位小用例现通过4次调用/3次复位，包括清除待处理标签状态。负/正例分别在 `exclusion_reset_negative_20261024`、`exclusion_reset_positive_20261024`。
3. **组合握手反馈。** v3功能回归通过后，Vivado综合报1个LUTLP-1环（7 LUT），路径经ap_start→ap_ready→complete/fault→ap_start。v4断开ready相关组合故障到ap_start的反馈，外部abort仍即时阻断，内部故障锁存停止。完全相同的整链路测试再次通过，组合环归零，无豁免。

复位与调用契约的更正见 `hardware/HLS_RESET_BOUNDARY.md`。各失败、旧源码和旧独立物理结果保持不变。

## 实际综合

`results/exclusion_edge_engine_v4_synthesis_20261024`：Vivado2022.2、U280、OOC，55.875秒/exit0/checksum dee28a76；**1172 CLB LUT、2190 FF、39 CARRY8，0 BRAM/URAM/DSP/latch**。该范围包括新state-reset HLS、调度/收集器和标签桥接器，**不包括原生状态存储端点**。

LUTLP-1与check_timing的loop均0，内部无时钟/未约束终点为0，零critical warning/错误。159条未使用端口warning、1条并行综合规模warning保留；另有OOC HD.CLK_SRC未设置提示。419输入、228输出无外部delay。独立 `scripts/audit_exclusion_engine_synthesis.py` passed，绑定DCP、源码、报告和实际MCP收据，也明确记录v3为结构门禁失败，即使工具exit0。

未布局布线，不能声称该整合引擎时序闭合；不能套用旧独立exclusion组件的WNS或资源。

## 剩余工作

下一步实现页解析与租约、原生命令仲裁及miss时合法WB/RELEASE/BIND/RF流程，加入真实换页/背压/错误恢复测试；随后连接图读取、getChildren首次过滤缓存与created/deadEnd副作用。完整搜索仍需统一价格、设计级占用、frontier、回溯和提交所有权。

本轮使用三个预绑定槽、32帧目录、生产16位页绑定/epoch；无AXI活动。27680条是单边功能验证向量，不是完整570286次CPU搜索的硬件重放。既有全38状态端点回放9.5213%的时间降低仍只属于该回放实验，本轮未新增完整路由或板上加速数据。
