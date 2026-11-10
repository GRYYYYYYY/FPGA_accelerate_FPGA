# 查询生命周期与成本状态联接

独立cost_state_store完成同源综合：1916LUT/1338FF/100CARRY8，零RAM/DSP/latch/组合环。10ns内部max/setup估计裕量7.833ns，但IO延迟和时钟位置未绑定、hold未评估、未布线。历史与表数据驻留外部AXI后备；不是板上频率或加速结论。

新wrapper实际连接candidate/pager的query活动状态、32位发布版本和成本请求租约。32槽及单槽各1212扩展/3022判定/60EARLY与CPU一致，每组9067成本AXI读逐笔核验，完整design/owner/cost镜像符合预期。测试确认core最终结果先退休时成本租约继续阻止host工作，以及编辑期间排队OPEN不阻止PUBLISH完成。

| 配置 | 成本请求 | 成本读 | 仿真周期 |
|---|---:|---:|---:|
| 32槽 | 9073 | 9067 | 1463909 |
| 单槽 | 9073 | 9067 | 1358222 |

新wrapper使用16384帧/14位索引/15位hash，尚未验证默认大目录、联合综合或新故障路径。每个候选输出由TB发history(child)、price(ordinal%256)、net请求；还未按occupancy自动选择价格，也未形成成本包或执行算术/提交。表仍是CPU初始factor0.5；空编辑发布只用于query版本生命周期测试，不能解释为真实轮次价格更新。

证据：cost_state_synthesis_20261025/final_audit.json、candidate_cost_state_full_20261025/source_bound_audit.json。契约hardware/CANDIDATE_COST_STATE_CONTRACT.md。后续补联合SET可见性/身份/故障与默认参数验证，再实现内部成本producer、标签提交、Frontier/递归和完整search。独立模块资源不能相加当成测得联合资源。
