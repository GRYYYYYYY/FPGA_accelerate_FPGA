# 代价调用服务

`cost_service_v2`连接冻结的`search_cost_exact_hls_20261024`实际RTL，单未完成请求。23字输入和5字输出按word0位于低32位排列，数值语义见`hls/search_cost/ARCHITECTURE.md`。

- 请求握手复制全部23字及query2/price4/cookie32；之后输入总线变化不影响计算。同步双读口延迟一拍。
- 外部查询协调器提供active/query/price，成功请求至响应退休必须保持。inactive请求返回status1，owner不匹配返回2；均不调用HLS。正常结果status0。返回原请求标识。
- 启动即取得输出归属，允许ready之前写出。按地址收集双写口的五个字。当前冻结核ready与done同拍，只有这拍收齐五字才能发布响应；它不是任意HLS核的通用适配器。
- 越界输入/输出地址、重复输出、同拍同址、无归属读写/ready/done、ready/done分离、done缺字、owner漂移、abort或1024拍超时均停止。完成拍优先于超时。输出写事件仅以CE且WE为准。
- 背压不计入计算超时。响应valid及字段保持到握手，包括晚到fault时；接收者必须同时检查fault=0。fault锁存，新请求不再受理；没有失败后热重试。
- 冷复位必须同时复位包装和算术核，并由外部协调器排空旧请求、标签写及其他服务事务。复位取消未完成请求和未退休响应；本服务没有设计级占用/历史状态，不触发Frontier CLEAR或标签checkpoint。

尚未接入几何、价格快照读取、原访问性判断、prev/visited写入、Frontier或完整搜索控制器。数值/服务仿真不能代替这些顺序约束、物理时序或板上性能验证。

验证入口：`scripts/audit_cost_service.py`及`scripts/audit_cost_service_boundaries.py`。v1与v2设计RTL相同，v2修正测试台撤销写口后的delta-cycle采样；失败快照保留。当前720时刻复位扫使用实测最长包index4169，正常服务最长689拍；额外实际核测试覆盖单拍冷复位、32个计算中故障、12个响应背压期间故障、8拍超时及44次恢复。
