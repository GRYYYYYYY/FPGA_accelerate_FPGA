6位epoch端点物理实现恢复结果

v1在路由日志成功后工具进程exit134，未留下最终报告或routed DCP，失败证据原样保留。v2从相同综合DCP、U280/10ns/Default/2线程重新实现，增加placed DCP保存，现已终态成功并完成路由、时序路径、约束、资源与哈希审计。

|指标|静态codec epoch8|静态codec epoch6|
|---|---:|---:|
|布线后LUT|11571|12216|
|FF|11118|11111|
|BRAM|319|303|
|DSP|3|3|
|WNS ns|0.766|1.621|
|WHS ns|0.037|0.037|
|WPWS ns|4.458|4.458|

两者建立、保持、脉宽失败端点均0。epoch6少16个BRAM但多645个布线后LUT；本次实现WNS较高，不外推为普遍或单因子频率收益。最差路径owner BRAM到bucket CE，数据路径8.228ns。

627输入和847输出缺IO延迟，物理上游时钟模型未补齐，不能声称平台闭合或实卡加速。全38候选回放已通过，逐查询/CP收据及总周期与小页基线一致，见rtl_epoch6_checkpoint_stream_full_20261023.md。证据：rtl_epoch6_endpoint_timing_v2_20261023/final_manifest.json及completion_audit.json。
