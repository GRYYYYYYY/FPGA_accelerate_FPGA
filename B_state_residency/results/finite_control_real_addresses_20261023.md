# 有限控制报文：完整真实地址回放

完整回放及独立终态绑定/计数审计通过。1113间隔查询+19超大查询，共1132查询、16151535真实TLD地址访问，无截断；值是合成sequence，不是实际距离标签。4槽×64节点，18位page ID、16位transaction/generation、2位query、2位fence tag，数值price固定0。

| 组 | 查询 | 访问 | 中途恢复 | 排空 | 控制请求包 | ACK包 | 重复ACK | tag回绕 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| interval_sample | 1113 | 2399968 | 0 | 1113 | 2226 | 3339 | 2226 | 278 |
| large_query_tail | 19 | 13751567 | 63 | 82 | 164 | 246 | 164 | 20 |

每次fence通过3字节opcode/tag请求与ACK队列，注入重复请求及重复ACK；peer仅request/work空时ACK，host仍等待控制队列、数据完成、本地bindings和payload全部清空再复用标识。合计1195次fence、2390请求包、3585ACK包（含2390重复ACK）、298次有限tag回绕。全组边界探针skip=0。63次真实长查询中途恢复从实际resident+backing导出检查点，不用oracle恢复。

命中、写回、换入、查询/访问数、checkpoint/fence和stale计数逐组完全匹配已完成的finite_page_fast回放；控制逻辑未改变数据事件路径。审计重验源/输入哈希、源码快照、终态和完整访问数量、fences关系、重复控制计数与tag回绕。oracle逐读、恢复前/最终全映射验证由冻结driver执行，独立终态审计不重新执行1600万事件，因此不是第二套值状态机证明。

控制专项及回放fixture全套83项检查已通过，证据fence_control_20261023T015957Z。模型输入/源码保留冻结。performance为空，不把解释器运行时间、事件数或编号分配器优化当作真实DMA/FPGA性能。

未完成边界：所有延迟包必须存在于已建模闭合队列，单owner在fence期间停止旧生产者，peer去重状态不丢失；真实隐藏链路旧包、丢包/超时重传、设备复位以及控制信道物理有序隔离都未证明。同一旧ACK在tag回绕后与新ACK不可区分，有限tag本身不提供无限迟到安全。后备仍是按QueryKey隔离的Python字典，不是实际DDR地址和字节预算；未验证物理地址提前复用、固定宽度页数据、内存一致性或RTL。设计级history/占用与真实价格变化未包含。

下一步优先补有限后备页地址分配及字节容量/租约：把当前逻辑命名空间映射到有界页帧，旧query的DMA/payload未排空时不得将物理地址分给新query，容量不足明确背压；先用对抗值检查，之后才确定实际设备接口或可综合实现。既有真实路由CPU基线保留，不能以封闭协议回放替代实际硬件验证。

证据目录：`finite_control_real_addresses_20261023T020009Z/`；复核：`python3 scripts/report_finite_control.py results/finite_control_real_addresses_20261023T020009Z`。
