# 独立驻留服务系统组合

residency_system.sv 将原测试台内的实际硬件组合抽成独立 SystemVerilog 顶层。模块包含 13 个实例：candidate_recursive_engine、route adapter、recovery/config/label 三个控制器、transaction_fence 和七个单挂起 AXI 排空观察器。所有原计算、分页、图/设计/占用/成本/连接状态、heap 和 HLS 子模块均由原 engine 层级实例化。本顶层没有文件 I/O、CPU oracle、initial 激励、时钟发生器或测试台搜索循环。

16 路正常/admin 服务使用原 layout.json 的 packed ABI（每路 request2432、reply256，padding 由调用者置零）；route 是独立 192 位缓存请求。结果流、身份和七组 AXI 从原 engine 导出；恢复 authority 与标签 snapshot 仍由外部生产者提供。interface.json 列出全部 313 个端口的方向与位宽，extraction.json 记录所有实例和内部信号。宽接口适于当前组合验证，后续仍需主机总线适配与外层搜索调度，不能视为完成的板卡包装。

k_cold_rst 复位围栏、日志和恢复控制器，服务复位 rst=k_cold_rst||k_target_reset，仅在协调器取得退休/物理排空所有权后触发 target reset。不得把 target reset 回接独立日志域。cold reset 的调用方须保证接口和外存恢复前提；本模块没有突然掉电保证。

recover_cookie/checkpoint/version/design/query/price 在 recover_valid/ready 握手前必须保持，协调器在握手时捕获。snapshot_design/checkpoint/cookie/count/nodes/probe 同一握手时由顶层寄存，之后允许生产者复用输入线。实际标签恢复的 expected identity/count/probe 来自这些寄存值，不再固定为 logicnets 的 328/9089009/150697；snapshot s_cookie 是逐记录输入，标签服务核对它与捕获的 cookie。标签集合完整性、唯一性和内容仍由可信外部快照协议保证；此处未实现完整快照读取器。

正常/admin payload 与结果归属、route 保存路径、恢复 callback 和七 AXI 排空逻辑沿用已验证组件。实例按显式端口连接，无隐式 `.*`。build.py 对生成器当前支持的端口声明/表达式做严格匹配，未解析字段直接拒绝，不是通用 HDL parser。由原成功 fixture 提取结构并不代替仿真、逐周期比较或综合检查。

ENABLE_TEST_INJECTION 默认0。test_route_abort 和 test_route_version_flip 只在参数为1时接入 route 诊断路径；默认综合中没有逻辑负载。原 abort 端口保持 engine 的现有语义，不是本系统所有控制器统一取消。故障回归显式启用诊断参数，正常基线回归关闭它，真实续接回归保持诊断参数为1但两个输入为0。原 AXI 故障仍由外部存储模型产生。

测试台外部只保留 clocks/reset、typed ABI 驱动/解码、文件 AXI agent、authority/标签流生产和只读层级观测。禁止用层级赋值或 force 修改系统内部。正常/续接 fixture 对照原完整 CPU 审计成功结果；故障 fixture 在恢复握手后的 negedge 反转全部 snapshot 描述输入，恢复必须继续使用原捕获值。没有引入额外等待拍或丢弃原断言以取得一致性。

本模块是完整“现有服务组合”的生产结构顶层，仍没有自主 search/prepare 调度器和完整 checkpoint 生产/存储。journal 只覆盖 route owner 修改；legacy owner/design/cost 写入、warm frontier/path/created-cache 快照、未知页生命周期、实际价格更新/回绕、容量预留和耐掉电尚需完成。不能把组件组合闭环称为全设计 FPGA 布线或板卡加速。
