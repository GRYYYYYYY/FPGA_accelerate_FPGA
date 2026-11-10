"""Freeze the completed eight-case matrix only after actual restored audits."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

base=Path('/tmp/B_state_residency_offer_20261025')
queue=base/'native_retirement_matrix_queue_v1'
qm=json.loads((queue/'manifest.json').read_text())
assert qm['status']=='observed' and qm['stage']=='complete', 'matrix still owns its outputs'
report=ROOT/'results/native_retirement_matrix_20261027.json'
assert sha(report)==qm['result_sha256']
r=json.loads(report.read_text())
assert r['status']=='eight_behavioral_cases_passed' and r['total_case_file_comparisons']==216
assert r['cases']==qm['cases'] and len(r['cases'])==7
assert sha(queue/'runner.py')==qm['runner_sha256']==sha(ROOT/'scripts/run_native_retirement_matrix_queue.py')
assert {c['target']for c in r['cases']}=={
    'native_matrix_off_full_v1','native_matrix_off_pressure_v1',
    'native_matrix_on_full_v1','native_matrix_on_pressure_v1',
    'native_matrix_retry_cancel_full_v1','native_matrix_retry_cancel_pressure_v1','native_matrix_retry_crc_full_v1'}
anchor_path=ROOT/'results/native_matrix_crc_pressure_anchor_20261027.json'
anchor=json.loads(anchor_path.read_text())
assert r['anchor']==anchor and sha(anchor_path)==qm['anchor_sha256']
assert anchor['matched_production_sources']==133 and len(anchor['matched_files'])==27
names=[c['target']for c in r['cases']]+[Path(anchor['existing_run']).name]
assert len(set(names))==8
expected={c['target']:c for c in r['cases']}
struct=base/'native_retirement_synth_v1'
sm=json.loads((struct/'manifest.json').read_text())
sa=json.loads((struct/'source_bound_audit.json').read_text())
assert sha(struct/'source_bound_audit.json')==r['structural_audit_sha256']
assert sa['status']=='passed' and sa['check_timing_counts']['loops']==0
assert sa['manifest_sha256']==sha(struct/'manifest.json')
srp=ROOT/'results/native_retirement_synth_v1_restore_20261025.json'
sr=json.loads(srp.read_text())
assert sha(srp)==r['structural_restore_sha256'] and sr['status']=='passed' and sr['audit_byte_identical']
assert sr['audit_sha256']==sha(struct/'source_bound_audit.json')
audits={};manifests={};receipts={}
for name in names:
    p=base/name
    a=json.loads((p/'source_bound_audit.json').read_text())
    m=json.loads((p/'manifest.json').read_text())
    rp=ROOT/'results'/f'{name}_restore_20261025.json';receipt=json.loads(rp.read_text())
    assert a['status']==receipt['status']=='passed' and receipt['audit_byte_identical']
    assert a['manifest_sha256']==sha(p/'manifest.json')
    assert receipt['audit_sha256']==sha(p/'source_bound_audit.json') and len(a['exact_comparisons'])==27
    if name in expected:
        e=expected[name]
        assert sha(rp)==e['restore_sha256'] and receipt['archive_sha256']==e['archive_sha256']
        assert sha(p/'source_bound_audit.json')==e['audit_sha256'] and a['finish_time']==e['finish_time']
    else:
        assert sha(rp)==anchor['existing_restore_sha256']
        assert sha(p/'source_bound_audit.json')==anchor['existing_audit_sha256']
        assert a['finish_time']==anchor['finish_time']
    assert set(m['rtl'])==set(sm['rtl']) and len(m['rtl'])==133
    for n in m['rtl']:
        assert sha(p/'sources'/n)==m['sources'][n]['sha256']==sm['sources'][n],(name,n)
    audits[name]=a;manifests[name]=m;receipts[name]=receipt

frozen=ROOT/'results/native_retirement_matrix_sources_20261027'
assert not frozen.exists()
md=ROOT/'results/native_retirement_matrix_20261027.md';assert not md.exists()
lines=['# 同源八项行为矩阵通过','',
       '关闭/开启优化、取消重试、CRC重试各含32槽和单槽；CRC单槽复用已直接核对原参考的anchor，其余七例串行执行。每例27份输出及周期精确比较，共216项；八归档均实际恢复且审计字节一致。', '',
       '| 实验 | 结束仿真时间 | 比较文件 |','|---|---:|---:|']
for name in names:lines.append(f"| {name} | {audits[name]['finish_time']} | 27 |")
lines += ['', '全部133份生产RTL逐文件匹配已验证开启版OOC。该OOC零组合环，但10ns下布局前WNS仍为-7.111ns，不代表物理时序或板卡验收。关闭版OOC结果另列，不能由本行为矩阵推断。', '',
          '范围仍为固定价格/history、既有真实四查询与可信初始快照。任意重定价、持久化floor/认证、自然overflow分配回收、物理实现和板卡收益未由本矩阵证明。后续query native exclusion候选不在这八项结果内。','']
md.write_text('\n'.join(lines));frozen.mkdir()
files={};source_map={};seen={}
def copy(src,rel):
    dst=frozen/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(dst)==sha(src)
    files[str(rel)]=dict(source=str(src),sha256=sha(dst))
for name in names:
    p=base/name;source_map[name]={}
    for n,e in manifests[name]['sources'].items():
        src=p/'sources'/n;h=sha(src);assert h==e['sha256']
        if h not in seen:
            rel=Path('sources')/name/n;copy(src,rel);seen[h]=str(rel)
        source_map[name][n]=seen[h]
    for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('reports')/name/n)
    copy(ROOT/'results'/f'{name}_restore_20261025.json',Path('reports')/f'{name}_restore.json')
copy(queue/'manifest.json',Path('reports/queue_manifest.json'))
copy(srp,Path('reports/structural_restore.json'))
for n,h in qm['tools'].items():
    assert sha(queue/'tools'/n)==h==sha(ROOT/'scripts'/n)
    copy(queue/'tools'/n,Path('scripts')/n)
for n in ['run_native_retirement_matrix_queue.py','freeze_native_retirement_matrix.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for src in [report,md,anchor_path,struct/'source_bound_audit.json']:
    copy(src,Path('reports')/('structural_audit.json'if src.parent==struct else src.name))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,
    cases=8,case_file_comparisons=216,timing_qualified=False,scope=r['scope']),indent=2,sort_keys=True)+'\n')
print('NATIVE_RETIREMENT_MATRIX_FROZEN',len(files),'files')
