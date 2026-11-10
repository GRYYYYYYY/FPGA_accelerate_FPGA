# 设计级状态与持久首次过滤缓存

实现 `variants/design_store_v3/design_state_store.sv`，v1/v2/v3 的 RTL 和 oracle 字节完全相同；v2修复TB保留字任务名，v3补充B应答逐笔记录及发布等待断言。当前为独立实际AXI服务，尚未接图读取器/children HLS/paged exclusion。

## 生命周期与存储

一次不可变配置：base64（64B对齐）、N32（1..2^24）。分配 `align64(N*16)` 字节并在**设计开始时清零一次**；当前真实图为145,424,192B。物理后备区是权威持久状态，无在片缓存或淘汰，因此不存在驻留淘汰后重新过滤的正常路径。没有query/price/checkpoint端口，查询切换不清除记录；不能将这份设计级存储当成查询标签池。

配置成功后锁定至协调冷复位。cfg status：0成功、1对齐错误、2节点数/65位范围计算失败；允许末字节恰为2^64−1。这里只核对地址范围，不能检查主机是否实际分配/清零，上传器尚未实现。所有访问者必须共享唯一串行服务所有者，禁止CPU或其他AXI主设备同时改写记录。

每节点16字节，小端：

| 字节 | 内容 |
| --- | --- |
| 0..3 | flags：bit0运行中created增量，bit1dead，bit2cache_valid，bit3design_sink；其余0 |
| 4..7 | 已发布原始CSR度数raw_count；尚未发布时0 |
| 8..11 | 已发布原始边位置keep_mask；尚未发布时0 |
| 12..15 | reserved，必须0 |

缓存以**原始边位置**表示；重放按CSR位置递增输出置位的child，所以重复child与原顺序保留。当前容量32个原始位置；真实图全量核验max_degree18，超32的CLAIM在发AXI前拒绝。泛化更大度数必须增加表示或外置位图，不能截断。cache_valid单独区分未构建和已发布空缓存。图及节点编号在同一设计生命周期不可改变。

本模块的created是运行增量。最终 `created = raw_graph.flags[0] OR store.flags[0]`，不要漏掉初始创建，也不要用查询label present替代created。design_sink需由真实设计目标端点表在搜索前通过SINK初始化；不是本轮已完成的输入适配。dead谓词还需图type/flags及sink信息，由组合层按原函数计算。

## 命令与所有权

所有命令使用 req valid/ready，op3、cookie/owner/node/arg各32位；响应status4、cookie/flags/count/mask各32位。单条命令串行；响应背压稳定。结果须在status0且fault0时使用。响应cookie回显，调用方负责完整服务归属与命令序列校验。

| op | 动作 |
| --- | --- |
| GET0 | 返回当前记录；无隐式创建 |
| CLAIM1 | arg为真实raw_count，owner必须非0。valid命中返回已发布记录，不取得claim；count必须与arg一致。miss锁定owner/node/count，清空局部keep_mask |
| CREATE2 | 幂等设置created增量，保留其他状态和缓存 |
| DEAD3 | 幂等设置dead，保留其他状态和缓存 |
| EMIT4 | arg为原始边位置，须严格递增且小于claim_count；在局部claim_mask置位，不读写外存 |
| PUBLISH5 | 重读父记录以保留构建中更新的created/dead/sink，写入valid/count/mask；成功B应答后释放claim并返回 |
| SINK6 | 幂等设置design_sink，仅无活动claim时可用 |

除CLAIM和EMIT外，arg必须0。无claim时GET/CREATE/DEAD/SINK要求owner0；有claim时业务命令owner须匹配当前claim_owner，EMIT/PUBLISH还要求node为claim_node。活动claim下新的CLAIM返回BUSY；无claim时EMIT/PUBLISH拒绝。SINK不允许插入活动构建。EMIT位置不能重复或倒退，但重复**child ID**在不同原始位置上合法。

CREATE/DEAD/SINK已有相应位时只读不写。CREATE/DEAD也允许针对已经发布缓存的节点，不改变缓存；父节点自环或同一64B内多个节点的更新不会覆盖其他记录。每次写仅16B有效WSTRB，AW/W独立握手，读取当前父记录后再PUBLISH。

claim_owner由外层扩展事务分配，不一定等于HLS generation：CLAIM必须先于首次构建START，HLS generation在START后才获得；组合层需维护二者关联。miss后必须保护整个构建，缓存hit直接重放位图，不运行EXCLUDE/HLS构建状态机。本服务没有独立的epoch/owner防重放计数器，只有单活动owner校验；外层负责编号唯一性、过期消息隔离和禁止跨冷复位残留命令。

## 提交与故障

AXI地址64位、数据512位、固定ID0/单64B拍。读对齐的四记录行，写只对目标16B置WSTRB；每个修改命令先读该记录，等待AW和W都被接受，再等匹配B。操作没有重试或提前成功。PUBLISH的valid位可能在物理内存中先被写入，但在成功B之前claim不释放且不允许其他访问者使用；这要求严格唯一所有者。

| status | 意义 |
| --- | --- |
| 0 | 成功 |
| 1 | 未配置，无AXI |
| 2 | op/node/arg/degree/位置非法，不推进 |
| 3 | 已有claim，拒绝另一个CLAIM |
| 4 | owner/父节点/阶段所有权不符 |
| 5 | RID/RRESP/RLAST/BID/BRESP错误，锁存fault |
| 6 | 记录保留位、count/mask/valid不一致；命中count不符；PUBLISH前发现外部已发布，锁存fault |
| 7 | 活动命令期间出现无归属R/B，锁存fault |

status1..4为可恢复请求拒绝；5..7停止。无归属R/B出现在空闲或已提供响应时同样锁存fault，但不会编造/修改业务响应。所有错误响应的flags/count/mask为0；fault后保留活动claim及局部位图。已提供的成功响应后来遇fault仍保持，调用者必须同时查fault。

**B错误不保证物理写入没有发生。** 验证模型特意先写字节再回错误，独立审计确认该情况；此时控制器保留claim、停止、绝不报告发布成功。禁止直接重试PUBLISH或重新运行过滤。已发生CREATE副作用不回滚，重做过滤可能改变结果。当前恢复策略是终止该设计运行，协调所有总线/上下游后重置并从新的已清零设计状态重新开始；尚未实现中途日志恢复。

协调冷复位只清模块局部状态，不清外存。只有在所有命令退休且无未完成claim、总线旧消息排空的安全边界才可重新配置同一后备区继续读取已提交状态；这个安全边界的完整图/搜索状态恢复仍由外层负责。本模块不支持热取消、超时、跨复位旧消息隔离、多主一致性或并发claim。

## 验证与接入

`results/design_store_v3_20261024`：98893正常命令（4523真实CSR父节点的选定服务操作，加一组人工degree32边界），68287逐笔读/17821逐笔写及B顺序核对；4524发布与命中、890空缓存。额外一次安全冷复位读取，总AR/R68288。初始145424192B零文件及全部最终字节均独立核对。17故障、35故障检查，AW先/W先/同时三种接受顺序覆盖。过滤保留决策是测试输入，不是实际EXCLUDE结果；不能称为完整getChildren联调。

下一步：外层先用graph META获得count/属性，CLAIM取得hit/miss。hit按位图重放原始CSR；miss进入children_build_engine，并让NEXT/CLASSIFY/CREATE/DEAD/EMIT/PUBLISH调用实际图/设计服务，EXCLUDE接现有paged_exclusion。构建从CLAIM到结果/重放退休整体锁定query/price及相关标签写入；还需导入design_sink并合并初始created。图访问和设计存储采用独立AXI端口/窗口，平台聚合留给后续。
