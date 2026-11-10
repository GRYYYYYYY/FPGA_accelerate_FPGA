# 邻接排除硬件协议验证

32位正式实例通过27648个边上下文、354530次接口调用的C++、Csim、综合和RTL协同仿真；独立审计绑定原函数golden、完整真实CPU路由helper、冻结源、编译参数及每阶段终态收据。

START忙时拒绝；每条成功新边消耗一个单调generation。标签RESPONSE须匹配generation及phase；错误、旧、重复响应不推进状态。保持原函数条件读取顺序与arc路径再次prev读取。SNAPSHOT只读。gen3实例实际完成7条边后拒绝新START，无编号回绕；12次调用的RTL验证通过。没有执行2^32条正式实例上下文。

本接口仍为单上下文标量ap_ctrl_hs，调用方等待完成并捕获结果后再提交。冷复位必须排空旧消息；query/price/设计成本视图及异常清理仍需集成层管理。未连接真实标签页服务或完整设备搜索。

HLS报告资源只是估计；正式32位RTL的Vivado实际综合正在运行，结果exclusion_hls_vivado_synthesis_20261024。时序/平台/板上收益尚无结论。

代码与协议：../hardware/hls/exclusion/ARCHITECTURE.md。证据：exclusion_hls_20261024/source_bound_audit.json。

实际Vivado综合已完成并独立审计：798LUT、1415FF、0BRAM/URAM/DSP/latch，43.455s、exit0、checksumbf4b1600。10ns独立布局布线已启动，结果exclusion_hls_timing_20261024，尚未终态。接入标签页服务前的字段、地址范围、两种generation及零记录语义核对见../hardware/EXCLUSION_LABEL_BOUNDARY.md。

物理终态已完成并独立审计（116.2s、exit0）：791LUT、1415FF、0BRAM/DSP/latch；WNS7.124ns、WHS0.038ns、WPWS4.725ns，内部setup/hold/pulse失败与route错误0。287输入79输出尚无外部delay预算，因此只支持当前10ns内部模型结论，不是平台闭合或板上性能。final_audit.json绑定方法学报告、约束diff、时序路径与DCP。

接入时还需维护设计级created，不能用查询页rsp_present替代。当前没有后台实验需等待；下一步实现并验证标签服务适配器。
