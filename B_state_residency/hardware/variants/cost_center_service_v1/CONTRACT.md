# Center distance service v1

独立服务连接已冻结的 `cost_center_step` 实际生成 RTL；不修改共享基线。
请求为4个u32（childX、effectiveY、centerX、centerY，低字先行），结果为2个u32（kernel status、distance，低字先行）。`rsp_status` 是传输/准入状态，和结果低字中的数值域状态分开：0成功准入，1无活动查询，2身份不匹配。数值域错误仍以 kernel status=1 返回。

接收时快照全部输入和 cookie/query2/price4/full version32；整个计算及回复背压期间保持忙，禁止下一请求。外部调用者必须同时持有所属设计/查询及完整版本的租约，直到回复退休；本独立模块不替外部控制器延长租约，也不识别没有输入的design_id。query/price/full version 或 active 在持有期间变化会锁死 fault，不能仅凭 rsp_status=0 消费已暴露的结果。

输入只有一个一周期读口。输出按地址收集，允许提前写或完成当拍双写；地址0为kernel status，地址1为distance，不能从端口号推断语义。seen检查包括完成当前拍。重复写、同址双写、未收齐完成、done/ready不同步、空闲或回复阶段的接口活动均触发停止。生成核正常完成为done/ready同拍。

超时默认1024运行拍，最后允许拍的完整完成优先于超时。abort、超时、协议/所有权错误均停止新准入且fault保持；已暴露回复稳定，可退休但fault不自行清除。没有AXI在途，此处恢复条件是服务与算术核同时同步复位，之后重新设置外部身份；不支持只复位一侧，也没有算术结果回滚承诺。busy在停止状态保持，故外部不得将其作为已经安全释放的信号。

验证入口：`scripts/run_cost_center_service.py <new-result-dir>`，随后 `scripts/audit_cost_center_service.py <result-dir>`。实际RTL重放110397冻结向量；独立mock覆盖同拍/提前写、快照、背压、重复/缺失/不同步事件、身份漂移、abort、16拍超时及最后拍完成。实际核另在120个偏移abort后共同复位并恢复正常调用。这些测试不证明与candidate/pager、post-prev坐标或成本23字producer已联接，不代表板上性能。
