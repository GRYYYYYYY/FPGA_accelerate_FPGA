# 真实工具适配入口

方案 B 已接入 logicnets_jscl 真实已布局 Interchange：[prepare_real.py](prepare_real.py) 使用 [RealInterchangeExport.java](RealInterchangeExport.java) 和原始导出器生成冻结 RRT1；[build_real_router.py](build_real_router.py) 编译独立原始/计时/访问记录副本；[verify_real.cpp](verify_real.cpp) 在计时外检查最终路径。真实结果见 [报告](../results/real_trace_20261022.md)。运行时来自官方同版本 RapidWright；原包加密 runtime 不是本次生成，也不再是阻塞项。

[build_paged_router.py](build_paged_router.py) 将逐节点 epoch 接入实际 SparseLabels，保留整页清零对照；串行同序与原有 batch 两组分别比较。使用 `--output build/paged_real_v2`，冻结构建已存在时不覆盖。正式结果及适配边界见 [分页报告](../results/paged_real_20261022.md)。

已有 [extract_state.py](extract_state.py) 仍用于从只读 main.cpp 提取状态原语供 CPU 合成微基准使用，与真实完整路由入口分开。

提取时校验固定边界唯一，记录源文件/片段 SHA256 和起始行，生成到本目录 `build/<时间戳>/original_state.inc`。原始函数文本不改动；串行状态上下文、简化占用镜像、合成价格打包以及候选实现位于 `src/state_bench.cpp`。

优先阅读 main.cpp 的 NodeDyn、SparseLabels、gatherShareSet、flushDirtyToGpu 与资源提交函数。

建议保持两个方向的转换可追溯：源工具输入/资源 ID → 本目录任务格式；本目录结果 → 源工具验证。不要从原始 reference 目录直接开展改写。

需要记录数据与工具版本、字段单位、规范节点/边映射、约束覆盖和输出验证方式。接口细节见 [INTERFACES.md](../INTERFACES.md)。
