# 路径 checkpoint 的系统接入

隔离变体从 `results/recovery_retry_normal_v1/sources` 派生五个现有组件，并新增 `checkpoint_lease_guard`。路径核心复用已验证的逐对扫描版（`route_checkpoint_unit_v8`）；117个继承RTL/dat保持。原基线入口不变。

新增公共端口分为lease（pc_acquire_valid/ready、pc_owned、pc_release_valid/ready）、路径命令（cp_valid/restore/ready及design/node/net/CRC描述）、32位输入/输出流和完成状态。完整路径格式仍为两个slot共78字/312字节，little-endian CRC32。输出pc_route_retired表示route adapter没有held、owner buffer或核心/回复占用，故障锁存本身不表示在途事务。

取得lease需要配置已激活、工作允许、查询/搜索/路由/恢复均已退休、fence IDLE、物理AXI全排空、内部后台空闲、没有错误及没有已暴露的普通host/query/route/recovery请求。取得前普通业务按原流程进行；调用方须停止发出新普通请求，持续供给普通回复ready，不能靠撤回已发VALID取得lease。已运行查询完成后才可接受等待的lease。

持有期间，最外层query wrapper封锁16个host lane、query命令、route命令和recovery命令；内部CPP命令和流仍可运行。硬件根据实际退休信号产生cp_safe，不再由测试台直接承诺安全。路径命令、流或完成回复尚未退休时不允许释放lease。CPP命令出错后，若物理/逻辑、route及CPP上下文全部退休，允许在普通错误锁存保留时释放lease，交还原有恢复入口；不要求先清除错误。lease单元以受控谓词验证这条错误退出路径，尚未在真实AXI checkpoint持有期注入故障验证完整接管。当前旧恢复authority仍只有q1六行，包含q2新增资源的失败不能据此保证恢复成功。

cp_test_reset是ENABLE_TEST_INJECTION=1时使用的诊断端口，只在lease持有、CPP命令和route上下文空闲时，经寄存器复位路径核心；不复位owner/标签/配置/journal/query控制器。CPP命令输入与注册reset互锁。默认综合参数0关闭诊断复位。测试用它模拟保存路径丢失，不能解释为完整系统reset恢复。

真实试验：q1和q2均由硬件完成prepare/search/commit/目标清理。q2运行期间提出lease请求并保持到取得。RTL从实际保存路径导出图像到测试台外部缓冲；复位路径核心后，先拒绝CRC损坏导入，再导入原RTL图像并重新导出核对，最后释放lease并执行两条路径的实际AXI ripup。两个共享资源refs 2→1→0，四阶段完整owner图像与CPU一致。数据流不是由CPU路径oracle填充，CPU只用于独立核验。

持有期间同时向全部16host、query、route、recovery入口持续提出请求，检查无接受、无AXI访问；journal=10、last_sequence=2、2304位配置描述保持。七条AXI日志和四份完整物理图像与正常基线逐字节一致，其中table在本fixture闲置。两容量均包括坏CRC拒绝、完整重放、输出/完成背压；没有测试任意未知页或更改实际价格。

另有CPP接口全部闲置时的owner真实B错误恢复回归，验证新增接口不影响原有已知q1恢复链；这不等于checkpoint持有期AXI故障已完成验证。

入口：

- `python3 hardware/variants/route_checkpoint_join_v1/build.py`
- `python3 hardware/variants/route_checkpoint_join_v1/build_tb.py`
- `python3 scripts/run_route_checkpoint_join.py NEW_RESULT INPUT_RESULT`
- 加`--normal`关闭checkpoint操作及诊断参数，回归旧正常路径。
- `python3 scripts/audit_route_checkpoint_join.py RESULT`
- `python3 scripts/run_checkpoint_lease_guard.py NEW_RESULT`
- `python3 scripts/audit_checkpoint_lease_guard.py RESULT`
- `python3 hardware/variants/route_checkpoint_join_v1/build_fault_tb.py`
- `python3 scripts/run_route_checkpoint_fault_regression.py NEW_RESULT`
- `python3 scripts/audit_route_checkpoint_fault_regression.py RESULT`

路径流存储仍是外部缓冲，不是自主AXI checkpoint读写引擎。导入的路径必须与可信同一checkpoint的owner图像一致；组件只校验design/范围/格式/CRC，没有完整快照身份、防旧快照重放或拓扑认证。当前所有其他backing保留，last_sequence只是未被路径复位影响，没有被序列化再恢复。完整owner/design/history/labels/directory/config/journal快照、frontier重启语义、未知页/旧prev、价格/epoch回绕、容量和耐掉电仍未完成。没有place/route/Fmax或板卡加速证明。
