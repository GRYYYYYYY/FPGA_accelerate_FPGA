# 排除标签读取适配器 v1

仅一个在途读取，连接排除控制器的逻辑标签请求与原生 READ=2。这里不包含 HLS ap_ctrl_hs 输出收集器、页解析器/自动换页或完整搜索调度器。请求携带 node32、edge generation32、phase32、query2、price4；拒绝 node>=2^24、generation=0、phase 不在1..4。

合法请求先发 resolve(page=node>>3, query, price, generation, phase, token)。解析器回复须完整回显身份，并给出 slot5、binding generation16。token 是适配器独立的单调事务编号，不得截断边编号当页编号；参数 TOKEN_BITS 只允许1..32，生产32，缩位测试3。编号耗尽拒绝新合法请求，不回绕；非法请求不消耗编号。

解析器必须持有查询/页租约直到读取回复退休；未驻留页需由解析器完成 WB/RELEASE/BIND/RF。v1 的测试解析器只提供预先驻留的映射，不能据此声称自动分页。原生端点仍独立验证 slot/page/query/price/binding generation；换绑时返回错误。原生通道须由外层独占或由保存事务归属的仲裁器提供，不能混入主机响应。

READ 的 offset=node&7；phase1/4读字段2(payload95:64)，phase2/3读字段3(payload127:96)。保留原始32位值与 present，空记录0和显式prev=-1不能混同。present 不表示设计级 created。

回复 status：0成功、1非法请求、2解析器错误、3解析器身份不匹配、4原生错误、5服务故障、6事务编号耗尽；service_status保留解析器/原生4位状态。错误回复value=0仅为清洁输出，**不是成功标签值**。只有 status=0 且 fault=0 的回复可提交 HLS RESPONSE；协调器负责其他状态的查询失败/回退，组件不提供在线取消。

两个服务均使用时钟同步握手，回复最早在接受命令后的下一拍有效，恰好一次。身份错配、非等待阶段出现服务回复、native_fault 都锁定 fault，拒绝后续请求，直至协调冷复位。fault 是全链路中止：尚未接受的服务请求可以撤销，已发出的请求不得再被当作新任务。普通背压下valid/payload保持；已提供的最终回复即使随后fault也保持不变，接收方必须同时检查fault。复位需要外层排空旧回复并同步重置服务，不能将本模块单独复位作为恢复方案。无响应超时归外层监督器处理。

验证范围：连接冻结 sparse_records 原生端点，生产16位binding及16位record epoch；小目录32帧不执行外部AXI。覆盖32槽×8偏移×4阶段、零/显式-1/高位visited、不同页与编号、错误页绑定、换绑/换query或price、解析器错误/错身份、原生错误、服务中止、重复回复、背压、3位真实token耗尽。故障注入是测试shim，不能替代AXI服务自身已有验证。这里不宣称完整路由等价、自动分页正确性、物理时序或板上性能。
