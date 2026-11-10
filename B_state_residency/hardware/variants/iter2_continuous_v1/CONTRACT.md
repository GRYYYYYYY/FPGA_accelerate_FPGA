# 真实相邻查询之间的 owner 连续准备

生产RTL沿用 iter2_lifecycle_v5（warm_retry_system_v2 层级及 multi_owner_capacity_fixed_v1 coordinator），只修改独立TB。先原生执行 query180327、验证822标签，保留提交路径slot0。通过实际PC lease导出78字路径镜像，保留slot0原字，将独立原CPU观察到的下一连接旧路径导入slot1。CRC来自实际完整镜像，原生导入成功并释放lease后，执行slot1原生ripup。

历史路径67922→990179→558358→265324→66893，内部三个DEC为990179 refs2→1/occ2、558358 refs4→3/occ2、265324 refs5→4/occ1。不得直接改写owner内存，或以重装下一prepared快照替代连续执行。保留slot0、sequence180327、storage3/1/3。

scripts/audit_iter2_continuous.py 审核第一query数值oracle、全822标签与3MB backing、真实路径导入、全部owner主表对下一CPU prepared快照、overflow保持、六次物理owner记录写及8AXI重放。该步骤只完成owner准备；下一source/target标签准备、query180328搜索、G2共同发布及故障恢复仍须后续实验。历史路径由CPU已观察轨迹提供，不是运行中发现/快照生产器。

运行：scripts/run_iter2_continuous.py ROOT --full-only 或 --pressure-only。每例结束后执行 scripts/audit_iter2_continuous.py ROOT，审计成功后才可归档并恢复重审。行为仿真不得宣称板卡收益。
