# 777原生流CRC失败后非冷复位重试通过（2026-10-27）

详见results/label_baseline_crc_retry_20261027.json与hardware/variants/label_baseline_crc_retry_v1/CONTRACT.md。选定full_v1/pressure_v1，全部生产RTL/agent逐文件SHA等于label_baseline_warm_full_v3；只增加真实错误/重试激励和独立审计。仍无初始标签imports/中间host final读，源777/389页/CRC b539040c来自原生runtime导出。

q2第二owner-B故障先真实修复两键；attempt4/query2/price4选错源CRC xor1，native label status8/written776/verified0，最后一行未写。coordinator status6/J2保留，776部分写没有回滚；消费失败后owned/fault与业务封锁保持。正确CRC的新cookie c0020000相同attempt4被原生status1拒绝；c0020001的attempt5/query3/price5非冷重试两轮G2/工作owner复核corrected0，无重复DEC。

两次target reset共10样本均baseline retired1/physical1/owned0，两个RAW探测实际absent0；service/guard不随target reset清归属。再次完整写入并实际回读777，原CRC、path78/query10源CRC1d36e333/79283e8e和floor180327不变，真实三回执/退休/最终成功回复消费后才放行。q2随后完整重试匹配原CPU114poll/113expand/564candidate/302cost，最终sequence180328/store5/3/5，两路径共存。q1仍171/170/849/421且原始trace/cycle前缀精确等于前轮正常例。

第九路2338实际R分777/4/776/777/4阶段；23569 native字段写，restore输入1554记录、字段写7765、只在第二次验证777。32槽1503WB/1304RF，单槽2655WB/3638RF；43 authority读beat、13 owner记录写、全部11AXI和最终781标签/393页/全部3MB backing及146284032B owner独立重放。无外部cold reset或working DDR重装，两份归档实际恢复重审audit字节一致；源冻结results/label_baseline_crc_retry_sources_20261027。2563614/2678084结束周期仅行为仿真。

下一优先在实际777恢复过程验证一个baseline AR/R在途取消与非冷重arm边界，然后必须推进G3 owner generation/bank/receipt与B错误rearm。已记录owner_cumulative_rearm_v1/PLAN.md为设计草案，尚未实现：当前tracking_fault混合B错误与覆盖丢失，不能直接清fault/dirty表。G3可先保持G1累计差分；真正baseline epoch/reseed仍缺，不能混称完成。

CRC不是认证，价格/history内容不变；immutable全节点基线、G1 clone和描述符仍外部可信，目录/路径容量有界。新恢复阶段取消、owner epoch/实际overflow新增回收、任意变价、持久化writer/授权/floor、综合时序和板卡收益仍未完成。研究继续，goal active。

