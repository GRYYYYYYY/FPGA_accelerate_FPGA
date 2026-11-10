# 结果目录

- [BASELINE_REPORT.md](BASELINE_REPORT.md)：2026-10-22 的原始 VPR 独立复现结果与边界。
- `baseline_*/`：带版本与输入哈希的模型基线批次，包含完整命令、原生日志、route、独立审计与 summary；失败尝试也保留。
- `plan_*.json`：可执行模型基线与后续待实施实验表。
- `smoke_*.json`：CPU 合成样例语义检查，性能字段保持空值。

上述均不是 FPGA 实卡性能数据。新运行使用新目录，不覆盖历史结果。
