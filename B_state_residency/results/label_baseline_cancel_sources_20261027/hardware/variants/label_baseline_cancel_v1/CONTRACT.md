# 777标签恢复中的真实baseline R在途取消通过（2026-10-27）

选定label_baseline_cancel_full_v2/pressure_v2。生产RTL逐文件SHA与前轮777 warm恢复一致，仅增加独立内存agent hold_r及TB/审计；hold只延迟真实R生成，不屏蔽DUT握手。

第21条恢复记录node558372触发真实baseline AR（0xb00110a480），R被保持64周期。期间第九路owned1/physical drained0/retired0，恢复完成和target reset均未出现，业务持续封锁。释放后真实R、baseline前端回执及原生标签操作退休，leaf返回status7/written20/verified0，coordinator status6/J2。20条完整写与第21条部分字段没有回滚；失败回复消费后仍owned/fault。

相同attempt4新cookie原生status1拒绝；attempt5/query3/price5以新cookie非冷复位重试，G2两轮authority和工作owner复核corrected0，无重复DEC。再次完整恢复并回读777条、原CRC b539040c、path78/query10及floor180327后才放行。q2故障前和重试均114poll/113expand/564candidate/302cost，最终sequence180328/store5/3/5，两路径保留。

baseline真实1583读分777/4/21/777/4；16015次native字段写，恢复输入798条/字段写3986。全部11AXI、最终781标签/393页/3MB物理页及146284032B owner独立重放通过。32槽结束2312330周期，单槽2488788周期，仅行为仿真。

早期v1因agent hold错误依赖会被撤销的labels_valid而未保持64周期，属于激励问题；v2锁存cancel_active修正，不是生产RTL缺陷证据。本轮仅覆盖一个确定AR/R取消点，不证明任意取消或永久不响应。固定价格/history，外部可信baseline/G1 clone/描述符、持久化认证、G3 writer rearm与综合板卡收益仍未完成。
