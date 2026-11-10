# 小页codec与AXI联合验证

Vivado/XSim 2022.2：编译、展开和仿真exit0，runner8153 exit0；146个检查、70次完整写页、65次完整读页、8类错误，520条解码记录、412拍原始数据一致，结束75670ns。final_audit通过，manifest SHA704d02a9182463369136da64275808cee745acc6ba725c8734eba9ff2fd27d05。

scratch_page_axi_small.sv从原AXI引擎独立导出，仅改变页拍数21→3、cookie64→72和最高合法页起址ffffff40。codec继续使用上一轮冻结源码。由独立字节循环构造64页fixtures，逐拍/逐记录核对；生成器重建一致，输入和源码哈希核对。

覆盖64种64B对齐的4KiB内偏移（页址frame×192遍历）；跨边界须分拆；0xffffff40可完整传输，1/0xffffff80/0xffffffc0地址拒绝。cookie bit64=1被完整回传并在done背压时保持。独立AXI slave包含W先于AW、周期背压、延迟B、AW/AR长度与地址/边界检查及保持输出稳定检查。

错误包括BRESP/BID、RRESP/RID、RLAST、第二突发B/R错误和三拍读突发首拍错误后的排空。仅成功AXI完成才允许codec commit，错误后取消未完成codec，不发布记录。AXI错误保持fault直至协调冷复位。

不含目录、租约生命周期、完整端点checkpoint或小页真实轨迹RTL回放；也不证明综合面积、时序或实卡性能。下一步扩展27位owner/32槽/72位cookie后备目录及记录服务，并保留已有64节点完整回放。

三项变异均被局部断言检出：截断cookie→done/cookie hold mismatch；取消4KiB分拆→bad AW burst；跳过错误排空→undrained error。runner40792 exit0，manifest 086a4ce617b7a585a1512b16e8e1d852afbd91d4303f0e61695272f8b33f5aa4。原RTL/TB未改，变异副本及失败日志单独保留。
