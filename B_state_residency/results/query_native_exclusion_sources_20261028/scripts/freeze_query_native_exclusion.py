"""Freeze restored native query tests without claiming integrated timing benefit."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/query_native_exclusion_unit_v1')
ap=p/'source_bound_audit.json';a=json.loads(ap.read_text())
mp=p/'manifest.json';m=json.loads(mp.read_text())
rp=ROOT/'results/query_native_exclusion_unit_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert a['status']==r['status']=='passed' and r['audit_byte_identical']
assert a['manifest_sha256']==sha(mp) and r['audit_sha256']==sha(ap)
assert len(a['cases'])==12 and m['status']=='observed'
report=ROOT/'results/query_native_exclusion_20261028.json';assert not report.exists()
report.write_text(json.dumps(dict(status='twelve_native_controller_cases_passed',audit=a,restoration=r,
    scope='Native query lifecycle with modeled service/search/route backends, default compatibility and three overlap negatives. Full-system port exclusion, full-system exact regression and matched synthesis still required.'),indent=2,sort_keys=True)+'\n')
md=ROOT/'results/query_native_exclusion_20261028.md';assert not md.exists()
md.write_text('''# Query接口互斥候选原生12例通过

baseline/default/exclusive各覆盖正常完整单元回归与service/search/route三种请求受理同拍回复。正常例每例28项生命周期结果检查；默认模式四例的完整事件和结束时间均与基线一致，exclusive正常例也一致。exclusive三种重叠输入返回status7，route已完成时保留committed1。正常例逐周期检查三对READY/reply VALID互斥，没有force/deposit。

独立审计12例通过，378文件归档已实际恢复且audit字节一致。候选两源及源码绑定二态分析、builder、runner、auditor和结果冻结。

这里只验证原生query_lifecycle和模拟后端；未把该候选接入完整四查询系统，未证明完整系统三接口的所有实际轨迹，也没有新综合网表或时序改善结论。后续先做实际三接口监视及27输出/周期精确回归，再匹配OOC测量。旧十源八项矩阵结论不自动适用于本候选。
''')
f=ROOT/'results/query_native_exclusion_sources_20261028';assert not f.exists();f.mkdir();files={}
def copy(src,rel):
    dst=f/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(src)==sha(dst);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
v=ROOT/'hardware/variants/query_native_exclusion_v1'
for mode in ['baseline','fixed']:
    for n in ['query_lifecycle.sv','query_residency_system.sv']:copy(v/mode/n,Path('variant')/mode/n)
for n in ['build_tb.py','manifest.json','CONTRACT.md']:copy(v/n,Path('variant')/n)
for n in ['run_query_native_exclusion.py','audit_query_native_exclusion.py','freeze_query_native_exclusion.py','analyze_query_native_exclusion.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('reports')/n)
for src in [report,md,rp,ROOT/'results/query_native_exclusion_20261027.json',ROOT/'results/query_ready_path_hypothesis_20261027.json']:
    copy(src,Path('reports')/src.name)
for c in m['cases']:
    name=f"{c['mode']}_{c['early']}"
    for n in ['tb.sv','events.txt','simulate.log']:copy(p/name/n,Path('cases')/name/n)
(f/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,scope=a['scope']),indent=2,sort_keys=True)+'\n')
print('QUERY_NATIVE_EXCLUSION_FROZEN',len(files),'files')
