# 访问性共享服务实验（2026-10-24）

已连接实际驻留访问性HLS、动态分派、分页标签与图/坐标服务，整个child判定期间持有共享端口独占。接口见 [ACCESS_FABRIC_CONTRACT.md](../hardware/ACCESS_FABRIC_CONTRACT.md)。WILL_OVERUSE/COUNT_USER两个owner端口仍使用明确的占用/引用模型，尚未连接真实设计状态；metadata生产和完整search也未整合。

## 参考与功能

输入 `access_fabric_inputs_20261024`：从冻结原CPU测试环境保留原判定与坐标函数，图属性从64节点合成图或真实9089009节点图读取。合成18³×2=11664组，真实512组；hot复制静态权威数据，原函数与状态机事件/决策对照通过UBSan。把fixture局部prev编号映射到实际图编号，保证硬件前驱读取实际图数据。

v1 `access_fabric_20261024`三组功能及独立审计通过：

| 测试 | child | HLS步 | 动态请求 | native标签读 | 图AXI读 | 表AXI读 | CP |
|---|---:|---:|---:|---:|---:|---:|---:|
| 合成/32槽 | 11664 | 51549 | 39885 | 24690 | 22600 | 4868 | 234 |
| 真实图/32槽 | 512 | 1756 | 1244 | 979 | 424 | 0 | 11 |
| 合成抽样/1槽 | 614 | 2727 | 2113 | 1304 | 1235 | 264 | 13 |

合成11类请求全覆盖，397次SLL坐标标签读取；38次parent.prev及13次前驱tile，保留原顺序。每组都覆盖OPEN/CLOSE、周期性显式CP、内部页替换和响应背压。压力614组从原始用例每19组取一组，未改参考值。真实512组没有SLR请求，不能外推为真实跨SLR路由验证。

独立审计从初始空标签、host写、原图属性和行表重算每个动态值，逐HLS输出、最终决策及所有图/表AXI返回比对；标签AXI逐字节重放并核对最终后备文件。原生READ边界另有完整payload/presence计分板。owner模型使用占用数和同net引用数计算结果，两个端口仍不属于已实现的物理占用服务。

## 故障与冷启动发现

故障首轮和v2在恢复阶段失败：测试将服务上限人为设为256拍，冷目录尚未完成初始化就超时；v2仅增加诊断，确认status5。v3新增监测代码存在变量声明顺序错误，未进入仿真。所有失败源码/日志保留。v4恢复设计原默认上限262144，19故障/19恢复通过，max_service_cycles32753、1445311周期；实际图Rerr1/表Rerr1/标签Rerr2/Berr1。

另外以**完整默认**163840帧、INDEX/HASH18冷启动，两个路径通过，首次服务262129拍。原预算262144只剩15拍余量，故创建 `access_fabric_v2`，唯一设计差异是服务默认预算改为目录深度加262144操作预算。默认524288拍，功能目录294912拍。v1功能与负例保留，不把冷目录初始化等待说成每次connection清零开销。

`access_fabric_v2_20261024`全量重跑及独立审计通过，158.121s。budget_change_audit证明设计仅更改默认服务预算，三组全部结果/周期/图表标签AXI轨迹及最终后备文件与v1逐字节相同。`access_fabric_v2_boundaries_20261024`19故障/19恢复通过，1478082周期；`access_fabric_v2_cold_20261024`两条完整默认容量冷路径通过，262129拍最久正常服务、524541总周期。两项合计52.314s，均有独立源绑定审计。

## 实际综合

v2完整组合 `access_fabric_synthesis_20261024` 的综合进程exit0，但结构门禁**failed**：LUTLP-1和check_timing均发现1条4-LUT组合环。a_busy含fault又门控共享标签响应归属，形成d_fault→a_svc_fault→a_busy反馈。393.9s/history90，完整日志和DCP冻结，negative_audit验证该负例；不得作为通过实现或放宽ALLOW_COMBINATORIAL_LOOPS。

`access_fabric_v3`以握手维护access_pending寄存器，仅改变所有权选择信号。三组全量功能及独立审计通过，ownership_change_audit证明其他设计RTL不变、全部正常结果/周期/内存轨迹与v2相同。v3实际综合及结构门禁已通过。

`access_fabric_v3_boundaries_20261024`通过19次故障注入和19次协调冷复位恢复，共1478082周期；`access_fabric_v3_cold_20261024`以完整默认容量通过两条冷路径，最长服务262129周期，共524541周期。两项合计53.384s、exit0，独立源绑定审计均passed。所有权修复没有改变这些正常冷启动和故障测试的计数。

`access_fabric_v3_synthesis_20261024/final_audit.json` passed：19739 LUT、16938 FF、375 BRAM、3 DSP、453 CARRY8；零URAM、latch和组合环。LUTLP-1与check_timing loops均为0，没有忽略组合环约束。完整默认容量163840帧，Vivado2022.2 OOC实际综合433.643s、exit0、checksum298dc55e、history92。完整日志按唯一标记从会话日志提取，原100KiB截断收据也保留，审计逐行绑定通过。

时钟为10ns研究约束；2864输入和1307输出没有平台delay，HD.CLK_SRC未设，尚未布局布线。本资源统计不含外部owner后端及metadata生产器，不代表完整FPGA路由资源或速度。功能、边界、冷启动和结构门禁对应同一v3冻结源。

## 后续

[完整CPU占用观测](owner_profile_20261024.md)已补齐18515060次更新及加载预引用语义，独立重放通过。下一步实现真实设计级occupancy和同net引用服务（占用按不同net计数、分支共享引用增减、overflow和提交可见性），替换owner模型；然后从children/design store生成静态/dead快照并检查hot/ns一致性。再连接geometry/cost、Frontier和显式递归栈，处理回溯与提交。保留target先CLEAR、prev写后重算SLL、首次push置visited、CP不清heap/栈和设计history独立生命周期。
