# 完整层级的 G2 warm 故障恢复

本变体从 checkpoint_commit_v6 冻结基线生成 query_residency_system/search_residency_system/residency_system，并复用原生 query ledger 转换模块、双槽 authority 与发布屏障。ENABLE_WARM_RECOVERY 默认0，启用参数及 wm_enable 后才进入新路径。不改公共参考源码。

## 真实握手与管理员资格

transaction_fence 的 recover_ready 等于 backend_recover_valid&&backend_recover_ready，并不存在提前的前端 ready。wm_on 在真实 backend offer（RECSEND）选择本次模式，随后在同一个受理沿锁存恢复上下文和 source/CRC 描述符，同时 arm 联合逻辑与原生 coordinator。请求者必须保持字段至实际 ready。此前“先用前端 ready 锁存、后端再用”的实现已在 warm_system_v1 实例复现 wm_mode0/未arm失败，保留为负例。

arm 来自实际 backend recover 受理，recovery_owned 来自原生 transaction_fence，owner_repaired 来自 coordinator LABELS 阶段。没有伪造 pc_owned；整个 warm 导入期间普通 checkpoint lease 仍为0。wm_owned/admin_safe 提供独立恢复管理员域，路径/查询的新 VALID/READY 受准入限制，已受理导入的 safe 许可不因自身 busy 消失，回复继续原生退休。

## 标签建立目标上下文

标签恢复的原生 control0 自身建立新标签上下文，因此 label_allow 不能在开始前要求目标标签上下文已经存在。新 join 保留全过程 design/generation/checkpoint 检查，但在标签成功回复被消费后才要求实际活动上下文匹配目标。独立 context 切片从 active_version0 经原生 label control 建立5，405检查通过；旧 join 在140ns、check9进入HALT，负例与修复均保存。

warm 模式下 `lr_start_valid=k_labels_valid&&wm_label_allow`，防止持续 LABELS 重新启动；`lr_rsp_ready=wm_owned` 使标签回复先消费并锁存原生成功记录；coordinator labels_done 使用 wm_joined。路径78字和查询40B均成功、原始 CRC 匹配选定快照并退休后才 joined；查询使用原始 version4/query2/price4 镜像和 CRC，在原生控制器中绑定新 attempt version5/query3/price5，保留 seq1 下限。

joined 的 retired 包含恢复控制器和实际回复/后端退休，排除正等待 joined 回调的 coordinator busy/recovery-owned。最终原生恢复回复消费前保留 wm_owned；coordinator permit/fence共同封锁业务。HALT当前要求退休后的冷复位，尚未无复位重试。

## 已执行完整系统验证

warm_system_v2 的32槽与单槽两例：先完成旧故障修复及q1重试，再发布 G2/CP18 并通过原生新槽 GET 检查快照；执行 q2，于首个 owner 写B回复注入真实SLVERR。实际 journal 新增 node1231788/net2717 一项，原生G2两轮GET从新只读窗口返回目标ref0/occ0，工作 owner GET/DEC/GET修复并验证。未直接驱动 journal、owner计数或服务完成回复。

同一真实恢复 fence 下，原生标签模块经实际 DDR/pager 写入与回读328记录，原生路径控制器恢复q1槽，查询控制器完整导入选定G2镜像并转换上下文。标签单独成功、路径/查询回复保持时均不向coordinator报告完成；完整回复保持8周期后消费，才恢复业务。使用现有独立数值CPU oracle 重试q2，43poll/42expand/176candidate/122cost及328最终标签检查通过。原生q1/q2两条路径均可拆除，两共享节点263946/554512引用1→2→1→0。独立审计全部8路AXI和最终DDR、G2修复地址/值、真实标签写入/回读、查询源字节、回执顺序及CPU数值结果；最终其他net状态保留。

价格/history DDR内容始终逐字节不变，只改变 attempt 标签；此条件及CPU数值比对支持本fixture标签恢复，不能据此推断任意真实价格改动后距离仍有效。

warm_system_normal_v2：关闭warm参数，32槽/单槽各14文件（8AXI、4DDR、完整native协议、directory）及最终周期与 checkpoint_commit_v6 逐字节一致。不是形式等价或任意负载证明。

## 仍未完成

本轮只覆盖一个net、两路径、owner capacity0的首个q2 owner-B错误；共享节点故障、多项journal、其他错误点/AXI在途abort、epoch回绕、未知页、通用多net/overflow、非冷复位失败重试仍需扩展。快照来自既有已提交bundle，没有运行中工作DDR生产器或持久化manifest认证/下限证明。没有新综合/实现、时序闭合或板卡加速结论。

下一优先把错误注入移到q2共享资源写回复，使G2恢复目标ref1与旧G1的ref0可区分，验证多项journal与保存q1关系；再恢复流/AXI在途取消和退休后的非冷复位重试。
