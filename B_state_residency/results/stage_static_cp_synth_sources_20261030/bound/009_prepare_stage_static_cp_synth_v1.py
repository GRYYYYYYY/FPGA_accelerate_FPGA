"""Prepare the isolated stage candidate's matched production-only OOC inputs.

Does not launch Vivado or claim full-system functional netlist acceptance.
"""
from pathlib import Path
import json
import shutil
import sys
from host_edit_system_common_v1 import ROOT, BASE, sha, read, restored, verify_freeze, identity

REFERENCE = BASE / 'checkpoint_edit_synth_v1'
FULL = BASE / 'stage_static_cp_system_v1'
TARGET = BASE / 'stage_static_cp_synth_v1'
VARIANT = ROOT / 'hardware/variants/stage_static_cp_system_sources_v1'


def evidence():
    accepted = ROOT / 'results/stage_static_cp_system_20261030.json'
    frozen = verify_freeze(ROOT / 'results/stage_static_cp_system_sources_20261030')
    fm, fa, ff = restored(FULL)
    report = read(accepted)
    assert report['status'] == 'isolated_stage_host_system_actual_restored'
    assert report['audit'] == fa and fa['status'] == 'passed'
    assert fm['stage'] == 'complete'
    assert identity(fm['runner_pid']) != str(fm['runner_start_ticks'])
    assert len(fa['exact_comparisons']) == 27
    assert fa['production_sources'] == 133 and fa['verification_sources'] == 3
    rm, ra, rf = restored(REFERENCE)
    assert rm['exit_code'] == 0 and rm['part'] == 'xcu280-fsvh2892-2L-e'
    assert len(rm['rtl']) == len(set(rm['rtl'])) == 133
    assert ra['check_timing_counts']['loops'] == 0
    cm = read(VARIANT / 'manifest.json')
    assert set(cm['sources']) == {'route_commit_controller.sv', 'route_commit_host_adapter.sv'}
    for path, digest in cm['bound'].items():
        assert sha(path) == digest
    assert set(rm['rtl']).issubset(fm['rtl']) and len(fm['rtl']) == 136
    for name in rm['rtl']:
        assert not Path(name).name.startswith('tb_')
        assert Path(name).name != 'axi_file_memory.sv'
        original = sha(REFERENCE / 'sources' / name)
        assert original == rm['sources'][name]
        expected = cm['sources'][name]['fixed'] if name in cm['sources'] else original
        assert sha(FULL / 'sources' / name) == fm['sources'][name]['sha256'] == expected
    for name, entry in cm['sources'].items():
        assert sha(VARIANT / 'baseline' / name) == entry['baseline'] == rm['sources'][name]
        assert sha(VARIANT / 'fixed' / name) == entry['fixed']
    files = ff + rf + [accepted, frozen, VARIANT / 'manifest.json', Path(__file__).resolve()]
    files += [VARIANT / role / name for role in ['baseline', 'fixed'] for name in cm['sources']]
    return rm, cm, {str(p): sha(p) for p in files}


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == TARGET and not p.exists()
    rm, cm, proof = evidence()
    p.mkdir()
    src = p / 'sources'
    src.mkdir()
    (p / 'bound').mkdir()
    sources = {}
    for name, digest in rm['sources'].items():
        origin = REFERENCE / 'sources' / name
        assert sha(origin) == digest
        dest = src / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, dest)
        sources[name] = digest
    changes = {}
    for name, entry in cm['sources'].items():
        shutil.copyfile(VARIANT / 'fixed' / name, src / name)
        sources[name] = sha(src / name)
        changes[name] = dict(original_sha256=entry['baseline'], candidate_sha256=entry['fixed'])
    for file in src.rglob('*.dat'):
        shutil.copyfile(file, p / file.name)
    tcl = (REFERENCE / 'synth.tcl').read_text().replace(str(REFERENCE), str(p))
    assert tcl.count('read_verilog -sv ') == 133
    (p / 'synth.tcl').write_text(tcl)
    shutil.copyfile(REFERENCE / 'clock.xdc', p / 'clock.xdc')
    bound = {}
    for i, (origin, digest) in enumerate(proof.items()):
        name = f'{i:03d}_{Path(origin).name}'
        shutil.copyfile(origin, p / 'bound' / name)
        assert sha(p / 'bound' / name) == digest
        bound[name] = dict(source=origin, sha256=digest)
    manifest = dict(status='prepared', sources=sources, rtl=rm['rtl'], parameters=rm['parameters'],
                    part=rm['part'], reference=str(REFERENCE), production_changes=changes,
                    reference_audit_sha256=sha(REFERENCE / 'source_bound_audit.json'),
                    tcl_sha256=sha(p / 'synth.tcl'), xdc_sha256=sha(p / 'clock.xdc'),
                    clock_period_ns=10, bound=bound, stage_static_evidence=proof,
                    full_system_functional_netlist_validated=False, timing_qualified=False,
                    scope='CP-only static stage, matched133 production RTL/U280/parameters/10ns. Preparation only; no Vivado launched.')
    (p / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print('STAGE_STATIC_CP_SYNTH_PREPARED', len(rm['rtl']), len(changes))


if __name__ == '__main__':
    main()
