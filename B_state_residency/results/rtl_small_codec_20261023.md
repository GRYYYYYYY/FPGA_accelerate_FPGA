# 小页codec RTL先导

Vivado/XSim 2022.2行为仿真通过：83用例、259个计数检查，编译/展开/运行exit0，独立v2 runner exit0。manifest SHA256 266eea1c00d5f2f73d161b570d4f110923074236d77c4aff7c3d6e190736c0ba。

新增scratch_page_codec_small.sv使用1536位整页寄存器，实现8位有效图、8条160位记录和31字节零尾部，输出3个512位beat。解码检查全部记录及填充后等待commit，只有合法页面且commit_ok才输出记录。

测试包含16种页面内容、有效零值、全136位全一、跨512位边界编码、背压期间数据稳定、提交前无输出、拒绝提交、记录填充/尾部/无效记录非零拒绝、非法输入offset和接收期cancel。不是完整状态覆盖；尚待取消各状态、复位、非法encode payload、变异检出及AXI集成。

首轮RTL与TB已完成，但runner预期检查数误写387导致exit1；正确计数为16×16+3=259。原失败日志与failure_classification保留。v2只修正runner预期数，源码和TB哈希逐一相同，再完整重跑通过。

现为功能先导，不代表BRAM映射、综合面积、时序或端到端性能。下一步补充协议边界和变异测试，再实现3beat/72bit cookie AXI接口及4KiB跨界验证。
