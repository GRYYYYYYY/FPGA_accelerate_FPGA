# 中心距离调用接口实验

结果：`cost_center_service_v2_20261025/source_bound_audit.json` passed。

- 实际生成RTL通过新服务逐位重放110397组/220794输出字。
- 16项独立mock协议边界；120个时刻abort、共同同步复位并在同实例恢复。
- 完整版本身份锁存和漂移检查；按地址收集完成当拍双写；回复背压与输入快照。
- Vivado2022.2 XSim，经已有B MCP会话执行，70.845秒/exit0。

首轮目录`cost_center_service_20261025`保留failed。100ns mock done writes检查在清除接口事件的同一delta读取尚未稳定的组合fault；只改测试台增加#1，RTL未改，v2完整重跑通过。

详细契约：[CONTRACT.md](../hardware/variants/cost_center_service_v1/CONTRACT.md)。该独立服务尚未连接candidate租约、post-prev坐标或23字producer，未做新联合综合，没有板上性能证据。
