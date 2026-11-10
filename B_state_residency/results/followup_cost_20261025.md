# 后续查询完整成本与过滤验证

真实logicnets query2和iteration2准备态，恢复实际Router搜索并只读导出成本/State表。九份快照/事件保持原采集逐字节相同。独立验证全9089009节点history、256价格值、27960 net成本记录、180326 CPS1连接记录，以及每次push的23输入和5个binary32成本结果。

| 指标 | 同网query2 | iteration2 |
| --- | ---: | ---: |
| 成本调用 | 122 | 421 |
| 同网共享引用成本调用 | 7 | 106 |
| 从overflow查得本net引用 | 0 | 10 |
| history>1成本调用 | 0 | 26 |
| 最大本net引用数 | 1 | 166 |
| expand / warm hit | 42 / 34 | 170 / 170 |
| created新增 | 20 | 0 |
| 判定candidate | 176 | 849 |
| 保守标签导入记录 / 8节点页数 | 194 / 75 | 822 / 403 |

独立过滤按已保存warm children直接重放；冷缓存才执行原CSR过滤/创建。候选visited、access、target、EARLY及全图created转移与真实事件相符。完整CPU heap审计来自已通过的capture审计。独立binary32重算没有以CPU结果回填预期成本。

两份followup_q2_inputs_20261025.json / followup_iter2_inputs_20261025.json绑定warm持久图像和本轮成本/State图像，验证同一base审计、history/价格完全一致，并显式使用warm layout的owner_pool_capacity覆盖cost-only layout的旧占位0。清单给出所有region文件、字节数和hash。CPS1使用当前query权重，非不同connection各自prepare后的权重表。

范围：没有实际AXI/RTL导入、多query控制器、硬件backtrace/owner提交或未知页初始化。native160保留完整旧visited/prev，32bit搜索sequence与2bit存储epoch是不同字段；cost_label_commit已有独立req_sequence，不能把sequence180327截断为epoch。标签读闭包仍由CPU事件推导，不能称未知工作集解决。既有first-query默认实现保持不变。

来源固定followup_cost_sources_20261025；主要脚本prepare_followup_cost.py、audit_followup_cost.py、verify_followup_filters.py、bind_followup_inputs.py。纯CPU算法/格式检查，没有启动Vivado或HLS流程。

四份成本/过滤归档已实际移走原scratch后恢复，逐文件hash核验；恢复后两成本审计和两输入绑定清单重建逐字节一致。收据followup_cost_restore_20261025.json。run.py check和四脚本语法检查通过；check不替代功能证据。
