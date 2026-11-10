# G3前的owner writer重arm约束（设计草案，尚未实现/验证）

现有incremental_owner_snapshot把B错误、脏表溢出和丢失AW覆盖合成tracking_fault；q2真实SLVERR后即使工作owner已被原生修复、重试成功，writer仍poison，不能生成下一快照。现有source/destination/span也只在copy命令锁存，没有明确baseline身份/新generation回执。

不要用清tracking_fault或清dirty_count作为修复。清dirty会丢掉相对G1的历史变更，而另一个候选bank仍可能只是一份G1 clone。

下一实现采用有界、累计G1差分的generation推进，区分两种操作：

- G2→G3是输出generation轮转，仍保持同一个可信G1 baseline及累计dirty集合，不冒充baseline重建。
- baseline重建/清脏需要另一个已验证全图clone/reseed协议，当前没有；不能在本实现中偷偷清表。

必要接口和检查：

1. 工作前绑定design/baseline ID/source base/span及两个候选bank，外部只在最初提供准确G1 clones。窗口不可由后续copy参数任意更换；每个真实AW都必须校验覆盖范围。
2. 分离data_error（已记录全部AW、随后B失败）和coverage_error（丢失/重叠观测、未知B、越界、脏表溢出等）。data_error只在真实PC lease、source真实drained/healthy、服务/回复全部退休时显式rearm；coverage_error不能通过此命令清除。dirty集合始终保留。
3. 每次copy绑定checkpoint/generation/destination和source身份；attempt generation floor单调，拒绝重复/旧generation。不得写当前authority正在使用的bank；bank的可信G1来源必须在绑定中明确。
4. 成功回执包含generation/destination/baseline，只有与实际jp候选一致并已消费/退休才允许manifest。源AW会撤销回执。不要仅用旧receipt_valid布尔值放行新的generation。
5. 实验在真实G2 q2故障/原生修复/CRC更高attempt成功重试后，使用实际lease重arm，只清可恢复的B错误；累计脏行仍4，向另一份G1 clone原生copy/readback。旧G2图像逐字节不变，新G3全图逐字节等于当前工作owner，再接原生三方发布/只读GET验证。
6. native标签导出应为实际781条；path保存两槽，query floor180328。若没有自然q3 CPU prepared-state，不要重复已消费q180328冒充连续下一query。

范围仍有MAX_DIRTY容量上限；先证实上述完整G3链，再决定可扩展脏目录和真正baseline epoch/reseed。此文不是RTL或实验通过结论。
