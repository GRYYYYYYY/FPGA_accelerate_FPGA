# 排除接口到原生标签端点的接入约束

源绑定检查见results/exclusion_label_boundary_20261024/manifest.json。这是原始静态接口核对。后续适配器v2已连接原生端点RTL验证，见[实验报告](../results/exclusion_label_adapter_20261024.md)与[同拍故障修订](variants/exclusion_label_v2/REVISION.md)；HLS调用收集器/页解析器仍未接入。

- phase1/4读取prev，原生READ操作2、字段2，对应rsp_payload[95:64]；phase2/3读取visited，字段3，对应[127:96]。原生READ返回整条记录，field不授权改变其布局。
- 当前8节点页：page=node>>3，offset=node&7。必须先检查node<2^24，再转换到21位page；HLS控制器允许的INT32_MAX范围比端点更宽。已验证实际图9089009节点可表示。
- 边generation32标识排除上下文；页binding generation16由槽映射管理，不得截断边编号后直接用作cmd_generation。query/price/slot/page/页绑定编号共同授权读取；边编号/phase授权将读回值送回排除控制器。
- created是CPU getNode依据的设计级节点状态，由getOrCreate更新；rsp_present是当前绑定查询页中是否写入过标签的状态。两者不能互换，图flags.createdAtInit也只是初值，不能替代运行时created。
- native rsp_present=0返回全零payload，与real_field_values来源resident_zero模型一致。不能自行将零prev改成-1；-1是显式写入时的0xffffffff。原始dense CPU默认标签和本驻留查询模型并不相同，适配后的整条搜索验收应绑定同一驻留模型的查询、标签初始化及created/缓存策略。
- 页未驻留时，槽管理器须完成合法WB/RELEASE/BIND/RF流程后才提交READ；当前HLS排除组件不承担自动分页。请求期间保留边上下文与查询语义；禁止slot被无关所有者换绑后复用旧响应。
- 端点错误/STALE/FAULT不能转换成数值零或成功RESPONSE。尚无单边取消协议，需由后续查询协调器决定清理/回退；冷复位必须排空旧消息，不能当热恢复使用。
- HLS标量接口要收齐一次调用的输出并捕获ap_done，再提交下一条；各输出ap_vld是独立信号，适配器必须证明不会混合两次调用结果。

后续集成测试需要同页/跨页父子节点、空记录与显式prev=-1、同编号重复phase、旧边响应、换绑/换price拒绝、读错误及背压；同时保持getChildren首次过滤/缓存和created/deadEnd副作用。现有全38端点回放和独立HLS cosim不能替代这些测试。
