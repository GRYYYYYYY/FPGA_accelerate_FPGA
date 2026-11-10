# 累计G1差分的绑定、错误分类与generation回执

cumulative_owner_snapshot为隔离候选，不修改旧writer。一次cold启动内先在安全lease下BIND（op0）design/baseline/source/span/两个不重叠候选bank。真实源AW必须在绑定窗口、64B对齐、INCR/size6/ID0且不跨4KB；单未完成AW/B和脏行扫描有界。外部source_protocol_ok必须来自实际AW/W/B退休监视，不能用B成功替代。任意覆盖损失粘滞到cold reset：绑定前AW、未知/错ID B、重叠/越界/形状错误、脏表溢出或外部协议fault均不可REARM。

已覆盖AW的非OK B另记data_error。op1仅在lease、source_drained、source_healthy、source_protocol_ok且本服务/旧回复退休时清除data_error；不清dirty、不换baseline、不回退generation/checkpoint floor。op2复制累计脏行到已绑定且不是当前authority的bank，generation和checkpoint均须超过保留floor，受理后即占用floor，即使随后失败也不允许同代重放。cold reset会清floor，不是持久化防回退。

原生源R→候选AW/W/B→候选R逐行验证。成功receipt锁存design/baseline/generation/checkpoint/destination；实际回复消费后、仍持lease且健康，只有选定发布描述符逐项匹配才manifest_ready。源AW、B、错误或安全条件消失撤销receipt。命令/held回复占用期间release_blocked；不掩码内存AXI，不伪造完成。

cumulative_owner_unit_v2：Vivado/XSim2022.2行为仿真278检查、46事务；独立字节重放18 R/9 W/9 B，2读错误/1写错误。覆盖两bank、重启保留dirty2→3及floor、错generation/checkpoint/bank/baseline/design、命令后改引脚、回复保持、不可恢复覆盖错误与256拍跨页宽度边界，以及R/B在途取消。两bank仅检查实际复制行和其他字节保留；合成AW/B观察与lease/健康/authority输入来自TB，不是完整G3系统证明。

初始G1 clone/身份仍外部可信，MAX_DIRTY默认64有界，源单未完成写，copy从设备遵守所发单拍AXI协议。没有运行中全图clone/reseed、任意未知从设备协议恢复、认证、综合时序或板卡收益证明。PLAN.md保留最初草案，当前实现状态见本文件和owner_cumulative_system_v1记录。

源冻结results/cumulative_owner_unit_sources_20261027；归档已实际恢复复审，audit字节一致。
