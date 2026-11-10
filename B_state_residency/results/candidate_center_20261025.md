# 候选处理器与中心距离调用联接

结果：[独立审计](candidate_center_full_20261025/source_bound_audit.json) passed。

| 每组指标 | 32槽 | 单槽压力 |
|---|---:|---:|
| 扩展 |1212|1212|
| 判定/EARLY |3022/60|3022/60|
| 实际中心距离调用 |4233|4233|
| core退休后持续围栏检查 |1211|1211|
| 成本/owner/graph读拍核验 |9067/194/42117|9067/194/42117|
| 仿真cycles |1849331|1743049|

完整设计、owner及cost后备均与原对照一致；54份不变共享源码与6份冻结生成模块、两份collector绑定既有门禁。图文件末尾43次短读零填充逐拍核验；table没有实际读，不主张新增取数覆盖。244.709秒，exit0。

修改为新独立顶层，算术busy纳入统一租约，覆盖core退休后的回复背压、主机修改、查询控制和五组config入口。测试每次主动offer上述入口并保持回复4拍。

算术输入是明确固定fixture `(3,-4,0,0)`，结果7；当前证明实际查询生命周期联接，尚非真实坐标producer或23字成本生产。新联合identity/fault恢复、默认目录、联合综合、完整search和板上验证尚未完成。详见[接口契约](../hardware/variants/candidate_center_v1/CONTRACT.md)。

首轮pilot保留编译失败：query_owned先被隐式声明为wire，再reg声明发生冲突；reg前移后pilot_v2及两组全量通过。未覆盖或改写原/shared基线。
