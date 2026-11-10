"""Freeze actual G4 warm recovery evidence only after archive restoration audits."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

b=Path('/tmp/B_state_residency_offer_20261025')
names=['fourth_warm_full_v2','fourth_warm_pressure_v2','fourth_warm_full_v1']
result=dict(status='passed',cases={},restores={},reference_report='results/fourth_system_20261027.json',reference_report_sha256=sha(ROOT/'results/fourth_system_20261027.json'),phase_analysis='results/fourth_warm_phases_20261027.json',phase_analysis_sha256=sha(ROOT/'results/fourth_warm_phases_20261027.json'),
 scope='Actual G4 graph-R fault following sole-owner ripup, native three-INC repair and raw781/156/10 saved state restoration into attempt7, source-floor rejection and CPU q4 retry. Failed attempt6 consumed180330; new-attempt source ledger180329 is restored by native target reset/rebase. No global never-reuse/persistent floor, arbitrary fault/cancel, overflow pool allocation/reclaim, variable-price validity or board/timing claim.')
freeze=ROOT/'results/fourth_warm_sources_20261027';freeze.mkdir();files=[]
def keep(p,rel):
 target=freeze/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 files.append(dict(source=str(p),path=str(rel),sha256=sha(target)))
for name in names:
 p=b/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
 r=json.loads((ROOT/'results'/(name+'_restore_20261025.json')).read_text())
 assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
 assert r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
 assert a['auditor_sha256']==sha(ROOT/'scripts'/r['auditor'])
 result['cases'][name]=a;result['restores'][name]=r
 for n,e in m['sources'].items():
  assert sha(p/'sources'/n)==e['sha256'];keep(p/'sources'/n,Path(name)/n)
for n in ['run_fourth_warm.py','audit_fourth_warm.py','audit_fourth_warm_records.py','audit_fourth_warm_compile.py','audit_route_fault_axi.py','analyze_fourth_warm_phases.py','freeze_fourth_warm.py']:
 keep(ROOT/'scripts'/n,Path('scripts')/n)
for p in sorted((ROOT/'hardware/variants/fourth_warm_v1').glob('*')):
 if p.is_file():keep(p,Path('variant')/p.name)
keep(ROOT/'hardware/variants/restore_seed_bypass_v1/PLAN.md',Path('future_design_only/PLAN.md'))
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files),indent=2,sort_keys=True)+'\n')
result['source_freeze']=str(freeze/'manifest.json');result['source_freeze_sha256']=sha(freeze/'manifest.json');result['source_files']=len(files)
(ROOT/'results/fourth_warm_20261027.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOURTH_WARM_FROZEN',len(files))
