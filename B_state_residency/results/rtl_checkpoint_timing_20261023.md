# 索引端点与checkpoint端点内部时序配对结果

两份冻结默认23405-frame DCP完成相同U280、10ns、2线程、Default布局/布线。Vivado2022.2 MCP source退出0，耗时443.055秒，项目已关闭。输入/脚本/约束哈希、全部可路由net、内部max/min路径与timing summary逐项审计通过；审计状态仅evidence_verified。

| 指标 | 索引基线 | checkpoint端点 |
| --- | ---: | ---: |
| 内部建立裕量WNS (ns) | 4.382 | 3.727 |
| 内部保持裕量WHS (ns) | 0.036 | 0.027 |
| 脉宽裕量 (ns) | 4.458 | 4.458 |
| 建立/保持/脉宽失败端点 | 0/0/0 | 0/0/0 |
| 布线后LUT | 5975 | 6497 |
| 寄存器 | 5288 | 5296 |
| BRAM / DSP | 43 / 3 | 43 / 3 |
| 完整可路由net | 10768 | 11343 |
| 路由错误 | 0 | 0 |

checkpoint端点布线后增加522 LUT和8寄存器，BRAM/DSP不变。建立裕量减少0.655ns，仍满足该内部10ns模型；不换算Fmax。基线最差建立路径从work队列read_ptr到page transferred位；checkpoint版最差从owner BRAM到目录rsp_valid。这里只比较一次固定实现，不据此给出平台频率或收益保证。

模型限制：两版各624输入/788输出无delay，日志保留HD.CLK_SRC和HD.PARTPIN_LOCS缺失提示。no_clock和unconstrained_internal_endpoints为0只覆盖内部约束，不能弥补接口/物理时钟缺失。两版methodology均SYNTH-10三项、TIMING-18一千项；DRC均DPIP-2六项、DPOP-3/4各三项及RTSTAT-10一项。没有新增豁免或修改约束。Vivado技能要求2026.1+的JSON接口未使用，采用已验证的2022.2文本命令。

最终证据rtl_checkpoint_timing_20261023/final_manifest.json，SHA256 `77f0e6fa37ce67b45bbaff77a2ca10673a5ff7f85e9db544d15cb98d0d47304e`，completion_audit.json和completion_receipt.json。manifest.json保留启动时配置，终态以final_manifest和收据为准。平台时序闭合与实卡性能字段仍false/null。

完整38查询行为回放继续独立运行，当前第16查询（attempt504884）已通过，含首次真实checkpoint及其后恢复访问；不能把这份时序审计当作剩余查询的功能证明。
