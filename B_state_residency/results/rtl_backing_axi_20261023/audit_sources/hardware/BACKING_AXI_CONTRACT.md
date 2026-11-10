# 后备地址租约与 AXI 页服务

新增三个模块：`backing_frame_directory.sv`、`scratch_page_axi.sv`、`backing_page_service.sv`。服务模块组合地址目录和AXI引擎，内存完成只由引擎返回，外部不能注入MEMORY_DONE。它尚未与此前 `queued_scratch_endpoint` 及标签记录打包/解包器组成总顶层。

## 格式和容量

一页仍为1,344B：8B有效图、64条20B scratch记录、56B尾部对齐。AXI流每页21个512bit beat，低字节先传；该服务把所有字节视为载荷，**不在RTL内验证记录padding或解释hist/字段**，测试字节由已验证的软件ScratchPageCodec生成。地址从0开始，每frame固定stride1344B，64B对齐。

默认23,405 frame、15位索引，占后备31,456,320B，在30MiB原始字节预算内余960B。目录自身、租约寄存器、stream buffer、页槽及其他模块另计。默认容量仅完成综合，行为测试用64 frame覆盖满池、重复owner、地址回收和全部64种4KB起始位置。

owner24位为price[23:20]、query[19:18]、page[17:0]。cookie64位为slot[1:0]、page[19:2]、query[21:20]、price[25:22]、generation[41:26]、tx[57:42]、kind[58]（0写回/1换入），保留位[63:59]必须0。

目录采用BRAM顺序查找，所有已分配owner在fence前保留；查到原owner复用其frame，未命中且有容量才追加，满池不烧事务号。它没有全并行CAM/哈希加速，查找每个条目用读/检查两个周期，不能把有界容量和BRAM推断当成性能收益。冷reset/fence只清allocated计数，旧RAM由分配范围和published位隔离，不逐项清零。

## 服务命令与租约

一次接受一个服务命令，响应背压时所有字段稳定；cmd_ready只表示接受。请求被锁存，之后输入可变化。对外op为：0 RESERVE(owner)，1 TRANSFER(frame,cookie)，2 RETIRE(frame,cookie)，3 RECYCLE(fence_retired)。状态0 OK、1 STALE、2 BUSY、3 BAD、4 FULL、5 OLD_TX、6 UNREADY、7 IO_ERROR；与页槽控制器状态码属于不同接口，不可混用。

TRANSFER先PIN。frame必须已分配且owner与cookie匹配，同一slot不能已有租约，同一frame不能被另一slot租用；换入还必须published。成功PIN才消耗tx；此原型要求PIN的tx在一次fence期间严格递增，不支持乱序发放PIN。cookie的query/generation正确性仍来自上游已验证页控制器，目录不会自行建立当前查询。

写回PIN立即撤销旧published，AXI操作全部成功后才重新published。换入PIN不改变已存在的后备有效性。租约沿 `INFLIGHT → COMPLETE → FREE`：AXI完成只到COMPLETE；上游消费者已经提交成功的页控制器COMPLETE后，才能发RETIRE。四个slot的租约可同时保留，并允许反序RETIRE，但当前AXI总线引擎一次只处理一个页。错误cookie、旧tx、别的owner都不能回收租约。

AXI失败使租约到FAILED，拒绝RETIRE与RECYCLE，写回保持unpublished；引擎进入sticky fault并拒绝新TRANSFER。没有热恢复/重试流程，需要整个相关传输域协调冷启动。不能只reset本模块而让旧总线响应继续存在。

RECYCLE必须所有租约为FREE且fence_retired为真；才清owner分配范围和tx隔离。**fence_retired和RETIRE目前仍是适配器侧控制输入**，尚未由总顶层接到前一轮真实fence退休/页提交事件，不能宣称完整地址池回收链已经闭合。

## AXI 子集与错误处理

AXI4 INCR、512bit、SIZE=6、固定ID=0、32bit byte address，最多一个未完成burst。AW与W独立握手，不能因为AW尚未握手而禁止提供已有W数据；VALID及对应payload在背压下保持稳定。按4KB边界拆分1,344B页，全部WSTRB=1，不支持非对齐/部分页。AW/AR地址、长度和有效数据均由目录地址及已传beat计数决定。

写回必须每个burst的B握手均为OKAY、BID=0，最后一个B后才能报告成功。这里是AXI完成/可见性语义，**不是掉电持久性保证**；外部内存控制器和系统属性仍须正确配置。读回逐beat检查RID、RRESP和RLAST；成功还要等21个beat都被服务消费者接收。

读错误后不发布该错误beat，按当前burst已承诺的长度继续接收并丢弃余下beat，排完才报告失败，不再启动后续burst。已经返回的正确前缀只能暂存，收到服务失败后不能向搜索发布。非法从设备若提前停止提供剩余beat，引擎会保持等待及fault；没有超时或擅自宣称排空。

协议依据：[Arm IHI0022H](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)，A3.3.1握手依赖、A3.4.1的4KB边界及禁止提前终止burst。单ID方案不处理非法重复B或域外旧包，也不是完整AXI一致性/安全证明；未接AMD AXI Protocol Checker、CDC、物理平台或板卡。

## 下一步组合约束

下一层需把页控制器EXPORT/BEAT的160bit记录与本服务的512bit原始页流进行逐字节转换，并把成功服务响应绑定到原始完整描述符的页控制器COMPLETE。只有页控制器确认COMPLETE后才能RETIRE地址租约。最后应等待页域fence退休、目录RECYCLE及所有内存/响应队列清空，再向任务提交方返回fence成功；期间禁止开始新query，避免有限query复用先于地址命名空间清理。

现有验证和限制见 [报告](../results/rtl_backing_axi_20261023.md)。没有端到端实际路由、HBM/DDR实卡性能或加速结论。
