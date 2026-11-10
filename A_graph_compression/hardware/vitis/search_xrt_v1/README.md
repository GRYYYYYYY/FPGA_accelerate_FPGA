# 完整搜索核 XRT 宿主接口 v1

独立宿主库，尚未接入完整1062网协商路由程序。原 CPU 实验及旧邻接译码器 XRT 实现不变。

- `abi.hpp` 来自上一版静态内存计划，准备脚本重新核对全部参数名、类型大小、控制偏移、BO容量及计划摘要。
- `topology.hpp` 按实际文件大小检查 xclbin 表和索引，同时读取物理 `MEM_TOPOLOGY/CONNECTIVITY` 与聚合 `GROUP_TOPOLOGY/GROUP_CONNECTIVITY`。核对选择的 DDR/HBM 布局、物理通道集合、连续地址、组容量、16MiB策略预留和共享AXI映射。不会把组编号当作物理bank编号；未知格式/缺失组表直接拒绝。实际 U280 xclbin 尚未验证这些检查。
- `transport.hpp` 要求真实硬件目标、U280器件、`ap_ctrl_chain`、精确15参数ABI，使用 `search_kernel_top:{search_kernel_top_1}` 独占CU。每个BO用实际 `kernel.group_id()` 分配，与组连接表核对。实际 BO 分配失败会抛错；名义容量检查不代表驱动空闲容量。所有H2D/D2H操作均显式同步，核执行检查 `ERT_CMD_STATE_COMPLETED`。
- `exchange.hpp` 在单一宿主线程中供一个Session独占一个Backend。图/config与初始meta只上传一次；生产核在首个有效查询初始化slots。heap/slots/records/keys保留在设备，查询只提交roots和packet，返回头先校验再读取有效路径和unknown记录。校验不要求每个拒绝都推进epoch：包预检和控制器预检均可能保留旧epoch。设备/传输异常后Session拒绝继续使用。

宿主层保留时间与提交字节计数；kernel时间是宿主观察到的wall，字节是同步API请求量，不等于物理总线流量。这里没有设备功耗、时序或加速结果。

冻结、编译和CPU验证（输出目录必须不存在）：

```bash
python3 scripts/prepare_search_xrt_interface.py \
  --output data/derived/search_xrt_interface_20261024_v1 --cpu 119
```

验证链接已有审计的真实生产C核，保留全部生产工作区容量；两种图表示各11次连续查询含32/16/8满状态、三类溢出、兼容合并、冲突、无效包、禁用目标和后续恢复。12类传输故障拒绝；另有三套合成内存拓扑、16类损坏及4类截断。ASAN/UBSAN与严格警告检查适用于CPU协议/拓扑测试；实际XRT路径做本机库编译、链接检查，**没有打开板卡**。

下一步须在新的完整路由副本接入该Session，保留完整路径/状态比较、外层协商和动态占用更新，并增加真实link报告及xclbin摘要绑定。CSR/compact使用相同核名和XML接口，不能仅凭XML辨别编译模式；调用者必须用审计过的构建证据确定模式。当前接口类的mode参数只核对图描述符，尚不提供这项构建来源证明。

API依据本机XRT 2.14.354头文件和[官方2022.2 Native API文档](https://xilinx.github.io/XRT/2022.2/html/xrt_native_apis.html)。当前不使用新版本的 `wait2()`。
