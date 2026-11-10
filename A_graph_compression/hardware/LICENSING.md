# 当前实验的 Vivado 授权与环境（2026-10-22）

本机 Vivado 2022.2 对 `xcvu13p-fhgb2104-2-e` 的综合报 Common 17-345：找不到 Synthesis/xcvu13p 许可。导出器件图此前成功，不代表具备综合授权。

## 如何获得 VU13P 授权

1. 优先询问学校/课题组/集群管理员是否有支持 Vivado 2022.2 和 Virtex UltraScale+ 的 Enterprise 浮动授权，取得实际的 `端口@许可证服务器`。服务器须能从运行 Vivado 的节点访问。
2. 高校教师可通过 [AMD University Program](https://www.amd.com/en/corporate/university-program.html) 申请供教学与研究团队使用的 Enterprise 授权。AMD 的[许可说明](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html)明确列出这一渠道；以申请结果为准。
3. 登录 [AMD 许可证门户](https://account.amd.com/en/forms/license/license-form.html)，查看账户可用评估或已购授权并生成许可证。当前官方新方案为一次性 60 天评估；2022.2 历史文档写的是 30 天，不能保证当前门户仍提供旧试用项。
4. 购买时明确要求“能运行 Vivado 2022.2，支持 VU13P”。[AMD 购买页](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-buy.html)说明新 PRO/ENTERPRISE/GOLD 支持 2026.1 前版本；新 BASIC/CORE 不提供该向后兼容，已有旧授权需保留。

获得文件后设置 `XILINXD_LICENSE_FILE` 为实际 `.lic` 绝对路径；使用浮动许可时设为管理员给出的 `端口@服务器`。不要根据示例猜端口。固定节点授权绑定到相应 host ID，生成时应确认实际执行节点/服务器。设置后重新启动 Vivado 并跑小型综合验证，不仅检查环境变量是否存在。

## U280 的独立路径

[UG973 2022.2 第 7–8 页](https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_2/ug973-vivado-release-notes-install-license.pdf)说明 Alveo 包含在 ML Standard 中，该版 Standard 不需要工具许可证。本机 `xcu280-fsvh2892-2L-e` 的综合和实现已通过许可检查，日志有 `Got license for feature Implementation and/or device xcu280`。

U280 与 VU13P 的数据、checkpoint、模板与结果必须分开记录。这是官方支持的另一器件流程，不会让 VU13P 综合自动获得授权。当前没有 XRT 可见实卡，也尚未找到 U280 xpfm；能够综合实现不等于已具备实卡测量条件。

## 路由后工具崩溃

U280 初次 MCP 运行与本机 batch 都在 `Routing Is Done` 后崩溃，堆栈经过 `HAPRWebtalkHelper`、`libXil_lmgr11.so`、`udev_enumerate_scan_devices`，最后在系统 `libudev.so.1` 内 `realloc(): invalid old size`。路由算法报告 0 failed nets / 0 overlaps，但当时尚未保存 routed.dcp，不能据此认定完整构建通过。

当前 `config_webtalk -info` 已报告用户和安装侧关闭；不能把再次关闭作为已验证解决方案。正在用仅对本次进程有效的系统 libudev 预加载测试加载顺序兼容性，不修改工具安装或许可证逻辑。该假设来自本地堆栈，尚无匹配的 AMD Answer Record；必须以重跑的完成标记和实际产物确定结果。


后续验证：`LD_PRELOAD=/lib/x86_64-linux-gnu/libudev.so.1` 的同一恢复流程返回 0，生成 routed.dcp、路由状态和时序报告，带 `NETLIST_BASELINE_COMPLETE` 标记。此本地兼容性处理已验证有效；尚不归因到确定的 vendor bug 编号。命令、库哈希、失败堆栈和输出哈希见 `data/netlist/routeracc_cost_u280_20261022_v1/capture.json`。
