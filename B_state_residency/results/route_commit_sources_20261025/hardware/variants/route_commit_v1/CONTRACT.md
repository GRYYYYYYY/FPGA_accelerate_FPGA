# 可综合路径保存/回溯/提交控制器 v1

`route_commit_controller.sv`是独立可综合RTL，不修改现有search/label/owner基线。两个路径slot，默认每slot最多32个内部节点；仿真用8，上界溢出测试用9内部节点链。一次请求由外部排他lease覆盖至响应退休；query2/price4/version32/design64完整上下文被锁存。

op0 TRACE_COMMIT：仅可写空slot，从sink实际标签读取prev，检测重复内部节点/回到sink、未到source已遇-1、长度溢出、缺失/坏标签。sink必须target=1且visited==req_sequence；source必须prev=-1。整条链通过后才逐个内部节点发送owner INC，等待匹配cookie/status成功回复后推进；源/汇不计数。最后成功ACK后发布slot_valid及保存的net/source/sink/design。空路径同样可发布/拆除。

op1 RIPUP：必须slot有效且net/source/sink/design匹配，使用已保存路径发送owner DEC，不读取可能被后续查询改写的prev。slot最后成功ACK后才清valid。价格/version可在不同操作间改变；设计身份不可绕过，外部仍须保证这些slot和同一权威owner backing对应。重复提交、空slot拆除或身份不匹配为可恢复status1，无后端请求。当前只处理真实sink到source、无altSink的内部节点规则；替代sink/其他端点提交范围尚未扩展。

接口：label为注册型只读native160 payload；owner为注册型串行INC/DEC，cookie回显，status0表示已提交。每类最多一挂起请求，禁止未经协调并发写同一owner或prev。必须通过适配器连接真实服务，不能把本模块lease直接等同search decision_lock，因为搜索外host owner操作要求原decision_lock已释放。

故障：abort、超时、完整上下文漂移、坏/缺失标签或错误owner回复会锁定停止。SEND中的VALID及字段不撤回，已发请求仍等待被接受并排空对应回复；排空前不发完成响应。rsp_acked仅表示cookie/status确认成功的修改数，不是物理副作用上界；坏B/错误回复或晚到取消可能已经修改owner。无rollback/热重试。调用方需阻止新查询并协调重置/从权威checkpoint恢复或修复，不能仅重发请求。响应背压时字段稳定；已成功响应期间晚到上下文变化会锁fault但不修改该响应，调用方还需检查全局fault。复位只可在协调后端/在途事务后执行。端点永久不回复时保持排空等待而不是错误释放lease。

资源：周期检测并行比较已保存节点，路径存储在寄存器，容量不是任意长connection路径；32内部节点之外明确拒绝。本轮OOC仅综合，无时钟/I/O约束、布局布线/Fmax或整机可行性证明。

验证：真实首/同网第二query的两组8节点native payload从冻结CPU快照逐位派生，注册mock label服务按控制器请求返回；mock owner按实际请求增减引用。25项检查包含双slot共享、重复提交、net/design身份、保存路径ripup不重读标签、环/源prev错误/缺失/坏状态、容量上界、坏cookie后partial ACK、label/owner背压取消且不撤VALID、超时后晚到回复排空、query/price/version/design/active/lease漂移、空路径、响应持有期间迟到漂移。未接真实pager/owner AXI或整条search。后端行为仿真不是整机验证。
