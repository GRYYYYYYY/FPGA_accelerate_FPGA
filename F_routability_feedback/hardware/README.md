# 硬件实现起点

计划模块：复用 D 的搜索引擎，增加共享快照、候选差量页、预算计数和结果归约。

当前没有可综合 RTL/HLS 工程、时序报告或板卡产物。确认真实工作集和软件参考语义后，再在本目录建立 `rtl/` 或 `hls/`、testbench 与 Tcl 配置。

优先平台计划为 U280，同卡 DDR/HBM 对照。固定 PE 数、片上容量和目标频率，并报告实际实现频率与内存连接。配置见 [platform.json](../configs/platform.json)。实际工具链、XRT 和平台包匹配尚未验证。

执行相关任务时主动选择适用 Ross Skill，先阅读 SKILL.md；进行 HLS 设计时遵守 pragma scope 规则。使用 Vivado MCP 前查询已有会话；默认 2022.2、Tcl 无 GUI。技能若依赖新版本，核实本机支持后采用适用替代方案。
