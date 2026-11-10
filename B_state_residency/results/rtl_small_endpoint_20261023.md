# 小页完整端点先导验证

新增scratch_page_controller_small、queued_scratch_endpoint_small及memory_scratch_endpoint_small，保持独立冻结版本。32槽/8节点、21位page、72位cookie；命令FIFO有效宽度由233+TX+GEN增为236+TX+GEN，query_used仍4位，槽位标签与租约扩为32位。

Vivado/XSim2022.2先导通过221检查、36传输、8checkpoint、4tag回绕；runner69695及各阶段exit0。槽位0/8/16/31、高位页号1048676..1048679、query2/price9、offset0/7的五字段逐项核对，独立原始页字节一致。checkpoint检查内部排空/FINISH/保留回收/同query恢复顺序及期间host入口关闭。

manifest b5986230e9c6caeb0af111779ae5d3fd93972ff4e66ee6883a12d02900a69fec，final_audit核对源hash与生成器重建。此先导只有4个驻留页面、小位宽事务/代数，尚需32槽同时驻留、阻塞ACK/排空、负例变异、真实38轨迹、默认容量综合和时序。不能称完整小页设计已完成或有实测加速。
