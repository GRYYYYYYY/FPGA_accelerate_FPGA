# 共享资源故障与多项 journal 的完整 warm 恢复

build_tb.py 只从已审计 warm_system_v2 的 TB 增加 warmfaultnode 参数、物理 B 握手观察，并把 warm 模式下的 owner B 错误延迟到选定共享资源。初始旧 q1 故障不变；所有生产 RTL、配置和独立数值 oracle 不变，逐文件 SHA 验证。

两个目标均来自真实 CPU q2 路径：554512 是第5次 owner 写，263946 是第6次。32槽和单槽各执行两目标，共四例。SHARED_B 记录实际 ready/valid 的节点、BRESP 状态与 journal 数量；第5/6个 B 必须返回SLVERR，先前4/5个返回成功。实际物理写已经发生，由后端字节重放确定其结果；不假设失败B意味着未写入。

G2/CP18 已吸收 q1，因此四个新资源的恢复目标是 ref0/occ0，共享资源目标是 ref1/occ1。原始 G1 图像对应共享行全零。第5写错误生成5项journal（4个新资源+共享554512），第6写错误生成6项（再含共享263946）。两轮原生 G2 GET 必须按journal顺序返回目标值；工作 owner 第一轮 GET/DEC，第二轮 GET 验证。每个共享行实际由ref2降回ref1，occupancy保持1，不能误按G1再降至0。未触碰的另一个共享资源在第5写场景同样保留原q1关系。

每例从原始输入开始，在同一RTL实例中完成旧故障修复、q1重试、G2发布、共享故障、多项修复、328标签与保存路径/查询恢复、attempt5/query3/price5下的q2重试和两次拆线。中途没有冷复位或重新装载工作DDR；沿用原生 target_reset。没有直接驱动journal、ref计数、配置回执或原生完成回复。

独立审计核对真实B顺序、5/6个journal键、两轮G2快照GET值/地址、15/18个工作owner修复操作及响应、原始标签写入与读回、源查询字节、全部8路AXI与最终DDR。q2重试43poll/42expand/176candidate/122cost与CPU数值oracle一致；保存q1路径原生拆线向量等于bundle，两个共享行在重试/拆线阶段2→1→0，其他net的状态逐字节保留。G2与G1的ref1/ref0差异是实际数据对照，不是另行运行错误绑定G1的硬件负例。

价格/history DDR内容未改变，只有attempt标签改变；不证明真实价格变化后的距离标签复用。仍为单net、两路径、owner capacity0、两个确定写回复故障点的行为RTL验证；无综合/时序/板卡收益结论。恢复流/AXI在途取消、恢复过程失败后的非冷复位重试、回绕/未知页、通用多net/overflow、运行中快照生产与持久化认证/下限仍待完成。
