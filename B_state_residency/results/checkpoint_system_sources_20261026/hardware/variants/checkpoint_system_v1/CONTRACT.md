# 完整层级的 checkpoint 元数据接入（实验变体）

build.py 基于已验证 cold_axi_fixed_v1，在 query_residency_system → search_residency_system → residency_system 显式传递元数据接口。最外层使用双槽 authority 与 checkpoint_publish_barrier，内层使用 checkpoint_stage_v1 的 coordinator/config shadow 模块。原始基线不变。

checkpoint lease 的获取条件沿用真实工作健康/退休状态；联合事务退休判断使用物理退休、route retired、authority 退休、path/query stream 退休，不能使用准备后有意关闭的 k_permit。事务拥有权保持到完成回复被消费；lease command_busy 包括事务、authority 配置与回复。事务开始不得与 path/query/authority 配置或 host/recovery offer 同拍争用。

prepare_allowed 仅控制新准备请求；publish_permit 使用持有中的 lease 与事务拥有权，不能绑定 prepare_allowed，否则 commit offer 会关闭准备许可并反过来关闭 publish_ready。完成回复保持期间不接受新准备；旧回复仍可退休。路径/查询 checkpoint 请求在元数据事务期间同时屏蔽 VALID 与 READY。

coordinator/config 的专用准备接口仅在事务拥有许可下选择，初始配置与旧 host 回复通过原 fabric。配置准备载荷取自模块当前有效 descriptor，不由测试伪造 provider 回复。authority 准备通过已有配置端口加 jp_authority_stage；读取/配置共用原 AXI。

本轮全系统验证只准备 coordinator/config 两个候选并取消，不准备 authority，不执行共同发布。journal 来自真实查询工作写入、实际故障修复及重试后的六个资源；没有手工 journal stimulus。保持准备回复八周期，检查 lease 不能释放；路径/查询请求持续八周期不能受理；取消后保持完成回复八周期，检查 CP17/journal6/旧 generation 不变；消费完成后继续导出保存路径、查询、配置与 journal。

本变体尚不得视为已验证的完整运行中 checkpoint。共同发布的三方同拍行为此前只在元数据切片验证；完整层级中 authority 准备/成功提交及后续故障 warm 恢复仍待验证。target reset 后保存路径/查询/标签及序号下限的恢复联锁尚未实现。运行中工作 DDR 快照生产、通用多 net/overflow、时序和板卡收益也未完成。manifest_ready 仍为外部输入。
