# 实际非零占用成本输入回放

[组合审计](candidate_occupied_revision_20261025.json)通过。真实图上脚本注入8个节点和54条overflow owner，CPU用原incrementUser/原候选判定重新生成对照；全部64份RTL/模型与上一轮相同，测试断言保留。

| 每组指标 | 32槽 | 单槽压力 |
|---|---:|---:|
| 扩展/判定/EARLY |1212/3022/60|1212/3022/60|
| 自动prefetch/非零占用/同网共享 |785/12/6|785/12/6|
| owner/cost/graph读拍逐字核验 |3024/2356/42117|3024/2356/42117|
| 仿真cycles |1780205|1674779|

实际价格索引覆盖0、1、2、3、4、5、15、16、31、32。例如同一节点在同网refs7/occupancy32时读31，换成其他net后读32；不是用分支引用数7去减occupancy。不同history和factor1.25价格值均从真实AXI后备读取，完整design/owner/cost镜像一致。223.235秒/exit0。

非零状态为脚本注入，非自然路由轮次；本轮没有host SET事务。尚无post-prev几何、完整23字成本包、标签提交/Frontier递归或板上加速结论。

首次输入生成因quota截断镜像，CPU虽exit0且旧manifest标passed，完整性检查仍拒绝该目录。有效v2检查两份完整设计镜像及全量向量后通过。原失败数据保留。

有效数据的results路径是临时盘symlink。持久归档在[occupied_archives_20261025](occupied_archives_20261025/durability_audit.json)，共约14.3MB，全部成员和压缩文件哈希通过；pilot已实际解包恢复核验。若tmp消失，运行：

```bash
for index in results/occupied_archives_20261025/candidate_occupied_*.json; do
  python3 scripts/restore_occupied_result.py "$index"
done
```

详细语义见[EXPERIMENT.md](../hardware/variants/candidate_prefetch_occupied_v1/EXPERIMENT.md)。下一步接入prev写确认后的有效坐标和父节点upstream，遵守EARLY先CLEAR的顺序，形成完整成本输入。
