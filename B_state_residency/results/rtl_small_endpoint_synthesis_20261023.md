# 小页默认端点综合

Vivado2022.2，U280 xcu280-fsvh2892-2L-e，10ns研究时钟，2线程，OOC综合。默认163840帧/18位哈希/32槽/8节点页。MCP147904 source exit0、291.738秒，close_project后闲置；cell1586已回收。final_audit核验源hash、DCP、约束、0latch及RAM清单；final_manifest SHAa422f9b3f58b9c6018fb03bd24a7ee74316cc856b2654ae206b2b4504278afec。原启动manifest保留running历史值，终态以final_manifest为准。

|资源|64节点保留回收版|8节点小页版|差值|
|---|---:|---:|---:|
|LUT|6532|14651|8119|
|FF|5296|11164|5868|
|BRAM36等价|43|319|276|
|DSP|3|3|0|
|锁存器|0|0|0|

小页目录占317 BRAM、3587 LUT；驻留存储占2 BRAM；codec占5115 LUT/1622 FF。当前codec使用1536位整页寄存器和动态切片，值得做独立常量索引/多路选择实现对照。目录成本来自保持30MiB池时更多页面及更宽owner/index，不能只按固定256驻留节点估资源。

日志保留2条Synth8-693零重复（默认TX/GEN均16位）、10条Synth8-3917常量端口警告；完整会话片段和warning_summary在结果目录。未修改warning级别，未消除原始记录。

仅综合资源，不表示布局布线、平台时序或实卡性能。两版还改变了codec/槽位/目录等，不是纯页大小消融。下一步保留基线，分离codec实现与目录容量/布局的实验，再做配对实现与完整轨迹对照。
