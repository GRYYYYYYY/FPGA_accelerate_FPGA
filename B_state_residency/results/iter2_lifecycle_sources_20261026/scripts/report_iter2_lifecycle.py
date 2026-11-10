from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['iter2_lifecycle_full_v5','iter2_lifecycle_pressure_v5']
audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names};restores={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names}
assert all(a['status']=='passed'for a in audits.values())and all(x['status']=='passed'and x['audit_byte_identical']for x in restores.values())
assert [audits[n]['case']for n in names]==['full','pressure']
d=ROOT/'hardware/variants/iter2_lifecycle_v1';closure=ROOT/'results/iter2_lifecycle_sources_20261026';closure.mkdir();sources={}
paths=[*d.glob('*.py'),*d.glob('*.sv'),*d.glob('*.md')]+[ROOT/'scripts'/n for n in ['run_iter2_lifecycle.py','audit_iter2_lifecycle.py','report_iter2_lifecycle.py']]
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in names:assert sha(d/'tb_iter2.sv')==sha(base/n/'sources/tb_query_fault.sv')
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'results/iter2_lifecycle_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=restores,sources=sources),indent=2)+'\n')
body='''# 真实iteration2接入当前完整查询生命周期通过（2026-10-26）

详见results/iter2_lifecycle_20261026.json及hardware/variants/iter2_lifecycle_v1/CONTRACT.md。选定full_v5/pressure_v5，真实connection170782/net26422/source66893/sink204279，完整sequence180327与存储version3/query1/price3分离。使用同一CPU prepared-state的design、146284032B owner primary/pool/allocator、history/price/net/CPS1及822条保守标签闭包，不混用原q1/q2 oracle。先通过原生PC租约/只读authority验证真实overflow链，再由当前query_lifecycle、自主search、实际heap POLL、回溯和owner引擎完成整条查询。

两容量均171poll/170expand/849candidate/421cost通过原CPU数值oracle；822标签与403逻辑页对应的全部3MB物理页（含空页）、全部8AXI逐字节重放通过。真实previous-pointer链含三个内部节点339193/558358/265324，提交refs1/4/5、occupancy1/2/1，节点558358另一net23916始终ref1。原生ripup回refs0/3/4，整个146MB owner图像逐字节等于输入，pool/allocator与其他net未破坏。重复sequence180327被status1拒绝且prepare_acked0，最终存储context仍3/1/3。

本轮不新增生产RTL修复，沿用已审计multi_owner_capacity_fixed_v1 coordinator和warm_retry_system_v2其余生产层级。两个归档实际恢复重审audit字节一致，源冻结results/iter2_lifecycle_sources_20261026。以上为行为仿真；本自然路径不新增overflow slot，不能将前轮组件满池修复与本轮正常查询合并为完整多net warm恢复结论。

仍缺本数据的G2三方发布、warm故障恢复、任意未知页/全图cache生成、任意变价、持久化floor/认证、综合时序和板卡收益。822条CPU未来读闭包是当前前提；恢复服务MAX_RECORDS仍512、旧fixture snapshot_count仍328，下一阶段须显式参数化到1024并迁移822流/实际path/query CRC。WARM_NEXT.md记录G1两项真实owner-B故障恢复的接入要求，以及G2后续query须新CPU oracle、不可重用已消费sequence的约束。研究继续，goal active。
'''
(ROOT/'results/iter2_lifecycle_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('iteration2 lifecycle evidence frozen',len(sources))
