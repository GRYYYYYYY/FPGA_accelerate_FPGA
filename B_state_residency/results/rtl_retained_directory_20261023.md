# 保留数据的目录事务号回收原语

新增独立 `backing_frame_directory_retained`，从冻结索引目录机械生成。只增加内部opcode6：所有租约FREE且fence_retired为真时清tx_used/last_tx；保留allocated、owner/published、索引与epoch。旧模块不改。该接口只能由后续可信顶层调用，不能直接暴露给主机。

独立Vivado 2022.2 XSim行为仿真通过1006条命令，结束124960ns。六个owner超过两桶/单探测预算，覆盖索引溢出回退。40轮把事务号提升到65535，检查旧ID拒绝，回收后ID0可复用，并逐个查询/RESERVE核对frame与published。每个响应均背压3周期，检查稳定性与新命令禁止。INFLIGHT、未退休COMPLETE、失败租约及无fence条件拒绝回收；普通RECYCLE执行6次跨2位epoch回绕，仍清空owner命名空间。opcode7仍BAD。

首次MCP工程启动的编译/展开成功，但Vivado父进程在SimBridge::BoostProcessTransport::launch中经tcmalloc tc_cfree触发SIGABRT，未取得运行结果。原进程PID2985465已终止；崩溃栈与日志保留。未找到直接匹配此栈的官方修复公告。采用相同源码、独立重新编译/展开的XSim批处理后完成；未修改全局库或安装。官方流程参考：[UG900 2022.2仿真脚本](https://docs.amd.com/r/2022.2-English/ug900-vivado-logic-simulation/export_simulation)。

独立runner的三个工具阶段均exit0，但Python后处理误期待1007条而实际为1006，runner退出1。真实序列为6×4 + 40×(9+12+3) + 6×3 + 4 = 1006。原runner与原manifest保留，未调整测试断言或重复运行；`audit_retained_directory.py`核对完整日志、源码快照和机械生成关系后单独写入 `classified_manifest.json`，状态passed_with_wrapper_classification，功能状态passed。原manifest仍显示running是后处理异常的遗留值，应以明确终态分类为准。

证据目录 `results/rtl_retained_directory_20261023/`；classified_manifest SHA256 `bf6ec0fbf3c7912b6fbfdcb73851a8caf69bfd9cae1c0b723422241798069981`。源码/测试/脚本均冻结。

范围限制：只验证目录元数据与有限ID原语。fence_retired仍是可信输入；没有证明原始页数据保持、队列/AXI排空、独占query条件、服务/top串接、域外旧包隔离或综合资源/时序。下一步先跑旧目录完整差分回归及破坏性负例，再接入服务链和端点。完整checkpoint仍未实现。
