最新[Config14元数据服务](../results/metadata_20261024.md)已通过原CPU配置、真实AXI字节、错误边界及零组合环综合；下一步与children及access_owner共用设计状态并串联，尚无完整设备搜索或板上结论。

最新[共享访问与真实owner联接](../results/access_owner_20261024.md)已通过三组真实后端回归、身份/整合故障与完整默认零组合环综合。下一步实际metadata生产和全搜索，尚无板上加速结论。

最新真实占用AXI硬件已通过功能/故障/字节核对及零组合环综合，见[占用AXI报告](../results/owner_axi_20261024.md)。下一步接完整owner身份桥和共享访问模块；尚无整合或板上加速结论。

最新设计占用布局与可回收pool规范已通过原函数/真实全事件/最终字节验证，见[占用存储报告](../results/owner_store_20261024.md)；下一步是实际AXI后端和共享访问身份桥。

最新共享访问模块v3已通过功能、故障、默认冷启动及零组合环综合，见[共享服务报告](../results/access_fabric_20261024.md)。完整CPU的18515060次引用更新独立重放通过，见[占用观测](../results/owner_profile_20261024.md)；下一步是实际owner后端及设计初始化，尚无完整FPGA路由或板上结果。

# 硬件实现起点

最新：[原版/宽codec配对实现](../results/rtl_codec_timing_20261023.md)完成相同10ns约束下的OOC布局布线与审计。最终建立裕量+4.395/+4.280ns、保持裕量+0.036/+0.016ns，两版路由错误为零；内部模型无需为宽版降频。宽版实现后5626 LUT/5184 FF/22 BRAM tile。接口延迟、实际时钟源及平台集成仍缺失，不能解释为实卡频率或加速证明。以下为此前阶段记录。

最新：[周期测量与宽codec实验](../results/rtl_wide_codec_20261023.md)在相同真实小查询下将仿真周期减少21.56%，全部回归/故障对照通过；整顶层5684 LUT、5185寄存器、22 BRAM tile。代价为+383 LUT、+80寄存器、+1.5 BRAM tile；尚待实现时序和实卡验证。

最新：[闭合页槽与AXI状态端点](../results/rtl_memory_endpoint_20261023.md)已通过19个真实小查询的77099条公开命令、6086次完整页传输及边界/故障测试；整体综合5301 LUT、5105寄存器、20.5 BRAM tile。页完成、地址退休和双域回收已由RTL闭合；仍无完整FPGA路由或实卡加速证明。

最新：[可综合记录级后备适配器](../results/rtl_record_backing_20261023.md)已通过1144服务检查、4288记录核验和7项负例，整体综合2078 LUT、3035寄存器、18.5 BRAM tile。记录校验、内存响应与codec提交/中止已由RTL协调；页槽COMPLETE/地址RETIRE/双域fence闭环仍待完成，无板级加速结果。

最新：[页codec与AXI串接验证](../results/rtl_page_codec_20261023.md)已通过独立5645检查、串接910服务检查和6项故障对照；codec综合1 RAMB18E2、965 LUT、1469寄存器。可综合总适配器与页完成/地址回收/fence协调仍待实现，无板级性能结果。

新增[后备地址与AXI服务](../results/rtl_backing_axi_20261023.md)，[接口契约](BACKING_AXI_CONTRACT.md)明确描述符租约、B响应完成和错误burst排空。独立默认23405-frame综合18 BRAM/932 LUT/1416 FF；实际页槽流转换和总顶层fence协调尚未接通，线性目录不作为最终性能结构。

新增[有界队列/fence组合](../results/rtl_queued_endpoint_20261023.md)已通过边界、真实回放和独立顺序值压力测试；[接口](QUEUED_ENDPOINT_CONTRACT.md)不再接受外部任意排空布尔值，但证明范围仅为同钟闭合端点。整体2 RAMB36E2、2708 LUT、1653 FF。实际DMA、后备地址与内存完成绑定仍未实现。

计划模块：BRAM/URAM 活跃状态页、页表、epoch 标记、更新合并/转发及 DDR/HBM 后备存储。

现已有首个页槽RTL `rtl/scratch_frame_store_bram.sv`、自检testbench和独立验证脚本，默认4槽×64节点，通过XSim及U280独立综合，映射2 RAMB36E2、1332 LUT、641 FF。见[验证报告](../results/rtl_scratch_20261023.md)和[接口契约](SCRATCH_FRAME_CONTRACT.md)。在此基础上新增[传输端点控制器](../results/rtl_page_controller_20261023.md)，保护写回/换入租约并管理有限ID，组合综合共2 RAMB36E2、2154 LUT、1605 FF；[接口前提](PAGE_CONTROLLER_CONTRACT.md)中的远端排空和持久完成尚待真实适配器实现。还没有完整DMA、布后时序或板卡产物。原版 `rtl/scratch_frame_store.sv` 仅保留作RAM推断失败对照，不与修正版一同编译。

优先平台计划为 U280，同卡 DDR/HBM 对照。固定 PE 数、片上容量和目标频率，并报告实际实现频率与内存连接。配置见 [platform.json](../configs/platform.json)。实际工具链、XRT 和平台包匹配尚未验证。

执行相关任务时主动选择适用 Ross Skill，先阅读 SKILL.md；进行 HLS 设计时遵守 pragma scope 规则。使用 Vivado MCP 前查询已有会话；默认 2022.2、Tcl 无 GUI。技能若依赖新版本，核实本机支持后采用适用替代方案。

已有 [参数化真实标签流缓存分析](../results/page_cache_20261022.md) 比较64/512/4096节点页和假设1/4/16MiB预算，普通与尾部查询分开。它只是CPU访问流的全相联LRU模型，不是实际片上资源、带宽或加速估计；现有 `src/page_residency.py` 仅实现独立CPU事件规格，页槽LOAD/READ接口现已验证，页写回/换入端点控制已通过RTL验证，实际DMA与远端排空队列仍未实现。

已完成 [实际CPU路由同步页置换先导](../results/resident_pilot_20261022.md)：RAII租约保护表达式内引用，两个设计在固定96KiB页槽载荷下保持同序质量；页表/后备/全局状态另计，单次耗时明显更高。它仍不是异步DMA或硬件实现。
