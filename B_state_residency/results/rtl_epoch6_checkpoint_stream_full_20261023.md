静态codec / 6位epoch完整真实轨迹回放

全部38查询、14047736字段访问、21466914公开命令、2472066页传输、28次checkpoint、16次页标签回绕通过，错误0。独立逐查询与输入/源码/日志哈希审计通过，自动观察器终态replay_audited。

与动态codec / 8位epoch小页基线比较：全部38条查询收据、28条checkpoint收据、终态计数及结束时间完全一致，均6246828510ns。此结论覆盖该冻结真实轨迹，不是全输入形式等价；较短epoch长期更频繁清表的代价仍存在。

默认容量保持163840帧。候选布线后12216 LUT/11111 FF/303 BRAM/3 DSP，内部10ns模型WNS1.621ns、WHS0.037ns，无失败端点。相对静态codec/epoch8，少16BRAM但多645个布线后LUT；缺平台IO和物理时钟约束，无实卡性能结论。

证据：rtl_epoch6_checkpoint_stream_full_20261023/final_audit.json，epoch6_full_cycle_comparison_20261023/manifest.json，rtl_epoch6_endpoint_timing_v2_20261023/final_manifest.json。64节点原版全量回放仍在运行，整体研究未完成。
