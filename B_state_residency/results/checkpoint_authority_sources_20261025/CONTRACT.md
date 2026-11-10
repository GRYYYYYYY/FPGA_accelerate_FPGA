# 版本化 owner 快照只读服务

`checkpoint_authority_reader.sv` 复用既有 `owner_state_store` 的 GET 校验路径，读取完整 primary/pool/allocator 图像。绑定 design64、checkpoint32、generation64、地址、节点/net 范围与 pool 容量；成功后本次生命周期不允许换绑。请求身份不匹配或越界在发 AXI 前拒绝，错误回复不提供 refs/occupancy；成功回复携带实际绑定身份。

`cfg_permit` 由调用方提供静止配置许可，不能替代系统级 lease。绑定只验证描述和基础配置，不扫描全部图像、证明真实性或冻结外部写入。集成方必须保证同代完整快照及读取期间不可变。generation 是逻辑身份，不是持久化提交协议、密码学认证或跨 cold reset 的防回放下限。

服务只发 GET；测试使用真实只读文件 AXI agent，并检查任何 AW/W offer 均失败。响应背压期间不能接新请求或重启。取消已暴露的 AR 必须维持 offer、接收 RLAST、退休内核和前端回复。安全 `rearm` 仅在配置许可、无取消、旧回复消费、实际 AXI 与内核退休后握手；保留所有身份与配置，清除故障暂态并私有 reset/reconfigure。成功重配前 configured=0/busy，禁止读入。接受 rearm 后立即清 stopped，CORE_RESET 屏蔽旧内核 fault，防止父协调器下一周期再次锁存旧错。新配置错误仍重新锁存。

独立组件验证：两份真实准备态均 9089009 节点，第二份包含 53734 overflow 记录；选择性 728 请求向量（含 58 overflow owner 查询）及 8 故障/重启探针，736 回复。错误身份含 generation 高 32 位差异。SLVERR、AR 停顿取消、回复背压、重启及配置拒绝有真实 AXI 证据。

恢复子系统验证：既有协调器 + 本服务 + 可写 owner 引擎，分别 journal 3/5 项真实 INC/DEC、overflow 与 primary promotion，首次实际 snapshot R SLVERR 导致 status6 且保留 journal；更高 version/query 的显式重试成功、修复 3/5 项、清 journal。live backing 在目标 reset 下保留。所有字节与 CPU owner oracle 独立审核；promotion 后编码可不同，owner 集合/引用数及 allocator 一致，未涉及记录原字节不变。

此子系统的 labels_done 明确由 mock 完成；未接完整查询 top、保存路径、标签/目录、设计缓存、价格/历史、query 序号/epoch/版本下限统一恢复。未证明未知页、真实价格变化、回绕、容量极限、耐掉电、板卡性能或 Fmax。已有全系统旧基线保持不变。
