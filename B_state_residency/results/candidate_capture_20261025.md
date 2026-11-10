# 封存children已联接实际候选/成本/提交/入队链（2026-10-25，优先历史）

hardware/variants/candidate_capture_v1新增candidate_capture_query_core.sv、candidate_capture_engine.sv、TB和derive_core/top.py。core从guarded commit core派生，仅在原expansion_controller与candidate_controller之间插入已验证expansion_capture/children_frames；metadata/access及其实际标签端口保持原接线。真实扩展请求较父请求晚一拍，因此expansion.enable改为已受理operation_pending且配置无错，不能继续使用要求!operation_pending的can_start。外层operation_pending/host/config围栏覆盖整个父操作，底层expander释放后仍不提前放开。capture fault进入组合fault，但联合故障排空仍未证明。

512bit帧保存12个连接/父字段及完整version32/design64/query/price，未缓存动态标签。实际metadata请求必须发生在物理expander完成、seal后，TB检查物理expansion.state=0及捕获适配器state=0；context父/cookie/完整身份与当前controller及外层版本逐项一致。独立auditor逐E/D重建384bit字段并验证保留位零、每帧完成children数以及S→M顺序。原cost/label/OFFER/journal全部保留。derive_core与derive_top均从先前冻结结果在内存重建逐字比较；其余53份旧baseline、62份prior与6份center RTL核验保持。

主结果results/candidate_capture_pilot_20261025（160扩展/169判定/40 cost OFFER）与candidate_capture_full_20261025（完整32槽/单槽）通过。完整每组1216 seal/3066次seal后metadata、702实际geometry+cost23/702成本标签提交/2106有序ACK/701实际成本OFFER/65非空CLEAR，195 seed另计。16146成本输入与3510输出逐bit一致；978条队列命令/回复与原CPU8叉堆逐字段一致，关闭前验证POLL仅4条有效输出，不是真实搜索POLL。最终checkpoint后436条标签/2180字读回一致。13个prior-commit visited skips等压力仍来自前轮脚本输入，不是本轮实现递归的证据。

完整后备标签3145728B及逐字journal核验；graph43888R（49短拍零填充）、owner1620R、cost2107R、tableR0；design145424192B/owner145433472B/cost36812672B后备全部核验。设计级owner/history未随标签清零；所有allowed owner仍为0，不能混称已覆盖非零owner组合。32槽label843R/1362W；单槽具体计数见revision JSON。周期仅仿真收据，不能宣称硬件加速。仍沿用受控4个SLL beginY修改及hasLaguna压力、landmark inactive/crossSLR0和跨扩展复用seq脚本，不是自然全连接搜索。

run_candidate_capture.py为运行入口；最终audit_candidate_capture.py包含seal计数、完整384bit context与reserved检查。先导最初auditor在归档前已通过并冻结为audit_candidate_capture_v1.py，其原SHA与归档保持；后来加强的先导复核单独保存candidate_capture_pilot_stronger_20261025.json，不覆盖归档source_bound_audit。完整组最终主审计使用加强版；completed_full_audit只是运行中中间审计，不作为最终manifest凭据。组合收据results/candidate_capture_revision_20261025.json。

尚未做递归：candidate_controller仍保留单parent pending，action2仍为回调。封存后每项重新实际metadata/access已接通，但没有子树挂起/返回，自然不能声称已验证返回后的标签重读。下一步除保存/恢复controller父context，还必须把当前parent送外层postprev/commit；现有held_parent只在外部expand更新，直接内递归会把根parent写给子帧。连接State的q_meta/q_connection/q_net/q_sink与frame cookie也须分离。详细契约hardware/RECURSIVE_INTEGRATION.md列出身份、立即下降、early传播、reply背压、FULL与联合恢复要求。真实landmark/非零owner/完整搜索回溯与板卡性能仍未完成。

持久化offer_archives_20261025中的pilot/full两个包，成员与copy SHA核验，完整组已实际移开scratch后恢复验证；精确数量与bytes见revision JSON。B同进程跨300s观察交还继续，无超时重启。研究goal继续active。

完整/单槽最终实测仿真计数（仅收据）：

{
  "full": {
    "cycles": 2453955,
    "label_R_beats_checked": 843,
    "label_W_beats_checked": 1362,
    "sealed_frames": 1216,
    "sealed_before_metadata": 3066
  },
  "pressure": {
    "cycles": 2470765,
    "label_R_beats_checked": 3639,
    "label_W_beats_checked": 3714,
    "sealed_frames": 1216,
    "sealed_before_metadata": 3066
  }
}

