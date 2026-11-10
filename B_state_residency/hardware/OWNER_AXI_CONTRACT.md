本独立后端已进一步接入共享访问，完整身份桥、查询后持久性及整合结构证据见[ACCESS_OWNER_CONTRACT](ACCESS_OWNER_CONTRACT.md)。下文保留独立AXI阶段接口与验证范围。

# 设计占用AXI服务（owner_axi_v1）

`hardware/variants/owner_axi_v1/owner_state_store.sv` 已实际实现[占用存储布局](OWNER_STORE_CONTRACT.md)的GET0/INC1/DEC2，包括动态链表、主owner晋升、前驱修复、free链回收和共享pool容量检查。它独占三个后备区域；尚未连接access_fabric kind4/6身份桥，不含history或metadata生产。

## 配置与所有权

一次cfg握手保存primary/pool/allocator三个64位基址、nodes32和capacity32。三基址须64B对齐，primary非空；每个区域按逻辑16B记录向上分配到64B，范围不能越过64位空间或相互重叠。capacity可以为0，此时仍可存主owner，再加其他net返回容量错误。cfg_status0成功、1非法，cfg响应背压时字段稳定；配置成功后不能热改。

新设计由外部明确清零三块后备并重放loader预引用；模块没有标签OPEN/CP/CLOSE清表功能。冷复位只清模块控制/配置，不清后备，且要求系统协调处理旧总线事务。半提交错误后不得仅复位该控制器并沿用不完整记录，必须隔离并重新加载设计。

req输入op3/node32/net32/cookie32，单命令在响应退休前持有模块。net支持0..INT32_MAX，node必须在配置范围；同net引用与不同net占用均按规范保持。rsp回显cookie、status4、操作后count32/occupancy32/will_overuse；正常GET返回当前值。请求中的完整query/price/kind/phase/token身份还需后续桥保存和验证。

整个access child判定期间需要上层禁止设计引用修改，不能只在某一次kind4/6请求期间排他；当前独立模块不接受该child所有权信息。当前后备仅允许本模块写入，不能有其他主机并发改变链表或allocator。

## AXI与提交

AXI512、64位地址、ID0、单64B拍、INCR、LEN0/SIZE6。记录读取按地址低位选择16B lane。每次记录写用恰好16个WSTRB，其他记录和区域填充字节保持；AW/W独立握手。构建完整计划后才开始写，一条命令最多4项写；正常成功响应只在最后一项成功B后出现。

链表在计划前完整检查：活动记录字段、范围、占用数和allocator活动数边界，以及与primary或先前条目的重复net。用前缀重读检查重复，无按pool容量分配的片上目录。长链检查会增加AXI读取，尚未优化吞吐，也没有将C++模型的计数结果当作已测硬件周期。

错误status沿用0成功、1范围、2减空、3引用65535耗尽、4不同net占用65535耗尽、5pool满、6结构损坏、7非法op；8留作CPU规范的过期计划状态，在该单请求RTL中不返回。新增9已归属R/B错误或身份/RLAST错误，10无归属响应/内部协议错误，11超时，12abort，13未配置。逻辑错误1/2/3/4/5/7/13在写计划发出前返回，存储不变，可以接后续命令；6及9..12锁存fault并永久拒绝新命令，等待系统恢复。

默认整体预算1048576拍，从req接受到正常/错误响应暴露；最终响应背压不计入预算。功能使用该默认，故障测试以同一RTL的2048参数测试实际超时。合法但很长的链也可能超时，不能将CPU支持的65535-net边界理解为默认预算内的硬件完成保证。超时与最后成功B同拍时错误优先，即使物理数据已经更新也停止设计。

fault到来时，已经暴露的AR/AW/W保持VALID和字段，直到握手；已经接受的当前单拍读或写事务继续排空，但不再发起后续记录操作。错误rsp可先于排空完成出现，busy在排空期间仍保持；外部不能因读到错误rsp就撤掉AXI对端。若对端始终不接收，fault和错误rsp依然可见，控制器保持当前VALID等待系统隔离/复位。

已经暴露的rsp字段在late abort或无归属响应时保持稳定，只提升fault；消费者须同时检查fault0。发生B错误前的写可能已经物理可见，模块不提供回滚。若slave违反ARLEN继续发送畸形多拍流，单拍排空测试不证明能够恢复该流，系统仍需隔离和协调复位。

## 验证

`owner_axi_v2_20261024/source_bound_audit.json`：13549条命令、79645读、7083写/B，1146826仿真周期。9043成功、2549减空、1944容量拒绝、10引用上限、2范围和1非法op。209次四记录提交；所有正常/逻辑错误结果、B计数、背压稳定性与测试过的CPU布局规范一致。实际所有R/W字节及完整16384B窗口独立重放通过，包括>4GiB基址和32位进位、间隙及相邻记录保护。

`owner_axi_boundaries_20261024/source_bound_audit.json`：22故障/22显式重载恢复、97项检查、8857周期；6条R/B状态/身份/RLAST错误、6种记录/链表损坏、AR/AW/W暂停及计划阶段abort、AR超时、最后B超时同拍、两种late fault和idle无归属R/B。首次/部分写入错误、VALID保持、最终响应字段稳定均有实际RTL检查。

半提交用例在第二B失败：pool和primary已改，allocator仍旧，后续第三写未发出，fault停止。所有恢复都显式重载设计后备，不代表只清controller就能修复写入。

完整默认模块实际综合4866LUT/3081FF/252CARRY8，零BRAM/URAM/DSP/latch/组合环。80.646s、checksum899b478、history96，34845B完整收据与DCP保留。891输入/806输出没有平台delay，HD.CLK_SRC未设；未布局布线，不代表板上时序或速度。
