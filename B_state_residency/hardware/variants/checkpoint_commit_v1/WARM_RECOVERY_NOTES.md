# 后续 warm 恢复接入约束（源码检查，尚未实现）

完整共同发布与正常 q2 不证明故障后的保存状态恢复。当前 checkpoint_system/commit 继承的实际连接存在以下约束，后续实现应逐项用运行证据验证。

- residency_system 的 `rst=k_cold_rst||k_target_reset` 向上层导出。route_commit_controller 与 query_lifecycle 都会失去其运行状态；新 G2 owner 图像正确仍不足以恢复 q1 保存路径和序号下限。
- coordinator RECONFIG 以后修复 journal owner，再进入 LABELS；当前 `k_labels_done=lr_rsp_valid`，没有路径/查询恢复回执。需要真实回执的联合完成条件，不能仅观察 host 提供的完成位；已经消费的 label 回复也不能因附加路径导入较慢而丢失。
- query_lifecycle `cp_bad` 要求导入 version/query/price 等于当前上下文。已提交 bundle 是 version4/query2/price4，下一次恢复使用新的 attempt context；直接输入原40B query.bin 会失败。需要明确定义、校验和测试受恢复拥有权约束的上下文转换，保持 source generation/checkpoint 身份和原序号下限。不能把修改后的 host 包当作原包 CRC 通过，也不能借此降低 attempt floor。
- 路径78字镜像保存设计身份、槽、net、source/sink、路径节点，没有 query version；仍需绑定选定 bundle/checkpoint，并校验 count/CRC 和完整发布回执，部分前缀不能开放业务。
- 当前 path/query 导入需要 `pc_owned&&pc_safe`；checkpoint lease 的健康条件依赖 `k_permit`，而 coordinator 正在恢复时它关闭。不能直接复用普通 checkpoint 入口等待自己放行。应在实际 recovery fence/退休证明下定义恢复管理员资格，区分新请求准入与已受理回复退休，保持恢复拥有权直至所有保存状态完成。
- 新 ap 检查接口只在普通 checkpoint lease 下工作，不构成上述 recovery 管理员入口。它已经证明新 G2 原生 reader 数据可读；后续仍必须通过 coordinator 的真实恢复 GET 去验证修复过程，不能用只读检查代替。

优先场景：G2/CP18 发布后执行 q2 并注入真实 owner 写回复故障；真实 GET 从 G2 修复 journal（q1资源应保持ref1，新q2资源回到0）；保持工作封锁，恢复 q1 path/query/labels 与下限；完成消费后用适用新上下文的 CPU oracle 重试，并验证共享引用及两次拆线。进一步覆盖部分流、AXI在途取消、回复背压、epoch回绕等。以上是待验证要求，不是已有结果。
