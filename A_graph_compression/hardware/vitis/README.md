# Vitis / XRT 邻接核接入（2022.2）

当前提供两种独立核的构建、平台链接、XRT 主机执行和完整读回审计入口。它们只执行规范节点邻接展开，尚未把完整搜索、协商占用或路由器放到 FPGA。实卡 DDR/HBM、完整端到端性能和功耗均未测量。

## 当前证据

- `../../results/vitis_host_preparation_20261023_v1.json`：本机 XRT 2.14.354 主机编译成功，CSR/compact 各10批输入预检通过；3项主机契约测试、3项内核审计测试和1项独立读回审计测试通过。包含损坏输入、错误状态/边属性、越界写、计时不闭合、XO中缺失/改变RTL等拒绝用例。这是离线验证。
- `../../data/derived/vitis_graph_kernel_20261023_v1`：失败证据保留。完整C仿真/综合成功，2022.2 co-simulation插桩改写声明后产生C/C++ linkage冲突，RTL未执行。
- `v2/graph_accel.hpp`用`extern "C" { ... }`声明块避免该插桩问题。独立v2工程重新进行完整C仿真、综合、RTL联合仿真和XO导出；原解码算法、原始测试及黄金数据保持一致。
- v2实时状态：`../../data/derived/vitis_graph_kernel_20261023_v2/pipeline.json`。两模式均已通过并导出，独立审计`../../results/vitis_graph_kernel_audit_20261023_v2.json`已经通过，原两个owner均终态。
- XRT重新探测见`../../results/vitis_board_environment_20261023_v1.json`及同名log：0 devices。默认2022.2 base_platforms中没有U280平台；其他器件平台不能替代。

独立审计逐项核对冻结源文件、完整C仿真11批、RTL三批及XO的8参数ABI，并要求XO中每份Verilog与相应经过仿真的综合工程完全相同。完整图的274732请求/1100754有向记录覆盖来自C仿真；RTL仅覆盖8请求/664记录的匹配样本、容量不足和错误模式三批。综合仍报告部分循环约束未满足。原OOC布局布线时序不自动继承到这个Vitis包装核。

新包装核匹配RTL样本为CSR38803周期、compact4700243周期（121.13倍），并非压缩加速。相对旧包装的224.89倍下降也不能称优化：旧CSR20820周期、compact4682265周期，新的CSR周期增加。详见`../../results/vitis_decoder_diagnosis_20261023_v1.json`。样本642度节点贡献642/664边；全图已知行的中位度数4、p99为8，排序工作量明显不同，不把该样本周期比外推到全网路由。

独立副本OOC实现及审计已全部通过：`../../results/vitis_ooc_audit_20261023_v1.json`。200MHz下CSR/compact内部WNS为0.998/0.561ns，WHS为0.011/0.040ns，路由错误与DRC均为0；布局布线LUT6708/12339、FF9426/15285。外部612输入/314输出无delay约束，仍不能代替真实平台链接和板端测量。

新的按度数分层RTL对照运行于`../../data/derived/vitis_stratified_cosim_20261023_v1`：九个非空层各2节点、额外均匀64节点以及两批负例。仅增加stimuli，算法和综合RTL不变。两种图镜像存在不同的字符串编号，黄金数据先按完整资源语义比较，再分别核对各自的8字段输出。最终报告将写入`../../results/vitis_stratified_audit_20261023_v1.json`；运行中不能提前引用周期结论。

## 接口与内存

`graph_accel`参数顺序：`image, config, requests, output, result, counts, request_count, output_capacity_words`。前6项为内存缓冲区，最后2项为32位标量。`counts[0]`为成功写入的边记录数，`counts[1]`为失败请求数。每条边保留全部8个32位字段，每请求保留start/degree/status。

输入容量128MiB，每次最多65536请求；输出最多1048576个32位word（131072条边），每行最多1024条边。主机将完整输出与结果尾部填入sentinel，执行后全量读回并检查未写区域。完整板端manifest包含9个完整图分块及1个容量负例，共274736请求；其中完整图的53759个未知行，以及容量负例批中的3个失败（容量不足、未知行、无效请求各1个）均是预期状态。错误模式负例在RTL测试中保留，板端主机预检会拒绝错误模式配置。

`ddr.cfg`与`hbm.cfg`分别把全部6个缓冲区连接到`DDR[0]`或`HBM[0]`。这比较单个bank，不表示跨32个HBM通道聚合带宽。主机从实际xclbin和kernel group读取连接，检查每个参数的bank名称与内存类型，不能仅用运行参数冒充HBM结果。v2综合产生graph 32bit、control_data 512bit、output_data 64bit AXI端口，两模式相同；这不同于旧OOC包装，不能直接继承旧周期或资源结果。

## 使用

以下命令从方案A根目录执行。独立XO审计已通过；准备与实际U280 shell匹配的已安装2022.2平台；`/actual/...`必须替换为真实路径。现有环境未执行平台链接或上板。

```bash
python3 scripts/vitis_board.py link \
  --kernel-report results/vitis_graph_kernel_audit_20261023_v2.json \
  --platform /actual/u280/platform.xpfm \
  --mode csr --memory 'DDR[0]' \
  --output data/derived/board_link_csr_ddr_run1

python3 scripts/vitis_board.py run \
  --link data/derived/board_link_csr_ddr_run1 \
  --host-report results/vitis_host_preparation_20261023_v1.json \
  --device 0 --repetitions 7 \
  --output data/derived/board_csr_ddr_run1
```

依次为csr/compact与DDR[0]/HBM[0]四个组合使用不同目录。平台链接请求200MHz；实际频率、时序收敛和平台资源仍需检查链接报告。单次`run`保持图驻留并重复全部10批，尚不等同于7个独立进程的正式统计设计。正式比较还需随机化条件顺序、重复首次装载、控制共享主机干扰并采集功耗。

主机编译命令（已有的验证二进制及绑定源文件不得覆盖；修改时使用新版本）：

```bash
g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  -I/opt/xilinx/xrt/include hardware/vitis/host.cpp \
  -L/opt/xilinx/xrt/lib -Wl,-rpath,/opt/xilinx/xrt/lib \
  -lxrt_coreutil -luuid -pthread -o /new/path/graph_host
```

先前主机编译错误和测试启动错误日志均保留；最终成功编译为`vitis_graph_host_compile_20261023_v4.log`。UUID输出需要显式链接`-luuid`。`--preflight manifest mode`只作输入形状检查，不访问设备；正式入口额外验证冻结输入与内核证据摘要。

## 结果口径

每批保存完整`batch_N.bin`读回及`batches.jsonl`，记录fixture加载、输入与guard传输、XRT启动到等待完成、读回、验证、导出和整批wall time。`summary.json`另外记录设备BDF、设备名、xclbin UUID、6个实际内存group、首次设备加载、分配和图上传时间。

`kernel_wall_ms`包含XRT启动/等待开销，不能当硬件周期。`application_wall_ms`包含完整guard传输、验证和原始结果导出。容量负例须单独列示，不混入有效邻接吞吐。链路入口将计划、输入、xclbin、主机、退出码、日志摘要和独立读回结果绑定；单独调用读回checker只证明内容和计时闭合，不证明物理板卡执行。

尚需完成：实际平台依赖与shell版本确认、链接后时序/资源核验、真实板端比较、功耗、完整路由器接入以及完整特殊资源模型。

参考：AMD [2022.2 Vitis HLS用户指南](https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_2/ug1399-vitis-hls.pdf)、[v++命令](https://docs.amd.com/r/2022.2-English/ug1393-vitis-application-acceleration/v-Command)、[XRT Native API](https://xilinx.github.io/XRT/2022.2/html/xrt_native_apis.html)。实际API按本机2022.2头文件编译验证，link选项按本机`v++ --help`核实。

## 完整CPU路由器的核接口验证

`router_provider.hpp`通过明确的KernelCall回调提供邻接，支持按规范节点的LRU和先批量展开全部行。现有测试绑定的是原Vitis v2核C模型；`data/derived/kernel_router_cmodel_20261023_v1/preparation.json`记录两种表示各自全图黄金检查、20类坏返回拒绝及缓存/预展开检查。核错误会中止，不降级成无路径；未知行与已知空行保持不同。

`data/derived/kernel_router_integration_20261023_v1`正在执行CSR/compact×direct/expanded四条件，每项两批完整1062网路由。搜索/代价/占用/site状态与原实现相同，结束后独立检查全部路线和轮次状态。结果明确标为CPU C模型；XRT transport现已实现并完成离线编译/模拟交换检查，但尚未上板，也未把搜索器放到FPGA。

## 真实XRT完整路由入口（尚未上板）

`data/derived/kernel_router_xrt_20261023_v1/report.json`记录真实XRT链接、两模式shape预检和无CPU核链接符号检查。`router_exchange.hpp`的fake-device ASAN/UBSAN测试只证明拷贝/同步/guard契约；不证明真实板卡可运行。

完整四条件C模型审计和实际平台链接完成后，使用明确设备BDF与空闲主机CPU运行：

```bash
python3 scripts/kernel_router_board.py \
  --link data/derived/board_link_csr_hbm_run1 \
  --device DEVICE_BDF --cpu 122 --execution direct \
  --output data/derived/hybrid_csr_hbm_direct_run1
```

将DEVICE_BDF和link目录替换为实际值。模式与内存后端从绑定link收据读取；每次输出新目录，执行两批完整router并自动独立审核。expanded模式先硬件解码全部行再CPU路由；direct模式缓存miss逐行调用硬件，频繁启动可能很慢。核出错直接中止，没有CPU解码回退。仍需正式重复统计、平台时序/实际频率、功耗与完整FPGA搜索实现。

分层基线RTL已审计：`results/vitis_stratified_audit_20261023_v1.json`。非空层抽样compact/CSR约18–131倍，均匀64节点46.743倍；这些均非完整router或板端计时，不能用旧121倍概括所有访问。归并对照已独立核验：642度样本周期减少19.97%，但均匀64节点慢0.33%，综合BRAM翻倍；保留为混合结果消融，不替换默认核，见`results/vitis_merge_decision_20261023_v1.json`。
