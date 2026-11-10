# 文献输入与本地数据核查（2026-10-22）

结论：LaZagna 和 Into the Third Dimension 的主要评测输入是公开应用电路的 RTL/BLIF 网表，以及目标 FPGA 的架构描述。研究布线算法可以使用这些电路在研究架构上的资源图和固定布局，不以商业 DCP 或已有 RRT1 导出为前提。

此前“本机未找到真实输入/DCP”的判断错误：默认文件检索遗漏了被忽略的目录，输入类型也过度限定于原适配器格式。本次确认了公开电路、VPR 中间文件和商业器件设计。正确状态是“数据已定位，方案 C 接入和新实验尚未完成”。本次没有执行新的布线，也不把相邻项目的既有结果登记为方案 C 实测。

## 两篇主论文具体使用什么

| 工作与原文位置 | 电路输入 | 架构/其他输入 | 后续处理与评测 |
|---|---|---|---|
| LaZagna，PDF 第 5 页 III.D、IV.A，第 6 页 IV.B | Koios 子集中的应用电路 RTL，经 Yosys 综合；选择能在 2D 基线上 1 小时内完成 PnR 且装得进目标资源的电路 | FPGA 网格、层数、CLB/DSP/BRAM、通道宽度、垂直 SB/CB 连接方式、位置、密度与延迟等参数，生成 3D 路由资源图（RRG） | VTR 8.1 完成应用电路布局布线，评估线长、关键路径延迟和利用率；定制 OpenFPGA 1.2 生成结构 RTL/比特流 |
| Into the Third Dimension，PDF 第 7 页 IV，第 8 页 V.A | 明确写明 VPR 接收设计 BLIF 网表；同构 3D 案例使用 Koios | XML 架构，含层与跨层连接；RAD-Gen 给出资源面积、延迟和 TSV 占位等模型参数 | 先在能容纳电路的最小 2D 规模上建立基线，再映射到对应 3D 架构，比较线长和关键路径延迟 |
| Into the Third Dimension，第 8 页 V.B | 与 NoC 相连的流式 MLP 加速器电路 | FPGA-on-ASIC 架构，NoC/SRAM、跨芯粒接口及其面积/时序模型 | 比较异构 3D 与对应 2D 系统的布线及时序、NoC 指标 |

来源：[LaZagna 本地 PDF](<../../LaZagna：An Open-Source Framework for Flexible 3D FPGA.pdf>)、[作者论文页面](https://arxiv.org/abs/2505.05579)、[Into the Third Dimension 本地 PDF](<../../Into the Third Dimension：Architecture Exploration.pdf>)、[作者公开全文](https://andrewboutros.github.io/assets/pdf/papers/026_fpt2023_3dfpga.pdf)。页码按 PDF 文件页序计；本地 LaZagna 为 arXiv v4（2026-01-22），不要将当前仓库版本自动等同于论文实验版本。

LaZagna 需要区分两条流：一条把架构参数变成 **FPGA 本身的 fabric RTL**；另一条把 **用户应用电路**映射到该 FPGA。论文用 MCNC 的 `s298` 验证生成 RTL/比特流的功能，又用 FreePDK45 和修改后的 RTK LEF 做一个 4×4 fabric 的物理实现示范；这些与 Koios 主实验的输入角色不同。当前[官方代码说明](https://github.com/sharc-lab/LaZagna)支持 YAML 配置、架构 XML 和 Verilog/BLIF 基准。

Into the Third Dimension 的完整框架还需要工艺、互连 RC、键合间距、TSV/供电等参数来构建架构模型。做固定架构上的路由调度比较时，可以先冻结已有模型；若要研究新的物理结构或宣称工艺 PPA，则必须说明这些模型的来源和适用范围。

## 三份 HTML 及其他相关工作

这三份 HTML 是研究综述/方案，不能视为各自已经完成了一套独立基准实验。

| 文档/相关路线 | 输入含义与可复用内容 |
|---|---|
| [3D IC研究进展梳理](../../3D%20IC研究进展梳理.html) | 明确推荐 LaZagna/Beyond-Flatland 的公开电路和架构，导出/导入 VPR RRG，并在固定布局上比较路由器。Beyond-Flatland 公开 20 个 ML/DNN 电路的 BLIF 及架构 XML、运行配置；是本方向直接可用的来源。 |
| [润色开题报告](../../润色开题报告.html) | 包含两类工具路线：VTR/OpenFPGA 的网表＋研究架构，以及 RapidWright/FPGA Interchange 的商业器件模型＋逻辑/物理网表。提及 Potter、CUFR、RND 等对照，但每个工具的入口和版本仍要单独适配。 |
| [FPGA 加速方法综述](../../fpga_acceleration_methods_2016_2026_zh.html) | 覆盖多类计算任务。Sextans 的运行时输入是稀疏矩阵与稠密矩阵；FlowGNN 是图结构、节点/边特征与模型权重；AutoBridge/RapidStream 面向 HLS/数据流硬件设计及其物理实现约束。它们提供调度、缓存、编译方法参考，不能把应用运行时数据直接当作 FPGA 布线基准。 |

公开来源：[Beyond-Flatland](https://github.com/andrewluoooo/Beyond-Flatland)、[Sextans](https://github.com/linghaosong/Sextans)、[FlowGNN](https://github.com/sharc-lab/FlowGNN)、[FPGA'24 布线竞赛格式与流程](https://github.com/Xilinx/fpga24_routing_contest)。本地 Beyond-Flatland 数据的锁定源是 `IY2002/Beyond-Flatland`，见下表，不能仅凭同名仓库假定提交一致。

例如，`spmv.blif` 表示“实现稀疏矩阵运算的硬件电路”，不是“一个稀疏矩阵”。前者可以成为 FPGA 布线任务；后者用于测量该加速器执行应用的性能。综述另提到 InstantGR 的 `.cap/.net` 容量网格输入，其语义与 FPGA 中带可编程开关、引脚类型和方向的 RRG 不同，不能只转换文件后缀就视为等价。

## 本地已确认的输入

详细绝对路径、文件大小、原溯源哈希与本次复核哈希见 [input_inventory_20261022.json](data/input_inventory_20261022.json)。`source_manifest_sha256` 是既有记录，`verified_sha256` 才是本次重算；没有重算的文件不能说已完成哈希验证。

| 来源 | 已存在的内容 | 本次核查与用途 |
|---|---|---|
| 相邻 `../../3D_FPGA_routing/benchmarks/downloads/beyond_flatland/` | 20 个 BLIF：attention、conv、LSTM、GEMM、SpMV、TPU 等；原始 `sb_architecture.xml` | 20 个网表逐一检查存在；重算 attention_layer、softmax、spmv 的哈希并与锁定记录一致。架构也已重算哈希。锁定源提交 `84ba44acf1bad597bc5a9d1f615415870e178a86`，详见相邻项目 `benchmarks/beyond_flatland.lock.json`。 |
| `FPGA_Acc/projects/tileplace/experiments/attention_layer_input_capture_2026-08-31.json` | Koios `attention_layer` 的架构、BLIF、packed `.net`、固定 `.place`、基线路由、RRG、`connections.csv` | 网表、布局、路由和连接表哈希已与原记录比对；原记录有 41,954 个连接、6,181,188 个 RR 节点和 91,982,111 条边。7.19 GB RRG 本次仅查存在和大小，没有重算图哈希或重新解析图计数。 |
| `FPGA_Acc/projects/tileplace/experiments/titan23_neuron_input_capture_2026-09-01.json` | Titan23 `neuron`，对应 Stratix IV 架构、SDC、网表/布局/路由/RRG/连接表 | 可扩展规模与工作负载；原记录 77,106 个连接。大 BLIF 和 3.26 GB RRG 本次仅核对存在/大小；其余核查范围见清单。不能把 Titan 的硬块模型直接配给任意 Koios 架构。 |
| `FPGA_Acc/projects/persistroute/third_party/fpga24/logicnets_jscl/` 及其 experiments 目录 | `logicnets_jscl_unrouted.phys` 和 `logicnets_jscl_vivado_input.dcp`，目标 `xcvu3p-ffvc1517-2-e` | 两者存在，哈希与已有来源记录一致。可用作商业器件验证路线；当前 C 的 RRT1 适配器还不能直接读取它们。 |

上述 `FPGA_Acc` 的绝对根目录是 `/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_Acc`。无需复制 GB 级图或修改相邻项目；在本目录引用锁定清单，保存新派生产物即可。

相邻 3D 项目还有 `koios_native3d_n6_f16_d1_v3.xml` 和已准备的运行目录。该架构是保留 Koios 硬块/平面模型、接入原生 CHANZ 的本地适配，不能称为原版 LaZagna/Beyond-Flatland 架构的逐字复现。接入时必须选择已通过源工具检查的完整网表/布局/RRG 配对，并读取对应 provenance；同目录里也有失败运行。

## 方案 C 接下来应接入什么

主线采用与用户所列论文一致的 VPR/Koios/Beyond-Flatland 输入。将商业 Interchange/DCP 作为后续验证来源。一次可比较的固定布局路由实验至少冻结：

1. **电路与布局**：BLIF、packed `.net`、`.place`、适用的时序约束；从完整网连接和引脚映射提取连接任务。
2. **目标资源图**：架构 XML、RRG 的节点/边/开关、层、坐标、方向、容量、时延和通道宽度。记录图与构图工具的版本/哈希。
3. **路由状态和协议**：初始路由树、占用、历史拥塞、关键度、迭代顺序、随机种子、停止条件与计时范围。基线与候选使用同一个搜索后端，隔离调度策略的影响。
4. **校验和结果**：保留基线 `.route`、运行日志、合法性与时序检查；新轨迹记录连接耗时、访问资源、预算退出及重试代价。`.route` 是结果/参照，不能代替完整资源图；只测最终路径上的边也不能代表搜索足迹。

现有 `profile` 仅接收 eager RRT1，不能直接喂入 `.blif`、RRG XML、`.phys` 或 DCP。VPR 接入应保留 `RRNodeId` 语义，以 `(rr_graph_sha256, rr_node_id)` 标识资源；不能强行套用当前 RRT1 的 `(tileAddr << 20) | wireIndex` 编码。VPR 数据接口与插桩尚待实现，未把清单状态改为 `ready`。

这些公开应用电路在研究架构上的运行可以形成有效的布线算法基准；应同时说明电路来源和架构模型。CPU 墙钟、模型预测的关键路径延迟、商业工具时序以及 FPGA 实卡性能是不同指标，分别记录。此前手写 64 节点图仍只用于程序验证，其预算重试尚未证明加速。
