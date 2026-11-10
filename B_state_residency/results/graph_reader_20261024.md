# 真实图 CSR / 属性 AXI 读取验证（2026-10-24）

`hardware/variants/graph_reader_v1/graph_static_reader.sv` 已从完整真实图的二进制文件经 AXI 模型读取原始 CSR 和 32B 属性。功能回归、逐笔独立审计和实际 OOC 综合均 passed。它是独立图读取服务，尚未与 children_build_engine、动态设计状态或自动页引擎整合，不能据此声称完整设备路由或加速。

## 数据与覆盖

输入为已通过原 CPU 加载器全量核验和逐字节 RRT 重建的 `graph_image_20261024`：9,089,009 节点、40,469,536 原始有序边。读取器保留原始属性全部 256 位、原序和重复边，不进行过滤或创建副作用。

AXI 从端通过 `$fseek/$fread` 读取 offsets.u32le、edges.u32le、nodes.rrt32，64B 尾部补零；Python oracle 独立按小端字节生成期望值。三个 64 位基址分别为 0x1fffff000、0x10fffff000、0x20fffff000，实际覆盖 4GiB 以上及低32位进位。不是把 oracle 服务回复直接喂给读取器。

| 项目 | 完整选定集回归 |
| --- | ---: |
| 抽样父节点 | 10,163 |
| 全部真实 CSR offset 4KiB 边界 | 8,875 |
| META 成功 | 10,163 |
| CHILD 成功 | 44,480 |
| CHILD index=degree 合法拒绝 | 10,163 |
| 真实图请求合计 | 64,806 |
| 对应逐笔审计 AXI AR/R | 221,602 |
| 加入错误/恢复用例的总 AR/R | 221,640 / 221,640 |
| 检查数 | 64,828 |
| 配置检查（含重配） | 28 |
| 故障场景 | 19 |
| AR 背压周期 | 54,973 |

节点选择含首尾128、固定种子1024随机节点、每种实际度数首例及重复边首例。实际度数为0/1/2/3/4/5/6/8/10/12/16/18，含全部16种 offset 对齐和两种属性半拍。每个选定父节点验证 META、全部原序 CHILD、越界 CHILD index。独立 auditor 重读原文件，再逐行比较全部 AR 地址和完整响应日志，校验来源/冻结源/向量/日志 SHA、事务守恒及选择覆盖。

另有未配置、非法 op/node/META index 无 AXI、配置对齐/范围/溢出/重叠拒绝、零边与末字节2^64−1配置接受、配置锁定及响应背压检查。19 故障为四个读阶段的 RRESP/RID/RLAST 各错误（12），五种 CSR/child 数据错误（5），无归属 R 与已提供响应期间晚到 R（2）。错误停止新工作；已提供回复保持，调用者须同时查 fault。当前没有热取消/超时/自动恢复，需总线及上下游协调冷复位。

200请求先导同样 passed：222检查、28配置、19故障、415 AR/R。完整 XSim 运行11.851s，虚拟结束时间26,780,580ns；这些是该验证程序的时间，不是路由吞吐量或相对基线收益。末尾不足64B的文件读警告来自最后表拍，模型先补零；全部合法记录字节及地址通过审计。

## 实际综合

Vivado2022.2、xcu280-fsvh2892-2L-e、10ns研究时钟、OOC：

- 1,829 CLB LUT、873 FF、166 CARRY8。
- BRAM/URAM/DSP/latch均0；LUTLP-1与check_timing loops均0，无内部无时钟/无约束端点。
- 880输入、519输出未设置IO delay；HD.CLK_SRC未设置，未布局布线，无外部接口频率或板上时序结论。
- 资源不含图数据存储。配置范围验证、64位地址计算和256位响应寄存器在本模块内。
- MCP 60.108s/exit0，checksum `17e9e66c`；完整回归 MCP34.591s/exit0。

冻结结果：`graph_reader_20261024`，manifest SHA `17164dd246812ff861955fdea4d9d88289540b0e20557df0119115be272f0498`；`scripts/audit_graph_reader.py` passed。综合结果：`graph_reader_synthesis_20261024`，`scripts/audit_graph_reader_synthesis.py` passed，DCP和工具完成收据已保存。所有源与结果不覆盖。

## 接下来

按 [GRAPH_READER_CONTRACT](../hardware/GRAPH_READER_CONTRACT.md) 将 META 的实际 count 作为构建输入；绑定 generation/parent/position，把实际原始属性供给 NEXT/CLASSIFY 等服务。实现独立设计级 created/dead、持久过滤缓存的 claim/publish/hit；再接 paged_exclusion，整个构建锁住 query/price 与相关标签修改。缓存命中不重新过滤，空缓存也有效；淘汰应保留后备列表或原序位图，查询 checkpoint 不得清除设计状态。Frontier复位、距离代价、回溯/提交、平台和板上仍在后续范围。
