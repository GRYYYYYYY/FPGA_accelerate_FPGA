"""Prepare a fresh static-stage OOC opt/place/route input set; never execute tools."""
from pathlib import Path
import json
import shutil
import sys
from check_stage_static_cp_physical_inputs_v5 import evidence
from check_stage_static_cp_physical_inputs_v5 import ROOT, BASE, TARGET, FULL, sha, read


OUTPUT = BASE/'stage_static_cp_physical_v5'


def main():
    out = Path(sys.argv[1]).resolve()
    assert out == OUTPUT and not out.exists()
    proof = evidence()  # Before reading any candidate synthesis files or creating output.
    m = read(TARGET/'manifest.json')
    template = ROOT/'hardware/scripts/implement_state_ooc.tcl'
    text = template.read_text()
    sequence = ['open_checkpoint [file join $state_out inputs synthesized.dcp]',
                'opt_design', 'place_design -directive Default', 'route_design -directive Default']
    positions = [text.index(command) for command in sequence]
    assert positions == sorted(positions)
    assert text.count('@OUT@') == 1 and 'resume_placed' not in text
    # No old placement is copied. Preserve the original, validated command template.
    tool_paths = [Path(__file__).resolve(), ROOT/'scripts/check_stage_static_cp_physical_inputs_v5.py',
                  ROOT/'scripts/config_native_publication_synth_common_v1.py',
                  ROOT/'scripts/host_edit_system_common_v1.py', template]
    proof.update({str(p): sha(p) for p in tool_paths})
    out.mkdir()
    inputs = {}

    def copy(source, relative):
        dest = out/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        inputs[str(relative)] = sha(source)
        assert sha(dest) == inputs[str(relative)]

    for name in m['rtl']:
        copy(TARGET/'sources'/name, Path('sources')/name)
    copy(TARGET/'synth.dcp', Path('inputs/synthesized.dcp'))
    copy(TARGET/'clock.xdc', Path('inputs/clock.xdc'))
    for i, (source, digest) in enumerate(proof.items()):
        assert sha(source) == digest
        copy(Path(source), Path('bound')/f'{i:03d}_{Path(source).name}')
    (out/'run.tcl').write_text(text.replace('@OUT@', str(out)))
    record = dict(status='prepared', stage='awaiting_validated_runner', reference=str(TARGET),
        full_system_reference=str(FULL), part=m['part'], parameters=m['parameters'],
        rtl=m['rtl'], top='query_residency_system', clock_period_ns=10,
        inputs=inputs, external_evidence_sha256=proof,
        tcl_sha256=sha(out/'run.tcl'), template_sha256=sha(template),
        preparer_sha256=sha(Path(__file__)), timing_qualified=False, board_acceptance=False,
        scope='Fresh candidate synthesis checkpoint, original default opt/place/route template; '
              'no prior placement, new IO budgets, clock locations, exceptions or waivers. '
              'Preparation alone does not authorize an unvalidated runner or prove physical timing.')
    (out/'manifest.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print('STATIC_STAGE_PHYSICAL_PREPARED', len(m['rtl']))


if __name__ == '__main__':
    main()
