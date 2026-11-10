"""Reuse case-specific ten-source references with only the query two-file overlay."""
from pathlib import Path
import importlib.util
import json
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025')
REFERENCES={f'native_matrix_{kind}_{cap}_v1'for kind in ['off','on','retry_cancel']for cap in ['full','pressure']}|{'native_matrix_retry_crc_full_v1'}
spec=importlib.util.spec_from_file_location('query_system_parent',HERE.parent/'query_native_system_v1/build.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
NAMES=parent.NAMES
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources(fixed):return parent.sources(fixed)
def monitored_tb(original):return parent.monitored_tb(original)
def audited(p):
    m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    rp=ROOT/'results'/f'{p.name}_restore_20261025.json';r=json.loads(rp.read_text())
    assert m['status']=='observed'and a['status']==r['status']=='passed'and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_sha256']==sha(p/'source_bound_audit.json')
    return m,a,rp
def preflight(ref):
    assert ref.parent==BASE and ref.name in REFERENCES
    rm,ra,rp=audited(ref)
    original,oa,op=audited(BASE/'native_retirement_synth_v1')
    candidate=json.loads((BASE/'query_native_synth_v1/manifest.json').read_text())
    assert len(original['rtl'])==133 and candidate['rtl']==original['rtl']
    assert set(rm['rtl'])==set(original['rtl'])|{'axi_file_memory.sv','tb_directory_observer.sv','tb_query_fault.sv'}
    fixed=sources(True);baseline=sources(False)
    for n in original['rtl']:
        assert sha(ref/'sources'/n)==rm['sources'][n]['sha256']==original['sources'][n],(ref.name,n)
        if n in fixed:assert (ref/'sources'/n).read_text()==baseline[n]
        expected=sha(HERE/'fixed'/n)if n in fixed else original['sources'][n]
        assert candidate['sources'][n]==expected==sha(BASE/'query_native_synth_v1/sources'/n),n
    return dict(reference_audit_sha256=sha(ref/'source_bound_audit.json'),reference_restore_sha256=sha(rp),
                production_sources=133,case=next(iter(rm['cases'])))
def evidence(ref):
    binding=preflight(ref)
    sm,sa,srp=audited(BASE/'query_native_synth_v1')
    assert sa['check_timing_counts']['loops']==0,'new candidate requires independently restored zero-loop OOC'
    assert not sa['timing_loop_warnings'],'automatic loop cuts require diagnosis'
    anchor=BASE/'query_native_system_crc_pressure_v1';am,aa,arp=audited(anchor)
    assert len(aa['exact_comparisons'])==27
    for n in sm['rtl']:assert sm['sources'][n]==am['sources'][n]['sha256']==sha(anchor/'sources'/n)
    result=parent.evidence(ref)
    result.update(builder_sha256=sha(HERE/'build.py'),parent_builder_sha256=sha(HERE.parent/'query_native_system_v1/build.py'),
                  structural_audit_sha256=sha(BASE/'query_native_synth_v1/source_bound_audit.json'),
                  structural_restore_sha256=sha(srp),anchor_audit_sha256=sha(anchor/'source_bound_audit.json'),
                  anchor_restore_sha256=sha(arp),case_binding=binding)
    return result
