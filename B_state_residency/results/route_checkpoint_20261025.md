# 保存连接路径的 checkpoint 组件验证（2026-10-25）

发现并补齐了一类完整checkpoint缺口：原控制器reset会清除已提交连接的保存路径，恢复owner和标签后仍无法正确ripup。隔离组件新增固定格式导出、CRC32校验、暂存语义检查及双slot原子导入，保留原基线。

组件用两条真实CPU路径验证保存、控制器复位、恢复和共享ripup：554512、263946的引用计数从2降1再降0，ripup不读取label。owner/label仍是注册mock；这不等于真实AXI或完整系统checkpoint已完成。

每种8/32容量均通过31项路由检查及27项checkpoint检查，保留原25项回归。覆盖CRC/order/last、8种语义损坏、失败替换保持已发布路径、部分输入取消、导出背压期间丢失权限、部分暂存bank reset、空图像、普通请求退休。额外合成满长度路径覆盖最后一节点及重复检测；其拓扑有效性不在该组件验证范围。独立审计重算CRC并恢复owner操作序列。默认图像78字/312字节。

| 实现 | LUT | FF | 结果 |
|---|---:|---:|---|
| 算术索引、并行去重 | 12897 | 5789 | 保留参考 |
| 固定slot选择、并行去重 | 13825 | 5786 | LUT增加928，负结果保留 |
| 逐对去重扫描 | 12061 | 5751 | 当前选择 |

三者默认32节点组件U280 OOC均零latch/blackbox/BRAM/DSP。三者两容量的完整单元事件流字节一致，表示这些场景语义保持，不是周期或穷举等价。第三版较首版减少836 LUT（6.482%）。原无checkpoint控制器为2144 LUT/2924 FF，新增功能仍增加9917 LUT/2827 FF，开销较高，尚不适合宣称系统收益。后续考虑缓存元数据、减少暂存多读口及双bank BRAM结构，须再实测。

逐对扫描以较多校验周期换取比较器减少；最坏两slot校验约2×((7+P)+P×(P-1)/2)，P=32时1070个扫描周期，另加流传输和背压。此为结构上限说明，不是板卡实测。

11个结果归档共373文件已实际恢复并重审，audit逐字节一致，20源文件冻结；源、输入、三个综合版本与负结果保留。

完整checkpoint尚缺什么：

1. 将路径接口接入route adapter和统一系统围栏，以实际AXI owner及标签同时保存/复位/恢复，验证无并发更新。
2. 用同一checkpoint身份绑定owner primary/pool/allocator、design创建/children cache、history/价格、标签页/目录和配置描述；当前authority仍q1六行、标签328条外部可信流。
3. 恢复query last_sequence、epoch及成功/尝试版本下限；当前last_sequence随reset清零，只有恢复路径不能防止旧序号重新接受。
4. 明确frontier/递归/在途查询的重启边界或完整序列化，落实全局原子发布；未知页默认值/旧prev语义、价格真实变更、回绕/容量回收与耐掉电仍缺。

逐项源证据及八类状态义务见`checkpoint_coverage_20261025.json`，协议及运行命令见`hardware/variants/route_checkpoint_v1/CONTRACT.md`。当前外层cp_safe、拓扑与owner快照一致性仍由可信调用方保证，没有系统集成、place/route/Fmax或板卡结论。研究goal继续active。
