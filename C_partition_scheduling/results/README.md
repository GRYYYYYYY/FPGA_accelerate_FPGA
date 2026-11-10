# 结果目录

`plan_*.json` 是待实施实验表；`smoke_*.json` 是 CPU 合成样例检查。二者都不是实卡性能数据。

真实实验后另存 run manifest、完整命令、日志与验证报告，明确首次/复用运行和计时范围。不要覆盖旧运行结果。

`trace-smoke_*/` 为原始 C++ 源码在合成 RRT1 上的验证，`execution_kind=synthetic_router_validation`。`profile_*/` 是有溯源真实 RRT1 的 CPU 诊断（`real_cpu_diagnostic`），目前尚无此类真实运行。

[2026-10-22 实验记录](EXPERIMENT_20261022.md) 汇总 33 组验证、潜在跨区标签读写反例和 CPU-only 编译修补。各子目录保留对照/插桩版日志、二进制结果、JSONL 轨迹和校验结果。不可达与容量冲突负例的子运行应为 `failed`；顶层 `passed` 表示正确检出了这些预期失败。
