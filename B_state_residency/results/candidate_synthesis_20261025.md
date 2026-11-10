# 候选链路默认参数联合综合

同一份通过真实CSR功能与故障验证的RTL已完成Vivado2022.2独立综合。顶层candidate_engine，默认32槽/163840帧/18位目录，xcu280-fsvh2892-2L-e。

| 资源 | 数量 |
|---|---:|
| LUT | 31578 |
| FF | 30068 |
| BRAM tile | 375 |
| DSP | 3 |
| CARRY8 | 1029 |
| URAM / latch / combinational loop | 0 / 0 / 0 |

10ns研究时钟下内部max/setup估计裕量3.190ns，内部无未约束端点；仅max分析，hold未评估。4135输入和3473输出无平台delay，HD.CLK_SRC未设，尚未布线，因此不是板上频率或加速证据。最差估计路径为目录lease_phase至扩展器state CE；估计data delay6.706ns，不代表实际布后路径。

源绑定门禁、完整日志/工具收据、检查点与报告见candidate_synthesis_20261025/final_audit.json。综合571.452s、exit0、history125、checksum2327df0f。300s工具交还后持续观察同一进程，未重启。52份综合RTL不含AXI测试模型；对应三组真实功能回归、受控错误测试与实际AXI故障测试同一修订。

下一步实际成本输入生产与提交。原CPU顺序要求写prev后重新获取动态坐标，成本完成后才写lb/upstream/visited，再offer或递归。历史拥塞必须保持设计级持久性；价格表/版本与net参数也需要真实服务。接入契约hardware/CANDIDATE_COST_BINDING.md，源顺序证据candidate_cost_binding_20261025.json。当前综合体尚无cost/Frontier/完整search、回溯提交或板上接口。
