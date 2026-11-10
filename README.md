# FPGA 加速 FPGA 布局布线：A—G 实验工作区

已为七条路线建立独立研究目录。每个目录包含研究上下文、基线/消融设计、输入输出约定、真实数据待办、平台配置以及可运行的 Python CPU 合成参考。

| 方向 | 目录 | 已实现的小型参考 |
|---|---|---|
| [A · 资源图压缩与直接执行](A_graph_compression/README.md) | `A_graph_compression/` | 两个相邻 tile 共享一个规范节点；同一个局部连接模板展开后加一条例外边，与显式图逐项比较。 |
| [B · 驻留状态与稀疏初始化](B_state_residency/README.md) | `B_state_residency/` | 稠密清零与有限位宽 epoch 标签执行同一组读写；覆盖搜索切换和 epoch 回绕。只统计逻辑操作。 |
| [C · 自适应分区与异构调度](C_partition_scheduling/README.md) | `C_partition_scheduling/` | 在两个抽象 worker 上调度带依赖、资源集合和容量约束的任务；输出抽象工作单位的排程。 |
| [D · 事件驱动搜索数据流](D_search_dataflow/README.md) | `D_search_dataflow/` | 在含并行边、不同出度的有向非负图上运行 Dijkstra，保留边 ID 回溯并验证已知最短代价。 |
| [E · 异构约束布局加速](E_placement_acceleration/README.md) | `E_placement_acceleration/` | 对多个位置移动候选检查资源类型、位置占用、区域、固定单元和简单级联关系，并计算加权 HPWL。 |
| [F · 硬件局部布线评估驱动布局反馈](F_routability_feedback/README.md) | `F_routability_feedback/` | 同一局部图上的多个候选查询，共享冻结的外部硬保留节点；区分找到路径、局部无路径和预算耗尽。 |
| [G · 三维跨层资源选择与分层搜索](G_3d_routing/README.md) | `G_3d_routing/` | 两层有向图含两个固定垂直端口，逐个限制端口求局部路径，并与不限制端口的参考路径一起输出。 |

## 使用

进入任一目录：

```bash
cd A_graph_compression
python3 scripts/run.py check
python3 scripts/run.py plan
python3 scripts/run.py smoke
```

批量检查与执行七个参考例：

```bash
python3 scripts/check_all.py
python3 -m unittest discover -s _shared/tests -v
```

下一次在子目录继续工作时，先读该目录的 AGENTS.md、README.md、EXPERIMENTS.md 与 NEXT_STEPS.md。各方向可以独立发展，成熟方法的合理迁移均保留为主贡献候选。

## 当前完成范围

- 七个独立目录与统一检查/计划/样例运行接口。
- 合成样例的参考结果与必要语义检查。
- 真实基线与 FPGA 变体的配置、指标和接入路径，均明确标为待实现。
- 原始 CPU/GPU 参考源码轻量提取与 SHA256 溯源，未展开大运行时包。

当前没有真实基准运行、GPU/FPGA 实现、综合结果或实测加速比。样例输出标记 `synthetic_smoke`，性能字段为空。实验板卡按公平对照优先考虑 U280 DDR/HBM；设备、XRT 与平台包尚未验证。

## 资料与共用设施

- [完整研究分析](FPGA加速FPGA布局布线_论文切入点与迁移方案.html)
- [素材与源码路径登记](_shared/sources.json)
- [公共支撑说明](_shared/README.md)
- [原始 GPU 源码提取记录](_shared/assets/gpu_router_provenance.json)

配置、样例和结果属于各自目录；共用 Python 工具保持轻量。原始参考源码保留为快照，本方向的改写和适配放入各子目录。

## GitHub 工作快照（2026-11-10）

本仓库保存 A—G 路线的源码、脚本、配置、研究文档及选定实验结果。上文“当前完成范围”是工作区最初建立时的说明；各路线的最新进度以其子目录文档、脚本和结果为准，本次上传未重新运行实验。

本地工作区约 682 GiB，本仓库不是完整磁盘备份。保留既有原始/派生数据忽略规则，同时纳入原先忽略的实验结果 JSON；排除构建缓存、工具运行时、生成的二进制与仿真数据、归档文件和超过 50 MiB 的单文件。

- [上传范围统计](upload_manifest/summary.json)
- [已上传文件 SHA-256 清单](upload_manifest/included_sha256.tsv)
- [未上传文件及原因](upload_manifest/omitted_files.tsv)
- [复旦大学 GPU 布线原始 ZIP（已校验的独立私有仓库 Release）](https://github.com/GRYYYYYYY/gpu-fpga-routing-fudan-linzihan/releases/tag/archive-v1)

原始 ZIP 的 SHA-256：`799e7425041db5d5de04e4fd36d88df91f83b5f96a225c303c0b753ff963567d`。需要相应私有仓库权限才能下载。未上传的生成文件和数据仍保存在原工作区。

## GitHub 工作快照（2026-11-10）

本仓库保存 A—G 路线的源码、脚本、配置、研究文档及选定实验结果。上文“当前完成范围”是工作区最初建立时的说明；各路线的最新进度以其子目录文档、脚本和结果为准，本次上传未重新运行实验。

本地工作区约 682 GiB，本仓库不是完整磁盘备份。保留既有原始/派生数据忽略规则，同时纳入原先忽略的实验结果 JSON；排除构建缓存、工具运行时、生成的二进制与仿真数据、归档文件和超过 50 MiB 的单文件。

- [上传范围统计](upload_manifest/summary.json)
- [已上传文件 SHA-256 清单](upload_manifest/included_sha256.tsv)
- [未上传文件及原因](upload_manifest/omitted_files.tsv)
- [复旦大学 GPU 布线原始 ZIP（已校验的独立私有仓库 Release）](https://github.com/GRYYYYYYY/gpu-fpga-routing-fudan-linzihan/releases/tag/archive-v1)

原始 ZIP 的 SHA-256：`799e7425041db5d5de04e4fd36d88df91f83b5f96a225c303c0b753ff963567d`。需要相应私有仓库权限才能下载。未上传的生成文件和数据仍保存在原工作区。
