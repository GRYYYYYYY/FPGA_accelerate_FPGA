# 成功回复发布后的abort边界

基于warm_retry_system_v2审计生产RTL，仅改变独立TB。不能把早期取消的J6规则搬到已经成功提交之后，也不能改写背压中的成功回复来模拟取消。

## 场景与契约

先真实完成G2/CP18共享六项修复、328标签/78路径字/10query字恢复和三个回执join，原生coordinator提交current5/3/5、清journal并发布status0成功回复；故障修复计数corrected6。

1. held：成功回复先背压8周期，再置abort并继续背压8周期；VALID、status0、cookie c0010001、corrected6必须稳定，journal仍0。
2. edge：成功回复先背压8周期，再将abort与READY在同一消费边沿置有效；消费的真实回复仍须是原status0/cookie/corrected6。

两种情况下都必须保留warm owned/fault隔离及已提交current5和attempt floor5，不冷复位，不恢复旧journal，不重装工作DDR。abort撤销、旧回复/fence退休后，相同attempt5返回原生status1，严格更高6/query0/price6以新cookie重试。J0由native coordinator跳过owner journal修复，不能伪造两轮GET；全部保存状态仍重新恢复和验证，完整成功消费后再放行q2及两路径拆线。

status0是已经提交的恢复结果，不是对晚到abort的拒绝或取消确认。晚到abort导致隔离，不能据此声称此前的成功被回滚。接口是否需要额外显式的晚到取消状态属于后续设计问题，当前只验证已有回复稳定性和可恢复性。

## 证据

run_warm_late_abort.py支持--late-mode=0/1以及--full-only/--pressure-only。生产源与基线逐文件SHA一致。audit_warm_late_abort.py重建冻结TB，检查两次完整回执、提交/回复/隔离/重试顺序、J0分支无owner/authority访问、全部8AXI和DDR重放、CPU数值oracle、最终标签与共享引用2→1→0。以各source_bound_audit.json及results报告为准。

只覆盖两个确定边沿与一个net两路径/capacity0、固定价格/history内容；不代表任意异步竞态、协议违规、永久超时、持久化floor/认证、运行时快照、多net/overflow、综合时序或板卡验证已经完成。
