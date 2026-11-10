# 显式时钟与接口预算研究壳

两份clock_shell包装冻结的原版/宽codec端点，保留全部参数、端口、默认容量及数据/ready-valid连接。唯一硬件变化是输入clk通过一个BUFG再驱动端点。没有输入/输出寄存器、流水延迟或协议转换。复位仍为原端点的同钟同步复位。

`make_clock_shell.py`从各端点头部生成完整命名连接，并机械迁移已有测试台的模块名与`dut.endpoint`观察路径。测试刺激、断言、字段/页字节oracle及失败条件均不改；UNISIM BUFG行为模型用于回归。

研究约束：10ns输入时钟；以`b_clock/O`的有效时钟边沿为外部预算参考，输入最小0.5ns、最大2ns，输出最大2ns、最小-0.5ns（对应0.5ns保持预算）。包括同步rst和控制输入，所有非时钟输入与全部输出均覆盖。没有false path、multicycle、waiver或固定BUFG位置；布局工具选取缓冲位置并布线时钟网络。

参考引脚语义依据Vivado 2022.2官方命令说明：[set_input_delay](https://docs.amd.com/r/2022.2-English/ug835-vivado-tcl-commands/set_input_delay)、[set_output_delay](https://docs.amd.com/r/2022.2-English/ug835-vivado-tcl-commands/set_output_delay)。这些数值是预先声明的研究条件，不是从未提供的板卡数据推导的要求，也不是为了清除违例而事后选择。

实现须分别保存内部、输入到寄存器、寄存器到输出及输入到输出路径，报告时钟缓冲数量、位置、时钟网络路由、约束覆盖与全部违例。原版/宽版使用相同流程。正裕量仅证明该模型下的时序；负裕量作为测量结果保留。外部实际连接、CDC、引脚、负载、复位来源、平台及DDR/HBM时序仍需系统集成验证。OOC没有真实外部端口负载，不等于板级实现。
