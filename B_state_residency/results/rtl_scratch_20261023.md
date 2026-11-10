# 首个scratch页槽RTL与BRAM映射

单写端口版本的行为仿真、独立综合及终态审计均passed，证据：[completion_audit](rtl_scratch_bram_20261023T090356Z/completion_audit.json)。manifest SHA256 `6ea6c6c574422432775f3c9712175c5d144de5f7e0b802d0ac1dd8473815d6e5`。

|项目|结果|
|---|---|
|后端|Vivado/XSim 2022.2，Tcl/批处理，无GUI|
|器件|xcu280-fsvh2892-2L-e|
|实例|4槽 × 64节点，每节点136位；历史拥塞独立|
|行为检查|98351次响应检查，其中98322条实际轨迹转换命令|
|真实输入覆盖|19完整小查询、56588次字段访问|
|背压|17358个响应保持周期|
|仿真结束|3.780030 ms，明确TEST_PASS和$finish；100 ms watchdog，120 ms运行上限|
|综合资源|2 RAMB36E2、1332 LUT、641 FF、0 latch|
|约束|10 ns探索性综合时钟约束；未布线、未验证100 MHz物理达成|

当前实现为 [scratch_frame_store_bram.sv](../hardware/rtl/scratch_frame_store_bram.sv)，接口与边界详见[契约](../hardware/SCRATCH_FRAME_CONTRACT.md)。采用统一写使能、地址及数据，将搜索字段更新和LOAD合并为单个物理写端口；同步读与节点有效图保证旧RAM数据不会在新绑定中暴露。浮点按位传递，不执行浮点运算。

输入向量由冻结的实际字段采集生成，19个查询完整选入，并非截断大查询。每次dirty页卸载前，通过公开READ端口比对全部有效节点，然后发CLEAN/UNBIND；重新装入时通过LOAD输入参考后备记录。最终计数包含8992次导出READ和15672次LOAD，见 `rtl_scratch_20261023/vectors_manifest.json`。响应背压期间不接收新命令，并检查全部响应字段保持。实际大查询尚未用于该RTL测试；软件30 MiB有界模型则已覆盖全部38查询/14047736次访问，见[实际值报告](real_field_values_20261023.md)。

初版 `scratch_frame_store.sv` 行为仿真同样通过，但综合报告 `Synth 8-4767`，两处写语句未推断为RAM，`data_reg`退化为寄存器。初版后续时序优化被修正版替代并主动终止，未声称初版综合完整通过或给出其最终资源计数；负例日志、源码及终止收据保存在 `rtl_scratch_20261023/superseded_register_mapping/`。这一差异说明行为通过不足以证明存储可实现性。RAM端口结构参考了AMD [UG901单端口RAM说明](https://docs.amd.com/r/2022.1-English/ug901-vivado-synthesis/Single-Port-Block-RAMs?contentId=wEtg165R5zc7Sdlg2UGywA)，映射结果由本机2022.2实际综合确认。

另保留了两次流程问题：初次编译误用SystemVerilog关键字matches，改为binding_matches后通过；XSim参数以短横线开头，按本机set_property帮助改为显式-name/-value/-objects。完整失败证据和修改前源码保存在 `compile_failure_01/`。未弱化断言或忽略错误。

原MCP会话 `vivado-20261023-025350-329eb221` 在launch_runs时主进程退出，崩溃栈包含libudev/realloc、libXil_lmgr11及Webtalk注册查询。独立综合子进程仍存活，已先核验后保留，未因MCP观察失败重复提交。针对版本、launch_runs与精确栈符号进行官方站点检索，未找到可确认适用的Answer Record，根因未证实；环境doctor无失败项。没有更改系统库、安装补丁或关闭检查。修正版通过本机独立批处理完成同版本XSim/综合，验证了可继续工作的路径，不能解释为修复了原会话崩溃。

综合仍有两条非关键警告：并行综合规模条件不满足、扁平网表不适合floorplanning；另有BRAM未合并可选输出寄存器的时序优化提示。没有Critical Warning或Error。未运行物理实现、SDF仿真、板卡或性能基准。

后续任务是将有限事务ledger、写回/refill租约、fence控制及整页发布屏障接到页槽接口，尤其不能将任意CLEAN或有限token相等当作真实DMA完成证明。当前页槽模块不是完整驻留路由器；全局occupancy/history与价格有效性仍在接口外。
