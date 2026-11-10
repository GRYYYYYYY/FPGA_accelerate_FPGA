"""Classify a successful RTL run separately from a mistaken wrapper count."""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/rtl_retained_directory_20261023';RUN=OUT/'standalone'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((RUN/'manifest.json').read_text())
assert len(p['commands'])==3 and all(c['exit_code']==0 for c in p['commands'])
for path,digest in p['sources'].items():
 assert sha(Path(path))==digest and sha(OUT/Path(path).name)==digest
spec=importlib.util.spec_from_file_location('gen',OUT/'make_retained_directory.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert mod.generate((OUT/'backing_frame_directory_indexed.sv').read_text())==(OUT/'backing_frame_directory_retained.sv').read_text()
# Six owners: reserve/pin/done/retire. Each epoch: nine setup/guard commands,
# twelve lookup/reserve commands and three zero-ID transfer commands.
# Six full recycles with lookup/reserve, then four failed-lease/bad-op commands.
checks=6*4+40*(9+12+3)+6*3+4
assert checks==1006
s=(RUN/'simulate.log').read_text()
assert s.count(f'RETAINED_DIRECTORY_PASS checks={checks} checkpoints=40 full_recycles=6')==1
assert '$finish called at time : 124960 ns' in s
for name in ['compile_stdout.log','elaborate_stdout.log','simulate.log']:
 text=(RUN/name).read_text()
 assert not any(word in text for word in ['ERROR:', 'Fatal:', 'Error:']),name
m={'status':'passed_with_wrapper_classification','functional_status':'passed','checks':checks,
   'checkpoint_cycles':40,'full_recycles':6,'end_ns':124960,
   'raw_wrapper_exit_code':1,'raw_wrapper_failure':'Expected 1007 commands; testbench sequence has 1006. No assertion or stimulus changed, no rerun.',
   'source_manifest_sha256':sha(RUN/'manifest.json'),'sources':p['sources'],
   'rtl_checkpoint_integrated':False,'synthesized':False,
   'scope':'Standalone directory only. fence_retired remains trusted; no raw page contents or queue drain verified.',
   'artifacts':{str(f.relative_to(OUT)):sha(f) for f in OUT.rglob('*') if f.is_file() and f.suffix in ('.log','.sv','.tcl','.py','.sh')},
   'audit_source_sha256':sha(Path(__file__))}
(OUT/'classified_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(OUT/'run_retained_directory.py').write_bytes((ROOT/'hardware/scripts/run_retained_directory.py').read_bytes())
print('passed',checks,'classified_manifest',sha(OUT/'classified_manifest.json'))
