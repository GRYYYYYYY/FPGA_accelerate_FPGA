# 坐标服务实验（2026-10-24）

已实现静态属性、动态 SLL endY、SLR 行表及 Laguna 列表读取，连接实际图读取器和分页标签服务。接口见 [COORDINATE_SERVICE_CONTRACT.md](../hardware/COORDINATE_SERVICE_CONTRACT.md)。目前不是完整 FPGA 路由器，也没有板上或端到端加速结论。

## 功能联调与独立审计

源绑定结果：`coordinate_service_v2_20261024/manifest.json`、`source_bound_audit.json`。

| 测试 | 请求 | 标签读取 | 图 AXI 读 | 表 AXI 读 | 检查点 | 仿真周期 |
|---|---:|---:|---:|---:|---:|---:|
| 合成图，32 槽 | 740 | 250 | 1946 | 385 | 8 | 79252 |
| 真实图，32 槽 | 23957 | 23292 | 95820 | 11660 | 13 | 2272678 |
| 合成图，1 槽/缩位编号 | 740 | 250 | 1946 | 385 | 17 | 79147 |

真实测试覆盖 9,089,009 节点图的全部 11,520 个 SLL 节点及分散非 SLL 样本。标签写、CP、CLOSE/OPEN、身份错误拒绝与响应背压均通过。独立 Python 审计重新计算每次返回，检查全部图/表 AXI 字节、标签后备读写及最终文件；测试台另在原生 READ 边界对照标签记录和 presence。

合成表包含 128 行/64 列，覆盖跨 SLR、Laguna 柱及 INT_MIN/INT_MAX 哨兵。真实图为 311 行/无 Laguna 列，不能将合成列覆盖说成真实跨器件测量。当前功能目录 16384 帧与默认综合 163840 帧分开记录。

首轮 `coordinate_service_20261024/` 在生成向量时因子 Python 继承 Vivado PYTHONHOME 而启动失败，未进入 RTL。v2 子进程补 `-I` 后通过，设计 RTL 未变；保留失败日志。合成 CSR 尾部不足 64 字节由内存模型显式补零，XSim 的 fread 尾部警告已由逐字节审计核对。

## 默认前驱语义

`coordinate_inputs_verify_20261024` 使用冻结原始 loader，逐项核对真实表，并使用原 Router/SparseLabels 验证 hot0/hot1：dense 默认 −1 返回 Y70，paged 空 prev0 返回 Y10，显式 −1 恢复 Y70；前驱也是 SLL 时只看其静态 endY，不能递归。硬件保留实际零标签，未将 absent 强制转成 −1。

本次真实 node0 静态 endY=273；全部真实 SLL 的空标签条件下，没有因 prev0 而改变静态 endY。合成组各有 18 次空标签坐标改变，负例确实进入硬件。这个结果不能替代完整 dense/paged 路由兼容性门禁。

## 故障与实现

`coordinate_boundaries_20261024`：40 项控制器检查和 17 项表读取器检查通过，覆盖错误身份/状态、非法前驱/坐标、token3 实际耗尽、64 拍超时、服务/无归属响应、owner 改变、中断、背压期间迟到故障、地址配置及 AXI 协议错误。该组服务边界使用模型。

`coordinate_integration_boundaries_v2_20261024`：实际组合 7 故障/7 冷复位恢复通过，99422 周期；原始 AXI 日志记录图 R 错误1、表 R 错误1、标签 R 错误2、标签 B 错误1。另含非法 prev、执行中 abort、已给响应期间 abort。重置同时清除测试内存模型的旧事务，不能外推为任意物理总线独立复位安全。

组合故障首轮 `coordinate_integration_boundaries_20261024` 在 665ns 恢复采样处失败：wait(rsp_valid) 后同 delta 检查数据。v2 唯一测试台改动是在检查前等待下降沿；所有设计 RTL 与功能冻结源相同。负例保留，独立审计核对该唯一差异。

`coordinate_synthesis_20261024/final_audit.json`：默认163840帧完整坐标服务实际OOC综合 **17873 LUT / 14570 FF / 375 BRAM / 3 DSP / 376 CARRY8**；零URAM、锁存器与组合环。综合311.908s、exit0、checksum a901d510、MCP history78。保留约100KiB截断的MCP收据，并从同一Vivado会话按唯一marker保存完整日志、逐行绑定验证及DCP。

当前2180输入和1391输出无delay约束，HD.CLK_SRC未设；只有研究用10ns时钟约束，未布局布线。资源不含外部图/表/标签后备存储，不把独立模块资源简单相加当成完整搜索系统资源，也不提供板上频率或加速结论。

## 后续

为 access_step 增加驻留状态和请求归属包装，连接 visited/target/prev、图属性与本坐标服务；再接价格/同网引用、几何与代价核心、完整搜索和显式递归栈。保留 target 先 CLEAR、prev 写后重算 SLL 坐标、首次 push 即 visited、CP 保留 heap/栈；最终验证回溯和设计级提交。

项目 check 和 smoke 均通过，plan 已更新。所有新正负例留在本目录，原始基线与其他方案未修改。
