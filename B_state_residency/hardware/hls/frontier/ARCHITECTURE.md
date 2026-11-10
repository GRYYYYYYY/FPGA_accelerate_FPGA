# 单上下文64K frontier 原型

目标沿用研究配置：xcu280-fsvh2892-2L-e、10ns，Vitis HLS2022.2。没有指定吞吐目标，本阶段不应用performance/PIPELINE/UNROLL/ARRAY_PARTITION。尚未连接图扩展、原生页标签组件或主机平台。

## 宏结构与时序

采用Ross architect的规范三阶段：load_input → compute → store_output。顶层仅局部非static stream声明及三个函数调用；一个DATAFLOW，两个depth2 FIFO。compute单一进程拥有heap和size，内部是顺序原子sift，不在多个进程之间共享可写heap。

每次调用接收一个操作，compute完成状态更新后发一条响应，store_output写出结果。当前调用者须等上次ap_done并捕获输出后才启动下一次；没有主张多个heap操作并发提交或已实现跨操作吞吐。load/compute/store的单条token依赖存在；本布局不是搜索算法的数据并行化。

CLEAR只设size=0，不逐项清payload；原CPU参考本来已复用heap backing且clear也是O(1)，因此不宣称新增初始化收益。OFFER满时返回FULL，不修改heap/size；POLL空时返回EMPTY；SIZE只读；非法操作BAD。响应带status、原始key_bits/id及size。本原型接口是独立组件的ap_ctrl_hs标量调用，不是已定义的PCIe/XRT主机ABI。

## 比较与容量

entry为32位IEEE binary32 key_bits及32位id。按原8叉heap规则：offer在父<=新key时停止，poll仅在child<当前best时选更靠后的child，last<=best时停止；不引入id二级排序。整数解码比较保留NaN无序、正负零相等、负数/无穷/次正规值顺序及原始payload；不模拟浮点异常标志。避免依赖特定HLS浮点比较IP的次正规处理。

65536容量下最大索引到root最多6条边，sift循环固定上限6、每层最多8个child检查。size只由单一compute维护，FIFO只传命令/响应。64K×8B=512KiB仅是entry逻辑payload，不是综合BRAM数量或时序保证。完整真实CPU路由中最大观察值38638；未来设计仍必须保留运行时FULL检测及完整查询回退协议，不能用已知轨迹峰值作无条件准入。

## 技能核对与版本

- pragma作用域：INTERFACE/DATAFLOW在顶层函数体；STREAM在声明可见的函数体。没有优化类pragma。
- dataflow：两stream均单生产者/单消费者，staticheap和size只由compute读写，顶层无算术调用实参或控制语句，标量输出仅store_output写。
- 可综合子集：top及其用户helper无动态分配、系统调用、STL算法、递归、虚函数、函数指针或pointer-to-pointer。动态vector golden仅在frame_based与TB，不进入HLS top。
- 参考[AMD Vitis Utils stream接口模式](https://raw.githubusercontent.com/Xilinx/Vitis_Libraries/2025.1/utils/L1/include/xf_utils_hw/stream_dup.hpp)学习顺序read/write与通道所有权，未复制或链接其实现；仅使用本机SDK的hls::stream。
- Ross最新统一IDE配置仅存为架构元数据。2022.2实际采用已验证的vitis_hls Tcl入口；缺省csim/cosim argv均为空，TB不依赖外部参数。

验证分层：相同helper已进入隔离CPU参考并核对完整570286次搜索的结果与元数据、已有采样标签轨迹；两个C++实现各135228条命令及1000169组比较核对。Csim/csynth/cosim仍须各有真实终态收据，不能以G++通过替代硬件证明。本组件不承担query/price上下文或设计级占用生命周期，CLEAR不等同整条连接完成/标签fence。
