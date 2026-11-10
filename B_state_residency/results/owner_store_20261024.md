# 设计级占用存储布局验证（2026-10-24）

已实现可执行的主记录＋可回收overflow池规范，并通过原函数差分和完整真实事件重放。接口、位宽、错误及提交边界见[OWNER_STORE_CONTRACT](../hardware/OWNER_STORE_CONTRACT.md)。当前为CPU存储规范，AXI RTL及access_fabric真实owner后端仍待实现。

主记录16B/node保存owner、16位引用、16位不同net占用及链表头；共享pool16B/entry保存其他net引用和next，allocator16B保存未分配游标、free链及活动数。同net共享不重复计占用，主owner删除后晋升一项，删除空overflow条目后回收并可用于别的节点。容量不足显式失败，不将当前样本的占用峰值4硬编码为每节点4个net。

`owner_store_v2_20261024`验证通过：

| 项目 | 已验证结果 |
|---|---:|
| 原函数随机增减 | 200000 |
| 原函数逐net查询差分 | 3200000 |
| 完整真实引用更新重放 | 18515060 |
| pool容量 / 活动峰值 | 65536 / 53734 |
| 逻辑16B写计划 / 单命令最多 | 18940411 / 4 |
| 最终主记录全字节核验 | 145424144B |
| 最终pool全字节核验 | 1048576B |
| allocator核验 | 16B |
| 最终活跃节点 | 722477 |
| 最终overflow活动条目 | 0 |

独立审计从原始事件取得每个节点的最终owner/引用，在真实已收敛单owner终态逐一检查全部主记录；遍历free链确认所有已分配pool条目均可达、无重复，并检查未分配区域全零。真实重放逐命令比较count/occupancy/过用结果，测试台记录和统计不作为最终文件的唯一预期来源。

边界包括主/overflow引用65535后拒绝递增、65535引用精确晋升、65535不同net占用后拒绝新增、256-net未截断占用、pool耗尽后保持原存储、主owner删除回收及跨节点复用、减空、非法node/net/op、旧计划/被修改before拒绝、generation耗尽及损坏链/保留位。UBSan无错误。

原方法来自冻结原始main.cpp，仅提取count/promotion/hot同步/inc/dec作为对照。首次`owner_store_20261024`因测试fixture没有定义原HotExpand类型而编译失败，没有进入验证；v2增加类型别名，并补齐完整occupancy等边界，原失败源码/日志保留。

新布局可选择与原unordered_map不同的主owner晋升顺序；支持域内所有net的可观察计数一致。对原uint16回绕或更宽overflow引用不作等价声明，超出65535引用显式失败。模型prepare不修改存储，commit校验before和generation后整体应用；实际总线部分写入失败不能由此推断可回滚。

manifest SHA256 `6b2b7ce7d9a789f0c1c03d8a777e6d704451eeca8702acfbfb74b6b9f83ff9a4`，独立审计SHA256 `ebe953e157553db4af13226dcdedc866c9a012529c141b25d6d3f4dcfd2aedfc`。exec97365和50389均已终态，无本阶段在途作业。

后续直接实现该布局的实际AXI事务控制和故障停止，正常结果必须等待最后成功B；然后接kind4/6完整身份桥，替换共享访问模块当前模型。设计加载预引用和查询标签独立生命周期必须保留。本结果未证明硬件综合、真实AXI流量或FPGA加速。
