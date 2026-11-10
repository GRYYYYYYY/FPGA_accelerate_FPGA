# 实际五字段值与独立历史状态

完整真实CPU路由采集及终态审计passed，证据目录 `real_field_values_20261023T024250Z/`，进程50316/句柄54107已结束。新构建 `build/real_values_trace_v1` 派生自冻结index-LRU源码，不改旧构建或上游。

18个只读、10个写入站点逐字段插桩，读取返回原始primitive值，写入由持有实际LabelLease的代理完成；按float32/int32原始位模式和target字节记录，不经浮点文本转换。每条20B小端record：node u32、sourceLine u32、valueBits u32、field u8、write u8、reserved u16、histBits u32。hist从全局tl_dyn观测，不进入局部scratch codec。

选择首8查询、每轮首查询和此前全部19个大查询，共38个完整查询，14047736次访问（10324516读、3723220写），原始二进制280954720B。最大23279唯一页。逐查询从局部全零默认状态重建oracle，所有读位模式与已记录写入一致；每节点hist在同一查询内保持不变，记录到29626个非默认history节点观测、90个跨选中查询变化观测。这些计数不是完整history更新轨迹，不证明价格计算。

完整570286次真实搜索、12轮收敛、全部路由结果SHA与原始一致：`428fa84ffa9e9839965c5000a32a4078f2fc7ea3f787a50cd4f7aff57447aa84`。生成代理的原生ASan/UBSan检查通过，覆盖NaN payload、负零、负prev、最大visited、target=255、真实脏页换出/换入、租约释放、query重置和global hist保留。全套97项Python测试通过。采集插桩耗时不作为性能比较。

终态审计检查源/输入/输出绑定，manifest SHA `e6eaa58c27c56125f727d01f1d9189c71e943de2e9343912ea71a38f5f374aac`。同名router.cpp在平铺副本中会发生覆盖，权威源码快照位于按完整项目路径分层保存的 `frozen_sources/`；对应哈希在completion_audit.json中，不使用平铺同名文件消除歧义。

新 `src/scratch_page_values.py` 将lb/upstream位模式、prev、visited、target打包为20B显式记录，排除hist；64节点含presence bitmap后stride1344B。页值类型校验及位模式、缺省值、容量背压、原始字节refill、checkpoint恢复/重用的5项新测试通过。与原始NodeDyn 24B ABI不同，不是原始对象字节的直接搬运。最大查询codec字节上界31286976B，30 MiB预算足够；不含host shadow/元数据/快照、驻留槽、全局占用/历史状态，也不是总RSS证明。

真实值有限队列先导 `real_scratch_pilot_20261023T024745Z/` passed：19查询56588次访问，34610读/21978写；10位事务/槽代次、2位query/fence tag，2次中途恢复、21fence、42重复ACK、19迟到写回均被丢弃，原始字节最终值与oracle相同。实际30 MiB完整38查询回放及终态审计已passed，见下文。仍无DMA/RTL/设备执行或加速结论。

完整回放 `real_scratch_full_20261023T024846Z`：38查询/14047736访问、31中途checkpoint、69fence、138重复ACK、38迟到写回；实际后备峰值21883页，预算容纳23405页。577440次写回、2166437次换入；逐访问完整五字段比较及直接解码raw字节的checkpoint/终态oracle全部通过。终态manifest SHA `92cd24ce1cf515c9f53ccd85e63aa321245aef6642c2dd93fd9555cfc275c148`，审计文件为该目录completion_audit.json。price只用查询迭代号作tag，hist没有在后备池中搬运/重算；完整真实路由算法仍由CPU执行。
