# 内部拥塞与网参数取数实验

[组合门禁](candidate_prefetch_revision_20261025.json) passed：已完成的32槽case、独立单槽压力case及同RTL边界测试分别审计，未把配额中断的原批次改为通过。

| 每组真实回放 | 数量 |
|---|---:|
| 扩展/判定/EARLY |1212/3022/60|
| allowed自动prefetch |785|
| SKIP且不prefetch |2237|
| actual owner/cost/graph读拍核验 |1764/2356/42117|
| 保留center fixture调用/退休后围栏 |4233/1211|

输入地址由硬件生成：真实owner查询→same-net refs与occupancy→合法price索引，再读取history、price和实际net参数。不是测试台按ordinal选择价格。完整design/owner/cost后备及所有原判定一致；本轮不写prev或其他标签。

真实allowed样本均为occupancy0/refs0/index0。非零分支由独立mock覆盖：1024合法组合、12非法索引/矛盾、13故障。需要继续补实际store的非零占用样本，不能把mock结果说成已跑实际拥塞路径。

原full批次完成32槽后在准备pressure时触发磁盘quota。其manifest保持failed，`completed_full_audit.json`只认可已完成case。无损稀疏化本轮bin回收1,553,989,632B，处理前后SHA相同；单独pressure随后112.992秒/exit0通过。详见[prefetch_storage](prefetch_storage_20261025.json)。

保留编译声明冲突、输出交接和边界检查负例。输出交接修正在RTL增加一拍确认，不弱化原稳定性断言。完整语义见[CONTRACT.md](../hardware/variants/candidate_prefetch_v1/CONTRACT.md)。

尚未完成post-prev有效坐标、parent upstream、geometry/connection参数与完整23字生成、内部标签提交/Frontier递归/回溯引用提交、新联合故障恢复、默认目录/新综合或板上测试。center算术仍由明确fixture驱动，仿真cycles不是路由加速证据。
