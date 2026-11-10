"""Freeze the AXI physical-drain / frontend-retirement counterexample and fix."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['cold_axi_unfixed_v1','cold_axi_fixed_v1'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(v['status']=='passed'and v['audit_byte_identical']for v in receipts.values())
a=json.loads((base/names[1]/'source_bound_audit.json').read_text());assert a['status']=='passed'and len(a['cases'])==4
closure=ROOT/'results/cold_axi_sources_20261026';closure.mkdir();d=ROOT/'hardware/variants/cold_axi_abort_v1';paths=sorted(d.glob('*.sv'))+sorted(d.glob('*.py'))+[d/'CONTRACT.md']+[ROOT/'scripts'/n for n in ['run_cold_axi_abort.py','audit_cold_axi_abort.py','audit_cold_axi_negative.py','report_cold_axi.py','verify_rtl_bundle.py','audit_route_fault_axi.py']];sources={}
for p in paths:
 n=str(p.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
for n in ['query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv']:assert sha(base/names[1]/'sources'/n)==sha(d/n)
report={'status':'passed','cases':a['cases'],'negative':json.loads((base/names[0]/'source_bound_audit.json').read_text()),'archives':receipts,'sources':sources,'remaining':['Normal-start full-system regression and new-root synthesis/timing.','Runtime authority rotation, general multi-net/overflow snapshots and no-reset recovery.','Durable floors/authentication, unknown pages/price/epoch/capacity, power failure and board evaluation.']}
(ROOT/'results/cold_axi_20261026.json').write_text(json.dumps(report,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body='''# AXI在途取消启动后的回复退休修复（2026-10-26）

完整系统反例cold_axi_unfixed_v1：真实AR受理、R尚未发出时abort；R排空后前端仍卡LRSP。8192周期后phase2/all_drained1/normal_retired0/backend_idle0，旧成功回复被启动门控一起屏蔽，无法退休。

cold_axi_abort_v1新增16bit已接受host回复归属，实际request/response handshake置位/清位，abort不清。新请求仍用原mask封锁，旧回复使用mask|owned退休，payload/status原样保持。修复版32槽/单槽各R、B两边界，共四例通过。读cut有待接收R，返回5字段与bundle首条逻辑记录一致；写cut AW=B+1，退休时AW=B。这里abort取消本次启动，不能撤销已经接受的DDR事务：原native读/flush均成功完成后才退休。

回复保持8周期期间不开放新请求或boot成功。完全物理/逻辑退休后，同一实例cold reset，不重新装载外部DDR，328标签/path/query重新恢复。旧seq1拒绝、CPU q2 43poll/42expand/176candidate/122cost、42owner probes和共享refs1→2→1→0通过。四例全8AXI/最终可写图像审核通过。旧失败与新成功两归档实际恢复复审，audit字节一致，当前源冻结results/cold_axi_sources_20261026。

普通启动完整回归、新顶层综合/时序仍缺；下一优先补齐，再进行运行中authority换代。无复位恢复、通用多net/overflow快照、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍未证明。周期含两轮恢复、取消/退休、查询与撤销，不是加速结论。goal active。
'''
(ROOT/'results/cold_axi_20261026.md').write_text(body)
header='''# AXI在途取消后的回复退休修复（2026-10-26，优先历史）

详见 results/cold_axi_20261026.md/.json 和 hardware/variants/cold_axi_abort_v1/CONTRACT.md。真实AR受理/R前abort的旧版反例：AXI排空但前端8192周期仍phase2/all_drained1/normal_retired0/backend_idle0。新增16bit已接受host回复归属，abort不清；请求mask继续封锁，回复mask|owned只让旧回复退休，不伪造payload/status。

32槽/单槽各读R、写B在途边界，共四例通过。读数据逐字等于bundle，写cut AW=B+1、退休AW=B；原native读/flush成功完成。旧回复背压8周期，新请求/boot成功仍关闭；完整物理与逻辑退休后才cold reset，同实例不重装外部DDR重建328标签/path/query。旧seq1拒绝、CPU q2 43poll/42expand/176candidate/122cost、42owner probes及refs1→2→1→0通过。全8AXI/最终图像与两归档实际恢复复审一致，源冻结results/cold_axi_sources_20261026。

后续使用cold_axi_abort_v1；旧variant保留历史反例。下一优先普通启动完整回归与新顶层综合/时序，再运行中authority换代。无复位恢复、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('AXI cancellation evidence and handoff frozen',len(sources))
