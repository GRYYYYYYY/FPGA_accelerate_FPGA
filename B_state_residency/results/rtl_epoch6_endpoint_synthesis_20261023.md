6位epoch完整端点综合

相同Vivado2022.2、U280、10ns OOC、2线程、163840帧、262144哈希槽和静态codec，仅EPOCH_BITS从8改6，日志已核验目录层参数。

|资源|epoch8|epoch6|变化|
|---|---:|---:|---:|
|LUT|11688|12256|+568（4.86%）|
|FF|11123|11115|-8|
|BRAM tile|319|303|-16（5.02%）|
|DSP|3|3|0|
|锁存器|0|0|0|

索引BRAM192→176，owner125和页存储2不变。LUT增加原因尚未逐层归因。较短epoch每63次完整回收清表，epoch8为255次；38查询向量不新增清表。

19真实查询、32槽阻塞checkpoint及默认容量130次回收验证已通过，全38回放仍在运行。仅综合资源权衡，尚无epoch6物理时序或实卡结果，不据此修改默认配置。证据：rtl_epoch6_endpoint_synthesis_20261023/final_audit.json，包含源文件、DCP、日志及命令收据哈希。

层级对照已定位资源变化：directory -126 LUT，codec +29，memory子树合计-97；pages子树+665，其中work FIFO+566。总净增568主要落在FIFO等结构，不能归结为epoch比较器直接成本。scripts/compare_epoch6_hierarchy.py与epoch6_hierarchy_comparison_20261023/manifest.json可复查；这些是综合映射结果的定位，尚非根因证明。epoch6物理实现已独立启动。
