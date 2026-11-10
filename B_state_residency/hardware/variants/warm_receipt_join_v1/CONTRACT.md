# Warm 恢复原生回执联合逻辑

warm_restore_receipt_join 在真实恢复 fence 拥有权下，锁存选定 design/generation/checkpoint、目标上下文、snapshot cookie、标签数量及 path/query 原始 CRC。接入本模块的 *_accept 与 *_done 必须来自实际原生请求受理和回复消费，不能由 host 直接提供完成位。

接收 arm 后等待 owner_repaired（coordinator 原生 LABELS 阶段），再核对实际活动上下文与选定绑定。label_allow 仅允许一次标签恢复开始；验证原生成功回复、cookie、written/verified 之后保存标签回执，即使该回复已经消费也不丢失记录。此后 admin_safe 持续支持已受理的路径/查询导入，path_allow/query_allow 各只准入一次。两个原生完成回复均须成功且 CRC 与 arm 锁存的选定 bundle CRC 相符。

admin_safe 不能依赖路径/查询控制器自身的逻辑退休，否则导入一旦忙碌就会撤销自己的 cp_safe。joined 则必须等三项回执齐全、物理 backend_drained 和包含三个恢复控制器的 retired 都成立才输出，并保持 owned 到最终恢复完成回复实际消费。物理退休暂时关闭时 joined 同步屏蔽、保留成功回执；abort 与最终消费同拍仍进入隔离，不清 owned。

错身份、错 cookie、失败回复、源 CRC 不符、上下文漂移、部分流 abort 等进入 HALT，关闭管理员许可并保持拥有权；已经受理的原生错误回复仍须允许退休。当前变体 HALT 只由冷复位清除，没有实现非冷复位重试。上层必须先完成实际物理和逻辑退休再执行冷复位；测试每轮复位前检查 retired。

## 已执行验证

选定 warm_receipt_join_v4：原生 label_restore_controller + route_commit_controller + ENABLE_REBASE=1 query_lifecycle，通过真实 G2/CP18 bundle 的328标签、78字路径及40B查询镜像恢复。标签后端为可变 RAM 模型：实际五字段写入，随后由原生控制器逐行回读比对；不是强制 verified 计数或伪造完成回复。无 DDR/pager/AXI 性能含义。

389 次检查、9 个场景；8轮标签恢复共2624行验证、13120字段写入。成功及最终 abort 场景同时恢复实际路径槽和 version5/query3/price5/seq1 ledger。保持所有原生回复8周期，标签回复先消费并延迟路径/查询；路径39/78、查询5/10保持时不完成；回复已消费后仍持续8周期提供 label start offer，不能重新启动。全部完成后保持8周期、物理退休暂时关闭、abort与完成消费同拍也验证。

其他场景包括原生标签成功但 cookie 不符；原生路径 CRC 失败；查询9/10 abort；错误 checkpoint；上下文漂移；以及格式有效、原生返回成功但与选定 bundle CRC 不符的路径和查询镜像（必须隔离，不能仅信原生status0）。独立 oracle 重放实际写入/读回请求、源CRC与字节，并逐周期重建接收/消费、busy、回执、owned/admin_safe/joined/fault，核对全部状态观察。

## 完整层级接线待办

本轮仍为原生三控制器切片。recovery_owned、owner_repaired 和活动身份/上下文由 TB 提供；没有完整 fence/coordinator、工作 owner AXI 修复或 q2 搜索重试。不得将本结果解释为完整 warm 故障恢复，亦不证明跨价格距离标签有效。

现有 residency_system 中 `lr_start_valid=k_labels_valid`、`lr_rsp_ready=!k_labels_valid`。完整接入时必须在 warm 模式用 label_allow 封锁重复开始，并让原生标签回复独立消费，再以 joined 替代单独 `lr_rsp_valid` 的 coordinator labels_done。沿用旧自动 ready 会形成“等联合完成才消费标签、等消费标签才联合完成”的死锁。

arm 应观察原生 backend recover 握手，并使用该次选定快照与恢复上下文；不能把早期 host offer 当作 owner_repaired。用于 joined 的 retired 不得包含正等待 joined 回调的 coordinator busy 或 recovery fence owned，否则同样死锁。它应包含恢复控制器、相关回复与实际后端退休。

路径/查询入口通过实际 recovery fence 管理员资格接入，不得伪造普通 pc_owned 或等待 k_permit 打开才取得恢复权限。query_lifecycle 的 cp_rebase_permit 接 admin_safe，source 上下文/原CRC绑定选定manifest；READY/VALID的新准入可关闭，已受理回复退休不能随之关闭。最终 completion_consumed 绑定真实恢复回复消费。

下一优先完整换代后 q2 owner 写故障，从 G2 原生GET修复，恢复 q1 保存路径/查询/标签和下限，再通过适用新上下文的CPU oracle重试。运行中快照、多net/overflow、持久化认证、综合时序及板卡仍未完成。
