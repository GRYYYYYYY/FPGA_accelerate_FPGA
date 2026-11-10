# 通用 owner authority 接入完整查询（2026-10-25）

选定 authority_query_v4 + authority_query_retry_v3。版本化只读快照服务已接入 query/search/residency 生产层级，原 k_a 响应输入在 query top 改为调试输出，测试台不再代替服务返回 refs。真实初始 primary（9089009 节点）和 allocator 经独立第八路 AXI 读取；本例 pool 容量0。此前组件已验证真实非零 owner/overflow，但本轮完整查询实际 authority key 是当前 journal 中的空初始 owner，不可宣称完整查询中已验证 warm 非零 owner 恢复。

| 完整系统场景 | 32槽周期 | 单槽周期 | 结果 |
|---|---:|---:|---|
| owner B SLVERR →恢复→完整重跑 | 835704 | 892858 | 修复1项，journal1→0 |
| owner B后 snapshot R SLVERR →显式重试→完整重跑 | 836213 | 892858 | 首次status6/修复0/journal1保留；重试修复1、journal清零 |

每例真实写回并读取核验328标签，完整重跑73 polls/72 expands/271 candidates/171 cost outputs和6项路由 owner提交。没有 labels_done mock。普通故障的 authority 两次 GET 共4次 snapshot读；二次故障先1次错误allocator读，再两次GET，共5次读。完整八路 AXI 每个字节、所有最终图像、CPU poll/candidate/cost/path/label/owner 均独立核验。普通故障的原七路AXI日志和四份完整图像两容量共22文件与旧基线字节一致；不是全部cycle trace等价或加速结论。

初始配置在无既有offer且服务/总线退休后接受，独立配置lease保持到回复消费并封锁16host/query/route/recovery。checkpoint acquire优先于同时的authority bind。协调器只接受与实际已绑定 design/checkpoint 一致且generation非零的受信任配置。读取请求使用绑定generation，回复验证实际generation。不可将该本机受信任配置看成持久化认证。

两个实际集成反例已保存：工作域 rst 在目标恢复时置位，若用于 reader 会丢绑定；修复为仅k_cold_rst。第二例安全rearm后，AXI已空但reader尚在私有重配，旧DRAIN过早触发target reset；新增normal_retired&&as_retired，等待身份可用和逻辑退休。没有清journal或冷复位协调器来绕过失败。开发包还保留声明顺序编译错误，以及明确SIGTERM停止的错误测试启动；它们均不算成功恢复。

三个已有生产层改写+一个reader新增，其余118份生产RTL继承；普通与二次故障的选定生产源一致。旧方案和公共源码保持不变。配置过程在冷域，工作目标复位不改变绑定；authority排空/退休/fault进入系统围栏、恢复与重试。这里只支持一个绑定快照；没有提供快照轮换或与保存路径一起原子发布的协议。

选定完整系统 Vivado2022.2 U280 OOC：104144 LUT / 70377 FF / 160.5 BRAM / 23 DSP；零latch/blackbox/file-agent，439逻辑端口/59228位。较上一版99321LUT/66384FF增4823LUT/3993FF。默认32slots/16384frames、诊断关闭；不是独立组件4537LUT数，也不是布局布线/Fmax/板卡收益。较早source的综合单独保存，不冒充选定版。

六归档2789文件均实际移走原目录、解压并重新审计，审计JSON逐字节一致；当前19源/审核依赖另冻结于 results/authority_query_sources_20261025。基础check通过。完整机器证据见 authority_query_20261025.json；开发反例“审计通过”只表示证据核验通过。

重跑：先以 build.py 和 build_retry_tb.py 生成本variant；`python3 scripts/run_authority_query.py /tmp/B_state_residency_offer_20261025/新目录`，二次故障追加 `--authority-fault`；然后 `audit_authority_query.py 同目录`。归档位于 results/offer_archives_20261025，恢复复审回执位于 results/*authority_query*restore_20261025.json。

统一checkpoint仍不完整：owner真实快照、路径buffer、labels/目录、design cache、history/价格、配置/journal及query sequence/epoch/version下限尚未绑定成可冷恢复的同代图像。328标签集仍为已知外部流，design backing保留；本轮价格数值不变，frontier不保存。下一优先为统一描述/快照轮换、序号与版本下限恢复，再验证warm非零owner和未知页。快照真实性/不可变、任意reroute、回绕/容量、耐掉电及板卡证据仍缺。goal active。
