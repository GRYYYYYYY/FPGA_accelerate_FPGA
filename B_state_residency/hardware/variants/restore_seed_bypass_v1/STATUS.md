# 更新：完整四组成功路径消融已通过

2026-10-27：详见本目录CONTRACT.md及results/restore_seed_20261027.json。原运行中四组已终止、独立审计、归档实际恢复复审通过；180文件源冻结。32槽/单槽标签恢复周期减少23.6060%/30.3384%，不是板卡结论。当前在独立restore_seed_retry_v1继续优化后的完整失败重试，不再改本候选或已冻结审计器。

以下是此前启动时记录。

# 恢复整记录写跳过baseline：候选已实现，完整结果待定

2026-10-27。原PLAN.md是设计依据；当前已经新增build.py、build_tb.py和8份隔离生产源，不再只是设计。尚未替换任何已冻结基线。候选新增默认0的ENABLE_RESTORE_SEED_BYPASS与运行时restore_seed_enable；原生label_restore启动握手锁存许可，WS/WW维持请求来源，实际manager IO受理后锁存。root还要求recovery-owned与k_labels_valid。普通查询、恢复回读、原CRC/五字段写完计数/全量验证和退休逻辑不改；原raw_probe写仍拒绝。

组件结果见results/restore_seed_components_20261027.json：

- restore_seed_leaf_v1：286检查，关闭/开启后反转启动许可引脚、最后记录CRC错误、第一记录第三字段写入且回复延迟4周期时取消。错误状态保持8周期；成功2条全量回读；取消written0/status7，CRC错误written1/status8。此切片后端为RAM模型，每场景使用服务reset，不是完整系统非冷恢复证明。
- restore_seed_manager_full_v1/pressure_v1：各157检查，实际native endpoint、baseline AXI、page AXI；5次字段写无baseline读取/预读；许可在真实IO受理后撤回；读请求带许可、非法flags、raw-probe写三次拒绝，无native事务。随后普通未知记录仍加载原baseline，写回/重载字节完整核对；末尾原生baseline读错误仍封锁。
- 三归档均实际恢复复审，audit字节一致；43文件冻结results/restore_seed_components_sources_20261027。leaf恢复包装器首次误传scripts/前缀，解包已成功但未找到审计脚本；随后直接运行正确审计器，核对原目录audit字节及全部归档member hash，恢复记录明确保留此经过。

完整仿真已编译/展开并启动，报告时仍运行，不能称通过：

```
/tmp/B_state_residency_offer_20261025/restore_seed_off_full_v1
/tmp/B_state_residency_offer_20261025/restore_seed_off_pressure_v1
/tmp/B_state_residency_offer_20261025/restore_seed_on_full_v1
/tmp/B_state_residency_offer_20261025/restore_seed_on_pressure_v1
```

入口scripts/run_restore_seed.py，候选审计器scripts/audit_restore_seed.py。启动命令为python3 scripts/run_restore_seed.py ROOT {full|pressure} {0|1}；已有ROOT禁止重启覆盖。开启模式仅G4恢复启用，并在原生start受理后撤销外部许可，观察实际下游WW受理3905写；此前G2/G3原baseline取消/CRC错误前缀保持原样。进程状态须实时检查，manifest running不能单独证明进程活着。

下一步：先确认四组终态；对default-off核对原native/12AXI/最终DDR/周期全部一致；对on执行独立记录与物理AXI重放，比较781恢复记录、CPU重试和实际baseline/native操作计数及周期。审计器刚编写，尚未运行到终态数据，若暴露测试假设错误要保留原始日志、按实际证据修正。再另建完整系统中途写取消/CRC失败、旧attempt拒绝与新attempt非冷复位重试；不可用当前叶切片代替。之后才归档恢复完整结果、冻结源、释放对应干净缓存。没有综合资源、时序或板卡收益结论。
