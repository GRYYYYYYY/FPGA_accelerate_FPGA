# 160位记录与512位页流编解码接口

模块 `scratch_page_codec.sv`，单时钟、单页在途。仿真与综合证据见
[实验报告](../results/rtl_page_codec_20261023.md)。此前页槽、页控制器、队列和后备服务源码保持冻结。

## 格式与握手

每页64个节点，格式与软件 `ScratchPageCodec` 相同：8字节 little-endian presence bitmap，随后64个20字节记录，最后56字节全零尾部，共1344字节、21个512位数据拍。记录低136位为两个float32原始位模式、两个int32及一个uint8；高24位必须为零。NaN payload和负零按位保留。不存在的节点必须带全零记录；存在且值全零与不存在不同。hist不在此格式中。

`start_valid && start_ready` 开始编码或解码。各数据接口在valid与ready同时为1时接受。输出在背压期间保持valid和数据。`done_valid` 与 `done_error` 保持到 `done_ready`；完成响应被消费之前不接受下一页。接口不携带owner/cookie，调用者必须保持本次页描述符绑定，不能交错不同页面。

编码依次接受offset 0..63的64条记录，包括absent记录；不接受乱序、重复、跳过位置或非规范padding。收齐并验证全部记录后开始输出页流；第21拍 `raw_out_last` 为1。`done` 只表示原始页流已被下游接受，不能代表AXI写响应成功，更不能触发页槽CLEAN或地址RETIRE。

解码收齐21拍并验证bitmap约束、记录padding及页尾后进入提交等待。仅 `commit_valid && commit_ready && commit_ok` 后才输出记录。失败提交或格式错误返回 `done_error=1`，不输出任何记录。成功提交后依次输出全部64个offset，最后一条被消费后才返回done。调用者必须以对应事务的成功内存响应驱动commit；不能把“接收了完整页流”等同成功响应。

格式检查不提供CRC、ECC或身份认证：将一种规范有效页改成另一种规范有效页不一定被检测。owner/query/price/generation/tx等身份和价格有效性仍由上层维护。

## 中止、复位与缓冲

`cancel` 是显式本地中止协议：活动操作在下个上升沿撤回未完成输出，返回错误done，并禁止该拍RAM读写。上下游必须一起识别此中止；普通ready/valid背压不允许撤回输出。已经输出并被消费的记录不能回滚，因此上层仍须在全64位置完成前隐藏refill目标页。

cancel不排空AXI、不释放目录租约、不清除后备服务sticky fault。读总线错误必须先由AXI服务排完已接受burst；写失败也须等到已接受工作的错误响应。外部应协调冷复位/恢复，不能仅重置codec后重用仍被占用的地址。IDLE中已有done等待消费时cancel不改变done的结果。

页缓冲为320×32位同步RAM。复位清元数据，不批量清RAM；编码输入和解码输入均覆盖本页全部320个记录word后才读取，因此旧RAM不能通过未写位置暴露。一次只运行编码或解码，不能同时收发两页。

## 组合验证的范围

`tb_codec_axi.sv` 将codec数据口直接连接真实RTL `backing_page_service`，复用独立AXI从设备模型及目录租约检查。测试台协调器在成功服务响应后驱动解码commit；写路径同时检查编码done和所有B响应，再允许测试台继续。失败读/写对codec显式中止，地址租约保持。

该协调器目前是测试台task，不是可综合总顶层。它尚未连接 `queued_scratch_endpoint` 的EXPORT/BEAT/COMPLETE，也没有实现页完成→地址RETIRE→双域fence的自动顺序。本轮独立codec综合资源不能与历史模块简单相加宣称为完整实现。当前采用逐word串行转换，尚无布局布线时序、DDR/HBM平台或实卡吞吐证据。
