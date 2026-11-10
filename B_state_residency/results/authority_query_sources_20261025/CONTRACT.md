# 完整查询中的版本化 owner authority

派生自冻结的 `route_checkpoint_fault_regression_v1/sources`，生产变化限于 query/search/residency 三层和新增只读 reader；保留原基线。原 `k_a_*` 数据输入在 query top 改为调试输出，下层原接口由 reader 驱动，测试台不得提供 refs/status。reader 实际读取完整独立 primary/pool/allocator。

初始配置只能在工作引擎/AXI/逻辑退休、无既有 host/query/route/recovery offer、无 checkpoint lease 时被接受。`as_cfg_lease` 保持到配置回复消费，期间挡住 16 host、query、route、recovery；checkpoint acquire 优先于同时出现的 authority bind，避免两者互等。成功绑定后该 reader 生命周期只允许同一描述，不支持生成下一代快照或轮换已绑定快照。调用方必须保证图像真实且不可变。

协调器的 cfg_authoritative 除既有标志外，要求已绑定 design/checkpoint 一致且 generation 非零。请求使用绑定 generation，回复核验实际 generation。业务 journal 按实际 key 查询通用 owner 引擎，不再依赖六行 authority 响应表。现有六行表仅保留为正常 owner probe 的期望值。

快照 reader 和绑定租约由 `k_cold_rst` 复位，不能接工作域 `rst`，后者在目标恢复时会置位。authority AXI 排空、逻辑退休分别进入 f_all_drained/f_backend_idle；协调器 DRAIN 的 normal_retired 还显式要求 authority 退休，必须等待私有 rearm 完整重配后才触发目标复位。authority fault 进入协调器/fence；旧回复消费和真实退休后，已有 k_attempt_reset 发起私有 rearm，旧身份保持。私有重启完成自动消费配置回复，不需新主机绑定。

验证使用真实完整图像与八路文件 AXI agent。业务 owner B SLVERR 后修复实际但未 ACK 的变更，真实恢复/核验 328 标签并完整 CPU 查询重跑；另在 owner 恢复期间注入 snapshot R SLVERR，保留 journal 后更高 query/version 的显式重试。两容量为 32 槽与单槽。不得用 mock labels_done 或 force 代替恢复。

范围限制：只有一个受信任的初始 owner 快照和已知 328 标签流；实际恢复 key 由当前 journal 决定，不能解释为遍历全部节点。设计 backing 保留，路径/labels/价格/历史/目录/配置/journal/序号和 epoch 尚未组成统一持久化 checkpoint；服务绑定 generation 也不是 cold-reset 防回放认证。尚未验证 checkpoint lease 持有期间 AXI 故障接管、快照轮换、未知页/旧 prev/frontier、实际价格变化、回绕/容量极限、耐掉电、时序或板卡加速。
