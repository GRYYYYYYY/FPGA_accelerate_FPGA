"""Read-only reference/source/monitor preflight; does not submit simulations."""
from pathlib import Path
import importlib.util,json
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
variant=ROOT/'hardware/variants/native_retirement_matrix_v1'
spec=importlib.util.spec_from_file_location('matrix_builder',variant/'build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
original,fixed=b.sources(False),b.sources(True)
names=[f'restore_seed_{kind}_{cap}_v1'for kind in ['off','on','retry_cancel','retry_crc']for cap in ['full','pressure']]
result=[]
for name in names:
    p=base/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    receipt=ROOT/'results'/f'{name}_restore_20261025.json';r=json.loads(receipt.read_text())
    assert m['status']=='observed'and a['status']==r['status']=='passed'
    assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_byte_identical']
    assert r['audit_sha256']==sha(p/'source_bound_audit.json')and len(m['cases'])==1
    case=next(iter(m['cases']))
    assert len(m['cases'][case]['commands'])==3 and all(c['exit_code']==0 for c in m['cases'][case]['commands'])
    for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],(name,n)
    for n in b.NAMES:
        assert (p/'sources'/n).read_text()==original[n],(name,n)
        assert (variant/'fixed'/n).read_text()==fixed[n]
    assert sha(Path(m['binding']))==m['binding_sha256']
    tb=b.monitored_tb((p/'sources/tb_query_fault.sv').read_text())
    assert 'CAPTURE_RETIREMENT_PASS'in tb and 'BACKEND_EXCLUSION_PASS'in tb
    files=sorted(f.name for f in(p/case).iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat'])
    assert len(files)==27 and sum(n.endswith('_axi.txt')for n in files)==12
    kind=name.removeprefix('restore_seed_').removesuffix('_v1')
    target='native_retirement_system_crc_pressure_v1'if kind=='retry_crc_pressure'else 'native_matrix_'+kind+'_v1'
    record=dict(reference=name,case=case,target=target,reference_manifest_sha256=sha(p/'manifest.json'),
        reference_audit_sha256=sha(p/'source_bound_audit.json'),reference_restore_sha256=sha(receipt),
        seed_bypass=m['restore_seed_bypass'],failure=m.get('restore_seed_failure'),
        candidate_tb_sha256=__import__('hashlib').sha256(tb.encode()).hexdigest(),expected_files=files,
        execution='not_submitted')
    existing=base/target/'manifest.json'
    if existing.exists():
        assert kind=='retry_crc_pressure','unexpected existing matrix run; inspect before replacing'
        em=json.loads(existing.read_text())
        for n in b.NAMES:assert (existing.parent/'sources'/n).read_text()==fixed[n]
        assert (existing.parent/'sources/tb_query_fault.sv').read_text()==tb
        record['execution']='existing_'+em['status']
    result.append(record)
out=ROOT/'results/native_retirement_matrix_preflight_20261027.json';assert not out.exists()
out.write_text(json.dumps(dict(status='references_and_sources_preflight_only',cases=result,
    builder_sha256=sha(variant/'build.py'),script_sha256=sha(Path(__file__)),
    cumulative_changes={n:dict(original_sha256=sha(variant/'baseline'/n),candidate_sha256=sha(variant/'fixed'/n))for n in b.NAMES},
    scope='Eight restored references and exact ten-source candidate bindings; no simulation submitted or passed by this preflight.'),indent=2,sort_keys=True)+'\n')
print('NATIVE_MATRIX_PREFLIGHT',len(result),'cases',len(b.NAMES),'production sources')
