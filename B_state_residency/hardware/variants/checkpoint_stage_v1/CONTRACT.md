# Checkpoint 元数据联合发布契约

本变体由 build.py 从 cold_axi_fixed_v1 生成 coordinator/config restore 修改；新增 checkpoint_publish_barrier。尚未接入完整查询顶层。

初始配置后，旧的非 staged 覆盖请求被拒绝。准备必须持有许可：coordinator 检查设计、checkpoint 递增和当前 version/query/price；config restore 要求与当前有效 descriptor 完全一致。准备回复未消费时不暴露 prepared。准备不修改活动 checkpoint、有效配置、journal 或恢复 attempt floor。

barrier 在真实 checkpoint_lease_guard 持有期间记录基线，验证三方准备身份、上下文、退休状态及 manifest_ready。三个 publish_valid 在同一握手沿产生，authority 切换，coordinator 更新保存 checkpoint 并清 journal，config restore 更新保存 descriptor。下一拍验证活动元数据，再保持完成回复；消费完成之前不能释放 lease。任何基线漂移或发布后验证失败进入隔离，不能静默继续。

错配/显式取消清理候选槽，保留活动状态。部分候选被 abort 清除后仍可取消其余槽。config restore 的空闲 abort 不一定产生 fault，因此 prepared/publish 资格直接屏蔽 abort。发布不降低 attempt floor；本轮同版本恢复请求被原生 coordinator 拒绝。

验证范围：checkpoint_joint_v7，205 次检查，四个事务状态 1/2/2/0，唯一共同发布，5 个原生 GET、8 个真实 AXI 读 beat。六项 journal 由已验证 bundle delta 驱动，不是本轮工作 owner 写入；无 route engine，route_retired 固定 1。manifest_ready 为测试输入，bundle 由主机独立校验。旧 GET 回复保持、配置回复保持和完成回复保持均阻止提前推进。

尚未验证完整路由系统的配置回调、恢复执行、path/query/label 联合保存恢复、运行中工作 DDR 快照生产、多 net/overflow、持久化原子发布、综合、时序或板卡性能。不能将本结果解释为完整 checkpoint 或加速实测。
