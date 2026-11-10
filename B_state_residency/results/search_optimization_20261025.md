# 自主搜索接口资源对照（2026-10-25）

本轮在上一自主搜索基线上隔离两项接口改写，旧版与全部结果保留。搜索FSM、生产顶层和真实测试台保持，唯一生产文件差异是`search_host_fence.sv`。每个真实版本有120个源文件（含TB）与上一基线逐SHA相同。

| 完整U280 OOC | LUT | FF | BRAM Tile | DSP |
| --- | ---: | ---: | ---: | ---: |
| 上一动态选择v1 | 99477 | 61700 | 160.5 | 23 |
| 仅回复静态切片v2 | 99477 | 61700 | 160.5 | 23 |
| 四路搜索请求注入v3 | 86129 | 61699 | 160.5 | 23 |

v2资源完全不变，否定“单靠改写回复动态切片即可解决开销”的假设。v3相比v1减少13348 LUT（13.418%）；与搜索加入前服务顶层79811 LUT相比差值为+6318。下一实验选用`search_sparse_v3`。所有版本默认32槽/16384帧，Vivado2022.2，诊断关闭；零URAM/latch/blackbox/file-agent实例。层次优化会移动逻辑，不能用层次归属直接代替孤立控制器成本；面积下降不代表Fmax或板卡加速。

v2只将16路ready/reply-valid/256-bit回复选择改成常量case，全部输入输出协议保持。v3进一步按现有FSM实际发出的6/8/11/12四类lane，限制私有搜索请求注入；其余12路在搜索占有时VALID/回复READY始终0，其无效payload不再选择搜索广播数据。主机侧16路服务全部保留，开放时原样传递；私有搜索若请求其余lane则READY=0且不发事务。未来FSM若新增服务，需要同时扩展这一集合并回归，不能将v3当作通用16路搜索器。

## 行为证据

- 两变体各20组合模型场景通过，包含整查询host/route竞争、取消时保持已发请求、恢复意图延迟交接。
- v2并行新旧比较69632组：16路×4096回复单比特模式，再每路256组控制门组合，比较所有输出。
- v3并行比较17420组：4路×4096回复位、每路256控制组合，比较全部控制输出与所有VALID载荷；另外12组非法私有lane拒绝。无效payload按协议不比较。这些是仿真覆盖，不是任意X/Z输入的形式等价证明。
- 两变体分别32槽/单槽共4次真实执行，各包含双查询和四次commit/ripup。与独立CPU/状态/协议审计的v1相比，逐cycle完整轨迹、七AXI日志、四最终图像均逐字节一致。周期仍682354/745363，无新增吞吐收益声明。
- 每次执行116POLL/114expand/447判定/293cost-OFFER/879标签ACK，两个共享节点refs1→2→1→0、按net占用1→1→1→0保持；table AXI仍闲置。

`search_static_v2/CONTRACT.md`和`search_sparse_v3/CONTRACT.md`说明约束。入口为`run_search_static_join.py`或`run_search_sparse_join.py`，原`run_search_scheduler_join.py`仍指向旧基线。综合使用`prepare_search_scheduler_synth.py RESULT JOIN_RESULT`冻结相应源，原生Vivado MCP source执行，不因观察300秒超时而重启。

八结果均已归档，实际移开原件、解压、逐文件验证并重新独立审计，audit字节相同；收据`search_optimization_restore_20261025.json`。129文件源闭包位于`search_optimization_sources_20261025`，负结果v2完整保留。临时综合会话均完成并关闭，监督记录`search_optimization_supervision_20261025.json`。

## 下一研究步骤

将query准备和search→commit编排迁入设备侧，并补真实search错误与非空目标CLEAR、完整checkpoint。已核对原CPU `push/prepareRouteConnection/clear targets`及q1-final→q2-prepared328条标签：现有5次写分别清旧target、置新target、归零source的lb/upstream、更新source visited；仅3个值实际改变，另两次归零仍是任意未来source所需语义，不能因为当前值为0就删去。详见`search_prepare_analysis_20261025.json`，它是后续实现依据，不是已完成硬件prepare的证据。

初始CPU已知328标签/120页、外部authority/snapshot、仅route-owner journal、完整warm/frontier/path/created-cache、unknown-page、价格/epoch回绕、容量与耐掉电/板卡等尚未完成。goal保持active。
