# 真实相邻两查询连续执行

基于iter2_continuous_v1：先执行query180327并保留slot0，原生lease路径导入/旧路径拆线后，直接执行query180328（connection170996/sink67922/net26422/source66893）。storage3/1/3持续不变，无冷复位、label重新导入或工作DDR重装。第二次source/target准备与清理完全由原生query lifecycle完成。

两条独立CPU输入分别预期171/170/849/421与114/113/564/302（poll/expand/candidate/cost）。下一query584条读取闭包为现有822条子集；第二query后验证全部822条，包括其未更新的行。保留第一path槽，第二path由实际previous-pointer回溯提交slot1。第一目标204279与第二目标67922均清理，最终ledger180328，storage3/1/3。

独立审计逐项核对两组P/O/C数值、生命周期回执、原生路径/owner操作、全owner图像及8AXI重放。中间owner准备状态对下一CPU prepared-state全部主记录逐一检查。路径历史元数据仍来自已验证CPU轨迹，通过原生接口导入；不代表运行中路径发现或快照writer。生产RTL与已审计基线相同。

本例尚未G2共同发布，也未下一query故障恢复。行为仿真不代表综合时序或板卡收益。
