"""Publish frozen authority evidence and honest checkpoint coverage."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

def main():
 scratch=Path('/tmp/B_state_residency_offer_20261025');names=['checkpoint_authority_v1','checkpoint_authority_v2','authority_recovery_v1','authority_recovery_v2','checkpoint_authority_synth_v1'];evidence={}
 for n in names:
  p=scratch/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/f'{n}_restore_20261025.json').read_text());assert a['status']==r['status']=='passed'and r['audit_byte_identical']and sha(p/'source_bound_audit.json')==r['audit_sha256'];evidence[n]={'audit':a,'restore':r}
 frozen=ROOT/'results/checkpoint_authority_sources_20261025';frozen.mkdir();sources={}
 paths=list((ROOT/'hardware/variants/checkpoint_authority_v1').glob('*'))+[ROOT/'scripts'/n for n in ['prepare_checkpoint_authority_vectors.py','prepare_authority_recovery_mutations.py','run_checkpoint_authority.py','run_authority_recovery.py','audit_checkpoint_authority.py','audit_authority_recovery.py','audit_authority_recovery_failure.py','audit_checkpoint_authority_synth.py','report_checkpoint_authority.py']]
 for p in paths:
  if p.is_file():shutil.copyfile(p,frozen/p.name);sources[str(p.relative_to(ROOT))]=sha(p)
 (frozen/'manifest.json').write_text(json.dumps({'status':'passed','sources':sources,'scope':'Current source closure; executed sources remain separately frozen in each archive.'},indent=2)+'\n')
 coverage={'status':'incomplete','new_evidence':'Generic generation-bound owner snapshot GET service and actual owner-recovery subsystem retry are validated. Labels completion is a mock. Existing full-query top still uses earlier limited authority.', 'validated':['design64/checkpoint32/generation64 immutable binding and identity/range rejection before AXI','real primary/pool/allocator GET and overflow-chain validation against original CPU oracle','actual SLVERR and stalled AR cancel with retirement before rearm','journal-preserving owner subsystem retry, 3/5 dirty keys, promotion and overflow references','all snapshot/live AXI bytes and complete owner semantics; untouched records byte identical'], 'missing':['unified path/owner/design/history/price/labels/directory/config/journal checkpoint publication','full-query top integration with this generic reader and real label restore','query sequence/epoch/version lower-bound serialization and restart','snapshot authenticity, memory immutability enforcement and durable atomic storage','unknown pages, stale predecessor/frontier restart policy, arbitrary reroute','real changing prices, rollover, worst-case capacity/performance and board evidence'], 'previous_full_query_evidence':'results/route_checkpoint_join_20261025.json'}
 (ROOT/'results/checkpoint_authority_coverage_20261025.json').write_text(json.dumps(coverage,indent=2)+'\n')
 report={'status':'passed','research_goal':'active','scope':'Version-bound owner authority and owner-recovery subchain, not full checkpoint or full-query integration','evidence':evidence,'archive_files':sum(e['restore']['files']for e in evidence.values()),'frozen_sources':sources,'coverage':coverage,'basic_check':'python3 scripts/run.py check passed'}
 (ROOT/'results/checkpoint_authority_20261025.json').write_text(json.dumps(report,indent=2)+'\n')
 md='''# 版本化 owner 快照服务与恢复子系统（2026-10-25）

新增只读 authority 服务，绑定 design64/checkpoint32/generation64 与真实 primary/pool/allocator；复用未改写的 owner GET 引擎。身份/范围错误在 AXI 前拒绝，回复回显实际绑定身份；成功绑定后不可换绑。恢复子系统使用该服务实际读取快照，不再由测试表返回 refs。原完整查询 top 保持旧版，尚未接入此服务。

| 验证 | q2 准备态 | iter2 准备态 |
|---|---:|---:|
| 完整图像节点数 | 9089009 | 9089009 |
| 图像 overflow 记录数 | 0 | 53734 |
| 独立组件请求向量 | 298 | 430 |
| 含故障/重启的核验回复 | 302 | 434 |
| 实际 snapshot 读事务 | 590 | 1208 |
| 独立组件仿真周期 | 12181 | 21589 |
| 恢复子系统 journal 项 | 3 | 5 |
| 首次恢复错误/保留 journal | status6 / 3 | status6 / 5 |
| 显式重试修复项/最终 journal | 3 / 0 | 5 / 0 |
| 恢复子系统 snapshot 读事务 | 13 | 25 |
| live 写事务（变更及恢复合计） | 6 | 14 |

728 向量含身份错（generation 低/高 32 位差异）、越界、空/已占节点与外来 net，其中 58 个查询访问实际 overflow owner。每例另有 4 次真实故障/重启探针，共 736 回复；每例 7 配置回复、2 安全 rearm。只读 AXI 无 AW/W offer，配置和数据回复背压，实际 SLVERR 与 AR 停顿取消均通过。未穷举全部 53734 overflow 记录。

恢复测试先 journal，再通过实际 AXI 改写 live owner。含主 owner INC、DEC、清空/新建，iter2 另含 overflow INC 和删除主 owner 后 promotion。首次 snapshot allocator R 注入真实 SLVERR；旧回复消费、真实 AXI/逻辑退休后，更高 version/query 的显式重试成功。每例 target reset 共 10 周期、两段，authority 私有重启一次且 generation 保持。live backing 不随 target reset 清除。labels_done 明确是 mock，此结果只覆盖 owner 恢复子链。

保留失败版 authority_recovery_v1：首次读错后 journal=3，安全重启仍被旧 fault 污染，第二次在目标 reset 前返回 status6。修复版在 rearm 握手清 stopped、CORE_RESET 时屏蔽旧内核 fault；configured=0/busy 持续阻止读入，重配失败仍重新锁存。没有 reset 协调器或清 journal 来绕过失败。

独立审核从原始 CPU initial_nodes/initial_overflow 构建 oracle，重放每个实际 AXI 地址、数据、mask 与错误响应，核对完整 live 文件。修改节点的全部 owner 集合、refs/occupancy 与 CPU 一致，其他 primary/pool 记录字节不变，allocator 全字节一致。因此 owner 语义恢复完整。q2 文件也字节一致；iter2 promotion 改变内部 owner 顺序，文件不字节一致，不能宣称位级回滚。

Vivado 2022.2、U280 OOC：4537 LUT / 3973 FF / 0 BRAM / 0 DSP，零 latch/blackbox，74 逻辑端口、2420 位；MCP source 成功 73.826 秒、临时会话关闭。仅独立读取组件，不能与旧完整系统数字相加视作已集成结果。无布局布线、Fmax 或板卡加速结论。GET 沿用重复链校验，K overflow 需 2+K(K+1)/2 次读，未做最坏情况性能改进。

五份归档均实际移走原目录、解压并重新独立审计，审计文件逐字节一致；共 ARCHIVE_FILES 文件。当前 SOURCE_FILES 源文件另冻结于 results/checkpoint_authority_sources_20261025；执行源仍各自在归档内。失败版“审计通过”仅表示反例证据被核验，不表示实验成功。基础 check 通过，公共/其他方案基线未改写。

重跑：`python3 scripts/run_checkpoint_authority.py /tmp/B_state_residency_offer_20261025/新目录`、`python3 scripts/audit_checkpoint_authority.py 同目录`；恢复子系统用 `run_authority_recovery.py`、`audit_authority_recovery.py`。归档索引位于 results/offer_archives_20261025；完整机器证据见 checkpoint_authority_20261025.json。

下一步仍是统一 checkpoint：将可信同代描述绑定保存路径和全部 owner/design/history/price/labels/目录/配置/journal，接入完整 query top，恢复 query sequence/epoch/version 下限。当前 generation 不是持久化认证；需外部保证快照真实且不可变，cfg_permit 不是系统 lease。未知页、旧 prev/frontier 重启、实际价格变化、回绕/容量、耐掉电和板卡验证仍缺。研究目标继续 active。
'''.replace('ARCHIVE_FILES',str(report['archive_files'])).replace('SOURCE_FILES',str(len(sources)))
 (ROOT/'results/checkpoint_authority_20261025.md').write_text(md)
 prefix='''# 版本化owner快照与恢复子系统通过（2026-10-25，优先历史）

详见 results/checkpoint_authority_20261025.md/.json、checkpoint_authority_coverage_20261025.json 和 hardware/variants/checkpoint_authority_v1/CONTRACT.md。新增design64/checkpoint32/generation64绑定的通用只读owner快照服务；真实完整primary/pool/allocator图像，两份各9089009节点，第二份53734 overflow。728向量+8错误/重启探针共736回复，含58 overflow查询，非全量硬件穷举。

接既有协调器与真实可写owner引擎，journal先于变更；两例首次snapshot R SLVERR保留3/5项，再以新version/query显式重试成功。验证INC/DEC、overflow引用与primary promotion。独立CPU oracle、全部AXI字节、完整owner语义与未涉及字节一致，allocator一致；iter2内部编码顺序不同。旧fault污染重试的真实反例保留，修复仅安全rearm清暂态，身份/journal保留。

读取组件U280 OOC 4537LUT/3973FF/0BRAM/0DSP，零latch/blackbox；不是全系统资源或加速。五归档ARCHIVE_FILES文件实际恢复复审一致，SOURCE_FILES当前源冻结。labels_done仍mock，完整query top尚未接新authority，旧完整query基线保持。

下一优先统一checkpoint描述绑定路径与全状态，真实labels恢复和完整query接入，序号/epoch/version下限恢复。快照真实性/不可变、外部持久化仍调用方保证；未知页/旧prev/frontier、实际价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

'''.replace('ARCHIVE_FILES',str(report['archive_files'])).replace('SOURCE_FILES',str(len(sources)))
 for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/n;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','archives':5,'archive_files':report['archive_files'],'source_files':len(sources)}))
if __name__=='__main__':main()
