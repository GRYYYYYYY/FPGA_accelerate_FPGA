# 恢复期间真实 AXI 故障契约

本变体仅增加验证激励，从 `results/search_fault_retire_matrix_v6/sources` 冻结继承生产 RTL 和 AXI 文件内存代理。没有通过层级 force/deposit 伪造服务回复；第二次 SLVERR 由同一个实际内存代理的公开注入端口产生，正常地址/数据/背压逻辑不变。

先执行真实 q1 搜索，在第一次 owner 提交 B 回复注入错误，形成一条有物理副作用、没有成功 ACK 的 journal 项。查询退休后进入已有恢复协议，安装六服务配置、按 authority 修复 owner，再恢复和核验 328 条已知标签。在恢复过程中注入以下第二次错误，各跑32槽与单槽：

1. owner GET 的 R 回复；
2. owner DEC 修复的 B 回复；
3. 标签 snapshot 写入过程中 eviction writeback 的 B 回复；
4. 标签 snapshot CHECKPOINT 刷回的 B 回复；
5. 标签 snapshot 读回核验的 R 回复。

正确结果是**恢复失败但关闭业务入口**，不是恢复成功。必须保持原 journal；不允许自动重新 reset 或清日志。恢复错误完成必须晚于实际 AXI 和回调回复退休，回复背压时保持有效并拒绝16路主机、route和query准入。消费错误回复后，再提出恢复请求仍不得被接受。事务围栏可保持 RECSEND(8) 未接受请求，协调器的 sticky fault 拒绝握手；不能把这一状态误判成再次恢复成功。

测试记录正常错误、第二次错误的具体控制器阶段、全部原生回调、owner 修改、snapshot 流及读回。独立审计要求正常搜索的全部73 POLL/72 expand/271候选/171 cost与CPU一致，完整回放七类 AXI 数据并比对最终二进制图像。owner GET错误时保持那一项实际脏值；DEC B错误即使物理修复已完成，确认计数仍为0且journal不清；标签错误前owner已确认修复1项，但标签恢复失败仍不得放行业务。

`observed` 只表示模拟产生了可分类结果。`fail_closed` 经独立审计后才表示故障处理通过；`stalled`、Fatal或编译失败必须保留，不计通过。验证层首版声明顺序错误保留在 `results/recovery_fault_matrix_v1`。

运行：

```
python3 hardware/variants/recovery_fault_v1/build_tb.py
python3 scripts/run_recovery_fault.py NEW_RESULT
python3 scripts/audit_recovery_fault.py NEW_RESULT
```

仅一次业务故障加一次恢复故障。当前仍是可信 q1 六行 owner authority 和328标签快照，design backing保留；没有自动二次恢复、完整checkpoint、未知页、真实价格变化、wraparound、容量耗尽、耐掉电或板卡性能结论。错误后重启协调器会丢失寄存器journal，仍需外部权威恢复保证；测试不把cold reset当作恢复算法。
