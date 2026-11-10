"""Prepare full-root structural recheck with both audited component rewrites."""
from pathlib import Path
import json,shutil,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();ref=p.parent/'restore_seed_synth_on_v1'
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert rm['status']=='observed'and ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
groups={'capture_loops_component_v1':['recursive/recursive_candidate_controller.sv','capture/expansion_capture.sv'],
        'rearm_loops_component_v2':['recovery_coordinator.sv','label_restore_controller.sv','residency_system.sv']}
changes={};component_receipts={}
for name,names in groups.items():
    root=p.parent/name;cm=json.loads((root/'manifest.json').read_text());ca=json.loads((root/'source_bound_audit.json').read_text())
    assert ca['status']=='passed'and ca['manifest_sha256']==sha(root/'manifest.json')
    receipt=ROOT/'results'/f'{name}_restore_20261025.json';rr=json.loads(receipt.read_text())
    assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(root/'source_bound_audit.json')
    component_receipts[name]=dict(audit_sha256=sha(root/'source_bound_audit.json'),restore_receipt_sha256=sha(receipt))
    for n in names:
        base=root/'sources/baseline'/Path(n).name;fixed=root/'sources/fixed'/Path(n).name
        assert sha(base)==rm['sources'][n]==sha(ref/'sources'/n)
        assert sha(fixed)==cm['sources']['fixed/'+Path(n).name]['sha256']
        changes[n]=dict(component=name,original_sha256=sha(base),candidate_sha256=sha(fixed),path=str(fixed))
p.mkdir();src=p/'sources';src.mkdir();sources={}
for n,h in rm['sources'].items():
    origin=ref/'sources'/n;assert sha(origin)==h
    target=src/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,target);sources[n]=h
for n,c in changes.items():shutil.copyfile(c['path'],src/n);sources[n]=sha(src/n)
for f in src.rglob('*.dat'):shutil.copyfile(f,p/f.name)
tcl=(ref/'synth.tcl').read_text().replace(str(ref),str(p));(p/'synth.tcl').write_text(tcl)
shutil.copyfile(ref/'clock.xdc',p/'clock.xdc')
shutil.copyfile(Path(__file__),src/'prepare_combined.py');sources['prepare_combined.py']=sha(src/'prepare_combined.py')
m=dict(status='prepared',sources=sources,rtl=rm['rtl'],parameters=rm['parameters'],part=rm['part'],
       reference=str(ref),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
       tcl_sha256=sha(p/'synth.tcl'),xdc_sha256=sha(p/'clock.xdc'),clock_period_ns=10,
       component_receipts=component_receipts,production_changes=changes,
       scope='Full query root recheck after five-source cumulative capture and REARM component rewrites; identical parameters and10ns experimental clock to restore_seed_synth_on_v1. No claim that remaining authority/owner/fault loops are gone until complete DCP checks. Combined runtime regression and final matrix pending; no IO timing, physical closure or board claim.')
(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print('COMBINED_LOOP_SYNTH_PREPARED',p,len(rm['rtl']),len(changes))
