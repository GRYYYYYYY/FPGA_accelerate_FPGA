"""Freeze audited/restored held-success and consumption-edge abort runs."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025')
names=['warm_late_held_v2','warm_late_edge_v2','warm_late_held_pressure_v2','warm_late_edge_pressure_v2']
restores={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names}
audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names}
assert all(x['status']=='passed'and x['audit_byte_identical']for x in restores.values())and all(x['status']=='passed'for x in audits.values())
bm=json.loads((base/'warm_retry_system_v2/manifest.json').read_text())
for i,n in enumerate(names):
 m=json.loads((base/n/'manifest.json').read_text());assert m['late_mode']==i%2 and set(m['cases'])==({'full_5'}if i<2 else {'pressure_5'})
 for f in m['rtl']:
  if f!='tb_query_fault.sv':assert m['sources'][f]['sha256']==bm['sources'][f]['sha256'],f
closure=ROOT/'results/warm_late_abort_sources_20261026';closure.mkdir();sources={};d=ROOT/'hardware/variants/warm_late_abort_v1'
paths=[*d.glob('*.py'),*d.glob('*.sv'),*d.glob('*.md')]+[ROOT/'scripts'/n for n in ['run_warm_late_abort.py','audit_warm_late_abort.py','report_warm_late_abort.py']]
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in names:assert sha(d/'tb_late.sv')==sha(base/n/'sources/tb_query_fault.sv')
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'results/warm_late_abort_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=restores,sources=sources),indent=2)+'\n')
body='''# 成功回复发布后的abort边界与J0重试通过（2026-10-26）

详见results/warm_late_abort_20261026.json与hardware/variants/warm_late_abort_v1/CONTRACT.md。32槽与单槽各覆盖成功回复背压后abort、成功回复消费同沿abort，共四例。真实完成G2/CP18六项修复与三类回执后，原生coordinator已提交5/3/5、journal清零并发布status0/cookie c0010001/corrected6。held场景继续在abort下背压8周期，edge场景于同一实际消费边沿断言abort；成功回复VALID及全部检查的状态/cookie/corrected保持稳定，不能把已经发布的成功改写成取消失败。

消费后仍warm owned/fault、业务关闭，current5与attempt floor5/J0保留，不能称此前成功被回滚。旧回复/fence退休后，相同attempt5原生status1拒绝，更高6/query0/price6以新cookie非冷复位重试成功，不重装工作DDR。J0分支无authority/owner journal访问，不伪造六键GET；重新恢复并验证全部328标签、78路径字和10query字后才允许正常业务。CPU oracle43poll/42expand/176candidate/122cost、最终标签、两路径拆线及共享2→1→0通过，全部8AXI/DDR重放通过。

本轮仅改独立TB，生产RTL逐文件SHA等于warm_retry_system_v2；成功发布前的事件/周期与既有shared-last基线精确匹配。四归档实际恢复后重审audit字节一致，源冻结results/warm_late_abort_sources_20261026。行为仿真不能作为板卡速度、任意竞态或取消回滚证明。

固定价格/history、一个net两路径/capacity0与两个确定边沿仍是本轮范围。晚到abort是否需另设显式状态/确认尚未形成通用接口；持久化floor/认证、运行中快照、多net/overflow、任意变价距离有效性、综合时序及板卡仍缺。下一优先扩展真实多net/overflow与资源回收生命周期，避免只在capacity0单net fixture上得出普遍结论；研究继续，goal active。
'''
(ROOT/'results/warm_late_abort_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('warm late abort evidence frozen',len(sources))
