"""Gated text builder for a default-off descriptor publication experiment.

Preparing this tool does not produce candidate RTL. Its actual invocation must
first pass the restored matrix and both original-controller RTL probes.
"""
from pathlib import Path
import json
import re
import shutil
from host_edit_system_common_v1 import ROOT, BASE, sha, read, predecessors, restored, verify_freeze

TARGET = ROOT / 'hardware/variants/config_native_publication_v1'
REFERENCE = BASE / 'checkpoint_edit_synth_v1'
CONTROLLER = 'config_restore_controller.sv'
WRAPPER = 'residency_system.sv'
PARAMETER = 'NATIVE_FEEDBACK_PUBLICATION'
OLD_MODULE = 'module config_restore_controller #(parameter integer MAX_CYCLES=1048576)('
NEW_MODULE = 'module config_restore_controller #(parameter integer MAX_CYCLES=1048576,NATIVE_FEEDBACK_PUBLICATION=0)('
OLD_PUBLISH = 'if(publish_valid&&publish_ready)begin descriptor<=shadow_payload;saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_payload[2240+:32];prepared<=0;end'
NEW_PUBLISH = '''if(publish_valid&&publish_ready)begin
    if(NATIVE_FEEDBACK_PUBLICATION!=0)descriptor[2240+:32]<=shadow_payload[2240+:32];
    else descriptor<=shadow_payload;
    saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_payload[2240+:32];prepared<=0;
   end'''
OLD_INSTANCE = 'config_restore_controller #(.MAX_CYCLES(1048576))config_restore('
NEW_INSTANCE = 'config_restore_controller #(.MAX_CYCLES(1048576),.NATIVE_FEEDBACK_PUBLICATION(1))config_restore('


def candidate(controller, wrapper):
    assert PARAMETER not in controller + wrapper
    assert controller.count(OLD_MODULE) == controller.count(OLD_PUBLISH) == 1
    assert wrapper.count(OLD_INSTANCE) == 1 and len(re.findall(r'\bjp_effective\b', wrapper)) == 3
    for text in ['.load_stage(jp_permit)', '.publish_permit(jp_permit)',
                 '.active_payload(jp_effective)', '.load_payload(jp_permit?jp_effective:(fd_fc_payload))',
                 ".load_authoritative(jp_permit?1'b1:(fd_fc_authoritative))"]:
        assert text in wrapper
    changed_controller = controller.replace(OLD_MODULE, NEW_MODULE).replace(OLD_PUBLISH, NEW_PUBLISH)
    changed_wrapper = wrapper.replace(OLD_INSTANCE, NEW_INSTANCE)
    assert changed_controller.replace(NEW_MODULE, OLD_MODULE).replace(NEW_PUBLISH, OLD_PUBLISH) == controller
    assert changed_wrapper.replace(NEW_INSTANCE, OLD_INSTANCE) == wrapper
    return {CONTROLLER: changed_controller, WRAPPER: changed_wrapper}


def main():
    assert not TARGET.exists()
    gates = predecessors('baseline')  # Matrix and both original RTL probes, before text generation.
    m, a, evidence = restored(REFERENCE)
    assert len(m['rtl']) == 133 and m['part'] == 'xcu280-fsvh2892-2L-e' and m['exit_code'] == 0
    assert a['check_timing_counts']['loops'] == 0 and not a['timing_loop_warnings']
    assert not a['critical_warnings'] and a['facts']['latches'] == a['facts']['blackboxes'] == 0
    models = [ROOT/'results/config_publication_retention_20261030.json',
              ROOT/'results/config_native_feedback_20261030.json']
    assert read(models[0])['status'] == 'binary_projection_checked_four_value_counterexample_found'
    assert read(models[1])['status'] == 'native_feedback_four_value_projection_passed_not_rtl_equivalence'
    for name in ['config_publication_retention_sources_20261030', 'config_native_feedback_sources_20261030']:
        evidence.append(verify_freeze(ROOT/'results'/name))
    source = {name: REFERENCE/'sources'/name for name in [CONTROLLER, WRAPPER]}
    physical = BASE/'checkpoint_edit_route_recovery_v1/sources'
    for name, file in source.items():
        assert sha(file) == m['sources'][name] == sha(physical/name)
    # The native model binds the physical sources; require the exact same controller and wrapper here.
    model_bound = read(models[1])['bound']
    for file in [physical/CONTROLLER, physical/WRAPPER]:
        assert model_bound[str(file)] == sha(file)
    texts = candidate(source[CONTROLLER].read_text(),source[WRAPPER].read_text())
    for file in models + list(source.values()) + [Path(__file__).resolve(), ROOT/'scripts/host_edit_system_common_v1.py']:
        gates[str(file)] = sha(file)
    for file in evidence:
        gates[str(file)] = sha(file)
    TARGET.mkdir(); (TARGET/'baseline').mkdir(); (TARGET/'fixed').mkdir()
    for name, file in source.items():
        shutil.copyfile(file,TARGET/'baseline'/name)
        (TARGET/'fixed'/name).write_text(texts[name])
        assert sha(TARGET/'baseline'/name) == m['sources'][name]
    manifest = dict(status='prepared_not_compiled_or_simulated', reference=str(REFERENCE),
        reference_manifest_sha256=sha(REFERENCE/'manifest.json'), reference_audit_sha256=sha(REFERENCE/'source_bound_audit.json'),
        builder_sha256=sha(Path(__file__)), bound=gates, modified_production_sources=[CONTROLLER,WRAPPER],
        sources={name:dict(baseline=sha(TARGET/'baseline'/name),fixed=sha(TARGET/'fixed'/name)) for name in source},
        parameter=dict(name=PARAMETER,default=0,native_residency_instance=1),
        retained_semantics=['Initial descriptor load and cold reset remain full-bank writes.',
            'Publication still writes the 32-bit raw version slice, saved design/checkpoint, current version and prepared state on the same original edge.',
            'All ready/valid, CRC-independent descriptor validation, X/Z-sensitive comparison, cancellation, attempt-reset and retirement guards remain byte-identical.',
            'Default-off generic behavior retains the original full publication assignment.'],
        required_before_selection=['Run generic original/default modes and native original/default/enabled modes with full event/cycle comparison.',
            'Require actual accepted-stage payload alias and full non-version prepared-bank invariants, including X and Z.',
            'Compare complete raw descriptor, active/cfg payloads, checkpoints and every control output each observed edge.',
            'Run a separately versioned full system with all original CP/query/backend/capture monitors and actual native alias observations.',
            'Independently audit, archive, actually restore and re-audit before matched OOC and physical comparison.'],
        timing_qualified=False,board_acceptance=False,
        scope='Isolated native feedback descriptor publication candidate from preferred CP baseline. No path/stage/route-label overlay, retiming, protection removal, formal equivalence, functional acceptance or measured timing benefit.')
    (TARGET/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('CONFIG_NATIVE_PUBLICATION_PREPARED',TARGET)


if __name__ == '__main__':
    main()
