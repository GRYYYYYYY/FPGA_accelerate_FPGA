# FPGA 布局布线实验工作区

## 用户研究意图

- A—G 是独立研究路线；先阅读当前子目录说明，保留各自基线、配置和结果。
- 吸纳其他场景的成熟方法以降低实现风险。不能仅因“压缩、驻留、调度、稀疏初始化”等概念已存在就排除创新，也不能未经最近邻比较和实验宣称新颖。
- 已有授权内自主推进。文档中的阶段、检查与待确定项不是新的审批流程。
- 当前工作区只有合成 CPU 参考与研究脚手架。真实数据、GPU/FPGA 后端、综合/实卡性能均需实际接入验证。禁止将 toy 计数、排程估计或空性能值当作实测。
- 原始论文/HTML/ZIP 和参考源码保留原状。方案改写优先放入对应目录，共享工具修改后验证受影响方案。

## FPGA / AMD 工具规则

- 执行 FPGA、RTL/HDL、Vivado、Vitis/HLS 任务时主动判断是否适合 AMD Ross Skills 与 vivado-mcp；使用前阅读对应 SKILL.md。
- 查询实时工程/器件状态、打开工程或 DCP、执行 Tcl、仿真/综合/实现或生成报告时优先考虑 vivado-mcp；先查询现有会话，按需复用或创建，默认无 GUI Tcl。
- 纯代码阅读、算法、已有报告分析与文稿工作无需启动 Vivado。
- 默认 Vivado 2022.2：`/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado`。核实新版本功能支持，采用适用替代方案并说明限制。
- MCP 不可用或失败时说明实际情况，判断是否通过本机 Tcl/现有脚本继续。
- Ross/MCP 配置位于 `/inspire/hdd/global_user/guoruiyuan-253208540291/codex/home`。

## 验证入口

- 单目录：`python3 scripts/run.py check`、`plan`、`smoke`。
- 工作区：`python3 scripts/check_all.py`。
- 共享语义检查：`python3 -m unittest discover -s _shared/tests -v`。
