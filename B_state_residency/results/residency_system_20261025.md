本轮把真实服务组合从测试台抽成独立可综合顶层 `residency_system`，并完成完整组合 OOC 综合。默认正常路径2例、真实成本续接2例、真实route故障恢复10例，共14次 XSim 2022.2 运行及独立审计通过：逐周期 trace、七份 AXI 文本和四种完整内存图像均与抽取前相同。相对抽取前的116份组件RTL/dat不改，新顶层连接它们并捕获外部恢复快照描述。

入口为 [residency_system.sv](../hardware/variants/residency_system_v1/residency_system.sv)、[接口清单](../hardware/variants/residency_system_v1/interface.json)、[结构生成器](../hardware/variants/residency_system_v1/build.py)及[契约](../hardware/variants/residency_system_v1/CONTRACT.md)。机器结果见 [JSON](residency_system_20261025.json)，87个冻结文件保存在 residency_system_sources_20261025/sha256.json。

顶层包含13个实例：原 candidate_recursive_engine、route adapter、recovery/config/label 三个控制器、transaction_fence 和七个 AXI 排空观察器；原图、设计、分页标签、owner、cost、connection、heap及HLS服务位于 engine 层级内。硬件组合不含 CPU oracle、文件 agent、测试激励或层级写入。测试台现在只驱动外部接口、提供存储/authority/快照流并进行只读观测。313个逻辑端口展开为55,702个接口位，其中包括16路宽packed ABI；这仍需后续总线包装，不能将这些位当成已经完成的封装引脚方案。

恢复 checkpoint/version/design/query/price/cookie 都是明确输入；标签 snapshot 的 design/checkpoint/cookie/count/nodes/probe 在恢复命令 valid/ready 握手时锁存，不再把328条、9089009节点或150697探针固定在硬件内。10个故障fixture均在接受恢复命令后的 negedge 反转全部 snapshot 描述输入，并在标签恢复期间逐字段检查捕获值；实际恢复仍成功且轨迹未变化。标签流每条记录独立带 cookie。外部快照集合的完整性、唯一性、数据真实性仍是可信前提。

复位域也移入顶层：`rst=k_cold_rst||k_target_reset`。服务复位不会清围栏、journal和恢复控制器；target reset继续受正常事务退休、原服务 retired_idle 和物理AXI排空约束。诊断注入参数默认关闭，正常双查询使用0，故障fixture显式使用1。原 engine `abort`保持原语义，不声明为所有控制器的统一取消接口。

| 验证组 | 运行数 | 关键结果 |
| --- | ---: | --- |
| 默认生产参数正常双查询 | 2 | 诊断注入关闭；每次116 POLL、114展开、447判定、293成本、879标签ACK；完整共享提交/ripup |
| 真实服务续接 | 2 | 父前端回复先消费，真实center HLS和cost AXI子回复背压7周期，后端父上下文保持 |
| route故障与恢复 | 10 | owner B/R错误、label R错误、取消、版本漂移，各32槽/单槽；描述输入复用后仍按锁存快照恢复 |

逐周期比较分别绑定上一轮三组已通过CPU/字节/协议独立审计的结果：transaction_fence_normal_rtl_v1、transaction_fence_normal_dependent_rtl_v1、transaction_fence_static_join_rtl_v1。审计重新验证参考manifest/源及参与比较的全部artifact哈希，不仅比较 PASS 字符串。默认正常和续接配置的总周期仍为32槽683640、单槽747471，本次结构抽取没有添加周期。owner共享节点、四阶段完整owner、标签物理帧和全部cost/design状态保持。

完整顶层 OOC 使用 U280 `xcu280-fsvh2892-2L-e`、32槽、16,384帧、INDEX_BITS14/HASH_BITS15，诊断注入默认0，运行时输入没有绑定为特定设计数据。Vivado原生Tcl在535.115秒正常退出，DCP、综合网表、资源报告均生成：

| 资源 | 使用量 |
| --- | ---: |
| LUT | 79,811 |
| FF | 60,324 |
| BRAM Tile | 160.5（160×RAMB36、1×RAMB18） |
| DSP | 23 |
| URAM / latch / black box | 0 / 0 / 0 |

综合网表查询也确认文件agent实例数为0。源清单继承仿真文件集，包含一个未实例化的 AXI 文件模型定义；它仅产生声明警告，不存在于综合网表。没有时钟约束、布局布线、Fmax或板卡测试，本数字是现有服务组合综合资源，不包含尚未实现的自主搜索调度器、主机包装或完整快照生产器。

综合记录保留5,026条警告：2,963条常量输出、2,040条未使用端口、10条删除未使用寄存器、4条寄存器截位、5条未实例化文件agent输出初始化、2条旧codec零次复制、2条RAM降为寄存器。最后两条对应 `counts_reg` 和 `cursors_reg`，工具说明包括同进程多写端口等推断限制，已将其寄存器代价计入资源；没有把警告改成忽略或声称零警告。实际综合零ERROR、零CRITICAL WARNING、零latch。综合经过300秒观察窗口后继续跟踪同一原会话，没有因观察超时重启；结束后查询网表事实并关闭仅本轮创建的综合会话，监督记录见 residency_system_supervision_20261025.json。

下一优先实现设备侧 search/prepare 调度：从真实heap POLL取parent，走当前展开/结果流，驱动目标检测、准备和route提交；正常共享与故障归属回归保留。随后扩展完整 checkpoint，包括 design-created/cache、frontier、保存路径及所有legacy owner/design/cost写入。当前snapshot/authority仍外部，初始化工作集为CPU预知328条，本轮恢复只覆盖route journal；未知页、真实恢复期AXI故障、table活跃排空、实际价格变化/epoch回绕、容量预留、耐掉电和板卡加速尚待完成，研究目标保持active。

四份归档均将原目录移开后实际解压，1628个文件逐SHA核对；执行与综合独立审计重新运行，四份audit JSON与原始结果逐字节一致，原目录保留。见 [恢复收据](residency_system_restore_20261025.json)。Python语法检查和 `python3 scripts/run.py check` 通过。
