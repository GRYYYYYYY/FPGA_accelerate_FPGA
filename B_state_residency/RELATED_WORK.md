# 驻留标签的方法来源与待检验差异

本记录区分成熟数据结构、当前适配和未验证假设。它不是穷尽的最近邻检索，也不支持新颖性或发表结论。

## 稀疏集合

Briggs与Torczon的1993年论文用dense/sparse双向索引和成员计数进行成员判定与清空；成员校验同时检查索引边界和反向元素身份。论文应用于编译器寄存器分配。原文：[An Efficient Representation for Sparse Sets](https://www.dcs.gla.ac.uk/~pat/ads2/papers/sparseSets.pdf)，本地保存于 `data/raw/literature/Briggs_Torczon_1993_sparse_sets.pdf`。

对本项目的推论：当前compact同时保存页内uint32索引和uint32 epoch，可尝试将epoch替换为紧凑池中的全局node ID反向验证。候选判定为 `index < live_count && dense_node_id[index] == requested_node`，查询切换令live_count=0。该迁移现已完成独立8次先导，见 `results/identity_pilot_20261022.md`；容量下降但本轮单次未提速，不把该成员判定称为新算法。

必须额外检查：页槽换绑后旧索引指向其他node、旧索引恰落在新live_count范围内、紧凑池增长、查询结束回收、独立context、空池以及失效后prefetch。C++存储必须有合法已初始化的索引值或另有已定义的未初始化处理方案，不能从论文抽象中推出读取未初始化C++整数安全。反向验证增加一次依赖访问，减少元数据不一定减少耗时。

## 数组初始化的空间—访问代价

Hagerup与Kammer研究word-RAM中常数时间初始化与空间/单项访问时间的取舍。原文条目：[On-the-Fly Array Initialization in Less Space](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ISAAC.2017.44)，ISAAC 2017，DOI 10.4230/LIPIcs.ISAAC.2017.44。

对本项目的边界：理论上减少初始化或元数据的结构不自动给出更少缓存停顿、FPGA端口占用或DRAM事务。应将完整访问链、增长/失效/回收和尾部查询放入同一个对照；理论复杂度不能替代综合或实测。本文暂未实现该论文结构。

## 当前贡献候选需要证明什么

| 机制 | 当前证据 | 尚需证明 |
|---|---|---|
| 原有分页与逐节点epoch | 两真实设计首轮，首设计已有三次重复 | 完成当前78次矩阵；与原始串行对照，保留负结果 |
| 紧凑标签池 | ASan/UBSan、同模式输出一致、容量下降 | 是否在不同页粒度/尾部稳定获益，映射依赖开销是否抵消收益 |
| dense/sparse反向成员校验 | 独立实现、ASan/UBSan旧索引检查、8次真实配对先导 | 如需正式Pareto主张须预先设计重复；本轮容量改善、时间未改善 |
| 版本化占用与查询失效 | CPU规格、真实570286事件回放 | 真实history事件、设备传输、有限版本排空、实际并发与集成 |
| 活跃页与后备存储 | 首设计CPU标签流LRU敏感性分析 | 运行中写回/换入协议、真实器件资源/接口、综合与实卡测量 |

当前两个设计的首轮原始串行仍最快。可研究的差异在于路由状态生命周期、同网引用及严格质量约束下的布局/协议组合；是否形成贡献须以完整对照和进一步最近邻比较判断。不能用相对整页清零的改善隐藏相对原始串行的退步。
