# 排除判断标签读取适配器（2026-10-24）

最终采用 `hardware/variants/exclusion_label_v2`。它将逻辑节点请求转换成带查询、价格和页绑定校验的原生 READ，并返回原始 prev/visited 值、边编号和阶段。已连接冻结的 sparse_records 原生状态端点 RTL 通过 XSim；尚未连接 HLS 标量调用收集器，也没有实现页解析/自动换页或完整搜索。

## 结果与证据

| 项目 | 结果 |
|---|---|
| 全槽位读取矩阵 | 32槽×8偏移×4阶段＝1024项通过 |
| 生产32位事务编号测试 | 2250项检查，1049次原生READ，11735个阻塞周期 |
| 解析器身份检查 | token/边编号/phase/page/query/price六项错配均拒绝；含同边同phase旧token |
| 服务状态错误 | 解析器及原生各15种非零状态，共30项，均不作为成功标签回复 |
| 故障/重复回复 | 8种场景通过，故障锁存阻止继续工作 |
| 3位真实事务编号耗尽 | 7次合法请求后第8次拒绝，非法请求仍正确分类，共9项检查 |
| Vivado 2022.2 OOC综合 | 163 CLB LUT、191 FF、11 CARRY8；BRAM/URAM/DSP/latch均0 |

仿真证据：`results/exclusion_label_adapter_v2_20261024`，独立 `scripts/audit_exclusion_label_adapter.py` passed；manifest SHA256 `1e1633145f120eb67654de8bf355c65f99cf42312a20b513d6a788633d6ba903`。矩阵包括最大可表示节点0xffffff、空记录、显式prev=-1、高位visited、其他字段隔离；实际端点还验证旧binding、错slot/page/query/price、等待解析期间换绑、切换查询后的旧读拒绝。

综合证据：`results/exclusion_label_adapter_v2_synthesis_20261024`，`scripts/audit_exclusion_label_synthesis.py` passed；38.094秒、exit0、checksum5684f693。163是report_utilization的CLB LUT数（已考虑LUT合并），原始LUT primitive为171，不能混为一数。203条warning均逐条分类：常量READ输出、未读取的payload其他字段、未达到并行综合规模；零critical warning/错误。已绑定DCP、源码、时钟约束、报告及实际MCP返回收据。未布线，不能声称该适配器的物理时序通过。

## 保留的失败与修正

v1 首轮矩阵通过，保存在 `results/exclusion_label_adapter_20261024`。增强测试在462741ns复现：成功回复尚待接收时同拍出现服务故障，寄存器fault要下一拍才能反映，接收方可能在当前拍接受成功。负例在 `results/exclusion_label_samecycle_negative_20261024`；编译/展开成功，仿真明确Fatal，属于设计问题。

v2使fault组合输出当前故障并由stopped寄存器锁存；已经提供的回复字段不改动，接收方必须同时检查fault。与负例使用完全相同的增强测试台和后端RTL，只有适配器RTL不同，最终通过。原v1和失败证据保持不变，不以初轮通过掩盖增强测试失败。

## 语义与下一步

三个编号域分离：边generation32识别排除上下文，内部token32识别每次解析事务，binding generation16识别页绑定。编号耗尽不回绕；node先验证小于2^24，再拆page21+offset3。空标签返回原始0，不改成-1；present也不充当设计级created。

本次页映射由测试代理提供，目录32帧，record epoch16、binding16；无AXI活动。不是自动分页、满容量后备目录或HLS—端点整链路证明。服务故障会中止未接收请求，冷复位需外层排空旧消息；不得单独复位适配器后复用旧服务回复。成功状态与fault必须共同控制是否提交HLS RESPONSE。

下一步加入HLS ap_done/各ap_vld的输出收集与调用调度，保持单调用归属，再连接页解析器/租约管理。完整搜索还需getChildren首次过滤缓存、created/deadEnd副作用、价格/占用与回溯提交的统一所有权。既有全38状态端点回放9.5213%的时间降低仍是该回放实验结论，本轮未新增完整路由或板上加速数据。
