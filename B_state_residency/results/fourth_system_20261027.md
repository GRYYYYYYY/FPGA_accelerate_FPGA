# 四路径G4发布与自然第四查询通过（2026-10-27）

详见同名JSON及hardware/variants/four_path_v1/CONTRACT.md。选定fourth_system_full_v2/pressure_v2，生产RTL逐文件SHA与此前三路径G3 warm相同，仅TB使用PATH_SLOTS4、156字镜像和新增实际激励。此前q1/q2、G3发布、q3第二owner-B错误和非冷warm恢复均保留；全部已有数值/路由/journal/恢复事件字段与12AXI原始前缀核对。

G3 warm恢复后context6/0/6、floor180329、三条有效路径/journal3。原生PC lease下累计writer重arm并把四条64B脏行从工作DDR复制到未使用的A bank：该区原保存G2，当前authority仍C bank G3。实际写和回读、完整146284032B图像独立核对。第72个authority读beat后的退休边界没有在途事务；全85个读beat按旧A=G2/新A=G4分别重放，未拿最终A图像解释旧读。

原生导出781标签/393页、三有效路径加空第四槽156字与query10字，在实际三方111共同发布沿切G3/CP19/J3→G4/CP20/J0。保持准备回复和最终回复时的旧身份/封锁核对，发布后拒绝旧G3 GET并从新A窗口读取目标及外来net。源路径CRC f00b72b4、query327d3916/floor180329；标签CRC full083ee4ad、pressure ae573141，流顺序不同但集合与CPU q3相同。

随后实际登记q4历史路径6954→990178→558358→265324→66893，仅导入元数据不补owner引用。原生ripup把990178 sole primary写为全零（refs1/occ1→0/0），另外两节点4/5→3/4；真实query180330/connection170791在第四槽搜索并提交回1/4/5。q1/q2/q3和节点558358外来net23916/ref1保留，不冷复位、不重装工作DDR。

两容量83poll/82expand/402candidate/231cost均逐项匹配独立CPU oracle；全部12AXI、31个物理owner record写、146284032B owner与G3/G4快照全量相等、全部781标签/393逻辑页/3MB物理标签页通过。q4新增baseline miss0，426条保守CPU闭包仅供审计、未预加载硬件。最终四路径CRC eec36b70、query bcf23ef5、floor180330/slots15/CP20/journal3；最终四路径没有再发布成G5。

结束4165462/4482678周期，q4从prepared到查询回复382627/449109周期，仅行为仿真，不是板卡时间或加速比。G4复制含重arm169/159周期，标签导出18417/18651周期；完整换代至发布19445/19602周期。

首个full_v1的生成器将checkpoint字符串替换误作用于查询序号，使两处期望变为190328，实际原生导出正确180329后触发TB断言。修正版仅改这两处断言；完整共有native事件/周期及12AXI原始前缀逐字节一致。首版作为开发失败归档，不是生产RTL反例。独立审计开发中还修正了AXI地址字符串8位/16位显示的比较，按数值比较后所有数据字节完全一致，未修改实验数据。

两个成功例与一个开发失败例均实际归档恢复并重新独立审计，audit逐字节一致；489文件源冻结results/fourth_system_sources_20261027。输入/组件四归档及34源文件冻结另见four_path_inputs_20261027.json。每轮收尾按已审计目录释放干净缓存，不删除数据。

尚未G4故障恢复、任意变价下标签有效性、持久化writer/认证/floor、全图baseline reseed、自然overflow新增/回收或当前完整层级综合时序/板卡收益。初始G1 clones/full baseline与历史路径元数据仍为外部可信输入。下一按four_path_v1/NEXT.md验证q4已释放最后owner后、commit前图R错误的G4原生三键恢复，不能直接套用共享引用案例。研究继续，goal active。
