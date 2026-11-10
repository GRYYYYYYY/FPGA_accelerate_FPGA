"""Copy a restored complete-system OOC checkpoint for independent physical measurement."""
from pathlib import Path
import json
import shutil
import sys
from run_checkpoint_authority import ROOT, sha


def main():
    out = Path(sys.argv[1]).resolve()
    reference = Path(sys.argv[2]).resolve()
    base = reference.parent
    assert out.parent == base and out != reference
    assert not any(c in str(out) for c in '{}\n\r')
    full_names = {
        'checkpoint_edit_synth_v1':'checkpoint_edit_system_crc_pressure_v1',
        'route_path_synth_v1':'route_path_system_crc_pressure_v1',
        'route_stage_synth_v1':'route_stage_system_crc_pressure_v1',
    }
    assert reference.name in full_names
    gate = json.loads((base/'route_stage_synth_followup_v1/manifest.json').read_text())
    assert gate['status'] == 'observed' and gate['stage'] == 'complete', 'Current synthesis owner must finish first'
    memory = Path('/sys/fs/cgroup')
    assert int((memory/'memory.current').read_text())*4 <= int((memory/'memory.max').read_text())*3
    m = json.loads((reference/'manifest.json').read_text())
    a = json.loads((reference/'source_bound_audit.json').read_text())
    receipt_path = ROOT/'results'/f'{reference.name}_restore_20261025.json'
    receipt = json.loads(receipt_path.read_text())
    assert m['status'] == 'observed' and m['exit_code'] == 0
    assert a['status'] == receipt['status'] == 'passed' and receipt['audit_byte_identical']
    assert a['manifest_sha256'] == sha(reference/'manifest.json')
    assert receipt['audit_sha256'] == sha(reference/'source_bound_audit.json')
    assert a['check_timing_counts']['loops'] == 0 and not a['timing_loop_warnings']
    assert not a['critical_warnings'] and a['facts']['latches'] == a['facts']['blackboxes'] == 0
    assert m['part'] == 'xcu280-fsvh2892-2L-e' and len(m['rtl']) == 133
    assert sha(reference/'synth.dcp') == a['artifact_sha256']['synth.dcp']
    assert (reference/'clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    full = base/full_names[reference.name]
    fm = json.loads((full/'manifest.json').read_text())
    fa = json.loads((full/'source_bound_audit.json').read_text())
    frp = ROOT/'results'/f'{full.name}_restore_20261025.json'
    fr = json.loads(frp.read_text())
    assert fm['status'] == 'observed' and fa['status'] == fr['status'] == 'passed'
    assert fr['audit_byte_identical'] and fr['audit_sha256'] == sha(full/'source_bound_audit.json')
    assert fa['manifest_sha256'] == sha(full/'manifest.json') and len(fa['exact_comparisons']) == 27
    for name in m['rtl']:
        assert sha(reference/'sources'/name) == m['sources'][name] == fm['sources'][name]['sha256'], name
        assert sha(full/'sources'/name) == m['sources'][name], name
    template = ROOT/'hardware/scripts/implement_state_ooc.tcl'
    out.mkdir()
    copied = {}

    def copy(source, relative):
        target = out/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied[str(relative)] = sha(target)
        assert sha(source) == copied[str(relative)]

    for name in m['rtl']:
        copy(reference/'sources'/name, Path('sources')/name)
    for source, name in [
        (reference/'synth.dcp', 'synthesized.dcp'), (reference/'clock.xdc', 'clock.xdc'),
        (reference/'manifest.json', 'synthesis_manifest.json'),
        (reference/'source_bound_audit.json', 'synthesis_audit.json'),
        (receipt_path, 'synthesis_restoration.json'),
        (full/'source_bound_audit.json', 'full_system_audit.json'),
        (frp, 'full_system_restoration.json'),
    ]:
        copy(source, Path('inputs')/name)
    copy(Path(__file__), Path('tools/prepare_state_ooc_physical.py'))
    copy(template, Path('tools/implement_state_ooc.tcl'))
    (out/'run.tcl').write_text(template.read_text().replace('@OUT@', str(out)))
    record = dict(status='prepared', reference=str(reference), full_system_reference=str(full),
                  part=m['part'], top='query_residency_system', clock_period_ns=10,
                  parameters=m['parameters'], rtl=m['rtl'], inputs=copied,
                  tcl_sha256=sha(out/'run.tcl'), preparer_sha256=sha(Path(__file__)),
                  template_sha256=sha(template), synthesis_audit_sha256=sha(reference/'source_bound_audit.json'),
                  full_system_audit_sha256=sha(full/'source_bound_audit.json'),
                  timing_qualified=False,
                  scope='Copied complete-system OOC DCP and original 10ns constraints. '
                        'Default opt/place/route research measurement only; no invented IO budgets, '
                        'clock location, timing exceptions or board frequency claim. '
                        'Preparation does not execute Vivado or prove physical feasibility.')
    (out/'manifest.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print('STATE_OOC_PHYSICAL_PREPARED', len(m['rtl']), reference.name)


if __name__ == '__main__':
    main()
