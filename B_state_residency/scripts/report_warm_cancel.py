from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['warm_cancel_unfixed_v1','warm_cancel_transition_v1','warm_cancel_fixed_v2','warm_cancel_normal_v2'];rs={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(r['status']=='passed'and r['audit_byte_identical']for r in rs.values());audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names};assert all(a['status']=='passed'for a in audits.values())
d=ROOT/'hardware/variants/warm_cancel_v1';closure=ROOT/'results/warm_cancel_sources_20261026';closure.mkdir();paths=[d/n for n in ['build.py','build_tb.py','query_residency_system.sv','search_residency_system.sv','residency_system.sv','recovery_coordinator.sv','tb_cancel.sv','CONTRACT.md','HALT_REARM_NOTES.md']]+[ROOT/'scripts'/n for n in ['run_warm_cancel.py','audit_warm_cancel.py','run_warm_cancel_regression.py','audit_warm_cancel_normal.py','report_warm_cancel.py']];sources={}
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv','recovery_coordinator.sv']:assert sha(d/n)==sha(base/'warm_cancel_fixed_v2/sources'/n)
assert sha(d/'tb_cancel.sv')==sha(base/'warm_cancel_fixed_v2/sources/tb_query_fault.sv')
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'results/warm_cancel_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=rs,sources=sources),indent=2)+'\n')
body='''# Warm查询取消的错误出口与退休修复通过（2026-10-26）

详见results/warm_cancel_20261026.json与hardware/variants/warm_cancel_v1/CONTRACT.md。真实G2共享故障修复后，在query原始镜像9/10字取消。两个实际反例：旧LABELS仍等成功joined，原生query错误回复已消费后仍卡住；只修错误出口会在旧query回复尚未消费时提前返回失败。最终LABELS错误独立转FAILWAIT，并以真实warm服务/回复退休约束失败完成，包含CF busy/回复观察。

warm_cancel_fixed_v2的32槽和单槽通过：原生query status2/CRC0保持8周期时恢复完成VALID始终0；消费后才返回status6，journal6/CP18保留，服务均退休。最终失败回复消费后仍HALT/owned/fault，业务关闭，未假装已经允许重试。实际工作owner图像等于G2快照，全部8AXI/DDR重放通过。健康六项共享恢复normal_v2两容量共28文件及周期精确匹配既有baseline。四归档实际恢复重审audit一致，源冻结results/warm_cancel_sources_20261026。

本轮不是AXI在途中断，也未实现失败后非冷复位重试、晚成功abort或任意取消点。下一优先HALT在旧回复/fence全部退休后，为新attempt6/query0/price6重新arm并选择新命令字段；真实G2只读复核保留journal，corrected0，再恢复保存状态/重试，详见HALT_REARM_NOTES.md。标签/AXI取消、通用多net/overflow、运行中快照、持久化认证、综合时序及板卡仍缺。研究继续，goal active。
'''
(ROOT/'results/warm_cancel_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('warm cancel completion evidence frozen',len(sources))
