# 完整搜索核静态内存配置 v1

适用源码：`hardware/vitis/search_kernel_offsets_v3/search_kernel_top.cpp`。
CSR/compact 分别编译、分别链接；每个配置只实例化一个 `search_kernel_top_1`。
已和两个实际 HLS `kernel.xml` 核对全部 15 个参数；13 个缓冲区均有映射，两个标量不作内存映射。
旧 `hardware/vitis/ddr.cfg`、`hbm.cfg` 属于六参数译码器，不能用于完整搜索核。

| 配置 | 映射 | 用途 |
|---|---|---|
| `ddr_shared.cfg` | 全部缓冲区 → `DDR[0]` | DDR 共享池基线 |
| `hbm_shared.cfg` | 全部缓冲区 → `HBM[0:3]` | HBM 共享池候选 |
| `hbm_split.cfg` | graph/input/heap/index/record/output 各占 0/1/2/3/4/5；keys → 6:7 | 另列的内存拓扑实验 |

全部缓冲区按生产 pragma 最大深度同时驻留：原始 523788712 字节；每个请求向上对齐 4096 后共 523800576 字节（499.53515625 MiB）。其中 keys 为 272629760 字节（260 MiB），不能放入单个 256 MiB HBM 伪通道。共享 `HBM[0:1]` 在零预留假设下勉强容纳全部请求，但不满足本计划每池额外预留 16 MiB 的策略，因此使用四通道池。

4096 对齐与 16 MiB 预留是显式宿主申请策略，**不是驱动实际开销或板卡空闲内存测量**。真实图可小于 image 的 128 MiB 上限，这里为两种表示保留相同最大容量。每个 AXI bundle 的参数必须使用相同组；各组必须相同或互不重叠，拒绝部分重叠以避免重复计算可用容量。

重新生成时指定新的输出目录，现有目录会被拒绝：

```bash
python3 scripts/search_kernel_memory_plan.py --output <新的目录>
python3 -m unittest discover -s tests -p test_search_kernel_memory_plan.py -v
python3 scripts/check_search_kernel_memory_plan.py \
  --plan hardware/vitis/search_kernel_memory_v1/plan.json \
  --output <新的审计JSON路径>
```

`plan.json` 绑定源码、两份真实 XML、生成器和三份连接配置。审计器重读输入、配置和容量表并核对摘要，不会生成硬件成功标记。

下一步宿主须用 `kernel.group_id(arg_id)` 为每个 BO 选择链接后的组，不得把聚合 group ID 当作物理 `MEM_TOPOLOGY` bank 下标。链接时核对实际 U280 平台拓扑；加载后核对真实组容量并检查每次 BO 分配结果。当前尚无针对完整搜索核的 XRT 宿主或平台链接/实卡分配证据。三套配置只通过静态验证，未测带宽、时序、功耗或加速。

名义容量依据 [AMD U280 平台说明](https://docs.amd.com/r/en-US/ug1120-alveo-platforms/U280-Gen3x16-XDMA-base_1-Platform)；分组语法及容量失败语义依据 [AMD HBM 迁移教程](https://xilinx.github.io/Vitis-Tutorials/2021-1/build/html/docs/Hardware_Acceleration/Feature_Tutorials/07-using-hbm/2_Migrating_to_HBM.html)。教程演示平台为 U50，不能替代本地 U280 的链接验证；早期 `hbm_large_buffers` 示例的排除表还包含 U280，故不以该示例证明本板支持情况。
