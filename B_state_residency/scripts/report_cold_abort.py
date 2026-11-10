"""Freeze abort-cancellation evidence after actual restore and re-audit."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['cold_abort_unfixed_v1','cold_abort_fixed_v1'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(v['status']=='passed'and v['audit_byte_identical']for v in receipts.values())
a=json.loads((base/names[1]/'source_bound_audit.json').read_text());assert a['status']=='passed'
closure=ROOT/'results/cold_abort_sources_20261026';closure.mkdir();paths=[*sorted((ROOT/'hardware/variants/cold_abort_v1').glob('*.sv')),*sorted((ROOT/'hardware/variants/cold_abort_v1').glob('*.py')),ROOT/'hardware/variants/cold_abort_v1/CONTRACT.md',*[ROOT/'scripts'/n for n in ['run_cold_abort.py','audit_cold_abort.py','audit_cold_abort_negative.py','report_cold_abort.py','verify_rtl_bundle.py','audit_route_fault_axi.py']]];sources={}
for p in paths:
 n=str(p.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
for n in ['query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv']:
 assert sha(base/names[1]/'sources'/n)==sha(ROOT/'hardware/variants/cold_abort_v1'/n)
report={'status':'passed','cases':a['cases'],'negative':json.loads((base/names[0]/'source_bound_audit.json').read_text()),'archives':receipts,'sources':sources,'scope':a['limits'],'remaining':['Partial path/query import and AXI-in-flight interruption tests.','Normal-start full-system regression and new root synthesis/timing.','Runtime authority rotation, general snapshots, durable floors/authentication and board evaluation.']}
(ROOT/'results/cold_abort_20261026.json').write_text(json.dumps(report,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body='''# 启动完成被abort中断：反例与修复（2026-10-26）

旧版 cold_boot_v1 仅以 rst 取消门控。完整系统在 G2/checkpoint18、八配置回执、328标签核验和原生path/query导入完成后，保持boot成功回复；abort与消费请求同拍时，旧版仍输出成功。cold_abort_unfixed_v1保留预期失败，不算成功恢复。

cold_abort_v1唯一生产差异是gate work_rst(rst||abort)。相同stimulus下成功回复立即屏蔽，恢复资格取消，8周期业务和lease释放保持关闭。lease不强制撤销。之后在同一RTL实例显式cold reset，外部DDR文件不重新装载，重新配置、重建328标签并导入path/query，再验证旧seq1拒绝、seq2 CPU oracle和双ripup。32槽/单槽均通过；全部8AXI字节重放、最终owner图像和42owner probes通过。第二轮查询仍43poll/42expand/176candidate/122cost，共享263946/554512 refs1→2→1→0。

两归档实际恢复并重审audit字节一致。当前源冻结results/cold_abort_sources_20261026。原cold_boot_v1及其历史归档保持，用于反例比较；后续实验应采用cold_abort_v1连接。

中断点已完全退休，本轮不证明AXI/导入流中途取消或无复位恢复。普通启动回归、新顶层综合/时序、运行中authority轮换、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电和板卡仍缺。周期包含两轮恢复、查询、探针和撤销，不作加速比较；goal active。
'''
(ROOT/'results/cold_abort_20261026.md').write_text(body)
header='''# 启动完成abort反例已修复（2026-10-26，优先历史）

详见 results/cold_abort_20261026.md/.json、hardware/variants/cold_abort_v1/CONTRACT.md。旧cold_boot_v1在恢复完成回复被保持时未接入abort取消，完整系统复现“abort与消费同拍仍输出成功”。唯一生产差异：gate work_rst(rst||abort)。同一stimulus修复后屏蔽成功、清除资格并保持业务/lease释放封锁；不强制释放可能持有事务的lease。

32槽/单槽在同一实例cold reset、不重新装载外部DDR，第二轮328标签重建与path/query导入成功；旧seq1拒绝、seq2 CPU oracle43poll/42expand/176candidate/122cost及共享refs1→2→1→0通过。全部8AXI重放/最终owner和42probes通过。旧失败与新成功两归档实际恢复复审一致，源冻结results/cold_abort_sources_20261026。后续使用cold_abort_v1；旧variant保留为历史反例。

本轮只覆盖已完全退休的完成回复边界。下一优先导入流/AXI中途中断、普通启动回归及新顶层综合，再运行中authority换代。无复位恢复、通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('abort evidence and handoff frozen',len(sources))
