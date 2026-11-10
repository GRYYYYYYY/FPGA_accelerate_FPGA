# 当前候选之后的G3发布要求（尚未执行）

本变体只计划完成实际owner累计覆盖/错误重arm/G3候选复制；共同发布必须另建隔离变体，不能把候选存在或manifest_ready称为CP19已发布。

1. 当前真实q2重试后store5/query3/price5、sequence180328、两路径；G2 CP18仍为authority。只在真实PC lease/control(1) flush/全部服务退休下生成G3 bundle。
2. runtime_label_snapshot当前TB硬接query1/price3，只适用于G2源。G3须从实际活动上下文选择3/5，枚举当前目录并实际DDR读；应得781条/393页，但只能以真实导出为准。源CRC从原生流算出，不手填答案。不要复用旧777流冒充完整G3。
3. 原生path controller导出两槽78字，query controller导出原始10字并选择新generation 0x100000003。核对floor180328与源上下文、实际CRC；不能使用旧G2 path/query镜像。源price/history字节始终不变。
4. 新候选owner在0xc000000000、pool c008aaff40、allocator c008b81dc0，容量53734；独立内存窗口必须读这份实际硬件复制的g3.bin。G1/G2窗口维持原字节，source clone只在启动提供一次。
5. publication JP描述符改为G3/CP19，authority/coordinator/config由真实三方屏障准备并同拍提交；必须逐项核对owner receipt design/baseline/generation/checkpoint/destination和label/path/query源身份，且全部真实回执/服务退休。prepare与held回复期间旧G2/CP18保留；publication不应因自己的busy失去已经选定的manifest许可。
6. 发布后通过原生AP检查G3 owner refs339193=1、990179=2、558358=4（另一net23916=1）、265324=5及occ1/2/2/1；旧G2 generation请求拒绝。实际owner图像与运行状态逐字节一致，旧G2图像不变；query导出generation变更而floor180328不回退。
7. 没有自然q3 CPU prepared-state/oracle时停留在CP19发布证明，不重复已消费180328。完整G3 fault/warm、连续自然q3、实际overflow新增回收、无限脏表、运行中全图baseline reseed、持久化认证/floor与板卡性能均须另证。

## 发布接线必须处理的健康信号问题

当前候选TB的g3_healthy使用system.pc_safe，只足够生成候选。query root的pc_quiet包含!as_cfg_lease和!k_busy，authority/config准备自身会临时关闭pc_safe；新writer在source_healthy消失时撤销receipt。因此不能直接把当前g3_manifest接进G3 JP然后宣称可发布。下一隔离变体须分离“允许开始copy/rearm”的真实管理员资格与“源仍健康且不可变”的持续证明：仍保持PC owned、物理退休/协议检查和普通工作封锁，不能因自身authority准备busy撤销已经完成的owner receipt；也不能将真正source AW/错误忽略。应保留该接线的实际失败反例和修复验证，尤其held prepare及最终commit边界。

持续source_drained目前也会撤销owner receipt；G3发布接线须核对其是否包含authority自身逻辑busy。允许copy/rearm前的全局退休条件与发布过程中的源owner不可变证明应分开验证，不可仅把健康/退休输入固定为1。

代码核对已确认residency_system的f_backend_idle包含as_retired，因此authority准备时的自身busy确实会进入当前source_drained。此为静态接线发现，不是已经运行过的G3发布失败结论。下一轮应保留真实发布负例，再决定仅将开始许可/临时busy与持续receipt失效原因分离的最小修复。
