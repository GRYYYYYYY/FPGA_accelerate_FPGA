# 双槽不可变authority：prepare / publish / discard

两个原生checkpoint_authority_reader，各自使用已验证owner_state_store GET codec，共用一个串行只读AXI通路。cfg_stage=0仅首次绑定；cfg_stage=1配置非活动槽。配置处理期间阻止GET，准备回复消费后、尚未publish时仍服务旧槽。cfg包在受理时锁存，后续引脚变化不得影响配置。

调用方提供不可变snapshot；原生配置验证布局，硬件不扫描全表做hash。外部publish_permit须由后续全局事务层产生，本组件测试由TB驱动，尚非真实系统lease/manifest联合授权。

publish_ready要求准备槽健康、两槽busy=0且AXI drained、无GET/config/rearm/discard争用、外部许可。publish握手只在同一时钟翻转活动槽，旧generation随即拒绝。held旧GET/配置回复均阻止publish。discard/abort只清准备资格，不回退活动槽。

身份生命周期独立于configured服务就绪：首次绑定资格使用原生bound_generation==0判断。反例authority_rotate_v5_unfixed在active rearm取消导致configured=0后，允许重新初绑G1并回退已发布G2，没有publish。authority_rotate_v6唯一修复条件改为检查非零bound_generation；旧身份在rearm失败时仍保留，随后成功rearm恢复原G2。

选定v6：224次检查（含重复背压稳定检查）、28 GET、7原生配置和2 rearm、45个64B R beat、两次publish和一次discard。真实SLVERR返回status9，rearm取消返回3，地址布局失败返回2；失败准备不污染活动槽。G1→G2→G4在同一实例内完成。G4复用warm owner图像，仅测试namespace选择，不是新捕获G4完整bundle。

初始表有其他net占用。独立审计证明warm仅相对初始表新增六个资源ref1/occ1，所有其他字节保持；六个目标资源及已有node0/net4754在切换前后实际GET核对。两份完整真实owner图像与allocator、全部实际AR/R地址/数据/status独立重放，未发出写请求。

本轮未接完整查询系统，未实现coordinator journal/config/path/query/label的联合提交及恢复，也没有工作DDR运行中snapshot writer。尤其target reset后必须恢复保存路径等状态再开放工作，不能只更新authority。未综合/约束时序/板卡验证，无持久化anti-replay/认证或通用overflow快照结论。
