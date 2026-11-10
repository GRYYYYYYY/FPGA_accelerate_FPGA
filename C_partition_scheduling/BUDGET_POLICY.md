# 预算保留判据与运行入口

预算默认关闭。只有在相同输入、约束和测量环境下，实测换后端或重新调度节省的时间覆盖全部新增开销，才允许在该范围启用。判定代码为 `src/budget_policy.py`，已接入 `profile`；原始公共源码未修改。

## 三种模式

| 模式 | 行为 |
|---|---|
| `off`（默认） | 有效预算恒为 0，即使指定 `--budget 8000`。正常搜索和足迹诊断仍可运行。 |
| `diagnostic` | 显式运行指定 pop 预算及同 CPU 重试，记录开销和失败；不代表优化已获准。 |
| `auto` | 重新计算原始测量证据的判定并核对执行身份。无证据、证据不适用或不满足收益条件，有效预算为 0。 |

```bash
# 现有合成开销实验：两臂使用同一个二进制，关闭足迹集合收集
python3 scripts/run.py budget-bench --fixture shared_candidate --budget 2 --repetitions 10
python3 scripts/run.py budget-bench --fixture shared_candidate --budget 8 --repetitions 10

# 从刚生成的结果重新计算判定；不把一个 enabled=true 标志当证据
python3 scripts/run.py budget-evaluate --evidence results/<运行目录>/evidence.json

# 已有真实 RRT1 的诊断入口；VPR/BLIF/Interchange 仍需独立适配
python3 scripts/run.py profile --input /path/design.rrt --provenance /path/provenance.json
python3 scripts/run.py profile --input /path/design.rrt --provenance /path/provenance.json --budget-mode diagnostic --budget 8000
python3 scripts/run.py profile --input /path/design.rrt --provenance /path/provenance.json --budget-mode auto --budget 8000 --budget-evidence /path/evidence.json
```

`trace-smoke` 中的预算用例明确使用 `diagnostic`，继续验证退出/重试语义。直接调用 Python `profile()` 也默认关闭预算；继承的 `C_CPU_BUDGET`、RW 配置和输出路径会被清理。

## 计算方式

每臂记录互不重叠的墙钟分量：

```
T完整 = T有效搜索 + T失败/丢弃搜索 + T调度及状态维护 + T传输 + T其他
G = T无预算有效搜索 - T候选有效搜索
H = 候选其余四项之和 - 无预算其余四项之和
净收益 = G - H = T无预算完整 - T候选完整
```

重试保留最终结果所需的搜索记入有效搜索，先前预算耗尽且未复用的搜索记入丢弃搜索；两者都进入完整时间，不能只计重试成功的一次。当前串行计时把搜索之外的路由阶段全部归入“调度及状态维护”，它是一个包含其他路由管理开销的保守分组，不是纯调度器微基准。进程启动、构图、校验、日志/结果输出和父进程等待归入其他项。

当前 CPU 路径没有主机/设备传输，因此明确记录传输为 0；未来后端不能把尚未测量的传输填成 0。并行实现必须提供互斥墙钟区间或关键路径归因，不能把重叠 kernel/DMA 和多个 worker 的忙时直接相加。计时分量不完整、为负、非有限值或总和与完整墙钟不一致时，判定关闭。

保留预算需要同时满足：

1. 是真实电路上的完整运行，关闭足迹集合收集，具有源工具合法性与质量验证。合成结果和仅导出图校验不能用于启用优化。
2. 至少 10 对测量，预先确定重复数，交替执行次序；失败、超时和回退均保留，不允许丢弃慢样本后再判定。
3. 后端或调度策略确有变化，并记录实际发生的切换/重新调度次数。同 CPU、同调度的立即重试不能通过此条件。
4. 平均 `G > 0` 且 `G > H`，完整墙钟平均净改善超过 2%；对每对“改善超过 2%”做单侧精确符号检验，`p <= 0.05`。平局计作未改善。这些是本版保守工程门槛，不是普适收益保证。
5. 输入、二进制、运行器/判定源码、环境、约束、计时范围、两臂配置和预算阈值与当前执行一致；更换输入或后端后重新测量。不会由一个电路的通过自动启用整个基准集。

证据字段包含 `schema_version`、`context`、`measurement_kind`、`accounting`、`timing_includes_all_costs`、`footprint_collection`、`legality_scope`、`planned_pairs`、`complete_campaign`、`pairs`。每对含 `pair_id/order/baseline/candidate`；每臂含上述五个时间分量和 `end_to_end_ms/status/legal/quality_passed/backend_switches/reschedules`。详见运行生成的 `evidence.json`；其失败状态同样是有效诊断证据。数据来源是受信任的测量工具，JSON 不是防篡改认证。

当前只实现同 CPU 重试，没有新的异构后端或预算触发的重新调度，因此本轮判定保持关闭。后续新后端需生成上述测量记录，使用 `evaluate/resolve` 接入同一判据，并补充无预算同后端对照，隔离后端改进和预算机制各自的贡献。

## 验证

`python3 -m unittest discover -s tests -v` 覆盖开销吞没内核收益、异常值、超时/非法结果、样本不完整、同后端伪收益、旧证据/阈值不匹配，以及默认关闭/显式诊断的实际 C++ 路径。测试中的正向时间数值为契约测试数据，不是实测性能证据。

本轮运行与限制见 [预算判据实验记录](results/BUDGET_POLICY_20261022.md)。
