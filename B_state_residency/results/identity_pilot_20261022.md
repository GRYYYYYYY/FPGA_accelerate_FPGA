# 反向身份校验标签：8次配对先导

8/8通过同调度输出SHA和逐轮收敛；实际日志、结果和label数据、冻结构建输入及参考绑定已复核，证据 `identity_pilot_20261022T214133Z/completion_audit.json`。每配置仅一次，不作统计显著或正式加速结论。

新实现使用成熟dense/sparse反向身份判定，页内uint32索引经过live_count边界和紧凑池global node ID双重验证，替代逐槽uint32 epoch。页面epoch保留，索引数组合法初始化；查询切换live_count清零，不复用旧距离。机制来源见RELATED_WORK.md。独立构建 `build/identity_real_v1`，原compact与78次矩阵未修改。

| 设计/调度 | 页节点数 | compact秒 | identity秒 | compact容量MiB | identity容量MiB | 容量下降 |
|---|---:|---:|---:|---:|---:|---:|
| logicnets_jscl/serial | 64 | 34.981 | 36.291 | 29.08 | 23.08 | 20.6% |
| logicnets_jscl/batch | 512 | 35.198 | 36.167 | 70.54 | 39.54 | 43.9% |
| vtr_mcml/serial | 64 | 131.046 | 135.904 | 23.79 | 16.79 | 29.4% |
| vtr_mcml/batch | 512 | 142.185 | 147.184 | 70.89 | 39.89 | 43.7% |

容量为结束时所有context的mapping、epoch、页表、紧凑payload、反向ID数组之和；全局dyn另存且未变化，未测RSS。这不是全流程内存等比例下降。串行只测64节点页，batch只测512节点页，不能据此推断其他粒度。

本轮四组identity耗时均略高（约2.8%–3.8%）。依赖链中多一次反向身份访问是可能原因，但未进行新PC/硬件计数采样，不能作为已证实归因。当前保留容量优化候选，不把它升级为性能默认方案，也不因单次结果宣称稳定退步。若后续需要正式容量/时间Pareto比较，应另外做预注册重复，不能将先导混入之前三次。

ASan/UBSan检查真实生成SparseLabels类：三种页粒度、独立context、池增长、静止回收、页面epoch回绕；攻击性测试包含旧索引落在live范围但身份错误，以及UINT32_MAX索引的prefetch/访问边界。结果 `../build/identity_real_v1/semantic_tests.json`；全套32个Python检查通过。

四个输出哈希与既有物理验证完全相同，可复用同输出的证据；MCML RTSTAT-10警告仍保留，不能写成零违规。没有新增GPU/FPGA、真实设备同步、运行中页置换或时序结论。

后续优先补运行中页写回/换入的正确性协议：有效标签不能在LRU驱逐时丢失，迟到完成必须验证查询身份、价格版本和物理槽身份。当前Context仍将查询页持有租约至finish，尚未实现这类置换；需要在独立模型与测试中补齐，再考虑RTL/HLS实现。
