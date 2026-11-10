# 显式静态状态复位的排除HLS构建

算法、端口与C++测试与原exclusion副本逐字节相同，唯一构建差异为2022.2 Tcl `config_rtl -reset state`。本机help确认默认control只复位控制寄存器；power-on初始化不等于ap_rst复位。state同时复位static/global派生存储到C++初值。

旧exclusion_hls_20261024保持冻结，旧物理资源/时序不能套到此新构建。新32位及3位构建均重新C++/Csim/Csynth/cosim；重复复位语义由实际RTL整链路测试另证。没有热取消或跨复位旧消息防护，冷复位仍须外层排空服务并协调全部模块。源码不可新增RESET操作绕过此要求。
