# 真实准备态持久状态导入

`encode_warm_state.py BASE OUT`仅导出准备态持久子集，复用现有design16B、owner primary/pool16B、allocator64B以及native160标签导入布局。不是完整query硬件输入，也不改变现有首次查询codec。

- design flags bit0运行created增量，bit2缓存valid，bit3设计sink；raw_count/mask为原CSR范围及位置位图。按CSR递增位置重放必须逐字节恢复CPU缓存child序列，空缓存仍valid。遇到重复child ID时取最早可匹配位置（CPU快照未记录原始位置），保证有序child序列，不宣称恢复不可观察的原始位置身份。度数超过32、缓存不是CSR有序子序列、mutable type无法由静态图表示时拒绝。当前profile prune关闭，未编码deadEnd，不能用于开启prune的配置。
- primary为net+1、refs低16/不同net occupancy高16、head+1、0；pool为net+1、refs32、next+1、0。按节点/net排序紧凑分配，所有pool entry均live；allocator为next_unused、free_head=0、live、0并补零到64B。容量等于已有entry数，只保证读取/复用释放entry，未预留新增net所需空间；生产提交需另行容量规划。
- owner refs/occupancy超65535拒绝。每节点occupancy必须等于primary存在数加overflow不同net数。
- history和prices独立保留；lb/upstream/prev/visited/target原样进入native160。native160只是host导入，不是192B paged backing，不做epoch变换、标签有效化或未知页初始化。
- 保留完整旧prev不意味着旧距离可复用。query/price/version/design必须由后续控制器显式管理。

独立审计完整解码每节点、每条链、每个缓存并对照CPU快照和原CSR。C++检验使用已有owner_store.hpp读取全部真实owner/overflow，另选一个实际多owner节点验证primary删除提升、free-list复用及occupancy不丢失。尚未实际AXI/RTL导入或运行多query搜索。
