# 代价服务接入与中断边界（2026-10-24）

当前实现为`hardware/variants/cost_service_v2`，连接冻结的整数binary32 `exact_v2`实际HLS核。新增23字输入快照、同步双读口、双输出写口按地址收集、query/price/cookie归属、背压与停止故障处理。接口见[契约](../hardware/COST_SERVICE_CONTRACT.md)。

当前算术核在done/ready前写出四个结果字，最终完成拍写出第五字；不能沿用Frontier“ready之前返回非法”的收集规则。启动时建立归属，五字均收到且done/ready同拍才给响应。默认1024拍计算上限，背压不计入该上限。

## 功能与独立审计

`cost_service_v2_20261024/source_bound_audit.json` passed，实际Vivado2022.2 XSim：

- 原21576向量全部通过，含16224真实包、576双NaN、24 underflow以及普通/特殊/随机数值；复用冻结原始oracle与HLS源码哈希。
- 23019请求，22299响应，其中22297有效计算、1 inactive、1错误owner；111485有效输出字由独立Python再次对照向量。
- 720个复位时刻逐拍覆盖实测最长包index4169，另含完成后等待响应时段。721次冷复位取消720个请求，每次恢复后重新计算并核对，没有旧响应泄漏。最长正常服务689拍（含包装），不能当端到端吞吐或板上延时。
- 89634次ready前输出写，111963次总写，22329次算术完成。完成数大于已退休响应数，因为部分复位取消的是已完成但尚未退休的响应。
- 独立collector遍历120种五字排列，检查双口同拍与提前写出；18类协议/归属故障及完成/超时同拍边界通过。包含越界、重复/同址、未归属事件、ready/done不匹配、缺字、超时、query/price/active漂移、abort和晚到故障。
- 请求握手后主动改写输入总线，快照仍返回正确值；响应背压1100拍不会误触计算超时。
- 主流程149.018s/exit0。模拟总11050823拍。不是布线后或硬件实测。

`cost_service_boundaries_20261024/source_bound_audit.json` passed：额外45类实际核边界，4种外部失效（abort/query/price/active）各11个时刻，共32个计算中故障、12个响应已给出后的故障；再加实际算术核8拍超时。故障后保持1030拍仍不接受新请求、不泄漏新结果，已给响应字段保持稳定；44次单拍冷复位后计算正确。流程14.688s/exit0。

## 保留的失败与修正

`cost_service_20261024`初次运行在70ns报告`early outputs rejected`。测试台撤销写口后同一delta立即读取组合fault，尚未等待信号传播。`cost_service_v2`只在测试台清事件任务后增加1ns稳定时间；设计RTL及真实HLS测试台与v1逐字节相同，独立审计核对。失败日志、源码、runner及manifest全部保留。没有弱化故障检查。

## 实际综合

`cost_service_synthesis_20261024/final_audit.json` passed。xcu280、10ns研究时钟、OOC综合：8038 LUT、5814 FF、20 DSP、365 CARRY8，零BRAM/URAM/latch，LUTLP-1及check_timing组合环均0。相对裸算子7543 LUT/4791 FF，完整服务增加495 LUT/1023 FF；这不是布局布线后增量。

流程142.699s/exit0，checksum `b1b51999`，MCP history72；61619字节完整完成日志与DCP冻结。785输入/204输出没有IO delay，HD.CLK_SRC未设，未布局布线，不能据此声称10ns物理时序或板上频率已满足。

## 范围与下一步

这是代价服务的实际HLS/RTL接入，还不是完整FPGA路由。外部协调器仍需提供稳定价格快照和查询归属，cold reset要排空其他服务旧事务。此模块不修改设计占用/历史、标签、Frontier或缓存，也不能代替它们的顺序证明。

下一步接原整数几何和访问性判断，再组合完整search控制器：保留prev先写、SLL坐标依赖、首次push置visited、target先CLEAR后push、有序children与显式递归栈。随后回溯/同网引用/提交，最后才是平台、布线、板上与端到端性能评估。
