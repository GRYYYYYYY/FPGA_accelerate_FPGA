"""Publish only audited and actually restored retry experiment results."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names=['recovery_retry_unit_v6','config_retry_unit_v2','recovery_retry_matrix_v2','recovery_retry_pressure_v1','recovery_retry_normal_v1','recovery_retry_synth_v1']
 audits={};receipts={}
 for n in names:
  p=ROOT/'results'/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/(n+'_restore_20261025.json')).read_text())
  assert a['status']==r['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json') and r['audit_sha256']==sha(p/'source_bound_audit.json') and r['audit_byte_identical'];audits[n]=a;receipts[n]=r
 cases={}
 for n in names[2:4]:cases.update(audits[n]['cases'])
 assert len(cases)==10 and all(c['outcome']=='recovered_retry'for c in cases.values())
 comp=ROOT/'results/recovery_retry_normal_comparison_20261025.json';assert json.loads(comp.read_text())['status']=='passed'
 syn=audits[names[-1]];old=json.loads((ROOT/'results/search_retire_synth_v6/source_bound_audit.json').read_text())
 source=ROOT/'results/recovery_retry_sources_20261025';assert not source.exists();source.mkdir()
 files=list((ROOT/'hardware/variants/recovery_retry_v1').glob('*.py'))+list((ROOT/'hardware/variants/recovery_retry_v1').glob('*.sv'))+[ROOT/'hardware/variants/recovery_retry_v1/CONTRACT.md']
 files+= [ROOT/'scripts'/n for n in ['run_recovery_retry_unit.py','run_config_retry_unit.py','audit_recovery_retry_unit.py','run_recovery_retry.py','audit_recovery_retry.py','run_recovery_retry_normal.py','audit_recovery_retry_normal.py','compare_recovery_retry_normal.py','prepare_query_lifecycle_synth.py','audit_recovery_retry_synth.py','audit_route_fault_axi.py','audit_natural_axi.py','summarize_recovery_retry.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py']]
 files += [ROOT/'hardware/variants/recovery_coordinator_v1/tb_recovery_coordinator.sv',ROOT/'hardware/variants/config_restore_v1/tb_config_restore.sv',ROOT/'results/recovery_retry_matrix_v2/sources/runner.py']
 hashes={}
 for p in files:
  n=str(p.relative_to(ROOT));q=source/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);hashes[n]=sha(q)
 (source/'manifest.json').write_text(json.dumps({'status':'frozen','files':hashes,'baseline':'results/recovery_fault_matrix_v2 (already archived/restored), results/search_fault_retire_matrix_v6 (success tail), results/search_retire_normal_v6, original unit TBs included'},indent=2)+'\n')
 report={'status':'passed','meaning':'Explicit fresh-command recovery retry after a second AXI fault; not autonomous retry or a full durable checkpoint.','cases':cases,'unit_checks':{'coordinator':39,'config_restore':32},'normal_comparison_sha256':sha(comp),'synthesis':syn['utilization'],'synthesis_delta':{k:syn['utilization'][k]-old['utilization'][k]for k in syn['utilization']},'netlist_facts':syn['netlist_facts'],'results':{n:{'audit_sha256':sha(ROOT/'results'/n/'source_bound_audit.json'),'restore_receipt':str(ROOT/'results'/(n+'_restore_20261025.json'))}for n in names},'actual_restored_files':sum(r['files']for r in receipts.values()),'source_files':len(hashes),'source_manifest_sha256':sha(source/'manifest.json'),'development_index_sha256':sha(ROOT/'results/recovery_retry_development_20261025/index.json'),'scope':'q1 six-owner authority +328 known labels, retained design backing, epoch3/version5 with same actual prices; no arbitrary checkpoint/reroute/unknown-page/wrap/capacity/durability/place-route/Fmax/board speedup.'}
 (ROOT/'results/recovery_retry_20261025.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# 恢复失败后的显式重试验证（2026-10-25）','', '十个真实二次AXI故障用例全部在新命令下恢复成功，并完整重跑q1查询。改动保留dirty journal、authority身份和配置描述，只有旧回复消费、物理AXI和内部回调全部退休后才清理恢复服务暂态。不是cold reset重建，也没有自动重试策略。','', '| 第二次故障位置 | 32槽 | 单槽 | 第二次恢复确认修复数 |','|---|---|---|---|']
 for fc,label in enumerate(['owner GET R','owner修复DEC B','标签eviction B','标签CHECKPOINT B','标签核验R'],1):lines.append(f'| {label} | 恢复并完整重跑 | 恢复并完整重跑 | {int(fc==1)} |')
 lines += ['', 'DEC B错误时物理扣减已生效，第一次确认数为0；第二次从实际owner计数读取后确认无需再扣减。其他标签故障同样保留journal，不能据此放行业务。每例第二次恢复均写入并核验328标签；重跑73 POLL、72展开、271候选判定、171成本调用，最终owner等于CPU精确一次提交。', '', '验证与可复现性：', '', '- 协调器39、配置控制器32项单元检查；包括旧回归、非法版本/查询/身份、待消费回复、物理/逻辑排空、意外authority回复、部分物理修复与标签失败重试。', '- 三生产组件修改，119继承RTL/dat不变；独立审计重建生成源，首轮故障语义与七AXI字节前缀对齐已审计基线，第二轮完整CPU轨迹、七AXI和完整内存图像校验。', '- 正常32槽/单槽双查询和共享ripup回归通过，24份周期轨迹、七AXI和完整图像与旧基线字节一致，周期657222/724963。', f"- 完整U280 OOC：{syn['utilization']['LUT']:g} LUT、{syn['utilization']['FF']:g} FF、{syn['utilization']['BRAM']:g} BRAM、{syn['utilization']['DSP']:g} DSP；相对v6增加{report['synthesis_delta']['LUT']:g} LUT、{report['synthesis_delta']['FF']:g} FF。零latch/blackbox/file-agent，无布线时序/板卡结论。", f"- 六归档共{report['actual_restored_files']}文件实际恢复并复审，audit逐字节一致；{len(hashes)}源文件冻结。", '', '开发记录保留于recovery_retry_development_20261025：原版单元重跑28项通过；新测试台紧凑64位加法赋值曾产生X，显式分支赋值及非X断言后通过，未以放松身份校验消除失败；初版真实测试台声明顺序编译失败也保留。未声称已确认仿真器缺陷根因。', '', '边界与下一步：', '', 'snapshot仍是外部可信生产者，须在旧尝试终止后以新cookie从头重放。仍仅已知q1六owner行/328标签，design backing保留；query3/version5未改变实际价格。下一优先完整checkpoint描述与覆盖、未知页及一般reroute；版本/epoch回绕、容量回收、持久化和板卡测量仍未完成。', '', '入口和协议见 `hardware/variants/recovery_retry_v1/CONTRACT.md`；详细源哈希、逐例内存核验、综合与归档收据见同名JSON及各结果目录。']
 (ROOT/'results/recovery_retry_20261025.md').write_text('\n'.join(lines)+'\n')
 prefix=f'''# 保留journal的恢复失败后重试通过（2026-10-25，优先历史）

详见 results/recovery_retry_20261025.md/.json 和 hardware/variants/recovery_retry_v1/CONTRACT.md。业务owner B错误后，恢复owner GET R/DEC B、标签eviction B/CHECKPOINT B/核验R二次真实故障，各32槽/单槽共10例全部在显式新命令下成功恢复并完整CPU重跑。保留journal/authority/配置描述，只在旧回复消费、物理和逻辑退休后REARM清理恢复暂态；新version/query身份拒绝旧尝试。DEC B已实际修复时重试不重复扣减。不是自动重试或完整checkpoint。

协调器39/配置32单元检查、真实七AXI/全图像/完整CPU与第一故障基线前缀审计通过。三生产组件改写、119继承RTL/dat保持；正常双查询共享ripup的24文件与旧基线字节一致，周期657222/724963。完整U280 OOC {syn['utilization']['LUT']:g}LUT/{syn['utilization']['FF']:g}FF/{syn['utilization']['BRAM']:g}BRAM/{syn['utilization']['DSP']:g}DSP，零latch/blackbox/file-agent。六归档{report['actual_restored_files']}文件实际恢复复审一致，{len(hashes)}源冻结，开发失败保留。无板卡加速结论。

下一优先完整checkpoint与未知页/一般reroute。仍q1六行authority/328已知标签、design backing保留、snapshot外部新cookie重放；实际价格未变，回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

'''
 for n in ['AGENTS.md','NEXT_STEPS.md','README.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/n;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','cases':len(cases),'restored_files':report['actual_restored_files'],'source_files':len(hashes),'synthesis':report['synthesis']}))
if __name__=='__main__':main()
