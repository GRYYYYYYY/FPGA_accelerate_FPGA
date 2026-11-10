# 驻留LRU元数据初始化容量实测

提取冻结源中的实际NodeDyn和SparseLabels类，在CPU24独立小程序中调用initPaged，使用本机GCC/libstdc++对象布局及malloc_usable_size。未运行路由，不计入性能样本。

| 设计/槽数 | Frame对象 / B | 链表节点请求容量 / B | 索引节点请求容量 / B | 已列对象与请求容量减少 / B |
|---|---:|---:|---:|---:|
| logicnets_jscl/256 | 56（两者相同） | 6144 | 0 | 6160 |
| vtr_mcml/4096 | 56（两者相同） | 98304 | 0 | 98320 |

本机Frame均为56B，索引并未缩小单Frame对象；SparseLabels对象256→240B，消除每槽24B的std::list节点请求容量。初始化后已列对象+请求容量：LogicNets1550088→1543928B，MCML8493328→8395008B。收益小，不能把链节点消除解释为整体状态显著压缩。

known_requested_total_bytes包含SparseLabels对象、frames容量、各标签页payload、两个页表和链节点。known_usable_total_bytes将对应堆请求替换为malloc_usable_size，仍不包含malloc头、arena碎片、进程RSS等。后备此时为空，全局dyn、填充后备map/向量及其他Router结构完全未计入。GNU内部_List_node大小和iterator节点指针仅用于本机ABI测量，不承诺跨实现可移植。

证据保存生成源、二进制和各自SHA，以及冻结类源/片段SHA；脚本scripts/measure_resident_metadata.py。测量证明初始化容量，不证明动态峰值、完整路由内存或时间收益。探针编译/运行期间正式重复队列仍运行于CPU8，探针位于CPU24；共享机器缓存/带宽干扰不能完全排除。
