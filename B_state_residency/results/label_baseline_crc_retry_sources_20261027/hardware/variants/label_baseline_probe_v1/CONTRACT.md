# 真实RAW presence组件核对

manager字节等于label_baseline_warm_v1生产候选。实际native endpoint、BRAM、backing codec/目录/AXI和完整immutable CPU baseline参与，不用模拟native present回复。

先raw-read空node0，真实present0/payload0且baseline misses0；再普通read实际seed，raw-read同节点必须真实present1/原payload。RAW标记在请求受理后立即拉低，仍保持锁存语义。raw写返回3，之后普通read确认原记录未改；继续原有首次write保留字段、io/CLIENT纯读seed写回/重载和provider R错误测试。

full_v1/single_v1各106检查，独立CPU/原生命令/回复/AXI/最终3072B backing字节重放；新增RAW路径不影响原3次WB/3次RF、3个完整seed/16个字段写结论。两个归档均实际恢复重审audit字节一致。此处测试内部RAW输入，不代表外部用户可直接开启；完整residency只在真实恢复PS/PW限定该信号。leaf保留l_present拒绝，不跳过空目标检查。
