from pathlib import Path
import hashlib,json,re
from make_retained_endpoint import generate
from make_retained_endpoint_tb import generate as generate_tb
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pilot=ROOT/'results/rtl_retained_endpoint_pilot_20261023';legacy=ROOT/'results/rtl_retained_endpoint_legacy_20261023'
neg=ROOT/'results/rtl_retained_endpoint_guards_20261023';remaining=ROOT/'results/rtl_retained_endpoint_guards_remaining_20261023'
pm=json.loads((pilot/'manifest.json').read_text());lm=json.loads((legacy/'simulation_manifest.json').read_text())
assert pm['status']=='passed' and lm['status']=='completed'
for path,digest in pm['sources'].items():assert sha(Path(path))==digest==sha(pilot/'sources'/Path(path).name)
for path,digest in lm['sources'].items():assert sha(ROOT/path)==digest==sha(legacy/'sources'/path)
assert generate((ROOT/'hardware/rtl/memory_scratch_endpoint_indexed.sv').read_text())==(ROOT/'hardware/rtl/memory_scratch_endpoint_retained.sv').read_text()
assert generate_tb()==(ROOT/'hardware/tb/tb_retained_endpoint.sv').read_text()
for suffix in ['', '_profile']:
 old=(ROOT/f'hardware/tb/tb_memory_endpoint_indexed{suffix}.sv').read_text()
 expected=old.replace('memory_endpoint_indexed','memory_endpoint_retained').replace('memory_scratch_endpoint_indexed','memory_scratch_endpoint_retained')
 assert expected==(ROOT/f'hardware/tb/tb_memory_endpoint_retained{suffix}.sv').read_text()
for row in lm['cases'].values():assert row['status']=='passed' and all(c['exit_code']==0 for c in row['commands'])
for name,digest in lm['artifacts'].items():assert sha(legacy/name)==digest
for name in ['profile.counts.csv','profile.commands.csv']:
 assert (legacy/name).read_bytes()==(ROOT/'results/rtl_indexed_endpoint_20261023'/name).read_bytes(),name
s=(legacy/'actual/simulate.log').read_text();assert 'PROFILE_PASS samples=7289882 accepted=77099 retired=77099' in s
assert '$finish called at time : 72898860 ns' in s
nm=json.loads((neg/'manifest.json').read_text());rm=json.loads((remaining/'manifest.json').read_text());assert nm['status']=='failed' and rm['status']=='passed'
assert nm['cases']['ignore_live_slots']['status']=='detected' and nm['cases']['skip_query_resume']['status']=='detected'
third=neg/'clear_backing_directory/simulate.log';lines=[l for l in third.read_text().splitlines() if l.startswith('Fatal:')]
assert lines==['Fatal: address RECYCLE before page fence acknowledgement'] and 'RETAINED_ENDPOINT_PASS' not in third.read_text()
assert all(c['exit_code']==0 for c in nm['cases']['clear_backing_directory']['commands'] if c['stage']!='simulate')
assert rm['cases']['ignore_query_exclusivity']['status']=='detected'
a={'status':'passed','scope':'Directed small checkpoint pilot, unchanged legacy regression and four semantic mutants. No full-38 checkpoint replay, synthesis or board result.',
 'pilot_manifest_sha256':sha(pilot/'manifest.json'),'legacy_manifest_sha256':sha(legacy/'simulation_manifest.json'),
 'negative_manifest_sha256':sha(neg/'manifest.json'),'remaining_negative_manifest_sha256':sha(remaining/'manifest.json'),
 'legacy_profile_byte_identical':True,'pilot_checks':134,'pilot_checkpoints':21,'pilot_tag_wraps':11,
 'third_negative_classification':'Earlier existing full-recycle protocol assertion detected wrong opcode before content check. Raw failed runner preserved; no checker changed or rerun.',
 'sources':{str(ROOT/name):sha(ROOT/name) for name in ['hardware/scripts/make_retained_endpoint_tb.py','hardware/scripts/make_retained_endpoint.py','hardware/scripts/audit_retained_endpoint.py']}}
(pilot/'final_audit.json').write_text(json.dumps(a,indent=2)+'\n')
for path in a['sources']:(pilot/Path(path).name).write_bytes(Path(path).read_bytes())
print(json.dumps(a,indent=2))
