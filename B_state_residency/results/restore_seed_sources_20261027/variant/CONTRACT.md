# 原生恢复整记录写的受限baseline跳过

选定restore_seed_bypass_v1，8份隔离生产源。ENABLE_RESTORE_SEED_BYPASS默认0，restore_seed_enable只有在label_restore原生start握手时采样；请求引脚随后撤销不改变本次事务。l_import在WS/WW保持，root还要求ENABLE_BASELINE、recovery-owned和k_labels_valid；manager只在真实IO受理时锁存，并且只准合法写请求跳过probe/seed。读请求带恢复许可、非法flags和原raw-probe写仍拒绝。不是任意host可用的raw写接口。

原生leaf仍先接收完整160bit payload，依次写五字段，全部成功后才增加written；源CRC校验、完整781记录回读、三回执联锁及业务释放前退休均保留。取消/CRC错误不得把部分记录算作成功恢复。当前成功系统测试仅在G4启用，其余G2/G3测试前缀精确不变。

## 完整验证

restore_seed_off_full_v1/pressure_v1在默认关闭下，与fourth_warm_full_v2/pressure_v2的完整native trace、12AXI日志、最终DDR和周期一致。32槽4547230周期、单槽4775002周期。不是形式等价或任意输入证明。

restore_seed_on_full_v1/pressure_v1实际start后撤销外部许可，下游WW真实受理3905次恢复写，逐字段与781个源payload匹配。无恢复阶段baseline miss，native读4687→782、写7810→3905。782次读为原空检查与781次完整回读；绑定、换出、写回和重载数量保持。全部12AXI按事务/字节审计，原owner修复/保存路径和query原CRC/新attempt及CPU重试通过。最终146284032B owner与3MB labels及其他最终输入图像与正确性基线逐字节一致。

| 容量 | 原标签恢复周期 | 优化后 | 少用周期 | 阶段降幅 |
|---|---:|---:|---:|---:|
| 32槽 | 374180 | 285851 | 88329 | 23.6060% |
| 单槽 | 290780 | 202562 | 88218 | 30.3384% |

故障至业务释放分别375301→286972和291900→203682。整例最终周期4459033/4687480。重试及导出阶段因测试台周期性ready/响应时序相位改变，分别多92/666周期，因此整例净减少88197/87522，不能把整例差额等同于标签阶段节省。上述均为同一行为仿真条件下的周期，不是板卡时间或加速比。

四归档均实际恢复重审，audit字节一致。组件证据见restore_seed_components_20261027.json；完整证据见restore_seed_20261027.json。源码冻结后旧候选与审计器不得就地修改。

## 尚未覆盖

完整系统开启优化后的部分写取消/CRC错误与非冷重试尚在独立restore_seed_retry_v1中运行，不能用组件RAM测试代替。没有任意中断/失联AXI、任意变价标签有效性、自然overflow新增回收、持久化认证/floor、综合资源/时序或板卡收益结论。运行时许可属于可信恢复控制面，未新增认证协议。
