# 访问性驻留控制实验（2026-10-24）

已将实际 `access_step` HLS 封装成完整child决策服务，Config和阶段状态保持在设备控制器中，自动发起动态请求并推进到最终action。原始参考算法与单步HLS保持不变。接口见 [ACCESS_SERVICE_CONTRACT.md](../hardware/ACCESS_SERVICE_CONTRACT.md)。动态后端尚未接入真实标签/坐标/占用fabric，不能将本轮成功当成完整设备搜索。

## 功能

`access_service_20261024/source_bound_audit.json`通过，全部46656child、195175实际HLS调用、148519动态服务请求逐项核对。

| 最终结果 | 数量 |
|---|---:|
| 跳过 | 25230 |
| 普通push判定 | 16097 |
| lookahead判定 | 5329 |
| EARLY | 2308 |
| PRUNED | 1614 |

11类动态请求全部覆盖，包括151次parent.prev及61次前驱tile读取；没有合并原有的两次parent.prev。sink/child SLR请求顺序保持。TB逐HLS输入检查驻留Config/phase状态，逐六输出字核对已通过原始CPU差分的轨迹，并记录每次服务身份/值及最终决策；独立审计重放日志。

实际仿真4442374周期，含刻意的请求和响应背压，不是板上时间，也不用于推导加速。原始路径/搜索CPU回归仍以之前的search_access_real_20261024为准；本次没有改CPU算法或新增完整物理后端回归。

## 边界

`access_boundaries_20261024`通过：六输出字720排列、18类收集协议故障、最后允许拍完成优先于超时；实际HLS+控制器122检查，包含96个逐周期复位偏移、217次总复位、token3实际耗尽、128拍超时、非法Config、七类错误身份、服务错误、owner改变、迟到abort和140拍响应背压。简单完整决策测试54拍，不能外推为所有路径延迟。

## 实现

`access_service_synthesis_20261024/final_audit.json`通过：实际完整驻留控制器+HLS综合 **1675 LUT / 2687 FF / 57 CARRY8**，零BRAM/URAM/DSP、锁存器、组合环。122.3s，exit0，checksum6b05da52，MCP history81；完整31588字节收据和DCP冻结。

776输入、415输出未设置delay，HD.CLK_SRC未设置；研究用10ns时钟约束，未布局布线。资源不含动态标签/图表/占用服务，不能简单加总独立模块资源当作完整搜索系统资源。

## 下一步

在完整child busy期间实现共享服务独占：标签visited/target/prev走分页端点；SLR/ENDY/STATIC走上一阶段实际坐标服务；WILL_OVERUSE/COUNT_USER接真实设计占用和同net引用。再与geometry/cost/Frontier及显式递归栈组成完整search，最后处理回溯提交。原始target先CLEAR、prev写后重算SLL坐标、首次push即visited和CP不清heap/栈仍为硬约束。

项目check及相关Python语法检查通过，原始参考源码与已冻结算法均未修改。
