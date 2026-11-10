# 设计级状态与持久过滤缓存服务（2026-10-24）

新增 `hardware/variants/design_store_v3/design_state_store.sv`：实际AXI外存记录、排他claim、原始边位置位图、成功B应答后发布。它补上created/dead/过滤缓存的存储服务，不再仅用测试函数维持这些状态；尚未与图读取器、children HLS或paged_exclusion组合。

每节点16B，flags(created增量/dead/cache_valid/design_sink)、raw_count32、keep_mask32、reserved32。原始CSR位置位图保留顺序和重复child，空缓存单独valid；查询切换不清设计记录。当前真实图后备区145,424,192B，在设计开始时一次清零，后续直接读写；不是每connection重新分配/清零。32位置容量适用于已核验最大度18，超32明确拒绝。

## 验证结果

测试使用完整大小的零初始化文件作AXI存储，每次AR读取真实64B，每次W按16B WSTRB写回；AW/W独立随机背压，B延迟返回。4523真实CSR父节点及其child ID/度数驱动存储操作，保留决策为人工确定的测试输入；另有一组degree32边界。因此这是实际存储协议验证，不是原getChildren完整过滤语义联调。

| 指标 | v3完整选定集 |
| --- | ---: |
| 正常命令 | 98,893 |
| 检查 | 98,895 |
| 正常逐笔审计读事务 | 68,287 |
| 含安全冷复位后读取的总AR/R | 68,288 / 68,288 |
| AW/W/B | 17,821 / 17,821 / 17,821 |
| 发布 / 随后命中 | 4,524 / 4,524 |
| 空缓存发布 | 890 |
| owner相关拒绝 | 9,049 |
| 涉及记录 | 23,833 |
| AW先 / W先 / 同拍接受 | 4,449 / 8,883 / 4,489 |

独立 `scripts/audit_design_store.py` 从零状态重放协议，重新核对真实CSR度数，逐行校验所有AR地址/64B内容、W地址/字节使能/512位数据、B成功后才返回的顺序和claim状态。最终全部145,424,192B与独立预期完全一致，包含未访问字节与邻记录；最终SHA `61ea6e5da3854af1df7d3a81f0855d21b135ebdaf6e21335067589eb3afc42f3`。

另有200命令先导、17故障/35检查/24配置、31读/5写，全部passed。故障包含RRESP/RID/RLAST、五种记录内容损坏、CREATE/PUBLISH的B错误/错ID、缓存度数不符、发布前外部valid、无归属R/B和持有回复时晚到B。故障模型在B错误前也写入物理字节；独立最终全文件审计确认控制器没有把这些错误当成功，保留claim并停止。**错误B不等于没有写入**，恢复不能简单重新过滤或重试发布。

响应及AW/W背压稳定、同一64B内四个记录不互相覆盖、幂等CREATE不重复写、父节点创建/死端位在PUBLISH时保留、bit31/全32位mask、空缓存valid和安全冷复位后继续读取也通过。冷复位测试在全部命令退休且没有claim时执行，不证明未完成构建可恢复。

## 失败与修正记录

`design_store_20261024`首轮在TB编译失败：任务名config是SystemVerilog关键字。`design_store_v2_20261024`只将该任务改名后全回归passed；`design_store_v3_20261024`仅新增B日志和发布等待断言，便于独立审计提交顺序，同样passed。三版RTL和oracle完全一致，负例/已通过结果均保留并绑定审计；没有以修改期待值消除RTL失败。

v3 manifest SHA `26b1678947ca7881e6dd85494a05113b47ae5d49aa21b8222bc74915a9073056`。MCP回归41.486s/exit0；虚拟完整用例16,080,290ns，是测试程序端点，不能解释为完整路由性能。

## 实际综合

`design_store_synthesis_20261024`及 `scripts/audit_design_store_synthesis.py` passed：Vivado2022.2 / xcu280-fsvh2892-2L-e / OOC10ns研究时钟，**1059 LUT、1056 FF、34 CARRY8**，BRAM/URAM/DSP/latch均0。LUTLP-1/check_timing loops均0，无内部无时钟/无约束端点。

762输入/849输出未设IO delay，HD.CLK_SRC未设，未布局布线，无接口频率结论。资源不含外存后备区或其他组件。MCP60.628s/exit0/checksum5f59a1a9，源/DCP/日志/工具收据均保存。

## 后续整合

按 [DESIGN_STORE_CONTRACT](../hardware/DESIGN_STORE_CONTRACT.md) 接图META→CLAIM→hit重放或miss构建。CLAIM先于HLS START，owner由外层扩展事务分配，之后绑定HLS generation；不要引入循环依赖。有效created为图初始标志OR设计增量，design_sink须从真实设计端点表导入，结构dead谓词遵循原函数。

整个CLAIM/构建/缓存重放期间锁定query/price及相关标签写入，再将EXCLUDE交给已有paged_exclusion。当前仍缺组合调度、真实sink导入、Frontier复位/距离代价/回溯提交和平台/板上；未宣称完整设备路由或加速收益。
