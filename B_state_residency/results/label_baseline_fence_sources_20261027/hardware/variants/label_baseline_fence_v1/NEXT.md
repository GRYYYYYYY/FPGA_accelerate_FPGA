# 接入777标签G2 warm恢复

1. 新guard/reset域与baseline_retired三层联锁已经通过正常17文件精确回归、SOURCE_CHECK取消与实际AR反例。仍需在完整恢复请求/target-reset场景验证，不能把没有实际恢复请求的PC争用测试说成已恢复成功。
2. 在旧runtime_label_snapshot/label_source_crc完整链使用新七层+三层fence变体、guard实际第九路AR/R和cold-only baseline service。删除全部初始imports及两query中间final host读。q1后实际777条/389页，由PC lease/control(1)/原生扫描和DDR读生成动态源count/CRC，不保留822硬编码。
3. 接原生owner四行增量copy、G2共同发布、source path/query原始导出及floor180327；q2新增4个未知record应真实读baseline。第二owner-B故障，从G2 authority两轮修复并target reset，777条/原始path/query真实恢复后再重试。
4. **generic manager的第一次restore字段写也会探测absent并seed原始基线**。target reset后777条恢复预计新增777次baseline取值；这些读取不属于q2新4记录，审计必须按阶段区分。所有五字段随后被恢复流完整覆写，业务封锁直到验证/回执齐全；不要为了维持旧读取计数跳过正确性或伪造present。
5. 明确baseline immutable源epoch3/1/3与目标attempt4/query2/price4的外部许可和固定内容前提。guard的物理退休与服务归属不能在target reset清零。检查配置/标签恢复等待f_all_drained是否形成回调环；若失败，保留首因证据再修复实际协议。

完成以上再做CRC失败的更高attempt重试、取消点扩展、owner epoch轮转/真实overflow新增回收及综合时序/板卡/认证。
