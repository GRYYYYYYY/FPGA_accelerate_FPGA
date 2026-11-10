# 排除边引擎 v3

组合实际已审计 exclusion_step HLS生成RTL、exclusion_hls_call调用收集器、exclusion_edge_controller边调度器，以及冻结的exclusion_label_v2桥接器。外层输入一条边的parent/child/flags/created/has_laguna、query/price和cookie；输出同cookie的判断或显式错误。只允许一条在途边。

收集器锁存288位调用参数，ap_start保持到ap_ready接受，随后等待ap_done及五个独立ap_vld全部到达。每个字段仅按其有效信号写入；收齐之前不发布回复，不启动下一调用。支持输出与done不同拍，不依赖本版HLS恰巧同时输出。重复/无归属/接受前的输出、默认256周期内未完整完成、外部abort均锁存故障；MAX_CALL_CYCLES须>=2。该限时是局部调用看门狗，不是整条边或分页时限。实际HLS默认延迟3–4周期，不能把本地超时阈值当性能指标。

调度器先START，校验HLS generation单调、phase1..4最多各一次、请求node符合父/子角色，逐次发标签读取。只在label status=0、身份匹配且fault=0时发RESPONSE。完成后校验DONE/node0/excluded布尔，再向外提供判断。外层cookie不替代HLS generation，标签桥接token与页binding编号仍独立。

结果status：0成功、1非法边（未调用HLS，可继续）、2 HLS状态错误、3标签服务错误、4协议错、5异步于事务阶段但同步于clk的服务故障。detail保留HLS状态或{label_status4,service_status4}；错误时excluded=0不表示允许该边，只有status=0且fault=0可用。除非法输入外，错误锁存禁止继续工作，因当前HLS上下文可能仍等待标签，必须由外层协调排空后冷复位，不提供热取消。冷复位须同时作用于引擎、解析器和原生端点。

输入parent/child必须<2^24，即使该边立即完成也不得超范围；flags<=255、created/has_laguna<=1。查询/价格/动态created与图属性由外层在边执行期间保持语义稳定。created与label present独立，零初始化标签原样读取。引擎仍不管理getChildren过滤缓存、动态设计状态、图获取、占用/价格或回溯提交。

外部页解析器须提供页槽和绑定编号，并维持租约；仍未实现自动WB/RELEASE/BIND/RF。原生命令通道需独占或经过归属正确的仲裁。测试使用32帧目录和三个预先绑定槽，含同页、跨页、最高地址、空记录；不执行AXI。不能外推自动分页或完整搜索正确性。

验证计划：原始CPU函数生成27648组合+32零记录边，核对实际HLS—桥接—native链路判断与读顺序/值；调用收集器720种输出/done排列及故障；实际gen3 HLS七次成功后第八次耗尽；非法边、解析器/绑定/身份错误和同拍故障禁止RESPONSE。无完整路由/平台/板上或物理时序结论。

首轮v1在166951ns失败属于测试台采样错误：缺失done的超时测试用wait(fault)，捕获了有效信号尚未撤销时seen更新产生的半拍组合协议条件，未等时钟确认。debug.vcd显示该条件在下一采样沿前消失、stopped始终0。v2只改超时检查为跨越32周期期限后检查锁存故障，所有RTL与v1逐字节相同；保留首轮与波形，不放宽期限或成功判据。全部接口均同步于clk采样，非CDC/异步协议。

v3明确使用exclusion_hls_reset_20261024的config_rtl -reset state生成RTL。v2整链路完成全部27680正常边后，复位恢复测试发现旧HLS静态generation及Machine状态未随ap_rst清除（默认control复位）。新构建保持同一算法/控制器/收集器/标签桥接源码；增加phase2/3/4中止后协调复位、gen3两轮真实耗尽与恢复测试。只有新HLS重新通过协议cosim门禁后才能整合。旧HLS的资源/物理结论不适用于新构建。
