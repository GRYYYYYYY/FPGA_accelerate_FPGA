from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025')
names=['multi_owner_capacity_negative_v4','multi_owner_capacity_fixed_v1','multi_owner_capacity_bound_v1','multi_owner_normal_full_v1','multi_owner_normal_pressure_v1']
audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names}
restores={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names}
assert all(a['status']=='passed'for a in audits.values())and all(x['status']=='passed'and x['audit_byte_identical']for x in restores.values())
assert audits[names[0]]['expected_failure']and not audits[names[1]]['expected_failure']
d=ROOT/'hardware/variants/multi_owner_recovery_v1'
for n in names[1:]:assert sha(base/n/'sources/recovery_coordinator.sv')==sha(d/'recovery_coordinator.sv')
closure=ROOT/'results/multi_owner_recovery_sources_20261026';closure.mkdir();sources={}
paths=[*d.glob('*.py'),*d.glob('*.sv'),*d.glob('*.cpp'),*d.glob('*.md'),ROOT/'hardware/search/owner_state_v1/owner_store.hpp']+[ROOT/'scripts'/n for n in ['run_multi_owner_recovery.py','audit_multi_owner_recovery.py','run_capacity_bound.py','audit_capacity_bound.py','run_multi_owner_normal.py','audit_multi_owner_normal.py','report_multi_owner_recovery.py']]
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'results/multi_owner_recovery_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=restores,sources=sources),indent=2)+'\n')
body='''# 同资源多net与满overflow池的恢复顺序修复（2026-10-26）

详见results/multi_owner_recovery_20261026.json及hardware/variants/multi_owner_recovery_v1/CONTRACT.md。真实iteration2快照的overflow池capacity/live均53734且无free项。节点208292原net6632/ref1、net17601/ref2；基于真实快照构造确定压力变更（非自然路由轨迹），通过实际owner引擎删除主owner、加入net0、两次增加net17601引用，四次mutation产生三个去重journal键。旧生产coordinator先补回net6632，在后续net0释放空间之前遇status5 CAPACITY，恢复status3/J3；negative_v4保留实际反例。

新候选只对匹配cookie/原GET值且无写入的INC CAPACITY拒绝延后一次，继续处理其余journal，再追加一轮修正并最终完整验证。真实组件fixed_v1通过：先释放net0并修正net17601，再补回net6632，4次修正/J0，池大小仍53734、allocator回到满池。追加轮有独立authority cookie；永久CAPACITY模拟单元恰2次拒绝后status3/J1，不能无限循环或放行业务。

独立CPU模型与原CPU快照映射检查修复例21个真实owner操作/全部响应，逐条匹配16个物理record写，比较最终146284032字节；其余节点/池条目不被破坏，live和snapshot AXI全部重放通过。新coordinator用于完整系统正常G2回归，32槽/单槽共28文件及周期精确匹配旧基线。五归档实际恢复重审audit字节一致，源冻结results/multi_owner_recovery_sources_20261026。

范围必须分开：多net满池测试为真实owner/authority/coordinator组件，但reconfigure/labels回调模拟；完整系统回归仍为原capacity0单net两路径。尚未完成完整warm系统的多net快照发布/路径查询恢复，也无通用所有排列、并发回收、任意变价、持久化floor/认证、运行时快照、综合时序或板卡性能结论。

下一优先依NEXT_INTEGRATION.md，将已有真实iteration2 prepared-query、capacity53734布局和数值oracle接到当前query_residency_system/三方发布/保存状态恢复；不要重写已验证owner基本单元或混用原q1/q2单netoracle。新候选coordinator位于multi_owner_capacity_fixed_v1/sources，其余warm层级沿用warm_retry_system_v2。研究继续，goal active。
'''
(ROOT/'results/multi_owner_recovery_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('multi-owner capacity recovery evidence frozen',len(sources))
