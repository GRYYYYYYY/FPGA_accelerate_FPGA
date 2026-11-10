from pathlib import Path
import json,hashlib,shutil,copy,datetime
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names=['route_checkpoint_join_v3','route_checkpoint_normal_v2','checkpoint_lease_guard_v2','route_checkpoint_join_synth_v1','route_checkpoint_fault_regression_v1'];audits={};receipts={};manifests={}
 for name in names:
  p=ROOT/'results'/name;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/(name+'_restore_20261025.json')).read_text());assert a['status']==r['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json');audits[name]=a;receipts[name]=r;manifests[name]=json.loads((p/'manifest.json').read_text())
 syn=audits['route_checkpoint_join_synth_v1'];old=json.loads((ROOT/'results/recovery_retry_synth_v1/source_bound_audit.json').read_text());delta={k:syn['utilization'][k]-old['utilization'][k]for k in syn['utilization']}
 comp=ROOT/'results/route_checkpoint_join_normal_comparison_20261025.json';assert json.loads(comp.read_text())['status']=='passed'
 for name in names[:2]:assert audits[name]['unchanged_production_RTL_dat']==117 and audits[name]['modified_production_components']==6
 for core in ['route_commit_controller.sv','route_commit_host_adapter.sv','residency_system.sv','search_residency_system.sv','query_residency_system.sv','checkpoint_lease_guard.sv']:
  reference=sha(ROOT/'results/route_checkpoint_normal_v2/sources'/core)
  assert all(sha(ROOT/'results'/name/'sources'/core)==reference for name in ['route_checkpoint_join_v3','route_checkpoint_join_synth_v1','route_checkpoint_fault_regression_v1'])
 oldcov=ROOT/'results/checkpoint_coverage_20261025.json';cov=copy.deepcopy(json.loads(oldcov.read_text()));cov['parent_sha256']=sha(oldcov);cov['status']='incomplete';cov['meaning']='Saved-route checkpoint now integrated with actual AXI-backed two-query/ripup lifecycle under a production lease; all other backing retained. Full consistent checkpoint still incomplete.'
 for o in cov['obligations']:
  if o['state']=='saved_connection_paths':o.update(status='integrated_verified_on_retained_backing',remaining='Path stream needs external storage and trusted matching owner/checkpoint generation. Default remains two slots/MAX_PATH32. Owner/image generation binding and durable/full-system restore remain open.')
  if o['state']=='query_sequence_epoch_and_version_floors':o['status']='runtime_preserved_during_route_only_reset_not_serialized'
  if o['state']=='journal_and_atomic_checkpoint_publication':o['status']='runtime_journal10_preserved_during_path_lease_not_snapshot_atomic_publication'
 cov['selected_join_audit_sha256']=sha(ROOT/'results/route_checkpoint_join_v3/source_bound_audit.json');cov['next_experiment']='Introduce a versioned checkpoint descriptor bound to owner/design/labels/config/journal and sequence floors; produce generic authority from a checkpoint owner image, not the six-row q1 fixture. Continue reducing path staging multiport cost.'
 (ROOT/'results/checkpoint_join_coverage_20261025.json').write_text(json.dumps(cov,indent=2)+'\n')
 frozen=ROOT/'results/route_checkpoint_join_sources_20261025';assert not frozen.exists();frozen.mkdir()
 files=list((ROOT/'hardware/variants/route_checkpoint_join_v1').glob('*.py'))+list((ROOT/'hardware/variants/route_checkpoint_join_v1').glob('*.sv'))+[ROOT/'hardware/variants/route_checkpoint_join_v1/CONTRACT.md']
 files += [ROOT/'scripts'/name for name in ['run_route_checkpoint_join.py','audit_route_checkpoint_join.py','run_checkpoint_lease_guard.py','audit_checkpoint_lease_guard.py','prepare_query_lifecycle_synth.py','audit_route_checkpoint_join_synth.py','compare_route_checkpoint_join_normal.py','run_route_checkpoint_fault_regression.py','audit_route_checkpoint_fault_regression.py','audit_natural_axi.py','audit_route_fault_axi.py','summarize_route_checkpoint_join.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py']]
 files += [ROOT/'results/route_checkpoint_unit_v8/sources/route_commit_controller.sv',ROOT/'results/recovery_retry_normal_v1/sources/tb_query_lifecycle_join.sv',ROOT/'results/search_fault_retire_matrix_v6/sources/tb_query_fault.sv',ROOT/'results/route_checkpoint_fault_regression_v1/sources/runner.py']
 hashes={}
 for p in files:
  n=str(p.relative_to(ROOT));q=frozen/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);hashes[n]=sha(q)
 (frozen/'manifest.json').write_text(json.dumps({'status':'frozen','files':hashes,'dependencies':'Verified recovery_retry_normal_v1 baseline and route_checkpoint_unit_v8 component; each result archive includes complete executed RTL/dat closure. Prior CPU/graph assets remain in their verified archives.'},indent=2)+'\n')
 total=sum(r['files']for r in receipts.values());pc=audits['route_checkpoint_join_v3']['path_checkpoint'];normal=manifests['route_checkpoint_normal_v2']['cases'];fault=audits['route_checkpoint_fault_regression_v1'];assert fault['outcomes']=={'recovered_retry':2}and audits['checkpoint_lease_guard_v2']['retired_error_release']
 report=dict(status='integrated_path_checkpoint_verified',full_checkpoint_status='incomplete',path_checkpoint=pc,normal_results={k:v['result']for k,v in normal.items()},guard_checks=26,guard_error_release_scope='Modeled predicates unit, not an AXI fault during checkpoint ownership.',fault_regression=fault,synthesis=syn['utilization'],synthesis_delta=delta,netlist_facts=syn['netlist_facts'],actual_restored_files=total,archives=len(names),source_files=len(hashes),source_manifest_sha256=sha(frozen/'manifest.json'),normal_comparison_sha256=sha(comp),coverage_sha256=sha(ROOT/'results/checkpoint_join_coverage_20261025.json'),development_sha256=sha(ROOT/'results/route_checkpoint_join_development_20261025/index.json'),results={name:{'audit_sha256':sha(ROOT/'results'/name/'source_bound_audit.json'),'restore_receipt':str(ROOT/'results'/(name+'_restore_20261025.json'))}for name in names},limits='Only saved-route loss is diagnosed/restored. Owner/design/labels/history/allocator/backing and sequence remain resident; external path buffer and matching snapshot trusted, no full snapshot identity/generation binding. Two slots/MAX_PATH32, table idle. No checkpoint-held AXI fault handoff, arbitrary unknown page/price/wrap, durability or board/timing proof.')
 (ROOT/'results/route_checkpoint_join_20261025.json').write_text(json.dumps(report,indent=2)+'\n')
 md=f'''# 路径 checkpoint 接入系统围栏与真实 AXI（2026-10-25）

路径状态现在由实际硬件导出并重新导入，已接入统一query wrapper、route adapter和实际AXI-backed owner链。q2搜索期间提出的checkpoint lease等待当前查询、回复及物理事务退休后才取得；持有期间阻塞16个host lane及query/route/recovery新请求。

试验首先实际运行q1/q2，RTL从两条已保存路径导出78字/312字节到外部测试台缓冲。诊断端口仅复位路径核心，随后拒绝expected_crc翻转1位的导入，接受原RTL图像并重新导出核验，最后执行实际AXI ripup，两个共享资源refs 2→1→0。CPU路径只作为独立oracle，不用于填充恢复流。

| 容量 | 等待lease周期 | 持有周期 | 全部入口争用周期 | 路径复位周期 | 路径CRC |
|---|---:|---:|---:|---:|---|
'''
 for mode in ['full','pressure']:
  v=pc[mode];md+=f"| {mode} | {v['pending_acquire_cycles']} | {v['held_cycles']} | {v['contended_cycles']} | {v['diagnostic_path_reset_cycles']} | {v['crc32']} |\n"
 md+=f'''
持有期间无FS/FD/FB/route/recovery/owner journal接受，未新增物理AXI访问。journal=10、last_sequence=2和2304位配置描述保持。两容量的七AXI日志及四个完整物理图像与旧正常基线逐字节一致（table闲置），四阶段完整owner与CPU一致。完整双query仍为116 POLL/114展开/447判定/293成本。lease和诊断背压是固定fixture，不能把这些等待/持有周期当板卡checkpoint延迟或加速。

正常旁路两容量24份周期轨迹/AXI/图像与旧基线字节一致，周期657222/724963。启用保存、诊断复位、坏CRC、恢复和再导出的整段周期658736/726677，包含四条路径命令及时间对齐变化，不是单次checkpoint开销。

26项独立lease单元检查覆盖健康状态变差后，仍须等待物理/逻辑/route退休、旧回复消费和CPP输入清空才能释放权限。普通错误锁存不再造成lease释放死等。这是受控谓词单元证据；没有在真实AXI checkpoint持有期间注入错误并验证完整接管。

新增接口全部闲置时，32槽/单槽的owner真实B错误回归均恢复并完整重跑q1，修复1项实际副作用。独立CPU/七AXI字节/完整owner/标签审计通过，保留已知328标签、q1六行authority的既有边界。此两例不代替checkpoint持有期故障试验。

完整系统默认32槽/16384帧U280 OOC：{syn['utilization']['LUT']:g} LUT、{syn['utilization']['FF']:g} FF、{syn['utilization']['BRAM']:g} BRAM、{syn['utilization']['DSP']:g} DSP，相对原恢复重试版增加{delta['LUT']:g} LUT/{delta['FF']:g} FF。387逻辑端口/57270位，零latch/blackbox/file-agent；五个原组件改写、一个lease guard新增、117继承RTL/dat保持。默认ENABLE_TEST_INJECTION=0关闭诊断路径复位，CPP lease/流接口仍保留。没有place/route、时钟约束/Fmax或板卡测量，暂存资源开销仍需优化。

五归档共{total}文件实际恢复复审，audit逐字节一致；{len(hashes)}源文件冻结。开发阶段的声明顺序编译失败、lease单元驱动边沿错误、初步成功结果保留于route_checkpoint_join_development_20261025。故障回归原manifest沿用了旧scope描述，已保留原文件，仅修正文案并记录SHA；独立审计证明其余命令、来源与结果内容未改变。

下一步仍是完整checkpoint：

- 用同一版本化描述符绑定路径、owner primary/pool/allocator、design/cache、history/价格、标签页/目录、配置及journal；路径流与owner同一代快照目前由可信调用方保证。
- 实现通用checkpoint owner authority读取，扩展六行q1 fixture；当前q2新增资源的恢复不能由旧authority保证。
- 序列化并恢复query序号、epoch、成功/尝试版本下限。这里last_sequence只是未被路径复位影响，尚未证明全系统reset后恢复。
- 明确frontier/递归状态重启边界，推进未知页/旧prev、真实价格变化、回绕/容量回收和持久化；优化暂存多读口及考虑双bank BRAM。

详见checkpoint_join_coverage_20261025.json和hardware/variants/route_checkpoint_join_v1/CONTRACT.md。完整研究目标保持active。
'''
 (ROOT/'results/route_checkpoint_join_20261025.md').write_text(md)
 prefix=f'''# 路径checkpoint接入系统与真实AXI通过（2026-10-25，优先历史）

详见 results/route_checkpoint_join_20261025.md/.json、checkpoint_join_coverage_20261025.json 和 hardware/variants/route_checkpoint_join_v1/CONTRACT.md。硬件q1/q2完成后，在排空且无既有offer时取得显式lease，封锁16host/query/route/recovery。RTL导出78字→诊断仅丢失路径→坏CRC拒绝→原图像重放/再导出→实际AXI共享ripup refs2→1→0；32槽/单槽均通过。其他backing保留，不是全系统checkpoint恢复。

六派生组件（5改写+1新增guard）、117继承RTL/dat保持。全部入口争用1424周期、持有1425周期，无新增AXI访问，journal10/last_sequence2/配置保持，七AXI和四图像与旧基线字节一致。正常24文件字节一致，周期657222/724963；CPP闲置时两例owner B错误完整恢复重跑。lease26单元含退休后错误释放，未证明真实checkpoint持有期AXI错误接管。

完整U280 OOC 99321LUT/66384FF/160.5BRAM/23DSP，387端口57270位，零latch/blackbox/file-agent，默认诊断关闭。较旧版增10659LUT/2859FF，暂存开销仍高，无时序/板卡收益。五归档{total}文件实际恢复复审一致，{len(hashes)}源冻结，开发失败和scope文案修正证据保留。

下一优先版本化checkpoint描述绑定路径与owner等全部状态，通用authority读取与query序号/epoch/版本下限恢复。外部路径buffer、同代owner可信前提、仅两slot/MAX_PATH32、未知页/旧prev、frontier重启、真实价格/回绕/容量/耐掉电/板卡仍缺。继续优化暂存多读口。goal active。以下保留历史。

'''
 for name in ['AGENTS.md','NEXT_STEPS.md','README.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/name;p.write_text(prefix+p.read_text())
 (ROOT/'results/route_checkpoint_join_supervision_20261025.json').write_text(json.dumps({'status':'completed','updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Deterministic existing bounded XSim runners and independent audits; MCP source observed after300s handoff without restarting.','synthesis':{'session':'vivado-20261025-201429-d30eb79f','elapsed_s':628.811,'exit_code':0,'session_closed':True},'real_runs':6,'guard_unit_checks':26,'actual_restored_files':total,'goal':'active; full checkpoint incomplete'},indent=2)+'\n')
 print(json.dumps({'status':'integrated_path_checkpoint_verified','full_checkpoint':'incomplete','restored_files':total,'sources':len(hashes),'synthesis':syn['utilization']}))
if __name__=='__main__':main()
