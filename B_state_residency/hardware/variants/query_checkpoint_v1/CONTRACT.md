# Query lifecycle 序号 checkpoint

从 `authority_query_v4` 冻结的 query_lifecycle 派生。补充真实易失状态：sequence_seen、last_sequence、last_design/version/query/price 与 label_state_dirty。普通生命周期和后端接口保持原逻辑；checkpoint 期间阻止普通命令和全部后端请求。只有调用方提供 cp_safe、工作/回复/后端已退休、active 且无错误时接受。

固定10个little-endian32bit字：0魔数0x51435031；1格式1；2/3 design低/高；4/5 generation低/高；6 version；7 query[1:0]、price[5:2]、sequence_seen[6]、label_state_dirty[7]，其他位0；8 last_sequence（未见序号时为0）；9保留0。CRC32/IEEE LE，初始ffffffff、poly edb88320、结果取反；CRC由完成回复提供，不构成认证。

捕获时上下文从active及active_generation取值，generation/design/version必须非零。已有sequence上下文必须与当前active匹配，否则导出拒绝。导入严格index/last、先私有暂存，校验CRC、全上下文/格式/保留位与seen/sequence规范，再单沿发布全部ledger。错误1，取消/权限或上下文漂移2；错误不替换已发布ledger。同一活跃生命周期内不能回退已见sequence，不能通过导入旧clean图像清除已有label_state_dirty。冷复位后这些本地单调下限本身也丢失，仍必须由可信同代checkpoint与外部持久化下限防回放。

导出背压或取消不能撤回已暴露输出，仍退休完整10字后报告失败；导入失去安全条件即丢弃私有暂存。导入失败后上游须丢弃余下旧流。没有输出超时，永久背压可以阻止完成。cp_safe必须覆盖整个一致恢复过程及稳定的active_generation；本组件不能证明owner/labels/路径已恢复或内存不可变。

本变体当前为原生query控制器组件；后端是注册mock，不是八路AXI完整系统冷恢复。此前完整query top还未改接这个接口。generation仅绑定图像与调用方active上下文；不替代generation轮换、统一描述原子发布或恢复协调器attempt_version/query的持久化。实际epoch回绕、跨cold-reset的旧可信checkpoint回放、序号耗尽后的安全换代、owner/path/labels/config一致恢复仍缺。不得把该组件通过说成完整checkpoint完成或板卡收益。

冷启动/恢复模式由外层区分。恢复启动必须在完成全部匹配状态及本ledger导入前持续关闭普通admit；单靠cp_valid不能消除复位后、导入开始前的重放窗口。测试显式保留未导入即接受旧序号的反例。version/query/price只做上下文相等校验，不是恢复协调器的持久化attempt下限。
