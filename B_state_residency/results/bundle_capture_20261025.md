# 新提交代的健康边界参考bundle（2026-10-25）

选定bundle_capture_v3。运行实例仍绑定checkpoint17/G1（4294967297），在同一实际checkpoint lease下将query40B帧导出到待提交G2（4294967298），并导出真实路径312B。握手后故意改变generation引脚，流仍保留已接受值。降低代拒绝；合法CRC的G2图像在仍运行G1的实例中导入也拒绝；默认G1导出/导入完成后，捕获结束保持健康、lease持有、全部工作/AXI退休和frontier0。没有私有query reset，没有force或模拟authority返回值。

32槽/单槽实际owner B故障→328标签恢复/核验→完整CPU重跑后捕获，周期836290/893444。查询命令检查共5次，状态1/0/1/0/0；随后path流成功。全部既有8AXI+4图像与前基线同容量逐字节一致。周期包含验证事务和背压，不包含之后主机复制、hash、fsync或协议重建，不能当完整checkpoint延迟或加速。

| 内容 | 实际来源与校验 |
|---|---|
| working owner/allocator | 实际AXI写后的145MB primary及64B allocator，capacity0；6个保存路径资源ref1，旧journal键与已改变节点完全一致 |
| path/query | 硬件M流78字/10字；CRC32分别637ddbbb/6d0c23ca；query包含D/G2/version4/query2/price4/sequence1 |
| labels/directory | 实际3MB标签页与被动目录cmd/rsp重建的120个published frame；枚举全部328个present记录，与实际Z读回/CPU相同 |
| design/history/price等 | 完整实际design/cost图像；graph/table/connection六个immutable资源以长度/SHA256引用绑定，不重复复制 |
| 配置与恢复下限 | 实际2304bit旧描述、当前active与attempt4/query2/price4；按已有RTL cfg_payload规则只覆盖word70得到effective配置 |
| 新基线 | checkpoint18/G2，working owner已包含6项变化；新基线restore_journal为空，原实例仍保留旧G1/journal6 |

目录不是从测试台读取owners数组伪造：BUNDLE_TRACE观察器仅记录已接受native请求/回复、reset、memory_success/fence及lease结果。独立模型验证每个状态/分配/发布/lease/cookie转换，得到full/pressure的3965/9458次命令，120frame/328record。它仍是仿真被动协议跟踪，不是生产目录导出端口。非authoritative索引可重建；端点与目录cookie freshness必须在全退休冷会话内协调重启。

两bundle各330824322数据字节，13组件中11份字节一致；directory.json与labels.bin的物理顺序不同，但labels.records逻辑状态完全一致。不能将不同布局的页与目录混配。当前封装只核验本轮capacity0、一路径/6资源/单active context fixture，不宣称任意多net/overflow/多上下文全快照。

单写者主机参考发布：bundle.staging →逐文件fsync →manifest →COMMIT摘要 →fsync目录 →rename为bundle →fsync父目录。24检查包括2份有效包及22份拒绝：未提交/staging、缺COMMIT、摘要/身份错误，以及重算摘要后仍不合法的路径、query、目录映射、effective配置和attempt下限。源bundle字节不变。CRC/SHA提供完整性，本测试不证明断电恢复、签名认证或较早可信包防重放。

新功能生产逻辑只改query root。目录源仅增加BUNDLE_TRACE条件下的被动实例，生产不定义；其余120份RTL继承。完整U280 Vivado2022.2默认32/16384 OOC为105455LUT/71042FF/160.5BRAM/23DSP，比105272/70954增183/88。461逻辑端口/59502位，零latch/blackbox/file-agent/directory observer。无place/route/Fmax/板卡收益。临时MCP会话关闭。

三归档1658文件实际移走原目录、解压并独立复审；包含重新运行24项完整性检查，审计JSON逐字节一致。23当前源/依赖及两基线源另冻结于results/bundle_capture_sources_20261025。两个早期捕获版本作为开发证据保存，不冒充选定G2导入隔离/完整包核验。基础check通过，公共/其他方案基线未改。

复现：variant build.py/build_tb.py；run_bundle_capture.py新目录；audit_bundle_capture.py同目录 --before-bundle；对full_5与pressure_5分别package_rtl_bundle.py CASE；最后audit_bundle_capture.py同目录（含完整性检查）。verify_rtl_bundle.py CASE/bundle可单独验证。数据在归档中的full_5/bundle与pressure_5/bundle，机器证据bundle_capture_20261025.json。

尚未完成真实冷启动：host COMMIT不表示运行中authority换代。当前硬件仍G1；新实例需从完整可信G2包加载所有匹配状态，而不能单独拿query/path帧和早先初始owner组合。当前raw配置版本3与active4不同，恢复必须使用明确的effective4。下一步原生boot门控要从cold reset封锁业务，直到owner/配置、真实labels写回+读回CRC/count、path与query导入等全部实际receipt完成并消费，才放开；禁止常量done。已有CPU followup_q2可作为保存q1后冷恢复再执行sequence2分支的参考，验证共享owner1→2及真实ripup2→1→0。完整顺序见CONTRACT.md。

生产目录导出、全冷恢复consumer、实时namespace切换、全局持久化反重放下限、任意unknown页/旧prev/frontier、实际价格/回绕/容量、耐掉电与板卡仍缺。研究goal active。
