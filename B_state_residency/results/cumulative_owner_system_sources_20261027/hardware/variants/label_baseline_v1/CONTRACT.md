# 全节点不可变标签基线与原生读取器

初始CPU prepared-state每节点44B，提取u32字段[0,1,3,4,5]，原位保持距离位模式、sequence、previous pointer和flags；追加12B零，形成32B记录。节点数9089009，总文件290848320B（末尾空半beat）。构造器不接受未来访问列表。独立审计逐条比较完整原CPU记录，源SHA匹配原CPU已审计manifest。

label_baseline_reader配置base/epoch/count；仅空闲时接受配置，外部cfg_permit负责真实租约/上下文授权。错误配置返回status5（未许可）或2（布局），原绑定保持。请求必须匹配非零配置epoch，节点越界status1，无配置/旧epoch status5，均不发AR。请求锁存后不再依赖外部请求/配置引脚。每个合法请求实际读取一个64B beat，根据node奇偶取对应半拍160b，检查96b padding及flags高24位。R错误/错误ID/非last返回3，格式错误4，失败载荷为零。回复背压时身份/载荷保持。无AXI写端口。

选定label_baseline_unit_v1测试894个真实节点，其中72个在旧822闭包之外；实际897个AXI读取包括一次R错误、一次格式破坏和一次原配置保留后的重读。15010项TB检查、4528个配置/业务回复保持周期。独立审计重放每个AXI地址/字节与每个业务回复，并再次对完整9089009条基线做CPU映射核对。未知页miss尚未接入manager；完整系统仍用CPU未来闭包，不能声称已移除依赖。

复现：先prepare_label_baseline.py CPU初始节点文件 NEW_IMAGE；运行run_label_baseline.py NEW_UNIT（当前runner选择相邻label_baseline_image_v1），再分别audit_label_baseline_image.py IMAGE、audit_label_baseline.py UNIT。所有脚本位于scripts。不要覆盖选定结果。协议仅单beat、单在途；无取消/持久化认证/时序或板卡结论。后续见NEXT.md。
