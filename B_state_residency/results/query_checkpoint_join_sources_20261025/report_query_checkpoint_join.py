from pathlib import Path
import json,shutil,re
from run_checkpoint_authority import ROOT,sha

def main():
 scratch=Path('/tmp/B_state_residency_offer_20261025');names=['query_checkpoint_join_v3','query_checkpoint_import_v1','query_checkpoint_idle_v1','query_checkpoint_join_development_20261025','query_checkpoint_join_synth_v1'];evidence={}
 for n in names:
  p=scratch/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/f'{n}_restore_20261025.json').read_text());assert a['status']==r['status']=='passed'and r['audit_byte_identical']and sha(p/'source_bound_audit.json')==r['audit_sha256'];evidence[n]={'audit':a,'restore':r}
 units={n:json.loads((scratch/n/'manifest.json').read_text())for n in names[:3]};selected=units[names[0]]
 for n,m in units.items():
  for rtl in selected['rtl']:
   if not rtl.startswith('tb_'):assert m['sources'][rtl]['sha256']==selected['sources'][rtl]['sha256']
 frozen=ROOT/'results/query_checkpoint_join_sources_20261025';frozen.mkdir();paths=list((ROOT/'hardware/variants/query_checkpoint_join_v1').glob('*'))+[ROOT/'scripts'/n for n in ['run_query_checkpoint_join.py','audit_query_checkpoint_join.py','audit_query_checkpoint_join_development.py','report_query_checkpoint_join.py','prepare_query_lifecycle_synth.py','audit_authority_query_synth.py','run_checkpoint_authority.py','run_query_fault.py','audit_route_fault_axi.py']];sources={}
 for p in paths:
  if p.is_file():shutil.copyfile(p,frozen/p.name);sources[str(p.relative_to(ROOT))]=sha(p)
 base=scratch/'authority_query_v4/sources';baseline={}
 for n in ['query_lifecycle.sv','query_residency_system.sv']:
  shutil.copyfile(base/n,frozen/('baseline_'+n));baseline[n]=sha(base/n)
 (frozen/'manifest.json').write_text(json.dumps({'status':'passed','sources':sources,'baseline':baseline},indent=2)+'\n')
 coverage={'status':'incomplete','validated':['native query ledger interface inside actual eight-AXI query system under shared checkpoint lease','pending set on production import acceptance and cleared only after successful completion consumption','32/1slots query-only diagnostic loss, CRC and valid-CRC/wrong-generation rejection, import, stale-sequence rejection','32/1slots diagnosis disabled production import and no-command regression','all six CPU query reruns and actual328label restore; eight AXI/four final images identical to base'], 'missing':['unified boot admission gate with real owner/path/labels/directory/design/history/price/config/query receipts','same-boundary capture and atomic publication of a new bundle generation; authority snapshot rotation','query frame currently binds recovery-baseline generation, not a new current-working-state owner image','persistent sequence/attempt_version/query floors and durable authenticated commit','full cold reset tests including warm nonzero owners, unknown pages/oldprev/frontier policy','actual price/epoch rollover/capacity failures, lease-held AXI recovery takeover, timing and board evidence'], 'next_concrete_steps':['define pending bundle generation for capture and bind every captured state to its new commit identity','capture real owner/allocator plus current working data and all label/directory records at a healthy quiescent boundary','collect real component restore receipts and keep boot work admission closed until every required receipt is valid','perform a full cold-restart warm-owner path/query test; do not substitute a one-module reset or constant done flags'], 'prior_component':'results/query_checkpoint_20261025.json','prior_authority_system':'results/authority_query_20261025.json'}
 files=sum(e['restore']['files']for e in evidence.values());util=evidence[names[-1]]['audit']['utilization'];facts=evidence[names[-1]]['audit']['facts'];cycles={n:{k:int(re.search(r'cycles=(\d+)',v['result'])[1])for k,v in m['cases'].items()}for n,m in units.items()};inherited=len([n for n in selected['rtl']if not n.startswith('tb_')and n not in ['query_lifecycle.sv','query_residency_system.sv']])
 report={'status':'passed','research_goal':'active','evidence':evidence,'coverage':coverage,'cycles':cycles,'utilization':util,'facts':facts,'delta_from_authority_query':{'LUT':util['LUT']-104144,'FF':util['FF']-70377},'changed_production':['query_lifecycle.sv','query_residency_system.sv'],'inherited_rtl':inherited,'archive_files':files,'frozen_sources':len(sources)+2,'sources':sources,'baseline':baseline,'physical_files_compared':72,'basic_check':'python3 scripts/run.py check passed'}
 (ROOT/'results/query_checkpoint_join_20261025.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'results/query_checkpoint_join_coverage_20261025.json').write_text(json.dumps(coverage,indent=2)+'\n')
 md=f'''# 查询序号checkpoint接入实际系统（2026-10-25）

原生query_lifecycle组件已接入authority_query_v4完整层级，新增qc_cp_*接口并共用实际checkpoint lease。生产变化仅query_residency_system与query_lifecycle；其余{inherited}份生产RTL继承。原生核心与此前14查询/27checkpoint独立验证的组件逐字节一致。普通请求、查询、路由、恢复仍由真实层级和八路AXI驱动，没有以mock后端代替本轮工作。

| 场景 | 32槽周期 | 单槽周期 | 核验 |
|---|---:|---:|---|
| query局部诊断丢失后导入 | {cycles[names[0]]['full_5']} | {cycles[names[0]]['pressure_5']} | pending104周期；last_sequence1→0→1 |
| 诊断关闭的生产导入 | {cycles[names[1]]['full_5']} | {cycles[names[1]]['pressure_5']} | pending88周期；last_sequence保持1 |
| checkpoint接口闲置 | {cycles[names[2]]['full_5']} | {cycles[names[2]]['pressure_5']} | 与旧835704/892858周期保持 |

六例均先实际owner B SLVERR →修复已写但未确认的1项owner变更→真实恢复/读取核验328标签→完整CPU查询重跑：73polls、72expands、271candidates、171cost输出和6项owner提交。之后前四例执行40B流：导出0、坏期望CRC拒绝1、CRC正确但generation高32位错误拒绝1、正确导入0；所有回复持有6周期。成功导入回复尚未消费时pending仍为1，不能释放lease；消费后才清除。诊断reset是注册且有lease/空闲前提，仅query控制器丢失，非force。

导入开始即置生产qc_restore_pending，并非只在诊断下生效。失败后必须重试成功才能解除；导出不能解除。checkpoint guard命令busy包含pending/query_cp_busy；pc_quiet允许checkpoint自身busy而仍保留全部其他退休条件。path/query checkpoint互斥且query优先，ready与实际valid的仲裁一致。诊断默认参数0，生产导入例也按0编译；闲置回归同样关闭诊断。

恢复后将空闲slot1、合法design/version/query/price/source/sink等命令字段明确重建，再重放已经消费的sequence1。回复status1、prepare/cleanup/commit均0；source不是前次握手后故意翻转的无效引脚，因此不把其他参数拒绝当成序号保护。路径slot、完整2304bit配置描述、journal和authority绑定保持，nativeledger按图像恢复。

独立审计重建归档生成器、校验实际S/M全部字、以zlib验证CRC，并核对CPU poll/candidate/cost/path/label/owner、全部八路AXI字节和完整最终内存。每例8AXI+4图像与接入前authority_query_v4字节一致，共72文件比较；新增序号流和拒绝没有增加物理服务流量。不是全部trace周期等价或板卡加速结论。两个早期三命令诊断版本保留为开发证据，不代替选定四命令/生产默认关闭验证。

完整默认32slots/16384frames U280 Vivado2022.2 OOC：{int(util['LUT'])}LUT/{int(util['FF'])}FF/{util['BRAM']:g}BRAM/{int(util['DSP'])}DSP，零latch/blackbox/file-agent，{facts['logical_ports']}逻辑端口/{facts['port_bits']}位。较旧104144LUT/70377FF增{int(util['LUT'])-104144}LUT/{int(util['FF'])-70377}FF。实际集成资源不等于独立组件增量简单相加，未布局布线/定时闭合/板卡测量。source662.463秒、临时MCP会话已关闭。

五归档{files}文件均实际移走原目录、解压并重新独立审计，审计文件逐字节一致。{len(sources)+2}当前源/审核依赖及原两组件另冻结于results/query_checkpoint_join_sources_20261025。基础check通过，旧基线/其他方案未修改。机器证据见query_checkpoint_join_20261025.json，接口约束见hardware/variants/query_checkpoint_join_v1/CONTRACT.md。

运行：先执行该variant的build.py和build_tb.py；`python3 scripts/run_query_checkpoint_join.py /tmp/B_state_residency_offer_20261025/新目录`；生产无丢失模式加`--no-loss`，闲置回归再加`--bypass`；完成后audit_query_checkpoint_join.py同目录。

尚未完成全系统冷恢复。所有其他状态仍保留；k_cold_rst会清ledger、pending和lease。本轮frame的generation来自当前authority基线，基线owner图像早于当前working owner变更；后者及journal保留才使本次局部恢复一致。不能把该frame与早先初始owner快照单独配对冷恢复，也不能因generation相同就宣称同一时间点完整图像。恢复协调器attempt_version/query下限尚未序列化。

下一步是健康静止边界的新bundle提交身份与实际全状态捕获：提供待提交generation，捕获owner/allocator、query/path流、完整labels/目录、design/history/价格、实际当前配置和journal边界，完成各组件真实恢复receipt后才发布并放开boot业务。当前静态配置描述不一定等于恢复后的active版本，必须显式保存实际上下文。不能用软件常量done或只丢一个模块代替完整冷启动测试。warm非零owner、未知页/旧prev/frontier、实际价格变化/回绕/容量、耐掉电/认证/不可变、lease持有期AXI故障接管和板卡仍缺；goal active。
'''
 (ROOT/'results/query_checkpoint_join_20261025.md').write_text(md)
 prefix=f'''# 查询checkpoint已接入真实系统租约（2026-10-25，优先历史）

详见 results/query_checkpoint_join_20261025.md/.json、query_checkpoint_join_coverage_20261025.json 和 hardware/variants/query_checkpoint_join_v1/CONTRACT.md。两生产组件改写，{inherited}生产RTL继承。qc_cp复用实际lease，生产导入受理即pending，只在成功导入回复消费后清除；错误/部分导入及 held成功回复不能释放lease。query/path流互斥，诊断默认关闭。

32/单槽共六例：真实owner B恢复及完整CPU重跑后，局部query状态丢失导入、默认关闭诊断的生产导入、接口闲置。前四例40B导出、坏CRC拒绝、CRC正确但generation高32位错误拒绝、正确重放；旧sequence1以空闲slot/合法上下文提交而被拒绝且零prepare/commit。pending104/88周期。全部8AXI+4图像每例字节同旧基线，共72文件比较通过；不是加速。

完整U280 OOC {int(util['LUT'])}LUT/{int(util['FF'])}FF/{util['BRAM']:g}BRAM/{int(util['DSP'])}DSP，零latch/blackbox/file-agent；较旧增{int(util['LUT'])-104144}/{int(util['FF'])-70377}。五归档{files}文件实际恢复复审一致，{len(sources)+2}当前源冻结。仍只丢query控制器，其余状态保留，不是冷启动；cold reset会清pending/lease。

frame的generation绑定旧authority基线，不等于当前working owner的新快照；禁止与初始owner图像单独配对冷恢复。下一优先健康边界pending bundle generation/实际全状态捕获与真实receipt boot门控、原子提交/快照轮换，保存实际active配置与attempt下限，再完整warm-owner冷恢复。未知页/旧prev/frontier、价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

'''
 for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/n;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','archives':5,'files':files,'sources':len(sources)+2,'utilization':util}))
if __name__=='__main__':main()
