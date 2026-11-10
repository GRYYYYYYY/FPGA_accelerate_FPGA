"""Freeze audited/restored G4/q4 artifacts and record explicit proof boundaries."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
names=['fourth_system_full_v2','fourth_system_pressure_v2','fourth_system_full_v1']
result=dict(status='passed',cases={},restores={},behavioral_cycles={},
            inputs_report='results/four_path_inputs_20261027.json',inputs_report_sha256=sha(ROOT/'results/four_path_inputs_20261027.json'),
            scope='Native G4/CP20 publication and natural fourth-query continuity in four path slots; G3 warm prefix retained. Development v1 is a false TB sequence assertion, not production RTL failure. No G4 warm, overflow allocation/reclamation, persistent authentication/floor, arbitrary price validity or board/timing claim.')
freeze=ROOT/'results/fourth_system_sources_20261027';freeze.mkdir()
records=[]
def keep(source,relative):
    target=freeze/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    records.append(dict(source=str(source),path=str(relative),sha256=sha(target)))
for name in names:
    p=base/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    r=json.loads((ROOT/'results'/(name+'_restore_20261025.json')).read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert a['auditor_sha256']==sha(ROOT/'scripts'/r['auditor'])
    result['cases'][name]=a;result['restores'][name]=r
    for n,e in m['sources'].items():
        assert sha(p/'sources'/n)==e['sha256'];keep(p/'sources'/n,Path(name)/n)
    if not a.get('development_failure'):
        rows=[t.split()for t in(p/a['case']/'natural_trace.txt').read_text().splitlines()]
        events={tag:int(next(t[1]for t in rows if t[0]==tag))for tag in ['G4_ROTATION_BEGIN','G4_ROTATION_COPIED','G4_LABEL_BEGIN','G4_LABEL_DONE','G4_PUBLISHED','FOURTH_BEGIN','FOURTH_PREPARED','FOURTH_PASS']}
        events['query_reply']=int(next(t[1]for t in rows if t[0]=='LIFECYCLE'and t[2]=='3'))
        result['behavioral_cycles'][name]=dict(events=events,
            g4_owner_copy_with_rearm=events['G4_ROTATION_COPIED']-events['G4_ROTATION_BEGIN'],
            g4_label_export=events['G4_LABEL_DONE']-events['G4_LABEL_BEGIN'],
            g4_rotation_through_publication=events['G4_PUBLISHED']-events['G4_ROTATION_BEGIN'],
            q4_prepared_to_reply=events['query_reply']-events['FOURTH_PREPARED'],
            q4_with_preparation_and_exports=events['FOURTH_PASS']-events['FOURTH_BEGIN'])
for path in [ROOT/'scripts'/n for n in ['run_fourth_system.py','audit_fourth_system.py','audit_fourth_development.py','audit_third_warm_records.py','audit_route_fault_axi.py','freeze_fourth_system.py']]:keep(path,Path('scripts')/path.name)
for path in sorted((ROOT/'hardware/variants/four_path_v1').glob('*')):
    if path.is_file():keep(path,Path('variant')/path.name)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=records),indent=2,sort_keys=True)+'\n')
result['source_freeze']=str(freeze/'manifest.json');result['source_freeze_sha256']=sha(freeze/'manifest.json');result['source_files']=len(records)
(ROOT/'results/fourth_system_20261027.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOURTH_SYSTEM_FROZEN',len(records))
