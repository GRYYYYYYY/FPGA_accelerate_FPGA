"""Persist partial-stream cancellation coverage after restore/re-audit."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['cold_stream_abort_v1','cold_stream_late_v1'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(v['status']=='passed'and v['audit_byte_identical']for v in receipts.values())
audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names};assert all(a['status']=='passed'for a in audits.values());assert len(audits[names[0]]['cases'])==4 and len(audits[names[1]]['cases'])==2
closure=ROOT/'results/cold_stream_sources_20261026';closure.mkdir();paths=[]
for v in names:
 d=ROOT/'hardware/variants'/v;paths+=sorted(d.glob('*.sv'))+sorted(d.glob('*.py'))+[d/'CONTRACT.md']
paths += [ROOT/'scripts'/n for n in ['run_cold_stream_abort.py','audit_cold_stream_abort.py','run_cold_stream_late.py','audit_cold_stream_late.py','report_cold_stream.py','verify_rtl_bundle.py','audit_route_fault_axi.py']];sources={}
for p in paths:
 n=str(p.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
for v in names:
 for n in ['query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv']:assert sha(base/v/'sources'/n)==sha(ROOT/'hardware/variants'/v/n)
report={'status':'passed','audits':audits,'archives':receipts,'sources':sources,'remaining':['AXI-in-flight read/write abort with transaction retirement.','Normal-start full-system regression and synthesis/timing for the new root.','Runtime authority rotation/general snapshots, durable floors/authentication, unknown pages/price/epoch/capacity and board proof.']}
(ROOT/'results/cold_stream_20261026.json').write_text(json.dumps(report,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body='''# 部分路径/query导入取消通过（2026-10-26）

生产RTL与cold_abort_fixed_v1逐字节相同，本轮扩充完整系统覆盖：path在39/78字中断、query在5/10与9/10字中断，32槽/单槽共六例。path第一slot整条已送达仍不发布；query在第9字已送达last_sequence=1时，已发布sequence_seen/last_sequence仍0。真实取消回复status2；保持错误回复8周期期间业务与lease释放均关闭。

query实际S握手与bundle独立核对：部分5/9字前缀后，在同一实例cold reset、不重装外部DDR文件，完整10字重新导入，逐字值/次序/last一致。路径/query状态的被动观察不生成任何恢复回复；不是生产导出API。

每例第二轮328标签重建/核验、路径与query完整导入通过；旧seq1拒绝，seq2独立CPU oracle43poll/42expand/176candidate/122cost，42owner probes及共享refs1→2→1→0通过。全部8AXI逐字节重放与最终可写图像/owner一致。两归档实际恢复重审，audit字节一致，当前源冻结results/cold_stream_sources_20261026。

这是capacity0/同网双路径fixture的部分导入取消与cold-reset重试，不是无复位恢复或AXI在途中断。普通启动回归、新顶层综合/时序、运行中authority轮换、通用多net/overflow快照、持久化下限/认证、未知页/价格/回绕/容量/断电和板卡仍缺。周期包含两轮恢复/查询/探针/撤销，不解释为加速。goal active。
'''
(ROOT/'results/cold_stream_20261026.md').write_text(body)
header='''# 部分恢复流取消通过（2026-10-26，优先历史）

详见 results/cold_stream_20261026.md/.json、hardware/variants/cold_stream_abort_v1/CONTRACT.md和cold_stream_late_v1/CONTRACT.md。生产root/gate与cold_abort_fixed_v1逐字节不变。path39/78、query5/10与9/10中断，32槽/单槽共六例；第一条path整条与query序号下限分别已送达，仍未发布，真实取消status2，错误回复保持8周期业务/lease释放关闭。

query实际S流逐字与bundle比对，部分前缀后同一实例cold reset、不重装外部DDR，完整10字恢复。各例第二轮328标签/路径/序号导入、旧seq1拒绝、CPU q2 43poll/42expand/176candidate/122cost、42owner probes及refs1→2→1→0通过。全部8AXI/最终图像审核通过，两归档实际恢复复审audit一致；源冻结results/cold_stream_sources_20261026。

尚未AXI在途中断或无复位恢复；下一优先真实R/B在途取消及退休、普通启动回归与新顶层综合。运行中authority换代、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('partial stream evidence and handoff frozen',len(sources))
