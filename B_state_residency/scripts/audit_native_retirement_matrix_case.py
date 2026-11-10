"""Require literal full trace/cycle/DDR equality to the independently audited case."""
from pathlib import Path
import importlib.util,json,re,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and len(m['cases'])==1
case=next(iter(m['cases']));d=p/case;c=m['cases'][case]
assert c['status']=='observed'and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands'])
ref=Path(m['native_matrix_reference']);rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
assert sha(ref/'source_bound_audit.json')==m['native_matrix_reference_audit_sha256']
receipt=ROOT/'results'/f'{ref.name}_restore_20261025.json';rr=json.loads(receipt.read_text())
assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(ref/'source_bound_audit.json')
variant=ROOT/'hardware/variants/native_retirement_matrix_v1';builder=variant/'build.py'
spec=importlib.util.spec_from_file_location('native_matrix_builder',builder);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
baseline,fixed=b.sources(False),b.sources(True)
allowed={f'restore_seed_{kind}_{cap}_v1'for kind in ['off','on','retry_cancel','retry_crc']for cap in ['full','pressure']}-{"restore_seed_retry_crc_pressure_v1"}
assert ref.name in allowed,'CRC pressure is already owned by the existing combined run; do not duplicate'

# Require all production reference sources to be the matched original matrix.
base_manifest=b.audited(b.BASE)
assert set(base_manifest['rtl']).issubset(set(rm['rtl']))
for n in base_manifest['rtl']:
    assert sha(ref/'sources'/n)==rm['sources'][n]['sha256']==base_manifest['sources'][n],n
# Remaining seven runs are useful only after the combined candidate is accepted
# by the full CRC audit and has no loops in the matched structural recheck.
anchor=p.parent/'native_retirement_system_crc_pressure_v1'
am=json.loads((anchor/'manifest.json').read_text());aa=json.loads((anchor/'source_bound_audit.json').read_text())
ar=json.loads((ROOT/'results/native_retirement_system_crc_pressure_v1_restore_20261025.json').read_text())
assert am['status']=='observed'and aa['status']==ar['status']=='passed'and ar['audit_byte_identical']
assert aa['manifest_sha256']==sha(anchor/'manifest.json')and ar['audit_sha256']==sha(anchor/'source_bound_audit.json')
struct=p.parent/'native_retirement_synth_v1'
sm=json.loads((struct/'manifest.json').read_text());sa=json.loads((struct/'source_bound_audit.json').read_text())
assert sm['status']=='observed'and sa['status']=='passed'and sa['manifest_sha256']==sha(struct/'manifest.json')
assert sa['check_timing_counts']['loops']==0,'candidate is not yet structurally ready for the remaining matrix'
srpath=ROOT/'results/native_retirement_synth_v1_restore_20261025.json';sr=json.loads(srpath.read_text())
assert sr['status']=='passed'and sr['audit_byte_identical']and sr['audit_sha256']==sha(struct/'source_bound_audit.json')
for n in base_manifest['rtl']:
    expected=sha(variant/'fixed'/n)if n in fixed else base_manifest['sources'][n]
    assert sha(anchor/'sources'/n)==am['sources'][n]['sha256']==expected,n
    assert sha(struct/'sources'/n)==sm['sources'][n]==expected,n

proof_path=ROOT/'results/recovery_backend_exclusion_20261027.json';proof=json.loads(proof_path.read_text())
assert proof['status']=='native_interface_exclusion_verified_not_rtl_validation'
assert proof['analyzer_sha256']==sha(ROOT/'scripts/analyze_recovery_backend_exclusion.py')
assert m['native_matrix_evidence']==dict(builder_sha256=sha(builder),identity_sha256=sha(proof_path),reference_restore_sha256=sha(receipt),capture_identity_sha256=sha(ROOT/'results/capture_retirement_identity_20261027.json'),capture_builder_sha256=sha(ROOT/'hardware/variants/capture_retirement_loops_v1/build.py'),backend_builder_sha256=sha(ROOT/'hardware/variants/recovery_backend_loops_v2/build.py'),composition_builder_sha256=sha(ROOT/'hardware/variants/native_retirement_loops_v1/build.py'),anchor_audit_sha256=sha(anchor/'source_bound_audit.json'),structural_audit_sha256=sha(struct/'source_bound_audit.json'),structural_restore_sha256=sha(srpath),
    candidate_sha256={n:sha(variant/'fixed'/n)for n in fixed})
changed=sorted(fixed)
assert set(changed)==set(b.NAMES)
assert m['rtl']==rm['rtl']and m['binding_sha256']==rm['binding_sha256']==sha(Path(m['binding']))
assert set(m['sources'])==set(rm['sources'])
for n,e in m['sources'].items():
    assert sha(p/'sources'/n)==e['sha256'],n
    if n in fixed:
        assert (p/'sources'/n).read_text()==fixed[n]==(variant/'fixed'/n).read_text()
        assert (ref/'sources'/n).read_text()==baseline[n]
    elif n=='tb_query_fault.sv':
        assert (p/'sources'/n).read_text()==b.monitored_tb((ref/'sources'/n).read_text())
    elif n!='runner.py':assert e['sha256']==rm['sources'][n]['sha256'],n
assert sha(p/'sources/runner.py')==sha(ROOT/'scripts/run_native_retirement_matrix_case.py')
for old,new in zip(rm['cases'][case]['commands'],c['commands']):
    assert new['stage']==old['stage']and new['argv']==[x.replace(str(ref),str(p))for x in old['argv']]
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    assert m[key]==rm[key]
    for n,h in m[key].items():assert sha(p/n)==h
files=sorted(f.name for f in(ref/case).iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat'])
assert {f.name for f in d.iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat']}==set(files)
assert len([n for n in files if n.endswith('_axi.txt')])==12
assert all(n in files for n in ['natural_trace.txt','owners.bin','labels.bin','runtime_g4_labels.txt','restore_seed_trace.txt'])
comparisons={}
for name in files:
    actual=sha(d/name);expected=sha(ref/case/name)
    assert actual==expected,(name,'literal bytes differ; do not normalize away events or cycles')
    comparisons[name]=dict(bytes=(d/name).stat().st_size,sha256=actual)
log=(d/'simulate.log').read_text();oldlog=(ref/case/'simulate.log').read_text()
assert 'Fatal:'not in log and '$finish called'in log
finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
assert len(finish)==1 and finish==re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',oldlog)
markers=[l for l in log.splitlines()if any(tag in l for tag in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'])]
assert markers==[l for l in oldlog.splitlines()if any(tag in l for tag in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'])]
coverage=re.findall(r'BACKEND_EXCLUSION_PASS cycles=(\d+) authority=(\d+) owner=(\d+)',log)
assert len(coverage)==1 and all(int(v)>0 for v in coverage[0])
capture_coverage=re.findall(r'CAPTURE_RETIREMENT_PASS cycles=(\d+) nonzero=(\d+) replies=(\d+)',log)
assert len(capture_coverage)==1 and all(int(v)>0 for v in capture_coverage[0])
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),reference_restore_receipt_sha256=sha(receipt),
    native_matrix_evidence=m['native_matrix_evidence'],modified_production_sources=changed,
    capture_retirement=dict(zip(['cycles','nonzero_cycles','reply_cycles'],map(int,capture_coverage[0]))),backend_exclusion=dict(zip(['cycles','authority','owner'],map(int,coverage[0]))),exact_comparisons=comparisons,finish_time=finish[0],markers=markers,
    inherited_numerical_scope='Exact literal native cycles, all12 AXI traces, stream images and final DDR equal the restored independently audited reference; its CPU/oracle and byte replay conclusions apply to these identical observed artifacts. No trace rewriting or relaxed comparison.',
    scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('NATIVE_MATRIX_CASE_AUDITED',p.name,len(comparisons),finish[0])
