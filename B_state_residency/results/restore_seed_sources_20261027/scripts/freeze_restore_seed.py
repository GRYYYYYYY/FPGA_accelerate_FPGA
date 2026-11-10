"""Freeze audited four-case restore ablation; never overwrite old evidence."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
names=[f'restore_seed_{mode}_{case}_v1'for mode in ['off','on']for case in ['full','pressure']]
audits={};restores={};manifests={}
for name in names:
    p=base/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert m['status']=='observed'and a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_restore_seed.py')
    assert r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],n
    audits[name]=a;restores[name]=r;manifests[name]=m
canon=manifests[names[0]]['sources']
assert all(m['sources']==canon for m in manifests.values())
frozen=ROOT/'results/restore_seed_sources_20261027';frozen.mkdir()
files={}
def copy(p,rel):
    target=frozen/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);files[str(rel)]=sha(target)
for n in canon:copy(base/names[0]/'sources'/n,Path('sources')/n)
for name in names:
    for n in ['manifest.json','source_bound_audit.json']:copy(base/name/n,Path('cases')/name/n)
for n in ['run_restore_seed.py','audit_restore_seed.py','audit_fourth_warm_records.py','freeze_restore_seed.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['build.py','build_tb.py','PLAN.md','CONTRACT.md']:
    copy(ROOT/'hardware/variants/restore_seed_bypass_v1'/n,Path('variant')/n)
copy(ROOT/'results/restore_seed_20261027.md',Path('report.md'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files),indent=2,sort_keys=True)+'\n')
comparison={}
for case in ['full','pressure']:
    old=audits[f'restore_seed_off_{case}_v1'];new=audits[f'restore_seed_on_{case}_v1'];a=old['behavioral_cycles'];b=new['behavioral_cycles']
    comparison[case]=dict(label_before=a['label_phase'],label_after=b['label_phase'],
        label_reduction_percent=100*(a['label_phase']-b['label_phase'])/a['label_phase'],
        fault_to_release_before=a['fault_to_release'],fault_to_release_after=b['fault_to_release'],
        total_before=old['final_cycle'],total_after=new['final_cycle'],
        subsequent_retry_phase_increase=b['retry_including_exports']-a['retry_including_exports'],
        baseline_reads_removed=781,native_reads_removed=3905,native_writes_removed=3905,
        restored_records=781,verified_records=781,default_off_entire_trace_identical=True,enabled_final_ddr_identical=True)
report=dict(status='passed',cases=audits,restores=restores,comparison=comparison,
    source_freeze=str(frozen),source_freeze_sha256=sha(frozen/'manifest.json'),source_files=len(files),
    scope='Four complete-system behavioral cases: default-off exact regression and G4-only enabled native full-record restore seed bypass for 32 and one slot. Original CRCs, actual readback, three receipts, owner bytes and CPU query retry preserved. Optimized complete-system abort/CRC-failure noncold retry remains separate and pending. No timing/resource/board-speed claim.')
(ROOT/'results/restore_seed_20261027.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('RESTORE_SEED_FROZEN',len(files),comparison)
