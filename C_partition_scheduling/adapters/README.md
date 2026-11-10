# 真实工具适配入口

已实现原始 C++ 路由器的 eager RRT1 插桩适配器，构建和语义已在合成图验证。公开 VPR 电路及商业器件 `.phys`/DCP 已定位，但还未接入方案 C，不能直接由本适配器读取；见 [输入核查](../INPUT_SOURCES.md)。原始快照不改动，生成文件和二进制位于 `../build/cpu_trace/`。

## 运行

```bash
python3 scripts/run.py build-router
python3 scripts/run.py trace-smoke
python3 scripts/run.py profile --input /path/design.rrt --provenance /path/design.provenance.json --repetitions 3
```

以上从方案 C 根目录运行，也支持 `run.py` 的绝对路径。真实输入的 provenance 文件必须包含：

```json
{
  "input_sha256": "实际输入文件的SHA256",
  "target_device": "实际器件型号",
  "source_version": "实际导出源版本或源码哈希",
  "exporter": "实际导出工具与配置描述"
}
```

预算默认 `--budget-mode off`；仅设置 `--budget 8000` 不会启用预算。显式 `--budget-mode diagnostic --budget 8000` 才进行 pop 预算搜索及同 CPU 重试；`--budget-mode auto --budget-evidence ...` 则要求匹配当前输入/版本且通过完整收益判据的原始证据，否则保持 0。详见 [预算策略](../BUDGET_POLICY.md)。`--partition-one-worker` 执行原始树/DAG 的单 worker 排序。此预算路径是新增诊断实验，不是 GPU flood 或 `RW_BATCH_BUDGET` 的性能复现。输出包含对应的无预算 CPU 兼容对照，路径输出必须字节一致；不一致保留结果并标为失败。

其他参数：`--timeout 60`（每个子进程秒数）、`--trace-limit 2000`（搜索记录数）、`--footprint-cap 200000`（每个集合项数）、`--output-dir`（必须不存在）。使用限量采样时应查看 coverage，不能以无交集作为独立性证明。失败/超时的日志保留在对应目录。

## 构建和插桩边界

- `instrument_router.py` 固定原始 `main.cpp` 的 SHA256，并核验每个替换锚点唯一。源码变更时必须重新审查，禁止盲目替换哈希。
- 原始源码 CPU-only 构建在 `releaseBulkArrays` 引用了 CUDA-only 成员，故对照和插桩版都加入相同的 `WITH_CUDA` 保护。这是兼容性修补，不宣称编译了逐字不变的原始文件。
- `trace.hpp` / `router_hooks.inc` 记录标签、占用写、候选边、路径、任务 DAG 和最终导出图校验。并未覆盖所有状态字段和内存预取。
- 对照采用 `-O3 -fno-fast-math`、C++17、pthread；无 `-march=native`，不启用 CUDA/JNI。每次运行剔除继承的 `RW_*`/`RWDEV*`/本实验环境变量，再设置明确的单线程配置。
- `rrt_fixture.py` 只生成手写链图和反例，不能登记为真实器件数据。

保留源工具输入/资源 ID → 本目录轨迹的映射；`.result` 仍使用原始协议，可供后续源工具导入。已找到真实 DCP/物理网表；导出器与 runtime/器件库的配套接入及外部合法性验证尚未在方案 C 完成，不再用“输入不存在”描述此状态。

需要记录数据与工具版本、字段单位、规范节点/边映射、约束覆盖和输出验证方式。接口细节见 [INTERFACES.md](../INTERFACES.md)。
