# HLS 复位与调用收集的集成边界

2026-10-24整链路验证确认：旧 `exclusion_hls_20261024` 默认采用control复位，静态Controller的generation与Machine状态只有power-on初值，不能将ap_rst视作这些变量的冷复位。旧ARCHITECTURE/历史记录中“复位后generation归零”的表述不能作为实现保证，保留旧冻结文件，实际接入改用 `exclusion_hls_reset_20261024`。

本机2022.2的 `help config_rtl` 明确区分control与state；完整输出在 `results/exclusion_hls_reset_preflight_20261024/help.stdout.log`。新构建设置 `config_rtl -reset state`，不改变算法/端口/C++测试。生成RTL已具有generation、request、previous、sequence、excluded的ap_rst分支；运行时证据是同一reset测试台：旧构建第二次复位后START返回generation2而失败，新构建返回1并能清除等待标签的Machine状态。

最终使用 `hardware/variants/exclusion_engine_v4` 收集实际HLS五个ap_vld与ap_done。ap_ready可能组合依赖ap_start，禁止将包含ap_ready的组合故障判断回接ap_start。v3实际综合出现7个LUT形成的LUTLP-1环；v4由锁存状态及外部abort驱动ap_start，保留相同功能回归且综合环计数归零。未设置ALLOW_COMBINATORIAL_LOOPS。

所有信号在clk采样，不支持CDC。外部服务故障当拍阻止启动；内部协议/超时错误在采样沿锁存后停止。已经提供的回复保持稳定，消费者必须同时检查status和fault。局部调用看门狗默认256周期，不是完整搜索时限。

state复位不等于在线取消，也不提供跨复位的旧消息防护：仍需排空解析/原生服务、协调所有模块复位，并重新建立查询和页映射。旧独立HLS物理资源/时序不能用于新state构建或整合引擎。后续Frontier等HLS组件接入时同样需要核实静态状态的复位或显式初始化命令，不能仅凭C++初值推断ap_rst行为。
