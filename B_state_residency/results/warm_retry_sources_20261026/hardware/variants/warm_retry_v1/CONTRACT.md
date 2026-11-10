# Warm取消后非冷复位重试

基于已审计warm_cancel_fixed_v2；隔离变体只改receipt join与query_residency_system命令选择，不改共享基线。生成器build.py保留native coordinator的attempt floor和真实服务退休条件。

## 协议

HALT持续持有owned。只有失败完成真正被消费、随后观察到旧recovery fence释放、再由新fence重新拥有，并且服务/回复退休、物理事务排空、abort已撤销，才开放一次重试受理窗口。新命令与其所有recover字段在真实backend offer上选择，同次受理锁存，不能通过释放owned切换字段。

相同/更低attempt与不同D/G/CP不启动恢复；原生coordinator仍必须返回其校验错误。每次受理都会清除失败消费/fence释放许可，拒绝后必须再次消费真实回复并完成fence交接。有效重试清除旧标签/路径/query回执，使用新目标版本；只有三类新回执与实际退休条件均成立才成功，最终回复消费后才能释放owned。

## 验证层次

- `run_warm_retry_unit.py`：XSim 2022.2行为仿真，35项协议检查。fence、服务和完成均为TB输入，不能据此宣称真实系统恢复成功。
- `run_warm_retry.py --fixed`：真实系统、DDR agent和native coordinator。共享第六owner-B错误产生journal6，G2修复后query9/10取消；消费错误并拒绝attempt5，再以6/query0/price6和新recover cookie重试。要求不冷复位、不重装工作DDR，journal6经两轮G2读取只读复核、corrected0，再恢复328标签、78路径字和10query字，执行q2 CPU数值oracle及两路径拆线。
- `run_warm_retry_normal.py`：健康路径回归，逐字节/周期对照既有shared-last基线。
- `audit_warm_retry*.py`：冻结源哈希、生成器重建、真实回执顺序、所有8条AXI日志和DDR重放、CPU oracle及共享引用检查。

单元35项通过；warm_retry_system_v2（32槽）与warm_retry_pressure_v1（单槽）完整用例均通过源绑定审计、全部8AXI/DDR重放和CPU oracle。warm_retry_normal_v1两容量28个文件及周期逐一与shared-last基线相等。四归档实际恢复重审结论见results/warm_retry_20261026.json。

## 未覆盖

取消点仅为query镜像9/10字，非AXI在途/标签在途/晚成功取消。价格和history内容不变，不能推广为价格变化后的距离有效性。一个net两路径、owner capacity0；运行时快照生成、持久化认证与floor、多net/overflow、综合时序及板卡性能仍需研究。
