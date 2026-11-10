# 硬件实现起点

计划模块：模板表、实例映射、例外查找、邻接流与译码缓存；先测真实访问轨迹，再接搜索。

压缩加速器尚未实现 RTL/HLS 后端。已有 AGRAPH01 完整二进制与原生参考，见 `../PACKED_FORMAT.md`。另已构建并完成 U280 上 RouterAcc cost_calculator 包装网表的综合/放置/布线，产物在 `../data/netlist/routeracc_cost_u280_20261022_v1/`；这是路由工作负载，不是压缩硬件。

优先平台计划为 U280，同卡 DDR/HBM 对照。固定 PE 数、片上容量和目标频率，并报告实际实现频率与内存连接。配置见 [platform.json](../configs/platform.json)。实际工具链为 2022.2，XRT 2.14.354 枚举 0 卡，尚无 U280 xpfm。VU13P 综合缺许可，但 U280 2022.2 Standard 流程已通过许可检查，见 [LICENSING.md](LICENSING.md)。

执行相关任务时主动选择适用 Ross Skill，先阅读 SKILL.md；进行 HLS 设计时遵守 pragma scope 规则。使用 Vivado MCP 前查询已有会话；默认 2022.2、Tcl 无 GUI。技能若依赖新版本，核实本机支持后采用适用替代方案。
