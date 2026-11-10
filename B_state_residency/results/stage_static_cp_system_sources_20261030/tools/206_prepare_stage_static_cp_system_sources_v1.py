"""Prepare two isolated CP source overlays; this does not run a full system."""
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,verify_freeze
import json
import shutil


def main():
    accepted=ROOT/'results/stage_bank_functional_matrix_20261030.json';report=read(accepted)
    assert report['status']=='four_slot_functional_matrix_outcomes_actual_restored'
    assert report['audit']['functional_passed_modes']==['static']
    freeze=verify_freeze(ROOT/'results/stage_bank_functional_matrix_sources_20261030')
    reference=BASE/'checkpoint_edit_synth_v1';rm,ra,_=restored(reference)
    full=BASE/'checkpoint_edit_system_crc_pressure_v1';fm,fa,_=restored(full)
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    controller=reference/'sources/route_commit_controller.sv'
    adapter=reference/'sources/route_commit_host_adapter.sv'
    for source in [controller,adapter]:
        assert sha(source)==rm['sources'][source.name]==fm['sources'][source.name]['sha256']
        assert sha(full/'sources'/source.name)==sha(source)
    assert sha(controller)==vm['baseline_sha256']
    assert sha(variant/'fixed.sv')==vm['fixed_sha256']
    old=adapter.read_text()
    needle='route_commit_controller #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),.MAX_PATH(MAX_PATH),.MAX_CYCLES(MAX_CYCLES)) controller('
    assert old.count(needle)==1
    new=old.replace(needle,needle.replace('#(','#(.STATIC_STAGE_WRITES(1),',1),1)
    assert new.replace('.STATIC_STAGE_WRITES(1),','',1)==old
    out=ROOT/'hardware/variants/stage_static_cp_system_sources_v1';assert not out.exists()
    (out/'baseline').mkdir(parents=True);(out/'fixed').mkdir()
    for source in [controller,adapter]:shutil.copyfile(source,out/'baseline'/source.name)
    shutil.copyfile(variant/'fixed.sv',out/'fixed/route_commit_controller.sv')
    (out/'fixed/route_commit_host_adapter.sv').write_text(new)
    names=['route_commit_controller.sv','route_commit_host_adapter.sv']
    bound={str(p):sha(p) for p in [accepted,freeze,variant/'manifest.json',reference/'source_bound_audit.json',full/'source_bound_audit.json']}
    record=dict(status='two_source_overlay_prepared_not_full_system_executed',
        sources={n:{role:sha(out/role/n) for role in ['baseline','fixed']} for n in names},
        bound=bound,generator_sha256=sha(__file__),reference=str(reference),full_reference=str(full),
        unit_acceptance_pending=True,full_system_acceptance=False,timing_qualified=False,
        scope='CP-only stage controller plus adapter parameter enabling STATIC_STAGE_WRITES1. No path/native/label overlays. Requires actual twelve-unit audit/restore/freeze before full-system execution.')
    (out/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    (out/'CONTRACT.md').write_text('''# Isolated CP stage system source overlay

Controller is the accepted bounded static-stage candidate, default disabled.
Adapter changes exactly one parameter at its controller instance to enable it.
No other integration behavior changes. This directory prepares sources only.
Twelve-unit actual restoration and freeze remain required before a separate
full-system run with original monitors, full event/data/cycle comparisons,
stage old-tree bank observation, independent audit and actual restoration.
Full-system functional netlist validation and matched timing remain separate.
''')
    print('CP_STATIC_STAGE_TWO_SOURCE_OVERLAY_PREPARED')


if __name__=='__main__':main()
