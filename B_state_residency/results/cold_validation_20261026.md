# 普通启动回归与冷恢复顶层综合（2026-10-26）

明确boot_required=0、其余boot输入为0，沿用旧bundle_capture_v3完整TB/CPU/AXI/data/faultcase5，仅换最新cold_axi_abort_v1生产root并加入gate定义。32槽/单槽均完成owner B故障、真实恢复、完整重跑和lease捕获。每例8AXI日志、4完整DDR图像、native全协议与目录记录共14文件逐字节一致，合计28；周期836290/893444及repair1也与旧基线相同。本结论限于该代表fixture，不是任意输入形式等价。

完整U280 OOC：LUT 113043、FF 73882、BRAM 160.5、DSP 23。相对无boot门控的bundle_capture综合增量LUT +7588、FF +2840、BRAM +0、DSP +0。全部runtime descriptor/context输入保留，测试注入默认关，latch/blackbox/file-agent/directory-observer均0。487逻辑端口/62227接口位；端口与源码事实详见JSON。新增19420条gate sp切片无负载告警已逐项分类，对应6条未观察lane、control请求payload与label IO未观察字段；非黑盒/锁存器告警。

综合经真实Vivado2022.2 MCP Tcl完成并关闭专用会话，122生产RTL。未约束时序、未布局布线，不报告Fmax或板卡收益。两归档实际移开原目录后恢复复审，audit字节一致；当前源冻结results/cold_validation_sources_20261026。

下一优先运行中authority换代和统一发布协议，随后通用多net/overflow快照。带约束时序/实现、无复位恢复、持久化下限/认证、未知页/价格/回绕/容量/断电及板卡仍缺。goal active。
