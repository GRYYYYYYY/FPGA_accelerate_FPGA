# 原生目录/标签导出接入G2 warm恢复通过（2026-10-27）

详见results/runtime_label_snapshot_20261027.json与hardware/variants/label_frame_export_v1/CONTRACT.md。选定full_v3/pressure_v3、default_full_v2、unit_v4。新增默认关闭的ENABLE_FRAME_SCAN只读端口，经实际层级访问权威owners RAM，不在TB读取DUT数组造答案；新label_snapshot_reader从真实目录帧信息和DDR页产生node/payload记录，label_snapshot_checkpoint_adapter门控lease释放和manifest许可。

实际PC lease下先验证非空驻留槽的导出请求被拒绝；原生control(1)刷回/释放后才导出。新增resident_page_manager.snapshot_clean要求active/idle且valid/dirty槽均零，query root还检查pc_owned/pc_safe、无warm/joint占用，目录要求无memory lease/fault。读取不修改allocation/index/lease/TX floor，保持回复时不接受普通目录操作。11份生产源由确定脚本派生，正常接口为具名参数/端口兼容。

32槽/单槽均枚举403个已发布当前上下文帧、实际读取1209个64B AXI beat，输出822条当前有效标签及CRC。恢复文件由实际记录VALID/READY握手捕获，snapshot_count来自原生完成count，不再由CPU构造本轮warm标签文件。两容量物理帧顺序不同，流CRC分别a2b92ed0/9ae2e09b，独立审计确认逻辑记录集合完全一致且逐条等于q180327真实final（204279 target已清理）。

同一完整实例继续原生owner增量copy、G2/CP18共同发布，q180328第二owner-B故障、G2两键refs1/3修正、原生822标签写入/回读及path/query恢复、attempt4重试。原始path/query CRC仍1d36e333/79283e8e、floor180327；重试最终ledger180328/storage4/2/4，两路径共存。第一query171/170/849/421；故障前及重试第二query各114/113/564/302（poll/expand/candidate/cost），逐项对CPU。全部10路AXI、13次工作owner记录写、31个authority读beat、完整146284032B owner候选/工作图像和全部822标签/3MB backing独立重放通过。

单元102项检查及5个实际流背压周期覆盖原生目录配置/发布、只读/拒绝/保持/TX floor、上下文过滤、未发布页、R错误、在途R取消、扫描offer背压取消、页padding错误，23个真实读beat独立重放（1个R错误）。默认关闭扫描的32槽普通查询/历史ripup回归，8AXI+7DDR+完整native trace共16文件及周期逐字节匹配旧基线。四归档均实际恢复重审audit逐字节一致。源冻结results/runtime_label_snapshot_sources_20261027（36文件）。

边界：初始822条CPU未来读闭包、历史路径元数据、初始准确G1 clone仍是前提；本轮移除了恢复标签文件的CPU构造，不是全图未知页初始化。只输出当前选定query/price的硬件present记录；恢复容量显式1024，本例822。CRC用于独立完整性审计，现有trusted label_restore_controller尚不在硬件强制绑定选定源CRC。快照描述身份、持久化floor/认证、任意变价/回绕、owner epoch rearm、真实overflow新分配/回收及综合时序/板卡收益仍缺；额外DDR主口仍为一致共享文件模型。具体下一步见hardware/variants/label_frame_export_v1/NEXT.md。研究继续，goal active。

以下保留历史。

