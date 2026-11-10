# 成本状态wrapper默认参数联合综合

同一份通过三配置功能回归和8组联合边界的54份RTL完成独立综合：candidate_cost_state_engine，默认32槽/163840帧/18位目录，Vivado2022.2，xcu280-fsvh2892-2L-e。

| 资源 | 实测综合数量 |
|---|---:|
| LUT | 34157 |
| FF | 31557 |
| BRAM tile | 375 |
| DSP | 3 |
| CARRY8 | 1154 |
| URAM / latch / combinational loop | 0 / 0 / 0 |

10ns内部max/setup估计裕量1.641ns，内部无未约束端点。hold未评估、5287输入/4548输出无平台delay、HD.CLK_SRC未设且未布线，不构成板上时序或加速结论。估计最差路径为目录lease_phase至扩展器scan_position CE；data8.255ns含估计net6.671ns，非实际布后路径。

源绑定审计见candidate_cost_synthesis_20261025/final_audit.json；542.149s/exit0/history137/checksum3d8c15c6，完整历史/日志/DCP已保存。300s工具交还后继续观察原进程，未重启。该组合资源是实际综合值，不是独立模块求和。

并行补齐了net-center距离标量的CPU数值门禁：110397向量逐位一致，12054非finite中心拒绝；原表达式与独立binary32阶段重建核验通过。27960真实静态值和37 SLL另一Y样本不等于live route或post-prev服务执行，尚无其HLS/RTL证明。该helper不在上述联合资源内。

下一步HLS验证输入准备，并将TB请求替换为实际成本producer和23字packet，再接exact cost、标签提交、Frontier和完整search。目前没有内部成本生产或板上加速证据。
