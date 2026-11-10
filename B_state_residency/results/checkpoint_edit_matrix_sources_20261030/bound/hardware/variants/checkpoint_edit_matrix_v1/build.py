"""Case-specific CP matrix preparation; actual runs wait for the physical owner."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025')
PARENT=HERE.parent/'checkpoint_edit_exclusion_v1'
NAMES=['query_lifecycle.sv','query_residency_system.sv']
REFERENCES=tuple('query_matrix_'+kind+'_'+capacity+'_v1'
                 for kind in ['off','on','retry_cancel'] for capacity in ['full','pressure'])+('query_matrix_retry_crc_full_v1',)
ANCHOR=BASE/'checkpoint_edit_system_crc_pressure_v1'
spec=importlib.util.spec_from_file_location('cp_matrix_system_parent',HERE.parent/'checkpoint_edit_system_v1/build.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def restored(path): return parent.restored(path)

def preflight(reference):
    assert reference.parent==BASE and reference.name in REFERENCES
    rm,ra,rr=restored(reference)
    original,oa,orr=restored(BASE/'query_native_synth_v1')
    candidate,ca,cr=restored(BASE/'checkpoint_edit_synth_v1')
    am,aa,ar=restored(ANCHOR)
    assert candidate['exit_code']==0 and candidate['part']=='xcu280-fsvh2892-2L-e'
    assert candidate['rtl']==original['rtl'] and len(candidate['rtl'])==133
    assert ca['check_timing_counts']['loops']==0 and not ca['timing_loop_warnings'] and not ca['critical_warnings']
    assert ca['facts']['latches']==ca['facts']['blackboxes']==0
    assert len(aa['exact_comparisons'])==len(ra['exact_comparisons'])==27
    assert aa['monitor_generator_sha256']==sha(ROOT/'scripts/prepare_checkpoint_edit_monitor.py')
    assert am['checkpoint_edit_reference']==str(BASE/'query_native_system_crc_pressure_v1')
    fixed,proof=parent.sources(BASE/'query_native_system_crc_pressure_v1')
    assert set(fixed)==set(NAMES)
    verification={'axi_file_memory.sv','tb_directory_observer.sv','tb_query_fault.sv'}
    assert len(rm['rtl'])==136 and set(rm['rtl'])==set(candidate['rtl'])|verification
    assert len(rm['cases'])==1 and rm['binding_sha256']==am['binding_sha256']==sha(Path(rm['binding']))
    for name in candidate['rtl']:
        assert sha(reference/'sources'/name)==rm['sources'][name]['sha256']==original['sources'][name],(reference.name,name)
        expected=sha(PARENT/'fixed'/name) if name in fixed else original['sources'][name]
        assert candidate['sources'][name]==expected==sha(BASE/'checkpoint_edit_synth_v1/sources'/name)
        assert sha(ANCHOR/'sources'/name)==am['sources'][name]['sha256']==expected
        if name in fixed: assert (reference/'sources'/name).read_text()==(PARENT/'baseline'/name).read_text()
    source=reference/'sources/tb_query_fault.sv'
    assert sha(source)==rm['sources']['tb_query_fault.sv']['sha256']
    text=source.read_text(); monitored=monitored_tb(text)
    for marker in ['BACKEND_EXCLUSION_PASS','CAPTURE_RETIREMENT_PASS','QUERY_INTERFACE_EXCLUSION_PASS']:
        assert text.count(marker)==monitored.count(marker)==1
    assert 'CHECKPOINT_EDIT_EXCLUSION_PASS' not in text and monitored.count('CHECKPOINT_EDIT_EXCLUSION_PASS')==1
    return dict(reference=str(reference),target=reference.name.replace('query_matrix_','checkpoint_matrix_',1),
        case=next(iter(rm['cases'])),reference_audit_sha256=sha(reference/'source_bound_audit.json'),
        reference_restore_sha256=sha(rr),structural_audit_sha256=sha(BASE/'checkpoint_edit_synth_v1/source_bound_audit.json'),
        structural_restore_sha256=sha(cr),anchor_audit_sha256=sha(ANCHOR/'source_bound_audit.json'),
        anchor_restore_sha256=sha(ar),production_sources=133,modified_production_sources=NAMES,
        monitor_generator_sha256=sha(ROOT/'scripts/prepare_checkpoint_edit_monitor.py'),
        original_tb_sha256=sha(source),monitored_tb_sha256=hashlib.sha256(monitored.encode()).hexdigest(),
        anchor_parent_evidence=proof,builder_sha256=sha(HERE/'build.py'),
        parent_builder_sha256=sha(HERE.parent/'checkpoint_edit_system_v1/build.py'))

def evidence(reference):
    owner=BASE/'checkpoint_edit_route_recovery_followup_v1'
    gate=json.loads((owner/'manifest.json').read_text())
    assert gate['status']=='observed' and gate['stage']=='complete', 'Existing physical recovery owner must complete before any matrix run'
    assert not Path('/proc',str(gate['runner_pid'])).exists()
    physical=BASE/'checkpoint_edit_route_recovery_v1'
    assert Path(gate['target'])==physical
    pm,pa,pr=restored(physical)
    assert pm['stage']=='complete' and pm['exit_code']==0 and pa['independent_reopened_dcp_matches']
    assert pm['reference']==str(BASE/'checkpoint_edit_synth_v1')
    accepted=ROOT/'results/checkpoint_edit_route_recovery_20261030.json'
    report=json.loads(accepted.read_text()); assert report['audit']==pa
    freeze=ROOT/'results/checkpoint_edit_route_recovery_sources_20261030'
    fm=json.loads((freeze/'manifest.json').read_text()); assert fm['status']=='frozen'
    for name,entry in fm['files'].items(): assert sha(freeze/name)==entry['sha256']==sha(Path(entry['source']))
    result=preflight(reference)
    result.update(physical_owner_manifest_sha256=sha(owner/'manifest.json'),
                  physical_audit_sha256=sha(physical/'source_bound_audit.json'),physical_restore_sha256=sha(pr),
                  physical_report_sha256=sha(accepted),physical_freeze_sha256=sha(freeze/'manifest.json'))
    return result

def sources(reference):
    proof=evidence(reference)
    return {name:(PARENT/'fixed'/name).read_text() for name in NAMES},proof

def monitored_tb(original): return parent.monitored_tb(original)
