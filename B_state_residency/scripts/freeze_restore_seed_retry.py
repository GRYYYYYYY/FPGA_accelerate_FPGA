"""Freeze audited four-case optimized restore failure/retry; never overwrite old evidence."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
names=[f'restore_seed_retry_{mode}_{case}_v1'for mode in ['cancel','crc']for case in ['full','pressure']]
audits={};restores={};manifests={}
for name in names:
    p=base/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert m['status']=='observed'and a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_restore_seed_retry.py')
    assert r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],n
    audits[name]=a;restores[name]=r;manifests[name]=m
canon=manifests[names[0]]['sources']
assert all(m['sources']==canon for m in manifests.values())
frozen=ROOT/'results/restore_seed_retry_sources_20261027';frozen.mkdir()
files={}
def copy(p,rel):
    target=frozen/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);files[str(rel)]=sha(target)
for n in canon:copy(base/names[0]/'sources'/n,Path('sources')/n)
for name in names:
    for n in ['manifest.json','source_bound_audit.json']:copy(base/name/n,Path('cases')/name/n)
for n in ['run_restore_seed_retry.py','audit_restore_seed_retry.py','audit_restore_seed_retry_records.py','freeze_restore_seed_retry.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['build.py','build_tb.py','base_tb.py','failure_task.sv','CONTRACT.md']:
    copy(ROOT/'hardware/variants/restore_seed_retry_v1'/n,Path('variant')/n)
copy(ROOT/'results/restore_seed_retry_20261027.md',Path('report.md'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files),indent=2,sort_keys=True)+'\n')
development=ROOT/'results/restore_seed_retry_audit_development_sources_20261027'
for p in sorted(development.iterdir()):copy(p,Path('audit_development')/p.name)
copy(ROOT/'results/restore_seed_retry_audit_development_20261027.json',Path('audit_development/record.json'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files),indent=2,sort_keys=True)+'\n')
report=dict(status='passed',cases=audits,restores=restores,
    source_freeze=str(frozen),source_freeze_sha256=sha(frozen/'manifest.json'),source_files=len(files),
    audit_development=json.loads((ROOT/'results/restore_seed_retry_audit_development_20261027.json').read_text()),
    scope='Four complete-system behavioral cases: optimized third native field write cancellation and last-record CRC corruption for32/one slot. Retained journal, retired failure, native attempt7 rejection and attempt8 noncold retry; complete781-label/156-path/10-query restore and CPU q4 replay, all12AXI/final DDR. Only two deterministic failure points, fixed price/history, trusted initial clones/baseline/historical path metadata. No resource/timing/board, persistent authorization or arbitrary-failure proof.')
(ROOT/'results/restore_seed_retry_20261027.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('RESTORE_SEED_RETRY_FROZEN',len(files))
