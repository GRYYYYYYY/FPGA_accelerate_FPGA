"""Bind all ten cumulative changes to the original eight-case reference matrix."""
from pathlib import Path
import hashlib,importlib.util,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/restore_seed_synth_on_v1')
ROUTE=BASE.parent/'route_block_synth_v1'
NAMES=sorted(['priced/candidate_recursive_query_core.sv','capture/expansion_capture.sv',
    'recursive/recursive_candidate_controller.sv','route_commit_controller.sv',
    'route_commit_host_adapter.sv','recovery_coordinator.sv','label_restore_controller.sv',
    'residency_system.sv','search_residency_system.sv','query_residency_system.sv'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('native_retirement_composition',HERE.parent/'native_retirement_loops_v1/build.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
def audited(p):
    m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    r=json.loads((ROOT/'results'/f'{p.name}_restore_20261025.json').read_text())
    assert m['status']=='observed'and a['status']==r['status']=='passed'
    assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_byte_identical']
    assert r['audit_sha256']==sha(p/'source_bound_audit.json')
    return m
def sources(fixed):
    bm=audited(BASE);rm=audited(ROUTE)
    assert bm['rtl']==rm['rtl']and len(bm['rtl'])==133
    patches=parent.sources(True);patchbase=parent.sources(False)
    original={};final={}
    for n in bm['rtl']:
        original[n]=(BASE/'sources'/n).read_text()
        assert sha(BASE/'sources'/n)==bm['sources'][n]
        final[n]=(ROUTE/'sources'/n).read_text()
        assert sha(ROUTE/'sources'/n)==rm['sources'][n]
        if n in patches:
            assert final[n]==patchbase[n]
            final[n]=patches[n]
    assert sorted(n for n in original if original[n]!=final[n])==NAMES
    return {n:(final if fixed else original)[n]for n in NAMES}
def monitored_tb(original):return parent.monitored_tb(original)
if __name__=='__main__':
    for mode in ['baseline','fixed']:
        d=HERE/mode;d.mkdir()
        for n,s in sources(mode=='fixed').items():
            q=d/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
    print('NATIVE_RETIREMENT_MATRIX_SOURCES_PREPARED',len(NAMES))
