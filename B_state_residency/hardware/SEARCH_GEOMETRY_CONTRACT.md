# 整数几何距离接口

`hardware/hls/search_geometry/v1`的`geometry_step`接受13个int32字，返回4个uint32字，ap_ctrl_hs与ap_memory。坐标必须由搜索控制器在正确阶段读取：本算子用于child.prev写入之后的代价几何，不能直接复用之前的访问性坐标。

| 输入字 | 内容 |
|---|---|
| 0–3 | child endX、动态endY、sink beginX、beginY |
| 4–5 | child、sink SLR索引，均按原动态endY查表 |
| 6 | crossSLR，非零为真 |
| 7 | superLongLineLength |
| 8–9 | childX对应next/prev Laguna柱；INT_MAX/INT_MIN分别为缺失哨兵 |
| 10–11 | xMinBB、xMaxBB；可用柱必须prev>xMinBB、next<xMaxBB |
| 12 | 原detour参数，仅用于参考oracle；结果不依赖它，硬件可能不读取此字 |

返回[status,deltaX,deltaY,distance]。正常status0；status1表示需要柱而两侧都不可用；status2表示非负距离超出int32；status4表示相邻SLR分支用到负SLL长度。失败时三个数值字均0，必须中止当前计算/查询，不能当距离0继续。

非cross或同SLR保留普通Manhattan距离。跨不同SLR且恰好相邻时，如果|deltaY|<SLL长度，调整为2×长度−|deltaY|。不同SLR时next==prev沿用原“在柱上”分支；否则选择到child距离较近的可用柱，相等时取到sink总距离较小者。所有中间差/加使用有界的int64数学运算，再检查int32返回范围。

原代码detour比较的两个分支与最终fallback选择相同，故消去比较不改变有定义输入上的deltaX。原哨兵路径可能实际求值INT_MAX+detour，C++有符号溢出没有可移植语义；新接口为这部分定义不回绕的行为，不声称与原UB等价。两侧都缺失时原INT_MAX+deltaY同样不宜作为距离。

CPU适配`adapters/build_search_geometry_router.py`只替换整数计算，保留原getSLRIndex、next/prev查表、child/parent标签访问和原源码行号；调用失败抛出异常并停止。没有提前读取SLR、改变child.prev写入位置或清除设计状态。

当前已有标量原函数差分、wide独立oracle、实际HLS RTL与全CPU路由回归流程。原可访问性、bbox、pinbounce、SLL返回方向等判断尚未硬件化；此算子不提供图/表读取、请求快照、query归属或中断复位服务。与代价服务的实际组合、完整搜索、布局布线和板上仍待完成。
