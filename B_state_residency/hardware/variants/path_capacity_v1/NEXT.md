本变体的默认两槽兼容和三槽组件已通过，见results/path_capacity_20261027.json。三槽完整q3实验path_capacity_third_full_v1/pressure_v1也已独立审计、归档实际恢复重审通过，见results/path_capacity_third_20261027.json；114poll/113expand/565candidate/302cost、781标签/393页/全部3MB物理页和12路AXI通过。

完整q3实验的初始G3源是117字镜像：q1/q2有效、第三槽为空。联合发布后，原生lease导出当前路径，保留前78字，只登记CPU实际q3历史路径的第三槽元数据。然后原生ripup把990179/558358/265324 refs2/4/5变成1/3/4，正常query180329以slot2提交后恢复2/4/5；q1/q2持续保存。新cost与CPS1表已独立审计，和q2工作DDR原字节相同，不需要中途换图像。完整117字最终路径与query floor180329会实际导出，但不再做G4共同发布。

q3独立输入位于followup_iter2_third_cost_v1/oracle_v1；114poll/113expand/565candidate/302cost均有独立CPU证据。保守584标签闭包只是oracle审计产物，本实验不将其预加载硬件；继续使用原生按需baseline。

下一优先接q3真实owner-B故障与G3 warm恢复。G3 snapshot为CP19、source5/3/5、781标签、两条有效路径及空第三槽、floor180328；原raw标签CRC与117字path CRC必须来自三槽实际导出（path CRC f4394572）。恢复attempt需>5，query epoch可回绕但price/history内容保持。target reset后恢复全部labels/path/query且真实回执/退休完成才放行，保留q1/q2，重新登记q3历史路径并实际拆线后重试。不得把新三路径最终导出（CRC437e9a9a）冒充此前G3源，也不得直接复用旧78字CRC。

首选在q3提交的第二次owner写（558358）注入B错误。注意journal在旧q3路径拆线时已经有三个键，不能沿用q2的两键假设。若内存agent在错误B前已接受该物理写，预期故障owner refs2/4/4，G3目标为2/4/5，实际修复应给265324补1次INC；该数值须由真实AXI和原生GET确认，不能手填。应检查满overflow池下同net已有owner INC可完成，其他net23916/ref1不变；故障与重试数值分别对照CPU。新的warm TB/runner/auditor放隔离变体，不修改本轮冻结生产源。

若路径扩展导致新失败，保留已归档默认兼容/组件源和audit；新的生产修复另建变体。后续还缺保存第三路径后的G4联合发布/恢复、持久化writer与认证、baseline reseed、实际overflow新增回收和综合板卡验证。
