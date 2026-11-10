"""Freeze actual restored CP unit results, including the generic counterexample."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_units_v1')
m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
rp=ROOT/'results/checkpoint_edit_units_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert m['status']=='observed'and a['status']==r['status']=='passed'and r['audit_byte_identical']
assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_sha256']==sha(p/'source_bound_audit.json')
assert len(a['cases'])==12 and a['exact_trace_comparisons']==7 and a['generic_overlap_specialization_counterexample']
report=ROOT/'results/checkpoint_edit_units_20261028.json';assert not report.exists()
report.write_text(json.dumps(dict(status='twelve_checkpoint_unit_cases_passed',audit=a,restoration=r,
    full_system_validated=False,timing_qualified=False,
    scope='Checkpoint/rebase compatibility plus native permission/edit scenarios and explicit generic overlap counterexample. Modeled backend unit evidence only. Full-system CP-safe/edit port monitoring, exact replay and matched OOC remain required.'),indent=2,sort_keys=True)+'\n')
md=ROOT/'results/checkpoint_edit_units_20261028.md';assert not md.exists()
md.write_text('''# CP编辑互斥候选原生单元验证

baseline/default/exclusive各覆盖原checkpoint测试、原rebase测试、独立native_cp和generic_overlap场景，共12例。四组baseline/default完整事件与结束时间一致；合法checkpoint/rebase/native_cp的exclusive也一致，共7组比较。默认通用协议保留。

native_cp覆盖半流许可撤销且编辑、CRC正确重试恢复、导出背压及许可撤销、dirty标记保留。generic_overlap故意提供cp_safe真且编辑真的非原生输入：baseline/default拒绝，特化可接受。这是必须保持默认关闭的合同反例，不能称对任意接口安全。

独立审计与归档实际恢复audit字节一致，源码/工具/输入/回执冻结。这里只验证query_lifecycle与模型后端；尚无完整系统轨迹、匹配新综合网表或时序改善结论。下一先在完整系统监视真实cp_safe/edit端口并执行27输出/周期精确比较，再测OOC。
''')
f=ROOT/'results/checkpoint_edit_units_sources_20261028';assert not f.exists();f.mkdir();files={}
def copy(src,rel):
    dst=f/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(src)==sha(dst);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
v=ROOT/'hardware/variants/checkpoint_edit_exclusion_v1'
for mode in ['baseline','fixed']:
    for n in ['query_lifecycle.sv','query_residency_system.sv']:copy(v/mode/n,Path('variant')/mode/n)
for n in ['build.py','build_tb.py','manifest.json','CONTRACT.md']:copy(v/n,Path('variant')/n)
for n in ['run_checkpoint_edit_units.py','audit_checkpoint_edit_units.py','freeze_checkpoint_edit_units.py','analyze_checkpoint_edit_exclusion.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('reports')/n)
for src in [report,md,rp,ROOT/'results/checkpoint_edit_exclusion_20261028.json']:copy(src,Path('reports')/src.name)
for src in (p/'tools').rglob('*'):
    if src.is_file():copy(src,Path('tools')/src.relative_to(p/'tools'))
for c in m['cases']:
    name=f"{c['mode']}_{c['suite']}"
    for n in ['tb.sv',c['trace'],'simulate.log']:copy(p/name/n,Path('cases')/name/n)
(f/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,full_system_validated=False,timing_qualified=False),indent=2,sort_keys=True)+'\n')
print('CHECKPOINT_EDIT_UNITS_FROZEN',len(files),'files')
