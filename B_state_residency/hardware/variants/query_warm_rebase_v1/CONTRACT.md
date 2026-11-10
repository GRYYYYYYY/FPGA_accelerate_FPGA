# 原始查询镜像到新恢复上下文的 ledger 转换

build.py 从 checkpoint_commit_v6 的原生 query_lifecycle 生成变体，默认 ENABLE_REBASE=0。未改公共源码或已归档基线。

原有 CP 镜像仍为10个32bit字。启用 ENABLE_REBASE=1 且 cp_rebase=1 时，必须为 restore、持有 cp_rebase_permit、非零 source_version 严格低于当前 active_version，源/目标 price 分别与各自 version 低4bit一致。选定 source_version/query/price 在请求握手时锁存；design/generation 仍要求与当前活动绑定一致。source 元数据和 permit 必须由后续恢复管理员根据选定 bundle 提供，不能直接接任意 host 完成位。

输入40B完全不改写，原始头、源上下文、边界、完整性、原始 CRC 和序号下限仍逐项验证。仅通过原生 CP_CHECK 的单拍 ledger 发布，把 last_version/query/price 绑定到请求时捕获的新活动上下文，保留 source sequence_seen/last_sequence。已有更高序号不能被降低，不能清除已有 sequence_seen。输入镜像不因转换而修改 CRC；后续导出才生成新上下文镜像和新 CRC。

cp_rebase_permit 在 CP_CHECK 发布前丢失或原生 abort、backend fault、active context 漂移时，取消导入，不能暴露半包 ledger。CP_DONE 后的上层 abort、回复退休和全系统放行资格仍需父恢复 gate 负责，不能将本组件成功等同全系统完成。

使用真实 G2/CP18 bundle/query.bin（version4/query2/price4/seq1），新活动上下文 version5/query3/price5。119 次检查、12 个事务：无许可、普通导入上下文不匹配、错误 CRC、错误 generation、错误 source 上下文、部分5字撤销许可、完整10字后发布前撤销许可均拒绝；正确原始镜像转换成功，导出新上下文镜像；seq1 重放及清除序号下限被拒绝，source_version 不小于目标被拒绝；复位后9字 abort 不发布。独立 oracle 重放 S/W/P/Z/R/M/Q 原生事件、原字节 CRC、导出字节和 ledger 状态。

默认关闭时新增输入可以不连接，常量 ENABLE_REBASE=0 保持 cp_rebasing=0，原有上下文判断/状态时序不变；另运行完整32槽/单槽共同发布、新槽GET和q2回归，逐字节比较所有AXI、DDR、原生协议、directory与最终周期。

尚未把 ENABLE_REBASE=1 接入完整系统。cp_rebase_permit/source descriptor 此处由 TB 给出，不是持久化授权/认证证明。转换仅涉及查询 ledger，不使旧距离标签在新价格下自动有效；原生标签恢复与价格一致性仍需独立完成。

下一步接入 recovery fence 管理员与 label/path/query 原生回执联合 gate：label 回复即使已消费也要保留成功回执，path/query 部分导入不能开放业务；不要求普通 checkpoint lease 在 k_permit 关闭时获取自身许可。所有新保存状态完成并消费恢复回复后才能放行工作。随后执行完整换代后 q2 owner 写故障、G2原生GET修复、恢复q1保存路径/查询/标签和新上下文oracle重试。warm恢复、通用多net/overflow、运行中快照生产、综合/时序/板卡仍未完成。
