from pathlib import Path
import json,shutil,re
from run_checkpoint_authority import ROOT,sha

def main():
 scratch=Path('/tmp/B_state_residency_offer_20261025');names=['bundle_capture_v3','bundle_capture_development_20261025','bundle_capture_synth_v1'];evidence={}
 for n in names:
  p=scratch/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/f'{n}_restore_20261025.json').read_text());assert a['status']==r['status']=='passed'and r['audit_byte_identical']and sha(p/'source_bound_audit.json')==r['audit_sha256'];evidence[n]={'audit':a,'restore':r}
 run=scratch/'bundle_capture_v3';m=json.loads((run/'manifest.json').read_text());bundles={n:json.loads((run/n/'bundle/manifest.json').read_text())for n in ['full_5','pressure_5']};directories={n:json.loads((run/n/'bundle/directory.json').read_text())for n in bundles};tests=json.loads((run/'bundle_integrity_tests.json').read_text());assert tests['checks']==24 and tests['status']=='passed'
 a,b=bundles.values();same=[n for n in a['components']if a['components'][n]['sha256']==b['components'][n]['sha256']];different=sorted(set(a['components'])-set(same));assert len(same)==11 and different==['directory.json','labels.bin']and a['context']==b['context']
 frozen=ROOT/'results/bundle_capture_sources_20261025';frozen.mkdir();paths=[p for p in(ROOT/'hardware/variants/bundle_capture_v1').rglob('*')if p.is_file()and p.suffix in ['.py','.sv','.md']]+[ROOT/'scripts'/n for n in ['run_bundle_capture.py','audit_bundle_capture.py','decode_bundle_directory.py','package_rtl_bundle.py','verify_rtl_bundle.py','test_rtl_bundle_integrity.py','audit_bundle_capture_development.py','audit_bundle_capture_synth.py','report_bundle_capture.py','prepare_query_lifecycle_synth.py','audit_authority_query_synth.py','run_checkpoint_authority.py','run_query_fault.py','audit_route_fault_axi.py']];sources={}
 for p in paths:shutil.copyfile(p,frozen/p.name);sources[str(p.relative_to(ROOT))]=sha(p)
 base=scratch/'query_checkpoint_join_v3/sources';baselines={}
 for n,dest in [('query_residency_system.sv','baseline_query_root.sv'),('expansion_20261024/pager/backend/backing_frame_directory_small.sv','baseline_directory.sv')]:shutil.copyfile(base/n,frozen/dest);baselines[dest]={'source':str(base/n),'sha256':sha(base/n)}
 (frozen/'manifest.json').write_text(json.dumps({'status':'passed','sources':sources,'baselines':baselines},indent=2)+'\n')
 coverage={'status':'incomplete','validated':['pending-generation query capture handshake, decreasing generation rejection, default running-generation export and valid-CRC future-generation import rejection','same held RTL lease: query/path streams, actual working DDR, current context and healthy recovery-attempt floors','passive accepted directory protocol reconstructs authoritative mapping and all328present labels; native state not fabricated from arrays','trusted single-writer host reference staging/fsync/manifest+COMMIT/rename package','24private-clone integrity checks; physical layouts differ across capacities but logical labels agree'], 'missing':['production directory metadata export and full cold-restoration consumer','cold reset business admission gate driven by real owner/config/labels/path/query receipts','runtime authority snapshot rotation and atomic hardware activation of the new bundle','persistent global replay floor/authentication and actual power-cut validation','multi-context/general unknown-page snapshots, arbitrary paths/overflow owner capture beyond this capacity0 one-path fixture','actual price changes/epoch rollover/capacity/board timing and performance'], 'next_experiment':'Use saved bundle in a fresh RTL instance. Configure effective version4/query2/price4, rebuild labels via actual IO with hardware CRC/count readback receipt, import saved path and sequence under G2, keep all business closed until real receipts complete, reject stale sequence1 then compare followup_q2 sequence2 CPU oracle and shared owner ripups. See CONTRACT.md for order.'}
 util=evidence[names[2]]['audit']['utilization'];facts=evidence[names[2]]['audit']['facts'];files=sum(e['restore']['files']for e in evidence.values());cycles={n:int(re.search(r'cycles=(\d+)',c['result'])[1])for n,c in m['cases'].items()};inherited=len([n for n in m['rtl']if not Path(n).name.startswith('tb_')and n not in ['query_residency_system.sv','expansion_20261024/pager/backend/backing_frame_directory_small.sv']])
 report={'status':'passed','research_goal':'active','evidence':evidence,'bundles':bundles,'directory_summary':{n:{k:v for k,v in d.items()if k!='owners'}for n,d in directories.items()},'integrity_tests':tests,'coverage':coverage,'cycles':cycles,'utilization':util,'facts':facts,'delta_from_query_checkpoint_join':{'LUT':util['LUT']-105272,'FF':util['FF']-70954},'cross_capacity_identical_components':same,'cross_capacity_different_physical_components':different,'archive_files':files,'frozen_sources':len(sources)+len(baselines),'sources':sources,'baselines':baselines,'inherited_rtl':inherited,'basic_check':'python3 scripts/run.py check passed'}
 (ROOT/'results/bundle_capture_20261025.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'results/bundle_capture_coverage_20261025.json').write_text(json.dumps(coverage,indent=2)+'\n')
 md=f'''# 新提交代的健康边界参考bundle（2026-10-25）

选定bundle_capture_v3。运行实例仍绑定checkpoint17/G1（4294967297），在同一实际checkpoint lease下将query40B帧导出到待提交G2（4294967298），并导出真实路径312B。握手后故意改变generation引脚，流仍保留已接受值。降低代拒绝；合法CRC的G2图像在仍运行G1的实例中导入也拒绝；默认G1导出/导入完成后，捕获结束保持健康、lease持有、全部工作/AXI退休和frontier0。没有私有query reset，没有force或模拟authority返回值。

32槽/单槽实际owner B故障→328标签恢复/核验→完整CPU重跑后捕获，周期{cycles['full_5']}/{cycles['pressure_5']}。查询命令检查共5次，状态1/0/1/0/0；随后path流成功。全部既有8AXI+4图像与前基线同容量逐字节一致。周期包含验证事务和背压，不包含之后主机复制、hash、fsync或协议重建，不能当完整checkpoint延迟或加速。

| 内容 | 实际来源与校验 |
|---|---|
| working owner/allocator | 实际AXI写后的145MB primary及64B allocator，capacity0；6个保存路径资源ref1，旧journal键与已改变节点完全一致 |
| path/query | 硬件M流78字/10字；CRC32分别637ddbbb/6d0c23ca；query包含D/G2/version4/query2/price4/sequence1 |
| labels/directory | 实际3MB标签页与被动目录cmd/rsp重建的120个published frame；枚举全部328个present记录，与实际Z读回/CPU相同 |
| design/history/price等 | 完整实际design/cost图像；graph/table/connection六个immutable资源以长度/SHA256引用绑定，不重复复制 |
| 配置与恢复下限 | 实际2304bit旧描述、当前active与attempt4/query2/price4；按已有RTL cfg_payload规则只覆盖word70得到effective配置 |
| 新基线 | checkpoint18/G2，working owner已包含6项变化；新基线restore_journal为空，原实例仍保留旧G1/journal6 |

目录不是从测试台读取owners数组伪造：BUNDLE_TRACE观察器仅记录已接受native请求/回复、reset、memory_success/fence及lease结果。独立模型验证每个状态/分配/发布/lease/cookie转换，得到full/pressure的{directories['full_5']['protocol_commands']}/{directories['pressure_5']['protocol_commands']}次命令，120frame/328record。它仍是仿真被动协议跟踪，不是生产目录导出端口。非authoritative索引可重建；端点与目录cookie freshness必须在全退休冷会话内协调重启。

两bundle各{sum(x['bytes']for x in a['components'].values())}数据字节，13组件中11份字节一致；directory.json与labels.bin的物理顺序不同，但labels.records逻辑状态完全一致。不能将不同布局的页与目录混配。当前封装只核验本轮capacity0、一路径/6资源/单active context fixture，不宣称任意多net/overflow/多上下文全快照。

单写者主机参考发布：bundle.staging →逐文件fsync →manifest →COMMIT摘要 →fsync目录 →rename为bundle →fsync父目录。24检查包括2份有效包及22份拒绝：未提交/staging、缺COMMIT、摘要/身份错误，以及重算摘要后仍不合法的路径、query、目录映射、effective配置和attempt下限。源bundle字节不变。CRC/SHA提供完整性，本测试不证明断电恢复、签名认证或较早可信包防重放。

新功能生产逻辑只改query root。目录源仅增加BUNDLE_TRACE条件下的被动实例，生产不定义；其余{inherited}份RTL继承。完整U280 Vivado2022.2默认32/16384 OOC为{int(util['LUT'])}LUT/{int(util['FF'])}FF/{util['BRAM']:g}BRAM/{int(util['DSP'])}DSP，比105272/70954增{int(util['LUT'])-105272}/{int(util['FF'])-70954}。{facts['logical_ports']}逻辑端口/{facts['port_bits']}位，零latch/blackbox/file-agent/directory observer。无place/route/Fmax/板卡收益。临时MCP会话关闭。

三归档{files}文件实际移走原目录、解压并独立复审；包含重新运行24项完整性检查，审计JSON逐字节一致。{len(sources)+len(baselines)}当前源/依赖及两基线源另冻结于results/bundle_capture_sources_20261025。两个早期捕获版本作为开发证据保存，不冒充选定G2导入隔离/完整包核验。基础check通过，公共/其他方案基线未改。

复现：variant build.py/build_tb.py；run_bundle_capture.py新目录；audit_bundle_capture.py同目录 --before-bundle；对full_5与pressure_5分别package_rtl_bundle.py CASE；最后audit_bundle_capture.py同目录（含完整性检查）。verify_rtl_bundle.py CASE/bundle可单独验证。数据在归档中的full_5/bundle与pressure_5/bundle，机器证据bundle_capture_20261025.json。

尚未完成真实冷启动：host COMMIT不表示运行中authority换代。当前硬件仍G1；新实例需从完整可信G2包加载所有匹配状态，而不能单独拿query/path帧和早先初始owner组合。当前raw配置版本3与active4不同，恢复必须使用明确的effective4。下一步原生boot门控要从cold reset封锁业务，直到owner/配置、真实labels写回+读回CRC/count、path与query导入等全部实际receipt完成并消费，才放开；禁止常量done。已有CPU followup_q2可作为保存q1后冷恢复再执行sequence2分支的参考，验证共享owner1→2及真实ripup2→1→0。完整顺序见CONTRACT.md。

生产目录导出、全冷恢复consumer、实时namespace切换、全局持久化反重放下限、任意unknown页/旧prev/frontier、实际价格/回绕/容量、耐掉电与板卡仍缺。研究goal active。
'''
 (ROOT/'results/bundle_capture_20261025.md').write_text(md)
 prefix=f'''# 新提交代健康边界参考bundle通过（2026-10-25，优先历史）

详见 results/bundle_capture_20261025.md/.json、bundle_capture_coverage_20261025.json 和 hardware/variants/bundle_capture_v1/CONTRACT.md。选定bundle_capture_v3：qc_cp_generation握手锁存目标G2，降低代拒绝，G2导出不激活仍运行G1的authority；合法CRC未来代导入仍拒绝，默认G1重放保持。生产只改query root，目录仅加仿真条件观察器。

同一真实lease下导出query40B/path312B，捕获实际working owner/allocator/design/cost/labels与active/attempt上下文；目录由真实native握手重建120frame/328record，非数组伪造，仍非生产导出端口。新参考checkpoint18/G2吸收6个ref1资源，原实例仍G1/journal6。raw配置3须按实际active4覆盖word70。主机staging/fsync/manifest+COMMIT/rename包校验及24检查通过（2有效、22拒绝），未声称断电或认证/反重放。

两容量各330824322数据字节，13组件11份同字节，目录/标签物理布局不同而328逻辑record相同。完整U280 OOC {int(util['LUT'])}LUT/{int(util['FF'])}FF/{util['BRAM']:g}BRAM/{int(util['DSP'])}DSP，增{int(util['LUT'])-105272}/{int(util['FF'])-70954}，零latch/blackbox/file-agent/observer；三归档{files}文件实际恢复复审一致，{len(sources)+len(baselines)}当前源冻结。

本轮是健康静止点/host参考包，尚未冷恢复或运行中换代。下一明确实验：新RTL实例cold reset，按effective4/query2/price4配置G2；真实label IO重建并硬件CRC/count核验；path/query导入实际receipt齐备且完成回复消费后才解除boot业务门控；拒绝旧seq1，再用已有followup_q2 oracle执行seq2并验证warm共享owner1→2、双ripup2→1→0。当前capacity0一路径fixture，不宣称通用多net/overflow快照。生产目录导出、持久化下限/认证、unknown页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
 for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/n;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','archives':3,'files':files,'sources':len(sources)+len(baselines),'utilization':util,'cross_capacity_physical_differences':different}))
if __name__=='__main__':main()
