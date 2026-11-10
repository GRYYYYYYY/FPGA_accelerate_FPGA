# 从状态端点到连接级搜索的控制边界

本说明绑定已验证的串行真实参考 `build/real_trace/trace.cpp`，行号和SHA见 `results/search_control_boundary_20261024/manifest.json`。它是源码依赖审计，不是已实现的搜索内核或新的公开ABI；旧原生接口与两条冻结全量链保持不变。

当前状态组件只实现标签页、后备存储及其生命周期；图搜索仍由CPU参考的 `routeIndirectConnection` 执行。若将逐字段READ/WRITE直接放在外部主机同步链路上，命令量见 `results/native_host_envelope_20261024.md`。把已有离线命令轨迹整体提交不能证明真实搜索也可批处理，因为下一次frontier/标签操作依赖上一条读取结果。

## 源码中的真实依赖链

| 阶段 | 当前参考位置 | 后续连接级切分必须保持 |
| --- | --- | --- |
| 迭代调度/重布线筛选 | `shouldRoute` / `routeIndirectConnections` | 根据设计级拥塞选择连接；不是清空标签后独立无状态任务 |
| 准备 | `prepareRouteConnection`→`ripUp`、`setAllTargets`、`push` | 旧路径资源引用先移除；目标包含altSinks；搜索种子与cost参数一致 |
| 搜索循环 | `routeIndirectConnection`→queue.poll、target检查、`exploreAndExpand` | frontier顺序、visited/prev/upstream/lb/target更新及早终止/预算语义保持 |
| 扩展/评分 | `exploreAndExpand`→getChildren、`evaluateCostAndPush` | 依赖图属性、bbox、SLR/Laguna规则、同net引用计数、设计占用/历史成本、启用时的landmark |
| 回溯 | `saveRouting`沿prev构建rnodes | 标签必须保留到回溯完成，检查最终source；不能提前FINISH丢失prev |
| 提交 | `finishRouteConnection`→`updateUsersAndPresentCongestionCost` | 串行基线在成功搜索后更新设计级引用与占用；deferred commit是另一个受控模式 |
| 退出 | 清target、记录aborted/found、可能的corridor重试 | 预算失败、回退、目标清理与旧路径状态不能被简单“成功ACK”替代 |

同网共享资源依引用关系计数；不同连接共享同一net不授权复用旧距离标签。查询本地epoch与设计级占用/历史成本的生命周期仍分开。

## 可实现切分的必要条件

可以优先评估“主机负责迭代与设计级提交，设备负责一次完整连接搜索/回溯”的切分，但尚未实现：

- 设备需要实际可访问的图/属性与启用的代价数据。`getChildren`在参考中存在lazy/rawFetched路径；预上传图的完整性和node-ID稳定性须由目标数据/模式验证，不能只拷贝某次搜索中已碰到的CSR片段。
- 在搜索开始前发布与本次rip-up一致的占用/同net引用/历史成本视图，并在结果被处理前保持该视图语义。price标识不自动表示所有设计级状态版本。
- 将frontier、扩展、标签访问与必要的目标管理放在设备内；标签组件仍需自动分页、租约退休和有限事务/GEN标识预算管理。现有CHECKPOINT保留标签，但尚未构成自动搜索控制器。
- 回溯和路径输出完成后才允许结束标签生命周期。设计级提交有单一所有者，主机状态与设备视图需明确发布顺序。
- 容量、frontier溢出、预算中止及故障要有明确状态和清理协议。既有端点FAULT冷复位是破坏性重置，不是完整搜索热恢复。

尤其不能在主机已执行rip-up后，无条件重新调用包含rip-up的完整CPU入口并保留旧rnodes，否则可能重复扣减引用；也不能由设备和主机重复commit。应依据现有失败分支对路径/targets的处理，定义一次性准备、提交和回退所有权，再以真实路径结果及占用引用不变量验证。

这不是已有端点上增加一个命令编号就能完成的移植。真实集成验收至少需要：完整连接搜索输出/路径与串行参考核对、跨查询设计级引用与拥塞一致、大小查询和有限标识回收、失败回退，并最终核对全设计结果和收敛。当前19/38查询状态访问回放、内部物理和高地址验证均不能替代这些验收。
