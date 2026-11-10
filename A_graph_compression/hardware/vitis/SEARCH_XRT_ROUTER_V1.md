# 完整搜索核 XRT 路由接入 v1

冻结副本：`data/derived/complete_search_xrt_router_20261024_v1/`。
`router_xrt` 已和本机 XRT 编译、链接；符号检查确认没有链接 `search_kernel_csr/compact` CPU 核。两种真实 AGRAPH01 图描述符通过离线预检。当前没有实际设备运行结果。

`search_xrt_routes_transform.py` 从冻结 CPU 完整路由副本派生新的 binding/adapter/runtime，不修改原实验。宿主侧只保留路径、unknown 和 metadata 输出暂存区；heap、slots、records、keys由后端驻留。每次调用必须经过显式的 `ExchangeScope`，未绑定时抛错。快照构建、协商、动态占用更新及全量结果导出仍在 CPU。

相同接口经真实生产C核后端完成400个随机完整协商问题、4938次搜索，所有中间路径、状态、代价、unknown集合和每轮冲突均与原生参考一致；包含节点/站点历史、站点路径、路由成功与失败。测试保留生产工作区容量、两种图表示及禁止native邻接回退。此证据证明CPU宿主协议和协商接入，不证明板卡速度。

重新准备需新目录：

```bash
python3 scripts/prepare_complete_search_xrt_router.py \
  --output <新的准备目录> --cpu 119
```

上板入口分两步，均要求新输出目录：

```bash
python3 scripts/search_xrt_board_link.py link \
  --xo <已导出的完整搜索核XO> --mode csr \
  --layout hbm_shared --platform <已安装的U280.xpfm> --output <新的链接目录>

python3 scripts/run_complete_search_xrt_router.py \
  --link <上述链接目录> \
  --host-report data/derived/complete_search_xrt_router_20261024_v1/report.json \
  --device <明确的设备编号或BDF> --cpu 119 --output <新的运行目录>
```

mode可为csr/compact，layout可为ddr_shared/hbm_shared/hbm_split。分组HBM是单独拓扑条件。没有默认推测平台或设备。

链接前必须具备原RTL重放及满状态边界RTL的独立通过报告。XO中的全部生产Verilog和ROM `.dat` 必须逐字节匹配所选模式的已审计综合产物；参数XML也要一致。然后记录精确链接命令、输入摘要、日志、退出码和xclbin摘要。运行入口重新核对整条证据链，**不能凭同名XML或mode字符串判定CSR/compact二进制**。

运行前还要求完整CPU真实1062网审计通过。每次硬件运行覆盖同样的两批完整工作量，核对全部结果字段和controller/snapshot/kernel计数、传输完成状态及字节/时间总计。未满足门控会直接报缺失证据，不创建成功结果。27项合成拒绝检查覆盖语义/计数/流量篡改、错误模式、ROM/RTL/ABI变化、未绑定RTL、缺失审计和旧译码器链接证据。

请通过Python入口运行，单独调用底层可执行文件不建立二进制构建来源证据。目前完整搜索核XO导出与实际平台链接均未完成，RTL重放仍在运行；未进行实卡分配/执行。后续仍需物理实现/时序、DDR/HBM完整统计和功耗，且现有站点模型只有14个物理验证实例。
