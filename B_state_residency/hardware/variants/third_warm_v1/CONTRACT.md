# 第三条查询的G3恢复候选

本候选只改变TB接线、激励和观察，生产RTL沿用已冻结path_capacity_third_full_v1/pressure_v1，默认两槽和正常三槽结果不修改。运行结果以各case manifest、完整transcript及独立audit为准，文件生成或编译成功不代表恢复通过。

前置流程是原真实q1/q2执行、G2发布、q2写故障、baseline在途取消与非冷重试，再真实G3/CP19联合发布。G3恢复源是5/3/5上下文、floor180328、781标签和117字路径（q1/q2有效、第三槽空），不是q3最终三路径图像。记录保存自原生导出，label流来自本轮runtime_g3_labels.txt；CRC直接取原生回执并由审计独立计算。

登记q3历史路径不增加owner引用；原生拆线产生990179、558358、265324三个journal键，refs2/4/5降至1/3/4。query180329完成113次展开后，在第二个提交节点558358的物理写B注入SLVERR。内存agent正常接受此前AW/W，只改变B响应；期望工作refs2/4/4，失败回复status7/detail5/committed0/acked1。所有数值须以真实AXI和原生响应确认。

随后attempt6/query0/price6从G3 authority两轮校验三个键，期望仅给265324执行一次INC至5，其他owner不变。target reset后，原生标签恢复须实际写入且回读781条，路径和query须消费原117/10字及CRC，并将query ledger转到6/0/6且保留floor180328。三回执齐全且服务退休、成功回复消费后才能放行业务。无外部cold reset或DDR图像重装。

恢复后再次登记q3历史元数据、实际拆线并重试同一sequence180329；失败前和重试搜索分别匹配独立CPU114poll/113expand/565candidate/302cost。最终三路径位图7、query floor180329、journal3；全部owner应等于G3完整146284032B，标签全部物理页应等于CPU最终标签。实际验证全部12AXI，其中未新增的三个snapshot writer接口通过与已审计前缀完整字节一致承接。

当前范围是一个确定owner-B错误点、固定价格/history、外部可信初始G1 clones/full baseline与历史路径元数据。不是任意变价、认证持久化floor、运行时完整bundle writer、G4发布/恢复、综合时序或板卡性能证明。
