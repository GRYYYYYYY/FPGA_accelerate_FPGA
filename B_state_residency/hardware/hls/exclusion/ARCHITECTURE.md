# 单边排除判断硬件接口

使用已完成完整CPU路由验证的exclusion_machine.hpp原样副本。目标U280、10ns、Vitis HLS2022.2；Ross HLS scope/dataflow/run-flow流程沿用frontier组件，最新统一IDE cfg仅为元数据，实际用2022.2 Tcl。未设置吞吐目标，没有性能类pragma。

顶层exclusion_step采用load_input→compute→store_output，两个depth2单生产者/单消费者FIFO，一个DATAFLOW；INTERFACE/DATAFLOW在顶层，STREAM在变量声明之后。compute独占静态Controller状态，其他进程仅搬运命令/响应。无动态分配、递归、函数指针；动态vector仅存在testbench抽取的原函数golden中。调用方等待ap_done并捕获输出后提交下一条，尚未验证并发顶层调用。

## 命令及结果

START=0：输入parent/child节点ID（0..INT32_MAX）、flags（原RRT低8位）、created/has_laguna布尔。仅无待处理标签请求时接受。每次成功START消耗一个新的generation，包括立即得到结果的情况。图属性和created快照保持至该边结束。

RESPONSE=1：输入generation、phase、value。只有当前待处理请求且generation/phase完全相同才消费响应；每个phase在同一边最多出现一次。生成的标签请求phase为CHILD_PREV1、CHILD_VISITED2、PARENT_VISITED3、ARC_PREV4；node输出对应child或parent。响应数据含原始32位prev/visited值，由服务方保证来自请求的正确查询标签视图。

SNAPSHOT=2：只读当前状态。返回status、generation、request、node、excluded。request=0且generation>0表示最后一条已完成边的结果；忙时excluded固定0，DONE时node固定0。

status：OK0、BUSY1、NO_REQUEST2、STALE3、WRONG_PHASE4、EXHAUSTED5、BAD6。拒绝操作只改变本次status，generation/请求/结果及内部边状态不变。START先检查BUSY，再检查参数，最后检查耗尽；RESPONSE先检查是否存在请求，再检查编号与阶段。非法命令BAD。

## 生命周期与边界

默认generation32从0开始，到UINT32_MAX后拒绝所有新START，绝不在该运行周期内回绕；SNAPSHOT仍可读取，完成边的旧响应被拒绝。没有软件RESET或取消命令。硬件冷复位必须由集成层在排空旧请求/响应后统一执行；本组件不保证跨冷复位仍能区分旧消息。

gen3版本使用完全相同代码/接口，仅编译宏不同，实际在7个成功上下文后验证EXHAUSTED。该测试证明缩小编号宽度实例的真实边界，不声称执行了2^32条生产上下文。32位实例验证全部27648个语义组合，并在每个标签阶段插入错误/重复响应和SNAPSHOT；最终判断与原函数golden比较，节点读取顺序也保持。

不提前读取未请求的标签，不删除ARC_PREV的原有再次读取。原getChildren首次过滤/缓存、created/deadEnd副作用、图读取、标签分页、查询/price标识、设计占用历史和失败清理仍由后续集成处理。当前没有RTL标签服务连接或完整设备搜索。
