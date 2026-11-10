默认小页端点全38查询RTL回放

8节点/页、32槽、192B/页、默认163840后备帧、epoch8动态codec。全部38查询、14047736字段访问通过；21466914条公开命令、2472066次页传输、28次保留后备checkpoint、16次页标签回绕，错误计数0。总模拟时间6246828510ns（10ns时钟）；不是主机耗时或板级性能。

独立逐查询参考计划、字段读值、页字节、checkpoint序列及输入/源码/日志哈希审计通过。传输字节474636672B，与软件小页有界checkpoint参考一致。自动workflow状态replay_audited。

证据：rtl_small_checkpoint_stream_full_20261023/manifest.json、final_audit.json。64节点原版全38回放仍未完成，不能将其已完成前缀作为全量性能对照；静态codec/epoch6候选的全量回放也仍在运行。尚未接入完整FPGA搜索路由或真实平台。

耗时分布：query30/31占总模拟时间44.66%、页传输44.54%、16/28次checkpoint，分别为1416798530ns和1372868140ns。区间包含主机节拍、内存与回收等待，不能解释为单独模块耗时。可复查small_full_query_concentration_20261023/queries.csv及manifest.json。
