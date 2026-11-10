"""Count the existing combined CRC run only after direct original-reference checks."""
from pathlib import Path
import importlib.util,json
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
p=base/'native_retirement_system_crc_pressure_v1'
ref=base/'restore_seed_retry_crc_pressure_v1'
def verified(root):
    m=json.loads((root/'manifest.json').read_text());a=json.loads((root/'source_bound_audit.json').read_text())
    receipt=ROOT/'results'/f'{root.name}_restore_20261025.json';r=json.loads(receipt.read_text())
    assert m['status']=='observed'and a['status']==r['status']=='passed'
    assert a['manifest_sha256']==sha(root/'manifest.json')and r['audit_byte_identical']
    assert r['audit_sha256']==sha(root/'source_bound_audit.json')
    return m,a,receipt
m,a,receipt=verified(p);rm,ra,rreceipt=verified(ref)
v=ROOT/'hardware/variants/native_retirement_matrix_v1'
spec=importlib.util.spec_from_file_location('matrix_builder',v/'build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
original,fixed=b.sources(False),b.sources(True);bm=b.audited(b.BASE)
assert m['rtl']==rm['rtl']and set(m['cases'])==set(rm['cases'])=={'pressure'}
for n in bm['rtl']:
    assert sha(ref/'sources'/n)==rm['sources'][n]['sha256']==bm['sources'][n],n
    expected=sha(v/'fixed'/n)if n in fixed else bm['sources'][n]
    assert sha(p/'sources'/n)==m['sources'][n]['sha256']==expected,n
assert (p/'sources/tb_query_fault.sv').read_text()==b.monitored_tb((ref/'sources/tb_query_fault.sv').read_text())
assert (p/'pressure/run.tcl').read_bytes()==(ref/'pressure/run.tcl').read_bytes()
assert m['binding_sha256']==rm['binding_sha256']==sha(Path(m['binding']))
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    assert m[key]==rm[key]
    for n,h in m[key].items():assert sha(p/n)==sha(ref/n)==h
for old,new in zip(rm['cases']['pressure']['commands'],m['cases']['pressure']['commands']):
    assert new['stage']==old['stage']and new['argv']==[x.replace(str(ref),str(p))for x in old['argv']]
files=sorted(f.name for f in(ref/'pressure').iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat'])
assert len(files)==27
for n in files:assert sha(p/'pressure'/n)==sha(ref/'pressure'/n)==a['exact_comparisons'][n]['sha256'],n
import re
finish=lambda root:re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',(root/'pressure/simulate.log').read_text())
assert finish(p)==finish(ref)==['48288200 ns']
result=dict(status='existing_crc_pressure_case_matched_to_original',existing_run=str(p),reference=str(ref),
    existing_audit_sha256=sha(p/'source_bound_audit.json'),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
    existing_restore_sha256=sha(receipt),reference_restore_sha256=sha(rreceipt),
    auditor_sha256=sha(Path(__file__)),builder_sha256=sha(v/'build.py'),
    matched_production_sources=133,cumulative_changes=10,matched_files=files,finish_time=finish(p)[0],
    scope='One existing combined CRC pressure run directly compared to its original reference; no duplicate simulation. Not the remaining seven cases or structural/timing acceptance.')
out=ROOT/'results/native_matrix_crc_pressure_anchor_20261027.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('NATIVE_MATRIX_CRC_ANCHOR_AUDITED 133 sources 27 outputs')
