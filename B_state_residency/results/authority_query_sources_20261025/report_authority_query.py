"""Publish source-closed full-query authority integration evidence."""
from pathlib import Path
import json,shutil,re
from run_checkpoint_authority import ROOT,sha

def main():
 scratch=Path('/tmp/B_state_residency_offer_20261025');names=['authority_query_v3','authority_query_v4','authority_query_retry_v3','authority_query_development_20261025','authority_query_synth_v1','authority_query_synth_v2'];evidence={}
 for name in names:
  p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text());assert a['status']==r['status']=='passed'and r['audit_byte_identical']and sha(p/'source_bound_audit.json')==r['audit_sha256'];evidence[name]={'audit':a,'restore':r}
 normal=scratch/'authority_query_v4';retry=scratch/'authority_query_retry_v3';nm=json.loads((normal/'manifest.json').read_text());rm=json.loads((retry/'manifest.json').read_text());comparison=json.loads((normal/'baseline_comparison.json').read_text());assert comparison['status']=='passed'and comparison['files_compared']==22
 for n in nm['rtl']:
  if not n.startswith('tb_'):assert nm['sources'][n]['sha256']==rm['sources'][n]['sha256']
 production=[n for n in nm['rtl']if not n.startswith('tb_')];changed=['residency_system.sv','search_residency_system.sv','query_residency_system.sv','checkpoint_authority_reader.sv'];inherited=[n for n in production if n not in changed]
 frozen=ROOT/'results/authority_query_sources_20261025';frozen.mkdir();paths=list((ROOT/'hardware/variants/authority_query_v1').glob('*'))+[ROOT/'scripts'/n for n in ['run_authority_query.py','audit_authority_query.py','audit_authority_query_synth.py','audit_authority_query_development.py','compare_authority_query.py','report_authority_query.py','prepare_query_lifecycle_synth.py','run_checkpoint_authority.py','run_query_fault.py','audit_route_fault_axi.py']];sources={}
 for p in paths:
  if p.is_file():shutil.copyfile(p,frozen/p.name);sources[str(p.relative_to(ROOT))]=sha(p)
 (frozen/'manifest.json').write_text(json.dumps({'status':'passed','sources':sources,'scope':'Selected current source and imported audit helpers; every executed source remains in its experiment archive.'},indent=2)+'\n')
 coverage={'status':'incomplete','validated':['generic generation-bound owner authority inside complete query/search/residency hierarchy','actual owner-B failure; 328-label restore and read verification; complete CPU query replay in32/1slots','actual snapshot R failure after owner-B; retained journal and safe rearm; newer query/version successful retry','cold reset separate from target reset; authority identity preserved across target resets','all8AXI bytes, whole final memories and CPU oracle; original7AXI plus4images byte-identical for ordinary fault'], 'missing':['one atomic checkpoint descriptor binds owner/path/design/history/price/labels/directory/config/journal','checkpoint snapshot rotation and warm nonzero-owner full-query recovery (reader currently binds one initial snapshot)','query sequence/epoch/version lower-bound serialization across cold reset','general unknown pages, stale prev/frontier restart, arbitrary reroute and actual changing prices','snapshot immutability/authenticity enforcement and durable atomic publication','capacity/rollover/timing/board verification; real AXI fault during path-checkpoint lease'], 'prior_path_checkpoint':'results/route_checkpoint_join_20261025.json','component_nonzero_overflow_evidence':'results/checkpoint_authority_20261025.json'}
 util=evidence['authority_query_synth_v2']['audit']['utilization'];facts=evidence['authority_query_synth_v2']['audit']['facts'];files=sum(e['restore']['files']for e in evidence.values());cycles={}
 for group,m in [('ordinary',nm),('authority_retry',rm)]:cycles[group]={n:int(re.search(r'cycles=(\d+)',c['result'])[1])for n,c in m['cases'].items()}
 report={'status':'passed','research_goal':'active','selected_ordinary':'authority_query_v4','selected_double_fault':'authority_query_retry_v3','evidence':evidence,'comparison':comparison,'cycles':cycles,'selected_utilization':util,'selected_facts':facts,'production_changed_or_new':changed,'inherited_production_rtl':len(inherited),'archive_files':files,'sources':sources,'coverage':coverage,'basic_check':'python3 scripts/run.py check passed'}
 (ROOT/'results/authority_query_20261025.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'results/authority_query_coverage_20261025.json').write_text(json.dumps(coverage,indent=2)+'\n')
 md=f'''# 通用 owner authority 接入完整查询（2026-10-25）

选定 authority_query_v4 + authority_query_retry_v3。版本化只读快照服务已接入 query/search/residency 生产层级，原 k_a 响应输入在 query top 改为调试输出，测试台不再代替服务返回 refs。真实初始 primary（9089009 节点）和 allocator 经独立第八路 AXI 读取；本例 pool 容量0。此前组件已验证真实非零 owner/overflow，但本轮完整查询实际 authority key 是当前 journal 中的空初始 owner，不可宣称完整查询中已验证 warm 非零 owner 恢复。

| 完整系统场景 | 32槽周期 | 单槽周期 | 结果 |
|---|---:|---:|---|
| owner B SLVERR →恢复→完整重跑 | {cycles['ordinary']['full_5']} | {cycles['ordinary']['pressure_5']} | 修复1项，journal1→0 |
| owner B后 snapshot R SLVERR →显式重试→完整重跑 | {cycles['authority_retry']['full_5']} | {cycles['authority_retry']['pressure_5']} | 首次status6/修复0/journal1保留；重试修复1、journal清零 |

每例真实写回并读取核验328标签，完整重跑73 polls/72 expands/271 candidates/171 cost outputs和6项路由 owner提交。没有 labels_done mock。普通故障的 authority 两次 GET 共4次 snapshot读；二次故障先1次错误allocator读，再两次GET，共5次读。完整八路 AXI 每个字节、所有最终图像、CPU poll/candidate/cost/path/label/owner 均独立核验。普通故障的原七路AXI日志和四份完整图像两容量共22文件与旧基线字节一致；不是全部cycle trace等价或加速结论。

初始配置在无既有offer且服务/总线退休后接受，独立配置lease保持到回复消费并封锁16host/query/route/recovery。checkpoint acquire优先于同时的authority bind。协调器只接受与实际已绑定 design/checkpoint 一致且generation非零的受信任配置。读取请求使用绑定generation，回复验证实际generation。不可将该本机受信任配置看成持久化认证。

两个实际集成反例已保存：工作域 rst 在目标恢复时置位，若用于 reader 会丢绑定；修复为仅k_cold_rst。第二例安全rearm后，AXI已空但reader尚在私有重配，旧DRAIN过早触发target reset；新增normal_retired&&as_retired，等待身份可用和逻辑退休。没有清journal或冷复位协调器来绕过失败。开发包还保留声明顺序编译错误，以及明确SIGTERM停止的错误测试启动；它们均不算成功恢复。

三个已有生产层改写+一个reader新增，其余{len(inherited)}份生产RTL继承；普通与二次故障的选定生产源一致。旧方案和公共源码保持不变。配置过程在冷域，工作目标复位不改变绑定；authority排空/退休/fault进入系统围栏、恢复与重试。这里只支持一个绑定快照；没有提供快照轮换或与保存路径一起原子发布的协议。

选定完整系统 Vivado2022.2 U280 OOC：{int(util['LUT'])} LUT / {int(util['FF'])} FF / {util['BRAM']:g} BRAM / {int(util['DSP'])} DSP；零latch/blackbox/file-agent，{facts['logical_ports']}逻辑端口/{facts['port_bits']}位。较上一版99321LUT/66384FF增{int(util['LUT'])-99321}LUT/{int(util['FF'])-66384}FF。默认32slots/16384frames、诊断关闭；不是独立组件4537LUT数，也不是布局布线/Fmax/板卡收益。较早source的综合单独保存，不冒充选定版。

六归档{files}文件均实际移走原目录、解压并重新审计，审计JSON逐字节一致；当前{len(sources)}源/审核依赖另冻结于 results/authority_query_sources_20261025。基础check通过。完整机器证据见 authority_query_20261025.json；开发反例“审计通过”只表示证据核验通过。

重跑：先以 build.py 和 build_retry_tb.py 生成本variant；`python3 scripts/run_authority_query.py /tmp/B_state_residency_offer_20261025/新目录`，二次故障追加 `--authority-fault`；然后 `audit_authority_query.py 同目录`。归档位于 results/offer_archives_20261025，恢复复审回执位于 results/*authority_query*restore_20261025.json。

统一checkpoint仍不完整：owner真实快照、路径buffer、labels/目录、design cache、history/价格、配置/journal及query sequence/epoch/version下限尚未绑定成可冷恢复的同代图像。328标签集仍为已知外部流，design backing保留；本轮价格数值不变，frontier不保存。下一优先为统一描述/快照轮换、序号与版本下限恢复，再验证warm非零owner和未知页。快照真实性/不可变、任意reroute、回绕/容量、耐掉电及板卡证据仍缺。goal active。
'''
 (ROOT/'results/authority_query_20261025.md').write_text(md)
 prefix=f'''# 通用owner authority已接入完整查询（2026-10-25，优先历史）

详见 results/authority_query_20261025.md/.json、authority_query_coverage_20261025.json 和 hardware/variants/authority_query_v1/CONTRACT.md。选定authority_query_v4/retry_v3，三生产层改写+reader新增，{len(inherited)}生产RTL继承。六行表只作正常probe期望值，不再生成authority回复；第八路AXI实际读完整初始owner图像，单快照绑定design64/checkpoint32/generation64。

32槽/单槽共四例owner B故障及其后的snapshot R二次SLVERR，全部恢复并完整CPU重跑。首次二次故障status6/journal1保留，显式新query/version重试修复1项、journal清零；真实328标签写回/核验，非mock。普通故障原七AXI+四图像共22文件与旧基线字节一致；周期{cycles['ordinary']['full_5']}/{cycles['ordinary']['pressure_5']}，二次故障{cycles['authority_retry']['full_5']}/{cycles['authority_retry']['pressure_5']}，不是加速结论。

修复目标rst误清reader绑定，以及私有rearm仅AXI排空却未逻辑退休的过早target reset，实际反例保留。完整U280 OOC {int(util['LUT'])}LUT/{int(util['FF'])}FF/{util['BRAM']:g}BRAM/{int(util['DSP'])}DSP，零latch/blackbox/file-agent。六归档{files}文件实际恢复复审一致，{len(sources)}当前源冻结。

仍只有一个绑定初始快照与已知328标签；本轮完整query authority key的初始owner为空，warm非零/overflow仅此前组件验证。统一checkpoint同代发布、轮换、query序号/epoch/version下限冷恢复、未知页/旧prev/frontier、实际价格/回绕/容量/耐掉电/板卡仍缺。下一优先统一描述与恢复下限，goal active。以下保留历史。

'''
 for name in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/name;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','archives':6,'archive_files':files,'source_files':len(sources),'utilization':util}))
if __name__=='__main__':main()
