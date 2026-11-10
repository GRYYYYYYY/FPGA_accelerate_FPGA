本页记录CPU可执行布局阶段。实际AXI后端已另外实现并通过功能/故障/综合，见[OWNER_AXI_CONTRACT](OWNER_AXI_CONTRACT.md)；本页CPU原子commit依然不能作为物理AXI回滚保证，身份桥及fabric整合仍待完成。

# 设计级占用存储的可执行布局（owner_state_v1）

当前 `hardware/search/owner_state_v1/owner_store.hpp` 是CPU可执行存储规范，已经通过原函数差分、真实完整事件重放和最终文件审计。尚未实现该布局的AXI控制器、身份回显、硬件超时或故障恢复；`access_fabric_v3` 的kind4/6仍为外部模型。此规范使用C++容器和排序，不是可直接综合的HLS核。

## 数据与生命周期

所有word按little-endian u32编码，所有记录16B。

| 区域 | word0 | word1 | word2 | word3 |
|---|---|---|---|---|
| primary[node] | net+1，0表示空 | refs低16 / distinct occupancy高16 | overflow head+1，0表示空 | 0 |
| pool[index]，活动 | net+1 | refs | next+1 | 0 |
| pool[index]，空闲 | 0 | 0 | next_free+1 | 0 |
| allocator[0] | next_unused | free_head+1 | live_entries | 0 |

net支持0..INT32_MAX，编码后的0x80000000有效。所有引用支持1..65535，occupancy支持0..65535；指针支持配置池范围内的index+1。主记录为空时必须全零。新设计显式将三个区域初始化为空；allocator首次递增分配未用条目，之后优先复用free链。

初始化必须重放loader对sink和已有路径的预引用，之后才能开始connection搜索。当前真实输入有180326次加载预引用；不能仅初始化为零就宣称加载完成。标签OPEN/CP/CLOSE均不得改变本存储，history保持独立的设计状态。

逻辑primary文件大小N×16B；本输入为145424144B，pool65536条为1048576B，allocator16B。未来AXI512端口需各区域64B对齐并向上分配到完整拍；最后一拍的额外字节不属于当前逻辑文件审计范围，写入必须用16B strobes保护其他记录。64位基址、范围溢出、区域不重叠及配置检查尚待实际控制器实现。

## 命令与结果

GET0、INC1、DEC2均针对node/net，结果含操作后count、occupancy和`occupancy>1 || (occupancy==1 && count==0)`。GET查询命令前状态。占用按不同net计数；同net分支共享只增减引用，不能重复增加occupancy。

主owner最后引用删除时，从链表头晋升一项，释放原pool条目。原unordered_map允许任意一个overflow owner晋升，链表使用确定的头项；在支持的引用范围内，所有net的count/occupancy/过用布尔保持相同，内部主owner编号不要求逐次相同。overflow条目删除时修复前驱链接并归还free链，不能丢失其余net。

错误状态：0成功、1范围、2减不存在引用、3引用宽度耗尽、4占用宽度耗尽、5pool容量耗尽、6结构损坏、7非法op、8过期计划或代号耗尽。所有错误在当前模型中不修改存储。原主引用16位回绕、overflow任意32位增长及晋升窄化不属于本支持域；超界显式失败，不能声称与原溢出行为等价。

## 更新计划与提交

`prepare`只读现有记录，产生最多4条16B更新，每项保存region/index/before/after。它不修改主记录、pool或allocator。`commit`先检查generation及所有before值，全部符合后才应用更新；过期计划不得覆盖后来的状态。64位generation到顶后停止修改，GET仍可读。generation是当前CPU模型中的事务校验字段，不是已实现的设备token协议，也未作为持久化allocator字段。

该CPU提交是一个原子模型。实际AXI需要在整个命令期间排他持有状态，逐项等待成功B，最后一项成功后才发正常响应。中途B错误可能已有物理写入，因此必须停止并使该设计状态不可继续使用，随后协调排空并重新加载设计；不能把模型中“未commit无变化”推广为物理AXI写失败回滚保证。

与access_fabric联接时，kind4读WILL_OVERUSE，kind6读COUNT_USER；必须回显完整kind/phase/node/net/token/query/price身份，并在整个child判定期间阻止设计引用更新。查询生命周期不能成为设计计数初始化信号。

## 已通过与待验证

结果 `owner_store_v2_20261024/source_bound_audit.json`：20万随机增减、320万原函数net查询、实际65535引用和occupancy边界、256不同net、池耗尽/跨节点回收复用、旧计划拒绝、损坏链表/记录测试通过UBSan。原countUserSlot、promoteOverflowOwner、syncHotOcc、incUserSlot、decUserSlot按源块原样提取。

全部18515060次真实更新重放通过，65536池的活动峰值53734；最终145424144B主记录、1048576B池和16B allocator独立审计通过，722477个活跃节点、所有已分配pool条目均可从free链到达。共18940411条计划写，单命令最多4条；这只是逻辑16B更新数，不是已测AXI拍数、流量收益或硬件周期。

下一步实现实际AXI读/写控制器并验证AW/W独立背压、最后B后可见性、R/B身份及状态错误、晚到响应、超时、复位和半提交失败停止；再接owner身份桥和共享访问服务。当前单设计pool峰值不保证所有输入都适合65536容量。
