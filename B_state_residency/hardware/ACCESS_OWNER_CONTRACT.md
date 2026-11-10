# 共享访问与真实设计占用联接（access_owner_v1）

`hardware/variants/access_owner_v1/access_fabric.sv` 在原access_fabric_v3基础上联接实际owner_state_store和owner_bridge。11类access动态请求中，kind4/6已由真实AXI占用存储返回；标签、图和坐标仍使用已验证的实际服务。Config/dead/static生产仍是外部fixture，完整search、真实设计引用导入/提交和板上未完成。

## 请求身份与映射

owner_bridge从内部dispatch接受kind4/phase5/node/net/cookie32/query2/price4完整身份。cookie是上层服务token，桥以同一cookie发raw store GET，并验证返回cookie。kind4使用raw will_overuse，kind6使用raw count；完整身份由桥快照并随服务响应返回，dispatch再次验证。源输入在接受后改变不影响快照。

接受服务要求decision_lock=1、pager active且query/price匹配，kind只允许4/6。请求期间lock丢失或query/price漂移、raw错误cookie、无归属raw响应、abort、raw fault、超时都会锁存桥fault。raw错误状态转服务status3；已发生fault后返回的正常raw结果标为5；非法kind1，错误活动归属2。服务回复已暴露后保持字段，late fault只提升fault。桥的错误回复没有撤销上层fault的含义。

桥是单请求，不另行复用或回绕token；上层access控制器管理服务token耗尽。raw store只有一条在途命令，cookie用于该命令身份验证，不提供跨未排空冷复位的旧消息隔离。恢复必须协调AXI和全部模块。

## 主机引用命令与整个child排他

新增host_owner_req/rsp转发raw GET0/INC1/DEC2，保存op/node/net/cookie，返回原raw status/count/occupancy/will。容量拒绝等raw逻辑错误可正常返回而不锁存桥fault；错误cookie转host status10并停止。host请求及回复退休前保持bridge_host_pending，禁止接收新的access child。

access_pending寄存器从child请求接受保持到最终回复退休。桥据此拒绝全部host owner命令，覆盖每次服务之间的HLS计算和最终回复背压，不能只锁单次kind4/6。host_owner_req_valid在空闲时优先阻止新的child；顶层同周期不会同时接受引用更新与判定。该所有权选择不使用含fault的busy，避免原v2已检出的组合环。

上层须保证图与owner区域属于同一设计、nodes配置一致；本版尚无跨区域设计标识或节点数一致性门禁。owner配置仅在没有child、桥在途命令或待接收主机命令时接受。access ready还要求owner已配置、配置回复已退休。原标签host OPEN/CP/CLOSE/IO仍按access_fabric_v3整child排他；它们不会清owner后备。owner字段存放在独立设计级区域中。

## 故障与后备

桥default整体预算1048576拍，不计最终服务/host回复背压。已捕获的raw请求VALID不因late fault撤销；接受后的raw事务由raw store继续处理/排空，其AXI VALID保持规则见[OWNER_AXI_CONTRACT](OWNER_AXI_CONTRACT.md)。若故障发生在raw接受前且raw已经停止，桥可能保持请求等待协调复位；外部必须观察fault，不能仅等待正常业务响应。

上层dispatch预算仍为目录规模加262144，整access预算8388608；合法长链可能先触发上层超时，已接受的只读owner查询仍可能在后端处理。系统终止应协调abort、总线排空和设计重载，不能仅凭上层错误回复就假定所有AXI已结束。本阶段实际错误测试明确等待raw_busy消失后才重载。

设计新加载显式初始化primary/pool/allocator，然后导入sink和已有路径引用。功能测试从fixture的occ/uses构造真实INC/DEC命令，在query外修改；这证明设备路径和生命周期，不代表已完成真实netlist的180326预引用加载器或路由提交器。每次CLOSE后执行GET验证owner仍与预期相同。失败后的整设计恢复显式重载后备，不能把query清标签当作修复部分提交。

## 验证范围

`access_owner_v3_20261024`：合成11664、真实512、单槽614；kind4/6共4970/59/249次实际查询。全部HLS状态转移、动态值、图/表/标签字节、所有主机引用命令、owner AXI字节、完整owner后备及其活动/空闲链独立核验。owner主机命令55248/2557/2963，判定期间host/config拒绝2114190/65553/130665拍；真实owner文件包含145424192B对齐primary区及独立pool/allocator。

`owner_bridge_v3_20261024`：受控raw后端15检查/12错误案例，验证完整快照、映射、cookie/status、owner漂移、非法归属/类型、超时/late abort、host逻辑错误和无归属响应；同一桥RTL在上述整合测试中连接实际AXI模块。

`access_owner_boundaries_v3_20261024`：完整默认163840帧/HASH18，4整合故障/5正常恢复，8次目录逐地址完整262144项清零；owner R错误、暂停AR时abort、owner回复暴露后abort、host B错误均传播并停止。最长实际服务等待262083拍；前置owner准备与后台目录清零重叠，所以它不同于旧独立cold测试的262129拍。清零计数是直接监测的工作量，服务等待只是剩余等待，不可混为一谈。

整合结构综合终态见[报告](../results/access_owner_20261024.md)。此前各组件更广泛的故障证据保留，本整合新增测试只覆盖列出的4种故障，不声明重新执行了所有旧故障组合。
