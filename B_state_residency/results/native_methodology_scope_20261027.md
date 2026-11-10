# 零组合环后的方法学告警范围核对

分析绑定已实际恢复的native_retirement_synth_v1审计、diagnostic manifest和methodology.rpt SHA，不改RTL、约束或运行任务。

SYNTH-10的23条是Wide multiplier，涉及目录3个cell与两个算术乘法层级各10个cell。报告的分解DSP数量具有重叠，不能逐条相加作为资源占用；实际综合资源仍为23 DSP。

TIMING-16的1000条是Large setup violation；已列路径全部从目录lease_phase_reg[27][1]/C出发，998条目的端点在authority，另两条为ap_owned_reg及as_cfg_lease_reg。所列slack范围为-6.274至-5.707ns，不含最差-7.111ns路径，因此既不是完整端点集合，也不能当作最差路径排名或代表性样本。完整timing summary有47416个失败端点/239469个总端点，TNS -214281.062ns；这些均为布局前估计。

TIMING-18的1000条是Missing input or output delay。check_timing实际统计46802个缺少input delay和10419个缺少output delay的端口；不能把1000条告警当成全部接口。后续需要真实集成边界的约束，不能虚构IO延迟来清告警。

与已有最差71级控制路径分析共同看，后续应先核对目录状态经服务退休/故障/许可到上层控制的组合依赖和状态资格。此处只是诊断导航，并未证明具体RTL约简、流水化方案或板卡收益。保持十源回归基线冻结，任何候选另建变体并验证故障、回复消费和退休边界。
