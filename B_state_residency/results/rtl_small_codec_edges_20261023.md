# 小页codec协议边界与变异检查

扩展回归通过：99用例、286项计数检查，编译/展开/仿真及runner80555 exit0，manifest 12845f8460f9e2fa29167606aba6ffadde1104984661b18c03d21ba912de99a7。

新增通过公开握手进入六个阶段（编码输入、原始输出、原始输入、整页检查、等待commit、记录输出），分别施加cancel和同步reset，验证输出门控、错误完成或复位恢复。另检查编码输入高24位非零及无效记录携带非零值，最后正常编码/解码验证恢复。DUT未修改，无内部force或deposit。

三项变异均检出，runner48237 exit0，manifest 2fe5a017a885f0db148f07efd84bff8384fa4f964cfa8b3165bc2dea2ad36772：

- 忽略commit_ok：invalid record exposed。
- 忽略尾部零检查：invalid record exposed。
- 忽略取消状态转移：watchdog。此项证明测试能发现取消不完成，属于有限时限活性检查，尚非局部取消延迟证明。

所有变异在独立目录的源码副本执行，原始RTL和TB哈希不变。结果不表示完整形式覆盖、时序或AXI集成完成。

新增scratch_page_axi_small.sv及make_small_page_axi.py：从冻结原版导出三拍传输、72位cookie，最高合法页起址0xffffff40，保留4KiB分拆和错误排空。此模块尚未编译/仿真，下一步以192B真实字节oracle验证跨4KiB、最高地址、72位cookie高位、背压、B/R错误和codec端到端提交门控。
