# 常量切片小页codec对照

仅改变动态record/beat切片实现，保留192B格式、状态机和握手。独立99用例/286检查通过；同输入2851周期差分通过，结束28610ns与原版相同。不是全输入形式等价。

同Vivado2022.2/U280/10ns/2线程OOC配对综合完成：

|资源|动态切片|常量切片|
|---|---:|---:|
|LUT|4215|1972|
|FF|1627|1582|
|BRAM/DSP/锁存器|0/0/0|0/0/0|

LUT减少53.21%。MCP147904 source exit0/118.015秒，cell1607回收、close_project后闲置。输入hash、DCP和收据审计通过，final_audit SHA6e0e63402efe10b5023bb4f297a82fc171b91bad26e8259e6eacfc35388c7251。独立codec数值不同于整端点层级报告的5115LUT，不能直接从整机资源减去差值。

新增record_backing_service_small_staticcodec和memory_scratch_endpoint_small_staticcodec，仅替换模块名/codec引用。32槽+阻塞回收回归通过1778检查/288传输/8checkpoint/800阻塞周期，结束694830ns与原端点相同；runner84060 exit0，manifest 491c80801a8b2a29c09d1b9c0fddc6b6a8f8db64f4e75222f05fd9ea03e48d97。两个真实38查询回放仍使用原版冻结DUT。

该阶段之后的整端点综合与真实轨迹验证已完成，结果见下文。配对布局布线已完成（见rtl_small_codec_endpoint_timing_20261023.md），不宣称实卡吞吐或平台时序收益。

真实19查询复核：静态codec整端点通过75194命令、5183传输，0错误。逐查询命令/传输/模拟完成时间和动态版全部一致，总20885360ns。证据：`rtl_static_checkpoint_stream_pilot_20261023/final_audit.json`及`cycle_comparison.json`。此比较保持同一冻结输入与目录配置，仅替换codec；不代表形式等价或板级性能。

完整端点默认容量综合通过：动态14651 LUT/11164 FF → 静态11688 LUT/11123 FF，LUT减少2963（20.22%）。两者均319 BRAM、3 DSP、0 latch。相同U280、10ns OOC、163840帧和32槽配置，完整证据位于`rtl_static_endpoint_synthesis_20261023/final_audit.json`。尚未物理实现或板级计时；目录BRAM成本仍未降低。

配对物理实现完成：布线后LUT14511→11571（-20.26%），WNS2.109→0.766ns，WHS均0.037ns，内部失败端点均0。两版最差路径均位于目录，缺平台IO/物理时钟模型；不能据此宣称实卡闭合。
